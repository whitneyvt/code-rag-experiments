# In-place codegen tasks: append-only-proposer measurement

`evals/code_generation_tasks_inplace.json` (5 tasks). All runs use
`QDRANT_DEFAULT_DENSE_VECTOR_NAME=dense`. Every task in this set
requires modifying *existing* code — extending a list literal,
inserting a branch into an existing function, flipping an existing
default, or weaving a regex branch into an existing helper. The
current source-edit templates are append-only and the generic add_test
handler is test-only; this run measures the gap.

## Task list

| id | category | source file | in-place required because… |
| --- | --- | --- | --- |
| inplace-router-error-patterns-out-of-memory | in_place_list_extension | `src/code_rag/retrieval/router.py` | `_is_error_query` iterates the existing `ERROR_PATTERNS` list; an appended duplicate list isn't consulted. |
| inplace-router-cli-patterns-pytest | in_place_list_extension | `src/code_rag/retrieval/router.py` | `_is_cli_query` iterates the existing `CLI_PATTERNS` list; same story. |
| inplace-router-classify-query-doc-branch | in_place_branch_insertion | `src/code_rag/retrieval/router.py` | Returning `"doc"` requires a new `if _is_doc_query(...)` branch inside `classify_query`; the function-scoped static check pins the branch to that exact function body. |
| inplace-evaluate-static-check-regex-branch | in_place_function_body_modification | `src/code_rag/codegen/execution_eval.py` | The regex branch must live inside `_evaluate_static_check` so the live runner uses it; the function-scoped check requires `regex` inside that function body. |
| inplace-config-loader-adaptive-default-true | in_place_default_change | `src/code_rag/experiments/config.py` | The default flips inside the existing `load_config` body (specifically the `retrieval_data.get("adaptive", True)` call); function-scoped check pins it to the existing loader. |

## Read-only run

| task | outcome | handler | proposed_files | unexpected | has_patch |
| --- | --- | --- | --- | --- | --- |
| inplace-router-error-patterns-out-of-memory | UnknownFailure | `handle_generic_add_test_task` | `tests/test_router.py` | 0 | true |
| inplace-router-cli-patterns-pytest | UnknownFailure | `handle_generic_add_test_task` | `tests/test_router.py` | 0 | true |
| inplace-router-classify-query-doc-branch | UnknownFailure | `handle_generic_add_test_task` | `tests/test_router.py` | 0 | true |
| inplace-evaluate-static-check-regex-branch | UnknownFailure | `handle_generic_add_test_task` | `tests/test_execution_eval.py` | 0 | true |
| inplace-config-loader-adaptive-default-true | UnknownFailure | `handle_generic_add_test_task` | `tests/test_experiments.py` | 0 | true |

Every task falls through both the seed table and the source-edit
dispatcher to the generic `add_test` handler. The proposer touches
*only* the test file in every case — the source file is untouched,
which is the exact capability gap this eval was built to expose.

## Execute run

| task | outcome | apply | pytest | static checks |
| --- | --- | --- | --- | --- |
| inplace-router-error-patterns-out-of-memory | **StaticCheckFailure** | 0 | 0 | 0/3 |
| inplace-router-cli-patterns-pytest | **StaticCheckFailure** | 0 | 0 | 0/3 |
| inplace-router-classify-query-doc-branch | **StaticCheckFailure** | 0 | 0 | 0/4 |
| inplace-evaluate-static-check-regex-branch | **StaticCheckFailure** | 0 | 0 | 0/4 |
| inplace-config-loader-adaptive-default-true | **StaticCheckFailure** | 0 | 0 | 0/3 |

| outcome | count |
| --- | --- |
| CorrectOutput | 0 |
| **StaticCheckFailure** | **5** |
| TestFailure | 0 |
| PatchApplyFailure | 0 |
| WrongFile | 0 |
| RetrievalMiss | 0 |
| SyntaxError / ImportError | 0 |

