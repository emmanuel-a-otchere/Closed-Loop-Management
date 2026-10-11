"""Workflow CRUD + lifecycle endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Path, Query, Request, status

from ..errors import ErrorCode, error_response
from ..models import (
    ActivityLifecycleState,
    Page,
    Workflow,
    WorkflowCreate,
    WorkflowPath,
    WorkflowStateTransitionRequest,
    WorkflowUpdate,
)
from ..store import NotFoundError, StateTransitionError

router = APIRouter(
    prefix="/api/v1/workflow",
    tags=["workflow"],
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


@router.post(
    "",
    response_model=Workflow,
    status_code=status.HTTP_201_CREATED,
    summary="Create a workflow",
)
async def create_workflow(
    payload: WorkflowCreate, request: Request
) -> Workflow:
    return await _store(request).create_workflow(payload)


@router.get(
    "",
    response_model=Page,
    summary="List workflows",
)
async def list_workflows(
    request: Request,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    lifecycleState: ActivityLifecycleState | None = Query(default=None),
    path: WorkflowPath | None = Query(default=None),
) -> Page:
    items, total = await _store(request).list_workflows(
        page=page,
        page_size=pageSize,
        lifecycle_state=lifecycleState,
        path=path.value if path else None,
    )
    return Page(items=items, total=total, page=page, pageSize=pageSize)


@router.get(
    "/{workflowId}",
    response_model=Workflow,
    summary="Get a workflow",
)
async def get_workflow(
    request: Request,
    workflowId: UUID = Path(..., description="Workflow ID"),
) -> Workflow:
    try:
        return await _store(request).get_workflow(workflowId)
    except NotFoundError as exc:
        return _not_found_response(exc)


@router.patch(
    "/{workflowId}",
    response_model=Workflow,
    summary="Update a workflow (partial)",
)
async def update_workflow(
    request: Request,
    patch: WorkflowUpdate,
    workflowId: UUID = Path(..., description="Workflow ID"),
) -> Workflow:
    try:
        return await _store(request).update_workflow(workflowId, patch)
    except NotFoundError as exc:
        return _not_found_response(exc)


@router.delete(
    "/{workflowId}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a workflow",
)
async def delete_workflow(
    request: Request,
    workflowId: UUID = Path(..., description="Workflow ID"),
) -> None:
    try:
        await _store(request).delete_workflow(workflowId)
    except NotFoundError as exc:
        return _not_found_response(exc)


@router.post(
    "/{workflowId}/state",
    response_model=Workflow,
    summary="Transition a workflow to a new lifecycle state",
)
async def transition_workflow_state(
    request: Request,
    body: WorkflowStateTransitionRequest,
    workflowId: UUID = Path(..., description="Workflow ID"),
) -> Workflow:
    try:
        return await _store(request).transition_workflow_state(workflowId, body)
    except NotFoundError as exc:
        return _not_found_response(exc)
    except StateTransitionError as exc:
        return _invalid_transition_response(exc)