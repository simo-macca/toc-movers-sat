from pysat.solvers import Solver

from app.models.problem import ProblemConfig
from app.encoding.task1_encoder import encode_task1
from app.solver.runner import solve_optimal


def test_task1_3persons_reach_floor2_in_2_steps():
    """3 persons at floor 0 must reach floor 2 in exactly 2 steps (m=n=3)."""
    config = ProblemConfig(
        num_floors=3,
        num_persons=3,
        person_names=["Joe", "Bill", "Mia"],
    )
    goal_floors = {0: 2, 1: 2, 2: 2}
    result = solve_optimal(config, task=1, goal_floors=goal_floors)

    assert result.satisfiable is True
    assert result.num_time_steps == 2


def test_task1_unsatisfiable_in_1_step():
    """Cannot reach floor 2 from floor 0 in just 1 step."""
    goal_floors = {0: 2, 1: 2, 2: 2}
    cnf, pool = encode_task1(num_floors=3, num_persons=3, T=1, goal_floors=goal_floors)
    with Solver(name="g3", bootstrap_with=cnf) as solver:
        assert solver.solve() is False


def test_task1_trivial_already_at_goal():
    """If goal is floor 0 and start is floor 0, T=0 should work."""
    config = ProblemConfig(num_floors=3, num_persons=1)
    goal_floors = {0: 0}
    result = solve_optimal(config, task=1, goal_floors=goal_floors)

    assert result.satisfiable is True
    assert result.num_time_steps == 0


def test_task1_plan_shows_ascend_actions():
    """Verify the decoded plan shows ascend actions."""
    config = ProblemConfig(
        num_floors=3,
        num_persons=3,
        person_names=["Joe", "Bill", "Mia"],
    )
    goal_floors = {0: 2, 1: 2, 2: 2}
    result = solve_optimal(config, task=1, goal_floors=goal_floors)

    assert result.plan is not None
    assert len(result.plan) == 3  # t=0, t=1, t=2

    for step in result.plan[:2]:  # t=0, t=1
        for action in step.actions:
            assert action.action == "ascends"

    final_step = result.plan[2]
    for name in ["Joe", "Bill", "Mia"]:
        assert final_step.person_positions[name] == 2
