# Relevant KernelPack code for the README RBF-FD operator assembly example.
# These are short, real excerpts. This copy is only for the search demo;
# the real KernelPack code is not changed.

# === src/kernelpack/nodes/core.py :: generate_poisson_nodes_in_box ===
# comment: Make a fresh cloud of sample points inside a box using Poisson-disk sampling, so the points are spread out evenly. You pass a spacing radius and the box corners, and it returns the generated points. This is the 'make the points' step of the example.
def generate_poisson_nodes_in_box(
    radius_or_func,
    x_min,
    x_max,
    *,
    attempts=30,
    seed=None,
    deterministic=None,
    use_parallel=True,
):
    ...

# === src/kernelpack/domain/core.py :: query_knn ===
# comment: Find the k nearest neighbor points around each point using a KD-tree. These neighbors are the small local group (the stencil) that RBF-FD uses at each point. It returns the neighbor indices and distances. This is the 'choose nearest-neighbor stencils' step.
def query_knn(self, tree_mode, query_points, k):
    tree, points = self._get_tree_data(tree_mode)
    query_points = np.atleast_2d(np.asarray(query_points, dtype=float))
    k = min(int(k), points.shape[0])
    distances, indices = tree.searcher.query(query_points, k=k)
    return indices, distances

# === src/kernelpack/geometry/core.py :: phs_kernel ===
# comment: Evaluate the polyharmonic spline radial basis function -- the RBF kernel -- for a distance r and a degree. This kernel decides how strongly neighbor points influence each other based on distance. It returns the kernel values. This is the 'evaluate the RBF kernel' step.
def phs_kernel(r, degree):
    return phs_kernel_matrix(r, degree)

# === src/kernelpack/rbffd/core.py :: compute_weights ===
# comment: Build the local RBF-FD weights for one stencil, so a weighted sum of neighbor values approximates the operator (such as the Laplacian). You pass the local point positions and stencil settings, and it returns the weight row. This is the 'build local RBF-FD weights' step.
def compute_weights(self, x, *args):
    # The Matlab code routes both interior and boundary rows
    # through the same public entry point.
    sp, op, apply_op, rhs_indices = args[:4]
    return self._compute_weights_interior(x, sp, op, apply_op, rhs_indices)

# === src/kernelpack/rbffd/core.py :: assemble_op ===
# comment: Assemble the full sparse RBF-FD operator matrix by building one row per center point from its local stencil weights. You pass the domain and stencil settings, and it fills in the global operator. This is the 'assemble the RBF-FD operator' step.
def assemble_op(self, domain, op_name, st_props, op_props, *, active_rows=None):
    # Assemble one sparse operator row per requested center. Each
    # row is built from a local stencil query, then scattered into
    # global triplet form before converting to CSR.
    center_points, center_row_ids, center_col_globals, center_normals = _pick_centers(
        domain, st_props.point_set)
    knn_indices = _query_center_stencils(domain, st_props.tree_mode, center_points, st_props.n)

# === src/kernelpack/rbffd/core.py :: bc_op ===
# comment: Build the boundary rows of the operator, mixing the normal-derivative (Neumann) part and the value (Dirichlet) part. You pass the boundary coefficients and local geometry, and it returns the boundary rows. This is the 'boundary conditions' step.
def bc_op(self, sp, op, neu_coeff, dir_coeff, r_rhs, x_subset, x, x_at_origin_subset, x_at_origin, nr_subset):
    total = np.zeros((self.n + self.npoly, x_at_origin_subset.shape[0]))
    if neu_coeff != 0:
        for d in range(self.s_dim):
            diff = x_subset[:, d : d + 1] - x[None, :, d]
            grad_rbf = (diff * self.phs_dr_over_r(r_rhs, sp.spline_degree)).T
    return total

# === src/kernelpack/rbffd/core.py :: from_accuracy ===
# comment: Pick stencil settings automatically from a target accuracy order. It returns a settings object. It only configures the stencil; it does not find neighbors or build weights.
def from_accuracy(cls, *, operator="lap", convergence_order=None, dimension, approximation="rbf"):
    ...

# === src/kernelpack/rbffd/core.py :: get_op ===
# comment: Return the finished sparse operator matrix after assembly is done. It only packages already-computed values into a sparse matrix.
def get_op(self):
    rows = self.locations[:, 0] - 1
    cols = self.locations[:, 1] - 1
    return sparse.csr_matrix((self.values, (rows, cols)), shape=(self.n1, self.n2))

# === src/kernelpack/geometry/core.py :: distance_matrix ===
# comment: Compute the pairwise distances between two sets of points. A small geometry helper used in many places.
def distance_matrix(x, y):
    return dense_distance_matrix(x, y)

# === src/kernelpack/rbffd/core.py :: grad_op ===
# comment: Build the gradient (first-derivative) rows for a stencil. Similar to the Laplacian rows but for the gradient operator.
def grad_op(self, sp, op, r_rhs, x_subset, x, x_at_origin_subset, _x_at_origin):
    dim = op.selectdim
    diff = x_subset[:, dim : dim + 1] - x[None, :, dim]
    top = (diff * self.phs_dr_over_r(r_rhs, sp.spline_degree)).T
    return top
