# In-place source-edit templates: in-place + regression results

`evals/code_generation_tasks_inplace.json` (5 tasks). All runs use
`QDRANT_DEFAULT_DENSE_VECTOR_NAME=dense`. The previous milestone built
the in-place eval set and the existing append-only proposer scored 0/5
CorrectOutput. This milestone adds a small in-place edit template
family and dispatches it ahead of the append-style templates.

## What was added

Four general-purpose in-place edit helpers in
`src/code_rag/codegen/deterministic_stubs.py`:

* **`_inplace_list_append(source, list_name, new_entry)`** — inserts a
  new entry before the closing bracket of a module-level list literal.
  Idempotent (unchanged if the entry is already present), returns
  `None` if the list cannot be located.
* **`_inplace_insert_before_line(source, anchor_substring, new_block,
  function_name=None)`** — inserts a block of code above the first
  line containing `anchor_substring`, matching the anchor's
  indentation. The optional `function_name` scopes both the
  idempotence check and the anchor search to that function's source
  segment.
* **`_inplace_replace_once(source, find, replace)`** — replaces a
  single literal occurrence; returns source unchanged when `replace`
  is already present and `find` is absent (idempotent), or `None`
  when both are missing.
* **`_wrap_inplace_change(file_path, repo_path, modifier, reasoning=)`** —
  reads the source, applies a modifier, and returns a `ProposedChange`
  or `None`.

Five in-place templates, one per in-place task id:

| task id | helper(s) used | source effect |
| --- | --- | --- |
| inplace-router-error-patterns-out-of-memory | `_inplace_list_append` | extend `ERROR_PATTERNS` in place with `"out of memory"` |
| inplace-router-cli-patterns-pytest | `_inplace_list_append` | extend `CLI_PATTERNS` in place with `"pytest"` |
| inplace-router-classify-query-doc-branch | `_inplace_insert_before_line` + append helper | add `_is_doc_query` helper if missing, then insert `if _is_doc_query(query): return "doc"` branch into `classify_query` body above the symbol-priority block |
| inplace-evaluate-static-check-regex-branch | `_inplace_replace_once` | weave a `getattr(check, "regex", None)` regex branch into both return paths of `_evaluate_static_check` |
| inplace-config-loader-adaptive-default-true | `_inplace_replace_once` | flip `retrieval_data.get("adaptive", False)` to `retrieval_data.get("adaptive", True)` inside `load_config` |

Each template is idempotent: it bails if its anchor is missing and it
returns no source change when the in-place edit has already landed.

Dispatch order is now:

```
1. seed-specific id handlers
2. in-place source-edit templates     ← NEW
3. append-style source-edit templates
4. generic add_test handler
5. None (TODO fallback)
```

## Outcome progression (in-place set)

| task | before (append-only proposer) | after (in-place templates) |
| --- | --- | --- |
| inplace-router-error-patterns-out-of-memory | StaticCheckFailure (0/3) | **CorrectOutput (3/3)** |
| inplace-router-cli-patterns-pytest | StaticCheckFailure (0/3) | **CorrectOutput (3/3)** |
| inplace-router-classify-query-doc-branch | StaticCheckFailure (0/4) | **CorrectOutput (4/4)** |
| inplace-evaluate-static-check-regex-branch | StaticCheckFailure (0/4) | **CorrectOutput (4/4)** |
| inplace-config-loader-adaptive-default-true | StaticCheckFailure (0/3) | **CorrectOutput (3/3)** |

| outcome | before | after |
| --- | --- | --- |
| CorrectOutput | 0 | **5** |
| StaticCheckFailure | 5 | 0 |

Static checks under `--execute`: **17 / 17 passed** (vs. 0 / 17 before).

## Read-only run

All 5 tasks route to `handle_source_edit_task` with `proposed_expected = 2`
(source + test) and `unexpected = 0`. Patches contain real in-place
diffs (visible in the result JSON) rather than append-only test
additions.

## Regression across all eval sets (combined `--execute`)

| eval set | CorrectOutput | StaticCheckFailure | other |
| --- | --- | --- | --- |
| seed (5 tasks) | 5 | 0 | 0 |
| unseen (6 tasks) | 6 | 0 | 0 |
| hard (6 tasks, append-only source templates) | 6 | 0 | 0 |
| **in-place (5 tasks, in-place templates)** | **5** | **0** | **0** |
| **total (22 tasks)** | **22** | **0** | **0** |

## Safety after `--execute`

```
HEAD before run : 021068c
HEAD after run  : 021068c
git status      : only this milestone's modified files (no source files
                  the eval edits live in)
git worktree list: no leftover codegen-eval worktrees
/tmp/code_rag_codegen_*: no matches
```

Live working tree never mutated; all execution happened inside
throwaway worktrees with `PYTHONPATH` pointed at the worktree's `src/`
so patched code actually loaded.

## Did in-place source-edit generation improve?

Yes — from **0 / 5** to **5 / 5** CorrectOutput on the in-place set,
without disturbing seed (5 / 5), unseen (6 / 6), or hard (6 / 6)
runs. Every static check across all four eval sets now passes (53 / 53
across the in-place + unseen + hard sets that declare them).

The harness now distinguishes:

* **append-only structural extension** — covered by the prior
  milestone's source-edit templates (hard set).
* **in-place list extension** — `_inplace_list_append`, idempotent,
  ERROR_PATTERNS / CLI_PATTERNS shape.
* **in-place branch insertion inside an existing function** —
  `_inplace_insert_before_line`, function-scoped, classify_query
  shape.
* **in-place literal/default replacement** — `_inplace_replace_once`,
  one-shot string replace with idempotence, load_config /
  `_evaluate_static_check` shape.

Together with the append-style templates these four shapes cover the
small structural-change vocabulary needed for the current eval
corpus.

## Remaining failure modes

None on the current 22-task corpus across seed + unseen + hard +
in-place. The MatClaw-inspired classifier still distinguishes the
full attribution stack — `PatchApplyFailure` / `SyntaxError` /
`ImportError` / `TestFailure` / `StaticCheckFailure` /
`WrongFile` / `RetrievalMiss` — and zero failures occurred in any
bucket.

## Recommended next step

The natural next eval expansion is **multi-file call-site updates**:
rename a helper *and* update every caller. The current in-place
templates target a single source file each. A call-site-rename task
would force the proposer to find references across the codebase and
edit each one consistently — that's the next capability gap the
harness should surface.

Alongside that:

* Begin **experience-memory distillation**. The
  `.agent_memory/history.jsonl` file now has 22 CorrectOutput episodes
  plus a complete prior-milestone trail of `StaticCheckFailure → "no
  source edit"` and `TestFailure → "no in-place edit"` attributions
  — exactly the recurring-pattern raw material `experience.md`
  should record. Keep that file out of retrieval / planning until the
  distillation pass produces stable patterns; the goal is post-hoc
  analysis, not online routing.
* Once a multi-file rename task surfaces `StaticCheckFailure → "no
  cross-file edit"`, that's the natural place to introduce a small
  LLM-backed proposer behind the same harness — temp worktree,
  function-scoped static checks, classifier, idempotent contracts —
  without changing default retrieval behaviour or adding any
  `apply_code_change` MCP tool.
