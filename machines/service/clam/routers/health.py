"""Health router.

Slice 4 PR4 splits the original /health into:

- ``/health/live``: trivial 200. The process is up.
- ``/health/ready``: 200 when the DB is reachable and the token store
  is initialised. 503 otherwise.
- ``/health``: kept for backward compatibility; returns 200 always.

Plus a Prometheus text-format ``/metrics`` exporter that surfaces
the in-process request / audit / token counters.
"""

from __future__ import annotations

import aiosqlite
from fastapi import APIRouter, Request, Response

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe (backward compatible)")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/live", summary="Liveness probe")
async def live() -> dict[str, str]:
    """Process is up; always 200."""
    return {"status": "ok"}


@router.get("/health/ready", summary="Readiness probe")
async def ready(request: Request) -> Response:
    """200 when DB is reachable + token store initialised, 503 otherwise."""
    store = getattr(request.app.state, "store", None)
    db_ok = True
    if store is not None:
        try:
            async with aiosqlite.connect(str(store.db_path)) as db:
                await db.execute("SELECT 1")
        except Exception:
            db_ok = False
    token_store = getattr(request.app.state, "token_store", None)
    token_ok = token_store is not None
    if db_ok and token_ok:
        return Response(
            content='{"status":"ready"}',
            media_type="application/json",
            status_code=200,
        )
    body = (
        '{"status":"not_ready",'
        f'"db":{str(db_ok).lower()},'
        f'"tokenStore":{str(token_ok).lower()}}}'
    )
    return Response(content=body, media_type="application/json", status_code=503)


@router.get(
    "/metrics",
    summary="Prometheus text-format metrics exporter",
    response_class=Response,
)
async def metrics_endpoint(request: Request) -> Response:
    """Render the in-process metrics counters as Prometheus text format."""
    store = getattr(request.app.state, "store", None)
    if store is None:
        return Response(
            content="# store not initialised\n",
            media_type="text/plain; version=0.0.4",
            status_code=503,
        )
    # Refresh the gauge for the active token count.
    token_store = getattr(request.app.state, "token_store", None)
    if token_store is not None and hasattr(token_store, "list_tokens"):
        store.set_token_total(len(token_store.list_tokens()))
    body = store.format_prometheus()
    # Slice 6 PR2: append the latest snapshot timestamp so operators
    # can tell whether the counter is freshly accumulated or restored
    # from a snapshot.
    try:
        snap = await store.latest_metrics_snapshot()
        if snap is not None:
            body += (
                "\n# HELP clam_metrics_snapshot_ts "
                "Timestamp of the latest persisted metrics snapshot.\n"
            )
            body += "# TYPE clam_metrics_snapshot_ts gauge\n"
            body += f'clam_metrics_snapshot_ts "{snap["taken_at"]}"\n'
    except Exception:
        # Best-effort.
        pass
    return Response(
        content=body,
        media_type="text/plain; version=0.0.4",
        status_code=200,
    )


@router.get(
    "/metrics/snapshot",
    summary="Latest persisted metrics snapshot (Slice 6 PR2)",
)
async def metrics_snapshot_endpoint(request: Request):
    """Return the latest persisted snapshot row as JSON."""
    import json

    from fastapi.responses import JSONResponse

    store = getattr(request.app.state, "store", None)
    if store is None:
        return JSONResponse(
            status_code=503,
            content={"error": "store not initialised"},
        )
    row = await store.latest_metrics_snapshot()
    if row is None:
        return {"exists": False, "takenAt": None, "tokenTotal": 0}
    return {
        "exists": True,
        "id": row["id"],
        "takenAt": row["taken_at"],
        "tokenTotal": int(str(row["token_total"])),
        "requestTotal": json.loads(str(row["request_total_json"])),
        "requestLatencyMsSum": json.loads(
            str(row["request_latency_ms_sum_json"])
        ),
        "requestLatencyMsCount": json.loads(
            str(row["request_latency_ms_count_json"])
        ),
        "auditTotal": json.loads(str(row["audit_total_json"])),
    }


__all__ = ["router"]