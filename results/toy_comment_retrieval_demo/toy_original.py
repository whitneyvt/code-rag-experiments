"""Toy RBF-FD Laplacian solver on a small 2D point cloud."""

import numpy as np


def grid2d(n_side):
    xs = np.linspace(0.0, 1.0, n_side)
    ys = np.linspace(0.0, 1.0, n_side)
    gx, gy = np.meshgrid(xs, ys)
    return np.column_stack([gx.ravel(), gy.ravel()])


def knn(pts, i, k):
    d = np.linalg.norm(pts - pts[i], axis=1)
    return np.argsort(d)[:k]


def phi(r, eps):
    return np.exp(-((eps * r) ** 2))


def local_weights(pts, stencil, eps):
    p = pts[stencil]
    r = np.linalg.norm(p[:, None, :] - p[None, :, :], axis=2)
    a = phi(r, eps)
    target = -4.0 * eps ** 2 * phi(r[0], eps)
    return np.linalg.solve(a, target)


def build_op(pts, k, eps):
    n = len(pts)
    m = np.zeros((n, n))
    for i in range(n):
        s = knn(pts, i, k)
        w = local_weights(pts, s, eps)
        for jj, j in enumerate(s):
            m[i, j] = w[jj]
    return m


def set_bc(m, rhs, idx, vals):
    for row, value in zip(idx, vals):
        m[row, :] = 0.0
        m[row, row] = 1.0
        rhs[row] = value
    return m, rhs


def spsolve(m, rhs):
    return np.linalg.solve(m, rhs)


def rms(u, exact):
    d = u - exact
    return float(np.sqrt(np.mean(d ** 2)))
