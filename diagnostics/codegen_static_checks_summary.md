# Static checks for meaningful codegen evals

`evals/code_generation_tasks_unseen.json` (6 tasks). All runs use
`QDRANT_DEFAULT_DENSE_VECTOR_NAME=dense`. The eval contract is tightened
in two coordinated ways:

1. Each unseen task now declares **function-scoped** `static_checks` — a
   `contains` marker must appear inside the AST source segment of the
   named function, not anywhere in the file. This blocks the previous
   "marker already lives in another test in the same file" loophole.
2. The generic add_test handler now matches **behaviour templates** that
   emit real assertions referencing the task's named symbols, with
   automatic import insertion (multi-line parenthesized imports honored).
   When no template matches, the handler falls back to `assert True` and
   the static checks correctly reject it.

A new outcome label, **`StaticCheckFailure`**, sits between `TestFailure`
and `CorrectOutput`: it triggers when `pytest -k <slug>` exits 0 but at
least one static check failed.

## Outcome progression (unseen set)

| task | TODO fallback | + generic (assert True) | + templates + static checks |
| --- | --- | --- | --- |
| unseen-sparse-dotted-module-router | TestFailure | CorrectOutput (trivial) | **CorrectOutput (meaningful)** |
| unseen-router-dense-vector-name-config | TestFailure | CorrectOutput (trivial) | **CorrectOutput (meaningful)** |
| unseen-cli-routing-explanation-help | TestFailure | CorrectOutput (trivial) | **CorrectOutput (meaningful)** |
| unseen-diagnostic-category-counts | TestFailure | CorrectOutput (trivial) | **CorrectOutput (meaningful)** |
| unseen-experiment-mrr-default | TestFailure | CorrectOutput (trivial) | **CorrectOutput (meaningful)** |
| unseen-sparse-screaming-env-var | TestFailure | CorrectOutput (trivial) | **CorrectOutput (meaningful)** |

| outcome | TODO fallback | + generic (assert True) | + templates + static checks |
| --- | --- | --- | --- |
| CorrectOutput | 0 | 6 | **6** |
| TestFailure | 6 | 0 | 0 |
| StaticCheckFailure | n/a | n/a | 0 |
| PatchApplyFailure | 0 | 0 | 0 |
| WrongFile | 0 | 0 | 0 |
| RetrievalMiss | 0 | 0 | 0 |
| UnknownFailure | 0 (after fix) | 0 | 0 |

Each execute task carried **17 / 17** function-scoped static checks
passing.

## What the templates emit (excerpted)

* `unseen-sparse-dotted-module-router` →

  ```python
  def test_dotted_module_router_preserved():
      tokens = tokenize_for_sparse("code_rag.retrieval.router")
      assert "code_rag.retrieval.router" in tokens
      assert "code_rag" in tokens
      assert "retrieval" in tokens
      assert "router" in tokens
  ```

* `unseen-router-dense-vector-name-config` →

  ```python
  def test_dense_vector_name_config():
      assert _is_config_query(
          "Where is QDRANT_DEFAULT_DENSE_VECTOR_NAME configured?"
      ) is True
  ```

* `unseen-cli-routing-explanation-help` →

  ```python
  def test_routing_explanation_help():
      script = Path("scripts/search_repo.py").read_text()
      assert "--routing_explanation" in script
  ```

* `unseen-diagnostic-category-counts` builds two `QueryDiagnostic`
  records and asserts
  `summary.category_counts == {"symbol": 1, "technical": 1}`.

* `unseen-experiment-mrr-default` →

  ```python
  def test_retrieval_metrics_mrr_default():
      metrics = RetrievalMetrics()
      assert metrics.mrr == 0.0
      assert metrics.hit_at_5 == 0.0
  ```

* `unseen-sparse-screaming-env-var` →

  ```python
  def test_screaming_env_var_path_weight():
      weighted = dict(
          tokenize_for_sparse_weighted("QDRANT_DEFAULT_DENSE_VECTOR_NAME")
      )
      assert weighted["qdrant_default_dense_vector_name"] == PATH_LIKE_WEIGHT
  ```

Every required import is inserted by `_ensure_imports`. The helper uses
`ast.parse` to find the line *after* the last `Import` / `ImportFrom`
node, so parenthesized multi-line imports are honored (no more
mid-block insertion).

## Trivial-body regression test

A spot check confirms the tightened contract:

```
function body: assert True
pytest exit  : 0   ← collection + pass
static checks:
  contains 'tokenize_for_sparse'      → FAIL
  contains 'code_rag.retrieval.router' → FAIL
  contains 'assert'                    → PASS
final outcome: StaticCheckFailure (not CorrectOutput)
```

i.e., `assert True` no longer satisfies any unseen task.

## Seed-eval regression

Seed eval was re-run under `--execute` after the changes landed:

| task | handler | outcome |
| --- | --- | --- |
| router-test-add | `_handle_router_test_add` | CorrectOutput |
| sparse-tokenization-test-add | `_handle_sparse_tokenization_test_add` | CorrectOutput |
| readme-section-update | `_handle_readme_section_update` | CorrectOutput |
| config-parsing-test-add | `_handle_config_parsing_test_add` | CorrectOutput |
| routing-diagnostic-test-add | `_handle_routing_diagnostic_test_add` | CorrectOutput |

Seed eval tasks have no `static_checks` declared, so the new code path
is a no-op for them; the classifier still promotes them to
`CorrectOutput`. **5 / 5** preserved.

## Combined execute outcomes

| eval set | CorrectOutput | StaticCheckFailure | TestFailure | other |
| --- | --- | --- | --- | --- |
| seed (5 tasks, no static checks) | 5 | 0 | 0 | 0 |
| unseen (6 tasks, 17 static checks) | **6** | 0 | 0 | 0 |
| **total (11 tasks)** | **11** | 0 | 0 | 0 |

## Safety after `--execute`

```
HEAD before run : 35cb6cb
HEAD after run  : 35cb6cb
git status      : only this milestone's new/modified files
git worktree list: no leftover codegen-eval worktrees
/tmp/code_rag_codegen_*: no matches
```

All execution happened inside throwaway worktrees under
`/tmp/code_rag_codegen_*` and was cleaned up by `cleanup_worktree`.

## Remaining failure modes

None on the current seed + unseen set. The eval now distinguishes
five layers of failure:

* `PatchApplyFailure`: malformed diff.
* `SyntaxError` / `ImportError`: invalid generated Python.
* `TestFailure`: `pytest -k <slug>` failed.
* `StaticCheckFailure`: tests pass but the new function body does not
  reference the symbols the task names. **New in this milestone.**
* `WrongFile` / `RetrievalMiss`: file targeting / retrieval problems.

The static-check classifier short-circuits past `TestFailure`: a failing
`success_command` is reported as `TestFailure`, not silently downgraded.

## Recommended next step

Two parallel tracks remain useful:

1. **Expand to harder unseen tasks** that the existing templates cannot
   cover — multi-file changes, signature changes with call-site updates,
   tasks whose `success_command` is a behavioural assertion derived from
   a real bug. Each new shape that lands in `StaticCheckFailure` or
   `TestFailure` becomes a generation-quality signal pointing at the
   next template (or eventually at an LLM proposer).
2. **Start experience-memory distillation.** With 11 / 11 CorrectOutput
   episodes and explicit static-check attribution, `.agent_memory/`
   history is informative enough to begin grouping by handler and by
   failure layer in `experience.md`. Keep that file out of retrieval and
   planning until the distillation pass produces stable patterns.
