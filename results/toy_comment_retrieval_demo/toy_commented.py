"""Toy RBF-FD Laplacian solver on a small 2D point cloud."""

import numpy as np


def grid2d(n_side):
    """Make a small cloud of points on the unit square in 2D. It returns one row per point with its x and y position. This is the first step and decides where the solution will be computed."""
    xs = np.linspace(0.0, 1.0, n_side)
    ys = np.linspace(0.0, 1.0, n_side)
    gx, gy = np.meshgrid(xs, ys)
    return np.column_stack([gx.ravel(), gy.ravel()])


def knn(pts, i, k):
    """Pick the nearest neighbor points around one center point. These neighbors form the small local group (the stencil) used to estimate derivatives at that point. Inputs are all the points, which point is the center, and how many neighbors to keep."""
    d = np.linalg.norm(pts - pts[i], axis=1)
    return np.argsort(d)[:k]


def phi(r, eps):
    """Evaluate the Gaussian radial basis function (the RBF kernel) for a distance r and a shape parameter eps. This kernel says how strongly two points influence each other based on how far apart they are."""
    return np.exp(-((eps * r) ** 2))


def local_weights(pts, stencil, eps):
    """Build the small set of local weights that approximate the Laplacian (the second derivative) at one point. It solves a little linear system made from the kernel so that a weighted sum of neighbor values estimates the Laplacian. Called once for every point while filling the big matrix."""
    p = pts[stencil]
    r = np.linalg.norm(p[:, None, :] - p[None, :, :], axis=2)
    a = phi(r, eps)
    target = -4.0 * eps ** 2 * phi(r[0], eps)
    return np.linalg.solve(a, target)


def build_op(pts, k, eps):
    """Put the whole Laplacian operator together into one big matrix. It loops over every point, builds that point's local weights, and drops them into the correct spots of the full matrix. This is where the differential operator is assembled."""
    n = len(pts)
    m = np.zeros((n, n))
    for i in range(n):
        s = knn(pts, i, k)
        w = local_weights(pts, s, eps)
        for jj, j in enumerate(s):
            m[i, j] = w[jj]
    return m


def set_bc(m, rhs, idx, vals):
    """Apply the boundary conditions by fixing the solution value at the edge points. Each boundary row is rewritten so that point just keeps its known value. This happens after the matrix is assembled and before the system is solved."""
    for row, value in zip(idx, vals):
        m[row, :] = 0.0
        m[row, row] = 1.0
        rhs[row] = value
    return m, rhs


def spsolve(m, rhs):
    """Solve the Poisson system for the unknown values at all points. It takes the assembled matrix and the right-hand side and returns the numerical solution."""
    return np.linalg.solve(m, rhs)


def rms(u, exact):
    """Measure how close the numerical solution is to the exact answer using the root-mean-square error. Smaller numbers mean a more accurate result. Used at the very end to check quality."""
    d = u - exact
    return float(np.sqrt(np.mean(d ** 2)))
