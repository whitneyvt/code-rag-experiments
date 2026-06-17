# LLM Scientific Driver v1 — External Interpolation Summary

Date: 2026-06-17

## Generator design

`scientific_driver_v1` (the deterministic per-difficulty scaffold) is
preserved unchanged. This milestone adds a parallel generator
`llm_scientific_driver_v1` backed by a real provider seam, behind the
same checker harness, the same scientific retrieval layer, and the
same parameter-extraction layer.

### Module layout

`src/code_rag/codegen/llm_standalone_driver_proposer.py` exports:

- `LLMClient` — structural `Protocol` with a single `generate(prompt, *, model)`.
- `FakeLLMClient(response=str)` — in-process test client that returns
  a canned response.
- `AnthropicLLMClient(model=None)` — lazy-import shim for the
  official `anthropic` SDK. Raises `LLMProviderUnavailable` when the
  SDK is not installed or `ANTHROPIC_API_KEY` is missing.
- `build_llm_client(provider, *, model=None)` — factory for the
  five provider names accepted by the runner.
- `build_prompt_packet(...)` — assembles the structured packet
  (TASK / DIFFICULTY / CHECKER CONTRACT / OUTPUT SCHEMA / EXTRACTED
  PARAMETERS / PARAMETER SOURCES / REQUIRED RETRIEVAL SYMBOLS /
  RETRIEVED KERNELPACK CONTEXT / OUTPUT instruction).
- `extract_python_code(response_text)` — strips optional ```python
  fences and validates the result via `ast.parse`. Raises
  `LLMResponseParseError` otherwise.
- `propose_llm_standalone_driver(...) -> (source_code, LLMProposerDiagnostics)`.

### Outcome additions

`src/code_rag/codegen/external_eval.py` gains two outcomes:

- `OUTCOME_LLM_PROVIDER_UNAVAILABLE` — surfaced when the runner
  cannot construct the requested provider (anthropic SDK missing,
  `ANTHROPIC_API_KEY` unset, unknown provider name).
- `OUTCOME_LLM_GENERATION_FAILURE` — surfaced when the LLM responded
  but `extract_python_code` rejected the response (prose-only,
  syntax error, empty).

### Runner wiring

`scripts/evaluate_external_interpolation.py` gains:

- `--generator llm_scientific_driver_v1`.
- `--llm_provider {anthropic, fake_easy, fake_medium, fake_hard, fake_invalid}`.
- `--llm_model <id>` (defaults to `claude-sonnet-4-6` for anthropic).
- `--llm_prompt_out <dir>`.
- `--llm_max_context_chunks <n>` (defaults to 8).

The archive directory for each LLM task now includes:

- `ragcode.py` — generated script.
- `llm_prompt_packet.txt` — exact prompt sent to the model.
- `llm_raw_response.txt` — raw response from the model.
- `retrieval_digest.json` — scientific retrieval state.
- `checker_stdout.txt` / `checker_stderr.txt`.
- `script_metadata.json` — extended with an `llm_diagnostics`
  block carrying `provider_name`, `model`, `chunks_included`,
  `extracted_python_length`, `prompt_length`, and SHA-256 hashes of
  the packet and raw response.

The runner default for `--generator` remains `deterministic_easy`.
`llm_scientific_driver_v1` is opt-in.

## Provider availability

- `anthropic` (real provider) — **Unavailable.** The `anthropic`
  package is not installed in the active venv and the
  `ANTHROPIC_API_KEY` env var is not set. The runner detects this at
  client-construction time and emits the `LLMProviderUnavailable`
  outcome without crashing.
- `fake_easy` / `fake_medium` / `fake_hard` — **Available.** These
  load the corresponding ground-truth driver from
  `evals/external_interpolation/` and wrap it in a ```python fence
  so `extract_python_code` accepts it.
- `fake_invalid` — **Available.** Returns prose that
  `extract_python_code` deliberately rejects, so the runner emits
  `LLMGenerationFailure`.

## Fake-client end-to-end runs

### Easy, original prompt

```bash
QDRANT_COLLECTION=code_chunks_kernelpack_ram \
QDRANT_ENABLE_SPARSE_VECTORS=true \
python scripts/evaluate_external_interpolation.py \
  evals/external_interpolation_tasks.json \
  --task external-easy-scalar-c4-matern \
  --generator llm_scientific_driver_v1 \
  --llm_provider fake_easy \
  --repo_path /Users/whitney/src/kernelpack-python-ram \
  --generated_dir .../generated/llm_scientific_driver_v1_easy_fake \
  --output       .../results/llm_scientific_driver_v1_easy_fake.json
```

- Outcome: **`CheckerPass`**, `MATCH=True`.
- LLM provider: `fake_easy`.
- Chunks included in packet: 8.
- Prompt packet: 12,444 chars (archived as
  `llm_prompt_packet.txt`).
- Raw response: ground-truth driver wrapped in a Python fence
  (archived as `llm_raw_response.txt`).
- Extracted Python: 5,707 chars; `ast.parse` clean.
- Parameter sources after extraction:
  `{seed: retrieval, node_counts: prompt, epsilons: fallback_default,
  evaluation_size: prompt, domain: prompt, output_schema: prompt}`.
- Overfit signal: `EPSILONS=[0.75, 1.5, 3.0]` flagged as
  `fallback_default` (same as the deterministic-scaffold run last
  milestone).

