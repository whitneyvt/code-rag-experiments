# KernelPack-Python Retrieval Benchmark

This sub-suite evaluates repository-grounded code generation for
`kernelpack-python` by scoring provenance, not PDE accuracy.

Each task asks a RAG system to generate:

- a standalone Python script
- a structured provenance log saved as a JSON file named
  `*_thought_process.json`

The checker scores:

- how many required repo components were retrieved correctly
- how many repo claims were valid
- how many innate/self-authored components were labeled correctly
- whether the claimed retrieved components actually appear in the generated code

Current tasks:

- `easy_1`
  - small 2D RBF-FD Laplacian driver on a structured grid
- `easy_2`
  - compare two finite-difference Laplacian assemblers on a structured grid
- `easy_3`
  - deterministic Poisson-disk sampling and scalar C4 Matern analysis
- `medium_1`
  - simple 2D pure-Neumann Poisson driver on a smooth circular domain
- `medium_2`
  - variable-coefficient Poisson driver on a smooth circular domain
- `medium_3`
  - mixed-boundary Poisson driver on a smooth closed curve

Files:

- `prompt_easy_1.txt`
- `prompt_easy_2.txt`
- `prompt_easy_3.txt`
- `prompt_medium_1.txt`
- `prompt_medium_2.txt`
- `prompt_medium_3.txt`
- `manifest_easy.json`
- `manifest_easy_2.json`
- `manifest_easy_3.json`
- `manifest_medium.json`
- `manifest_medium_2.json`
- `manifest_medium_3.json`
- `reference_easy.py`
- `reference_easy_2.py`
- `reference_easy_3.py`
- `reference_medium.py`
- `reference_medium_2.py`
- `reference_medium_3.py`
- `retrieval_checker.py`

Smoke-test commands:

```bash
python retrieval_checker.py easy reference_easy.py --min-final-score 0.99
python retrieval_checker.py easy_2 reference_easy_2.py --min-final-score 0.99
python retrieval_checker.py easy_3 reference_easy_3.py --min-final-score 0.99
python retrieval_checker.py medium reference_medium.py --min-final-score 0.99
python retrieval_checker.py medium_2 reference_medium_2.py --min-final-score 0.99
python retrieval_checker.py medium_3 reference_medium_3.py --min-final-score 0.99
```
