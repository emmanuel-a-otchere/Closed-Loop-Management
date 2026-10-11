"""SSE audit stream router (Slice 5 PR1).

Streams new audit rows as Server-Sent Events. Each row is emitted as a
JSON-encoded `data:` line, with `id:` carrying the audit row's UUID and
`event:` carrying the AuditAction value.

Filters (entityKind / entityId) are applied per-subscriber; the
underlying publisher fans out every row and the subscriber filters
in-process.

The endpoint requires no auth in dev mode (CLAM_AUTH_ENABLED=false);
with auth enabled, READ scope is sufficient.
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from ..models import AuditEntry

router = APIRouter(prefix="/api/v1/_stream", tags=["observability"])


def _entry_to_sse(entry: AuditEntry) -> bytes:
    """Encode one audit row as an SSE event payload."""
    data = entry.model_dump_json()
    return (
        f"id: {entry.id}\n"
        f"event: {entry.action.value}\n"
        f"data: {data}\n\n"
    ).encode()


@router.get(
    "/audit",
    summary="Server-Sent Events stream of new audit rows",
    response_class=StreamingResponse,
)
async def stream_audit(
    request: Request,
    entityKind: str | None = None,
    entityId: str | None = None,
) -> StreamingResponse:
    """Stream new audit rows as Server-Sent Events.

    Optional query filters narrow the stream to a single entity kind
    and/or id. The underlying publisher emits every audit row; the
    filter is applied per-subscriber (cheap, in-process).
    """
    store = request.app.state.store
    queue = await store.subscribe_audit()
    target_entity_id: str | None = entityId

    async def event_source():
        try:
            # Initial keep-alive so the client connection negotiates
            # before any audit rows arrive.
            yield b": connected\n\n"
            while True:
                try:
                    entry = await asyncio.wait_for(queue.get(), timeout=15.0)
                except TimeoutError:
                    # Heartbeat keep-alive.
                    yield b": keep-alive\n\n"
                    continue
                if entityKind is not None and entry.entityKind != entityKind:
                    continue
                if target_entity_id is not None and str(entry.entityId) != target_entity_id:
                    continue
                yield _entry_to_sse(entry)
        finally:
            store.unsubscribe_audit(queue)

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable nginx buffering, if any
        },
    )


__all__ = ["router"]
