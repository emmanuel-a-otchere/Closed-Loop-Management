"""FastAPI app entry for CLAM."""

from __future__ import annotations

import os
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .audit_context import _correlation_id_var  # noqa: F401 - re-exported for middleware
from .auth import TokenStore, _AuthChallenge, auth_enabled, resolve_principal
from .errors import (
    ErrorCode,
    error_envelope,
    error_response,
)
from .models import ErrorEnvelope
from .routers import (
    activity,
    auth,
    closed_loop,
    closed_loop_link,
    decision_model,
    goal,
    health,
    request_log,
    workflow,
)
from .store import Store


def create_app(db_path: Path | None = None) -> FastAPI:
    """Application factory.

    Splitting the factory out of the module level makes it trivial to
    spin up an isolated app per test session (each test gets its own
    SQLite file).
    """

    resolved_db = Path(db_path or os.environ.get("CLAM_DB_PATH", "clam.db"))
    store = Store(resolved_db)
    token_store = TokenStore()

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
            {
                "name": "auth",
                "description": (
                    "Token issuance, listing, revocation; whoami."
                ),
            },
            {"name": "closedLoop", "description": "Closed-loop CRUD + state."},
            {"name": "decisionModel", "description": "Decision-model CRUD."},
            {"name": "activity", "description": "Atomic step CRUD + lifecycle."},
            {"name": "workflow", "description": "Feedback / feedforward workflow CRUD + lifecycle."},
            {"name": "goal", "description": "Measurable goal CRUD."},
            {"name": "closedLoopLink", "description": "Daisy-chain / hierarchical interlinks between loops."},
        ],
        lifespan=lifespan,
    )

    app.state.store = store
    app.state.token_store = token_store

    @app.exception_handler(_AuthChallenge)
    async def _auth_challenge_handler(request: Request, exc: _AuthChallenge) -> JSONResponse:
        # Surface the JSONResponse the dependency built as the
        # final response (carrying the structured envelope).
        return exc.response

    @app.middleware("http")
    async def _resolve_principal_middleware(
        request: Request, call_next: object
    ) -> object:
        """Attach the principal for the request before the route runs.

        Also enforces scope requirements for write methods when auth
        is enabled.
        """
        principal = resolve_principal(request)
        request.state.principal = principal

        if auth_enabled():
            from .auth import Scope, require_scope  # local cycle avoidance

            method = request.method.upper()
            path = request.url.path
            # Bootstrap path: a fresh install must be able to issue the
            # first admin token without auth. Skip enforcement only on
            # POST /api/v1/auth/tokens when the store is empty.
            bootstrap_issue = (
                method == "POST"
                and path == "/api/v1/auth/tokens"
                and not token_store.list_tokens()
            )
            if (
                method in {"POST", "PUT", "PATCH", "DELETE"}
                and not bootstrap_issue
            ):
                # Auth revocation requires ADMIN; everything else WRITE.
                required = Scope.WRITE
                if path.startswith("/api/v1/auth"):
                    required = Scope.ADMIN
                denial = require_scope(principal, required)
                if denial is not None:
                    return denial

        return await call_next(request)  # type: ignore[operator]

    @app.middleware("http")
    async def _request_log_middleware(
        request: Request, call_next: object
    ) -> object:
        """Structured request log middleware (PR1).

        Captures method / path / status / latency_ms / request_id /
        principal_id / source_ip / user_agent for every request
        and writes the row to the request_log table after the
        response is produced. Log writes are best-effort: a write
        failure does not surface to the caller.
        """
        started = time.perf_counter()
        # Correlation id: header X-Correlation-Id if present, else UUID4.
        request_id = (
            request.headers.get("x-correlation-id") or str(uuid.uuid4())
        )
        # Slice 4 PR2: stash on a contextvar so audit hooks downstream
        # can read it without threading it through every call.
        _correlation_id_var.set(request_id)
        request.state.correlation_id = request_id
        # Echo the id back to the caller for client-side correlation.
        try:
            response = await call_next(request)  # type: ignore[operator]
        except Exception:  # pragma: no cover - defensive
            response = JSONResponse(
                status_code=500,
                content=error_envelope(
                    code=ErrorCode.INTERNAL_ERROR,
                    message="Unhandled error.",
                ).model_dump(),
            )
        latency_ms = (time.perf_counter() - started) * 1000.0
        # Best-effort write.
        try:
            principal = getattr(request.state, "principal", None)
            principal_id = (
                principal.token_id if principal and getattr(principal, "token_id", None) else None
            )
            source_ip = (
                request.client.host if request.client else None
            )
            user_agent = request.headers.get("user-agent")
            await store.record_request_log(
                method=request.method,
                path=request.url.path,
                status=response.status_code,
                latency_ms=latency_ms,
                request_id=request_id,
                principal_id=principal_id,
                source_ip=source_ip,
                user_agent=user_agent,
            )
        except Exception:  # pragma: no cover - log failures are silent
            pass
        response.headers["x-correlation-id"] = request_id
        return response

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
    app.include_router(auth.router)
    app.include_router(closed_loop.router)
    app.include_router(decision_model.router)
    app.include_router(activity.router)
    app.include_router(workflow.router)
    app.include_router(goal.router)
    app.include_router(closed_loop_link.router)
    app.include_router(request_log.router)

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