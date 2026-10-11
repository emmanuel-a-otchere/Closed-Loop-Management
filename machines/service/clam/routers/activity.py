"""Activity CRUD + lifecycle endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Path, Query, Request, status

from ..errors import ErrorCode, error_response
from ..models import (
    Activity,
    ActivityCreate,
    ActivityLifecycleState,
    ActivityStateTransitionRequest,
    ActivityType,
    ActivityUpdate,
    Page,
)
from ..store import LifecycleConstraintError, NotFoundError, StateTransitionError

router = APIRouter(
    prefix="/api/v1/activity",
    tags=["activity"],
)


def _store(request: Request):
    return request.app.state.store


def _not_found_response(exc: NotFoundError):
    return error_response(
        status_code=404,
        code=ErrorCode.NOT_FOUND,
        message=str(exc),
    )


def _invalid_transition_response(exc: StateTransitionError):
    current_v = (
        exc.current.value if hasattr(exc.current, "value") else str(exc.current)
    )
    target_v = (
        exc.target.value if hasattr(exc.target, "value") else str(exc.target)
    )
    return error_response(
        status_code=409,
        code=ErrorCode.STATE_TRANSITION_INVALID,
        message=str(exc),
        details={
            "currentState": current_v,
            "targetState": target_v,
            "kind": exc.kind,
        },
    )


def _lifecycle_constraint_response(exc: LifecycleConstraintError):
    return error_response(
        status_code=409,
        code=ErrorCode.LIFECYCLE_CONSTRAINT,
        message=str(exc),
        details={"conflicts": exc.conflicts},
    )


@router.post(
    "",
    response_model=Activity,
    status_code=status.HTTP_201_CREATED,
    summary="Create an activity",
)
async def create_activity(
    payload: ActivityCreate, request: Request
) -> Activity:
    return await _store(request).create_activity(payload)


@router.get(
    "",
    response_model=Page,
    summary="List activities",
)
async def list_activities(
    request: Request,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    lifecycleState: ActivityLifecycleState | None = Query(default=None),
    activityType: ActivityType | None = Query(default=None),
) -> Page:
    items, total = await _store(request).list_activities(
        page=page,
        page_size=pageSize,
        lifecycle_state=lifecycleState,
        activity_type=activityType,
    )
    return Page(items=items, total=total, page=page, pageSize=pageSize)


@router.get(
    "/{activityId}",
    response_model=Activity,
    summary="Get an activity",
)
async def get_activity(
    request: Request,
    activityId: UUID = Path(..., description="Activity ID"),
) -> Activity:
    try:
        return await _store(request).get_activity(activityId)
    except NotFoundError as exc:
        return _not_found_response(exc)


@router.patch(
    "/{activityId}",
    response_model=Activity,
    summary="Update an activity (partial)",
)
async def update_activity(
    request: Request,
    patch: ActivityUpdate,
    activityId: UUID = Path(..., description="Activity ID"),
) -> Activity:
    try:
        return await _store(request).update_activity(activityId, patch)
    except NotFoundError as exc:
        return _not_found_response(exc)


@router.delete(
    "/{activityId}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an activity",
)
async def delete_activity(
    request: Request,
    activityId: UUID = Path(..., description="Activity ID"),
) -> None:
    try:
        await _store(request).delete_activity(activityId)
    except NotFoundError as exc:
        return _not_found_response(exc)
    except LifecycleConstraintError as exc:
        return _lifecycle_constraint_response(exc)


@router.post(
    "/{activityId}/state",
    response_model=Activity,
    summary="Transition an activity to a new lifecycle state",
)
async def transition_activity_state(
    request: Request,
    body: ActivityStateTransitionRequest,
    activityId: UUID = Path(..., description="Activity ID"),
) -> Activity:
    try:
        return await _store(request).transition_activity_state(activityId, body)
    except NotFoundError as exc:
        return _not_found_response(exc)
    except StateTransitionError as exc:
        return _invalid_transition_response(exc)
    except LifecycleConstraintError as exc:
        return _lifecycle_constraint_response(exc)