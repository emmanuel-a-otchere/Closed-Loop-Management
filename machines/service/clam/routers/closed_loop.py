"""ClosedLoop CRUD + state endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, Path, Query, Request, status
from fastapi.routing import APIRouter

from ..errors import ErrorCode, error_response
from ..models import (
    ClosedLoop,
    ClosedLoopCreate,
    ClosedLoopGoalRollup,
    ClosedLoopUpdate,
    EvalRequest,
    EvalResult,
    JobInfo,
    JobState,
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


@router.post(
    "/{loopId}/workflow/{workflowId}",
    response_model=ClosedLoop,
    status_code=status.HTTP_201_CREATED,
    summary="Link an existing workflow to a closed loop (populates closed_loop_workflow junction)",
)
async def link_workflow_to_loop(
    request: Request,
    loopId: UUID,  # noqa: N803
    workflowId: UUID,  # noqa: N803
) -> ClosedLoop:
    try:
        return await _store(request).link_workflow_to_closed_loop(loopId, workflowId)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


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


@router.get(
    "/{loopId}/goalRollup",
    response_model=ClosedLoopGoalRollup,
    summary="Aggregate goal achievement across a closed loop and all of its child resources",
)
async def goal_rollup(
    request: Request,
    loopId: UUID = Path(..., description="Closed loop ID"),
) -> ClosedLoopGoalRollup:
    """Compute a goal achievement rollup for the closed loop.

    Aggregates goals from:
    - the closed loop's own ``goals`` array (CLOSED_LOOP scope with scopeRef matching the loop id)
    - any workflow the loop references (WORKFLOW scope)
    - any activity those workflows reference (ACTIVITY scope)

    Each goal is evaluated against its target direction. The endpoint
    returns 404 if the closed loop does not exist.
    """
    try:
        rollup = await _store(request).aggregate_closed_loop_goals(loopId)
    except NotFoundError as exc:
        return _not_found_response(exc)
    return ClosedLoopGoalRollup.model_validate(rollup)


# --- Slice 5 PR3: one-shot eval + async jobs --------------------------------


@router.post(
    "/{loopId}/eval",
    response_model=EvalResult,
    summary="One-shot decision + transition (synchronous)",
)
async def eval_loop(
    request: Request,
    loopId: UUID,  # noqa: N803
    payload: EvalRequest = EvalRequest(),
):
    """Run the next-state decision and apply it in one round trip."""
    try:
        store = _store(request)
        loop, transitioned, kind, rationale = (
            await store.run_eval_synchronously(loopId)
        )
    except NotFoundError as exc:
        return _not_found_response(exc)
    return EvalResult(
        state=loop.state.value,
        transitioned=transitioned,
        decisionKind=kind,
        rationale=rationale,
    )


@router.post(
    "/{loopId}/eval/async",
    response_model=JobInfo,
    status_code=202,
    summary="Enqueue an async one-shot eval",
)
async def enqueue_eval_async(
    request: Request,
    loopId: UUID,  # noqa: N803
    payload: EvalRequest = EvalRequest(),
):
    """Enqueue an eval and return the job id immediately."""
    try:
        store = _store(request)
        await store.get_closed_loop(loopId)
    except NotFoundError as exc:
        return _not_found_response(exc)
    job_id, enqueued_at = await store.enqueue_eval_job(
        loop_id=loopId, action="eval"
    )

    async def _run() -> None:
        try:
            await store.update_job_running(job_id)
            loop, _, _, _ = await store.run_eval_synchronously(loopId)
            await store.update_job_succeeded(job_id, loop.state.value)
        except Exception as exc:
            await store.update_job_failed(
                job_id, f"{type(exc).__name__}: {exc}"
            )

    import asyncio as _asyncio

    try:
        loop_obj = _asyncio.get_running_loop()
    except RuntimeError:
        return JobInfo(
            id=job_id,
            loopId=loopId,
            action="eval",
            state=JobState.QUEUED,
            enqueuedAt=enqueued_at,
            startedAt=None,
            completedAt=None,
            resultState=None,
            error="No running event loop; the job will not run.",
        )
    loop_obj.create_task(_run())
    return JobInfo(
        id=job_id,
        loopId=loopId,
        action="eval",
        state=JobState.QUEUED,
        enqueuedAt=enqueued_at,
        startedAt=None,
        completedAt=None,
        resultState=None,
        error=None,
    )


@router.get(
    "/{loopId}/jobs/{jobId}",
    response_model=JobInfo,
    summary="Get an async eval job",
)
async def get_job(
    request: Request,
    loopId: UUID,  # noqa: N803
    jobId: UUID,  # noqa: N803
):
    row = await _store(request).get_job(jobId)
    if row is None or str(row["loop_id"]) != str(loopId):
        return error_response(
            status_code=404,
            code=ErrorCode.NOT_FOUND,
            message=f"Job {jobId} not found for loop {loopId}",
        )
    return JobInfo(
        id=UUID(str(row["id"])),
        loopId=UUID(str(row["loop_id"])),
        action=str(row["action"]),
        state=JobState(str(row["state"])),
        enqueuedAt=row["enqueued_at"],
        startedAt=row.get("started_at"),
        completedAt=row.get("completed_at"),
        resultState=row.get("result_state"),
        error=row.get("error"),
    )


__all__ = ["router"]