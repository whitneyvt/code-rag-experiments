# MCP `retrieve_code` Server — Phase 1 Summary

Date: 2026-06-19

## Why this milestone

This is the first step of the refocus on *"a RAG layer for AI coding
agents working with scientific codebases, exposed via an MCP
server."* The existing eval / checker / overfit / parameter
diagnostics work is preserved unchanged; this milestone adds the
agent-facing surface that lets a coding agent (Jordan-style) call
into our retrieval stack directly.

Phase 1 is intentionally narrow: **one read-only tool**
(`retrieve_code`), a stable JSON return shape, an append-only call
log, and a Markdown report helper. The Jordan-style fine-to-coarse
chunking, named Qdrant vectors, identifier-aware sparse vectors,
and the paper bridge are scheduled for later milestones.

## What landed

### New package `src/code_rag/mcp/`

* `schemas.py` — `CodeChunk` dataclass plus
  `RETRIEVE_CODE_TOOL_SCHEMA` (the JSON schema the MCP server
  registers) and `build_context_header()`.
* `tools.py` — `retrieve_code(...)` adapter and a
  `RetrievalUnavailable` exception. The adapter is a thin
  wrapper over `code_rag.retrieval.search_service.search_codebase`:
  no ranking, no scoring, no re-fetching — it only normalises the
  payload and append-logs the call. Stubs for future tools
  (`explain_api`, `suggest_workflow`, `run_example`,
  `retrieve_paper_context`) intentionally raise
  `NotImplementedError` so the contract is documented but not
  exposed.
* `server.py` — stdio MCP server. The `mcp` Python package is
  imported lazily inside `serve_stdio()` so unit tests can
  exercise the adapter without the protocol library installed.
  Registers exactly one tool today (`retrieve_code`); future
  read-only tools land in the same `list_tools` callback.
* `__init__.py` — re-exports the public API
  (`retrieve_code`, `CodeChunk`, `RetrievalUnavailable`,
  `RETRIEVE_CODE_TOOL_SCHEMA`).

### New module `src/code_rag/retrieval/qlog.py`

Append-only JSONL logger for MCP retrieval calls:

* `RetrievalLogger.log_query(...)` writes a single record per
  call to a daily file `mcp_retrieve_code_YYYY-MM-DD.jsonl`.
  Records are never edited in place.
* `default_log_dir()` resolves in this order:
  `$CODE_RAG_RETRIEVAL_LOG_DIR` → experiment-repo
  `retrieval_logs/` if available → `${cwd}/.code_rag/retrieval_logs/`.
* `render_markdown_report(record)` / `render_query_report(query_id)`
  produce a readable Markdown report from any logged query.

### New launcher `scripts/run_mcp_server.py`

* Reads `.env` via `python-dotenv` so the operator can stash
  `QDRANT_*` once and forget it.
* `--list-tools` prints the registered tool schemas as JSON.
* `--check-config` prints the resolved config (server name,
  collection, sparse-vectors flag, embedding model, log
  directory) without contacting Qdrant.
* No flag, no mutation, no model call: defaults to running the
  stdio server.

### Tool contract

```json
{
  "name": "retrieve_code",
  "inputSchema": {
    "properties": {
      "query":         {"type": "string"},
      "module_filter": {"type": ["string", "null"], "default": null},
      "k":             {"type": "integer", "minimum": 1, "maximum": 64, "default": 8}
    },
    "required": ["query"]
  }
}
```

Per-chunk return payload (stable across milestones; missing fields
are `null` rather than omitted):

```json
{
  "file_path":       "...",
  "symbol_name":     "...",
  "chunk_type":      "...",
  "start_line":      123,
  "end_line":        171,
  "score":           0.83,
  "text":            "...",
  "context_header":  "<file>:<lines> :: <symbol>",
  "llm_summary":     null,
  "retrieval_plan":  "hybrid",
  "collection":      "code_chunks_kernelpack_ram"
}
```

The server's call entry point returns
`{"status": "ok", "count": ..., "chunks": [...], "query": ...,
"module_filter": ..., "k": ...}` on success, or
`{"status": "error", "code": "...", "error": "..."}` on failure.
Failure codes: `invalid_argument`, `retrieval_unavailable`,
`unknown_tool`.

## Smoke runs against KernelPack `ram_branch`

Collection: `code_chunks_kernelpack_ram` (sparse vectors enabled).
Log path: `code-rag-experiments/retrieval_logs/mcp_retrieve_code_2026-06-19.jsonl`.

### Query 1 — rbffd

```
query         = "scalar C4 Matern kernel interpolation epsilon"
module_filter = "rbffd"
k             = 8
```

All 8 hits land in `src/kernelpack/rbffd/core.py`:

| # | symbol | lines | score |
| - | ------ | ----- | ----- |
| 1 | `default_diff_order` | 136-145 | 0.0328 |
| 2 | `_apply_operator` | 319-329 | 0.0308 |
| 3 | `initialize_geometry` | 384-407 | 0.0306 |
| 4 | `_apply_operator` | 478-488 | 0.0297 |
| 5 | `bc_op` | 254-272 | 0.0294 |
| 6 | `initialize_geometry` | 182-198 | 0.0293 |
| 7 | `_compute_weights_interior` | 449-464 | 0.0161 |
| 8 | `bc_op` | 434-444 | 0.0161 |

