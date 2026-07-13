from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

from kernelpack import domain, rbffd


def output_dir() -> Path:
    return Path(os.environ.get("RAGSYSTEM_OUTPUT_DIR", ".")).resolve()


def main() -> None:
    out = output_dir()
    out.mkdir(parents=True, exist_ok=True)

    xg, yg = np.meshgrid(np.linspace(-1.0, 1.0, 7), np.linspace(-1.0, 1.0, 7), indexing="ij")
    x = np.column_stack([xg.ravel(), yg.ravel()])
    interior_mask = (np.abs(x[:, 0]) < 0.999) & (np.abs(x[:, 1]) < 0.999)
    active_rows = np.flatnonzero(interior_mask) + 1

    dd = domain.DomainDescriptor()
    dd.set_nodes(x, np.zeros((0, 2)), np.zeros((0, 2)))
    dd.set_sep_rad(float(2.0 / 6.0))
    dd.build_structs()

    sp = rbffd.StencilProperties(n=9, dim=2, ell=2, spline_degree=3, tree_mode="interior_boundary", point_set="interior_boundary")
    op = rbffd.OpProperties(overlap_load=0.5)

    f = x[:, 0] ** 2 + x[:, 1] ** 2
    g = x[:, 0] ** 4 + x[:, 1] ** 4

    fd_wls = rbffd.FDDiffOp(lambda: rbffd.WeightedLeastSquaresStencil())
    fd_wls.assemble_op(dd, "lap", sp, op, active_rows=active_rows)
    lwls = fd_wls.get_op()

    fdo = rbffd.FDODiffOp()
    fdo.assemble_op(dd, "lap", sp, op, active_rows=active_rows)
    lfdo = fdo.get_op()

    lap_wls_f = lwls @ f
    lap_fdo_f = lfdo @ f
    lap_wls_g = lwls @ g
    lap_fdo_g = lfdo @ g
    g_truth = 12.0 * (x[:, 0] ** 2 + x[:, 1] ** 2)

    summary = {
        "grid_shape": [7, 7],
        "node_count": int(x.shape[0]),
        "active_row_count": int(active_rows.size),
        "wls_quadratic_max_error": float(np.max(np.abs(lap_wls_f[active_rows - 1] - 4.0))),
        "fdo_quadratic_max_error": float(np.max(np.abs(lap_fdo_f[active_rows - 1] - 4.0))),
        "wls_quartic_max_error": float(np.max(np.abs(lap_wls_g[active_rows - 1] - g_truth[active_rows - 1]))),
        "fdo_quartic_max_error": float(np.max(np.abs(lap_fdo_g[active_rows - 1] - g_truth[active_rows - 1]))),
    }
    (out / "kp_easy_2_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    thought = {
        "task_id": "kp_easy_2",
        "entries": [
            {
                "component_id": "domain_descriptor_setup",
                "origin": "repo",
                "summary": "Initialized the DomainDescriptor in the same style used by the fdodiffop test.",
                "repo_symbols": ["DomainDescriptor", "set_nodes", "set_sep_rad", "build_structs"],
                "repo_refs": ["tests/test_nodes_rbffd.py:77-80"],
                "code_markers": ["domain.DomainDescriptor()", ".set_nodes(", ".set_sep_rad(", ".build_structs()"]
            },
            {
                "component_id": "stencil_properties_setup",
                "origin": "repo",
                "summary": "Reused the explicit StencilProperties and OpProperties setup from the rbffd tests.",
                "repo_symbols": ["StencilProperties", "OpProperties"],
                "repo_refs": ["tests/test_nodes_rbffd.py:81-82"],
                "code_markers": ["rbffd.StencilProperties(", "rbffd.OpProperties("]
            },
            {
                "component_id": "wls_operator_assembly",
                "origin": "repo",
                "summary": "Assembled a Laplacian with FDDiffOp and WeightedLeastSquaresStencil.",
                "repo_symbols": ["FDDiffOp", "WeightedLeastSquaresStencil", "assemble_op", "get_op"],
                "repo_refs": ["tests/test_nodes_rbffd.py:85-90"],
                "code_markers": ["rbffd.FDDiffOp(", "rbffd.WeightedLeastSquaresStencil()", ".assemble_op(", ".get_op()"]
            },
            {
                "component_id": "fdo_operator_assembly",
                "origin": "repo",
                "summary": "Assembled the center-explicit comparison operator with FDODiffOp.",
                "repo_symbols": ["FDODiffOp", "assemble_op", "get_op"],
                "repo_refs": ["tests/test_nodes_rbffd.py:87-93"],
                "code_markers": ["rbffd.FDODiffOp(", ".assemble_op(", ".get_op()"]
            },
            {
                "component_id": "grid_generation",
                "origin": "innate",
                "summary": "Built the 7x7 Cartesian grid with NumPy meshgrid.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["np.meshgrid("]
            },
            {
                "component_id": "interior_row_selection",
                "origin": "innate",
                "summary": "Selected strict interior active rows with a boolean mask.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["interior_mask = ", "active_rows = "]
            },
            {
                "component_id": "quadratic_field_definition",
                "origin": "innate",
                "summary": "Defined the quadratic benchmark field.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["f = x[:, 0] ** 2 + x[:, 1] ** 2"]
            },
            {
                "component_id": "quartic_field_definition",
                "origin": "innate",
                "summary": "Defined the quartic benchmark field and exact Laplacian reference.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["g = x[:, 0] ** 4 + x[:, 1] ** 4", "g_truth = "]
            },
            {
                "component_id": "summary_writer",
                "origin": "innate",
                "summary": "Wrote the benchmark summary JSON.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["kp_easy_2_summary.json", "json.dumps(summary"]
            }
        ]
    }
    (out / "kp_easy_2_thought_process.json").write_text(json.dumps(thought, indent=2), encoding="utf-8")


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
_bp_thought_json = "{\n  \"task_id\": \"kp_easy_2\",\n  \"entries\": [\n    {\n      \"component_id\": \"stencil_properties_setup\",\n      \"origin\": \"repo\",\n      \"summary\": \"Retrieved stencil_properties_setup from the KernelPack repo under the current retrieval budget.\",\n      \"repo_symbols\": [\n        \"StencilProperties\",\n        \"OpProperties\"\n      ],\n      \"repo_refs\": [\n        \"tests/test_nodes_rbffd.py:81-82\",\n        \"src/kernelpack/rbffd/core.py:39-84\"\n      ],\n      \"code_markers\": [\n        \"rbffd.StencilProperties(\",\n        \"rbffd.OpProperties(\"\n      ]\n    },\n    {\n      \"component_id\": \"wls_operator_assembly\",\n      \"origin\": \"repo\",\n      \"summary\": \"Retrieved wls_operator_assembly from the KernelPack repo under the current retrieval budget.\",\n      \"repo_symbols\": [\n        \"FDDiffOp\",\n        \"WeightedLeastSquaresStencil\",\n        \"assemble_op\",\n        \"get_op\"\n      ],\n      \"repo_refs\": [\n        \"tests/test_nodes_rbffd.py:85-90\",\n        \"src/kernelpack/rbffd/core.py:500-584\"\n      ],\n      \"code_markers\": [\n        \"rbffd.FDDiffOp(\",\n        \"rbffd.WeightedLeastSquaresStencil()\",\n        \".assemble_op(\",\n        \".get_op()\"\n      ]\n    },\n    {\n      \"component_id\": \"fdo_operator_assembly\",\n      \"origin\": \"repo\",\n      \"summary\": \"Retrieved fdo_operator_assembly from the KernelPack repo under the current retrieval budget.\",\n      \"repo_symbols\": [\n        \"FDODiffOp\",\n        \"assemble_op\",\n        \"get_op\"\n      ],\n      \"repo_refs\": [\n        \"tests/test_nodes_rbffd.py:87-93\",\n        \"src/kernelpack/rbffd/core.py:584-640\"\n      ],\n      \"code_markers\": [\n        \"rbffd.FDODiffOp(\",\n        \".assemble_op(\",\n        \".get_op()\"\n      ]\n    },\n    {\n      \"component_id\": \"grid_generation\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component grid_generation; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    },\n    {\n      \"component_id\": \"interior_row_selection\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component interior_row_selection; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    },\n    {\n      \"component_id\": \"quadratic_field_definition\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component quadratic_field_definition; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    },\n    {\n      \"component_id\": \"quartic_field_definition\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component quartic_field_definition; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    },\n    {\n      \"component_id\": \"summary_writer\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component summary_writer; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    }\n  ]\n}"
(_bp_out / "kp_easy_2_thought_process.json").write_text(
    _bp_thought_json, encoding="utf-8"
)
