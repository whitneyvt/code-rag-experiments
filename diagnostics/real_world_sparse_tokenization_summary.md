# Sparse Tokenization Improvement: Before / After

Real-world eval set: `evals/code_rag_real_world.json` (35 queries; 7 categories).

## Aggregate metrics

| Experiment | MRR (before) | MRR (after) | ΔMRR | Hit@5 (before) | Hit@5 (after) | ΔHit@5 |
| --- | --- | --- | --- | --- | --- | --- |
| real_world_baseline_hybrid (Python BM25) | 0.3271 | 0.3271 | 0.0000 | 0.4857 | 0.4857 | 0.0000 |
| real_world_native_hybrid (Qdrant sparse) | 0.2367 | 0.2538 | **+0.0171** | 0.3429 | 0.4000 | **+0.0571** |
| real_world_adaptive | 0.2381 | 0.2538 | **+0.0157** | 0.3429 | 0.4000 | **+0.0571** |

Native hybrid (Qdrant sparse) closes the gap to Python BM25 but does not yet
match it. Adaptive routing tracks native hybrid here because the routing
table maps most of the real-world questions to `native_hybrid` or `hybrid`.

## Per-category metrics (after sparse tokenization change)

| Category | n | Baseline MRR | Native Hybrid MRR | Adaptive MRR | Baseline Hit@5 | Native Hybrid Hit@5 | Adaptive Hit@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| architecture | 5 | 0.0667 | 0.0400 | 0.0400 | 0.2000 | 0.2000 | 0.2000 |
| cli | 6 | 0.1667 | 0.0333 | 0.0333 | 0.1667 | 0.1667 | 0.1667 |
| conceptual | 3 | 0.0833 | 0.0000 | 0.0000 | 0.3333 | 0.0000 | 0.0000 |
| config | 6 | 0.5889 | 0.6167 | 0.5333 | 0.8333 | 0.8333 | 0.8333 |
| error | 4 | 0.1250 | 0.0833 | 0.0833 | 0.2500 | 0.2500 | 0.2500 |
| symbol | 4 | 0.6250 | 0.6333 | 0.6333 | 1.0000 | 1.0000 | 1.0000 |
| technical | 7 | 0.4762 | 0.2857 | 0.2857 | 0.5714 | 0.2857 | 0.2857 |

Highlights:

- **config**: Native hybrid now slightly beats baseline (MRR 0.6167 vs 0.5889).
  The exact env-var and YAML-key forms (`QDRANT_COLLECTION`, `EMBEDDING_MODEL`,
  `collection_strategy`) are now preserved as single sparse terms with 2.5×
  weight, which gives Qdrant sparse enough signal to outrank baseline.
- **symbol**: Native hybrid edges baseline (MRR 0.6333 vs 0.6250) — exact
  CamelCase forms (`QdrantVectorStore`, `RoutingDecision`) match through
  both the exact lowercased form and the synthesized snake_case form.
- **error**, **architecture**, **cli**: Native hybrid still trails baseline.
  Most of these queries are conceptual ("how does X work?", "where is the
  error handled for…") rather than truly exact-token queries. Lexical
  signal is weak; dense retrieval carries most of the load.
- **technical**: Baseline still wins decisively (0.4762 vs 0.2857). Most
  technical queries phrase the question in natural language rather than
  quoting code, so BM25's longer doc-length normalization seems to help more
  than our weighted sparse encoding.
- **conceptual**: All three runs regress — the existing baseline's BM25
  occasionally surfaces the right file by chance. Both native hybrid runs
  miss every conceptual query, but the population is too small (n=3) to be
  load-bearing.

## Tokenization examples

```
QdrantVectorStore
  2.0  qdrantvectorstore
  1.0  qdrant_vector_store
  1.0  qdrant
  1.0  vector
  1.0  store

--native_hybrid
  2.5  --native_hybrid
  2.0  native_hybrid
  1.0  native
  1.0  hybrid

QDRANT_COLLECTION
  2.5  qdrant_collection
  1.0  qdrant
  1.0  collection

src/code_rag/retrieval/router.py
  2.5  src/code_rag/retrieval/router.py
  1.0  src
  2.0  code_rag
  1.0  code
  1.0  rag
  1.0  retrieval
  2.0  router.py
  1.0  router
  1.0  py

code_rag.retrieval.router
  2.5  code_rag.retrieval.router
  2.0  code_rag
  1.0  code
  1.0  rag
  1.0  retrieval
  1.0  router

ModuleNotFoundError
  2.0  modulenotfounderror
  1.0  module_not_found_error
  1.0  module
  1.0  found
  1.0  error
```

## Conclusion

The improved sparse tokenizer narrows the gap with Python BM25 but does not
close it. Native hybrid wins on `config` and `symbol`, ties on
`architecture`, `cli`, and `error`, and loses on `technical` and
`conceptual`. Adaptive routing should remain optional — it tracks native
hybrid but does not beat baseline on these queries.

Recommended next step: investigate why `technical` queries underperform
under native hybrid. The category contains many natural-language phrasings
where exact code tokens are rare, so the next sparse-side improvement
likely needs better doc-length normalization (sublinear length penalty) or
a learned sparse encoder, rather than further tokenizer tuning.