Total static checks: **0 / 17 passed** (every file-scoped marker and
every function-body marker is absent because the proposer never wrote
to the source file). Every `pytest -k <slug>` exited 0 (the trivial
`assert True` test collected and passed). The failures are localized
cleanly to *in-place source edit generation* — not retrieval, not
file targeting, not patch apply, not test infrastructure.

## Regression check across all eval sets

| eval set | CorrectOutput | StaticCheckFailure |
| --- | --- | --- |
| seed (5 tasks) | 5 | 0 |
| unseen (6 tasks) | 6 | 0 |
| hard (6 tasks, source-edit templates) | 6 | 0 |
| **in-place (5 tasks, NEW)** | **0** | **5** |
| **total (22 tasks)** | **17** | **5** |

The append-only source-edit templates from the prior milestone still
satisfy every task they were designed for, and the new in-place tasks
isolate the next capability gap without disturbing prior measurements.

## Safety after `--execute`

```
HEAD before run : f36c747
HEAD after run  : f36c747
git status      : only the new in-place files and history.jsonl
git worktree list: no leftover codegen-eval worktrees
/tmp/code_rag_codegen_*: no matches
```

All execution happened inside throwaway worktrees and was cleaned up
by `cleanup_worktree`. Live working tree never mutated.

## Did the append-style source templates fail as expected?

Yes, and the classifier attributed the failures precisely. Every
task surfaced as `StaticCheckFailure` with the source-file or
function-body markers absent. None fell into a noisier bucket
(`PatchApplyFailure`, `WrongFile`, `RetrievalMiss`, `TestFailure`).

## Most common failure mode

**No in-place source-edit template exists.** The previous milestone's
six source-edit templates are all append-style — they emit new helper
functions, constants, dataclass fields, and test functions, but they
never modify existing definitions. Every in-place task fails for the
same structural reason.

## What this says about readiness for trustworthy code generation

The eval pipeline is mature:

* File targeting is reliable (`0 WrongFile`, `0 unexpected` across
  every set).
* Patch generation is reliable (`0 PatchApplyFailure` across all
  multi-file patches the prior milestones generated, and the diffs
  the generic handler emits today still apply cleanly).
* Static-check attribution is precise enough to distinguish "added a
  helper" from "modified the existing helper" — the function-scoped
  check on `classify_query` would have been satisfied by an appended
  copy of `classify_query` with the new branch, but Python module
  semantics + the `_extract_function_body_source` AST walk catch the
  difference cleanly.
* The proposer can be trusted to *try* the safe behaviour (append
  rather than modify) and the classifier will refuse to grant
  `CorrectOutput` when an in-place change is required.

What's *not* ready: the proposer cannot yet make in-place changes.
That's the next capability the harness should drive into.

## Recommended next step

Implement a small **in-place edit template family** that mirrors the
append-style templates with targeted, idempotent in-place patches:

* **`_inplace_list_append`**: extend a known module-level list literal
  by finding `<NAME> = [\n` … `]` and inserting the new entry before
  the closing bracket.
* **`_inplace_function_body_branch_insert`**: insert a new
  `if <predicate>: return <value>` block into a known function at a
  named anchor (e.g. "below the config branch and above the symbol
  branch").
* **`_inplace_kwarg_default_swap`**: change a literal default in a
  named function call (e.g. `retrieval_data.get("adaptive", True)`).
* **`_inplace_dataclass_field_default`**: swap a literal default in a
  dataclass field assignment.

Each template should:

* Read the source file from disk;
* Find a tightly-anchored string region;
* Apply a deterministic transform;
* Bail out (return no source change) if the marker already exists or
  the anchor is missing — same idempotence + safety contract as the
  append-style templates.

Once those land, this in-place eval set should flip from 0/5 to 5/5
CorrectOutput, mirroring the seed → unseen → hard progression.

After (1) the next interesting question is: when the *anchor* itself
isn't predictable, can a proposer find it? That's the natural place
to introduce a small LLM-backed proposer behind the same harness —
temp worktree, static checks, classifier — without changing default
retrieval behaviour or adding any `apply_code_change` tool.
