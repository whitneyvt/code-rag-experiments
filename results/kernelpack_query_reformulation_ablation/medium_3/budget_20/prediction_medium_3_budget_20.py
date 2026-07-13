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


def forcing_values(x: np.ndarray) -> np.ndarray:
    return -4.0 * np.ones(x.shape[0])


def normal_derivative(nr: np.ndarray, xb: np.ndarray) -> np.ndarray:
    grad = np.column_stack([2.0 * xb[:, 0], 2.0 * xb[:, 1]])
    return np.sum(grad * nr, axis=1)


def boundary_data(neu_coeffs: np.ndarray, dir_coeffs: np.ndarray, nr: np.ndarray, xb: np.ndarray) -> np.ndarray:
    return neu_coeffs * normal_derivative(nr, xb) + dir_coeffs * exact_solution(xb)


def main() -> None:
    out = output_dir()
    out.mkdir(parents=True, exist_ok=True)

    h = 0.1
    t = np.linspace(0.0, 2.0 * np.pi, 80, endpoint=False)
    curve = np.column_stack([np.cos(t), 0.8 * np.sin(t)])
    surface = geometry.EmbeddedSurface()
    surface.set_data_sites(curve)
    surface.build_closed_geometric_model_ps(2, 0.06, curve.shape[0])
    surface.build_level_set_from_geometric_model()

    generator = nodes.DomainNodeGenerator()
    domain = generator.build_domain_descriptor_from_geometry(
        surface,
        h,
        seed=17,
        strip_count=5,
        do_outer_refinement=True,
        outer_fraction_of_h=0.5,
        outer_refinement_zone_size_as_multiple_of_h=2.0,
    )

    solver = solvers.PoissonSolver(lap_assembler="fd", bc_assembler="fd", lap_stencil="rbf", bc_stencil="rbf")
    solver.init(domain, 3)
    neu_coeff = lambda xb: 0.6 + 0.15 * xb[:, 0] ** 2 + 0.05 * xb[:, 1] ** 2
    dir_coeff = lambda xb: 1.0 + 0.1 * xb[:, 0] ** 2 + 0.08 * xb[:, 1] ** 2
    solve_result = solver.solve(forcing_values, neu_coeff, dir_coeff, boundary_data)

    xphys = domain.get_int_bdry_nodes()
    u_true = exact_solution(xphys)
    err = solve_result["u"] - u_true
    err = err - np.mean(err)
    summary = {
        "h": h,
        "n_physical": int(xphys.shape[0]),
        "num_boundary_nodes": int(domain.get_bdry_nodes().shape[0]),
        "linf": float(np.max(np.abs(err))),
        "l2": float(np.linalg.norm(err) / np.sqrt(err.size)),
        "used_nullspace_augmentation": bool(solve_result["used_nullspace_augmentation"]),
    }
    (out / "kp_medium_3_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    thought = {
        "task_id": "kp_medium_3",
        "entries": [
            {
                "component_id": "curve_geometry_setup",
                "origin": "repo",
                "summary": "Built the closed curve geometry by following the solver test helper domain pattern.",
                "repo_symbols": ["EmbeddedSurface", "set_data_sites", "build_closed_geometric_model_ps", "build_level_set_from_geometric_model"],
                "repo_refs": ["tests/test_solvers.py:6-12"],
                "code_markers": ["geometry.EmbeddedSurface()", ".set_data_sites(", ".build_closed_geometric_model_ps(", ".build_level_set_from_geometric_model()"]
            },
            {
                "component_id": "domain_generation",
                "origin": "repo",
                "summary": "Generated the domain descriptor with the same refined geometry workflow used in the tests.",
                "repo_symbols": ["DomainNodeGenerator", "build_domain_descriptor_from_geometry"],
                "repo_refs": ["tests/test_solvers.py:13-22", "src/kernelpack/nodes/core.py:600-620"],
                "code_markers": ["nodes.DomainNodeGenerator()", ".build_domain_descriptor_from_geometry("]
            },
            {
                "component_id": "poisson_solver_setup",
                "origin": "repo",
                "summary": "Configured and initialized a PoissonSolver with fd assemblers and rbf stencils.",
                "repo_symbols": ["PoissonSolver", "init"],
                "repo_refs": ["tests/test_solvers.py:30-31", "src/kernelpack/solvers/poisson.py:24-68"],
                "code_markers": ["solvers.PoissonSolver(", ".init(domain,"]
            },
            {
                "component_id": "mixed_boundary_solve_call",
                "origin": "repo",
                "summary": "Solved with nonzero Neumann and Dirichlet coefficients through the repository solve path.",
                "repo_symbols": ["solve"],
                "repo_refs": ["tests/test_solvers.py:32-37", "src/kernelpack/solvers/poisson.py:70-122"],
                "code_markers": [".solve(", "neu_coeff", "dir_coeff", "boundary_data"]
            },
            {
                "component_id": "mean_aligned_error_postprocess",
                "origin": "repo",
                "summary": "Applied the same mean-aligned error reporting pattern used by the Neumann convergence example.",
                "repo_symbols": ["get_int_bdry_nodes"],
                "repo_refs": ["examples/poisson_convergence_2d_neumann.py:149-160"],
                "code_markers": ["domain.get_int_bdry_nodes()", "err = solve_result[\"u\"] - u_true", "err = err - np.mean(err)"]
            },
            {
                "component_id": "exact_solution_definition",
                "origin": "innate",
                "summary": "Defined the exact solution directly in the script.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["def exact_solution("]
            },
            {
                "component_id": "forcing_definition",
                "origin": "innate",
                "summary": "Defined the constant forcing for the chosen exact solution.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["def forcing_values("]
            },
            {
                "component_id": "boundary_data_definition",
                "origin": "innate",
                "summary": "Defined the mixed-boundary callback from the exact solution and its normal derivative.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["def boundary_data(", "def normal_derivative("]
            },
            {
                "component_id": "summary_writer",
                "origin": "innate",
                "summary": "Wrote the benchmark summary JSON.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["kp_medium_3_summary.json", "json.dumps(summary"]
            }
        ]
    }
    (out / "kp_medium_3_thought_process.json").write_text(json.dumps(thought, indent=2), encoding="utf-8")


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
_bp_thought_json = "{\n  \"task_id\": \"kp_medium_3\",\n  \"entries\": [\n    {\n      \"component_id\": \"curve_geometry_setup\",\n      \"origin\": \"repo\",\n      \"summary\": \"Retrieved curve_geometry_setup from the KernelPack repo under the current retrieval budget.\",\n      \"repo_symbols\": [\n        \"EmbeddedSurface\",\n        \"set_data_sites\",\n        \"build_closed_geometric_model_ps\",\n        \"build_level_set_from_geometric_model\"\n      ],\n      \"repo_refs\": [\n        \"tests/test_solvers.py:6-12\"\n      ],\n      \"code_markers\": [\n        \"geometry.EmbeddedSurface()\",\n        \".set_data_sites(\",\n        \".build_closed_geometric_model_ps(\",\n        \".build_level_set_from_geometric_model()\"\n      ]\n    },\n    {\n      \"component_id\": \"domain_generation\",\n      \"origin\": \"repo\",\n      \"summary\": \"Retrieved domain_generation from the KernelPack repo under the current retrieval budget.\",\n      \"repo_symbols\": [\n        \"DomainNodeGenerator\",\n        \"build_domain_descriptor_from_geometry\"\n      ],\n      \"repo_refs\": [\n        \"tests/test_solvers.py:13-22\",\n        \"src/kernelpack/nodes/core.py:600-620\"\n      ],\n      \"code_markers\": [\n        \"nodes.DomainNodeGenerator()\",\n        \".build_domain_descriptor_from_geometry(\"\n      ]\n    },\n    {\n      \"component_id\": \"poisson_solver_setup\",\n      \"origin\": \"repo\",\n      \"summary\": \"Retrieved poisson_solver_setup from the KernelPack repo under the current retrieval budget.\",\n      \"repo_symbols\": [\n        \"PoissonSolver\",\n        \"init\"\n      ],\n      \"repo_refs\": [\n        \"tests/test_solvers.py:30-31\",\n        \"src/kernelpack/solvers/poisson.py:24-68\"\n      ],\n      \"code_markers\": [\n        \"solvers.PoissonSolver(\",\n        \".init(domain,\"\n      ]\n    },\n    {\n      \"component_id\": \"mixed_boundary_solve_call\",\n      \"origin\": \"repo\",\n      \"summary\": \"Retrieved mixed_boundary_solve_call from the KernelPack repo under the current retrieval budget.\",\n      \"repo_symbols\": [\n        \"solve\"\n      ],\n      \"repo_refs\": [\n        \"tests/test_solvers.py:32-37\",\n        \"src/kernelpack/solvers/poisson.py:70-122\"\n      ],\n      \"code_markers\": [\n        \".solve(\",\n        \"neu_coeff\",\n        \"dir_coeff\",\n        \"boundary_data\"\n      ]\n    },\n    {\n      \"component_id\": \"mean_aligned_error_postprocess\",\n      \"origin\": \"repo\",\n      \"summary\": \"Retrieved mean_aligned_error_postprocess from the KernelPack repo under the current retrieval budget.\",\n      \"repo_symbols\": [\n        \"get_int_bdry_nodes\"\n      ],\n      \"repo_refs\": [\n        \"examples/poisson_convergence_2d_neumann.py:149-160\"\n      ],\n      \"code_markers\": [\n        \"domain.get_int_bdry_nodes()\",\n        \"err = solve_result[\\\"u\\\"] - u_true\",\n        \"err = err - np.mean(err)\"\n      ]\n    },\n    {\n      \"component_id\": \"exact_solution_definition\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component exact_solution_definition; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    },\n    {\n      \"component_id\": \"forcing_definition\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component forcing_definition; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    },\n    {\n      \"component_id\": \"boundary_data_definition\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component boundary_data_definition; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    },\n    {\n      \"component_id\": \"summary_writer\",\n      \"origin\": \"innate\",\n      \"summary\": \"Innate component summary_writer; produced without repo retrieval.\",\n      \"repo_symbols\": [],\n      \"repo_refs\": [],\n      \"code_markers\": []\n    }\n  ]\n}"
(_bp_out / "kp_medium_3_thought_process.json").write_text(
    _bp_thought_json, encoding="utf-8"
)
