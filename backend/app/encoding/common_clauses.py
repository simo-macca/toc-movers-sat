"""CNF clause combinators for cardinality constraints.

Provides building blocks used by the SAT encoders to enforce at-most-one,
at-least-one, and exactly-one constraints over sets of literals.  Uses
the pairwise encoding for at-most-one (O(n^2) clauses), which is
efficient for the small literal sets in this problem.
"""

from itertools import combinations


def at_most_one(lits: list[int]) -> list[list[int]]:
    """Generate clauses enforcing that at most one literal is true.

    Uses pairwise negation: for every pair (a, b), adds clause [-a, -b].

    Args:
        lits: List of literal IDs.

    Returns:
        List of binary clauses.
    """
    return [[-a, -b] for a, b in combinations(lits, 2)]


def at_least_one(lits: list[int]) -> list[list[int]]:
    """Generate a clause enforcing that at least one literal is true.

    Args:
        lits: List of literal IDs.

    Returns:
        Single-element list containing the disjunction of all literals.
    """
    return [list(lits)]


def exactly_one(lits: list[int]) -> list[list[int]]:
    """Generate clauses enforcing that exactly one literal is true.

    Combines :func:`at_least_one` and :func:`at_most_one`.

    Args:
        lits: List of literal IDs.

    Returns:
        List of clauses (one disjunction + pairwise negations).
    """
    return at_least_one(lits) + at_most_one(lits)
