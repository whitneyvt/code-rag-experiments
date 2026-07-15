# Relevant KernelPack code for the README RBF-FD operator assembly example.
# These are short, real excerpts. This copy is only for the search demo;
# the real KernelPack code is not changed.

# === src/kernelpack/nodes/core.py :: generate_poisson_nodes_in_box ===
# comment: Creates a cloud of sample points inside a box using Poisson-disk sampling, which keeps the points spread out so no two are too close together. The inputs are a spacing radius (or a function that gives the spacing) and the lower and upper corners of the box, plus options like the number of attempts and a random seed. It returns the generated points. In the RBF-FD operator example, this is the first step that makes the points the operator will be built on.
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
# comment: Finds the k nearest neighbors of each query point using a KD-tree over the domain's points. These neighbors form the small local stencil that RBF-FD uses to estimate a derivative at a point. The inputs are which point set to search, the query points, and how many neighbors k to return; it returns the neighbor indices and their distances. In the operator example, this is how each center's stencil is picked before its weights are built.
def query_knn(self, tree_mode, query_points, k):
    tree, points = self._get_tree_data(tree_mode)
    query_points = np.atleast_2d(np.asarray(query_points, dtype=float))
    k = min(int(k), points.shape[0])
    distances, indices = tree.searcher.query(query_points, k=k)
    return indices, distances

# === src/kernelpack/geometry/core.py :: phs_kernel ===
# comment: Evaluates the polyharmonic spline radial basis function, the RBF kernel, for a set of distances and a chosen degree. This kernel sets how strongly points influence each other based on how far apart they are. The input is an array of distances r and the spline degree, and it returns the matching kernel values. In the operator example, this kernel is the building block used when forming the local RBF-FD weights.
def phs_kernel(r, degree):
    return phs_kernel_matrix(r, degree)

# === src/kernelpack/rbffd/core.py :: compute_weights ===
# comment: Builds the local RBF-FD weight row for one stencil so that a weighted sum of the neighbor values approximates the differential operator, such as the Laplacian, at the center point. The inputs are the local point positions and the stencil and operator settings, and it returns the weights for that row, sending interior and boundary points down the right path. In the operator example, this is the per-point weight calculation that fills each row of the global operator.
def compute_weights(self, x, *args):
    # The Matlab code routes both interior and boundary rows
    # through the same public entry point.
    sp, op, apply_op, rhs_indices = args[:4]
    return self._compute_weights_interior(x, sp, op, apply_op, rhs_indices)

# === src/kernelpack/rbffd/core.py :: assemble_op ===
# comment: Assembles the full sparse operator matrix by building one row per center point from that point's local stencil weights and scattering them into global form. The inputs are the domain, the operator name such as lap for the Laplacian, and the stencil and operator settings, and it fills in the assembled operator. In the README example, this is the main step that turns local weights into the global RBF-FD operator.
def assemble_op(self, domain, op_name, st_props, op_props, *, active_rows=None):
    # Assemble one sparse operator row per requested center. Each
    # row is built from a local stencil query, then scattered into
    # global triplet form before converting to CSR.
    center_points, center_row_ids, center_col_globals, center_normals = _pick_centers(
        domain, st_props.point_set)
    knn_indices = _query_center_stencils(domain, st_props.tree_mode, center_points, st_props.n)

# === src/kernelpack/rbffd/core.py :: bc_op ===
# comment: Builds the boundary rows of the operator by combining a normal-derivative Neumann part and a value Dirichlet part into each boundary row, matching the mixed boundary condition. The inputs are the stencil and operator settings, the Neumann and Dirichlet coefficients, and the local boundary geometry, and it returns the boundary rows. In the operator example, this is the step that handles boundary conditions during assembly.
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
