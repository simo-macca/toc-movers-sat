"""Serialize a CNF formula to the DIMACS CNF text format.

The DIMACS format is the standard interchange format for SAT solvers.
Output consists of comment lines (``c``), a problem line (``p cnf``),
and clause lines terminated by ``0``.
"""

from pysat.formula import CNF


def cnf_to_dimacs_string(cnf: CNF, mapping: dict[int, str]) -> str:
    """Convert a CNF formula and variable mapping to a DIMACS string.

    Args:
        cnf: PySAT CNF formula object.
        mapping: Variable ID to human-readable name mapping. Included
            as comment lines at the top of the output.

    Returns:
        Complete DIMACS CNF format string.
    """
    lines = []
    for var_id in sorted(mapping.keys()):
        lines.append(f"c {var_id} = {mapping[var_id]}")
    lines.append(f"p cnf {cnf.nv} {len(cnf.clauses)}")
    for clause in cnf.clauses:
        lines.append(" ".join(str(lit) for lit in clause) + " 0")
    return "\n".join(lines)
