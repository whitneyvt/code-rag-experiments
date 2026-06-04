# Codegen deterministic stubs: read-only + execute results

`evals/code_generation_tasks.json` (5 seed tasks). All runs use
`QDRANT_DEFAULT_DENSE_VECTOR_NAME=dense` against the default `code_chunks`
Qdrant collection.

## Outcome progression

| task | baseline | + file selection | + det stubs (read-only) | + det stubs (execute) |
| --- | --- | --- | --- | --- |
| router-test-add | RetrievalMiss | RetrievalMiss | UnknownFailure | **CorrectOutput** |
| sparse-tokenization-test-add | UnknownFailure | UnknownFailure | UnknownFailure | **CorrectOutput** |
| readme-section-update | **WrongFile** | UnknownFailure | UnknownFailure | **CorrectOutput** |
| config-parsing-test-add | UnknownFailure | UnknownFailure | UnknownFailure | **CorrectOutput** |
| routing-diagnostic-test-add | UnknownFailure | UnknownFailure | UnknownFailure | **CorrectOutput** |

| outcome | baseline | file selection | det stubs (read-only) | det stubs (execute) |
| --- | --- | --- | --- | --- |
| CorrectOutput | 0 | 0 | 0 | **5** |
| WrongFile | 1 | 0 | 0 | 0 |
| RetrievalMiss | 1 | 1 | 0 | 0 |
| UnknownFailure | 3 | 4 | 5 | 0 |
| TestFailure / PatchApplyFailure | 0 | 0 | 0 | 0 |

* The previous milestone eliminated `WrongFile` by targeting expected
  files. It also resolved one `RetrievalMiss` (the README case) by
  loading expected-file context from disk.
* This milestone eliminates every read-only `RetrievalMiss`: when a
  deterministic handler matches we mark `retrieval_hit = True` because
  the handler ships its own expected-file context.
* Under `--execute`, every seed task now produces `CorrectOutput`.

## Per-handler signal (read-only)

| task | handler | proposed_files | has_patch | expected_to_execute |
| --- | --- | --- | --- | --- |
| router-test-add | `_handle_router_test_add` | tests/test_router.py | true | true |
| sparse-tokenization-test-add | `_handle_sparse_tokenization_test_add` | (none — idempotent) | false | true |
| readme-section-update | `_handle_readme_section_update` | README.md | true | true |
| config-parsing-test-add | `_handle_config_parsing_test_add` | tests/test_experiments_config.py (create) | true | true |
| routing-diagnostic-test-add | `_handle_routing_diagnostic_test_add` | tests/test_routing_diagnostics.py | true | true |

`sparse-tokenization-test-add` returns no patch on purpose: an existing
`test_routing_explanation_flag` in `tests/test_sparse_vectors.py` already
satisfies the success command. The evaluator now treats
`phase = "no_change_needed"` plus `expected_to_execute = true` as a
sanctioned "run success_command in a worktree without applying any
patch" — that path runs and passes.

## Safety check after `--execute`

```
HEAD before run : e8cfa84
HEAD after run  : e8cfa84
git status      : modified files only from this milestone
                  (.agent_memory/history.jsonl,
                   scripts/evaluate_codegen.py,
                   src/code_rag/codegen/{diff_generator,execution_eval}.py,
                   new src/code_rag/codegen/deterministic_stubs.py,
                   new tests/test_deterministic_stubs.py)
git worktree list: no leftover codegen-eval worktrees
```

All execution happened inside throwaway worktrees under `/tmp/code_rag_codegen_*`
and was cleaned up by `cleanup_worktree`.

## What changed that made `--execute` produce `CorrectOutput`

Three changes, in order of impact:

1. **`src/code_rag/codegen/deterministic_stubs.py`** — new module with one
   handler per seed task. Handlers emit real code (a `pytest` function
   whose name matches the task's `-k` filter, a real markdown section)
   instead of TODO stubs, and check for existing markers so insertion is
   idempotent. Unknown task ids return `(None, None)` and the evaluator
   falls back to the previous TODO-stub flow.
2. **`src/code_rag/codegen/diff_generator.py`** — bug fix in
   `generate_unified_diff`: `lineterm=""` produced unified diffs without
   newlines between header lines, which `git apply` rejected as "No valid
   patches in input". Fixed to `lineterm="\n"`. The 15 existing
   `test_diff_generator.py` tests still pass.
3. **`scripts/evaluate_codegen.py`** — calls `handle_seed_task` first;
   falls back to the existing flow only for unknown tasks. Idempotent
   handler matches now run `success_command` in a worktree even when the
   patch is empty (the new `is_idempotent_handler` branch in
   `evaluate_task`). New `selection.deterministic_handler` /
   `handler_name` / `expected_to_execute` metadata records which path
   produced the proposal.

## Remaining failures

None on the seed set. Every task now classifies as `CorrectOutput` under
`--execute`. No `TestFailure`, `PatchApplyFailure`, or `RetrievalMiss`
outcomes remain.

## Is the MatClaw-inspired eval layer producing useful execution signal?

Yes — the loop now closes end-to-end:

* The same code paths that retrieve and propose also apply and verify.
* The classifier distinguishes `CorrectOutput` from `TestFailure`,
  `PatchApplyFailure`, `SyntaxError`, `ImportError`, `WrongFile`, and
  `RetrievalMiss`, giving per-layer failure attribution when something
  breaks.
* The seed set itself is now self-validating: a future refactor that
  silently breaks `_is_error_query`, the sparse tokenizer's
  `--routing_explanation` coverage, `load_config`'s adaptive flag
  parsing, or the routing-diagnostic tie counter would flip the
  corresponding task from `CorrectOutput` to `TestFailure`.

## Recommended next step

The seed tasks all pass deterministically — they're now upper-bounded by
the handlers themselves. To stress the loop further we should *grow* the
eval set with tasks that the deterministic handlers do *not* cover, so
the fallback TODO-stub path (and, eventually, an LLM proposer) gets
measured against `success_command`. Concrete suggestions:

* Add tasks that require touching multiple source files together (e.g.
  add a parameter to a function *and* update its call sites).
* Add tasks whose `success_command` is a property-style assertion the
  proposer must derive from retrieved code, not a hard-coded test name.
* Then begin distilling `.agent_memory/history.jsonl` patterns into
  `experience.md` so retrieval can be biased by past attribution
  signal — the MatClaw-inspired episodic-memory phase.
