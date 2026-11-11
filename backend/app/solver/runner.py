"""Solver orchestration layer.

Provides two entry points for running the PySAT solver:
:func:`solve_fixed` solves at a specific time horizon T, while
:func:`solve_optimal` performs iterative deepening (T = lb, lb+1, ...)
starting from a provable lower bound ``lb`` to find the minimum T with a
satisfying assignment.
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


def horizon_lower_bound(
    config: ProblemConfig,
    task: int,
    goal_floors: dict[int, int] | None = None,
) -> int:
    """Return a lower bound on the optimal horizon T*.

    * Task 1: every mover starts on floor 0 and climbs at most one floor per
      step, so ``T* >= max(goal floor)``.
    * Task 2: an item on floor ``f`` can only start moving once a mover has
      climbed to ``f`` (at least ``f`` steps) and then needs ``f`` carry steps,
      so ``T* >= 2 * max(item floor)``.

    Horizons below this bound are guaranteed UNSAT and can be skipped.
    """
    if task == 1:
        return max(goal_floors.values(), default=0) if goal_floors else 0
    return 2 * max((it.initial_floor for it in config.items), default=0)


def solve_fixed(
    config: ProblemConfig,
    task: int,
    T: int,
    goal_floors: dict[int, int] | None = None,
) -> SolverResult:
    """Encode and solve the movers problem at a fixed time horizon T.

    Args:
        config: Problem specification.
        task: Task variant (1 = movement only, 2 = movement + items).
        T: Fixed time horizon.
        goal_floors: Target floors at time T for each person index.
            Only used for Task 1. Defaults to floor 0 for all persons.

    Returns:
        A SolverResult. ``plan`` is set only when satisfiable; the DIMACS
        formula, variable mapping and stats are always set.
    """
    person_names = _get_person_names(config)

    if task == 1:
        if goal_floors is None:
            goal_floors = {p: 0 for p in range(config.num_persons)}
        cnf, pool = encode_task1(config.num_floors, config.num_persons, T, goal_floors)
    else:
        cnf, pool = encode_task2(config, T)

    plan = None
    start = time.perf_counter()
    with Solver(name=settings.solver_name, bootstrap_with=cnf) as solver:
        sat = solver.solve()
        elapsed_ms = (time.perf_counter() - start) * 1000
        if sat:
            plan = decode(solver.get_model(), pool, config, T, task)

    mapping = build_mapping(pool, person_names)
    return SolverResult(
        satisfiable=bool(sat),
        num_time_steps=T,
        plan=plan,
        cnf_dimacs=cnf_to_dimacs_string(cnf, mapping),
        variable_mapping=mapping,
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

    Calls :func:`solve_fixed` for T = lb, lb+1, ..., max_T, where ``lb`` is
    :func:`horizon_lower_bound`, and returns the first satisfiable result.
    Because every T < lb is provably UNSAT, the first SAT horizon is optimal.

    Args:
        config: Problem specification.
        task: Task variant (1 or 2).
        max_T: Upper bound on T to try. Defaults to ``settings.max_time_steps``.
        goal_floors: Target floors for Task 1 (see :func:`solve_fixed`).

    Returns:
        The first satisfiable SolverResult, or the UNSAT result for ``max_T``
        if no solution exists within the bound. ``stats.solve_time_ms`` and
        ``stats.horizons_tried`` are totals over all horizons tried.
    """
    if max_T is None:
        max_T = settings.max_time_steps

    first_T = min(horizon_lower_bound(config, task, goal_floors), max_T)
    total_ms = 0.0
    tried = 0
    result: SolverResult | None = None

    for T in range(first_T, max_T + 1):
        result = solve_fixed(config, task, T, goal_floors)
        tried += 1
        total_ms += result.stats.solve_time_ms
        if result.satisfiable:
            break

    result.stats.solve_time_ms = round(total_ms, 2)
    result.stats.horizons_tried = tried
    return result
