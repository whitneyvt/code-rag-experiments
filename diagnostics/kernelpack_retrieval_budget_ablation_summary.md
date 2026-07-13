# KernelPack Retrieval Budget Ablation

Provenance-coverage ablation of the agent re-retrieval budget over Ram's KernelPack retrieval benchmark. For each budget the deterministic planner issues at most N `retrieve_code` calls (one query per required component, manifest order) and only claims repo components with matching file/symbol evidence. Predictions reuse the reference body verbatim, so `repo_recall` (driven by retrieval coverage) is the quantity that moves with the budget.

| Task | Budget | Calls used | Repo recall | Repo precision | Repo F1 | Innate precision | Code alignment | Final score | Required matched | Required missed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| easy | 2 | 2 | 0.500 | 1.000 | 0.667 | 1.000 | 1.000 | 0.889 | 2/4 | domain_descriptor_setup, scalar_c4_kernel_eval |
| easy | 5 | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 4/4 | — |
| easy | 20 | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 4/4 | — |
| easy_2 | 2 | 2 | 0.750 | 1.000 | 0.857 | 1.000 | 1.000 | 0.952 | 3/4 | domain_descriptor_setup |
| easy_2 | 5 | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 4/4 | — |
| easy_2 | 20 | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 4/4 | — |
| easy_3 | 2 | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 3/3 | — |
| easy_3 | 5 | 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 3/3 | — |
| easy_3 | 20 | 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 3/3 | — |
| medium | 2 | 2 | 0.400 | 1.000 | 0.571 | 1.000 | 1.000 | 0.857 | 2/5 | mean_aligned_error_postprocess, poisson_solve_call, poisson_solver_setup |
| medium | 5 | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5/5 | — |
| medium | 20 | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5/5 | — |
| medium_2 | 2 | 2 | 0.250 | 1.000 | 0.400 | 1.000 | 1.000 | 0.800 | 1/4 | circle_geometry_setup, variable_poisson_solve_call, variable_poisson_solver_setup |
| medium_2 | 5 | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 4/4 | — |
| medium_2 | 20 | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 4/4 | — |
| medium_3 | 2 | 2 | 0.200 | 1.000 | 0.333 | 1.000 | 1.000 | 0.778 | 1/5 | curve_geometry_setup, mean_aligned_error_postprocess, mixed_boundary_solve_call, poisson_solver_setup |
| medium_3 | 5 | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5/5 | — |
| medium_3 | 20 | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5/5 | — |

## Interpretation

- Budget 2 shows whether a very small retrieval loop finds enough repo components.
- Budget 5 approximates a small agentic retrieval loop.
- Budget 20 tests whether extra re-retrieval improves provenance or adds noise.

## Per-task notes

### easy
- Budget 2 found: stencil_properties_setup, fd_operator_assembly
- Budget 5 added: domain_descriptor_setup, scalar_c4_kernel_eval
- Budget 20 added: (nothing new)
- Still missing at budget 20: none

### easy_2
- Budget 2 found: stencil_properties_setup, wls_operator_assembly, fdo_operator_assembly
- Budget 5 added: domain_descriptor_setup
- Budget 20 added: (nothing new)
- Still missing at budget 20: none

### easy_3
- Budget 2 found: poisson_sampler_setup, spacing_check, scalar_c4_kernel_eval
- Budget 5 added: (nothing new)
- Budget 20 added: (nothing new)
- Still missing at budget 20: none

### medium
- Budget 2 found: circle_geometry_setup, domain_generation
- Budget 5 added: mean_aligned_error_postprocess, poisson_solve_call, poisson_solver_setup
- Budget 20 added: (nothing new)
- Still missing at budget 20: none

### medium_2
- Budget 2 found: domain_generation
- Budget 5 added: circle_geometry_setup, variable_poisson_solve_call, variable_poisson_solver_setup
- Budget 20 added: (nothing new)
- Still missing at budget 20: none

### medium_3
- Budget 2 found: domain_generation
- Budget 5 added: curve_geometry_setup, mean_aligned_error_postprocess, mixed_boundary_solve_call, poisson_solver_setup
- Budget 20 added: (nothing new)
- Still missing at budget 20: none
