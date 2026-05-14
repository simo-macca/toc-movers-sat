"""Solver orchestration layer.

Provides two entry points for running the PySAT solver:
:func:`solve_fixed` solves at a specific time horizon T, while
:func:`solve_optimal` performs iterative deepening (T = 0, 1, 2, ...)
to find the minimum T with a satisfying assignment.
"""

import time

from pysat.solvers import Solver

from app.config import settings
from app.models.problem import ProblemConfig, SolverResult, SolverStats
from app.encoding.variables import build_mapping
from app.encoding.task1_encoder import encode_task1
from app.encoding.task2_encoder import encode_task2
from app.solver.decoder import decode
from app.output.dimacs import cnf_to_dimacs_string


def _get_person_names(config: ProblemConfig) -> list[str]:
    """Return person display names, falling back to "person_0", "person_1", etc."""
    if config.person_names:
        return config.person_names
    return [f"person_{i}" for i in range(config.num_persons)]


def solve_fixed(
    config: ProblemConfig,
    task: int,
    T: int,
    goal_floors: dict[int, int] | None = None,
) -> SolverResult:
    """Encode and solve the movers problem at a fixed time horizon T.

    Encodes the problem as a CNF formula (Task 1 or 2), runs the SAT
    solver, and returns the full result including the decoded plan,
    DIMACS output, and performance statistics.

    Args:
        config: Problem specification.
        task: Task variant (1 = movement only, 2 = movement + items).
        T: Fixed time horizon.
        goal_floors: Target floors at time T for each person index.
            Only used for Task 1. Defaults to floor 0 for all persons.

    Returns:
        A SolverResult with ``satisfiable=True`` and a decoded plan on
        success, or ``satisfiable=False`` with stats on failure.
    """
    person_names = _get_person_names(config)

    if task == 1:
        if goal_floors is None:
            goal_floors = {p: 0 for p in range(config.num_persons)}
        cnf, pool = encode_task1(config.num_floors, config.num_persons, T, goal_floors)
    else:
        cnf, pool = encode_task2(config, T)

    start = time.perf_counter()
    with Solver(name=settings.solver_name, bootstrap_with=cnf) as solver:
        sat = solver.solve()
        elapsed_ms = (time.perf_counter() - start) * 1000

        if sat:
            model = solver.get_model()
            mapping = build_mapping(pool, person_names)
            plan = decode(model, pool, config, T, task)
            dimacs = cnf_to_dimacs_string(cnf, mapping)
            assignment = {mapping.get(abs(lit), str(abs(lit))): lit > 0 for lit in model}

            return SolverResult(
                satisfiable=True,
                num_time_steps=T,
                plan=plan,
                cnf_dimacs=dimacs,
                variable_mapping=mapping,
                stats=SolverStats(
                    num_variables=cnf.nv,
                    num_clauses=len(cnf.clauses),
                    solve_time_ms=round(elapsed_ms, 2),
                ),
            )

    return SolverResult(
        satisfiable=False,
        num_time_steps=T,
        stats=SolverStats(
            num_variables=cnf.nv,
            num_clauses=len(cnf.clauses),
            solve_time_ms=round(elapsed_ms, 2),
        ),
    )


def solve_optimal(
    config: ProblemConfig,
    task: int,
    max_T: int | None = None,
    goal_floors: dict[int, int] | None = None,
) -> SolverResult:
    """Find the minimum time horizon T that yields a satisfying assignment.

    Iteratively calls :func:`solve_fixed` for T = 0, 1, 2, ..., max_T
    and returns the first satisfiable result, guaranteeing the optimal
    (shortest) plan.

    Args:
        config: Problem specification.
        task: Task variant (1 or 2).
        max_T: Upper bound on T to try. Defaults to
            ``settings.max_time_steps`` (20).
        goal_floors: Target floors for Task 1 (see :func:`solve_fixed`).

    Returns:
        The first satisfiable SolverResult, or a result with
        ``satisfiable=False`` if no solution exists within max_T steps.
    """
    if max_T is None:
        max_T = settings.max_time_steps

    for T in range(max_T + 1):
        result = solve_fixed(config, task, T, goal_floors)
        if result.satisfiable:
            return result

    return SolverResult(
        satisfiable=False,
        stats=SolverStats(num_variables=0, num_clauses=0, solve_time_ms=0),
    )
