from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

from kernelpack import geometry, nodes, solvers


def output_dir() -> Path:
    return Path(os.environ.get("RAGSYSTEM_OUTPUT_DIR", ".")).resolve()


def exact_solution(x: np.ndarray) -> np.ndarray:
    return np.exp(x[:, 0] + x[:, 1])


def forcing_values(x: np.ndarray) -> np.ndarray:
    return -2.0 * np.exp(x[:, 0] + x[:, 1])


def boundary_flux(xb: np.ndarray, nr: np.ndarray) -> np.ndarray:
    grad = np.column_stack([np.exp(xb[:, 0] + xb[:, 1]), np.exp(xb[:, 0] + xb[:, 1])])
    return np.sum(grad * nr, axis=1)


def main() -> None:
    out = output_dir()
    out.mkdir(parents=True, exist_ok=True)

    h = 0.14
    t = np.linspace(0.0, 2.0 * np.pi, 120, endpoint=False)
    curve_sites = np.column_stack([np.cos(t), np.sin(t)])

    surface = geometry.EmbeddedSurface()
    surface.set_data_sites(curve_sites)
    surface.build_closed_geometric_model_ps(2, h, curve_sites.shape[0])
    surface.build_level_set_from_geometric_model()

    generator = nodes.DomainNodeGenerator()
    domain = generator.build_domain_descriptor_from_geometry(surface, h, seed=17, strip_count=5)

    solver = solvers.PoissonSolver(lap_assembler="fd", bc_assembler="fd", lap_stencil="rbf", bc_stencil="rbf")
    solver.init(domain, 2)
    neu_coeff = lambda xb: np.ones(xb.shape[0])
    dir_coeff = lambda xb: np.zeros(xb.shape[0])
    bc = lambda neu_coeffs, dir_coeffs, nr, xb: boundary_flux(xb, nr)
    solve_result = solver.solve(forcing_values, neu_coeff, dir_coeff, bc)

    xphys = domain.get_int_bdry_nodes()
    u_true = exact_solution(xphys)
    err = solve_result["u"] - u_true
    err = err - np.mean(err)
    summary = {
        "h": h,
        "n_physical": int(xphys.shape[0]),
        "linf": float(np.max(np.abs(err))),
        "l2": float(np.linalg.norm(err) / np.sqrt(err.size)),
        "used_nullspace_augmentation": bool(solve_result["used_nullspace_augmentation"]),
    }
    (out / "kp_medium_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    thought = {
        "task_id": "kp_medium",
        "entries": [
            {
                "component_id": "circle_geometry_setup",
                "origin": "repo",
                "summary": "Built the smooth circular geometry by following the 2D Poisson convergence example.",
                "repo_symbols": ["EmbeddedSurface", "set_data_sites", "build_closed_geometric_model_ps", "build_level_set_from_geometric_model"],
                "repo_refs": ["examples/poisson_convergence_2d_neumann.py:41-58"],
                "code_markers": ["geometry.EmbeddedSurface()", ".set_data_sites(", ".build_closed_geometric_model_ps(", ".build_level_set_from_geometric_model()"]
            },
            {
                "component_id": "domain_generation",
                "origin": "repo",
                "summary": "Used DomainNodeGenerator.build_domain_descriptor_from_geometry with the same seed/strip pattern as the example.",
                "repo_symbols": ["DomainNodeGenerator", "build_domain_descriptor_from_geometry"],
                "repo_refs": ["examples/poisson_convergence_2d_neumann.py:52-58"],
                "code_markers": ["nodes.DomainNodeGenerator()", ".build_domain_descriptor_from_geometry("]
            },
            {
                "component_id": "poisson_solver_setup",
                "origin": "repo",
                "summary": "Configured and initialized the PoissonSolver with fd/rbf settings.",
                "repo_symbols": ["PoissonSolver", "init"],
                "repo_refs": ["examples/poisson_convergence_2d_neumann.py:140-147", "src/kernelpack/solvers/poisson.py:46-68"],
                "code_markers": ["solvers.PoissonSolver(", ".init(domain, 2)"]
            },
            {
                "component_id": "poisson_solve_call",
                "origin": "repo",
                "summary": "Called solve with forcing, Neumann coefficients, zero Dirichlet coefficients, and a boundary callback.",
                "repo_symbols": ["solve"],
                "repo_refs": ["examples/poisson_convergence_2d_neumann.py:132-147", "src/kernelpack/solvers/poisson.py:70-122"],
                "code_markers": [".solve(", "neu_coeff", "dir_coeff", "boundary_flux"]
            },
            {
                "component_id": "mean_aligned_error_postprocess",
                "origin": "repo",
                "summary": "Applied the same mean-aligned error postprocessing used in the convergence example.",
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
                "summary": "Defined the matching forcing function directly in the script.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["def forcing_values("]
            },
            {
                "component_id": "boundary_flux_definition",
                "origin": "innate",
                "summary": "Defined the Neumann flux callback from the exact gradient.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["def boundary_flux("]
            },
            {
                "component_id": "summary_writer",
                "origin": "innate",
                "summary": "Wrote the summary JSON required by the benchmark.",
                "repo_symbols": [],
                "repo_refs": [],
                "code_markers": ["kp_medium_summary.json", "json.dumps(summary"]
            }
        ]
    }
    (out / "kp_medium_thought_process.json").write_text(json.dumps(thought, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
