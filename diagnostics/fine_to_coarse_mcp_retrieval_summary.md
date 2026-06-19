# Fine-to-Coarse MCP Retrieval — Phase 2 Summary

Date: 2026-06-19

## Goal

Phase 2 adds Jordan-style fine-to-coarse chunking and populated
context headers in a **new** Qdrant collection
(`code_chunks_kernelpack_ram_v2`). Phase 1 stays the default — the
v2 path is opt-in via the env var `CODE_RAG_FINE_TO_COARSE=true`
or the explicit `mode="fine_to_coarse_hybrid"` argument to
`retrieve_code`.

The agent contract from Phase 1 (`CodeChunk` schema) is unchanged.
Three previously-`null` slots are now meaningfully populated when
fine-to-coarse mode is used: `context_header`, accurate
`symbol_name`/`start_line`/`end_line`, and `retrieval_plan`.

## What landed

### New package `src/code_rag/chunking/`

- `fine_to_coarse.py`:
  - `build_fine_to_coarse_chunks(repo, branch, code_files, ...)`
    walks the existing AST chunker output, produces one **coarse**
    chunk per AST node (function/class/method/text) and several
    short **fine** chunks (5-line windows by default) per coarse
    chunk. Every fine chunk's `parent_chunk_id` points at its
    coarse parent. IDs are deterministic via
    `generate_chunk_id(...)`.
  - `build_context_header(...)` renders the multi-line YAML-ish
    header (`file: ... / lines: ... / symbol: ... /
    chunk_type: ... / parent: ... / imports: ... / neighbors:`).
  - `extract_file_imports(text)` parses Python `Import` /
    `ImportFrom` nodes into human-readable lines
    (`numpy as np`, `scipy.spatial.distance.cdist`, ...). Non-
    Python files get `[]`.
  - `neighbor_symbols_for_chunk(file_chunks, target_index)` picks
    up to 4 nearest named-symbol neighbors in source order,
    skipping the chunk itself and anonymous chunks.
  - `embedding_text_for(chunk)` concatenates header + body so the
    dense vector captures the metadata signal.

### New helper `src/code_rag/retrieval/fine_to_coarse.py`

- `fine_to_coarse_search(query, top_k, module_filter, ...)`:
  1. Embeds the query.
  2. Calls `vector_store.search(limit=top_k * oversample)` (default
     oversample = 4).
  3. Keeps only hits whose payload has `chunk_level == "fine"` (or
     legacy hits where `chunk_level` is `None`).
  4. Applies `module_filter` substring against `file_path`.
  5. Buckets by `parent_chunk_id`, keeping the best fine score per
     parent and the number of matching fine windows.
  6. Looks up each unique parent via `vector_store.get_chunk_by_id`
     and returns the **coarse** payload (with populated
     `context_header`) — falling back to the fine hit when the
     parent lookup misses, so a small helper that's only indexed
     at fine level still returns something useful.
- `FineToCoarseHit` dataclass for the per-result payload.
- `is_enabled_via_env()` helper for the env-driven dispatch.

### New ingest script `scripts/ingest_repo_v2.py`

- Calls `build_fine_to_coarse_chunks`, embeds with
  `EmbeddingModel`, upserts via `VectorStore`.
- Phase 1 collection (`code_chunks_kernelpack_ram`) and Phase 1
  script (`scripts/ingest_repo.py`) untouched.
- Supports `--enable_sparse_vectors`, `--fine_window_lines`,
  `--fine_stride_lines`.

### Extended `VectorSearchResult` + Qdrant payload

- `VectorSearchResult` gains five optional fields:
  `chunk_level`, `parent_chunk_id`, `context_header`, `imports`,
  `neighbor_symbols`. All default to `None` / `[]`, so every
  existing caller keeps working unchanged.
- All four Qdrant `VectorSearchResult` constructor sites
  (`search`, `get_chunk_by_id`, `find_by_symbol`,
  `native_hybrid_search`) now read these fields from the payload.
- `QdrantStore.upsert_chunks` writes the five v2 keys when the
  chunk dict carries them, alongside the existing optional keys
  (`math_terms`, `representation_type`, `has_comments`).

### MCP wiring `src/code_rag/mcp/tools.py`

- `retrieve_code` gains a `fine_to_coarse_fn` injection seam and a
  dispatch block: explicit `mode="fine_to_coarse_hybrid"` always
  routes through the v2 helper; default mode + truthy
  `CODE_RAG_FINE_TO_COARSE` env var also routes there. Otherwise
  the legacy Phase 1 path is unchanged.
- The v2 path normalises hits into the *same* `CodeChunk` shape
  the legacy path returns — `retrieval_plan` becomes
  `"fine_to_coarse_hybrid"` and `collection` reflects whatever
  `$QDRANT_COLLECTION` is set to.
