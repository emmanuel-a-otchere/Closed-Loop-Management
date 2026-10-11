"""Request log router (PR1).

Lists the most recent request-log rows captured by the
request-log middleware. Requires READ scope.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query, Request

from ..errors import ErrorCode, error_response
from ..models import RequestLogPage

router = APIRouter(prefix="/api/v1/_log", tags=["observability"])


@router.get(
    "/recent",
    response_model=RequestLogPage,
    summary="Recent request-log entries (cursor-paginated, ts DESC)",
)
async def recent_request_log(
    request: Request,
    limit: int = Query(
        100, ge=1, le=1000, description="Page size (1..1000, default 100)"
    ),
    cursor: str | None = Query(
        None, description="Opaque cursor (the previous page's nextCursor)"
    ),
) -> RequestLogPage:
    """Return the most recent request-log entries (newest first)."""
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
    items, next_cursor = await store.list_request_log(
        limit=limit, before_id=before_id
    )
    return RequestLogPage(
        items=items,
        limit=limit,
        nextCursor=str(next_cursor) if next_cursor else None,
    )


__all__ = ["router"]
