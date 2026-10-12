"""Audit log router (PR3).

Lists and retrieves audit rows. Requires READ scope.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Query, Request

from ..auth import Scope, resolve_principal
from ..errors import ErrorCode, error_response
from ..models import AuditAction, AuditActor, AuditEntry, AuditPage

router = APIRouter(prefix="/api/v1/audit", tags=["observability"])


@router.get(
    "",
    response_model=AuditPage,
    summary="List audit rows (filterable, cursor-paginated, ts DESC)",
)
async def list_audit(
    request: Request,
    entityKind: str | None = Query(
        None, description="Filter by entity kind (ClosedLoop, Activity, ...)"
    ),
    entityId: UUID | None = Query(
        None, description="Filter by entity id (UUID)"
    ),
    actor: AuditActor | None = Query(
        None, description="Filter by actor (USER / SYSTEM)"
    ),
    action: AuditAction | None = Query(
        None, description="Filter by action (closed_loop.state_transition, ...)"
    ),
    since: datetime | None = Query(
        None, description="Rows with ts >= since (RFC3339)"
    ),
    until: datetime | None = Query(
        None, description="Rows with ts <= until (RFC3339)"
    ),
    limit: int = Query(
        100, ge=1, le=1000, description="Page size (1..1000, default 100)"
    ),
    cursor: str | None = Query(
        None, description="Opaque cursor (the previous page's nextCursor)"
    ),
) -> AuditPage:
    """Return audit rows matching the filters, newest first."""
    store = request.app.state.store
    before_id: UUID | None = None
    if cursor:
        try:
            before_id = UUID(cursor)
        except ValueError:
            return error_response(
                status_code=422,
                code=ErrorCode.VALIDATION_ERROR,
                message="Invalid cursor; expected a UUID.",
            )  # type: ignore[return-value]
    items, next_cursor = await store.list_audit(
        entity_kind=entityKind,
        entity_id=entityId,
        actor=actor,
        action=action,
        since=since,
        until=until,
        limit=limit,
        before_id=before_id,
    )
    return AuditPage(
        items=items,
        limit=limit,
        nextCursor=str(next_cursor) if next_cursor else None,
    )


@router.get(
    "/{auditId}",
    response_model=AuditEntry,
    summary="Fetch a single audit row by id",
)
async def get_audit(
    request: Request,
    auditId: UUID,
) -> AuditEntry:
    """Return a single audit row, or 404."""
    store = request.app.state.store
    try:
        return await store.get_audit(auditId)
    except Exception as exc:
        # The store raises NotFoundError on missing rows; map to 404.
        from ..store import NotFoundError

        if isinstance(exc, NotFoundError):
            return error_response(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message=str(exc),
            )  # type: ignore[return-value]
        raise


@router.post(
    "/prune",
    summary="Prune audit rows older than a timestamp (ADMIN only)",
)
async def prune_audit(
    request: Request,
    before: datetime = Query(
        ..., description="ISO-8601 timestamp; rows with ts < this are deleted."
    ),
):
    """Delete audit rows with ``ts < before``. ADMIN scope required.

    The audit log is the durable record of state changes; pruning
    is destructive. External archive before issuing in production.
    """
    from ..auth import require_scope

    principal = resolve_principal(request)
    denial = require_scope(principal, Scope.ADMIN)
    if denial is not None:
        return denial
    store = request.app.state.store
    deleted = await store.prune_audit_before(before_ts=before)
    remaining = await store.count_audit()
    return {"deleted": deleted, "remaining": remaining, "before": before.isoformat()}


@router.post(
    "/pruneByDays",
    summary="Prune audit rows older than N days (ADMIN only)",
)
async def prune_audit_by_days(
    request: Request,
    days: int = Query(..., ge=1, le=3650),
):
    """Convenience: delete audit rows older than ``days`` days."""
    from ..auth import require_scope

    principal = resolve_principal(request)
    denial = require_scope(principal, Scope.ADMIN)
    if denial is not None:
        return denial
    store = request.app.state.store
    before = datetime.now() - timedelta(days=days)
    deleted = await store.prune_audit_before(before_ts=before)
    remaining = await store.count_audit()
    return {
        "deleted": deleted,
        "remaining": remaining,
        "before": before.isoformat(),
        "days": days,
    }


__all__ = ["router"]