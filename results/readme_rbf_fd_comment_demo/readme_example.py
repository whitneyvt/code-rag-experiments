from kernelpack.rbffd import FDDiffOp, OpProperties, RBFStencil, StencilProperties

# Ask the code to choose stencil parameters from a target accuracy.
sp = StencilProperties.from_accuracy(
    operator="lap",
    convergence_order=4,
    dimension=2,
    approximation="rbf",
    tree_mode="all",
    point_set="interior_boundary",
)

# Record stencil metadata during assembly.
op = OpProperties(record_stencils=True)

# Assemble a Laplacian on the domain descriptor.
assembler = FDDiffOp(lambda: RBFStencil())
assembler.assemble_op(domain, "lap", sp, op)
L = assembler.get_op()
