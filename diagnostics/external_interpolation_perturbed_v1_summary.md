# Perturbed External Interpolation — v1 Summary

Date: 2026-06-17

## Why this eval was added

The previous milestone made `scientific_driver_v1` pass all three
external interpolation tasks (`easy`, `medium`, `hard`) with
`CheckerPass` / `MATCH=True`. But the proposer is still a
**deterministic per-difficulty scaffold**: it dispatches on
`task.difficulty` and never reads the prompt body. That means we
can't tell from the original benchmark whether the system would
withstand a different wording of the same scientific task.

This milestone adds **perturbed prompts** that keep the math and the
configuration but reword the description (including synonyms like
`incompressible` for `divergence-free`, `kernel shape parameter` for
`epsilon`, `center count` for `N`). The runner now also writes a
per-script `script_metadata.json` carrying a conservative
`possible_overfit` signal so the perturbed runs surface scaffold
hardcoding even when the checker happens to pass.

## Task list

`evals/external_interpolation_tasks_perturbed.json` (3 tasks):

| id                                       | difficulty | perturbation_of                              | perturbation_kind     |
| ---------------------------------------- | ---------- | -------------------------------------------- | --------------------- |
| `external-easy-perturbed-wording`        | easy       | `external-easy-scalar-c4-matern`             | wording               |
| `external-medium-perturbed-wording`      | medium     | `external-medium-divergence-free-kernel`     | wording_and_synonyms  |
| `external-hard-perturbed-wording`        | hard       | `external-hard-divergence-free-kernel`       | wording_and_synonyms  |

Each task reuses the original ground-truth driver
(`easy_scalar_c4_matern_driver.py`, `medium_df_c4_matern_driver.py`,
`hard_local_dfphs_poly_driver.py`) so `checker.py` remains the
objective evaluator. Only the *prompt* text changed.

Prompt fixture files (new):

- `evals/external_interpolation/prompt_easy_perturbed.txt`
- `evals/external_interpolation/prompt_medium_perturbed.txt`
- `evals/external_interpolation/prompt_hard_perturbed.txt`

## Original vs perturbed result table

```bash
QDRANT_COLLECTION=code_chunks_kernelpack_ram \
QDRANT_ENABLE_SPARSE_VECTORS=true \
python scripts/evaluate_external_interpolation.py \
  evals/external_interpolation_tasks_perturbed.json \
  --generator scientific_driver_v1 \
  --repo_path /Users/whitney/src/kernelpack-python-ram \
  --generated_dir .../generated/external_interpolation_perturbed_v1 \
  --output    .../results/external_interpolation_perturbed_v1.json
```

| Difficulty | Original (regression rerun) | Perturbed                                |
| ---------- | --------------------------- | ----------------------------------------- |
| easy       | `CheckerPass`, MATCH=True  | `CheckerPass`, MATCH=True                |
| medium     | `CheckerPass`, MATCH=True  | `CheckerPass`, MATCH=True                |
| hard       | `CheckerPass`, MATCH=True  | `CheckerPass`, MATCH=True                |

(Original regression: `results/external_interpolation_original_regression_after_perturbed.json`.)

## Checker outcomes

All six runs (3 original + 3 perturbed): exit 0, `MATCH=True`, schema
matches per difficulty, all numeric rows within
`atol=1e-8, rtol=1e-6`.

## Retrieval required-symbol table

Retrieval is **invariant** under prompt perturbation because
`scientific_retrieval.build_scientific_retrieval_queries` is keyed on
difficulty, not on prompt text. The matched / missing required-symbol
sets are therefore identical between the original and perturbed runs:

| Difficulty | matched required symbols                                                                | missing | retrieval_conditioned |
| ---------- | --------------------------------------------------------------------------------------- | ------- | --------------------- |
| easy       | `RBF`, `Matern`, `interpolation` (3 of 3)                                              | none    | True                  |
| medium     | `dfc4_matern_blocks`, `DivFreeGram`, `DivFreePHSInterpolant`, `divergence free` (4 of 4) | none    | True                  |
| hard       | `DFPHS`, `LocalDivFreeInterpolator`, `df_poly_basis_from_jacobi`, `divfree_gram_matrix` (4 of 4) | none    | True                  |

## Generated queries (per difficulty)

| Difficulty | focused queries                                                                                                                                                              |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| easy       | `C4 Matern scalar radial basis function interpolation`, `global scalar RBF interpolant`, `relative L2 error interpolation ablation`                                            |
| medium     | `divergence free C4 Matern kernel`, `dfc4_matern_blocks`, `DivFreeGram`, `divergence free vector interpolation`, `conservation of mass kernel`                                 |
| hard       | `DFPHS divergence free polyharmonic spline`, `LocalDivFreeInterpolator`, `df_poly_basis_from_jacobi`, `local divergence free interpolation polynomial`, `divfree gram matrix stencil` |

## Selected files / symbols (perturbed runs)

- easy: files include `src/kernelpack/rbffd/core.py`,
  `src/kernelpack/divfree/core.py`,
  `src/kernelpack/geometry/core.py`. Top symbols include
  `initialize_geometry`, `dfc4_matern_blocks`,
  `_solve_augmented_rbf_system`.
