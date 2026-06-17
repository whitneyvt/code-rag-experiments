# Anthropic LLM Smoke — External Interpolation Summary

Date: 2026-06-17

## Provider setup state

| check                         | result                                                                |
| ----------------------------- | --------------------------------------------------------------------- |
| Anthropic SDK installed       | **yes** — `anthropic 0.109.2` installed via `pip install anthropic`. |
| `ANTHROPIC_API_KEY` set       | **no** — not in shell env, not in `code_rag/.env`.                   |
| Provider construction         | **not_attempted** — short-circuits on the missing API key.            |
| Real model call attempted     | **no** — explicitly skipped per user instruction.                     |

The infrastructure to run the LLM provider is now in place, but no
real model call has been made. Per the user's instruction we have
*not* committed any API key, *not* edited `.env` to add one, and
*not* probed the model.

## Runner classification (confirmation only — no model call)

```bash
QDRANT_COLLECTION=code_chunks_kernelpack_ram \
QDRANT_ENABLE_SPARSE_VECTORS=true \
python scripts/evaluate_external_interpolation.py \
  evals/external_interpolation_tasks.json \
  --task external-easy-scalar-c4-matern \
  --generator llm_scientific_driver_v1 \
  --llm_provider anthropic \
  --repo_path /Users/whitney/src/kernelpack-python-ram \
  --generated_dir .../generated/llm_scientific_driver_v1_easy_anthropic_real \
  --output       .../results/llm_scientific_driver_v1_easy_anthropic_real.json
```

- Outcome: **`LLMProviderUnavailable`**.
- `notes`: `LLM provider 'anthropic' unavailable: ANTHROPIC_API_KEY environment variable is not set`.
- No `ragcode.py`, no `llm_prompt_packet.txt`, no `llm_raw_response.txt`
  were produced — the runner detected the unavailability before
  constructing the client, so there is nothing for the model to have
  emitted.

This is the clean-classification path called out in the milestone
decision criteria. The runner does not crash, does not call the model,
does not silently fall through.

The provider-check script reports the same state independently:

```
$ python scripts/check_llm_provider.py --provider anthropic
provider=anthropic sdk=available api_key=missing client=not_attempted test_generation=skipped ready=no
  notes: set the ANTHROPIC_API_KEY environment variable to enable this provider
```

(exit code 2)

## Easy original outcome

Not run — provider unavailable. See classification above.

## Easy perturbed outcome

Not run — gated on easy original.

## Checker message

Not produced — no script executed.

## Generated script path

Not produced — the runner aborts before any LLM call.

## Was output valid Python?

Not applicable — no LLM call.

## Was an output file produced?

Not applicable — no LLM call.

## Schema status

Not applicable — no LLM call.

## Numerical status

Not applicable — no LLM call.

## Parameter sources

Identical to the deterministic-scaffold runs of this task (the
extracted-parameter layer is generator-independent):

```
seed:            fallback_default
node_counts:     prompt
epsilons:        fallback_default
evaluation_size: prompt
domain:          prompt
output_schema:   prompt
```

## Fallback defaults used

`seed`, `epsilons` — same state as the
`scientific_driver_v1` baseline. No regression.

## Overfit signals

The script that *would* have been emitted was not emitted; no overfit
signals exist for this run. The deterministic scaffold's signals are
unchanged. The fake-provider smoke runs from the previous milestone
remain reproducible and still pass — they confirm the runner archive
pipeline, the `script_metadata.json` shape (including the
`llm_diagnostics` block), the new `llm_prompt_packet.txt`, and the
`llm_raw_response.txt` work end-to-end.

## Validation

- `ruff check .` — clean.
- `pytest -m "not integration"` — **1257 passed, 4 deselected**
  (up from 1245; +12 new in `tests/test_check_llm_provider.py`).
- New tests cover: unknown provider, missing SDK, missing API key,
  client constructor failure, the "no model call without
  --test_generation" invariant, the `test_generation` ok and
  prose-rejection branches, every fake provider, both CLI exit codes,
  and the `sys.modules['anthropic'] = None` import guard.

## Files added this milestone

Main repo:

- `pyproject.toml` — added `[project.optional-dependencies.llm]`
  with `anthropic>=0.40.0`.
- `docs/llm_scientific_driver.md` — setup steps, example command,
  outcome table, safety notes.
- `scripts/check_llm_provider.py` — read-only readiness check.
- `tests/test_check_llm_provider.py` — 12 tests.

Experiment repo:

- `diagnostics/llm_scientific_driver_v1_anthropic_smoke_summary.md`
  (this file).
- `results/llm_scientific_driver_v1_easy_anthropic_real.json` —
  the captured `LLMProviderUnavailable` classification.

No `.env` change, no API key, no model call. The committed result
file is the JSON output of the runner's clean classification, not the
model's response.

## Recommended next step

The user (or whoever has the API key) should:

1. Export the key locally:
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   ```
   *Do not commit it. Do not put it in a committed `.env` file.*
2. Confirm provider readiness with the included check:
   ```bash
   python scripts/check_llm_provider.py --provider anthropic
   ```
3. Rerun the easy original LLM smoke:
   ```bash
   QDRANT_COLLECTION=code_chunks_kernelpack_ram \
   QDRANT_ENABLE_SPARSE_VECTORS=true \
   python scripts/evaluate_external_interpolation.py \
     evals/external_interpolation_tasks.json \
     --task external-easy-scalar-c4-matern \
     --generator llm_scientific_driver_v1 \
     --llm_provider anthropic \
     --repo_path /Users/whitney/src/kernelpack-python-ram \
     --generated_dir /Users/whitney/src/code-rag-experiments/generated/llm_scientific_driver_v1_easy_anthropic_real \
     --output /Users/whitney/src/code-rag-experiments/results/llm_scientific_driver_v1_easy_anthropic_real.json
   ```
4. Classify the result against the table in
   `docs/llm_scientific_driver.md`. If `CheckerPass`, run the
   perturbed easy task next. If `NumericalMismatch`, inspect the
   model's seed/epsilon choice in the archived `ragcode.py` and
   consider whether to backfill `expected_parameters` into the
   manifest (the source-aware overfit detector already accepts
   manifest-supplied values).
