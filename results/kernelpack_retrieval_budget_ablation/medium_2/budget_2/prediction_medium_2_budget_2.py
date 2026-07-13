from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

from kernelpack import geometry, nodes, solvers


def output_dir() -> Path:
    return Path(os.environ.get("RAGSYSTEM_OUTPUT_DIR", ".")).resolve()


def exact_solution(x: np.ndarray) -> np.ndarray:
    return x[:, 0] ** 2 + x[:, 1] ** 2


def a_coeff(x: np.ndarray) -> np.ndarray:
    return 2.0 + x[:, 0] + 0.2 * x[:, 1]


def forcing_values(x: np.ndarray) -> np.ndarray:
    return -(4.0 * a_coeff(x) + 2.0 * x[:, 0] + 0.4 * x[:, 1])


def build_domain(h: float):
    t = np.linspace(0.0, 2.0 * np.pi, 80, endpoint=False)
    curve = np.column_stack([np.cos(t), 0.8 * np.sin(t)])
    surface = geometry.EmbeddedSurface()
    surface.set_data_sites(curve)
    surface.build_closed_geometric_model_ps(2, 0.06, curve.shape[0])
    surface.build_level_set_from_geometric_model()
    generator = nodes.DomainNodeGenerator()
    return generator.build_domain_descriptor_from_geometry(
        surface,
        h,
        seed=17,
        strip_count=5,
        do_outer_refinement=True,
        outer_fraction_of_h=0.5,
        outer_refinement_zone_size_as_multiple_of_h=2.0,
    )


def main() -> None:
    out = output_dir()
    out.mkdir(parents=True, exist_ok=True)

    h = 0.1
    domain = build_domain(h)
    xphys = domain.get_int_bdry_nodes()
    u_true = exact_solution(xphys)

    neu_coeff = lambda xb: np.zeros(xb.shape[0])
    dir_coeff = lambda xb: np.ones(xb.shape[0])
    boundary_data = lambda neu, dir_, nr, xb: exact_solution(xb)

    wls_solver = solvers.VariablePoissonSolver(lap_assembler="fd", bc_assembler="fd", lap_stencil="wls", bc_stencil="wls")
    wls_solver.init(domain, 3)
    wls_result = wls_solver.solve(forcing_values, a_coeff, neu_coeff, dir_coeff, boundary_data)

    rbf_solver = solvers.VariablePoissonSolver(lap_assembler="fd", bc_assembler="fd", lap_stencil="rbf", bc_stencil="rbf")
    rbf_solver.init(domain, 3)
    rbf_result = rbf_solver.solve(forcing_values, a_coeff, neu_coeff, dir_coeff, boundary_data)

    wls_err = wls_result["u"] - u_true
    rbf_err = rbf_result["u"] - u_true
    summary = {
        "h": h,
        "n_physical": int(xphys.shape[0]),
        "wls_linf": float(np.max(np.abs(wls_err))),
        "wls_l2": float(np.linalg.norm(wls_err) / np.sqrt(wls_err.size)),
        "rbf_linf": float(np.max(np.abs(rbf_err))),
        "rbf_l2": float(np.linalg.norm(rbf_err) / np.sqrt(rbf_err.size)),
        "wls_used_nullspace_augmentation": bool(wls_result["used_nullspace_augmentation"]),
        "rbf_used_nullspace_augmentation": bool(rbf_result["used_nullspace_augmentation"]),
    }
    (out / "kp_medium_2_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    thought = {
        "task_id": "kp_medium_2",
        "entries": [
            {
                "component_id": "circle_geometry_setup",
                "origin": "repo",
                "summary": "Built the smooth curve geometry by following the solver test helper domain.",
                "repo_symbols": ["EmbeddedSurface", "set_data_sites", "build_closed_geometric_model_ps", "build_level_set_from_geometric_model"],
                "repo_refs": ["tests/test_solvers.py:6-12"],
                "code_markers": ["geometry.EmbeddedSurface()", ".set_data_sites(", ".build_closed_geometric_model_ps(", ".build_level_set_from_geometric_model()"]
            },
            {
                "component_id": "domain_generation",
                "origin": "repo",
                "summary": "Generated the domain descriptor with outer refinement using the same test-domain pattern.",
                "repo_symbols": ["DomainNodeGenerator", "build_domain_descriptor_from_geometry"],
                "repo_refs": ["tests/test_solvers.py:13-22", "src/kernelpack/nodes/core.py:600-620"],
                "code_markers": ["nodes.DomainNodeGenerator()", ".build_domain_descriptor_from_geometry("]
            },
            {
                "component_id": "variable_poisson_solver_setup",
                "origin": "repo",
                "summary": "Configured and initialized two VariablePoissonSolver instances for wls and rbf stencils.",
                "repo_symbols": ["VariablePoissonSolver", "init"],
                "repo_refs": ["tests/test_solvers.py:70-82", "src/kernelpack/solvers/variable_poisson.py:47-113"],
                "code_markers": ["solvers.VariablePoissonSolver(", ".init(domain,"]
            },
            {
                "component_id": "variable_poisson_solve_call",
                "origin": "repo",
                "summary": "Solved the variable-coefficient Poisson problem with repository solve calls and coefficient callbacks.",
                "repo_symbols": ["solve"],
                "repo_refs": ["tests/test_solvers.py:72-89", "src/kernelpack/solvers/variable_poisson.py:115-178"],
                "code_markers": [".solve(", "a_coeff", "neu_coeff", "dir_coeff"]
            },
            {
                "component_id": "exact_solution_definition",
                "origin": "innate",
                "summary": "Defined the exact solution in the script.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["def exact_solution("]
            },
            {
                "component_id": "coefficient_field_definition",
                "origin": "innate",
                "summary": "Defined the spatially varying scalar coefficient field in the script.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["def a_coeff("]
            },
            {
                "component_id": "forcing_definition",
                "origin": "innate",
                "summary": "Defined the forcing term that matches the chosen coefficient field and exact solution.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["def forcing_values("]
            },
            {
                "component_id": "summary_writer",
                "origin": "innate",
                "summary": "Wrote the benchmark summary JSON.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["kp_medium_2_summary.json", "json.dumps(summary"]
            }
        ]
    }
    (out / "kp_medium_2_thought_process.json").write_text(json.dumps(thought, indent=2), encoding="utf-8")


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
_bp_thought_json = "{\n  \"task_id\": \"kp_medium_2\",\n  \"entries\": [\n    {\n      \"component_id\": \"domain_generation\",\n      \"origin\": \"repo\",\n      \"summary\": \"Retrieved domain_generation from the KernelPack repo under the current retrieval budget.\",\n      \"repo_symbols\": [\n        \"DomainNodeGenerator\",\n        \"build_domain_descriptor_from_geometry\"\n      ],\n      \"repo_refs\": [\n        \"tests/test_solvers.py:13-22\",\n        \"src/kernelpack/nodes/core.py:600-620\"\n      ],\n      \"code_markers\": [\n        \"nodes.DomainNodeGenerator()\",\n        \".build_domain_descriptor_from_geometry(\"\n      ]\n    },\n    {\n      \"component_id\": \"exact_solution_definition\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component exact_solution_definition; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    },\n    {\n      \"component_id\": \"coefficient_field_definition\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component coefficient_field_definition; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    },\n    {\n      \"component_id\": \"forcing_definition\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component forcing_definition; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    },\n    {\n      \"component_id\": \"summary_writer\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component summary_writer; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    }\n  ]\n}"
(_bp_out / "kp_medium_2_thought_process.json").write_text(
    _bp_thought_json, encoding="utf-8"
)