- medium: files include `src/kernelpack/divfree/__init__.py`,
  `src/kernelpack/divfree/core.py`, `src/kernelpack/_numba.py`.
  Top symbols include `dfc4_matern_blocks`, `DFPHS`,
  `LocalDivFreeInterpolator`, `DivFreePHSInterpolant`.
- hard: files include `src/kernelpack/divfree/core.py`,
  `src/kernelpack/divfree/__init__.py`,
  `src/kernelpack/rbffd/core.py`. Top symbols include
  `DivFreePHSInterpolant`, `DFPHS`, `LocalDivFreeInterpolator`,
  `DivFreeGram`.

README chunks were absent from every perturbed run's top results
(carried over from the v2 scientific retrieval milestone).

## Possible-overfit signals

The new `analyze_script` detector compares each canonical scaffold
constant against the perturbed prompt and the retrieved chunks. The
script-metadata payload (one per archive, under
`generated/external_interpolation_perturbed_v1/<id>/script_metadata.json`)
reports:

| Difficulty | possible_overfit | flagged signal                                                                                              |
| ---------- | ---------------- | ----------------------------------------------------------------------------------------------------------- |
| easy       | True             | `SEED=4` hardcoded in generated script but absent from prompt and retrieved context                          |
| medium     | True             | `SEED=7` hardcoded in generated script but absent from prompt and retrieved context                          |
| hard       | True             | `SEED=12` hardcoded in generated script but absent from prompt and retrieved context                         |

`NODE_COUNTS=[50, 100, 500, 1000, 2000]` is *not* flagged on any
difficulty because every perturbed prompt explicitly lists those
values. `EPSILONS=[0.75, 1.5, 3.0]` (easy) and
`EPSILONS=[0.5, 1.0, 2.0]` (medium) are not flagged either — the
retrieved KernelPack code (test fixtures, default arguments) happens
to contain those numbers, so the detector's
"prompt OR retrieval" criterion is satisfied. Hard `ORDERS=[4, 6]`
is mentioned in the perturbed prompt directly ("polynomial orders
are 4 and 6"), so it is not flagged.

**Interpretation.** The single robust overfit signal is `SEED`. The
perturbed prompts (and the original prompts) all say "fixed random
seed" without specifying a value; the scaffold picks 4 / 7 / 12 to
match the ground-truth drivers. Replacing the scaffolds with a real
LLM proposer must learn to read the prompt's seed (or, more honestly,
emit a clearly-marked free choice that the checker will tolerate via
some seed-agnostic comparison).

## Whether perturbed prompts still pass

Yes — all three perturbed prompts hit `CheckerPass`. But the
`possible_overfit=True` signal makes clear that this is a *scaffold
match*, not a *prompt-reading proposer*: the script content is byte-
identical to the original-prompt scaffold of the same difficulty
(every prompt at the same difficulty yields the same hash). The
identical `generated_script_hash` between the original and perturbed
runs is independent evidence of the same conclusion.

## What failures reveal

There are no checker failures to triage. The "failure" surfaced by
this milestone is structural rather than numerical: the proposer is
generating the same script regardless of prompt wording. The
diagnostics correctly identify this via:

1. `possible_overfit=True` from `analyze_script`.
2. Identical `generated_script_hash` between original and perturbed
   runs of the same difficulty.
3. The `generated_retrieval_queries` from `ProposerDiagnostics`
   being constant across prompts of the same difficulty (because the
   query builder is difficulty-keyed).

## Safety

- All archived bundles live under
  `code-rag-experiments/generated/external_interpolation_perturbed_v1/`
  and `code-rag-experiments/generated/external_interpolation_original_regression_after_perturbed/`,
  outside both `code_rag` and `kernelpack-python-ram`.
  A unit test asserts that `_archive_run_artifacts` writes outside
  the live repo.
- `evals/external_interpolation/` fixtures are untouched (the
  perturbed prompts are new files, not edits to the originals).
- Default `search_codebase` retrieval and MCP tools are unchanged —
  the scientific retrieval path is opt-in via runner flag and is the
  default only when `--generator scientific_driver_v1` is selected.
- No `apply_code_change` MCP tool added.

## Validation

- `ruff check .` — clean.
- `pytest -m "not integration"` — **1179 passed, 4 deselected**
  (up from 1154; 12 new in
  `tests/test_overfit_diagnostics.py`, 12 in
  `tests/test_external_interpolation_perturbed_tasks.py`, 1 new
  runner-archive test).

## Recommended next step

The decision-criteria pick is clear: **perturbed tasks pass and
required symbols are present, but the diagnostics show hardcoded
scaffold constants.** Two parallel moves:

1. **Replace the deterministic scaffolds with an LLM-backed
   proposer behind the same checker harness.** The seam is
   `propose_standalone_driver(...) -> (source_code, diagnostics)`;
   the LLM call should consume the focused retrieval context the
   scientific retrieval layer already returns. Gate on
   `diagnostics.retrieval_conditioned` for fallback to the
   deterministic scaffold.
2. **Add a parameter-extraction layer** that pulls constants from
   the prompt (seed, epsilon list, polynomial orders, node counts)
   and threads them into the proposer's render step, so the
   generated script reflects what the prompt asked for rather than
   what the scaffold remembers. This will turn the current
   `SEED=4 not in prompt` overfit signal into an actionable input.

Either move keeps the checker as the objective evaluator and keeps
generated scripts in temp dirs or experiment outputs only.
