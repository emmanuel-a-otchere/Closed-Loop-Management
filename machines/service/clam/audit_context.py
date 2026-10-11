"""Slice 4 PR2: per-request audit correlation context.

Holds a ContextVar carrying the current request's correlation id
(set by the request-log middleware in PR1). Audit hooks read this
to stamp ``audit_log.correlation_id`` without threading the value
through every store method.
"""

from __future__ import annotations

from contextvars import ContextVar

_correlation_id_var: ContextVar[str | None] = ContextVar(
    "clam_correlation_id", default=None
)


def get_correlation_id() -> str | None:
    """Return the current request's correlation id, or None."""
    return _correlation_id_var.get()


__all__ = ["get_correlation_id"]