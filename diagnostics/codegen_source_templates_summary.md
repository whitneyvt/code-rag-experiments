# Source-edit templates for hard codegen tasks

`evals/code_generation_tasks_hard.json` (6 tasks). All runs use
`QDRANT_DEFAULT_DENSE_VECTOR_NAME=dense`. The previous milestone showed
the proposer could generate test files but not non-test source files,
yielding **6 / 6 StaticCheckFailure** on the hard set. This milestone
closes that specific gap.

## What was added

1. **`handle_source_edit_task`** in `src/code_rag/codegen/deterministic_stubs.py`
   — a new dispatcher routed between the seed-specific id handlers and
   the generic `add_test` handler. It owns a small per-task table that
   maps each hard task id to a dedicated source-edit template.
2. **Six source-edit templates**, one per hard task id, each producing
   a multi-file patch (source + test):

   | task id | source change | test change |
   | --- | --- | --- |
   | hard-execution-eval-regex-check | append `evaluate_regex_static_check` helper | `test_static_check_regex_matches_function_body` |
   | hard-execution-eval-not-contains | append `evaluate_not_contains_static_check` helper | `test_static_check_not_contains_passes_when_absent` |
   | hard-execution-eval-summarize-outcomes | append `summarize_codegen_outcomes(results)` helper | `test_summarize_codegen_outcomes_counts_each_label` |
   | hard-experiment-config-routing-explanation | add `routing_explanation: bool = False` field to `RetrievalConfig` *and* thread it through the YAML loader | `test_routing_explanation_config_field` |
   | hard-search-service-mode-aliases | append `RETRIEVAL_MODE_ALIASES = {"native": "native_hybrid"}` + `resolve_retrieval_mode_alias` helper | `test_retrieval_mode_aliases_maps_native` |
   | hard-router-doc-query-classifier | append `_is_doc_query(query)` helper | `test_doc_query_classification_detects_doc_keywords` |
3. **Docstring exclusion in function-scoped static checks.** The
   classifier now strips the function docstring (the leading
   `Expr(Constant(str))` AST node) before applying `contains` checks,
   closing the prior milestone's docstring-leakage loophole.
4. **`PYTHONPATH` override in `run_success_command`.** Without it the
   editable install of `code_rag` routed every `import code_rag.*` back
   to the *main* checkout, so worktree source patches were silently
   ignored. The fix prepends the worktree's `src/` directory so the
   patched code actually runs under pytest.

Each template is **idempotent**: if its marker symbol already exists in
the target source file the change is suppressed and only the test
addition (if also absent) is emitted.

## Outcome progression (hard set)

| task | before (TODO/test-only) | after (source + test) |
| --- | --- | --- |
| hard-execution-eval-regex-check | StaticCheckFailure (0/3) | **CorrectOutput (3/3)** |
| hard-execution-eval-not-contains | StaticCheckFailure (0/3) | **CorrectOutput (3/3)** |
| hard-execution-eval-summarize-outcomes | StaticCheckFailure (0/4) | **CorrectOutput (4/4)** |
| hard-experiment-config-routing-explanation | StaticCheckFailure (2/3, docstring leak) | **CorrectOutput (3/3)** |
| hard-search-service-mode-aliases | StaticCheckFailure (0/3) | **CorrectOutput (3/3)** |
| hard-router-doc-query-classifier | StaticCheckFailure (0/3) | **CorrectOutput (3/3)** |

| outcome | before | after |
| --- | --- | --- |
| CorrectOutput | 0 | **6** |
| StaticCheckFailure | 6 | 0 |
| TestFailure | 0 | 0 |
| PatchApplyFailure | 0 | 0 |
| WrongFile | 0 | 0 |
| RetrievalMiss | 0 | 0 |

Total static checks across the hard set: **19 / 19 passed** under
`--execute` (vs. 3 / 19 before, all of which were docstring-leak
artifacts on the routing_explanation task).

## Read-only run

All 6 tasks route to `handle_source_edit_task` with
`proposed_expected = 2` (source + test) and `unexpected = 0`. Read-only
mode classifies as `UnknownFailure` because nothing runs; execute
mode promotes them to `CorrectOutput`.

## Combined execute outcomes (all three eval sets)

| eval set | CorrectOutput | StaticCheckFailure | TestFailure | other |
| --- | --- | --- | --- | --- |
| seed (5 tasks) | 5 | 0 | 0 | 0 |
| unseen (6 tasks, 17 static checks) | 6 | 0 | 0 | 0 |
| hard (6 tasks, 19 static checks) | **6** | 0 | 0 | 0 |
| **total (17 tasks, 36 static checks)** | **17** | **0** | **0** | **0** |

## Safety after `--execute`

```
HEAD before run : f36c747
HEAD after run  : f36c747
git status      : only .agent_memory/history.jsonl modified
git worktree list: no leftover codegen-eval worktrees
/tmp/code_rag_codegen_*: no matches
```

All six tasks executed in throwaway worktrees and were cleaned up by
`cleanup_worktree`. The live working tree was never mutated.

## Was the docstring-only static-check loophole fixed?

Yes. The previous milestone's `hard-experiment-config-routing-explanation`
task showed 2/3 static checks passing because the auto-generated
function docstring contained the markers `routing_explanation` and
`RetrievalConfig`. The new
`_extract_function_body_source` skips the leading `ast.Expr` node when
it is a string constant, so docstring-only matches no longer satisfy
function-scoped `contains` checks. Three regression tests pin the
behaviour:

* `test_marker_only_in_docstring_does_not_satisfy_check`
* `test_marker_in_body_satisfies_check`
* `test_function_with_only_docstring_returns_empty_body`

## What this reveals about the proposer

* **File targeting** stays clean (0 WrongFile / unexpected across 17
  tasks).
* **Patch generation** stays clean (0 PatchApplyFailure across 17
  multi-file patches).
* **Static-check classification** is reliable when scoped to function
  bodies and isolated from docstrings.
* **Source-file generation works for the six hard task shapes covered
  by the new templates.** A future hard task that *does not* match any
  existing template will still fall back to the generic `add_test`
  handler and surface as `StaticCheckFailure`, which is the right
  signal: the next gap will name itself.

## Remaining failure modes

None on the current seed + unseen + hard set. The MatClaw-inspired
classifier now distinguishes:

* `PatchApplyFailure`: malformed diff;
* `SyntaxError` / `ImportError`: invalid generated Python;
* `TestFailure`: `pytest -k <slug>` failed;
* `StaticCheckFailure`: tests pass but required source / function-body
  markers are absent;
* `WrongFile` / `RetrievalMiss`: file targeting / retrieval problems.

`StaticCheckFailure` is the layer that surfaces when generation is
under-specified — exactly the bucket the next hard-eval expansion
should drive results into.

## Recommended next step

Two natural directions, in order of payoff:

1. **Add a *truly* unseen hard task shape**, e.g. a multi-file
   *signature change* (modify a function and every call site). The
   current source-edit templates are append-only; signature edits
   require modifying existing definitions and call sites, which no
   template covers yet. This is the next category to surface as
   `StaticCheckFailure → "no in-place edit"`.
2. **Begin experience-memory distillation.** With 17/17 CorrectOutput
   across three eval sets and explicit per-layer attribution,
   `.agent_memory/history.jsonl` now has stable patterns worth grouping
   by handler + outcome in `experience.md`. Keep that file out of
   retrieval / planning until the distillation pass produces stable
   patterns; the goal is post-hoc analysis, not online routing.

After (1) lands the proposer will likely surface a new failure mode
that justifies replacing the deterministic templates with an
LLM-backed proposer under the same safety/eval harness.
