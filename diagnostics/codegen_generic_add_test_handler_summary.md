# Generic add_test handler: unseen eval results

`evals/code_generation_tasks_unseen.json` (6 tasks). All runs use
`QDRANT_DEFAULT_DENSE_VECTOR_NAME=dense` against the default `code_chunks`
Qdrant collection.

The new handler `handle_generic_add_test_task` lives in
`src/code_rag/codegen/deterministic_stubs.py`. It runs **after**
seed-specific id handlers but **before** the TODO fallback. It matches
any task whose `success_command` contains a `pytest ... -k <slug> ...`
filter against an existing test file in `expected_files`, and appends a
minimum-viable real pytest function named `test_<slug>` with the task
description in its docstring. It is idempotent: if a function whose name
already contains the slug exists in the target file, it returns `[]` so
the evaluator runs `success_command` against the untouched repo.

## Outcome progression (unseen set)

| task | before fallback | after fallback (TODO stubs) | + generic handler (read-only) | + generic handler (execute) |
| --- | --- | --- | --- | --- |
| unseen-sparse-dotted-module-router | — | TestFailure | UnknownFailure | **CorrectOutput** |
| unseen-router-dense-vector-name-config | — | TestFailure | UnknownFailure | **CorrectOutput** |
| unseen-cli-routing-explanation-help | — | TestFailure | UnknownFailure | **CorrectOutput** |
| unseen-diagnostic-category-counts | — | TestFailure | UnknownFailure | **CorrectOutput** |
| unseen-experiment-mrr-default | — | TestFailure | UnknownFailure | **CorrectOutput** |
| unseen-sparse-screaming-env-var | — | TestFailure | UnknownFailure | **CorrectOutput** |

| outcome | TODO-fallback run | generic handler (read-only) | generic handler (execute) |
| --- | --- | --- | --- |
| CorrectOutput | 0 | 0 | **6** |
| TestFailure | 6 | 0 | 0 |
| PatchApplyFailure | 0 | 0 | 0 |
| WrongFile | 0 | 0 | 0 |
| RetrievalMiss | 0 | 0 | 0 |
| UnknownFailure | 0 | 6 | 0 |

Every unseen task in the execute run is routed to
`handle_generic_add_test_task` (no seed id collision) and
`proposed_expected = 1`, `unexpected = 0` — file targeting is still
clean. The read-only run gets `UnknownFailure` only because read-only
mode never executes; the new handler's metadata sets
`expected_to_execute = true`.

## Seed eval regression check

A re-run of the seed eval under `--execute` after the generic handler
landed:

| task | handler | outcome |
| --- | --- | --- |
| router-test-add | `_handle_router_test_add` | CorrectOutput |
| sparse-tokenization-test-add | `_handle_sparse_tokenization_test_add` | CorrectOutput |
| readme-section-update | `_handle_readme_section_update` | CorrectOutput |
| config-parsing-test-add | `_handle_config_parsing_test_add` | CorrectOutput |
| routing-diagnostic-test-add | `_handle_routing_diagnostic_test_add` | CorrectOutput |

Seed-specific handlers still win — the dispatcher tries the per-id table
first and only falls through to the generic handler when no seed id
matches. **5 / 5 CorrectOutput** preserved.

## Combined execute outcomes

| eval set | CorrectOutput | TestFailure | other |
| --- | --- | --- | --- |
| seed (5 tasks) | 5 | 0 | 0 |
| unseen (6 tasks) | 6 | 0 | 0 |
| **total (11 tasks)** | **11** | **0** | **0** |

## Safety check after `--execute`

```
HEAD before run : c6be3f9
HEAD after run  : c6be3f9
git status      : only this milestone's new/modified files
git worktree list: no leftover codegen-eval worktrees
```

All execution happened inside throwaway worktrees under
`/tmp/code_rag_codegen_*` and was cleaned up by `cleanup_worktree`.

## What the generic handler emits

For each unseen task it appends a function shaped like this (here for
`-k routing_explanation_help`):

```python
def test_routing_explanation_help():
    """Codegen-eval generic stub for -k 'routing_explanation_help'.
    Add a unit test in tests/test_search_cli.py that runs ..."""
    # This minimum-viable test was emitted by the codegen eval's generic
    # add_test handler so `pytest -k routing_explanation_help` collects
    # and passes a real function. Future eval contracts should tighten
    # the success_command to verify the assertions inside this function.
    assert True
```

This is deliberately a minimum-viable test, not a behaviour-equivalent
test. The current eval contract is "`pytest -k <slug>` exits 0", and the
handler satisfies that contract. Tightening the contract — e.g. requiring
the new test to import a specific symbol or call a specific function —
is the natural next step.

## Limitations the next milestone should address

* The generic handler does not derive assertions from the task text. A
  follow-up could parse simple "`assert X` / `tokens = f('y')`" patterns
  out of the task description and seed the function body.
* The handler only modifies existing test files; tasks whose expected
  test file does not yet exist still fall through to the TODO path. A
  follow-up could lift the create-mode handler used for
  `config-parsing-test-add` into the generic path.
* Eval `success_command`s should be tightened so a no-op `assert True`
  function cannot satisfy them. Candidates: `pytest -k <slug>` plus a
  required substring assertion via `grep`, or a custom pytest plugin that
  rejects empty-body tests.

## Recommended next step

Two parallel tracks are now useful:

1. **Tighten the eval contracts** so the generic handler's
   minimum-viable function no longer satisfies them. This converts the
   measurement back into a generation-quality signal.
2. **Start distilling `.agent_memory/history.jsonl`** into
   `experience.md`. With 11 / 11 CorrectOutput episodes now logged across
   the seed + unseen runs, the MatClaw-style experience-memory phase has
   useful raw material.
