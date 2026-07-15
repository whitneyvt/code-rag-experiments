# README RBF-FD Comment Retrieval Demo

## What we tested

We picked one small example from the KernelPack README: assembling an RBF-FD operator. We broke it into simple steps and asked whether the search can find the right KernelPack code for each step.

The steps of the example are:

1. Make or load the points to work on. (right answer: `generate_poisson_nodes_in_box`)
2. Choose the nearest-neighbor stencil around each point. (right answer: `query_knn`)
3. Evaluate the RBF kernel. (right answer: `phs_kernel`)
4. Build the local RBF-FD weights. (right answer: `compute_weights`)
5. Assemble the global operator matrix. (right answer: `assemble_op`)
6. Handle boundary conditions. (right answer: `bc_op`)

## Why this matters

Scientific code often uses short names that are clear to experts but hard for a search to understand (names like `phi`, `query_knn`, or `bc_op`). A short comment can explain the purpose of each function in plain English, which may help the search find the right code.

## The two experiments

1. Original code only.
2. The same code with one short comment added per function.

## Results

| Question | Expected code | Original top result | Commented top result | Did comments help? |
|---|---|---|---|---|
| Where does KernelPack make or load the points? | `generate_poisson_nodes_in_box` | `grad_op` | `generate_poisson_nodes_in_box` | yes |
| Where does KernelPack choose nearest-neighbor stencils? | `query_knn` | `grad_op` | `from_accuracy` | yes |
| Where does KernelPack evaluate the RBF kernel? | `phs_kernel` | `bc_op` | `assemble_op` | yes |
| Where does KernelPack build local RBF-FD weights? | `compute_weights` | `bc_op` | `compute_weights` | yes |
| Where does KernelPack assemble the RBF-FD operator? | `assemble_op` | `bc_op` | `assemble_op` | yes |
| Where are boundary conditions handled? | `bc_op` | `bc_op` | `bc_op` | same |

## Summary numbers

| Version | Hit@1 | Hit@3 | MRR | Average context size |
|---|---:|---:|---:|---:|
| Original code | 17% | 33% | 0.33 | 1354 characters |
| Commented code | 67% | 83% | 0.79 | 855 characters |

(Hit@1 and Hit@3: how often the right function was first, or in the top three. MRR: how high the right function ranked, where 1.00 is perfect. Average context size: how much code text you would paste to be sure the right function was included.)

## Plain-English conclusion

Adding short comments helped. The search put the right function first more often after the comments were added.

Steps that improved: "Where does KernelPack make or load the points?", "Where does KernelPack choose nearest-neighbor stencils?", "Where does KernelPack evaluate the RBF kernel?", "Where does KernelPack build local RBF-FD weights?", "Where does KernelPack assemble the RBF-FD operator?".

No step got worse after adding comments.

The commented version also needed less code to reach the right answer. Because the right function ranked higher, you would paste less text to the model, so the prompt stayed smaller.

## What to do next

Next, have a language model write these short comments automatically, one function at a time, and keep them next to the code just for searching. The real KernelPack code would not change, and the plain code would still be the main thing we search. If the model writes clear, honest comments, we expect the same benefit on the full KernelPack library.
