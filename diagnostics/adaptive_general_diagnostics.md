# Routing Diagnostics: evals/code_rag.json

- Baseline mode: `native_hybrid`
- Top K: 5
- Total queries: 25

## Summary

- **Adaptive wins**: 2
- **Baseline wins**: 1
- **Ties**: 15
- **Neither found**: 7

## Loss Reasons

- Wrong route: 0
- Expected missing from adaptive: 0
- Expected lower ranked: 1
- Same results: 15
- No expected match: 7

## Query Type Distribution

- cli: 1 (4.0%)
- conceptual: 1 (4.0%)
- config: 1 (4.0%)
- fallback: 3 (12.0%)
- symbol: 5 (20.0%)
- technical: 14 (56.0%)

## Selected Mode Distribution

- native_hybrid: 25 (100.0%)

## Query Type -> Mode Mapping

- cli -> native_hybrid: 1 (4.0%)
- conceptual -> native_hybrid: 1 (4.0%)
- config -> native_hybrid: 1 (4.0%)
- fallback -> native_hybrid: 3 (12.0%)
- symbol -> native_hybrid: 5 (20.0%)
- technical -> native_hybrid: 14 (56.0%)

## Per-Query Results

| query_id | query_type | selected_mode | baseline_rank | adaptive_rank | winner | reason |
| --- | --- | --- | --- | --- | --- | --- |
| Q1 | technical | native_hybrid | 1 | 1 | tie | same_results |
| Q2 | technical | native_hybrid | 1 | 1 | tie | same_rank_different_results |
| Q3 | technical | native_hybrid | 1 | 2 | baseline | expected_lower_ranked |
| Q4 | symbol | native_hybrid | 1 | 1 | tie | same_results |
| Q5 | symbol | native_hybrid | 1 | 1 | tie | same_results |
| Q6 | symbol | native_hybrid | 1 | 1 | tie | same_results |
| Q7 | symbol | native_hybrid | 1 | 1 | tie | same_rank_different_results |
| Q8 | config | native_hybrid | - | - | neither | no_expected_match |
| Q9 | conceptual | native_hybrid | 4 | 4 | tie | same_rank_different_results |
| Q10 | fallback | native_hybrid | - | - | neither | no_expected_match |
| Q11 | fallback | native_hybrid | 1 | 1 | tie | same_results |
| Q12 | technical | native_hybrid | - | - | neither | no_expected_match |
| Q13 | technical | native_hybrid | - | - | neither | no_expected_match |
| Q14 | technical | native_hybrid | 4 | 4 | tie | same_results |
| Q15 | technical | native_hybrid | 1 | 1 | tie | same_results |
| Q16 | technical | native_hybrid | - | - | neither | no_expected_match |
| Q17 | symbol | native_hybrid | 3 | 3 | tie | same_results |
| Q18 | cli | native_hybrid | - | - | neither | no_expected_match |
| Q19 | technical | native_hybrid | 1 | 1 | tie | same_results |
| Q20 | technical | native_hybrid | 5 | 4 | adaptive | adaptive_better |
| Q21 | technical | native_hybrid | 1 | 1 | tie | same_results |
| Q22 | technical | native_hybrid | 1 | 1 | tie | same_results |
| Q23 | technical | native_hybrid | 1 | 1 | tie | same_results |
| Q24 | fallback | native_hybrid | 2 | 1 | adaptive | adaptive_better |
| Q25 | technical | native_hybrid | - | - | neither | no_expected_match |

## Adaptive Losses (Baseline Won)

### How does Qdrant search for similar vectors?...

- Query type: technical
- Selected mode: native_hybrid
- Baseline mode: native_hybrid
- Baseline rank: 1
- Adaptive rank: 2
- Loss reason: expected_lower_ranked
- Expected files: ['src/code_rag/vector_stores/qdrant.py']
- Baseline top files: ['src/code_rag/vector_stores/qdrant.py', 'src/code_rag/retrieval/search_service.py', 'src/code_rag/config.py']
- Adaptive top files: ['src/code_rag/retrieval/search_service.py', 'src/code_rag/vector_stores/qdrant.py', 'src/code_rag/config.py']
