"""Entry point executed inside the isolated solver child process.

Kept in its own small module so that the ``spawn`` start method only has
to import the solver stack, not FastAPI.
"""

from multiprocessing.queues import Queue


def run(kind: str, args: tuple, queue: Queue) -> None:
    """Run ``solve_optimal`` or ``solve_fixed`` and put the outcome on ``queue``.

    Puts ``("ok", SolverResult)`` on success or ``("error", message)`` on failure.
    """
    try:
        from app.solver.runner import solve_fixed, solve_optimal

        fn = solve_optimal if kind == "optimal" else solve_fixed
        queue.put(("ok", fn(*args)))
    except Exception as exc:  # noqa: BLE001 - report every failure to the parent
        queue.put(("error", f"{type(exc).__name__}: {exc}"))
