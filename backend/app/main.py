"""FastAPI application entry point.

Creates the ASGI application, attaches CORS middleware (configured via
:pydata:`app.config.settings`), and mounts all API routes under the
``/api`` prefix.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import settings
from app.api.routes import router

app = FastAPI(
    title="OptiMove: Movers SAT Solver",
    description="Optimal planning for the Movers problem via SAT encoding (PySAT).",
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
