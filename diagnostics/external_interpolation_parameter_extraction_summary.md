# Parameter Extraction — External Interpolation Summary

Date: 2026-06-17

## Why this milestone

The perturbed-prompts milestone surfaced one robust overfit signal:
the scaffolds in `scientific_driver_v1` hardcode the rng seed
(4 / 7 / 12 by difficulty), and the seed never appears in the
prompts or in the retrieved chunks. The previous detector reported
this with a single text-matching rule: "SEED in script but not in
prompt/retrieval."

That rule was correct but coarse — it conflated three different
states ("user told us in the prompt", "retrieved code happens to
contain the number", "we made it up because nobody said anything").
This milestone replaces the text-matching with a **provenance-aware
parameter extractor**: every benchmark-critical constant is now
attributed to one of `prompt` / `retrieval` / `manifest` /
`fallback_default` / `missing`, and the overfit detector flags
specifically the `fallback_default` and `missing` cases.

## Original result table

```bash
QDRANT_COLLECTION=code_chunks_kernelpack_ram \
QDRANT_ENABLE_SPARSE_VECTORS=true \
python scripts/evaluate_external_interpolation.py \
  evals/external_interpolation_tasks.json \
  --generator scientific_driver_v1 \
  --repo_path /Users/whitney/src/kernelpack-python-ram \
  --generated_dir   .../generated/external_interpolation_original_after_params \
  --output          .../results/external_interpolation_original_after_params.json
```

| Task                                       | Checker outcome | Match |
| ------------------------------------------ | --------------- | ----- |
| `external-easy-scalar-c4-matern`           | CheckerPass     | True  |
| `external-medium-divergence-free-kernel`   | CheckerPass     | True  |
| `external-hard-divergence-free-kernel`     | CheckerPass     | True  |

## Perturbed result table

```bash
QDRANT_COLLECTION=code_chunks_kernelpack_ram \
QDRANT_ENABLE_SPARSE_VECTORS=true \
python scripts/evaluate_external_interpolation.py \
  evals/external_interpolation_tasks_perturbed.json \
  --generator scientific_driver_v1 \
  --repo_path /Users/whitney/src/kernelpack-python-ram \
  --generated_dir   .../generated/external_interpolation_perturbed_after_params \
  --output          .../results/external_interpolation_perturbed_after_params.json
```

| Task                                       | Checker outcome | Match |
| ------------------------------------------ | --------------- | ----- |
| `external-easy-perturbed-wording`          | CheckerPass     | True  |
| `external-medium-perturbed-wording`        | CheckerPass     | True  |
| `external-hard-perturbed-wording`          | CheckerPass     | True  |

## Extracted parameters per task

(Identical between original and perturbed runs at each difficulty —
the perturbed prompts preserve every config constant.)

### easy
```json
{
  "seed": 4,
  "node_counts": [50, 100, 500, 1000, 2000],
  "epsilons": [0.75, 1.5, 3.0],
  "evaluation_size": 500,
  "domain": [-1.0, 1.0],
  "output_schema": "easy"
}
```

### medium
```json
{
  "seed": 7,
  "node_counts": [50, 100, 500, 1000, 2000],
  "epsilons": [0.5, 1.0, 2.0],
  "evaluation_size": 500,
  "domain": [-1.0, 1.0],
  "output_schema": "medium"
}
```

### hard
```json
{
  "seed": 12,
  "node_counts": [50, 100, 500, 1000, 2000],
  "poly_orders": [4, 6],
  "evaluation_size": 500,
  "domain": [-1.0, 1.0],
  "output_schema": "hard"
}
```

## Parameter source table

| Field            | Easy             | Medium           | Hard             |
| ---------------- | ---------------- | ---------------- | ---------------- |
| seed             | fallback_default | fallback_default | fallback_default |
| node_counts      | prompt           | prompt           | prompt           |
| epsilons         | fallback_default | fallback_default | n/a              |
| poly_orders      | n/a              | n/a              | prompt           |
| evaluation_size  | prompt           | prompt           | prompt           |
| domain           | prompt           | prompt           | prompt           |
| output_schema    | prompt           | prompt           | prompt           |

Notes:

* The original and perturbed prompts both explicitly state node
  counts, the `[-1, 1] x [-1, 1]` domain, the eval size (500), and
  the output column header — those four resolve to `prompt`.
* Neither set of prompts states the rng seed — every difficulty
  resolves the seed to `fallback_default`.
* Easy and medium prompts use phrasing like *"kernel shape
  parameter"* without specifying the values — the epsilon list also
  falls back. Hard's prompt explicitly lists `4 and 6` for the
  polynomial orders, so `poly_orders` resolves to `prompt`.

## Fallback defaults used

| Difficulty | fallback_defaults_used     |
| ---------- | -------------------------- |
| easy       | `seed`, `epsilons`         |
| medium     | `seed`, `epsilons`         |
| hard       | `seed`                     |

## Overfit signals before / after

The detector now uses the source labels above. A constant is flagged
only when it appears in the generated script **and** its source is
`fallback_default` or `missing`.

| Task                            | v1 (perturbed milestone)          | v2 (this milestone)                                |
| ------------------------------- | --------------------------------- | -------------------------------------------------- |
| easy (original + perturbed)     | `SEED` only                       | `SEED` + `EPSILONS` (both fallback_default)        |
| medium (original + perturbed)   | `SEED` only                       | `SEED` + `EPSILONS` (both fallback_default)        |
| hard (original + perturbed)     | `SEED` only                       | `SEED` only (poly_orders correctly tracked to prompt) |

The v2 detector flags more aggressively because the v1 text-matcher
unflagged `EPSILONS` whenever any of the values `0.75 / 1.5 / 3.0` or
`0.5 / 1.0 / 2.0` happened to appear in retrieved code (test
fixtures, default arguments). The provenance-aware detector only
trusts a value when retrieval surfaces it as an explicit
"epsilon" / "shape parameter". This is the intended sharper signal.

## Whether seed hardcoding is now explained by manifest or still suspicious

Still suspicious **for the existing manifests**: neither
`evals/external_interpolation_tasks.json` nor
`evals/external_interpolation_tasks_perturbed.json` declares an
`expected_parameters.seed`, so the seed resolves to
`fallback_default` and the overfit detector keeps flagging it.

The runner already supports the manifest-explained path. The unit
test `test_runner_archive_uses_manifest_expected_parameters` builds a
synthetic task with `expected_parameters={"seed": 7, "epsilons": [0.5, 1.0, 2.0]}`
and verifies that:

* `metadata["parameter_sources"]["seed"] == "manifest"`
* `metadata["parameter_sources"]["epsilons"] == "manifest"`
* `"seed"` and `"epsilons"` no longer appear in
  `metadata["fallback_defaults_used"]`
* no `SEED` or `EPSILONS` overfit signal is emitted

So the resolution is one manifest edit away — adding
`expected_parameters` to a task is enough to mark its seed/epsilons
as manifest-explained. We deliberately left the existing manifests
untouched so the current diagnostics keep the strongest possible
signal until the LLM-backed proposer lands.

## Validation

- `ruff check .` — clean.
- `pytest -m "not integration"` — **1218 passed, 4 deselected**
  (up from 1179; 29 new in
  `tests/test_parameter_extraction.py`, 4 in
  `tests/test_overfit_diagnostics.py`, 3 in
  `tests/test_standalone_driver_proposer.py`, 3 in
  `tests/test_external_interpolation_eval.py`).

## Safety

- Generated bundles live under
  `code-rag-experiments/generated/external_interpolation_original_after_params/`
  and `.../external_interpolation_perturbed_after_params/` — outside
  both `code_rag` and `kernelpack-python-ram`. Unit tests assert
  this.
- `evals/external_interpolation/` fixtures unchanged.
- Default `search_codebase` and MCP tools unchanged. The scientific
  retrieval path is still opt-in for the external eval runner.
- No `apply_code_change` added.

## Recommendation for the LLM-backed proposer

The seam is now in place:

1. `extract_parameters(prompt_text, retrieved_context, manifest_metadata)`
   returns an `ExtractedParameters` snapshot with a source label per
   field. The LLM-backed proposer can call it and decide whether to
   trust the prompt, the manifest, or its own internal default.
2. `ProposerDiagnostics` carries the snapshot through
   (`extracted_parameters`, `parameter_sources`,
   `fallback_defaults_used`, `missing_parameters`).
3. `analyze_script(parameters=...)` reads the source labels to
   decide overfit. The LLM-backed proposer will get an automatic
   "no signal" the moment it threads prompt-derived constants
   into its emitted script instead of static defaults.

Recommended next step:

> Build the LLM-backed proposer behind the same
> `propose_standalone_driver(...) -> (source_code, diagnostics)`
> interface, with the renderer consuming
> `diagnostics.extracted_parameters` and falling back to the current
> scaffold when `diagnostics.retrieval_conditioned` is `False`.

When that lands, the natural diagnostic improvement is: every
constant that the LLM threads from the prompt moves from
`fallback_default` to `prompt`, and the SEED overfit signal goes
away under both manifests without any further changes to the
detector or manifests.
