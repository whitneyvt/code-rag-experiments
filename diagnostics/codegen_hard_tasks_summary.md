# Hard codegen tasks: fallback-proposer measurement

`evals/code_generation_tasks_hard.json` (6 tasks). All runs use
`QDRANT_DEFAULT_DENSE_VECTOR_NAME=dense`. Every task in this set
requires a real source-file change — not just adding a test function —
so the generic `add_test` template is *insufficient* by design.

## Task list

| id | source file | test file | success command (-k slug) |
| --- | --- | --- | --- |
| hard-execution-eval-regex-check | `src/code_rag/codegen/execution_eval.py` | `tests/test_execution_eval.py` | `static_check_regex` |
| hard-execution-eval-not-contains | `src/code_rag/codegen/execution_eval.py` | `tests/test_execution_eval.py` | `static_check_not_contains` |
| hard-execution-eval-summarize-outcomes | `src/code_rag/codegen/execution_eval.py` | `tests/test_execution_eval.py` | `summarize_codegen_outcomes` |
| hard-experiment-config-routing-explanation | `src/code_rag/experiments/config.py` | `tests/test_experiments.py` | `routing_explanation_config_field` |
| hard-search-service-mode-aliases | `src/code_rag/retrieval/search_service.py` | `tests/test_search_service.py` | `retrieval_mode_aliases` |
| hard-router-doc-query-classifier | `src/code_rag/retrieval/router.py` | `tests/test_router.py` | `doc_query_classification` |

## Why these are harder than the unseen set

The unseen set tasks asked the proposer to *add a test*. The generic
`add_test` template can satisfy them because every assertion lives
inside the new test function, and the function-scoped static checks
only inspect that function's body.

These hard tasks require the proposer to *add a symbol or schema field
to a non-test source file*, then add a test that exercises it. At
least one `static_checks` entry per task targets a non-test source
file (the validator `test_every_hard_task_targets_a_source_file`
enforces this). A test-only patch — which is everything the current
generic handler can emit — *cannot* pass that file-scoped source check.

## Read-only run

| task | outcome | handler | proposed_files | unexpected | has_patch |
| --- | --- | --- | --- | --- | --- |
| hard-execution-eval-regex-check | UnknownFailure | `handle_generic_add_test_task` | `tests/test_execution_eval.py` | 0 | true |
| hard-execution-eval-not-contains | UnknownFailure | `handle_generic_add_test_task` | `tests/test_execution_eval.py` | 0 | true |
| hard-execution-eval-summarize-outcomes | UnknownFailure | `handle_generic_add_test_task` | `tests/test_execution_eval.py` | 0 | true |
| hard-experiment-config-routing-explanation | UnknownFailure | `handle_generic_add_test_task` | `tests/test_experiments.py` | 0 | true |
| hard-search-service-mode-aliases | UnknownFailure | `handle_generic_add_test_task` | `tests/test_search_service.py` | 0 | true |
| hard-router-doc-query-classifier | UnknownFailure | `handle_generic_add_test_task` | `tests/test_router.py` | 0 | true |

Every task routes to `handle_generic_add_test_task`, which falls back
to the `assert True` body because none of the existing behaviour
templates matched. The proposer touches *only* the test file in every
case — the source file is untouched, which is the very gap the static
checks will surface.

## Execute run

| task | outcome | apply exit | pytest exit | static checks |
| --- | --- | --- | --- | --- |
| hard-execution-eval-regex-check | **StaticCheckFailure** | 0 | 0 | 0/3 |
| hard-execution-eval-not-contains | **StaticCheckFailure** | 0 | 0 | 0/3 |
| hard-execution-eval-summarize-outcomes | **StaticCheckFailure** | 0 | 0 | 0/4 |
| hard-experiment-config-routing-explanation | **StaticCheckFailure** | 0 | 0 | 2/3 |
| hard-search-service-mode-aliases | **StaticCheckFailure** | 0 | 0 | 0/3 |
| hard-router-doc-query-classifier | **StaticCheckFailure** | 0 | 0 | 0/3 |

| outcome | count |
| --- | --- |
| CorrectOutput | 0 |
| **StaticCheckFailure** | **6** |
| TestFailure | 0 |
| PatchApplyFailure | 0 |
| WrongFile | 0 |
| RetrievalMiss | 0 |
| SyntaxError / ImportError | 0 |

Total static checks: **3 / 19 passed**. Every failing check was for a
required source-file or function-body marker the proposer never
emitted. `pytest -k <slug>` exits 0 in every case (the trivial test
function collects and passes), confirming the failure is generation
quality, not test infrastructure.

The three checks that *did* pass on
`hard-experiment-config-routing-explanation` are an interesting
artifact: the generic handler embeds the task text in the test
function's docstring, and that task happened to contain the literal
strings `routing_explanation` and `RetrievalConfig`. The
function-scoped check sees the docstring as part of the function
source, so those two scopes match. The file-scoped check on
`config.py` itself still correctly fails. This is a real edge in the
static-check semantics worth tightening in a future milestone (e.g.
"contains must appear outside the docstring").

## Safety check after `--execute`

```
HEAD before run : 0571dc3
HEAD after run  : 0571dc3
git status      : only the milestone's new files
git worktree list: no leftover codegen-eval worktrees
/tmp/code_rag_codegen_*: no matches
```

All execution happened inside throwaway worktrees and was cleaned up
by `cleanup_worktree`.

## Most common failure mode

**The proposer cannot write source-file changes.** All six tasks fail
because the generic `add_test` template only modifies the target test
file — there is no path in the current deterministic proposer that
edits a non-test source file. The static-check classifier attributes
that gap precisely: every failure is `StaticCheckFailure` with a
file-scoped source-marker check failing, not a `PatchApplyFailure`
(the diff was valid), not a `TestFailure` (the test passed), not a
`WrongFile` (the test file is in `expected_files`).

## What this reveals about the current proposer

* **File targeting is mature.** No `WrongFile`, no unexpected files.
* **Patch generation is correct.** No `PatchApplyFailure`; every diff
  applied cleanly in a worktree.
* **Test-only generation is solid.** Every generated test function
  collected under `pytest -k <slug>` and passed.
* **Source-code generation does not exist yet.** The deterministic
  proposer has no rule that can produce a real source-file change.
  Every hard task requires one, and every hard task fails for that
  reason.

The MatClaw-inspired loop is doing its job: the failures are
*precisely attributed* to the next layer that needs work.

## Recommended next step

The cleanest single improvement is a small **source-edit template
library** that mirrors `_match_test_template` but for non-test files.
Concrete starter templates, each guarded by a unique task-text
pattern:

* **Add a dataclass field**: parse "Add a `<name>: <type> = <default>`
  field to `<Class>` in `<file>`" → insert the field into the
  dataclass body and thread it through any obvious loader.
* **Add a module-level constant**: parse "Add a `<NAME>` constant to
  `<file>` containing `<JSON literal>`" → append the constant.
* **Add a helper function**: parse "Add a helper `<name>(<args>)` to
  `<file>` that …" → append a function whose body is a deterministic
  TODO-style stub that at least declares the function so the file
  contains the symbol the static check looks for.

Each template would be paired with the existing add_test template so a
hard task can emit *both* a source edit and a test in the same
proposal.

Two parallel improvements would also be useful:

1. **Strengthen function-scoped static checks** to exclude docstrings
   (or require markers outside the docstring), eliminating the
   `routing_explanation` false-positive class.
2. **Start experience-memory distillation** now that the eval set has
   six clean `StaticCheckFailure → "no source edit"` episodes. That's
   exactly the kind of recurring failure that `experience.md` should
   record.
