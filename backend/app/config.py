"""Application configuration loaded from environment variables.

Uses pydantic-settings so every field can be overridden via an
environment variable of the same name (case-insensitive).
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime settings for the Movers SAT Solver.

    Attributes:
        solver_name: PySAT solver backend identifier.
            Default "g3" selects Glucose3.
        max_time_steps: Upper bound on the time horizon T when
            searching for an optimal solution via iterative deepening.
        cors_origins: Allowed origins for CORS. Defaults to the
            Vue dev server at localhost:5173.
    """

    solver_name: str = "g3"
    max_time_steps: int = 20
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
