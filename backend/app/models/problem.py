"""Domain models for the movers SAT problem.

Defines Pydantic models for problem specification (inputs), solver
output (results), and the human-readable solution plan representation.
"""

from pydantic import BaseModel, Field, model_validator


class ItemPlacement(BaseModel):
    """An item and its starting floor.

    Attributes:
        name: Unique identifier for the item (e.g. "chair", "table").
        initial_floor: Zero-indexed floor where the item starts.
    """

    name: str = Field(min_length=1, max_length=50)
    initial_floor: int = Field(ge=0)


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

    num_floors: int = Field(ge=1, le=50)
    num_persons: int = Field(ge=1, le=20)
    person_names: list[str] | None = None
    items: list[ItemPlacement] = Field(default_factory=list, max_length=50)

    @model_validator(mode="after")
    def _check_consistency(self) -> "ProblemConfig":
        """Reject instances that would otherwise silently encode nonsense.

        Out-of-range floors create unconstrained variables and duplicate
        item names collapse onto the same variables, so both are refused
        here instead of producing a misleading SAT/UNSAT answer.
        """
        if self.person_names is not None:
            if len(self.person_names) != self.num_persons:
                raise ValueError(
                    f"person_names has {len(self.person_names)} entries "
                    f"but num_persons is {self.num_persons}"
                )
            if any(not n.strip() for n in self.person_names):
                raise ValueError("person_names must not contain empty names")
            if len(set(self.person_names)) != len(self.person_names):
                raise ValueError("person_names must be unique")

        names = [it.name for it in self.items]
        if len(set(names)) != len(names):
            raise ValueError("item names must be unique")

        for it in self.items:
            if it.initial_floor >= self.num_floors:
                raise ValueError(
                    f"item '{it.name}' starts on floor {it.initial_floor}, "
                    f"but floors range from 0 to {self.num_floors - 1}"
                )
        return self


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
        num_variables: Number of propositional variables in the (last) CNF formula.
        num_clauses: Number of clauses in the (last) CNF formula.
        solve_time_ms: Wall-clock solver runtime in milliseconds. For
            iterative deepening this is the total over all horizons tried.
        horizons_tried: How many time horizons T were encoded and solved.
    """

    num_variables: int
    num_clauses: int
    solve_time_ms: float
    horizons_tried: int = 1


class SolverResult(BaseModel):
    """Complete output from the SAT solver.

    ``plan`` is only populated when the formula is satisfiable. The CNF and
    the variable mapping are produced for both SAT and UNSAT results (an
    UNSAT formula is the infeasibility proof you may want to re-check in
    another solver). Both are excluded from JSON serialization to keep API
    responses small; fetch them via ``/api/cnf/{id}`` and ``/api/mapping/{id}``.

    Attributes:
        satisfiable: Whether the SAT solver found a valid assignment.
        num_time_steps: Time horizon T of the solution, or the last
            horizon tested when unsatisfiable.
        plan: Decoded human-readable solution as a list of TimeSteps.
        cnf_dimacs: The CNF formula in DIMACS format string.
        variable_mapping: Mapping from SAT variable ID to symbolic name.
        stats: Solver performance metrics.
    """

    satisfiable: bool
    num_time_steps: int | None = None
    plan: list[TimeStep] | None = None
    cnf_dimacs: str | None = Field(default=None, exclude=True)
    variable_mapping: dict[int, str] | None = Field(default=None, exclude=True)
    stats: SolverStats | None = None
