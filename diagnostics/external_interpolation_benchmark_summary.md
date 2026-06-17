# External Interpolation Benchmark — Milestone Summary

Date: 2026-06-17

This milestone adds a checker-based **external scientific-code benchmark** to
the code-rag project. Unlike the existing patch-based codegen evals, this
benchmark asks the system to generate a **standalone scientific driver
script** whose emitted error file numerically matches a ground-truth
driver's, under `checker.py` comparison.

## Files added (main repo)

- `evals/external_interpolation/checker.py` — runs two drivers in isolated
  temp dirs, parses `*_errors.txt`, compares with `--atol`/`--rtol`,
  prints `MATCH=True`/`MATCH=False`.
- `evals/external_interpolation/prompt_easy.txt`
- `evals/external_interpolation/prompt_medium.txt`
- `evals/external_interpolation/prompt_hard.txt`
- `evals/external_interpolation/easy_scalar_c4_matern_driver.py`
- `evals/external_interpolation/medium_df_c4_matern_driver.py`
- `evals/external_interpolation/hard_local_dfphs_poly_driver.py`
- `evals/external_interpolation_tasks.json`
- `src/code_rag/codegen/external_eval.py` — outcome constants, manifest
  loader, checker output parser, classification, temp-script
  materialization, and `run_checker()`. Read-only. No `apply_code_change`.
- `scripts/evaluate_external_interpolation.py` — CLI runner that loads the
  manifest, retrieves context from the indexed `ram_branch`, generates a
  candidate driver into a temp directory, runs `checker.py`, and writes a
  result JSON record.
- `tests/test_external_interpolation_eval.py` — 20 unit tests covering
  manifest loading, checker output parsing, every classification branch,
  temp-dir behaviour, and live-repo no-mutation safety.

## Task manifest

`evals/external_interpolation_tasks.json` defines three tasks:

| id                                             | difficulty | requires_kernelpack_branch | schema                              |
| ---------------------------------------------- | ---------- | -------------------------- | ----------------------------------- |
| `external-easy-scalar-c4-matern`               | easy       | false                      | `N epsilon rel_l2`                  |
| `external-medium-divergence-free-kernel`       | medium     | true                       | `N epsilon rel_l2_u rel_l2_v rel_l2_vec` |
| `external-hard-divergence-free-kernel`         | hard       | true                       | `poly_order N rel_l2_u rel_l2_v rel_l2_vec` |

## Outcome classification

`src/code_rag/codegen/external_eval.py` defines:

- `CheckerPass`
- `CheckerFailure`
- `GeneratedScriptRuntimeError`
- `GroundTruthRuntimeError`
- `OutputSchemaMismatch`
- `NumericalMismatch`
- `NoErrorFileProduced`
- `RetrievalMiss`
- `UnknownFailure`

The classifier reads `MATCH=True`/`MATCH=False`, schema lines, and stderr
markers (`CalledProcessError`, `No error text file found`,
`Schema mismatch`, `Metric mismatch`) and maps them to the constants
above. Ground-truth vs generated-script subprocess failures are
disambiguated via the `script_a`/`script_b` and `_driver.py` markers in
the checker's traceback.

## KernelPack `ram_branch`

- Clone path: `/Users/whitney/src/kernelpack-python-ram`
- Source: `https://github.com/ShankarLab/kernelpack-python.git`, branch
  `ram_branch`.
- Layout: includes `src/kernelpack/{divfree,rbffd,nodes,poly,solvers,geometry,domain}`,
  `examples/`, `tests/`, `scripts/`.

## Indexing command

```bash
QDRANT_COLLECTION=code_chunks_kernelpack_ram \
QDRANT_DEFAULT_DENSE_VECTOR_NAME=dense \
QDRANT_ENABLE_SPARSE_VECTORS=true \
python scripts/ingest_repo.py /Users/whitney/src/kernelpack-python-ram \
  --repo ShankarLab/kernelpack-python \
  --branch ram_branch \
  --enable_sparse_vectors
```

Result: **775 chunks ingested** into Qdrant collection
`code_chunks_kernelpack_ram` with sparse vectors enabled. Default user-
facing collection `code_chunks` is untouched.

## Retrieval smoke tests

Top-1 chunk for each diagnostic query against
`code_chunks_kernelpack_ram` (mode=hybrid, top_k=3, native sparse+dense):

| Query                                       | Top-1 symbol                  | File                                  |
| ------------------------------------------- | ----------------------------- | ------------------------------------- |
| `C4 Matern kernel`                          | `dfc4_matern_blocks`          | `src/kernelpack/divfree/core.py`      |
| `radial basis function interpolation`       | `initialize_geometry`         | `src/kernelpack/rbffd/core.py`        |
| `divergence free kernel`                    | `DFPHS`                       | `src/kernelpack/divfree/core.py`      |
| `conservation of mass kernel`               | `_evaluate_dfphs_entry`       | `src/kernelpack/divfree/core.py`      |
| `vector valued interpolation`               | `default_diff_order`          | `src/kernelpack/rbffd/core.py`        |
| `RBF-FD`                                    | `MultiSpeciesDiffusionSolver` | `src/kernelpack/solvers/...`          |
| `DFPHS divergence free polyharmonic spline` | `initialize`                  | `src/kernelpack/divfree/core.py`      |
| `global RBF interpolant`                    | `evaluate_gradient`           | `src/kernelpack/geometry/core.py`     |

Full retrieval smoke results: `diagnostics/external_interpolation_retrieval_smoke.txt`.

