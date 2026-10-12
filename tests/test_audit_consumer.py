"""Tests for the audit_consumer toolkit (Slice 7 PR3).

Uses httpx.MockTransport to simulate the paginated audit
endpoint; no live server required.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

from machines.toolkits.audit_consumer import (
    iter_audit_rows,
    write_csv,
    write_jsonl,
)
from machines.toolkits.audit_consumer.cli import main


def _run_cli(args: list[str]) -> int:
    saved = sys.argv
    sys.argv = ["clam-audit-consumer", *args]
    try:
        return main()
    finally:
        sys.argv = saved


def _row(i: int, cursor: str | None = None) -> dict:
    return {
        "id": f"00000000-0000-0000-0000-{i:012d}",
        "ts": f"2026-10-12T10:{i:02d}:00+00:00",
        "actor": "USER",
        "action": "closed_loop.state_transition",
        "entityKind": "ClosedLoop",
        "entityId": f"11111111-1111-1111-1111-{i:012d}",
        "correlationId": f"corr-{i}",
        "before": {"state": "active"},
        "after": {"state": "paused"},
    }


def _two_page_handler(request: httpx.Request) -> httpx.Response:
    """Page 1 returns rows 0..1 + cursor; page 2 returns row 2 + null."""
    cursor = request.url.params.get("cursor")
    if cursor is None:
        return httpx.Response(
            200,
            json={
                "items": [_row(0), _row(1)],
                "nextCursor": "page-2",
            },
        )
    assert cursor == "page-2"
    return httpx.Response(
        200,
        json={"items": [_row(2)], "nextCursor": None},
    )


def _error_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(500, json={"error": "boom"})


# --- iter_audit_rows ---------------------------------------------------------


def test_iter_walks_cursor_until_exhausted() -> None:
    transport = httpx.MockTransport(_two_page_handler)
    rows = list(
        iter_audit_rows(
            base="http://test", transport=transport, limit=2
        )
    )
    assert len(rows) == 3
    assert [r["correlationId"] for r in rows] == [
        "corr-0",
        "corr-1",
        "corr-2",
    ]


def test_iter_passes_filters_as_query_params() -> None:
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        for k, v in request.url.params.items():
            seen[k] = v
        return httpx.Response(200, json={"items": [], "nextCursor": None})

    transport = httpx.MockTransport(handler)
    list(
        iter_audit_rows(
            base="http://test",
            transport=transport,
            since="2026-10-01T00:00:00+00:00",
            until="2026-10-12T00:00:00+00:00",
            entity_kind="ClosedLoop",
            entity_id="11111111-1111-1111-1111-000000000000",
            actor="USER",
            action="goal.update",
            limit=50,
        )
    )
    assert seen["since"] == "2026-10-01T00:00:00+00:00"
    assert seen["until"] == "2026-10-12T00:00:00+00:00"
    assert seen["entityKind"] == "ClosedLoop"
    assert seen["actor"] == "USER"
    assert seen["action"] == "goal.update"
    assert seen["limit"] == "50"


def test_iter_sends_bearer_token() -> None:
    seen_auth: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_auth.append(request.headers.get("authorization", ""))
        return httpx.Response(200, json={"items": [], "nextCursor": None})

    transport = httpx.MockTransport(handler)
    list(
        iter_audit_rows(
            base="http://test", transport=transport, token="secret-token"
        )
    )
    assert seen_auth == ["Bearer secret-token"]


def test_iter_raises_on_error() -> None:
    transport = httpx.MockTransport(_error_handler)
    try:
        list(iter_audit_rows(base="http://test", transport=transport))
    except httpx.HTTPStatusError as e:
        assert e.response.status_code == 500
    else:
        raise AssertionError("expected HTTPStatusError")


# --- write_csv / write_jsonl --------------------------------------------------


def test_write_csv_header_and_rows(tmp_path: Path) -> None:
    out = tmp_path / "audit.csv"
    count = write_csv(iter([_row(0), _row(1)]), out)
    assert count == 2
    import csv as csv_mod

    with out.open(newline="") as f:
        rows = list(csv_mod.DictReader(f))
    assert len(rows) == 2
    assert rows[0]["correlationId"] == "corr-0"
    assert rows[0]["action"] == "closed_loop.state_transition"
    # `before` round-trips as JSON text.
    assert json.loads(rows[0]["before"]) == {"state": "active"}
    assert json.loads(rows[0]["after"]) == {"state": "paused"}


def test_write_csv_none_fields_become_empty(tmp_path: Path) -> None:
    out = tmp_path / "audit.csv"
    row = _row(0)
    row["before"] = None
    row["after"] = None
    write_csv(iter([row]), out)
    lines = out.read_text().splitlines()
    assert lines[1].endswith(",")


def test_write_jsonl_one_line_per_row(tmp_path: Path) -> None:
    out = tmp_path / "audit.jsonl"
    count = write_jsonl(iter([_row(0), _row(1), _row(2)]), out)
    assert count == 3
    lines = [line for line in out.read_text().splitlines() if line.strip()]
    assert len(lines) == 3
    assert json.loads(lines[0])["correlationId"] == "corr-0"


# --- CLI ---------------------------------------------------------------------


def test_cli_csv(tmp_path: Path, capsys, monkeypatch) -> None:
    """CLI end-to-end with a mocked transport."""
    transport = httpx.MockTransport(_two_page_handler)
    out = tmp_path / "audit.csv"

    # Patch httpx.Client construction to inject the mock transport.
    real_client = httpx.Client

    def patched(*args, **kwargs):
        kwargs["transport"] = transport
        return real_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "Client", patched)

    rc = _run_cli(
        [
            "--base",
            "http://test",
            "--format",
            "csv",
            "--out",
            str(out),
        ]
    )
    assert rc == 0
    assert "Wrote 3 audit rows (csv)" in capsys.readouterr().out
    assert len(out.read_text().splitlines()) == 4  # header + 3 rows


def test_cli_jsonl(tmp_path: Path, capsys, monkeypatch) -> None:
    transport = httpx.MockTransport(_two_page_handler)
    out = tmp_path / "audit.jsonl"
    real_client = httpx.Client

    def patched(*args, **kwargs):
        kwargs["transport"] = transport
        return real_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "Client", patched)

    rc = _run_cli(
        [
            "--base",
            "http://test",
            "--format",
            "jsonl",
            "--out",
            str(out),
        ]
    )
    assert rc == 0
    assert "Wrote 3 audit rows (jsonl)" in capsys.readouterr().out
    lines = [line for line in out.read_text().splitlines() if line.strip()]
    assert len(lines) == 3
