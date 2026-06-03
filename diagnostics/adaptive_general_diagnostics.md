# Routing Diagnostics: evals/code_rag.json

- Baseline mode: `hybrid`
- Top K: 5
- Total queries: 25

## Summary

- **Adaptive wins**: 0
- **Baseline wins**: 1
- **Ties**: 20
- **Neither found**: 4

## Loss Reasons

- Wrong route: 1
- Expected missing from adaptive: 0
- Expected lower ranked: 0
- Same results: 20
- No expected match: 4

## Query Type Distribution

- conceptual: 2 (8.0%)
- fallback: 3 (12.0%)
- symbol: 5 (20.0%)
- technical: 15 (60.0%)

## Selected Mode Distribution

- dense: 2 (8.0%)
- hybrid: 23 (92.0%)

## Query Type -> Mode Mapping

- conceptual -> dense: 2 (8.0%)
- fallback -> hybrid: 3 (12.0%)
- symbol -> hybrid: 5 (20.0%)
- technical -> hybrid: 15 (60.0%)

## Per-Query Results

| query_id | query_type | selected_mode | baseline_rank | adaptive_rank | winner | reason |
| --- | --- | --- | --- | --- | --- | --- |
| Q1 | technical | hybrid | 1 | 1 | tie | same_results |
| Q2 | technical | hybrid | 1 | 1 | tie | same_results |
| Q3 | technical | hybrid | 2 | 2 | tie | same_results |
| Q4 | symbol | hybrid | 1 | 1 | tie | same_results |
| Q5 | symbol | hybrid | 1 | 1 | tie | same_results |
| Q6 | symbol | hybrid | 1 | 1 | tie | same_results |
| Q7 | symbol | hybrid | 2 | 2 | tie | same_results |
| Q8 | technical | hybrid | - | - | neither | no_expected_match |
| Q9 | conceptual | dense | - | - | neither | no_expected_match |
| Q10 | fallback | hybrid | - | - | neither | no_expected_match |
| Q11 | fallback | hybrid | 1 | 1 | tie | same_results |
| Q12 | technical | hybrid | 3 | 3 | tie | same_results |
| Q13 | technical | hybrid | 1 | 1 | tie | same_results |
| Q14 | technical | hybrid | 1 | 1 | tie | same_results |
| Q15 | technical | hybrid | 1 | 1 | tie | same_results |
| Q16 | technical | hybrid | 3 | 3 | tie | same_results |
| Q17 | symbol | hybrid | 1 | 1 | tie | same_results |
| Q18 | conceptual | dense | 3 | 5 | baseline | wrong_route |
| Q19 | technical | hybrid | 1 | 1 | tie | same_results |
| Q20 | technical | hybrid | 3 | 3 | tie | same_results |
| Q21 | technical | hybrid | 1 | 1 | tie | same_results |
| Q22 | technical | hybrid | 1 | 1 | tie | same_results |
| Q23 | technical | hybrid | 1 | 1 | tie | same_results |
| Q24 | fallback | hybrid | 1 | 1 | tie | same_results |
| Q25 | technical | hybrid | - | - | neither | no_expected_match |

## Adaptive Losses (Baseline Won)

### How does the search CLI work with different retriever modes?...

- Query type: conceptual
- Selected mode: dense
- Baseline mode: hybrid
- Baseline rank: 3
- Adaptive rank: 5
- Loss reason: wrong_route
- Expected files: ['scripts/search_repo.py']
- Baseline top files: ['README.md', 'src/code_rag/retrieval/hybrid.py', 'scripts/search_repo.py']
- Adaptive top files: ['src/code_rag/retrieval/hybrid.py', 'tests/test_bm25.py', 'tests/test_search_cli.py']
