# Retrieval Budget Ablation

## Task
- task_id: external-medium-divergence-free-kernel
- difficulty: medium
- mode: fine_to_coarse_hybrid
- budgets: 2, 5, 20

## Summary Table

| Max retrievals | Calls used | Required found | Required missing | Unique files | Unique symbols | Runtime |
|---:|---:|---|---|---:|---:|---:|
| 2 | 2 | dfc4_matern_blocks | DivFreeGram, DivFreePHSInterpolant, divergence free | 3 | 9 | 3.436s |
| 5 | 5 | dfc4_matern_blocks, DivFreePHSInterpolant | DivFreeGram, divergence free | 5 | 24 | 3.533s |
| 20 | 5 | dfc4_matern_blocks, DivFreePHSInterpolant | DivFreeGram, divergence free | 5 | 24 | 3.426s |

## Per-budget Details

### Budget = 2
- Queries issued:
  1. divergence free C4 Matern dfc4_matern_blocks [module_filter=divfree]
  2. dfc4_matern_gram_matrix DivFreeGram epsilon [module_filter=divfree]
- Top retrieved files: src/kernelpack/divfree/__init__.py, src/kernelpack/divfree/core.py, tests/test_divfree.py
- Top retrieved symbols: DFPHS, _diff_tensor_from_coords, _stack_field, dfc4_matern_blocks, dfc4_matern_gram_matrix, initialize, test_dfc4_matern_3d_blocks_and_gram_shape, test_dfc4_matern_blocks_2d_match_manual_formula, test_dfc4_matern_periodic_2d_gram_matrix_is_symmetric
- Required symbols found: dfc4_matern_blocks
- Required symbols missing: DivFreeGram, DivFreePHSInterpolant, divergence free

### Budget = 5
- Queries issued:
  1. divergence free C4 Matern dfc4_matern_blocks [module_filter=divfree]
  2. dfc4_matern_gram_matrix DivFreeGram epsilon [module_filter=divfree]
  3. DivFreePHSInterpolant divergence free vector field [module_filter=divfree]
  4. conservation of mass incompressible interpolation kernel [module_filter=divfree]
  5. medium output columns N epsilon rel_l2_u rel_l2_v rel_l2_vec
- Top retrieved files: src/kernelpack/divfree/__init__.py, src/kernelpack/divfree/core.py, src/kernelpack/geometry/core.py, src/kernelpack/rbffd/core.py, tests/test_divfree.py
- Top retrieved symbols: DFPHS, DivFreePHSInterpolant, LocalDivFreeInterpolator, _assemble_one, _diff_tensor_from_coords, _rotational_field, _stack_field, build_closed_geometric_model_ps, build_level_set_from_cfi, build_planar_parametric_eval_nodes_2d
- Required symbols found: dfc4_matern_blocks, DivFreePHSInterpolant
- Required symbols missing: DivFreeGram, divergence free

### Budget = 20
Budget 20 allowed up to 20 retrievals, but planner used 5 because no more planned queries were available (planner has 5 planned queries).
- Queries issued:
  1. divergence free C4 Matern dfc4_matern_blocks [module_filter=divfree]
  2. dfc4_matern_gram_matrix DivFreeGram epsilon [module_filter=divfree]
  3. DivFreePHSInterpolant divergence free vector field [module_filter=divfree]
  4. conservation of mass incompressible interpolation kernel [module_filter=divfree]
  5. medium output columns N epsilon rel_l2_u rel_l2_v rel_l2_vec
- Top retrieved files: src/kernelpack/divfree/__init__.py, src/kernelpack/divfree/core.py, src/kernelpack/geometry/core.py, src/kernelpack/rbffd/core.py, tests/test_divfree.py
- Top retrieved symbols: DFPHS, DivFreePHSInterpolant, LocalDivFreeInterpolator, _assemble_one, _diff_tensor_from_coords, _rotational_field, _stack_field, build_closed_geometric_model_ps, build_level_set_from_cfi, build_planar_parametric_eval_nodes_2d
- Required symbols found: dfc4_matern_blocks, DivFreePHSInterpolant
- Required symbols missing: DivFreeGram, divergence free
