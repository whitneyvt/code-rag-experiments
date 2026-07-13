# KernelPack Query Reformulation Ablation

Tests whether extra retrieval calls help an agent recover when early queries are weak. The deterministic reformulation planner uses the `fine_to_coarse` arm and retries each required component with progressively broader query variants (specific -> symbol_only -> marker_only -> file_hint -> broad_concept) whenever the previous call is empty or weak, until the component matches, its variants are exhausted, or the budget is spent.

## Summary

| Task | Budget | Calls used | Components matched | Repo recall | Repo F1 | Final score | Empty calls | Weak calls | Successful reformulations | All found at call |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| easy | 2 | 2 | 0/4 | 0.000 | 0.000 | 0.333 | 2 | 0 | 0 | null |
| easy | 5 | 3 | 4/4 | 1.000 | 1.000 | 1.000 | 2 | 0 | 1 | 3 |
| easy | 20 | 3 | 4/4 | 1.000 | 1.000 | 1.000 | 2 | 0 | 1 | 3 |
| easy_2 | 2 | 2 | 0/4 | 0.000 | 0.000 | 0.333 | 2 | 0 | 0 | null |
| easy_2 | 5 | 3 | 4/4 | 1.000 | 1.000 | 1.000 | 2 | 0 | 1 | 3 |
| easy_2 | 20 | 3 | 4/4 | 1.000 | 1.000 | 1.000 | 2 | 0 | 1 | 3 |
| easy_3 | 2 | 1 | 3/3 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 1 |
| easy_3 | 5 | 1 | 3/3 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 1 |
| easy_3 | 20 | 1 | 3/3 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 1 |
| medium | 2 | 2 | 2/5 | 0.400 | 0.571 | 0.857 | 0 | 0 | 0 | null |
| medium | 5 | 4 | 5/5 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 4 |
| medium | 20 | 4 | 5/5 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 4 |
| medium_2 | 2 | 2 | 0/4 | 0.000 | 0.000 | 0.333 | 2 | 0 | 0 | null |
| medium_2 | 5 | 4 | 4/4 | 1.000 | 1.000 | 1.000 | 3 | 0 | 1 | 4 |
| medium_2 | 20 | 4 | 4/4 | 1.000 | 1.000 | 1.000 | 3 | 0 | 1 | 4 |
| medium_3 | 2 | 2 | 0/5 | 0.000 | 0.000 | 0.333 | 2 | 0 | 0 | null |
| medium_3 | 5 | 5 | 5/5 | 1.000 | 1.000 | 1.000 | 3 | 0 | 1 | 5 |
| medium_3 | 20 | 5 | 5/5 | 1.000 | 1.000 | 1.000 | 3 | 0 | 1 | 5 |

## Successful query variants

| Variant | Times issued | Times it matched a component |
|---|---:|---:|
| specific | 27 | 15 |
| symbol_only | 12 | 0 |
| marker_only | 8 | 4 |
| file_hint | 4 | 4 |
| broad_concept | 0 | 0 |

## Interpretation

- Budget 2 tests whether the first query attempts are enough.
- Budget 5 tests whether limited query reformulation recovers missing components.
- Budget 20 tests whether many retries help or just add extra calls.

## Per-task findings

### easy
- Found on first query (or spillover): stencil_properties_setup, fd_operator_assembly, scalar_c4_kernel_eval
- Required reformulation: domain_descriptor_setup (marker_only)
- Budget 20 vs 2: recovered domain_descriptor_setup, fd_operator_assembly, scalar_c4_kernel_eval, stencil_properties_setup
- All components matched by budget 20.

### easy_2
- Found on first query (or spillover): stencil_properties_setup, wls_operator_assembly, fdo_operator_assembly
- Required reformulation: domain_descriptor_setup (marker_only)
- Budget 20 vs 2: recovered domain_descriptor_setup, fdo_operator_assembly, stencil_properties_setup, wls_operator_assembly
- All components matched by budget 20.

### easy_3
- Found on first query (or spillover): poisson_sampler_setup, spacing_check, scalar_c4_kernel_eval
- Required reformulation: none
- Budget 20 vs 2: no additional components
- All components matched by budget 20.

### medium
- Found on first query (or spillover): circle_geometry_setup, domain_generation, poisson_solver_setup, poisson_solve_call, mean_aligned_error_postprocess
- Required reformulation: none
- Budget 20 vs 2: recovered mean_aligned_error_postprocess, poisson_solve_call, poisson_solver_setup
- All components matched by budget 20.

### medium_2
- Found on first query (or spillover): domain_generation, variable_poisson_solver_setup, variable_poisson_solve_call
- Required reformulation: circle_geometry_setup (file_hint)
- Budget 20 vs 2: recovered circle_geometry_setup, domain_generation, variable_poisson_solve_call, variable_poisson_solver_setup
- All components matched by budget 20.

### medium_3
- Found on first query (or spillover): domain_generation, poisson_solver_setup, mixed_boundary_solve_call, mean_aligned_error_postprocess
- Required reformulation: curve_geometry_setup (file_hint)
- Budget 20 vs 2: recovered curve_geometry_setup, domain_generation, mean_aligned_error_postprocess, mixed_boundary_solve_call, poisson_solver_setup
- All components matched by budget 20.
