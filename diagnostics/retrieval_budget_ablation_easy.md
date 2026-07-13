# Retrieval Budget Ablation

## Task
- task_id: external-easy-scalar-c4-matern
- difficulty: easy
- mode: fine_to_coarse_hybrid
- budgets: 2, 5, 20

## Summary Table

| Max retrievals | Calls used | Required found | Required missing | Unique files | Unique symbols | Runtime |
|---:|---:|---|---|---:|---:|---:|
| 2 | 2 | Matern | RBF, interpolation | 4 | 9 | 4.284s |
| 5 | 5 | RBF, Matern | interpolation | 9 | 30 | 3.559s |
| 20 | 5 | RBF, Matern | interpolation | 9 | 30 | 3.590s |

## Per-budget Details

### Budget = 2
- Queries issued:
  1. scalar C4 Matern kernel interpolation epsilon [module_filter=rbffd]
  2. C4 Matern kernel formula exp(-z) 3 3 z z^2
- Top retrieved files: src/kernelpack/_numba.py, src/kernelpack/divfree/core.py, src/kernelpack/rbffd/core.py, tests/test_divfree.py
- Top retrieved symbols: _divfree_polynomial_stack, bc_op, dfc4_blocks_3d, dfc4_blocks_periodic_3d_z, dfc4_matern_blocks, dfc4_matern_gram_matrix, test_dfc4_matern_3d_blocks_and_gram_shape, test_dfc4_matern_blocks_2d_match_manual_formula, test_dfc4_matern_gram_matrix_is_symmetric_in_2d
- Required symbols found: Matern
- Required symbols missing: RBF, interpolation

### Budget = 5
- Queries issued:
  1. scalar C4 Matern kernel interpolation epsilon [module_filter=rbffd]
  2. C4 Matern kernel formula exp(-z) 3 3 z z^2
  3. RBF interpolation scalar target field relative L2 [module_filter=rbffd]
  4. KernelPack interpolation examples Matern epsilon
  5. checker output columns N epsilon rel_l2
- Top retrieved files: examples/pusl_incompressible_euler_convergence_2d.py, src/kernelpack/_numba.py, src/kernelpack/divfree/core.py, src/kernelpack/rbffd/core.py, src/kernelpack/solvers/_common.py, src/kernelpack/solvers/detail/incompressible_euler_bdf_backend.py, src/kernelpack/solvers/variable_poisson.py, tests/test_divfree.py, tests/test_nodes_rbffd.py
- Top retrieved symbols: FDDiffOp, FDODiffOp, _apply_operator, _assemble_operators, _divfree_polynomial_stack, _get_cached_system, _normalize_problem, assemble_op, bc_op, build_ilu_preconditioner
- Required symbols found: RBF, Matern
- Required symbols missing: interpolation

### Budget = 20
Budget 20 allowed up to 20 retrievals, but planner used 5 because no more planned queries were available (planner has 5 planned queries).
- Queries issued:
  1. scalar C4 Matern kernel interpolation epsilon [module_filter=rbffd]
  2. C4 Matern kernel formula exp(-z) 3 3 z z^2
  3. RBF interpolation scalar target field relative L2 [module_filter=rbffd]
  4. KernelPack interpolation examples Matern epsilon
  5. checker output columns N epsilon rel_l2
- Top retrieved files: examples/pusl_incompressible_euler_convergence_2d.py, src/kernelpack/_numba.py, src/kernelpack/divfree/core.py, src/kernelpack/rbffd/core.py, src/kernelpack/solvers/_common.py, src/kernelpack/solvers/detail/incompressible_euler_bdf_backend.py, src/kernelpack/solvers/variable_poisson.py, tests/test_divfree.py, tests/test_nodes_rbffd.py
- Top retrieved symbols: FDDiffOp, FDODiffOp, _apply_operator, _assemble_operators, _divfree_polynomial_stack, _get_cached_system, _normalize_problem, assemble_op, bc_op, build_ilu_preconditioner
- Required symbols found: RBF, Matern
- Required symbols missing: interpolation
