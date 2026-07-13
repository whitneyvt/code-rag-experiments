# Retrieval Budget Ablation

## Task
- task_id: external-hard-divergence-free-kernel
- difficulty: hard
- mode: fine_to_coarse_hybrid
- budgets: 2, 5, 20

## Summary Table

| Max retrievals | Calls used | Required found | Required missing | Unique files | Unique symbols | Runtime |
|---:|---:|---|---|---:|---:|---:|
| 2 | 2 | LocalDivFreeInterpolator | DFPHS, df_poly_basis_from_jacobi, divfree_gram_matrix | 3 | 7 | 3.352s |
| 5 | 5 | LocalDivFreeInterpolator, df_poly_basis_from_jacobi | DFPHS, divfree_gram_matrix | 5 | 17 | 3.375s |
| 20 | 5 | LocalDivFreeInterpolator, df_poly_basis_from_jacobi | DFPHS, divfree_gram_matrix | 5 | 17 | 3.765s |

## Per-budget Details

### Budget = 2
- Queries issued:
  1. LocalDivFreeInterpolator DFPHS polynomial degree PHS degree [module_filter=divfree]
  2. local divergence free interpolation stencil construction weighted least squares [module_filter=divfree]
- Top retrieved files: src/kernelpack/divfree/__init__.py, src/kernelpack/divfree/core.py, tests/test_divfree.py
- Top retrieved symbols: DivFreePHSInterpolant, LocalDivFreeInterpolator, test_dfc4_matern_blocks_2d_match_manual_formula, test_divfree_global_interpolant_reproduces_nodal_values, test_divfree_polynomial_basis_shape_and_eval, test_local_divfree_interpolator_reproduces_nodal_values, test_local_divfree_interpolator_smoke_3d
- Required symbols found: LocalDivFreeInterpolator
- Required symbols missing: DFPHS, df_poly_basis_from_jacobi, divfree_gram_matrix

### Budget = 5
- Queries issued:
  1. LocalDivFreeInterpolator DFPHS polynomial degree PHS degree [module_filter=divfree]
  2. local divergence free interpolation stencil construction weighted least squares [module_filter=divfree]
  3. DFPHS poly_order phs_degree sampling domain [-1, 1] [module_filter=divfree]
  4. RBF assembly local stencil polynomial basis divfree [module_filter=divfree]
  5. hard output columns poly_order N rel_l2_u rel_l2_v rel_l2_vec
- Top retrieved files: src/kernelpack/divfree/__init__.py, src/kernelpack/divfree/core.py, src/kernelpack/geometry/core.py, src/kernelpack/rbffd/core.py, tests/test_divfree.py
- Top retrieved symbols: DivFreePHSInterpolant, LocalDivFreeInterpolator, _assemble_one, _divfree_polynomial_stack, _eval_open_surface_frame, _solve_augmented_rbf_system, assemble_op, build_closed_geometric_model_ps, build_planar_parametric_eval_nodes_2d, df_poly_basis_from_jacobi
- Required symbols found: LocalDivFreeInterpolator, df_poly_basis_from_jacobi
- Required symbols missing: DFPHS, divfree_gram_matrix

### Budget = 20
Budget 20 allowed up to 20 retrievals, but planner used 5 because no more planned queries were available (planner has 5 planned queries).
- Queries issued:
  1. LocalDivFreeInterpolator DFPHS polynomial degree PHS degree [module_filter=divfree]
  2. local divergence free interpolation stencil construction weighted least squares [module_filter=divfree]
  3. DFPHS poly_order phs_degree sampling domain [-1, 1] [module_filter=divfree]
  4. RBF assembly local stencil polynomial basis divfree [module_filter=divfree]
  5. hard output columns poly_order N rel_l2_u rel_l2_v rel_l2_vec
- Top retrieved files: src/kernelpack/divfree/__init__.py, src/kernelpack/divfree/core.py, src/kernelpack/geometry/core.py, src/kernelpack/rbffd/core.py, tests/test_divfree.py
- Top retrieved symbols: DivFreePHSInterpolant, LocalDivFreeInterpolator, _assemble_one, _divfree_polynomial_stack, _eval_open_surface_frame, _solve_augmented_rbf_system, assemble_op, build_closed_geometric_model_ps, build_planar_parametric_eval_nodes_2d, df_poly_basis_from_jacobi
- Required symbols found: LocalDivFreeInterpolator, df_poly_basis_from_jacobi
- Required symbols missing: DFPHS, divfree_gram_matrix
