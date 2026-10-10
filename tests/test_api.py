"""Tests for the CLAM FastAPI app."""

from __future__ import annotations

import tempfile
from collections.abc import AsyncIterator
from pathlib import Path
from uuid import uuid4

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from machines.service.clam.main import create_app


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """Yield an httpx AsyncClient bound to an in-process FastAPI app.

    Each test session gets its own SQLite file under ``tempfile.gettempdir()``.
    """

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "clam-test.db"
        app = create_app(db_path=db_path)
        async with app.router.lifespan_context(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                yield ac


async def test_health(client: AsyncClient) -> None:
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


async def test_openapi_document_is_oas_31(client: AsyncClient) -> None:
    r = await client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    assert spec["openapi"].startswith("3.1")
    assert spec["info"]["title"] == "Closed Loop Automation Management (CLAM)"
    assert "/api/v1/closedLoop" in spec["paths"]
    assert "/api/v1/decisionModel" in spec["paths"]


async def test_decision_model_lifecycle(client: AsyncClient) -> None:
    payload = {
        "kind": "OODA",
        "name": "ooda-1",
        "observe": {"id": str(uuid4())},
        "orient": {"id": str(uuid4())},
        "decide": {"id": str(uuid4())},
        "act": {"id": str(uuid4())},
    }
    r = await client.post("/api/v1/decisionModel", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    model_id = created["id"]

    r = await client.get(f"/api/v1/decisionModel/{model_id}")
    assert r.status_code == 200
    assert r.json()["kind"] == "OODA"

    r = await client.get("/api/v1/decisionModel")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == model_id

    r = await client.delete(f"/api/v1/decisionModel/{model_id}")
    assert r.status_code == 204

    r = await client.get(f"/api/v1/decisionModel/{model_id}")
    assert r.status_code == 404


async def test_closed_loop_lifecycle(client: AsyncClient) -> None:
    dm = {
        "kind": "MAPE",
        "name": "mape-1",
        "monitor": {"id": str(uuid4())},
        "analyze": {"id": str(uuid4())},
        "plan": {"id": str(uuid4())},
        "execute": {"id": str(uuid4())},
    }
    r = await client.post("/api/v1/decisionModel", json=dm)
    assert r.status_code == 201
    dm_id = r.json()["id"]

    payload = {
        "name": "loop-1",
        "description": "first loop",
        "decisionModelRef": {"id": dm_id, "kind": "MAPE"},
    }
    r = await client.post("/api/v1/closedLoop", json=payload)
    assert r.status_code == 201, r.text
    loop = r.json()
    loop_id = loop["id"]
    assert loop["state"] == "designed"

    r = await client.patch(
        f"/api/v1/closedLoop/{loop_id}",
        json={"description": "updated"},
    )
    assert r.status_code == 200
    assert r.json()["description"] == "updated"

    r = await client.get(f"/api/v1/closedLoop/{loop_id}")
    assert r.status_code == 200
    assert r.json()["name"] == "loop-1"


async def test_state_transitions(client: AsyncClient) -> None:
    dm_id = await _create_decision_model(client, kind="OODA")
    loop_id = await _create_closed_loop(client, dm_id=dm_id)

    r = await client.get(f"/api/v1/closedLoop/{loop_id}/state")
    assert r.status_code == 200
    assert r.json()["state"] == "designed"

    # designed -> validated
    r = await client.post(
        f"/api/v1/closedLoop/{loop_id}/state",
        json={"targetState": "validated"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["state"] == "validated"

    # validated -> published
    r = await client.post(
        f"/api/v1/closedLoop/{loop_id}/state",
        json={"targetState": "published"},
    )
    assert r.status_code == 200
    assert r.json()["state"] == "published"

    # published -> active
    r = await client.post(
        f"/api/v1/closedLoop/{loop_id}/state",
        json={"targetState": "active"},
    )
    assert r.status_code == 200
    assert r.json()["state"] == "active"

    # active -> retired is allowed
    r = await client.post(
        f"/api/v1/closedLoop/{loop_id}/state",
        json={"targetState": "retired"},
    )
    assert r.status_code == 200
    assert r.json()["state"] == "retired"


async def test_state_transition_invalid_returns_409(client: AsyncClient) -> None:
    dm_id = await _create_decision_model(client, kind="OODA")
    loop_id = await _create_closed_loop(client, dm_id=dm_id)

    # designed -> active is not a valid transition (must go through validated/published)
    r = await client.post(
        f"/api/v1/closedLoop/{loop_id}/state",
        json={"targetState": "active"},
    )
    assert r.status_code == 409
    body = r.json()
    assert body["code"] == "closed_loop.state_transition_invalid"
    assert body["details"]["currentState"] == "designed"
    assert body["details"]["targetState"] == "active"


async def test_get_unknown_closed_loop_returns_404(client: AsyncClient) -> None:
    r = await client.get(f"/api/v1/closedLoop/{uuid4()}")
    assert r.status_code == 404


async def test_validation_error_envelope(client: AsyncClient) -> None:
    # Missing required field `name`
    r = await client.post(
        "/api/v1/closedLoop",
        json={"description": "no name", "decisionModelRef": {"id": str(uuid4()), "kind": "OODA"}},
    )
    assert r.status_code == 422
    body = r.json()
    assert body["code"] == "request.validation_error"


async def test_pagination(client: AsyncClient) -> None:
    dm_id = await _create_decision_model(client, kind="OODA")
    for i in range(5):
        await _create_closed_loop(client, dm_id=dm_id, name=f"loop-{i}")

    r = await client.get("/api/v1/closedLoop?page=1&pageSize=2")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 5
    assert body["page"] == 1
    assert body["pageSize"] == 2
    assert len(body["items"]) == 2


# --- helpers ---------------------------------------------------------------


async def _create_decision_model(client: AsyncClient, *, kind: str) -> str:
    activity_ids = [str(uuid4()) for _ in range(4)]
    payload: dict[str, object]
    if kind == "OODA":
        payload = {
            "kind": "OODA",
            "name": f"dm-{kind}-{uuid4()}",
            "observe": {"id": activity_ids[0]},
            "orient": {"id": activity_ids[1]},
            "decide": {"id": activity_ids[2]},
            "act": {"id": activity_ids[3]},
        }
    elif kind == "MAPE":
        payload = {
            "kind": "MAPE",
            "name": f"dm-{kind}-{uuid4()}",
            "monitor": {"id": activity_ids[0]},
            "analyze": {"id": activity_ids[1]},
            "plan": {"id": activity_ids[2]},
            "execute": {"id": activity_ids[3]},
        }
    else:  # pragma: no cover - guarded
        raise ValueError(kind)
    r = await client.post("/api/v1/decisionModel", json=payload)
    assert r.status_code == 201, r.text
    return r.json()["id"]


async def _create_closed_loop(
    client: AsyncClient,
    *,
    dm_id: str,
    name: str = "test-loop",
) -> str:
    r = await client.post(
        "/api/v1/closedLoop",
        json={
            "name": name,
            "decisionModelRef": {"id": dm_id, "kind": "OODA"},
        },
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]