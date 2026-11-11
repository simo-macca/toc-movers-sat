"""Application configuration loaded from environment variables.

Uses pydantic-settings so every field can be overridden via an
environment variable of the same name (case-insensitive), e.g.
``SOLVER_NAME=cd19`` or ``SOLVER_TIMEOUT_SECONDS=60``.
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings
from pysat.solvers import SolverNames


def _solver_aliases() -> dict[str, str]:
    """Map every PySAT solver alias (e.g. ``"g3"``) to its canonical name (``"glucose3"``)."""
    aliases: dict[str, str] = {}
    for canonical, names in vars(SolverNames).items():
        if canonical.startswith("_") or not isinstance(names, tuple):
            continue
        for alias in names:
            aliases[alias] = canonical
    return aliases


SOLVER_ALIASES = _solver_aliases()


class Settings(BaseSettings):
    """Runtime settings for the Movers SAT Solver.

    Attributes:
        solver_name: PySAT solver identifier. Default ``"g3"`` (Glucose 3).
            Any PySAT alias is accepted, e.g. ``"g4"``, ``"cd19"``, ``"m22"``.
        max_time_steps: Default upper bound on the time horizon T when
            searching for an optimal solution via iterative deepening.
        solver_timeout_seconds: Wall-clock limit for one API solve. Keep it
            slightly below the frontend HTTP timeout (120 s).
        result_cache_size: Number of recent solve results kept in memory so
            CNF / mapping can be downloaded later (least recently used are dropped).
        cors_origins: Allowed origins for CORS (Vite dev server and Docker frontend).
    """

    solver_name: str = "g3"
    max_time_steps: int = 20
    solver_timeout_seconds: float = 118.0
    result_cache_size: int = 128
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    @field_validator("solver_name")
    @classmethod
    def _known_solver(cls, value: str) -> str:
        if value not in SOLVER_ALIASES:
            raise ValueError(
                f"unknown PySAT solver '{value}'. Valid names include: "
                + ", ".join(sorted(SOLVER_ALIASES))
            )
        return value

    @property
    def solver_canonical_name(self) -> str:
        """Canonical PySAT name of the configured solver (e.g. ``"glucose3"``)."""
        return SOLVER_ALIASES[self.solver_name]


settings = Settings()
