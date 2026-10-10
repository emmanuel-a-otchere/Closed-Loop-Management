"""FastAPI app entry for CLAM."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .errors import (
    ErrorCode,
    error_envelope,
    error_response,
)
from .models import ErrorEnvelope
from .routers import closed_loop, decision_model, health
from .store import Store


def create_app(db_path: Path | None = None) -> FastAPI:
    """Application factory.

    Splitting the factory out of the module level makes it trivial to
    spin up an isolated app per test session (each test gets its own
    SQLite file).
    """

    resolved_db = Path(db_path or os.environ.get("CLAM_DB_PATH", "clam.db"))
    store = Store(resolved_db)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        await store.init()
        try:
            yield
        finally:
            # aiosqlite connections are short-lived; nothing to close.
            pass

    app = FastAPI(
        title="Closed Loop Automation Management (CLAM)",
        summary=(
            "REST API + OAS 3.1 data model for managing closed loops through "
            "automation. CRUD decision models, goals, workflows, activities; "
            "activate / deactivate loops; daisy-chain or hierarchically "
            "interlink loops."
        ),
        version="0.1.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        contact={
            "name": "Emmanuel A. Otchere",
            "url": "https://github.com/emmanuel-a-otchere/Closed-Loop-Management",
        },
        license_info={
            "name": "Apache-2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0",
        },
        openapi_tags=[
            {"name": "health", "description": "Liveness and metadata."},
            {"name": "closedLoop", "description": "Closed-loop CRUD + state."},
            {"name": "decisionModel", "description": "Decision-model CRUD."},
        ],
        lifespan=lifespan,
    )

    app.state.store = store

    @app.exception_handler(RequestValidationError)
    async def _validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return error_response(
            status_code=422,
            code=ErrorCode.VALIDATION_ERROR,
            message="Request payload failed validation.",
            details={"errors": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def _unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        # Let HTTPException pass through unchanged.
        from fastapi import HTTPException

        if isinstance(exc, HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content=error_envelope(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=str(exc.detail),
                ).model_dump(),
            )
        return error_response(
            status_code=500,
            code=ErrorCode.INTERNAL_ERROR,
            message="Unhandled error.",
            details={"type": type(exc).__name__},
        )

    app.include_router(health.router)
    app.include_router(closed_loop.router)
    app.include_router(decision_model.router)

    @app.get(
        "/",
        summary="API root",
        tags=["health"],
        response_model=dict,
    )
    async def root() -> dict[str, str]:
        return {
            "name": "CLAM",
            "version": "0.1.0",
            "docs": "/docs",
            "openapi": "/openapi.json",
        }

    # Inject ErrorEnvelope into the OpenAPI components so the CLAM profile
    # validator + downstream SDK generators see it explicitly.
    original_openapi = app.openapi

    def _openapi_with_envelope() -> dict[str, object]:
        spec = original_openapi()
        schemas = spec.setdefault("components", {}).setdefault("schemas", {})
        schemas["ErrorEnvelope"] = ErrorEnvelope.model_json_schema(ref_template="#/components/schemas/{model}")
        return spec

    app.openapi = _openapi_with_envelope  # type: ignore[method-assign]

    return app


app = create_app()


__all__ = ["app", "create_app", "ErrorEnvelope"]