### Easy, perturbed prompt

```bash
... --task external-easy-perturbed-wording \
    --generator llm_scientific_driver_v1 --llm_provider fake_easy \
    --generated_dir .../generated/llm_scientific_driver_v1_easy_perturbed_fake \
    --output       .../results/llm_scientific_driver_v1_easy_perturbed_fake.json
```

- Outcome: **`CheckerPass`**, `MATCH=True`.

### LLM generation failure (`fake_invalid`)

```bash
... --task external-easy-scalar-c4-matern \
    --generator llm_scientific_driver_v1 --llm_provider fake_invalid \
    --output .../results/llm_scientific_driver_v1_easy_fake_invalid.json
```

- Outcome: **`LLMGenerationFailure`**. The runner reports the
  failure cleanly via the new exception path without crashing.

## Real LLM smoke

```bash
... --task external-easy-scalar-c4-matern \
    --generator llm_scientific_driver_v1 --llm_provider anthropic \
    --generated_dir .../generated/llm_scientific_driver_v1_easy_anthropic \
    --output       .../results/llm_scientific_driver_v1_easy_anthropic.json
```

- Outcome: **`LLMProviderUnavailable`**.
- `notes`: `LLM provider 'anthropic' unavailable: anthropic SDK is
  not installed; install it with 'pip install anthropic' to enable
  this provider`.
- This is the expected clean-classification path called out in the
  milestone decision criteria. No silent crash; no false
  `CheckerPass`.

## Checker outcomes table

| Run                                         | Provider        | Outcome                  | Match |
| ------------------------------------------- | --------------- | ------------------------ | ----- |
| easy original (llm)                         | fake_easy       | CheckerPass              | True  |
| easy perturbed (llm)                        | fake_easy       | CheckerPass              | True  |
| easy original (llm, invalid)                | fake_invalid    | LLMGenerationFailure     | n/a   |
| easy original (llm, anthropic)              | anthropic       | LLMProviderUnavailable   | n/a   |

## Generated script archive paths

- `/Users/whitney/src/code-rag-experiments/generated/llm_scientific_driver_v1_easy_fake/external-easy-scalar-c4-matern__llm_scientific_driver_v1/`
- `/Users/whitney/src/code-rag-experiments/generated/llm_scientific_driver_v1_easy_perturbed_fake/external-easy-perturbed-wording__llm_scientific_driver_v1/`
- `/Users/whitney/src/code-rag-experiments/generated/llm_scientific_driver_v1_easy_anthropic/external-easy-scalar-c4-matern__llm_scientific_driver_v1/`

Each holds `ragcode.py`, `llm_prompt_packet.txt`,
`llm_raw_response.txt`, `retrieval_digest.json`, `script_metadata.json`,
and (when the script ran) `checker_stdout.txt` /
`checker_stderr.txt`. The `LLMProviderUnavailable` run does not write
a generated script because the provider was rejected before any code
was emitted.

## Validation

- `ruff check .` — clean.
- `pytest -m "not integration"` — **1245 passed, 4 deselected**
  (up from 1218; 27 new in
  `tests/test_llm_standalone_driver_proposer.py`).
- New tests cover: every prompt-packet section, the
  fence/prose/empty branches of `extract_python_code`, the
  `FakeLLMClient` and `build_llm_client` factory, the
  `AnthropicLLMClient` "unavailable when SDK missing" / "unavailable
  without API key" paths (monkey-patched, no network), the
  runner's outcome classification for the LLM provider /
  generation paths, and the safety invariant that archived
  artefacts live outside the live repo.

## Safety

- No `apply_code_change` MCP tool.
- Generated scripts and the LLM packet / raw-response archives all
  live under `code-rag-experiments/generated/...` — outside both
  `code_rag` and `kernelpack-python-ram`. A unit test
  (`test_archive_writes_outside_live_repo`) asserts every archived
  path stays outside the live repo.
- `evals/external_interpolation/` fixtures unchanged.
- The deterministic `scientific_driver_v1` generator and the default
  `--generator deterministic_easy` are unchanged. The LLM path is
  opt-in.
- Default `search_codebase` and MCP tools unchanged. Scientific
  retrieval remains opt-in for the external eval runner only.
- Unit tests never require network or API access — the `fake_*`
  clients and monkey-patched SDK probes cover every branch.

## Recommended next step

Two paths, executable in parallel:

1. **Enable the real Anthropic provider.** Add `anthropic` to the
   dev/extras dependencies in `pyproject.toml` (or document the
   manual install), then run the easy task and inspect:
   - whether the model returns a single Python fence,
   - whether the extracted code passes `ast.parse`,
   - whether the checker passes / which outcome surfaces if it
     doesn't.
   When the LLM threads prompt-derived constants (seed, epsilons)
   into its emitted script, the `parameter_sources` will move from
   `fallback_default` to `prompt`, and the overfit signals for SEED
   and EPSILONS will go away without any change to the detector.
2. **Sharpen the overfit detector to compare values.** The current
   detector treats a parameter as explained as soon as *any* value
   for that field appears in retrieval (today retrieval surfaces a
   stray `np.random.default_rng(17)` and the SEED slot is therefore
   labelled `retrieval`). Comparing the *value* extracted to the
   *value* present in the script would catch the mismatch and flag
   it as `parameter_value_mismatch`, complementing the existing
   `fallback_default` signal.
