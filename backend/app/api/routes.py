"""FastAPI REST endpoints for the Movers SAT Solver.

All routes are mounted under the ``/api`` prefix by :mod:`app.main`.
Each solve runs in an isolated child process with a hard timeout, and
recent results are kept in a bounded in-memory cache so that the CNF and
variable mapping can be downloaded later by ``solve_id``.
"""

import multiprocessing
import queue
import threading
import time
import uuid
from collections import OrderedDict

from fastapi import APIRouter, HTTPException

from app import __version__
from app.config import settings
from app.models.api import FixedSolveRequest, SolveRequest, SolveResponse
from app.models.problem import SolverResult
from app.solver import worker

router = APIRouter()

# "spawn" starts a fresh interpreter for each solve. Forking a multi-threaded
# server process (FastAPI's thread pool) can deadlock, so fork is avoided.
_mp = multiprocessing.get_context("spawn")


class _ResultCache:
    """Thread-safe LRU cache of solve results, keyed by ``solve_id``."""

    def __init__(self, max_size: int) -> None:
        self._max_size = max(1, max_size)
        self._data: OrderedDict[str, SolverResult] = OrderedDict()
        self._lock = threading.Lock()

    def put(self, key: str, value: SolverResult) -> None:
        with self._lock:
            self._data[key] = value
            self._data.move_to_end(key)
            while len(self._data) > self._max_size:
                self._data.popitem(last=False)

    def get(self, key: str) -> SolverResult | None:
        with self._lock:
            value = self._data.get(key)
            if value is not None:
                self._data.move_to_end(key)
            return value

    def __len__(self) -> int:
        with self._lock:
            return len(self._data)


_result_cache = _ResultCache(settings.result_cache_size)


def _run_solver_process(kind: str, args: tuple) -> SolveResponse:
    """Run the solver in a child process, enforce the timeout, cache the result."""
    result_queue = _mp.Queue()
    process = _mp.Process(target=worker.run, args=(kind, args, result_queue), daemon=True)
    process.start()

    deadline = time.monotonic() + settings.solver_timeout_seconds
    try:
        while True:
            try:
                status, payload = result_queue.get(timeout=0.2)
                break
            except queue.Empty:
                if not process.is_alive():
                    # The child may have exited right after putting its result.
                    try:
                        status, payload = result_queue.get(timeout=0.5)
                        break
                    except queue.Empty:
                        raise HTTPException(
                            status_code=500, detail="Solver process exited unexpectedly."
                        ) from None
                if time.monotonic() > deadline:
                    raise HTTPException(
                        status_code=504,
                        detail=(
                            f"Solver timeout of {settings.solver_timeout_seconds:.0f} s "
                            "exceeded. Process terminated."
                        ),
                    )
    finally:
        if process.is_alive():
            process.terminate()
        process.join(timeout=5)
        if process.is_alive():
            process.kill()
            process.join()
        result_queue.close()

    if status == "error":
        raise HTTPException(status_code=500, detail=f"Solver error: {payload}")

    solve_id = str(uuid.uuid4())
    _result_cache.put(solve_id, payload)
    return SolveResponse(solve_id=solve_id, result=payload)


# These handlers are deliberately plain ``def`` (not ``async def``): they block
# while waiting for the solver process, and FastAPI runs sync handlers in a
# thread pool, so other requests (e.g. /health) stay responsive.
@router.post("/solve", response_model=SolveResponse)
def solve(req: SolveRequest):
    """Find the optimal (minimum-T) solution via iterative deepening."""
    return _run_solver_process(
        "optimal", (req.to_config(), req.task, req.max_steps, req.goal_floors)
    )


@router.post("/solve/fixed", response_model=SolveResponse)
def solve_at_fixed_t(req: FixedSolveRequest):
    """Solve at an exact time horizon T (SAT gives a plan, UNSAT proves infeasibility)."""
    return _run_solver_process(
        "fixed", (req.to_config(), req.task, req.time_steps, req.goal_floors)
    )


def _cached(solve_id: str) -> SolverResult:
    result = _result_cache.get(solve_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Solve ID not found (unknown or expired)")
    return result


@router.get("/cnf/{solve_id}")
def get_cnf(solve_id: str):
    """Retrieve the DIMACS CNF of a previous solve (SAT or UNSAT).

    Raises:
        HTTPException: 404 if ``solve_id`` is unknown or has been evicted.
    """
    result = _cached(solve_id)
    if not result.cnf_dimacs:
        raise HTTPException(status_code=404, detail="No CNF available for this solve")
    return {"cnf": result.cnf_dimacs}


@router.get("/mapping/{solve_id}")
def get_mapping(solve_id: str):
    """Retrieve the variable ID -> symbolic name mapping of a previous solve.

    Raises:
        HTTPException: 404 if ``solve_id`` is unknown or has been evicted.
    """
    result = _cached(solve_id)
    if not result.variable_mapping:
        raise HTTPException(status_code=404, detail="No mapping available for this solve")
    return {"mapping": result.variable_mapping}


@router.get("/health")
def health():
    """Return a simple health-check response."""
    return {
        "status": "ok",
        "solver": settings.solver_canonical_name,
        "version": __version__,
    }
