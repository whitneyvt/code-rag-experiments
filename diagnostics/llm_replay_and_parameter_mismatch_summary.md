# Replay LLM Provider + Parameter Value Mismatch — Summary

Date: 2026-06-17

## Why this milestone

The Anthropic-API path is blocked on credentials, but the rest of the
LLM harness — the prompt packet, the code extractor, the archive
layout, the overfit detector, the parameter extractor — can be
exercised and sharpened end-to-end without ever calling a model.
This milestone adds two model-independent improvements:

1. A new `replay` LLM provider that reads a saved response file
   instead of calling an API. This lets a human paste a real
   model response into a text file, run the eval against it, and
   compare like-for-like with the deterministic scaffold and the
   fake providers.
2. A `parameter_value_mismatch` signal in the overfit detector
   that compares each extracted (`prompt` / `retrieval` /
   `manifest` / `fallback_default`) parameter value to the value
   actually present in the generated script. The previous detector
   only flagged source labels; this one also catches the case
   where retrieval or the prompt suggested one value and the
   script used a different one.

Neither change touches the default `--generator deterministic_easy`,
the deterministic `scientific_driver_v1` scaffold, the fake
providers, or any MCP tool.

## Part 1 — Replay LLM provider

### What changed

`src/code_rag/codegen/llm_standalone_driver_proposer.py`:

- New `ReplayLLMClient(response_file)`: reads the file eagerly,
  fails fast with `LLMReplayFileMissing` (a subclass of
  `LLMProviderUnavailable`) if the path does not exist.
- `build_llm_client(provider, *, model=None, replay_response_file=None)`
  now recognises `provider="replay"` and threads the response-file
  path through. Asking for `replay` without a file path raises
  `LLMProviderUnavailable` with a clear note.

`src/code_rag/codegen/external_eval.py`:

- New outcome constant `OUTCOME_LLM_REPLAY_FILE_MISSING`
  (`"LLMReplayFileMissing"`) and corresponding entry in
  `VALID_EXTERNAL_OUTCOMES`.

`scripts/evaluate_external_interpolation.py`:

- New CLI flag `--llm_response_file <path>`.
- `replay` added to `LLM_PROVIDER_CHOICES`.
- The runner emits `LLMReplayFileMissing` when the response file
  is absent and `LLMProviderUnavailable` (with a clearer note) when
  the file path is omitted entirely. Both cases stay non-crashing.

### Replay smoke runs

For the smoke runs we manually saved an LLM-shaped response (the
easy ground-truth driver wrapped in a fenced Python block) to
`code-rag-experiments/manual_llm_responses/easy_response.txt`
(163 lines). Then:

```bash
QDRANT_COLLECTION=code_chunks_kernelpack_ram \
QDRANT_ENABLE_SPARSE_VECTORS=true \
python scripts/evaluate_external_interpolation.py \
  evals/external_interpolation_tasks.json \
  --task external-easy-scalar-c4-matern \
  --generator llm_scientific_driver_v1 \
  --llm_provider replay \
  --llm_response_file .../manual_llm_responses/easy_response.txt \
  --repo_path /Users/whitney/src/kernelpack-python-ram \
  --generated_dir .../generated/llm_scientific_driver_v1_easy_replay \
  --output       .../results/llm_scientific_driver_v1_easy_replay.json
```

- Outcome: **`CheckerPass`**, `MATCH=True`.
- Archive includes `ragcode.py`, `llm_prompt_packet.txt`,
  `llm_raw_response.txt`, `retrieval_digest.json`,
  `script_metadata.json`, plus `checker_stdout.txt` /
  `checker_stderr.txt`.
- The `llm_diagnostics` block reports `provider_name: "replay"`,
  `model: null`, and SHA-256 hashes of the packet and response.

Regression on the previously-working `fake_easy` provider also
passed:

| Task                                   | Provider     | Outcome     | Match |
| -------------------------------------- | ------------ | ----------- | ----- |
| external-easy-scalar-c4-matern         | fake_easy    | CheckerPass | True  |
| external-easy-scalar-c4-matern         | replay       | CheckerPass | True  |

Missing-file classification was confirmed by an additional run:

```bash
... --llm_provider replay --llm_response_file /tmp/does-not-exist.txt ...
```

- Outcome: **`LLMReplayFileMissing`**.
- Note: `LLM provider 'replay' replay file missing: replay
  response file not found: /tmp/does-not-exist.txt`.

## Part 2 — Parameter value mismatch diagnostics

### What changed

`src/code_rag/codegen/parameter_extraction.py`:

- New `extract_from_script(difficulty, generated_source) -> dict`.
  Tries script-side variable-assignment patterns first
  (`SEED=4`, `EPSILONS = [...]`, `NODE_COUNTS = [...]`,
  `EVAL_SIZE=500`, `ORDERS=[4, 6]`, ...) and falls back to the
  existing prompt-style finders against the script body (catching
  patterns like `np.random.default_rng(N)` and comment headers).
- `domain` and `output_schema` are intentionally excluded — they
  rarely have a sharp script representation.

`src/code_rag/codegen/overfit_diagnostics.py`:

- `OverfitDiagnostics` gains a `parameter_value_mismatches: list`
  field.
