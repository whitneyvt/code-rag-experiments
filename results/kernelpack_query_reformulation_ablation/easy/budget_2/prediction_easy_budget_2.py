from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

from kernelpack import domain, geometry, rbffd


def output_dir() -> Path:
    return Path(os.environ.get("RAGSYSTEM_OUTPUT_DIR", ".")).resolve()


def main() -> None:
    out = output_dir()
    out.mkdir(parents=True, exist_ok=True)

    xg, yg = np.meshgrid(np.linspace(-1.0, 1.0, 5), np.linspace(-1.0, 1.0, 5), indexing="ij")
    x = np.column_stack([xg.ravel(), yg.ravel()])
    interior_mask = (np.abs(x[:, 0]) < 0.999) & (np.abs(x[:, 1]) < 0.999)
    active_rows = np.flatnonzero(interior_mask) + 1

    dd = domain.DomainDescriptor()
    dd.set_nodes(x, np.zeros((0, 2)), np.zeros((0, 2)))
    dd.set_sep_rad(0.5)
    dd.build_structs()

    sp = rbffd.StencilProperties(n=9, dim=2, ell=2, spline_degree=3, tree_mode="interior_boundary", point_set="interior_boundary")
    op = rbffd.OpProperties(record_stencils=True)
    f = x[:, 0] ** 2 + x[:, 1] ** 2
    fd_wls = rbffd.FDDiffOp(lambda: rbffd.WeightedLeastSquaresStencil())
    fd_wls.assemble_op(dd, "lap", sp, op, active_rows=active_rows)
    lap = fd_wls.get_op() @ f

    r = geometry.distance_matrix(x, x)
    k = geometry.c4_matern_kernel(r, 1.3)

    summary = {
        "grid_shape": [5, 5],
        "node_count": int(x.shape[0]),
        "active_row_count": int(active_rows.size),
        "max_abs_laplacian_error": float(np.max(np.abs(lap[active_rows - 1] - 4.0))),
        "c4_diagonal_mean": float(np.mean(np.diag(k))),
        "c4_offdiag_max": float(np.max(k - np.diag(np.diag(k)))),
    }
    (out / "kp_easy_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    thought = {
        "task_id": "kp_easy",
        "entries": [
            {
                "component_id": "domain_descriptor_setup",
                "origin": "repo",
                "summary": "Initialized a DomainDescriptor exactly in the style used by the rbffd test.",
                "repo_symbols": ["DomainDescriptor", "set_nodes", "set_sep_rad", "build_structs"],
                "repo_refs": ["tests/test_nodes_rbffd.py:49-52"],
                "code_markers": ["domain.DomainDescriptor()", ".set_nodes(", ".set_sep_rad(", ".build_structs()"]
            },
            {
                "component_id": "stencil_properties_setup",
                "origin": "repo",
                "summary": "Reused the explicit StencilProperties and OpProperties setup from the test fixture.",
                "repo_symbols": ["StencilProperties", "OpProperties"],
                "repo_refs": ["tests/test_nodes_rbffd.py:53-54"],
                "code_markers": ["rbffd.StencilProperties(", "rbffd.OpProperties("]
            },
            {
                "component_id": "fd_operator_assembly",
                "origin": "repo",
                "summary": "Assembled the Laplacian using FDDiffOp with WeightedLeastSquaresStencil.",
                "repo_symbols": ["FDDiffOp", "WeightedLeastSquaresStencil", "assemble_op", "get_op"],
                "repo_refs": ["tests/test_nodes_rbffd.py:56-59"],
                "code_markers": ["rbffd.FDDiffOp(", "rbffd.WeightedLeastSquaresStencil()", ".assemble_op(", ".get_op()"]
            },
            {
                "component_id": "scalar_c4_kernel_eval",
                "origin": "repo",
                "summary": "Used the scalar geometry helpers to build a C4 Matern kernel matrix.",
                "repo_symbols": ["distance_matrix", "c4_matern_kernel"],
                "repo_refs": ["tests/test_nodes_rbffd.py:63-69"],
                "code_markers": ["geometry.distance_matrix(", "geometry.c4_matern_kernel("]
            },
            {
                "component_id": "grid_generation",
                "origin": "innate",
                "summary": "Created a small Cartesian test grid with NumPy meshgrid.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["np.meshgrid("]
            },
            {
                "component_id": "interior_row_selection",
                "origin": "innate",
                "summary": "Selected strict interior rows with a boolean mask.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["interior_mask = ", "active_rows = "]
            },
            {
                "component_id": "quadratic_test_field",
                "origin": "innate",
                "summary": "Defined the quadratic field used to verify the Laplacian.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["f = x[:, 0] ** 2 + x[:, 1] ** 2"]
            },
            {
                "component_id": "summary_writer",
                "origin": "innate",
                "summary": "Wrote the summary JSON file required by the benchmark contract.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["kp_easy_summary.json", "json.dumps(summary"]
            }
        ]
    }
    (out / "kp_easy_thought_process.json").write_text(json.dumps(thought, indent=2), encoding="utf-8")


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
_bp_thought_json = "{\n  \"task_id\": \"kp_easy\",\n  \"entries\": [\n    {\n      \"component_id\": \"grid_generation\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component grid_generation; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    },\n    {\n      \"component_id\": \"interior_row_selection\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component interior_row_selection; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    },\n    {\n      \"component_id\": \"quadratic_test_field\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component quadratic_test_field; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    },\n    {\n      \"component_id\": \"summary_writer\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component summary_writer; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    }\n  ]\n}"
(_bp_out / "kp_easy_thought_process.json").write_text(
    _bp_thought_json, encoding="utf-8"
)