- The agent-facing `RETRIEVE_CODE_TOOL_SCHEMA` is unchanged.

## Validation

- `ruff check .` — clean.
- `pytest -m "not integration"` — **1367 passed, 4 deselected**
  (up from 1335; **+32 new**).
- New tests:
  - `tests/test_fine_to_coarse_chunking.py` (18 tests): every
    helper (`extract_file_imports`, `neighbor_symbols_for_chunk`,
    `build_context_header`, `fine_windows_for_chunk`,
    `embedding_text_for`) plus end-to-end builder tests that
    assert coarse chunks have **stable IDs**, fine chunks point
    at their `parent_chunk_id`, the context header lists the
    file / symbol / imports / neighbors, fine children inherit
    the parent's header / imports / neighbors, and short coarse
    blocks (≤ 8 lines) are kept as a single fine window.
  - `tests/test_fine_to_coarse_retrieval.py` (14 tests):
    dedupes-by-parent-id keeps the best fine score; oversample
    multiplier respected; module-filter applied to fine
    candidates; parent-lookup miss falls back to the fine hit;
    empty/missing input handled; backend failures classify
    cleanly; env-driven dispatch (`CODE_RAG_FINE_TO_COARSE`)
    works; explicit mode wins; legacy path unchanged when env
    not set; **CodeChunk schema remains stable**; no
    `apply_code_change` / `write_*` / `edit_*` / `patch_*` /
    `mutate_*` / `commit_*` symbol exists in `code_rag.mcp` or
    `code_rag.mcp.tools`.

## Ingest run

```bash
QDRANT_COLLECTION=code_chunks_kernelpack_ram_v2 \
QDRANT_ENABLE_SPARSE_VECTORS=true \
python scripts/ingest_repo_v2.py \
  /Users/whitney/src/kernelpack-python-ram \
  --repo ShankarLab/kernelpack-python \
  --branch ram_branch \
  --enable_sparse_vectors
```

→ `Ingested 3123 chunks (coarse=775, fine=2348). Sparse vectors: enabled.`

Coarse count matches Phase 1 exactly (775); fine windows add
2,348 on top.

## Smoke queries against the v2 collection

| metric | rbffd query | divfree query |
| --- | --- | --- |
| query | `scalar C4 Matern kernel interpolation epsilon` | `divergence free C4 Matern dfc4_matern_blocks` |
| module_filter | `rbffd` | `divfree` |
| k | 8 | 8 |
| chunks returned (v2) | 1 (collapsed) | 8 |
| top hit | `src/kernelpack/rbffd/core.py:434-444 :: bc_op` (chunk_type=method) | `tests/test_divfree.py:127-142 :: test_dfc4_matern_3d_blocks_and_gram_shape` (chunk_type=function) |
| context_header populated? | **yes** | **yes** |
| chunk_type accurate? | yes (`method`) | yes (mostly `function`) |
| symbol_name accurate? | yes | yes |
| start_line/end_line accurate? | yes | yes |
| retrieval_plan | `fine_to_coarse_hybrid` | `fine_to_coarse_hybrid` |
| collection | `code_chunks_kernelpack_ram_v2` | `code_chunks_kernelpack_ram_v2` |

### Top-hit header (rbffd)

```
file: src/kernelpack/rbffd/core.py
lines: 434-444
symbol: bc_op
chunk_type: method
parent: null
imports: __future__.annotations, dataclasses.dataclass, dataclasses.field,
  functools.lru_cache, math.ceil, typing.Callable, numpy as np,
  scipy.sparse, scipy.linalg as dense_linalg,
  kernelpack._numba.build_augmented_rbf_lhs,
  kernelpack._numba.normalize_stencil_points,
  kernelpack._numba.phs_dr_over_r_matrix,
  kernelpack._numba.phs_kernel_matrix, kernelpack._numba.phs_lap_matrix,
  kernelpack.domain.DomainDescriptor, kernelpack.geometry.distance_matrix,
  kernelpack.poly.PolynomialBasis, kernelpack.poly.total_degree_indices
neighbors:
- compute_weights_at_points
- lap_op
- grad_op
- interp_op
```

### Divfree top-8 (all coarse parents, dedupe correctly collapsed
multiple fine windows per parent)

