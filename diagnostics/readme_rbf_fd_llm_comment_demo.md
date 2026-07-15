# README RBF-FD LLM Comment Retrieval Demo

## What we tested

We used the same small KernelPack README example (assembling an RBF-FD operator) and the same six questions as before. This time the short comments were written by a language model (answers pasted from a browser), not by hand. We compare three versions of the search: the plain code, the code with hand-written comments, and the code with the model-written comments.

## Summary numbers

| Version | Hit@1 | Hit@3 | MRR | Avg context size |
|---|---:|---:|---:|---:|
| Original code | 17% | 33% | 0.33 | 1354 characters |
| Hand-written comments | 67% | 83% | 0.79 | 855 characters |
| LLM-generated comments | 50% | 83% | 0.68 | 1229 characters |

## Question by question

| Question | Expected function | Original top result | Hand-commented top result | LLM-commented top result | Did LLM comments help? |
|---|---|---|---|---|---|
| Where does KernelPack make or load the points? | `generate_poisson_nodes_in_box` | `grad_op` | `generate_poisson_nodes_in_box` | `phs_kernel` | yes |
| Where does KernelPack choose nearest-neighbor stencils? | `query_knn` | `grad_op` | `from_accuracy` | `from_accuracy` | yes |
| Where does KernelPack evaluate the RBF kernel? | `phs_kernel` | `bc_op` | `assemble_op` | `phs_kernel` | yes |
| Where does KernelPack build local RBF-FD weights? | `compute_weights` | `bc_op` | `compute_weights` | `compute_weights` | yes |
| Where does KernelPack assemble the RBF-FD operator? | `assemble_op` | `bc_op` | `assemble_op` | `phs_kernel` | yes |
| Where are boundary conditions handled? | `bc_op` | `bc_op` | `bc_op` | `bc_op` | same |

## Comment quality checks

All model-written comments passed the simple checks (not empty, not too long, on-topic, no fake file paths, no code fences, and no mention of unrelated functions).

## Plain-English conclusion

The model-written comments made the search better than the plain code. The right function came first more often.

They helped, but a little less than the hand-written comments.

Steps that improved over the plain code: "Where does KernelPack make or load the points?", "Where does KernelPack choose nearest-neighbor stencils?", "Where does KernelPack evaluate the RBF kernel?", "Where does KernelPack build local RBF-FD weights?", "Where does KernelPack assemble the RBF-FD operator?".
No step got worse.
Steps where the right function was still not first: "Where does KernelPack make or load the points?", "Where does KernelPack choose nearest-neighbor stencils?", "Where does KernelPack assemble the RBF-FD operator?".

The model-commented version also needed less code to reach the right answer, so the prompt stayed smaller.

## What to do next

If this holds up, run the same simple check on more KernelPack functions, keep the model-written comments next to the code just for searching, and always run the quality checks so a weak or misleading comment gets caught before it is used.
