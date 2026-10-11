"""Goal CRUD endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Path, Query, Request, status

from ..errors import ErrorCode, error_response
from ..models import (
    Goal,
    GoalCreate,
    GoalScope,
    GoalUpdate,
    Page,
)
from ..store import NotFoundError

router = APIRouter(
    prefix="/api/v1/goal",
    tags=["goal"],
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
    response_model=Goal,
    status_code=status.HTTP_201_CREATED,
    summary="Create a goal",
)
async def create_goal(
    payload: GoalCreate, request: Request
) -> Goal:
    return await _store(request).create_goal(payload)


@router.get(
    "",
    response_model=Page,
    summary="List goals",
)
async def list_goals(
    request: Request,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    scope: GoalScope | None = Query(default=None),
    scopeRef: UUID | None = Query(default=None),
) -> Page:
    items, total = await _store(request).list_goals(
        page=page,
        page_size=pageSize,
        scope=scope.value if scope else None,
        scope_ref=scopeRef,
    )
    return Page(items=items, total=total, page=page, pageSize=pageSize)


@router.get(
    "/{goalId}",
    response_model=Goal,
    summary="Get a goal",
)
async def get_goal(
    request: Request,
    goalId: UUID = Path(..., description="Goal ID"),
) -> Goal:
    try:
        return await _store(request).get_goal(goalId)
    except NotFoundError as exc:
        return _not_found_response(exc)


@router.patch(
    "/{goalId}",
    response_model=Goal,
    summary="Update a goal (partial)",
)
async def update_goal(
    request: Request,
    patch: GoalUpdate,
    goalId: UUID = Path(..., description="Goal ID"),
) -> Goal:
    try:
        return await _store(request).update_goal(goalId, patch)
    except NotFoundError as exc:
        return _not_found_response(exc)


@router.delete(
    "/{goalId}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a goal",
)
async def delete_goal(
    request: Request,
    goalId: UUID = Path(..., description="Goal ID"),
) -> None:
    try:
        await _store(request).delete_goal(goalId)
    except NotFoundError as exc:
        return _not_found_response(exc)