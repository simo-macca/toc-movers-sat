"""FastAPI application entry point.

Creates the ASGI application, attaches CORS middleware (configured via
:pydata:`app.config.settings`), and mounts all API routes under the
``/api`` prefix.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import router

app = FastAPI(title="Movers SAT Solver", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
