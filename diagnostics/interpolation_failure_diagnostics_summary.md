# Interpolation Failure Diagnostics — Summary

Date: 2026-06-19

## Why this milestone

Ram and Jordan's eval notes pointed to specific failure categories
that the existing diagnostics couldn't surface:

* easy failed in another run because of an **epsilon grid mismatch**
  and a wrong **C^4 Matern formula** (Gaussian or expanded-product
  form);
* medium failed for the same epsilon reason even though retrieval had
  found `dfc4_matern_blocks`;
* hard failed because the generated driver sampled from the wrong
  box, used the wrong **PHS degree**, and/or the wrong **polynomial
  degree**.

The runner's metadata previously surfaced parameter-value mismatches
generically (`parameter_value_mismatch: seed=...`) but it did not
classify the failure by category, did not check the kernel formula
structure, did not check the sampling box, and did not check the
hard-task-specific degrees. This milestone adds those checks without
touching MCP, the default generator, or any production code path.

## What changed

### New module

`src/code_rag/codegen/kernel_diagnostics.py`:

- `analyze_kernel_formula(difficulty, source) -> dict`
  - easy: regex-detects `exp(-z)*(3+3z+z^2)` and the
    inlined-product variant `exp(-eps*r)*(3+3*eps*r+(eps*r)**2)`,
    plus `z*z` as a substitute for `z**2`.
  - medium: requires either the DF C^4 Matern symbol markers
    (`df_c4_blocks`, `dfc4_matern_blocks`, `DivFreeGram`,
    `divfree_gram_matrix`) **or** the block-structure fingerprint
    (`exp(-..)*(.. d[xy]**2 .. + 1)`).
  - hard: intentionally returns `matched=None` — hard structural
    detection lives in `analyze_hard_task` instead, since
    DFPHS+poly is harder to fingerprint with a single regex.
- `analyze_sampling_domain(source, expected_low=-1.0, expected_high=1.0) -> dict`
  - Detects `(low, high)` from `rng.uniform(...)` /
    `np.random.uniform(...)`, from `DOMAIN_LOW`/`DOMAIN_HIGH`
    constants, and from any `*_points`/`*_nodes`/`*_sample` call
    with two literal numbers as positional args. All three
    ground-truth drivers and the easy browser-replay response
    match this detector.
- `analyze_hard_task(source, expected_polynomial_orders, sampling_domain) -> dict`
  - Extracts `PHS_DEGREE` / `PHS_ORDER` and `POLY_DEGREE` /
    `POLYNOMIAL_DEGREE` constants from the script.
  - Compares the PHS-degree value against the per-order expected
    set derived via the same formula the hard scaffold uses
    (`phs_degree = min(poly+1 if (poly+1)%2==1 else poly+2, 7)`,
    so `[4, 6]` → `[5, 7]`).
  - Compares the polynomial-degree value against the
    `poly_orders` list.
  - When the script computes those degrees in a loop rather than
    declaring constants, the block reports `matched=None` with a
    `phs_degree_not_detected` / `polynomial_degree_not_detected`
    informational signal — no false-positive mismatch.
- `named_mismatch_signals(parameter_value_mismatches) -> list`
  - Turns each structured mismatch entry into a friendly named
    signal (`epsilon_grid_mismatch`,
    `node_count_grid_mismatch`, `poly_order_grid_mismatch`,
    `seed_mismatch`, `evaluation_size_mismatch`). The original
    free-form `parameter_value_mismatch` entries stay in place;
    these are additive.

### Runner-side wiring

`scripts/evaluate_external_interpolation.py`:

- `_build_script_metadata` now calls all three new analyzers and
  embeds the results under the keys
  `kernel_formula_diagnostics`, `sampling_diagnostics`,
  `hard_task_diagnostics` (only when the difficulty is `hard`),
  and `retrieval_found_required_symbols`.
- Every mismatch / structural-failure signal is appended to
  `overfit_signals` (dedup-aware). Informational
  `_undetected` / `_not_detected` signals stay out of
  `possible_overfit` so a script that simply computes a value in a
  loop is not flagged as failing.

### Metadata layout (one block per concern)

