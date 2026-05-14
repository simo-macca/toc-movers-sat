"""Domain models for the movers SAT problem.

Defines Pydantic models for problem specification (inputs), solver
output (results), and the human-readable solution plan representation.
"""

from pydantic import BaseModel


class ItemPlacement(BaseModel):
    """An item and its starting floor.

    Attributes:
        name: Unique identifier for the item (e.g. "chair", "table").
        initial_floor: Zero-indexed floor where the item starts.
    """

    name: str
    initial_floor: int


class ProblemConfig(BaseModel):
    """Full specification of a movers problem instance.

    Attributes:
        num_floors: Total number of floors (indexed 0 to num_floors - 1).
        num_persons: Number of movers available.
        person_names: Optional custom names for movers. When None, defaults
            to "person_0", "person_1", etc.
        items: Items to transport. An empty list implies Task 1 (movement
            only, no items).
    """

    num_floors: int
    num_persons: int
    person_names: list[str] | None = None
    items: list[ItemPlacement] = []


class StepAction(BaseModel):
    """A single person's action during one time step.

    Attributes:
        person: Name of the mover performing the action.
        action: One of "idle", "ascends", "descends", or "carries".
        from_floor: Floor the person occupies at the start of this step.
        to_floor: Floor the person occupies at the end of this step.
        item: Item being carried. Only populated when action is "carries".
    """

    person: str
    action: str
    from_floor: int
    to_floor: int
    item: str | None = None


class TimeStep(BaseModel):
    """Snapshot of the world state at time t, plus the transition actions.

    Positions represent the state *at* time t. Actions describe what
    happens during the transition from t to t + 1 (empty at the final
    time step).

    Attributes:
        t: Time index (0-based).
        actions: All person actions during this time step.
        person_positions: Mapping of person name to current floor.
        item_positions: Mapping of item name to current floor (Task 2 only).
    """

    t: int
    actions: list[StepAction]
    person_positions: dict[str, int]
    item_positions: dict[str, int]


class SolverStats(BaseModel):
    """Performance metrics from a single solver run.

    Attributes:
        num_variables: Number of propositional variables in the CNF formula.
        num_clauses: Number of clauses in the CNF formula.
        solve_time_ms: Wall-clock solver runtime in milliseconds.
    """

    num_variables: int
    num_clauses: int
    solve_time_ms: float


class SolverResult(BaseModel):
    """Complete output from the SAT solver.

    When the problem is unsatisfiable, only ``satisfiable`` is populated;
    all other fields remain None.

    Attributes:
        satisfiable: Whether the SAT solver found a valid assignment.
        num_time_steps: Time horizon T of the solution, if satisfiable.
        plan: Decoded human-readable solution as a list of TimeSteps.
        cnf_dimacs: The CNF formula in DIMACS format string.
        variable_mapping: Mapping from SAT variable ID to symbolic name.
        stats: Solver performance metrics.
    """

    satisfiable: bool
    num_time_steps: int | None = None
    plan: list[TimeStep] | None = None
    cnf_dimacs: str | None = None
    variable_mapping: dict[int, str] | None = None
    stats: SolverStats | None = None
