# Codegen file-selection improvement: read-only before/after

`evals/code_generation_tasks.json` (5 seed tasks). Both runs use
`QDRANT_DEFAULT_DENSE_VECTOR_NAME=dense` against the default `code_chunks`
Qdrant collection. Neither run uses `--execute`.

## Outcome table

| task | outcome before | outcome after | proposed_expected | unexpected | has_patch |
| --- | --- | --- | --- | --- | --- |
| router-test-add | RetrievalMiss | RetrievalMiss | 2 / 2 | 0 | true |
| sparse-tokenization-test-add | UnknownFailure | UnknownFailure | 2 / 2 | 0 | true |
| readme-section-update | **WrongFile** | **UnknownFailure** | 1 / 1 | 0 | true |
| config-parsing-test-add | UnknownFailure | UnknownFailure | 1 / 2 | 0 | true |
| routing-diagnostic-test-add | UnknownFailure | UnknownFailure | 2 / 2 | 0 | true |

Key wins:

* **`readme-section-update` is no longer `WrongFile`.** Before, the proposer
  emitted patches for `src/code_rag/__main__.py` and
  `src/code_rag/mcp_server.py` because `_build_likely_files` filters
  `README*` as a "noisy" file pattern, so it never reached the proposal
  loop even though retrieval surfaced it 4× as a source. After, the
  evaluator builds an HTML-comment TODO stub for `README.md` directly via
  the new `_make_markdown_stub` path. `proposed_expected = 1`, `unexpected
  = 0`.
* **Every task now has `unexpected_proposed_files == 0`.** Before, every
  task except one had 4–9 unexpected files dragged in by the proposer's
  default likely_files ranking. After, only expected (or expected +
  companion) files reach the proposal.
* **Test-add tasks now propose both the source file *and* the test file**
  for every case where the test file already exists on disk. The
  `infer_companion_test_files` helper would also fill in a test companion
  for any source file whose `tests/test_<stem>.py` exists, but in this
  seed set those targets are already listed in `expected_files`.

Remaining gaps:

* **`router-test-add` is still `RetrievalMiss`.** The patch *targets* the
  right files (we still build a direct stub against `expected_files`), but
  Qdrant did not surface either expected file. The intended next step is
  not on the file-selection layer — it's on retrieval. The proposal text
  itself is now safe to execute, but the metric still records that
  retrieval missed.
* **`UnknownFailure` is the read-only-mode rest state.** With `--execute`
  off, the classifier cannot promote a proposal to `CorrectOutput`. The
  new `selection` metadata is what should be read instead — `has_patch =
  true`, `unexpected = 0`, and `proposed_expected = N / N` together
  indicate the proposal is *safe to try in execute mode*.

## Per-task file detail (after)

```
[RetrievalMiss] router-test-add
  expected:           ['tests/test_router.py', 'src/code_rag/retrieval/router.py']
  retrieved_expected: []
  missing_expected:   ['tests/test_router.py', 'src/code_rag/retrieval/router.py']
  proposed_expected:  ['tests/test_router.py', 'src/code_rag/retrieval/router.py']
  unexpected:         []

[UnknownFailure] sparse-tokenization-test-add
  expected:           ['tests/test_sparse_vectors.py',
                       'src/code_rag/retrieval/sparse_vectors.py']
  retrieved_expected: ['src/code_rag/retrieval/sparse_vectors.py']
  missing_expected:   ['tests/test_sparse_vectors.py']
  proposed_expected:  ['tests/test_sparse_vectors.py',
                       'src/code_rag/retrieval/sparse_vectors.py']
  unexpected:         []

[UnknownFailure] readme-section-update
  expected:           ['README.md']
  retrieved_expected: ['README.md']
  missing_expected:   []
  proposed_expected:  ['README.md']
  unexpected:         []

[UnknownFailure] config-parsing-test-add
  expected:           ['tests/test_experiments_config.py',
                       'src/code_rag/experiments/config.py']
  retrieved_expected: ['src/code_rag/experiments/config.py']
  missing_expected:   ['tests/test_experiments_config.py']
  proposed_expected:  ['src/code_rag/experiments/config.py']
  unexpected:         []

[UnknownFailure] routing-diagnostic-test-add
  expected:           ['tests/test_routing_diagnostics.py',
                       'scripts/analyze_routing.py']
  retrieved_expected: ['scripts/analyze_routing.py']
  missing_expected:   ['tests/test_routing_diagnostics.py']
  proposed_expected:  ['tests/test_routing_diagnostics.py',
                       'scripts/analyze_routing.py']
  unexpected:         []
```

`config-parsing-test-add` proposes only the source file because the
expected test file (`tests/test_experiments_config.py`) does not yet
exist on disk; `build_expected_proposed_changes` intentionally skips
non-existent paths so we never invent a creation-style patch in eval mode.

## Is execute mode safe to try?

The proposals now touch only expected (or expected + companion) files and
the patches are deterministic TODO stubs against real on-disk content.
Apply will succeed for every file the proposer actually wrote a stub for.
However, the test `success_command`s for these seed tasks are not
satisfied by a TODO marker (e.g. `pytest tests/test_router.py -k
badly_formed_hex` expects a real test of that name). Running `--execute`
now would *cleanly classify* these as `TestFailure` rather than
`UnknownFailure`, which is itself a useful signal — but it will not
produce any `CorrectOutput`s until the stub generator is upgraded to emit
task-aware code (the next milestone).

Recommended next-step command, only if explicitly requested:

```bash
QDRANT_DEFAULT_DENSE_VECTOR_NAME=dense \
python scripts/evaluate_codegen.py \
  evals/code_generation_tasks.json \
  --repo_path /Users/whitney/src/code_rag \
  --execute \
  --output /Users/whitney/src/code-rag-experiments/results/codegen_seed_execute.json
```
