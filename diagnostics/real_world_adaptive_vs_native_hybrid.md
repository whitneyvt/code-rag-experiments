# Routing Diagnostics: evals/code_rag_real_world.json

- Baseline mode: `native_hybrid`
- Top K: 5
- Total queries: 35

## Summary

- **Adaptive wins**: 0
- **Baseline wins**: 1
- **Ties**: 16
- **Neither found**: 18

## Results by Category

| Category | Queries | Adaptive Wins | Baseline Wins | Ties | Neither |
| --- | --- | --- | --- | --- | --- |
| architecture | 5 | 0 | 1 | 0 | 4 |
| cli | 6 | 0 | 0 | 1 | 5 |
| conceptual | 3 | 0 | 0 | 1 | 2 |
| config | 6 | 0 | 0 | 5 | 1 |
| error | 4 | 0 | 0 | 1 | 3 |
| symbol | 4 | 0 | 0 | 4 | 0 |
| technical | 7 | 0 | 0 | 4 | 3 |

## Loss Reasons

- Wrong route: 0
- Expected missing from adaptive: 1
- Expected lower ranked: 0
- Same results: 16
- No expected match: 18

## Eval Category Distribution

- architecture: 5 (14.3%)
- cli: 6 (17.1%)
- conceptual: 3 (8.6%)
- config: 6 (17.1%)
- error: 4 (11.4%)
- symbol: 4 (11.4%)
- technical: 7 (20.0%)

## Query Type Distribution

- architecture: 5 (14.3%)
- cli: 6 (17.1%)
- config: 5 (14.3%)
- error: 2 (5.7%)
- symbol: 4 (11.4%)
- technical: 13 (37.1%)

## Selected Mode Distribution

- native_hybrid: 35 (100.0%)

## Query Type -> Mode Mapping

- architecture -> native_hybrid: 5 (14.3%)
- cli -> native_hybrid: 6 (17.1%)
- config -> native_hybrid: 5 (14.3%)
- error -> native_hybrid: 2 (5.7%)
- symbol -> native_hybrid: 4 (11.4%)
- technical -> native_hybrid: 13 (37.1%)

## Category -> Query Type Mapping

- architecture -> architecture: 5 (14.3%)
- cli -> cli: 6 (17.1%)
- conceptual -> technical: 3 (8.6%)
- config -> config: 5 (14.3%)
- config -> technical: 1 (2.9%)
- error -> error: 2 (5.7%)
- error -> technical: 2 (5.7%)
- symbol -> symbol: 4 (11.4%)
- technical -> technical: 7 (20.0%)

## Per-Query Results

| query_id | category | query_type | selected_mode | baseline_rank | adaptive_rank | winner | reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | error | error | native_hybrid | - | - | neither | no_expected_match |
| Q2 | error | error | native_hybrid | - | - | neither | no_expected_match |
| Q3 | error | technical | native_hybrid | 4 | 4 | tie | same_results |
| Q4 | error | technical | native_hybrid | - | - | neither | no_expected_match |
| Q5 | cli | cli | native_hybrid | - | - | neither | no_expected_match |
| Q6 | cli | cli | native_hybrid | - | - | neither | no_expected_match |
| Q7 | cli | cli | native_hybrid | - | - | neither | no_expected_match |
| Q8 | cli | cli | native_hybrid | - | - | neither | no_expected_match |
| Q9 | cli | cli | native_hybrid | 5 | 5 | tie | same_rank_different_results |
| Q10 | cli | cli | native_hybrid | - | - | neither | no_expected_match |
| Q11 | config | config | native_hybrid | 2 | 2 | tie | same_results |
| Q12 | config | config | native_hybrid | 1 | 1 | tie | same_rank_different_results |
| Q13 | config | config | native_hybrid | - | - | neither | no_expected_match |
| Q14 | config | config | native_hybrid | 1 | 1 | tie | same_rank_different_results |
| Q15 | config | technical | native_hybrid | 5 | 5 | tie | same_results |
| Q16 | config | config | native_hybrid | 1 | 1 | tie | same_results |
| Q17 | architecture | architecture | native_hybrid | - | - | neither | no_expected_match |
| Q18 | architecture | architecture | native_hybrid | - | - | neither | no_expected_match |
| Q19 | architecture | architecture | native_hybrid | - | - | neither | no_expected_match |
| Q20 | architecture | architecture | native_hybrid | - | - | neither | no_expected_match |
| Q21 | architecture | architecture | native_hybrid | 5 | - | baseline | expected_missing_from_adaptive |
| Q22 | technical | technical | native_hybrid | - | - | neither | no_expected_match |
| Q23 | technical | technical | native_hybrid | - | - | neither | no_expected_match |
| Q24 | technical | technical | native_hybrid | - | - | neither | no_expected_match |
| Q25 | technical | technical | native_hybrid | 3 | 3 | tie | same_results |
| Q26 | technical | technical | native_hybrid | 3 | 3 | tie | same_results |
| Q27 | technical | technical | native_hybrid | 1 | 1 | tie | same_results |
| Q28 | technical | technical | native_hybrid | 1 | 1 | tie | same_rank_different_results |
| Q29 | symbol | symbol | native_hybrid | 3 | 3 | tie | same_results |
| Q30 | symbol | symbol | native_hybrid | 1 | 1 | tie | same_results |
| Q31 | symbol | symbol | native_hybrid | 1 | 1 | tie | same_results |
| Q32 | symbol | symbol | native_hybrid | 5 | 5 | tie | same_results |
| Q33 | conceptual | technical | native_hybrid | - | - | neither | no_expected_match |
| Q34 | conceptual | technical | native_hybrid | - | - | neither | no_expected_match |
| Q35 | conceptual | technical | native_hybrid | 1 | 1 | tie | same_results |

## Adaptive Losses (Baseline Won)

### Which parts of the codebase handle multi-vector fusion?...

- Query type: architecture
- Selected mode: native_hybrid
- Baseline mode: native_hybrid
- Baseline rank: 5
- Adaptive rank: None
- Loss reason: expected_missing_from_adaptive
- Expected files: ['src/code_rag/retrieval/evaluation_service.py', 'src/code_rag/retrieval/fusion.py']
- Baseline top files: ['src/code_rag/retrieval/search_service.py', 'src/code_rag/experiments/config.py', 'src/code_rag/retrieval/dense.py']
- Adaptive top files: ['src/code_rag/retrieval/search_service.py', 'src/code_rag/retrieval/router.py', 'src/code_rag/experiments/config.py']
