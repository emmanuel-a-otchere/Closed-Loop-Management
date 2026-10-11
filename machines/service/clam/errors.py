"""Error envelope helpers."""

from __future__ import annotations

from enum import StrEnum

from fastapi.responses import JSONResponse

from .models import ErrorEnvelope


class ErrorCode(StrEnum):
    """Stable, machine-readable identifiers for API errors.

    Codes are namespaced: ``<resource>.<condition>``.
    """

    VALIDATION_ERROR = "request.validation_error"
    UNAUTHORIZED = "auth.unauthorized"
    FORBIDDEN = "auth.forbidden"
    NOT_FOUND = "resource.not_found"
    STATE_TRANSITION_INVALID = "closed_loop.state_transition_invalid"
    LIFECYCLE_CONSTRAINT = "lifecycle.constraint_violated"
    CYCLE_DETECTED = "topology.cycle_detected"
    TOPOLOGY_RULE = "topology.rule_violated"
    INTERNAL_ERROR = "server.internal_error"
    DUPLICATE = "resource.duplicate"


def error_envelope(
    *, code: ErrorCode, message: str, details: dict[str, object] | None = None
) -> ErrorEnvelope:
    return ErrorEnvelope(code=code.value, message=message, details=details)


def error_response(
    *, status_code: int, code: ErrorCode, message: str, details: dict[str, object] | None = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=error_envelope(code=code, message=message, details=details).model_dump(),
    )


__all__ = ["ErrorCode", "error_envelope", "error_response"]