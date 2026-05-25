"""FastAPI REST endpoints for the Movers SAT Solver.

All routes are mounted under the ``/api`` prefix by
:mod:`app.main`.  Solve results are cached in memory so that
CNF and variable-mapping data can be retrieved by ``solve_id``
after the initial solve request.
"""

import uuid
import multiprocessing

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.problem import ProblemConfig, SolverResult, ItemPlacement

router = APIRouter()

# In-memory cache keyed by solve_id (UUID). Does not persist across restarts.
_result_cache: dict[str, SolverResult] = {}

# Hard timeout in seconds to prevent the PySAT C-extension from causing cascading deadlocks.
# This should be set slightly lower than your frontend's HTTP timeout limit.
SOLVER_TIMEOUT_SECONDS = 118.0


class SolveRequest(BaseModel):
    """Request body for finding an optimal solution.

    Attributes:
        task: Task variant (1 = movement only, 2 = movement + items).
        num_floors: Number of floors in the building.
        num_persons: Number of movers.
        person_names: Optional custom names for the movers.
        items: Items to transport (Task 2 only).
        goal_floors: Target floor per person index (Task 1 only).
            Defaults to floor 0 for all persons when None.
        max_steps: Upper bound on T for iterative deepening.
    """

    task: int
    num_floors: int
    num_persons: int
    person_names: list[str] | None = None
    items: list[ItemPlacement] = []
    goal_floors: dict[int, int] | None = None
    max_steps: int | None = None


class FixedSolveRequest(SolveRequest):
    """Request body for solving at a specific time horizon.

    Attributes:
        time_steps: Exact time horizon T to solve for.
    """

    time_steps: int


class SolveResponse(BaseModel):
    """Response returned by both solve endpoints.

    Attributes:
        solve_id: UUID for retrieving CNF or variable mapping later.
        result: Full solver output including the decoded plan.
    """

    solve_id: str
    result: SolverResult


def _optimal_worker(config: ProblemConfig, task: int, max_steps: int | None, goal_floors: dict[int, int] | None, return_dict: dict):
    """Isolated worker function to run iterative deepening optimal solver."""
    from app.solver.runner import solve_optimal
    try:
        result = solve_optimal(config, task, max_steps, goal_floors)
        return_dict['result'] = result
    except Exception as e:
        return_dict['error'] = str(e)


def _fixed_worker(config: ProblemConfig, task: int, time_steps: int, goal_floors: dict[int, int] | None, return_dict: dict):
    """Isolated worker function to run the fixed time horizon solver."""
    from app.solver.runner import solve_fixed
    try:
        result = solve_fixed(config, task, time_steps, goal_floors)
        return_dict['result'] = result
    except Exception as e:
        return_dict['error'] = str(e)


def _run_solver_process(target_worker, worker_args: tuple) -> SolveResponse:
    """
    Auxiliary function to handle the multiprocessing setup, execution,
    timeout enforcement, and response generation for the solver.
    """
    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    # Append the return_dict to the arguments passed to the worker
    full_args = (*worker_args, return_dict)

    p = multiprocessing.Process(target=target_worker, args=full_args)
    p.start()
    p.join(timeout=SOLVER_TIMEOUT_SECONDS)

    if p.is_alive():
        # The solver took too long. Explicitly terminate the zombie process.
        p.terminate()
        p.join()
        raise HTTPException(status_code=504, detail="Solver timeout exceeded. Process terminated.")

    if 'error' in return_dict:
        raise HTTPException(status_code=500, detail=f"Solver error: {return_dict['error']}")

    if 'result' not in return_dict:
        raise HTTPException(status_code=500, detail="Solver process failed unexpectedly.")

    result = return_dict['result']
    solve_id = str(uuid.uuid4())
    _result_cache[solve_id] = result

    return SolveResponse(solve_id=solve_id, result=result)


@router.post("/solve", response_model=SolveResponse)
async def solve(req: SolveRequest):
    """Find the optimal (minimum-T) solution via iterative deepening."""
    config = ProblemConfig(
        num_floors=req.num_floors,
        num_persons=req.num_persons,
        person_names=req.person_names,
        items=req.items,
    )
    return _run_solver_process(
        target_worker=_optimal_worker,
        worker_args=(config, req.task, req.max_steps, req.goal_floors)
    )


@router.post("/solve/fixed", response_model=SolveResponse)
async def solve_at_fixed_t(req: FixedSolveRequest):
    """Solve at an exact time horizon T."""
    config = ProblemConfig(
        num_floors=req.num_floors,
        num_persons=req.num_persons,
        person_names=req.person_names,
        items=req.items,
    )
    return _run_solver_process(
        target_worker=_fixed_worker,
        worker_args=(config, req.task, req.time_steps, req.goal_floors)
    )


@router.get("/cnf/{solve_id}")
def get_cnf(solve_id: str):
    """Retrieve the DIMACS CNF string for a previous solve.

    Raises:
        HTTPException: 404 if solve_id is unknown or the result was UNSAT.
    """
    result = _result_cache.get(solve_id)
    if not result:
        raise HTTPException(status_code=404, detail="Solve ID not found")
    if not result.cnf_dimacs:
        raise HTTPException(status_code=404, detail="No CNF available (UNSAT)")
    return {"cnf": result.cnf_dimacs}


@router.get("/mapping/{solve_id}")
def get_mapping(solve_id: str):
    """Retrieve the variable ID to symbolic name mapping for a previous solve.

    Raises:
        HTTPException: 404 if solve_id is unknown or the result was UNSAT.
    """
    result = _result_cache.get(solve_id)
    if not result:
        raise HTTPException(status_code=404, detail="Solve ID not found")
    if not result.variable_mapping:
        raise HTTPException(status_code=404, detail="No mapping available (UNSAT)")
    return {"mapping": result.variable_mapping}


@router.get("/health")
def health():
    """Return a simple health-check response."""
    return {"status": "ok", "solver": "glucose3"}
