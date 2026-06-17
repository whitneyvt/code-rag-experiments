"""Easy ground-truth driver: scalar interpolation with a global C4 Matern kernel."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import solve
from scipy.spatial.distance import cdist


def target_field(x: np.ndarray) -> np.ndarray:
    x0 = x[:, 0]
    x1 = x[:, 1]
    return (
        np.sin(2.0 * np.pi * x0) * np.cos(3.0 * np.pi * x1)
        + 0.2 * np.exp(-5.0 * ((x0 - 0.25) ** 2 + (x1 + 0.10) ** 2))
    )


def c4_matern_kernel(x: np.ndarray, y: np.ndarray, epsilon: float) -> np.ndarray:
    r = cdist(x, y)
    z = epsilon * r
    return np.exp(-z) * (3.0 + 3.0 * z + z**2)


def relative_l2(reference: np.ndarray, approximation: np.ndarray) -> float:
    return float(np.linalg.norm(reference - approximation) / np.linalg.norm(reference))


def distinct_uniform_points(
    rng: np.random.Generator,
    n: int,
    low: float,
    high: float,
    dim: int = 2,
) -> np.ndarray:
    points: list[tuple[float, ...]] = []
    seen: set[tuple[float, ...]] = set()
    while len(points) < n:
        batch = rng.uniform(low, high, size=(max(32, n - len(points)), dim))
        for row in batch:
            key = tuple(float(v) for v in row)
            if key not in seen:
                seen.add(key)
                points.append(key)
                if len(points) == n:
                    break
    return np.asarray(points, dtype=float)


@dataclass
class GlobalScalarInterpolant:
    epsilon: float
    nugget: float = 1e-10
    x_train: np.ndarray | None = None
    weights: np.ndarray | None = None

    def fit(self, x_train: np.ndarray, y_train: np.ndarray) -> "GlobalScalarInterpolant":
        self.x_train = np.asarray(x_train, dtype=float)
        y_train = np.asarray(y_train, dtype=float)
        k_train = c4_matern_kernel(self.x_train, self.x_train, self.epsilon)
        k_train = k_train + self.nugget * np.eye(k_train.shape[0])
        self.weights = solve(k_train, y_train, assume_a="pos")
        return self

    def predict(self, x_eval: np.ndarray) -> np.ndarray:
        if self.x_train is None or self.weights is None:
            raise RuntimeError("Call fit before predict.")
        k_eval = c4_matern_kernel(np.asarray(x_eval, dtype=float), self.x_train, self.epsilon)
        return k_eval @ self.weights


def sample_points(rng: np.random.Generator, n: int) -> np.ndarray:
    return distinct_uniform_points(rng, n, -1.0, 1.0)


def output_dir() -> Path:
    path = Path(os.environ.get("RAGSYSTEM_OUTPUT_DIR", ".")).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def main() -> None:
    rng = np.random.default_rng(4)

    node_counts = [50, 100, 500, 1000, 2000]
    epsilons = [0.75, 1.5, 3.0]
    eval_size = 500
    outdir = output_dir()

    x_eval = sample_points(rng, eval_size)
    y_true = target_field(x_eval)

    errors = np.zeros((len(node_counts), len(epsilons)))
    representative = None

    for i, n in enumerate(node_counts):
        x_train = sample_points(rng, n)
        y_train = target_field(x_train)
        for j, epsilon in enumerate(epsilons):
            model = GlobalScalarInterpolant(epsilon=epsilon).fit(x_train, y_train)
            y_pred = model.predict(x_eval)
            err = relative_l2(y_true, y_pred)
            errors[i, j] = err
            print(f"N={n:4d}, epsilon={epsilon:5.2f}, relL2={err:.3e}")
            if representative is None or (n == node_counts[-1] and epsilon == epsilons[1]):
                representative = (x_train, x_eval, y_pred, epsilon, n)

    with (outdir / "easy_scalar_c4_matern_errors.txt").open("w", encoding="utf-8") as fh:
        fh.write("# domain=[-1,1]x[-1,1]\n")
        fh.write("# sampling=uniform_random\n")
        fh.write("# rng_seed=4\n")
        fh.write("# evaluation_nodes=500\n")
        fh.write("# interpolation_nodes_distinct=True\n")
        fh.write("# target_field=sin(2*pi*x)*cos(3*pi*y)+0.2*exp(-5*((x-0.25)^2+(y+0.10)^2))\n")
        fh.write("# columns: N epsilon rel_l2\n")
        for i, n in enumerate(node_counts):
            for j, epsilon in enumerate(epsilons):
                fh.write(f"{n} {epsilon:.8f} {errors[i, j]:.16e}\n")

    fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
    for j, epsilon in enumerate(epsilons):
        ax.loglog(node_counts, errors[:, j], "-o", linewidth=1.8, label=fr"$\epsilon={epsilon}$")
    ax.set_xlabel("Number of interpolation nodes")
    ax.set_ylabel("Relative $L^2$ error")
    ax.set_title("Scalar C4 Matern interpolation ablation")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend()
    fig.savefig(outdir / "easy_scalar_c4_matern_ablation.png", dpi=220)

    assert representative is not None
    _, x_rep, y_rep, epsilon_rep, n_rep = representative
    point_error = np.abs(y_true - y_rep)

    fig2, axes = plt.subplots(1, 3, figsize=(13, 4), constrained_layout=True)
    sc0 = axes[0].scatter(x_rep[:, 0], x_rep[:, 1], c=y_true, s=6, cmap="viridis")
    axes[0].set_title("True field")
    fig2.colorbar(sc0, ax=axes[0])

    sc1 = axes[1].scatter(x_rep[:, 0], x_rep[:, 1], c=y_rep, s=6, cmap="viridis")
    axes[1].set_title(f"Predicted field\nN={n_rep}, epsilon={epsilon_rep}")
    fig2.colorbar(sc1, ax=axes[1])

    sc2 = axes[2].scatter(x_rep[:, 0], x_rep[:, 1], c=point_error, s=6, cmap="magma")
    axes[2].set_title("Pointwise absolute error")
    fig2.colorbar(sc2, ax=axes[2])
    for ax in axes:
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_aspect("equal")
    fig2.savefig(outdir / "easy_scalar_c4_matern_fields.png", dpi=220)
    plt.show()


if __name__ == "__main__":
    main()