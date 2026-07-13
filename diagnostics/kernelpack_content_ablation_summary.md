# KernelPack Content Ablation: Code vs Comments

Compares retrieval when the searchable content is raw source code versus only the real comments/docstrings already present in the code. Retrieval mechanism: query-time in-memory re-embedding over v2 coarse-chunk payloads (matched subset only; no separate collections, no payload filter). Both arms search the identical matched subset (chunks with both code and comments), so only the embedding content differs. Operating point: budget 5, query reformulation enabled.

## Coverage

| Metric | Value |
|---|---:|
| Total chunks | 365 |
| Chunks with comments/docstrings | 63 |
| Comment coverage fraction | 0.173 |
| Matched subset chunks | 63 |
| Excluded (no comment) chunks | 302 |

## Required-component comment coverage

| Task | Required components w/ comment evidence | Excluded (no comment evidence) |
|---|---|---|
| easy | domain_descriptor_setup, stencil_properties_setup, fd_operator_assembly, scalar_c4_kernel_eval | — |
| easy_2 | domain_descriptor_setup, stencil_properties_setup, wls_operator_assembly, fdo_operator_assembly | — |
| easy_3 | poisson_sampler_setup, spacing_check, scalar_c4_kernel_eval | — |
| medium | circle_geometry_setup, domain_generation, poisson_solver_setup, poisson_solve_call | mean_aligned_error_postprocess |
| medium_2 | circle_geometry_setup, domain_generation, variable_poisson_solver_setup, variable_poisson_solve_call | — |
| medium_3 | curve_geometry_setup, domain_generation, poisson_solver_setup, mixed_boundary_solve_call | mean_aligned_error_postprocess |

## Results

| Task | Arm | Calls used | Repo recall | Repo precision | Repo F1 | Final score | Matched components | Missed components | Empty calls | Weak calls |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|
| easy | code_only | 5 | 0.500 | 1.000 | 0.667 | 0.889 | 2 | domain_descriptor_setup, scalar_c4_kernel_eval | 0 | 5 |
| easy | comments_only | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 4 | — | 0 | 4 |
| easy_2 | code_only | 5 | 0.750 | 1.000 | 0.857 | 0.952 | 3 | domain_descriptor_setup | 0 | 5 |
| easy_2 | comments_only | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 4 | — | 0 | 4 |
| easy_3 | code_only | 5 | 0.333 | 1.000 | 0.500 | 0.833 | 1 | scalar_c4_kernel_eval, spacing_check | 0 | 4 |
| easy_3 | comments_only | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 3 | — | 0 | 3 |
| medium | code_only | 5 | 0.800 | 1.000 | 0.889 | 0.963 | 4 | mean_aligned_error_postprocess | 0 | 3 |
| medium | comments_only | 5 | 0.800 | 1.000 | 0.889 | 0.963 | 4 | mean_aligned_error_postprocess | 0 | 4 |
| medium_2 | code_only | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 4 | — | 0 | 3 |
| medium_2 | comments_only | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 4 | — | 0 | 4 |
| medium_3 | code_only | 5 | 0.800 | 1.000 | 0.889 | 0.963 | 4 | mean_aligned_error_postprocess | 0 | 4 |
| medium_3 | comments_only | 5 | 0.800 | 1.000 | 0.889 | 0.963 | 4 | mean_aligned_error_postprocess | 0 | 4 |

## Interpretation

- Mean final score: code_only=0.933, comments_only=0.988.
- Mean repo recall: code_only=0.697, comments_only=0.933.
- Higher-scoring arm: **comments_only**.
- Tasks where comments_only reached full recall: easy, easy_2, easy_3, medium_2
- Comment coverage across the codebase is 17.3% of coarse chunks (63/365); 302 chunks carry no comment/docstring evidence at all.

Answers:
- Does code_only beat comments_only? See the mean scores above.
- Are comments sufficient for any tasks? See the full-recall list above.
- Which required components have no comment coverage? See the 'Excluded (no comment evidence)' column.
- Are comments-only failures from missing comments, bad retrieval, or weak semantic signal? Compare each task's excluded components (missing comments) against its empty/weak calls (bad retrieval) in the results table.
- Should comments-only be a real retrieval arm or supplemental evidence? Judge from whether it matches code_only within the matched subset and how much of the codebase it can even see.
