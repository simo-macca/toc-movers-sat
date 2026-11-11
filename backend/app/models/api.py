"""Request and response schemas for the REST API.

Requests extend :class:`~app.models.problem.ProblemConfig`, so all of
its validation (floor ranges, unique names, ...) applies to API input
as well.  Invalid requests are rejected by FastAPI with ``422``.
"""

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.models.problem import ProblemConfig, SolverResult

MAX_HORIZON = 100
"""Hard upper bound accepted for ``max_steps`` / ``time_steps``."""


class SolveRequest(ProblemConfig):
    """Request body for finding an optimal solution.

    Attributes:
        task: Task variant (1 = movement only, 2 = movement + items).
        goal_floors: Target floor per person index (Task 1 only).
            Defaults to floor 0 for all persons when None.
        max_steps: Upper bound on T for iterative deepening.
    """

    task: Literal[1, 2]
    goal_floors: dict[int, int] | None = None
    max_steps: int | None = Field(default=None, ge=0, le=MAX_HORIZON)

    @model_validator(mode="after")
    def _check_goal_floors(self) -> "SolveRequest":
        """Ensure every goal refers to an existing person and floor."""
        if self.task == 1 and self.goal_floors:
            for p, f in self.goal_floors.items():
                if not 0 <= p < self.num_persons:
                    raise ValueError(
                        f"goal_floors refers to person {p}, but persons are "
                        f"indexed 0 to {self.num_persons - 1}"
                    )
                if not 0 <= f < self.num_floors:
                    raise ValueError(
                        f"goal floor {f} for person {p} is out of range "
                        f"(0 to {self.num_floors - 1})"
                    )
        return self

    def to_config(self) -> ProblemConfig:
        """Return the plain problem specification of this request."""
        return ProblemConfig(
            num_floors=self.num_floors,
            num_persons=self.num_persons,
            person_names=self.person_names,
            items=self.items if self.task == 2 else [],
        )


class FixedSolveRequest(SolveRequest):
    """Request body for solving at a specific time horizon.

    Attributes:
        time_steps: Exact time horizon T to solve for.
    """

    time_steps: int = Field(ge=0, le=MAX_HORIZON)


class SolveResponse(BaseModel):
    """Response returned by both solve endpoints.

    Attributes:
        solve_id: UUID for retrieving CNF or variable mapping later.
        result: Full solver output including the decoded plan.
    """

    solve_id: str
    result: SolverResult
