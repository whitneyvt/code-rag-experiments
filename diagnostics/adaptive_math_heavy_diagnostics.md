# Routing Diagnostics: evals/code_rag_math_heavy.json

- Baseline mode: `native_hybrid`
- Top K: 5
- Total queries: 15

## Summary

- **Adaptive wins**: 0
- **Baseline wins**: 0
- **Ties**: 12
- **Neither found**: 3

## Loss Reasons

- Wrong route: 0
- Expected missing from adaptive: 0
- Expected lower ranked: 0
- Same results: 12
- No expected match: 3

## Query Type Distribution

- conceptual: 1 (6.7%)
- config: 2 (13.3%)
- fallback: 1 (6.7%)
- technical: 11 (73.3%)

## Selected Mode Distribution

- native_hybrid: 15 (100.0%)

## Query Type -> Mode Mapping

- conceptual -> native_hybrid: 1 (6.7%)
- config -> native_hybrid: 2 (13.3%)
- fallback -> native_hybrid: 1 (6.7%)
- technical -> native_hybrid: 11 (73.3%)

## Per-Query Results

| query_id | query_type | selected_mode | baseline_rank | adaptive_rank | winner | reason |
| --- | --- | --- | --- | --- | --- | --- |
| Q1 | technical | native_hybrid | - | - | neither | no_expected_match |
| Q2 | technical | native_hybrid | 3 | 3 | tie | same_results |
| Q3 | technical | native_hybrid | 1 | 1 | tie | same_results |
| Q4 | technical | native_hybrid | 1 | 1 | tie | same_results |
| Q5 | fallback | native_hybrid | 1 | 1 | tie | same_results |
| Q6 | conceptual | native_hybrid | 2 | 2 | tie | same_results |
| Q7 | technical | native_hybrid | - | - | neither | no_expected_match |
| Q8 | technical | native_hybrid | 3 | 3 | tie | same_results |
| Q9 | technical | native_hybrid | 2 | 2 | tie | same_results |
| Q10 | technical | native_hybrid | 1 | 1 | tie | same_results |
| Q11 | technical | native_hybrid | 3 | 3 | tie | same_results |
| Q12 | technical | native_hybrid | - | - | neither | no_expected_match |
| Q13 | config | native_hybrid | 1 | 1 | tie | same_rank_different_results |
| Q14 | config | native_hybrid | 1 | 1 | tie | same_results |
| Q15 | technical | native_hybrid | 1 | 1 | tie | same_results |
