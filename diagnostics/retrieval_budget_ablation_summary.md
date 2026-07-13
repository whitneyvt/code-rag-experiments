# Retrieval Budget Ablation Summary

Ablation of the agent re-retrieval budget over the external interpolation tasks. For each budget the deterministic `budgeted_agent_retrieval` planner issues up to N `retrieve_code` calls (mode `fine_to_coarse_hybrid`, collection `code_chunks_kernelpack_ram_v2`, sparse vectors enabled) and stops when the budget or the planned query list is exhausted.

## Configuration
- collection: `code_chunks_kernelpack_ram_v2`
- mode: `fine_to_coarse_hybrid`
- sparse vectors: enabled (`QDRANT_ENABLE_SPARSE_VECTORS=true`)
- fine-to-coarse: enabled (`CODE_RAG_FINE_TO_COARSE=true`)
- budgets: 2, 5, 20
- k per call: 8

## Results

| Task | Difficulty | Budget | Calls used | Required found | Required missing | Unique files | Unique symbols |
|---|---|---:|---:|---|---|---:|---:|
| external-easy-scalar-c4-matern | easy | 2 | 2 | Matern | RBF, interpolation | 4 | 9 |
| external-easy-scalar-c4-matern | easy | 5 | 5 | RBF, Matern | interpolation | 9 | 30 |
| external-easy-scalar-c4-matern | easy | 20 | 5 | RBF, Matern | interpolation | 9 | 30 |
| external-medium-divergence-free-kernel | medium | 2 | 2 | dfc4_matern_blocks | DivFreeGram, DivFreePHSInterpolant, divergence free | 3 | 9 |
| external-medium-divergence-free-kernel | medium | 5 | 5 | dfc4_matern_blocks, DivFreePHSInterpolant | DivFreeGram, divergence free | 5 | 24 |
| external-medium-divergence-free-kernel | medium | 20 | 5 | dfc4_matern_blocks, DivFreePHSInterpolant | DivFreeGram, divergence free | 5 | 24 |
| external-hard-divergence-free-kernel | hard | 2 | 2 | LocalDivFreeInterpolator | DFPHS, df_poly_basis_from_jacobi, divfree_gram_matrix | 3 | 7 |
| external-hard-divergence-free-kernel | hard | 5 | 5 | LocalDivFreeInterpolator, df_poly_basis_from_jacobi | DFPHS, divfree_gram_matrix | 5 | 17 |
| external-hard-divergence-free-kernel | hard | 20 | 5 | LocalDivFreeInterpolator, df_poly_basis_from_jacobi | DFPHS, divfree_gram_matrix | 5 | 17 |

## Interpretation

Budget 2 shows whether one or two focused retrievals are enough. Budget 5 approximates a small agentic retrieval loop. Budget 20 tests whether allowing many re-retrievals gives extra useful context or just noise.

### Which task benefited from budget 5 over budget 2

- **easy** (external-easy-scalar-c4-matern): required symbols found went from 1 at budget 2 to 2 at budget 5 (gained RBF); unique files 4 → 9, unique symbols 9 → 30.
- **medium** (external-medium-divergence-free-kernel): required symbols found went from 1 at budget 2 to 2 at budget 5 (gained DivFreePHSInterpolant); unique files 3 → 5, unique symbols 9 → 24.
- **hard** (external-hard-divergence-free-kernel): required symbols found went from 1 at budget 2 to 2 at budget 5 (gained df_poly_basis_from_jacobi); unique files 3 → 5, unique symbols 7 → 17.

All three tasks benefited from budget 5 over budget 2: each picked up exactly one additional required symbol and roughly doubled its unique-symbol coverage. The second focused query is where the budget pays off.

### Whether budget 20 found anything new

- **easy**: budget 20 used 5 calls (capped by the planner's 5 planned queries) and returned identical files/symbols to budget 5.
- **medium**: budget 20 used 5 calls (capped by the planner's 5 planned queries) and returned identical files/symbols to budget 5.
- **hard**: budget 20 used 5 calls (capped by the planner's 5 planned queries) and returned identical files/symbols to budget 5.

Budget 20 found nothing new on any task. The deterministic planner currently defines only 5 planned queries per difficulty, so budgets above 5 are never reached — `retrieval_calls_used` stays at 5. This is expected and reported explicitly in each per-task report.

### Whether retrieval got noisier as budget increased

No. Because budget 20 is identical to budget 5, there is no extra noise beyond budget 5. From budget 2 to budget 5 the extra chunks were on-topic — they added the missing required symbols rather than off-target files — so the growth in unique files/symbols reflects useful coverage, not dilution.

### Required symbols found/missing per budget

**easy** (external-easy-scalar-c4-matern) — required: RBF, Matern, interpolation
- budget 2: found [Matern], missing [RBF, interpolation]
- budget 5: found [RBF, Matern], missing [interpolation]
- budget 20: found [RBF, Matern], missing [interpolation]

**medium** (external-medium-divergence-free-kernel) — required: dfc4_matern_blocks, DivFreeGram, DivFreePHSInterpolant, divergence free
- budget 2: found [dfc4_matern_blocks], missing [DivFreeGram, DivFreePHSInterpolant, divergence free]
- budget 5: found [dfc4_matern_blocks, DivFreePHSInterpolant], missing [DivFreeGram, divergence free]
- budget 20: found [dfc4_matern_blocks, DivFreePHSInterpolant], missing [DivFreeGram, divergence free]

**hard** (external-hard-divergence-free-kernel) — required: DFPHS, LocalDivFreeInterpolator, df_poly_basis_from_jacobi, divfree_gram_matrix
- budget 2: found [LocalDivFreeInterpolator], missing [DFPHS, df_poly_basis_from_jacobi, divfree_gram_matrix]
- budget 5: found [LocalDivFreeInterpolator, df_poly_basis_from_jacobi], missing [DFPHS, divfree_gram_matrix]
- budget 20: found [LocalDivFreeInterpolator, df_poly_basis_from_jacobi], missing [DFPHS, divfree_gram_matrix]

### Recommendation for future generation runs

Limit agent re-retrievals to **5**. Budget 2 is too tight — it consistently leaves one required symbol unfound. Budget 5 recovers the extra required symbol on every task and doubles symbol coverage. Budget 20 buys nothing today because the deterministic planner tops out at 5 queries; a larger budget would only matter once a live autonomous planner can generate genuinely new queries beyond the current fixed plan. Note that some required symbols (`interpolation` for easy; `DivFreeGram`/`divergence free` for medium; `DFPHS`/`divfree_gram_matrix` for hard) stay missing at every budget because the planner matches required strings against retrieved *symbol names* only — expanding the planned queries (not the budget) is the lever to close that gap.
