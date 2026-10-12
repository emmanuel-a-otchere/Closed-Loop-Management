"""Webhook subscriptions router (Slice 5 PR2).

CRUD on webhook subscriptions, plus a delivery-history read endpoint.

Each subscription has a secret that's returned plaintext exactly once
on creation; thereafter only its SHA-256 fingerprint is persisted
(the on-disk column is named `secret_hash` to make this explicit).

Delivery attempts are best-effort: every audit row triggers an HTTP
POST to every active subscription, signed with HMAC-SHA256 over the
JSON body. The outcome is recorded on webhook_delivery regardless of
success / failure.
"""

from __future__ import annotations

import hashlib
import secrets
from uuid import UUID

from fastapi import APIRouter, Path, Query, Request, Response, status

from ..errors import ErrorCode, error_response
from ..models import (
    WebhookDelivery,
    WebhookDeliveryPage,
    WebhookSubscriptionCreate,
    WebhookSubscriptionInfo,
    WebhookSubscriptionIssued,
)

router = APIRouter(prefix="/api/v1/webhookSubscriptions", tags=["webhooks"])


def _to_info(row: dict[str, object]) -> WebhookSubscriptionInfo:
    desc_raw = row.get("description")
    desc = str(desc_raw) if desc_raw is not None else None
    return WebhookSubscriptionInfo(
        id=UUID(str(row["id"])),
        url=str(row["url"]),
        description=desc,
        createdAt=row["created_at"],  # type: ignore[arg-type]
        active=bool(row.get("active")),
        lastAttemptAt=row.get("last_attempt_at"),  # type: ignore[arg-type]
        lastStatus=row.get("last_status"),  # type: ignore[arg-type]
    )


@router.post(
    "",
    response_model=WebhookSubscriptionIssued,
    status_code=status.HTTP_201_CREATED,
    summary="Create a webhook subscription",
)
async def create_webhook(
    request: Request,
    payload: WebhookSubscriptionCreate,
) -> WebhookSubscriptionIssued:
    """Register a new subscriber. Plaintext secret returned exactly
    once.
    """
    store = request.app.state.store
    plaintext_secret = secrets.token_urlsafe(32)
    secret_hash = hashlib.sha256(plaintext_secret.encode("utf-8")).hexdigest()
    sub_id, created_at = await store.create_webhook_subscription(
        url=str(payload.url),
        description=payload.description,
        secret_hash=secret_hash,
    )
    return WebhookSubscriptionIssued(
        id=sub_id,
        url=str(payload.url),
        description=payload.description,
        secret=plaintext_secret,
        createdAt=created_at,
    )


@router.get(
    "",
    response_model=list[WebhookSubscriptionInfo],
    summary="List webhook subscriptions",
)
async def list_webhooks(request: Request) -> list[WebhookSubscriptionInfo]:
    store = request.app.state.store
    rows = await store.list_webhook_subscriptions()
    return [_to_info(r) for r in rows]


@router.delete(
    "/{webhookId}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a webhook subscription",
)
async def delete_webhook(
    request: Request,
    webhookId: UUID = Path(...),
) -> Response:
    store = request.app.state.store
    try:
        await store.delete_webhook_subscription(webhookId)
    except Exception as exc:
        from ..store import NotFoundError

        if isinstance(exc, NotFoundError):
            return error_response(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message=str(exc),
            )
        raise
    return Response(status_code=204)


@router.get(
    "/{webhookId}/deliveries",
    response_model=WebhookDeliveryPage,
    summary="List delivery attempts for a subscription",
)
async def list_webhook_deliveries(
    request: Request,
    webhookId: UUID = Path(...),
    limit: int = Query(100, ge=1, le=1000),
    cursor: str | None = Query(None),
) -> WebhookDeliveryPage:
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
    rows, next_cursor = await store.list_webhook_deliveries(
        subscription_id=webhookId, limit=limit, before_id=before_id
    )
    items = [
        WebhookDelivery(
            id=UUID(str(r["id"])),
            subscriptionId=UUID(str(r["subscription_id"])),
            auditId=UUID(str(r["audit_id"])),
            attemptedAt=r["attempted_at"],
            statusCode=r.get("status_code"),
            error=r.get("error"),
            attempt=int(r["attempt"]),
        )
        for r in rows
    ]
    return WebhookDeliveryPage(
        items=items,
        limit=limit,
        nextCursor=next_cursor,
    )


__all__ = ["router"]
