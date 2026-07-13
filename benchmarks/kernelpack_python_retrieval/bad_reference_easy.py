from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

from kernelpack import geometry


def output_dir() -> Path:
    return Path(os.environ.get("RAGSYSTEM_OUTPUT_DIR", ".")).resolve()


def main() -> None:
    out = output_dir()
    out.mkdir(parents=True, exist_ok=True)

    x = np.linspace(-1.0, 1.0, 5)
    xx, yy = np.meshgrid(x, x, indexing="xy")
    grid = np.column_stack([xx.ravel(), yy.ravel()])

    field = grid[:, 0] ** 2 + grid[:, 1] ** 2
    summary = {
        "num_nodes": int(grid.shape[0]),
        "field_mean": float(np.mean(field)),
        "kernel_trace": float(np.trace(geometry.c4_matern_kernel(geometry.distance_matrix(grid, grid), 1.3))),
    }
    (out / "kp_easy_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    thought = {
        "task_id": "kp_easy",
        "entries": [
            {
                "component_id": "domain_descriptor_setup",
                "origin": "innate",
                "summary": "Incorrectly claimed the domain descriptor setup was invented locally.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["grid = np.column_stack("],
            },
            {
                "component_id": "stencil_properties_setup",
                "origin": "repo",
                "summary": "Claims repo usage without actually implementing the stencil setup.",
                "repo_symbols": ["StencilProperties", "OpProperties"],
                "repo_refs": ["tests/test_nodes_rbffd.py:53-54"],
                "code_markers": ["rbffd.StencilProperties("],
            },
            {
                "component_id": "scalar_c4_kernel_eval",
                "origin": "repo",
                "summary": "Correctly used the scalar C4 Matern helper from the repository.",
                "repo_symbols": ["distance_matrix", "c4_matern_kernel"],
                "repo_refs": ["tests/test_nodes_rbffd.py:63-69", "src/kernelpack/geometry/core.py:13-28"],
                "code_markers": ["geometry.distance_matrix(", "geometry.c4_matern_kernel("],
            },
            {
                "component_id": "grid_generation",
                "origin": "innate",
                "summary": "Generated the structured 5x5 grid directly in the script.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["np.meshgrid(", "np.column_stack("],
            },
            {
                "component_id": "summary_writer",
                "origin": "innate",
                "summary": "Wrote the output summary JSON locally.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["kp_easy_summary.json", "json.dumps(summary"],
            },
        ],
    }
    (out / "kp_easy_thought_process.json").write_text(json.dumps(thought, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
