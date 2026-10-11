"""ClosedLoopLink CRUD endpoints.

PR1 wires the basic CRUD for the daisy-chain / hierarchical interlink
topology. PR3 adds cycle detection and bulk operations on top of this.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Path, Query, Request, status

from ..errors import ErrorCode, error_response
from ..models import (
    ClosedLoopLink,
    LinkDirection,
    LinkKind,
    Page,
)
from ..store import NotFoundError

router = APIRouter(
    prefix="/api/v1/closedLoopLink",
    tags=["closedLoopLink"],
)


def _store(request: Request):
    return request.app.state.store


def _not_found_response(exc: NotFoundError):
    return error_response(
        status_code=404,
        code=ErrorCode.NOT_FOUND,
        message=str(exc),
    )


@router.post(
    "",
    response_model=ClosedLoopLink,
    status_code=status.HTTP_201_CREATED,
    summary="Create a closed loop link (daisy-chain, hierarchical, feedback, shadow)",
)
async def create_closed_loop_link(
    payload: ClosedLoopLink, request: Request
) -> ClosedLoopLink:
    return await _store(request).create_closed_loop_link(payload)


@router.get(
    "",
    response_model=Page,
    summary="List closed loop links",
)
async def list_closed_loop_links(
    request: Request,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    sourceId: UUID | None = Query(default=None),
    targetId: UUID | None = Query(default=None),
    kind: LinkKind | None = Query(default=None),
    direction: LinkDirection | None = Query(default=None),
) -> Page:
    items, total = await _store(request).list_closed_loop_links(
        page=page,
        page_size=pageSize,
        source_id=sourceId,
        target_id=targetId,
        kind=kind.value if kind else None,
    )
    return Page(items=items, total=total, page=page, pageSize=pageSize)


@router.get(
    "/{linkId}",
    response_model=ClosedLoopLink,
    summary="Get a closed loop link",
)
async def get_closed_loop_link(
    request: Request,
    linkId: UUID = Path(..., description="ClosedLoopLink ID"),
) -> ClosedLoopLink:
    try:
        return await _store(request).get_closed_loop_link(linkId)
    except NotFoundError as exc:
        return _not_found_response(exc)


@router.delete(
    "/{linkId}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a closed loop link",
)
async def delete_closed_loop_link(
    request: Request,
    linkId: UUID = Path(..., description="ClosedLoopLink ID"),
) -> None:
    try:
        await _store(request).delete_closed_loop_link(linkId)
    except NotFoundError as exc:
        return _not_found_response(exc)