# Routing Diagnostics: evals/code_rag_real_world.json

- Baseline mode: `hybrid`
- Top K: 5
- Total queries: 35

## Summary

- **Adaptive wins**: 0
- **Baseline wins**: 0
- **Ties**: 20
- **Neither found**: 15

## Results by Category

| Category | Queries | Adaptive Wins | Baseline Wins | Ties | Neither |
| --- | --- | --- | --- | --- | --- |
| architecture | 5 | 0 | 0 | 1 | 4 |
| cli | 6 | 0 | 0 | 1 | 5 |
| conceptual | 3 | 0 | 0 | 1 | 2 |
| config | 6 | 0 | 0 | 5 | 1 |
| error | 4 | 0 | 0 | 2 | 2 |
| symbol | 4 | 0 | 0 | 4 | 0 |
| technical | 7 | 0 | 0 | 6 | 1 |

## Loss Reasons

- Wrong route: 0
- Expected missing from adaptive: 0
- Expected lower ranked: 0
- Same results: 20
- No expected match: 15

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

- hybrid: 35 (100.0%)

## Query Type -> Mode Mapping

- architecture -> hybrid: 5 (14.3%)
- cli -> hybrid: 6 (17.1%)
- config -> hybrid: 5 (14.3%)
- error -> hybrid: 2 (5.7%)
- symbol -> hybrid: 4 (11.4%)
- technical -> hybrid: 13 (37.1%)

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
| Q1 | error | error | hybrid | - | - | neither | no_expected_match |
| Q2 | error | error | hybrid | - | - | neither | no_expected_match |
| Q3 | error | technical | hybrid | 2 | 2 | tie | same_results |
| Q4 | error | technical | hybrid | 5 | 5 | tie | same_results |
| Q5 | cli | cli | hybrid | - | - | neither | no_expected_match |
| Q6 | cli | cli | hybrid | - | - | neither | no_expected_match |
| Q7 | cli | cli | hybrid | - | - | neither | no_expected_match |
| Q8 | cli | cli | hybrid | - | - | neither | no_expected_match |
| Q9 | cli | cli | hybrid | 1 | 1 | tie | same_results |
| Q10 | cli | cli | hybrid | - | - | neither | no_expected_match |
| Q11 | config | config | hybrid | 1 | 1 | tie | same_results |
| Q12 | config | config | hybrid | 1 | 1 | tie | same_results |
| Q13 | config | config | hybrid | - | - | neither | no_expected_match |
| Q14 | config | config | hybrid | 5 | 5 | tie | same_results |
| Q15 | config | technical | hybrid | 3 | 3 | tie | same_results |
| Q16 | config | config | hybrid | 1 | 1 | tie | same_results |
| Q17 | architecture | architecture | hybrid | - | - | neither | no_expected_match |
| Q18 | architecture | architecture | hybrid | - | - | neither | no_expected_match |
| Q19 | architecture | architecture | hybrid | - | - | neither | no_expected_match |
| Q20 | architecture | architecture | hybrid | - | - | neither | no_expected_match |
| Q21 | architecture | architecture | hybrid | 3 | 3 | tie | same_results |
| Q22 | technical | technical | hybrid | 2 | 2 | tie | same_results |
| Q23 | technical | technical | hybrid | 1 | 1 | tie | same_results |
| Q24 | technical | technical | hybrid | - | - | neither | no_expected_match |
| Q25 | technical | technical | hybrid | 4 | 4 | tie | same_results |
| Q26 | technical | technical | hybrid | 1 | 1 | tie | same_results |
| Q27 | technical | technical | hybrid | 1 | 1 | tie | same_results |
| Q28 | technical | technical | hybrid | 1 | 1 | tie | same_results |
| Q29 | symbol | symbol | hybrid | 1 | 1 | tie | same_results |
| Q30 | symbol | symbol | hybrid | 4 | 4 | tie | same_results |
| Q31 | symbol | symbol | hybrid | 1 | 1 | tie | same_results |
| Q32 | symbol | symbol | hybrid | 4 | 4 | tie | same_results |
| Q33 | conceptual | technical | hybrid | - | - | neither | no_expected_match |
| Q34 | conceptual | technical | hybrid | - | - | neither | no_expected_match |
| Q35 | conceptual | technical | hybrid | 1 | 1 | tie | same_results |
