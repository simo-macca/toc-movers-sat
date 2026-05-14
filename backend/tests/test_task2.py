from app.models.problem import ProblemConfig, ItemPlacement
from app.solver.runner import solve_optimal, solve_fixed


def _task2_config() -> ProblemConfig:
    """Task 2 configuration: m=n=3, 3 items (as listed in problem statement)."""
    return ProblemConfig(
        num_floors=3,
        num_persons=3,
        person_names=["Joe", "Bill", "Mia"],
        items=[
            ItemPlacement(name="flowerpot", initial_floor=2),
            ItemPlacement(name="chair", initial_floor=1),
            ItemPlacement(name="table", initial_floor=2),
        ],
    )


def _fig1_full_config() -> ProblemConfig:
    """Full Fig. 1 configuration: m=n=3, all 5 items."""
    return ProblemConfig(
        num_floors=3,
        num_persons=3,
        person_names=["Joe", "Bill", "Mia"],
        items=[
            ItemPlacement(name="flowerpot", initial_floor=2),
            ItemPlacement(name="chair", initial_floor=1),
            ItemPlacement(name="table", initial_floor=2),
            ItemPlacement(name="piano", initial_floor=1),
            ItemPlacement(name="sofa", initial_floor=2),
        ],
    )


def test_task2_all_items_to_ground_in_4_steps():
    """Task 2: flowerpot, chair, table reach floor 0 in exactly 4 steps."""
    config = _task2_config()
    result = solve_optimal(config, task=2)

    assert result.satisfiable is True
    assert result.num_time_steps == 4


def test_task2_unsatisfiable_in_3_steps():
    """Cannot move 3 items (2 from floor 2) to ground floor in 3 steps."""
    config = _task2_config()
    result = solve_fixed(config, task=2, T=3)

    assert result.satisfiable is False


def test_task2_final_state_correct():
    """All items and persons at floor 0 in the final step."""
    config = _task2_config()
    result = solve_optimal(config, task=2)

    assert result.plan is not None
    final = result.plan[-1]
    for name in ["Joe", "Bill", "Mia"]:
        assert final.person_positions[name] == 0
    for item in ["flowerpot", "chair", "table"]:
        assert final.item_positions[item] == 0


def test_task2_full_fig1_optimal():
    """Full Fig. 1 with all 5 items: optimal is 6 steps."""
    config = _fig1_full_config()
    result = solve_optimal(config, task=2)

    assert result.satisfiable is True
    assert result.num_time_steps == 6


def test_task2_dimacs_output_present():
    """Solver result includes DIMACS CNF and variable mapping."""
    config = _task2_config()
    result = solve_optimal(config, task=2)

    assert result.cnf_dimacs is not None
    assert "p cnf" in result.cnf_dimacs
    assert result.variable_mapping is not None
    assert len(result.variable_mapping) > 0


def test_task2_simple_one_item():
    """Single item on floor 1 with 1 person: optimal is 2 steps (ascend, carry down)."""
    config = ProblemConfig(
        num_floors=2,
        num_persons=1,
        items=[ItemPlacement(name="box", initial_floor=1)],
    )
    result = solve_optimal(config, task=2)

    assert result.satisfiable is True
    assert result.num_time_steps == 2