- `analyze_script` accepts a new `script_parameters: Optional[dict]`
  argument. When present, it compares each of `seed`, `epsilons`,
  `node_counts`, `poly_orders`, `evaluation_size` against the
  `ExtractedParameters` snapshot. A mismatch is recorded only when
  both sides have a concrete value and they differ.
- Each mismatch is also surfaced as a one-line entry in
  `overfit_signals` (`parameter_value_mismatch: <field>=<value>
  (source <source>) but generated script uses <other>`), so the
  existing `possible_overfit` boolean stays a single switch.

`scripts/evaluate_external_interpolation.py`:

- `_build_script_metadata` calls `extract_from_script` and passes
  the result into `analyze_script`.
- `script_metadata.json` gains `script_parameters` and
  `parameter_value_mismatches` keys.

### Concrete signal on the easy task

The `script_metadata.json` for the easy task (both `fake_easy` and
`replay` runs) now reads:

```json
"parameter_sources": {
  "seed": "retrieval",
  "node_counts": "prompt",
  "epsilons": "fallback_default",
  "evaluation_size": "prompt",
  "domain": "prompt",
  "output_schema": "prompt"
},
"script_parameters": {
  "seed": 4,
  "node_counts": [50, 100, 500, 1000, 2000],
  "epsilons": [0.75, 1.5, 3.0],
  "evaluation_size": 500
},
"parameter_value_mismatches": [
  {
    "field": "seed",
    "expected_or_extracted": 17,
    "script_value": 4,
    "source": "retrieval"
  }
],
"overfit_signals": [
  "EPSILONS=[0.75, 1.5, 3.0] sourced from 'fallback_default' (no prompt/retrieval/manifest evidence) but appears verbatim in the generated script",
  "parameter_value_mismatch: seed=17 (source 'retrieval') but generated script uses 4"
]
```

The new signal correctly catches the case described as a "known
limitation" in the previous milestone summary: retrieval surfaced a
stray `np.random.default_rng(17)` from some indexed code, the
extractor labelled `seed` as `retrieval`, but the actual script
uses `seed=4`. The detector now flags this as a
`parameter_value_mismatch` instead of silently reporting the seed
as "retrieval-explained".

## Diagnostics table

| Field            | Source label (extracted) | Extracted value         | Script value            | Mismatch? |
| ---------------- | ------------------------ | ----------------------- | ----------------------- | --------- |
| seed             | retrieval                | 17                      | 4                       | **yes**   |
| node_counts      | prompt                   | [50, 100, 500, 1000, 2000] | [50, 100, 500, 1000, 2000] | no        |
| epsilons         | fallback_default         | [0.75, 1.5, 3.0]        | [0.75, 1.5, 3.0]        | no        |
| evaluation_size  | prompt                   | 500                     | 500                     | no        |
| domain           | prompt                   | (-1.0, 1.0)             | (not extracted from script) | n/a       |
| output_schema    | prompt                   | "easy"                  | (not extracted from script) | n/a       |

## Validation

- `ruff check .` — clean.
- `pytest -m "not integration"` — **1276 passed, 4 deselected**
  (up from 1257; +19 new across 3 test files).
- New tests:
  - `tests/test_parameter_extraction.py`: 6 tests covering
    `extract_from_script` for easy/hard variable assignments, the
    `default_rng` seed fallback, the empty case, unknown
    difficulty, and the deliberate skip of `domain` /
    `output_schema`.
  - `tests/test_overfit_diagnostics.py`: 5 tests covering seed
    mismatch, epsilon-list mismatch, no-mismatch when values
    agree, the backward-compat fallback-default signal, and the
    "no false mismatch when the script extractor finds nothing"
    case.
  - `tests/test_llm_standalone_driver_proposer.py`: 8 tests
    covering `build_llm_client("replay", ...)` happy path, missing
    file, missing-file-path argument, Python-fence round-trip,
    invalid response, no-network invariant, runner-level
    `LLMReplayFileMissing` classification, and runner-level replay
    smoke.

## Safety

- No `apply_code_change` MCP tool added.
- No API key required by any code path in this milestone.
  `replay` is pure file I/O; `fake_*` providers are pure
  in-process; the `anthropic` provider remains opt-in and
  classifies cleanly when unavailable.
- All archived generated scripts and the new
  `llm_raw_response.txt` / `script_metadata.json` files continue to
  live outside the live repo. Unit tests cover the
  outside-live-repo invariant.
- `evals/external_interpolation/` fixtures unchanged.
- Default `search_codebase` and MCP tools unchanged. Scientific
  retrieval remains opt-in for the external eval runner.
- `--generator deterministic_easy` (default) and
  `scientific_driver_v1` are both preserved unchanged.

## Recommended next step

Two parallel moves:

1. **Tune the prompt packet to spell out the canonical seed.** The
   `parameter_value_mismatch` signal makes the failure mode
   visible; the next move is to make the packet say "if no seed
   is specified, use the extracted-parameters value verbatim". The
   provenance fields are already in the packet, so the change is
   small.
2. **When a real LLM call is feasible**, capture the response into
   `code-rag-experiments/manual_llm_responses/<task>.txt` and
   replay it. The replay provider is now the canonical offline
   path for sharing LLM outputs across machines without needing
   the same API key everywhere.
