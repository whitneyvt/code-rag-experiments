from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

from kernelpack import geometry, nodes


def output_dir() -> Path:
    return Path(os.environ.get("RAGSYSTEM_OUTPUT_DIR", ".")).resolve()


def main() -> None:
    out = output_dir()
    out.mkdir(parents=True, exist_ok=True)

    x_min = [0.0, 0.0]
    x_max = [1.0, 1.0]
    pts_a, info_a = nodes.generate_poisson_nodes_in_box(0.075, x_min, x_max, seed=19, strip_count=5)
    pts_b, _ = nodes.generate_poisson_nodes_in_box(0.075, x_min, x_max, seed=19, strip_count=5)

    d = geometry.distance_matrix(pts_a, pts_a)
    if pts_a.shape[0] > 1:
        d_no_diag = d.copy()
        np.fill_diagonal(d_no_diag, np.inf)
        min_spacing = float(np.min(d_no_diag))
    else:
        min_spacing = 0.0

    k1 = geometry.c4_matern_kernel(d, 1.0)
    k2 = geometry.c4_matern_kernel(d, 2.0)
    offdiag1 = k1 - np.diag(np.diag(k1))
    offdiag2 = k2 - np.diag(np.diag(k2))

    summary = {
        "node_count": int(pts_a.shape[0]),
        "deterministic": bool(np.array_equal(pts_a, pts_b) and info_a["deterministic"]),
        "min_pairwise_spacing": min_spacing,
        "kernel_cond_eps_1": float(np.linalg.cond(k1)),
        "kernel_cond_eps_2": float(np.linalg.cond(k2)),
        "kernel_diag_mean_eps_1": float(np.mean(np.diag(k1))),
        "kernel_diag_mean_eps_2": float(np.mean(np.diag(k2))),
        "kernel_offdiag_max_eps_1": float(np.max(offdiag1)),
        "kernel_offdiag_max_eps_2": float(np.max(offdiag2)),
    }
    (out / "kp_easy_3_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    thought = {
        "task_id": "kp_easy_3",
        "entries": [
            {
                "component_id": "poisson_sampler_setup",
                "origin": "repo",
                "summary": "Used the repository Poisson-disk helper with a fixed seed and strip count.",
                "repo_symbols": ["generate_poisson_nodes_in_box"],
                "repo_refs": ["tests/test_nodes_rbffd.py:7-10"],
                "code_markers": ["nodes.generate_poisson_nodes_in_box("]
            },
            {
                "component_id": "spacing_check",
                "origin": "repo",
                "summary": "Computed pairwise distances the same way the node-generation test checks minimum spacing.",
                "repo_symbols": ["distance_matrix"],
                "repo_refs": ["tests/test_nodes_rbffd.py:11-14", "src/kernelpack/geometry/core.py:13-14"],
                "code_markers": ["geometry.distance_matrix(", "np.fill_diagonal("]
            },
            {
                "component_id": "scalar_c4_kernel_eval",
                "origin": "repo",
                "summary": "Built two scalar C4 Matern kernel matrices using the repository geometry helpers.",
                "repo_symbols": ["distance_matrix", "c4_matern_kernel"],
                "repo_refs": ["tests/test_nodes_rbffd.py:63-69", "src/kernelpack/geometry/core.py:28-29"],
                "code_markers": ["geometry.distance_matrix(", "geometry.c4_matern_kernel("]
            },
            {
                "component_id": "box_definition",
                "origin": "innate",
                "summary": "Chose a simple unit box for the sampling experiment.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["x_min = [0.0, 0.0]", "x_max = [1.0, 1.0]"]
            },
            {
                "component_id": "determinism_check",
                "origin": "innate",
                "summary": "Compared two calls to confirm deterministic sampling under a fixed seed.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["np.array_equal(pts_a, pts_b)"]
            },
            {
                "component_id": "condition_number_calculation",
                "origin": "innate",
                "summary": "Computed condition numbers and simple kernel statistics for the two matrices.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["np.linalg.cond(k1)", "np.linalg.cond(k2)"]
            },
            {
                "component_id": "summary_writer",
                "origin": "innate",
                "summary": "Wrote the benchmark summary JSON.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["kp_easy_3_summary.json", "json.dumps(summary"]
            }
        ]
    }
    (out / "kp_easy_3_thought_process.json").write_text(json.dumps(thought, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()


# === Budgeted retrieval-provenance override (KernelPack ablation) ===
# The reference body above runs the real computation and writes the
# summary file. This block overwrites the thought-process JSON so its
# provenance reflects ONLY the repo components retrieved under this
# budget. Innate components are always included.
import json as _bp_json  # noqa: E402,F401
import os as _bp_os  # noqa: E402
from pathlib import Path as _bp_Path  # noqa: E402

_bp_out = _bp_Path(
    _bp_os.environ.get("RAGSYSTEM_OUTPUT_DIR", ".")
).resolve()
_bp_out.mkdir(parents=True, exist_ok=True)
_bp_thought_json = "{\n  \"task_id\": \"kp_easy_3\",\n  \"entries\": [\n    {\n      \"component_id\": \"poisson_sampler_setup\",\n      \"origin\": \"repo\",\n      \"summary\": \"Retrieved poisson_sampler_setup from the KernelPack repo under the current retrieval budget.\",\n      \"repo_symbols\": [\n        \"generate_poisson_nodes_in_box\"\n      ],\n      \"repo_refs\": [\n        \"tests/test_nodes_rbffd.py:7-10\"\n      ],\n      \"code_markers\": [\n        \"nodes.generate_poisson_nodes_in_box(\"\n      ]\n    },\n    {\n      \"component_id\": \"box_definition\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component box_definition; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    },\n    {\n      \"component_id\": \"determinism_check\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component determinism_check; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    },\n    {\n      \"component_id\": \"condition_number_calculation\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component condition_number_calculation; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    },\n    {\n      \"component_id\": \"summary_writer\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component summary_writer; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    }\n  ]\n}"
(_bp_out / "kp_easy_3_thought_process.json").write_text(
    _bp_thought_json, encoding="utf-8"
)
