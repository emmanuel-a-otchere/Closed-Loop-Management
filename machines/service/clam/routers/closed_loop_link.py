"""ClosedLoopLink CRUD endpoints.

Slice 2 PR1 wires basic CRUD for the daisy-chain / hierarchical interlink
topology. PR3 adds cycle detection, bulk operations, and topology queries
on top of that.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Path, Query, Request, status

from ..errors import ErrorCode, error_response
from ..models import (
    ClosedLoopLink,
    ClosedLoopLinkCreateBatch,
    ClosedLoopTopology,
    LinkDirection,
    LinkKind,
    Page,
)
from ..store import CycleError, NotFoundError

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


def _cycle_response(exc: CycleError):
    return error_response(
        status_code=409,
        code=ErrorCode.CYCLE_DETECTED,
        message=str(exc),
        details={"cycle": [str(n) for n in exc.cycle]},
    )


@router.post(
    "",
    response_model=ClosedLoopLink,
    status_code=status.HTTP_201_CREATED,
    summary="Create a single closed loop link (cycle-checked)",
    responses={
        409: {"description": "Cycle detected -- the link would close a loop"},
    },
)
async def create_closed_loop_link(
    payload: ClosedLoopLink, request: Request
) -> Any:
    try:
        return await _store(request).create_closed_loop_link(payload)
    except CycleError as exc:
        return _cycle_response(exc)


@router.post(
    "/bulk",
    response_model=list[ClosedLoopLink],
    status_code=status.HTTP_201_CREATED,
    summary="All-or-nothing bulk creation of closed loop links",
    responses={
        409: {"description": "Cycle detected -- entire batch rejected"},
    },
)
async def bulk_create_closed_loop_links(
    payload: ClosedLoopLinkCreateBatch, request: Request
) -> Any:
    try:
        return await _store(request).bulk_create_closed_loop_links(payload.items)
    except CycleError as exc:
        return _cycle_response(exc)


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
    "/topology",
    response_model=ClosedLoopTopology,
    summary="Get the full closed-loop link topology",
)
async def get_topology(request: Request) -> ClosedLoopTopology:
    links = await _store(request).topology_view()
    nodes: set[UUID] = set()
    for link in links:
        nodes.add(link.source.id)
        nodes.add(link.target.id)
    return ClosedLoopTopology(
        linkCount=len(links),
        nodeCount=len(nodes),
        links=links,
    )


@router.get(
    "/path",
    response_model=list[UUID],
    summary="Shortest path between two closed loops via the link graph",
)
async def find_path(
    request: Request,
    sourceId: UUID = Query(..., description="Source closed loop ID"),
    targetId: UUID = Query(..., description="Target closed loop ID"),
) -> list[UUID]:
    return await _store(request).find_link_path(sourceId, targetId)


@router.get(
    "/{linkId}",
    response_model=ClosedLoopLink,
    summary="Get a closed loop link",
)
async def get_closed_loop_link(
    request: Request,
    linkId: UUID = Path(..., description="ClosedLoopLink ID"),
) -> Any:
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


@router.get(
    "/from/{loopId}",
    response_model=list[ClosedLoopLink],
    summary="List links originating from a closed loop (downstream)",
)
async def list_links_from_loop(
    request: Request,
    loopId: UUID = Path(..., description="Closed loop ID"),
) -> list[ClosedLoopLink]:
    return await _store(request).list_links_from(loopId)


@router.get(
    "/to/{loopId}",
    response_model=list[ClosedLoopLink],
    summary="List links targeting a closed loop (upstream)",
)
async def list_links_to_loop(
    request: Request,
    loopId: UUID = Path(..., description="Closed loop ID"),
) -> list[ClosedLoopLink]:
    return await _store(request).list_links_to(loopId)
