# Toy demo: do comments help the search find the right code?

## 1. The toy problem

We used a tiny solver that estimates the Laplacian (a common second-derivative operator) on a small cloud of points in 2D, and then solves a simple Poisson problem. It is written as eight short functions you can read in a couple of minutes:

- `grid2d`
- `knn`
- `phi`
- `local_weights`
- `build_op`
- `set_bc`
- `spsolve`
- `rms`

We then asked six plain questions a user might type, and checked whether the search finds the correct function.

## 2. What the plain-code search did

First we searched the plain code with no comments added.

- It put the right function first for **0%** of the questions (Hit@1).
- The right function was in the top three for **33%** of the questions (Hit@3).
- Its average ranking score (MRR) was **0.29** (1.00 is perfect).

## 3. What changed after adding short comments

Then we added one short, plain-English comment to each function explaining what it is for, and searched again.

- The right function came first for **83%** of the questions (Hit@1).
- It was in the top three for **100%** of the questions (Hit@3).
- Its average ranking score (MRR) was **0.92**.

### Question-by-question

| Question | Right answer | Plain code top result | Commented top result | Did comments help? |
|---|---|---|---|---|
| Where is the Laplacian operator assembled? | `build_op` | `grid2d` | `build_op` | yes |
| Where are boundary conditions applied? | `set_bc` | `grid2d` | `set_bc` | yes |
| Where are nearest-neighbor stencils selected? | `knn` | `local_weights` | `knn` | yes |
| Where is the RBF kernel evaluated? | `phi` | `knn` | `phi` | yes |
| Where is the Poisson system solved? | `spsolve` | `grid2d` | `spsolve` | yes |
| Where is the numerical error computed? | `rms` | `grid2d` | `knn` | yes |

## 4. Did the search get better?

Yes. With comments the search put the right function first more often.

Questions that improved: "Where is the Laplacian operator assembled?", "Where are boundary conditions applied?", "Where are nearest-neighbor stencils selected?", "Where is the RBF kernel evaluated?", "Where is the Poisson system solved?", "Where is the numerical error computed?".

## 5. Did comments help keep the prompt small?

- Plain code: on average you would paste about **669 characters** of code to be sure the right function was included.
- Commented code: on average about **377 characters**.

So even though each commented function is a little longer, the search found the right function sooner, so you needed to paste less text overall. The prompt stayed small.

## 6. Next step with a real comment writer

Here we wrote the comments by hand as stand-ins. The next step is to have a language model write these short comments automatically, one function at a time, and store them next to the code only for search. The real code would not change, and the plain code would still be the main thing we search. If a real model writes clear, honest comments, we expect the same benefit seen here on a much larger set of functions.
