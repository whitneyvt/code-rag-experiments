# KernelPack Chunk Coarseness Ablation

Comparison of retrieval granularity on Ram's KernelPack retrieval benchmark at a fixed re-retrieval budget of 5. All arms are read-only adapters over the existing v2 collection (`code_chunks_kernelpack_ram_v2`), which stores both fine 5-line windows and coarse AST chunks. Predictions reuse the reference body verbatim, so `repo_recall` (driven by which components the arm's retrieval surfaces) is the score that moves.

## Arm ranking (mean over tasks)

| Arm | Mean final | Mean recall | Mean precision | Mean alignment | Tasks fully matched |
|---|---:|---:|---:|---:|---:|
| coarse_only | 0.974 | 0.875 | 1.000 | 1.000 | 4/6 |
| fine_only | 1.000 | 1.000 | 1.000 | 1.000 | 6/6 |
| fine_to_coarse | 1.000 | 1.000 | 1.000 | 1.000 | 6/6 |
| fine_plus_parent | 1.000 | 1.000 | 1.000 | 1.000 | 6/6 |

## Per task / arm

| Task | Arm | Calls | Recall | Precision | F1 | Innate | Alignment | Final | Matched | Empty | Weak | First@ | All@ | Missed |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| easy | coarse_only | 4 | 0.500 | 1.000 | 0.667 | 1.000 | 1.000 | 0.889 | 2 | 0 | 0 | 1 | null | domain_descriptor_setup, scalar_c4_kernel_eval |
| easy | fine_only | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 4 | 1 | 0 | 2 | 3 | — |
| easy | fine_to_coarse | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 4 | 1 | 0 | 2 | 3 | — |
| easy | fine_plus_parent | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 4 | 1 | 0 | 2 | 3 | — |
| easy_2 | coarse_only | 4 | 0.750 | 1.000 | 0.857 | 1.000 | 1.000 | 0.952 | 3 | 0 | 0 | 1 | null | domain_descriptor_setup |
| easy_2 | fine_only | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 4 | 1 | 0 | 2 | 4 | — |
| easy_2 | fine_to_coarse | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 4 | 1 | 0 | 2 | 4 | — |
| easy_2 | fine_plus_parent | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 4 | 1 | 0 | 2 | 4 | — |
| easy_3 | coarse_only | 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 3 | 0 | 2 | 1 | 1 | — |
| easy_3 | fine_only | 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 3 | 0 | 2 | 1 | 1 | — |
| easy_3 | fine_to_coarse | 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 3 | 0 | 2 | 1 | 1 | — |
| easy_3 | fine_plus_parent | 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 3 | 0 | 2 | 1 | 1 | — |
| medium | coarse_only | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5 | 0 | 0 | 1 | 1 | — |
| medium | fine_only | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5 | 0 | 0 | 1 | 5 | — |
| medium | fine_to_coarse | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5 | 0 | 0 | 1 | 5 | — |
| medium | fine_plus_parent | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5 | 0 | 0 | 1 | 5 | — |
| medium_2 | coarse_only | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 4 | 0 | 0 | 1 | 1 | — |
| medium_2 | fine_only | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 4 | 1 | 0 | 2 | 3 | — |
| medium_2 | fine_to_coarse | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 4 | 1 | 0 | 2 | 3 | — |
| medium_2 | fine_plus_parent | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 4 | 1 | 0 | 2 | 3 | — |
| medium_3 | coarse_only | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5 | 0 | 0 | 1 | 5 | — |
| medium_3 | fine_only | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5 | 0 | 1 | 1 | 5 | — |
| medium_3 | fine_to_coarse | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5 | 1 | 1 | 2 | 5 | — |
| medium_3 | fine_plus_parent | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 5 | 0 | 1 | 1 | 5 | — |

## Interpretation

- `coarse_only` tests whether large semantic chunks alone recover the required repo components.
- `fine_only` tests whether precise 5-line chunks recover enough evidence.
- `fine_to_coarse` is the current v2 design (search fine, return coarse parents).
- `fine_plus_parent` adds the matched fine chunk alongside its parent; more evidence per call but more chunks to weigh.

## Per-task notes

### easy
- coarse_only: final=0.889 recall=0.500; missed domain_descriptor_setup, scalar_c4_kernel_eval; empty=0 weak=0
- fine_only: final=1.000 recall=1.000; all components matched; empty=1 weak=0
- fine_to_coarse: final=1.000 recall=1.000; all components matched; empty=1 weak=0
- fine_plus_parent: final=1.000 recall=1.000; all components matched; empty=1 weak=0

### easy_2
- coarse_only: final=0.952 recall=0.750; missed domain_descriptor_setup; empty=0 weak=0
- fine_only: final=1.000 recall=1.000; all components matched; empty=1 weak=0
- fine_to_coarse: final=1.000 recall=1.000; all components matched; empty=1 weak=0
- fine_plus_parent: final=1.000 recall=1.000; all components matched; empty=1 weak=0

### easy_3
- coarse_only: final=1.000 recall=1.000; all components matched; empty=0 weak=2
- fine_only: final=1.000 recall=1.000; all components matched; empty=0 weak=2
- fine_to_coarse: final=1.000 recall=1.000; all components matched; empty=0 weak=2
- fine_plus_parent: final=1.000 recall=1.000; all components matched; empty=0 weak=2

### medium
- coarse_only: final=1.000 recall=1.000; all components matched; empty=0 weak=0
- fine_only: final=1.000 recall=1.000; all components matched; empty=0 weak=0
- fine_to_coarse: final=1.000 recall=1.000; all components matched; empty=0 weak=0
- fine_plus_parent: final=1.000 recall=1.000; all components matched; empty=0 weak=0

### medium_2
- coarse_only: final=1.000 recall=1.000; all components matched; empty=0 weak=0
- fine_only: final=1.000 recall=1.000; all components matched; empty=1 weak=0
- fine_to_coarse: final=1.000 recall=1.000; all components matched; empty=1 weak=0
- fine_plus_parent: final=1.000 recall=1.000; all components matched; empty=1 weak=0

### medium_3
- coarse_only: final=1.000 recall=1.000; all components matched; empty=0 weak=0
- fine_only: final=1.000 recall=1.000; all components matched; empty=0 weak=1
- fine_to_coarse: final=1.000 recall=1.000; all components matched; empty=1 weak=1
- fine_plus_parent: final=1.000 recall=1.000; all components matched; empty=0 weak=1
