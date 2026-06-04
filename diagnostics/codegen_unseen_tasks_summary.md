# Unseen codegen tasks: fallback-proposer measurement

`evals/code_generation_tasks_unseen.json` (6 tasks). None of these tasks
match any deterministic handler in
`src/code_rag/codegen/deterministic_stubs.py`. The point of this run is
to measure what the generic retrieve-and-stub fallback path produces on
small, unseen "add a focused test" tasks. Both runs use
`QDRANT_DEFAULT_DENSE_VECTOR_NAME=dense` against the default `code_chunks`
Qdrant collection.

## Tasks

| id | target test file | success command (-k slug) |
| --- | --- | --- |
| unseen-sparse-dotted-module-router | `tests/test_sparse_vectors.py` | `dotted_module_router_preserved` |
| unseen-router-dense-vector-name-config | `tests/test_router.py` | `dense_vector_name_config` |
| unseen-cli-routing-explanation-help | `tests/test_search_cli.py` | `routing_explanation_help` |
| unseen-diagnostic-category-counts | `tests/test_routing_diagnostics.py` | `category_counts_summary` |
| unseen-experiment-mrr-default | `tests/test_experiments.py` | `retrieval_metrics_mrr_default` |
| unseen-sparse-screaming-env-var | `tests/test_sparse_vectors.py` | `screaming_env_var_path_weight` |

## Read-only run

| task | outcome | handler | proposed_expected | unexpected | has_patch | is_TODO_only |
| --- | --- | --- | --- | --- | --- | --- |
| unseen-sparse-dotted-module-router | UnknownFailure | fallback | 2 / 2 | 0 | true | yes |
| unseen-router-dense-vector-name-config | UnknownFailure | fallback | 2 / 2 | 0 | true | yes |
| unseen-cli-routing-explanation-help | UnknownFailure | fallback | 2 / 2 | 0 | true | yes |
| unseen-diagnostic-category-counts | UnknownFailure | fallback | 2 / 2 | 0 | true | yes |
| unseen-experiment-mrr-default | UnknownFailure | fallback | 2 / 2 | 0 | true | yes |
| unseen-sparse-screaming-env-var | UnknownFailure | fallback | 2 / 2 | 0 | true | yes |

Every task

* fell through to the fallback proposer (`handler_name = null`);
* targeted only expected files (`unexpected = 0`); and
* produced a patch — but the patch is a TODO comment appended to each
  expected file, not real code.

File selection is healthy. The remaining problem is **generation
quality**.

## Execute run (in temp worktrees)

| task | outcome | apply exit | test exit | failure mode |
| --- | --- | --- | --- | --- |
| unseen-sparse-dotted-module-router | **TestFailure** | 0 | 5 | pytest: 0 tests collected (`-k` did not match) |
| unseen-router-dense-vector-name-config | **TestFailure** | 0 | 5 | same |
| unseen-cli-routing-explanation-help | **TestFailure** | 0 | 5 | same |
| unseen-diagnostic-category-counts | **TestFailure** | 0 | 5 | same |
| unseen-experiment-mrr-default | **TestFailure** | 0 | 5 | same |
| unseen-sparse-screaming-env-var | **TestFailure** | 0 | 5 | same |

| outcome | count |
| --- | --- |
| CorrectOutput | 0 |
| TestFailure | **6** |
| PatchApplyFailure | 0 |
| WrongFile | 0 |
| RetrievalMiss | 0 |
| SyntaxError / ImportError | 0 |

## Safety check after `--execute`

```
HEAD before run : 42e9c92
HEAD after run  : 42e9c92
git status      : only this milestone's new/modified files
git worktree list: no leftover codegen-eval worktrees
```

All execution happened inside throwaway worktrees under
`/tmp/code_rag_codegen_*` and was cleaned up by `cleanup_worktree`.

## Fallback proposer success rate

**0 / 6 = 0% CorrectOutput.** Every fallback proposal applied cleanly
but added only a TODO comment, so the targeted `-k <slug>` filter matched
no test and pytest exited 5. The MatClaw-inspired classifier put the
blame in the right place: not `PatchApplyFailure` (the diff was valid),
not `WrongFile` (the patch landed in the expected file), not
`RetrievalMiss` (handler-bypass enabled context loading from disk) —
just `TestFailure`, which is a generation-quality signal.

## Most common failure mode

**Stub-only generation.** The fallback proposer's
`_generate_deterministic_stub` only knows how to append a TODO comment.
That is safe but never satisfies a test-presence success command. Every
unseen task fails for the same reason.

## Is the fallback proposer ready for broader eval?

No. The fallback path is **safe** (patches apply, no live mutation, no
wrong-file regressions) but **not productive** — it cannot yet author a
real pytest function from retrieved context. Two directions could fix
this without breaking the safety contract:

* **Add a small task-classifier + template library** that recognises the
  "append a focused pytest function whose name contains a given slug"
  shape and emits a real function body using retrieved symbols. This
  extends the deterministic stub layer to cover a *class* of tasks
  instead of one task each.
* **Wire an LLM proposer** behind an opt-in flag so the eval can compare
  deterministic vs LLM proposals on the same unseen set. The temp-
  worktree apply+verify loop already exists; only the proposal step
  changes.

## Recommended next step

Generalize the deterministic stub layer to recognise the "append pytest
function matching `-k <slug>`" pattern, then re-run the unseen set. If
that closes most of the gap on the small-task shape, expand the unseen
set with multi-file tasks before introducing an LLM proposer.

A close second is to start distilling `.agent_memory/history.jsonl` into
`experience.md`: every entry in this run is a clean
`TestFailure → "stub-only generation" attribution`, which is exactly the
kind of pattern an experience-memory phase would benefit from.
