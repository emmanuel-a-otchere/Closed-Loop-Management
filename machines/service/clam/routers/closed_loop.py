"""ClosedLoop CRUD + state endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, Query, Request, status

from ..errors import ErrorCode, error_response
from ..models import (
    ClosedLoop,
    ClosedLoopCreate,
    ClosedLoopUpdate,
    Page,
    StateResponse,
    StateTransitionRequest,
)
from ..store import NotFoundError, StateTransitionError

router = APIRouter(
    prefix="/api/v1/closedLoop",
    tags=["closedLoop"],
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
    response_model=ClosedLoop,
    status_code=status.HTTP_201_CREATED,
    summary="Create a closed loop",
)
async def create_closed_loop(
    payload: ClosedLoopCreate, request: Request
) -> ClosedLoop:
    return await _store(request).create_closed_loop(payload)


@router.get(
    "",
    response_model=Page,
    summary="List closed loops",
)
async def list_closed_loops(
    request: Request,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
) -> Page:
    items, total = await _store(request).list_closed_loops(
        page=page, page_size=pageSize
    )
    return Page(
        items=[item.model_dump(mode="json") for item in items],
        total=total,
        page=page,
        pageSize=pageSize,
    )


@router.get(
    "/{loopId}",
    response_model=ClosedLoop,
    summary="Get a closed loop",
)
async def get_closed_loop(
    request: Request,
    loopId: UUID = Path(...),  # noqa: N803 (OAS parameter casing)
) -> ClosedLoop:
    try:
        return await _store(request).get_closed_loop(loopId)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=404, detail=str(exc)
        ) from exc


@router.patch(
    "/{loopId}",
    response_model=ClosedLoop,
    summary="Patch a closed loop",
)
async def patch_closed_loop(
    request: Request,
    loopId: UUID,  # noqa: N803
    patch: ClosedLoopUpdate,
) -> ClosedLoop:
    try:
        return await _store(request).update_closed_loop(loopId, patch)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete(
    "/{loopId}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a closed loop",
)
async def delete_closed_loop(
    request: Request,
    loopId: UUID,  # noqa: N803
) -> None:
    try:
        await _store(request).delete_closed_loop(loopId)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/{loopId}/state",
    response_model=StateResponse,
    summary="Read a closed loop's state",
)
async def get_state(
    request: Request,
    loopId: UUID,  # noqa: N803
) -> StateResponse:
    try:
        loop = await _store(request).get_closed_loop(loopId)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return StateResponse(state=loop.state)


@router.post(
    "/{loopId}/state",
    response_model=StateResponse,
    summary="Transition a closed loop to a new state",
    responses={409: {"description": "Invalid state transition"}},
)
async def transition_state(
    request: Request,
    loopId: UUID,  # noqa: N803
    payload: StateTransitionRequest,
):
    """Returns either a ``StateResponse`` (200) or an error envelope (404/409)."""
    try:
        loop = await _store(request).transition_state(loopId, payload)
    except NotFoundError as exc:
        return _not_found_response(exc)
    except StateTransitionError as exc:
        return error_response(
            status_code=409,
            code=ErrorCode.STATE_TRANSITION_INVALID,
            message=str(exc),
            details={
                "currentState": exc.current.value,
                "targetState": exc.target.value,
            },
        )
    return StateResponse(state=loop.state)


__all__ = ["router"]