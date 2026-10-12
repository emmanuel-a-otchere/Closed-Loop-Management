"""CLAM audit-consumer toolkit (Slice 7 PR3).

Reads audit rows from a live CLAM service via
``GET /api/v1/audit?since=<ISO-8601>`` (cursor-paginated,
newest first) and dumps them to CSV or JSON Lines.

The consumer walks the cursor until the API returns
``nextCursor = null``, then exits. All filters supported by
the audit endpoint (entityKind, entityId, actor, action,
since, until) are exposed as CLI flags.

CSV columns: ``id, ts, actor, action, entityKind, entityId,
correlationId, before, after`` (``before`` / ``after`` are
JSON-encoded when present, empty otherwise).

JSONL emits the full audit entry per line, unchanged.

CLI usage::

    clam-audit-consumer --base http://localhost:8000 \\
        --since 2026-10-01T00:00:00+00:00 \\
        --format csv --out audit.csv

    clam-audit-consumer --base http://localhost:8000 \\
        --entity-kind ClosedLoop --format jsonl \\
        --out audit.jsonl
"""

from __future__ import annotations

import argparse
import csv
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import httpx

__all__ = ["iter_audit_rows", "write_csv", "write_jsonl", "main"]

_CSV_COLUMNS = [
    "id",
    "ts",
    "actor",
    "action",
    "entityKind",
    "entityId",
    "correlationId",
    "before",
    "after",
]


def iter_audit_rows(
    *,
    base: str,
    since: str | None = None,
    until: str | None = None,
    entity_kind: str | None = None,
    entity_id: str | None = None,
    actor: str | None = None,
    action: str | None = None,
    limit: int = 100,
    token: str | None = None,
    transport: httpx.BaseTransport | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield audit rows from the live service, newest first.

    Walks ``nextCursor`` until exhausted. Raises
    ``httpx.HTTPStatusError`` on non-2xx responses. Pass
    ``transport=httpx.ASGITransport(app=...)`` to run against
    an in-process ASGI app (used by the test suite).
    """
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    params: dict[str, Any] = {"limit": limit}
    if since:
        params["since"] = since
    if until:
        params["until"] = until
    if entity_kind:
        params["entityKind"] = entity_kind
    if entity_id:
        params["entityId"] = entity_id
    if actor:
        params["actor"] = actor
    if action:
        params["action"] = action

    with httpx.Client(
        base_url=base, timeout=30.0, headers=headers, transport=transport
    ) as client:
        cursor: str | None = None
        while True:
            page_params = dict(params)
            if cursor:
                page_params["cursor"] = cursor
            r = client.get("/api/v1/audit", params=page_params)
            r.raise_for_status()
            body = r.json()
            yield from body.get("items", [])
            cursor = body.get("nextCursor")
            if not cursor:
                return


def _csv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return str(value)


def write_csv(rows: Iterator[dict[str, Any]], out: Path) -> int:
    """Write rows to CSV; returns the number of data rows."""
    out.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {col: _csv_value(row.get(col)) for col in _CSV_COLUMNS}
            )
            count += 1
    return count


def write_jsonl(rows: Iterator[dict[str, Any]], out: Path) -> int:
    """Write rows as JSON Lines; returns the number of rows."""
    out.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with out.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base",
        default="http://localhost:8000",
        help="CLAM base URL",
    )
    parser.add_argument("--since", default=None, help="RFC3339 lower bound")
    parser.add_argument("--until", default=None, help="RFC3339 upper bound")
    parser.add_argument("--entity-kind", default=None)
    parser.add_argument("--entity-id", default=None)
    parser.add_argument("--actor", default=None)
    parser.add_argument("--action", default=None)
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Page size (1..1000, default 100)",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="Bearer token (when CLAM_AUTH_ENABLED=true)",
    )
    parser.add_argument(
        "--format",
        choices=("csv", "jsonl"),
        default="csv",
        help="Output format (default: csv)",
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    rows = iter_audit_rows(
        base=args.base,
        since=args.since,
        until=args.until,
        entity_kind=args.entity_kind,
        entity_id=args.entity_id,
        actor=args.actor,
        action=args.action,
        limit=args.limit,
        token=args.token,
    )

    if args.format == "csv":
        count = write_csv(rows, args.out)
    else:
        count = write_jsonl(rows, args.out)

    print(f"Wrote {count} audit rows ({args.format}) to {args.out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