Key signal: the divergence-free kernel implementations needed for the
medium/hard tasks (`dfc4_matern_blocks`, `DFPHS`, `DivFreePHSInterpolant`,
`divfree_gram_matrix`) are surfaced at top-1/top-2 by the relevant
queries.

## Easy checker result

Command:

```bash
QDRANT_COLLECTION=code_chunks_kernelpack_ram \
QDRANT_ENABLE_SPARSE_VECTORS=true \
python scripts/evaluate_external_interpolation.py \
  evals/external_interpolation_tasks.json \
  --task external-easy-scalar-c4-matern \
  --repo_path /Users/whitney/src/kernelpack-python-ram \
  --output /Users/whitney/src/code-rag-experiments/results/external_interpolation_easy.json
```

Result: **`CheckerPass`** with `MATCH=True`.

- Generated script: temp path under `/var/folders/.../ragsystem_easy_*/ragcode.py`
  (cleaned up after run; `--keep_generated` preserves it).
- Schema A: `easy`, schema B: `easy`.
- 15 configuration rows (`N x epsilon` over `[50, 100, 500, 1000, 2000]`
  and `[0.75, 1.5, 3.0]`) all matched within `atol=1e-8, rtol=1e-6`.
- Checker stderr: only the benign matplotlib font-cache build notice and
  a `FigureCanvasAgg is non-interactive` warning from `plt.show()`.

Full JSON: `results/external_interpolation_easy.json`.

**Note on the baseline.** For the easy task the
`deterministic_easy` generator uses the ground-truth driver as a
deterministic stand-in for "what a correct generator would produce."
This is a **harness proof**, not a claim that the proposer is solving
the task — it demonstrates that the manifest, retrieval glue, temp-dir
materialization, checker invocation, output parsing, and classification
all work end-to-end. The real-proposer integration for the easy task is
the next milestone for the `easy` row.

## Sanity check on the checker for medium/hard

Running every difficulty with `--generator ground_truth_baseline`
produces `CheckerPass` for all three:

```
[external-easy-scalar-c4-matern]            outcome=CheckerPass MATCH=True
[external-medium-divergence-free-kernel]    outcome=CheckerPass MATCH=True
[external-hard-divergence-free-kernel]      outcome=CheckerPass MATCH=True
```

This confirms the checker, schema detection (easy / medium / hard), and
runner can drive the full benchmark surface; medium/hard ground-truth
drivers execute cleanly in temp dirs and emit `*_errors.txt` files that
parse against the expected schemas.

Full JSON: `results/external_interpolation_ground_truth_sanity.json`.

## Placeholder behaviour for medium/hard

Running medium/hard under `--generator deterministic_easy` (the default)
yields `GeneratedScriptRuntimeError` because the placeholder generator
deliberately exits non-zero with a clear failure note:

```
[external-medium-divergence-free-kernel] outcome=GeneratedScriptRuntimeError generator=placeholder_non_easy retrieved=4
[external-hard-divergence-free-kernel]   outcome=GeneratedScriptRuntimeError generator=placeholder_non_easy retrieved=4
```

This is the intended baseline behaviour: until a real proposer pathway
exists for divergence-free / local-stencil tasks, the harness reports
honestly rather than silently succeed.

Full JSON: `results/external_interpolation_medium_hard_baseline.json`.

## Safety

- Generated scripts live under the system temp root, never inside the
  live repo. A unit test asserts this.
- The fixture directory `evals/external_interpolation/` is unchanged
  after a run. A unit test asserts this.
- No `apply_code_change` MCP tool was added (none exists in this
  project).
- Default retrieval behaviour is unchanged; the runner uses the standard
  `search_codebase` entry point.
- Indexing went to a dedicated collection `code_chunks_kernelpack_ram`;
  the user-facing default collection `code_chunks` was not touched.

## Readiness for medium and hard

- Ground-truth drivers run cleanly under the checker (verified).
- Required divergence-free kernel symbols are retrievable from the
  indexed `ram_branch` (verified).
- The harness, manifest, and classification cover the medium and hard
  schemas (`N epsilon rel_l2_u rel_l2_v rel_l2_vec` and
  `poly_order N rel_l2_u rel_l2_v rel_l2_vec`).
- The **generator** for medium/hard is the only thing not yet built:
  the current `placeholder` deliberately fails, and `deterministic_easy`
  only handles the easy task. Until a real proposer is wired up,
  medium/hard will surface as `GeneratedScriptRuntimeError` with a
  clear note.

## Next recommended step

Add a real proposer pathway for the external scientific-driver setting
(scoped to the standalone-script shape, not patch generation against the
live repo), then re-run all three difficulties:

```bash
QDRANT_COLLECTION=code_chunks_kernelpack_ram \
QDRANT_ENABLE_SPARSE_VECTORS=true \
python scripts/evaluate_external_interpolation.py \
  evals/external_interpolation_tasks.json \
  --repo_path /Users/whitney/src/kernelpack-python-ram \
  --output /Users/whitney/src/code-rag-experiments/results/external_interpolation_proposer.json
```

If the proposer fails on medium/hard, the classification already
distinguishes:

- `OutputSchemaMismatch` -> output formatting bug,
- `NumericalMismatch` -> kernel formula / node generation / solve path,
- `GeneratedScriptRuntimeError` -> import / output-path / runtime issue,
- `RetrievalMiss` -> indexing / chunking improvement on `ram_branch`.

## Validation

- `ruff check .` — clean.
- `pytest -m "not integration"` — **1112 passed, 4 deselected**.
- New tests: 20 in `tests/test_external_interpolation_eval.py`.