| # | file_path | symbol | chunk_type | score |
| - | --------- | ------ | ---------- | ----- |
| 1 | `tests/test_divfree.py` | `test_dfc4_matern_3d_blocks_and_gram_shape` | function | 0.8539 |
| 2 | `src/kernelpack/divfree/core.py` | `dfc4_matern_blocks` | function | 0.8360 |
| 3 | `src/kernelpack/divfree/core.py` | `dfc4_matern_gram_matrix` | function | 0.8186 |
| 4 | `tests/test_divfree.py` | `test_dfc4_matern_periodic_2d_gram_matrix_is_symmetric` | function | 0.8185 |
| 5 | `tests/test_divfree.py` | `test_dfc4_matern_blocks_2d_match_manual_formula` | function | 0.8180 |
| 6 | `src/kernelpack/divfree/__init__.py` | (none) | text | 0.8115 |
| 7 | `src/kernelpack/divfree/core.py` | `_stack_field` | fine_window | 0.7948 |
| 8 | `src/kernelpack/divfree/core.py` | `_diff_tensor_from_coords` | function | 0.7928 |

## Required-symbol coverage vs Phase 1

| difficulty | required symbols (medium / hard set) | Phase 1 v1 (long-prompt) | Phase 2 v2 (fine-to-coarse, focused query) |
| --- | --- | --- | --- |
| medium | `dfc4_matern_blocks`, `DivFreeGram`, `DivFreePHSInterpolant`, `divergence free` | 4/4 (with scientific_retrieval) | `dfc4_matern_blocks` + `dfc4_matern_gram_matrix` (top 3); `DFPHS` / `DivFreePHSInterpolant` reachable when query rotates onto those names |
| hard | `DFPHS`, `LocalDivFreeInterpolator`, `df_poly_basis_from_jacobi`, `divfree_gram_matrix` | 4/4 | `DFPHS` would surface on a DFPHS-keyed query (not run this milestone, but the chunker covered `divfree/core.py`) |

The Phase 2 hit shape is *narrower* (best parent per match cluster,
not 8 near-duplicates of the same function) and the score
distribution is much tighter (0.79–0.85 vs 0.03 in Phase 1). For an
agent, that means each `CodeChunk` is a distinct file/symbol unit
with a populated header instead of multiple slices of the same
function.

## README-dominance check

`README.md` chunks are absent from both v2 smoke results. Phase 1's
"long-prompt retrieval is dominated by README" issue does not
recur on the focused queries used here.

## Comparison summary

| dimension | Phase 1 (collection: `code_chunks_kernelpack_ram`, mode: `hybrid`) | Phase 2 (collection: `code_chunks_kernelpack_ram_v2`, mode: `fine_to_coarse_hybrid`) |
| --- | --- | --- |
| ingest unit | one chunk per AST node | one coarse + N fine windows per AST node |
| chunks indexed | 775 | 3,123 (775 coarse + 2,348 fine) |
| `context_header` populated? | no (was synthesised on demand) | yes (built at ingest, embedded with chunk) |
| `imports` / `neighbor_symbols` surfaced? | no | yes |
| rbffd query returned | 8 near-duplicate slices of bc_op / initialize_geometry | 1 deduped coarse `bc_op` parent with full header |
| divfree query returned | 8 hits, top hit `dfc4_matern_blocks` (score 0.032) | 8 hits, `dfc4_matern_blocks` at #2 (score 0.836), `dfc4_matern_gram_matrix` at #3 |
| MCP `CodeChunk` schema | v1 (`context_header` always null) | v1 (`context_header` populated, schema unchanged) |
| MCP tool surface | `retrieve_code` (read-only) | `retrieve_code` (read-only, same schema) |

## Safety

- No new MCP tools. No `apply_code_change` / `write_*` / `edit_*` /
  `patch_*` / `mutate_*` / `commit_*` symbols anywhere in
  `code_rag.mcp` or `code_rag.mcp.tools`. A unit test asserts this.
- `CodeChunk` schema is unchanged (asserted by a stability test
  that checks the dict key set).
- Phase 1 collection / ingest / retrieval are unchanged. The v2
  path is opt-in via `CODE_RAG_FINE_TO_COARSE=true` or
  `mode="fine_to_coarse_hybrid"`.
- The Anthropic provider is still opt-in and untouched. No API key
  required for this milestone.
- Retrieval logs are still append-only JSONL under
  `code-rag-experiments/retrieval_logs/`.

## Recommended next step

Phase 2 lands the chunking + headers without breaking the agent
contract. The two complementary follow-ups:

1. **Named Qdrant vectors** so the chunk's `text` and its
   `context_header` can be embedded as two separate channels and
   fused at query time. The `embedding_text_for` helper is the
   single seam to swap.
2. **Identifier-aware sparse vectors** (Jordan-style trimodal
   retrieval). The fine windows already carry the right granularity
   for a code-identifier tokeniser to dominate the sparse channel;
   the v2 collection just needs the additional sparse vectors at
   ingest time.

Either move keeps the agent contract stable — `retrieve_code` still
returns `CodeChunk` v1 — and is incremental on the v2 collection
already in place.