The `module_filter="rbffd"` successfully scoped retrieval to that
subpackage; every hit's file path contains `/rbffd/`.

### Query 2 — divfree

```
query         = "divergence free C4 Matern dfc4_matern_blocks"
module_filter = "divfree"
k             = 8
```

| # | file_path | symbol | lines | score |
| - | --------- | ------ | ----- | ----- |
| 1 | `src/kernelpack/divfree/core.py` | `dfc4_matern_blocks` | 124-155 | 0.0323 |
| 2 | `src/kernelpack/divfree/core.py` | `DFPHS` | 20-43 | 0.0306 |
| 3 | `src/kernelpack/divfree/core.py` | `dfc4_matern_gram_matrix` | 158-191 | 0.0296 |
| 4 | `src/kernelpack/divfree/__init__.py` | (text) | 1-19 | 0.0161 |
| 5 | `src/kernelpack/divfree/core.py` | `initialize` | 367-409 | 0.0156 |
| 6 | `tests/test_divfree.py` | `test_dfc4_matern_3d_blocks_and_gram_shape` | 127-142 | 0.0155 |
| 7 | `src/kernelpack/divfree/core.py` | `DivFreePHSInterpolant` | 341-420 | 0.0154 |
| 8 | `tests/test_divfree.py` | `test_dfc4_matern_blocks_2d_match_manual_formula` | 80-98 | 0.0147 |

`dfc4_matern_blocks` is the top hit; the divergence-free
interpolator class and gram-matrix helper land within the top 4.
Two relevant test functions also appear — useful surface for an
agent looking for usage examples.

Both queries logged to
`mcp_retrieve_code_2026-06-19.jsonl`. The report helper renders
the second query as the table above.

## Validation

- `ruff check .` — clean.
- `pytest -m "not integration"` — **1335 passed, 4 deselected**
  (up from 1303 last milestone; +32 new tests).
- New tests:
  - `tests/test_qlog.py` (11 tests) — append-only JSONL writes,
    in-place no-edit invariant, per-day file naming,
    `find` / `iter_records` / `render_markdown_report` /
    `render_query_report`, default-log-dir env override and
    fallback, ISO-UTC timestamp.
  - `tests/test_mcp_retrieve_code.py` (21 tests) — tool-schema
    stability, `CodeChunk` field set,
    `build_context_header`, `list_registered_tools`,
    `SERVER_NAME` invariant, happy path with a fake backend,
    `module_filter` is forwarded as `SearchFilters(path_include=[...])`,
    no-filter path passes `filters=None`, every call is logged,
    empty-query and out-of-range-k raise `ValueError`,
    backend failure raises `RetrievalUnavailable`, the MCP
    server's `call_retrieve_code` returns the documented `ok`
    payload, invalid arguments return the `invalid_argument`
    error payload, retrieval outages return the
    `retrieval_unavailable` error payload, the live repo's
    `src/code_rag/mcp/` and `evals/external_interpolation/`
    files are byte-identical before and after a retrieve call,
    and the `mcp` namespace + `tools` namespace export no
    `apply_code_change`.

## Safety

- **Read-only.** No tool writes to the repo. No
  `apply_code_change`. The launcher cannot mutate files; the
  server stdio loop only ever returns JSON via `TextContent`.
- **No API key required.** The MCP server does not call any
  external model. The Anthropic provider added in earlier
  milestones is still opt-in and unrelated.
- **Logs append-only.** The unit test
  `test_logger_never_edits_in_place` asserts byte-for-byte that
  the existing log prefix is preserved when a new row is
  written.
- **Repo invariants.** A unit test snapshots every file under
  `src/code_rag/mcp/` and `evals/external_interpolation/`
  before and after a `retrieve_code` call and asserts the set
  is unchanged.
- **Existing diagnostics preserved.** The codegen / overfit /
  parameter-extraction / kernel-diagnostics modules and tests
  are untouched.

## Phase 1 explicitly does *not* include

(Documented here so reviewers don't expect them yet.)

- Jordan-style fine-to-coarse chunking with rich
  `context_header` strings (the current header is just
  `<file>:<lines> :: <symbol>`).
- Per-chunk `llm_summary` (always `null` for now; the schema
  slot is reserved).
- Identifier-aware sparse vectors and trimodal retrieval — the
  Qdrant collection is the existing single-channel one.
- New tools beyond `retrieve_code`. `explain_api`,
  `suggest_workflow`, `run_example`,
  `retrieve_paper_context` are stubs in `tools.py` raising
  `NotImplementedError`.

## Recommended next step

The minimum useful follow-up for agent integration is the
fine-to-coarse chunking pass:

1. Add a chunk builder that emits both a fine-grained
   `function/method/class` chunk and a coarser
   `module/package` chunk per file, with each fine chunk
   carrying a populated `context_header` that includes the
   parent class / module signature.
2. Backfill `context_header` from that builder so the existing
   `CodeChunk.context_header` field becomes informative without
   any schema break.
3. Re-index `ram_branch` into a new collection
   (`code_chunks_kernelpack_ram_v2`) and gate the MCP server
   on `$QDRANT_COLLECTION` so both the old and new collections
   stay queryable side by side until we cut over.

That sequence keeps the agent contract stable while the chunking
quality improves underneath it, which matches the milestone's
explicit instruction: "Important: this milestone is only Phase 1.
Do not rebuild chunking yet."
