"""DecisionModel CRUD."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, Query, Request, status

from ..models import (
    DecisionModel,
    Page,
)
from ..store import NotFoundError

router = APIRouter(
    prefix="/api/v1/decisionModel",
    tags=["decisionModel"],
)


def _store(request: Request):
    return request.app.state.store


@router.post(
    "",
    response_model=DecisionModel,
    status_code=status.HTTP_201_CREATED,
    summary="Create a decision model",
)
async def create_decision_model(
    payload: DecisionModel,
    request: Request,
) -> DecisionModel:
    return await _store(request).create_decision_model(payload)


@router.get(
    "",
    response_model=Page,
    summary="List decision models",
)
async def list_decision_models(
    request: Request,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
) -> Page:
    items, total = await _store(request).list_decision_models(
        page=page, page_size=pageSize
    )
    return Page(
        items=[item.model_dump(mode="json") for item in items],
        total=total,
        page=page,
        pageSize=pageSize,
    )


@router.get(
    "/{modelId}",
    response_model=DecisionModel,
    summary="Get a decision model",
)
async def get_decision_model(
    request: Request,
    modelId: UUID = Path(...),  # noqa: N803
) -> DecisionModel:
    try:
        return await _store(request).get_decision_model(modelId)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete(
    "/{modelId}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a decision model",
)
async def delete_decision_model(
    request: Request,
    modelId: UUID,  # noqa: N803
) -> None:
    try:
        await _store(request).delete_decision_model(modelId)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


__all__ = ["router"]