```json
{
  "retrieval_found_required_symbols": [...],
  "parameter_sources": {...},
  "script_parameters": {...},
  "parameter_value_mismatches": [...],
  "kernel_formula_diagnostics": {
    "expected": "scalar_c4_matern",
    "matched": true,
    "signals": []
  },
  "sampling_diagnostics": {
    "expected_low": -1.0, "expected_high": 1.0,
    "script_low": -1.0,   "script_high": 1.0,
    "matched": true, "signals": []
  },
  "hard_task_diagnostics": {
    "phs_degree":        {"script_value": null, "expected_for_orders": [5, 7], "matched": null},
    "polynomial_degree": {"script_value": null, "expected_orders": [4, 6], "matched": null},
    "sampling_domain":   {...},
    "signals": [...]
  },
  "overfit_signals": [...]
}
```

## Validation

- `ruff check .` — clean.
- `pytest -m "not integration"` — **1303 passed, 4 deselected**
  (up from 1276; +27 new across two test files).
- New tests:
  - `tests/test_kernel_diagnostics.py`: 24 tests covering every
    matched/mismatched/undetected branch for the easy C^4 Matern
    fingerprint, the medium DF C^4 Matern fingerprint, the
    intentional no-attempt on hard, the unit-square sampling
    detector (rng.uniform, DOMAIN_LOW/HIGH constants, and
    `distinct_uniform_points(...)` calls), the wrong-box flag, the
    hard PHS / polynomial degree extraction and mismatch flags,
    and the `named_mismatch_signals` helper for every supported
    field name.
  - `tests/test_external_interpolation_eval.py`: 3 new
    runner-level tests confirming that
    `script_metadata.json` carries the new
    `kernel_formula_diagnostics`,
    `sampling_diagnostics`,
    `hard_task_diagnostics`,
    `retrieval_found_required_symbols` keys; that the friendly
    `epsilon_grid_mismatch` signal appears alongside the existing
    `parameter_value_mismatch` entry; and that the hard block fires
    `phs_degree_mismatch` / `polynomial_degree_mismatch` when the
    script declares wrong constants.

## Smoke runs

Three runs against the easy task using the existing safe paths
(no API call):

| Run                                       | Provider     | Outcome             | kernel_formula | sampling | named-signal samples |
| ----------------------------------------- | ------------ | ------------------- | -------------- | -------- | -------------------- |
| `interp_diagnostics_fake_easy`            | fake_easy    | CheckerPass         | matched=True   | matched=True | seed_mismatch (existing, from retrieval-vs-script seed) |
| `interp_diagnostics_easy_browser_replay`  | replay (browser) | CheckerPass     | matched=True   | matched=True | seed_mismatch (same) |
| `interp_diagnostics_easy_wrong`           | replay (intentional) | **NumericalMismatch** | matched=False  | matched=False (`[0, 1]`) | epsilon_grid_mismatch, node_count_grid_mismatch, seed_mismatch, kernel_formula_mismatch, sampling_domain_mismatch |

The intentionally-wrong replay uses a Gaussian RBF on `[0, 1]^2`
with an off-grid epsilon list, off-grid node counts, and a wrong
seed. **All five** new diagnostic signals fire end-to-end alongside
the existing `parameter_value_mismatch` entries, and the checker
correctly reports `NumericalMismatch`.

The two healthy runs (`fake_easy` and the browser-captured replay
from the prior milestone) remain `CheckerPass` with
`kernel_formula_diagnostics.matched=True` and
`sampling_diagnostics.matched=True`. The persistent
`seed_mismatch` named signal is the same `default_rng(17)` issue
already documented in the parameter-extraction summary — it does
not change pass/fail; it just makes the cause visible.

## Recommended next step

Three actionable signals are now first-class:

1. `epsilon_grid_mismatch` — pair the runner with a one-line
   suggestion to backfill `expected_parameters.epsilons` in the
   manifest, since the prompt does not currently specify the
   epsilon list and the LLM has to guess.
2. `kernel_formula_mismatch` — tighten the prompt packet's CHECKER
   CONTRACT to include the literal C^4 Matern formula. The
   diagnostic now provides the regression signal we need to tell
   whether the packet change moved the needle.
3. `phs_degree_mismatch` / `polynomial_degree_mismatch` — same
   prompt-packet improvement for hard. When we replay the hard
   browser response next, these blocks will tell us whether the
   model hardcoded a wrong constant or computed it correctly per
   poly-order.

Either move is unblocked and model-independent: each can be
verified with the existing `--llm_provider fake_*` and
`--llm_provider replay` paths.
