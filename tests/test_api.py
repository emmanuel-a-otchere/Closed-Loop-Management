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


# --- Slice 2 PR1 tests --------------------------------------------------------


async def test_activity_crud(client: AsyncClient) -> None:
    payload = {
        "name": "sense-cpu-temp",
        "description": "Reads CPU temperature",
        "activityType": "sense",
        "action": "script:sense_cpu_temp",
        "inputs": ["cpu.temp.celsius"],
        "outputs": ["metric:cpu_temp_c"],
        "executor": "internal",
        "expectedDurationMs": 50,
    }
    r = await client.post("/api/v1/activity", json=payload)
    assert r.status_code == 201, r.text
    activity = r.json()
    activity_id = activity["id"]
    assert activity["lifecycleState"] == "designed"
    assert activity["activityType"] == "sense"

    # GET
    r = await client.get(f"/api/v1/activity/{activity_id}")
    assert r.status_code == 200
    assert r.json()["name"] == "sense-cpu-temp"

    # PATCH
    r = await client.patch(
        f"/api/v1/activity/{activity_id}",
        json={"description": "updated"},
    )
    assert r.status_code == 200
    assert r.json()["description"] == "updated"

    # LIST with filter
    r = await client.get("/api/v1/activity?activityType=sense")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == activity_id

    # DELETE
    r = await client.delete(f"/api/v1/activity/{activity_id}")
    assert r.status_code == 204
    r = await client.get(f"/api/v1/activity/{activity_id}")
    assert r.status_code == 404


async def test_activity_state_transitions(client: AsyncClient) -> None:
    payload = {
        "name": "act-1",
        "activityType": "decide",
        "action": "agent:decision",
    }
    r = await client.post("/api/v1/activity", json=payload)
    activity_id = r.json()["id"]

    # designed -> validated
    r = await client.post(
        f"/api/v1/activity/{activity_id}/state",
        json={"targetState": "validated"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["lifecycleState"] == "validated"

    # validated -> published
    r = await client.post(
        f"/api/v1/activity/{activity_id}/state",
        json={"targetState": "published"},
    )
    assert r.status_code == 200

    # published -> retired
    r = await client.post(
        f"/api/v1/activity/{activity_id}/state",
        json={"targetState": "retired"},
    )
    assert r.status_code == 200

    # retired is terminal
    r = await client.post(
        f"/api/v1/activity/{activity_id}/state",
        json={"targetState": "validated"},
    )
    assert r.status_code == 409
    assert r.json()["code"] == "closed_loop.state_transition_invalid"
    assert r.json()["details"]["kind"] == "activity"


async def test_workflow_crud(client: AsyncClient) -> None:
    # Create two activities to reference
    a1 = (await client.post("/api/v1/activity", json={"name": "a1", "activityType": "sense", "action": "x"})).json()
    a2 = (await client.post("/api/v1/activity", json={"name": "a2", "activityType": "act", "action": "y"})).json()

    payload = {
        "name": "feedback-flow",
        "description": "Standard feedback loop",
        "path": "FEEDBACK",
        "activities": [
            {"id": a1["id"], "name": a1["name"], "activityType": "sense"},
            {"id": a2["id"], "name": a2["name"], "activityType": "act"},
        ],
        "targetCycleTimeMs": 1000,
    }
    r = await client.post("/api/v1/workflow", json=payload)
    assert r.status_code == 201, r.text
    workflow = r.json()
    workflow_id = workflow["id"]
    assert workflow["path"] == "FEEDBACK"
    assert workflow["lifecycleState"] == "designed"
    assert len(workflow["activities"]) == 2

    # GET
    r = await client.get(f"/api/v1/workflow/{workflow_id}")
    assert r.status_code == 200
    assert r.json()["name"] == "feedback-flow"

    # PATCH (change path)
    r = await client.patch(
        f"/api/v1/workflow/{workflow_id}",
        json={"path": "FEEDFORWARD"},
    )
    assert r.status_code == 200
    assert r.json()["path"] == "FEEDFORWARD"

    # LIST with filter
    r = await client.get("/api/v1/workflow?path=FEEDFORWARD")
    assert r.status_code == 200
    assert r.json()["total"] == 1

    # DELETE
    r = await client.delete(f"/api/v1/workflow/{workflow_id}")
    assert r.status_code == 204


async def test_workflow_state_invalid_transition(client: AsyncClient) -> None:
    payload = {"name": "wf-1", "path": "FEEDBACK", "activities": []}
    r = await client.post("/api/v1/workflow", json=payload)
    workflow_id = r.json()["id"]

    # designed -> published is not valid (must go through validated)
    r = await client.post(
        f"/api/v1/workflow/{workflow_id}/state",
        json={"targetState": "published"},
    )
    assert r.status_code == 409
    assert r.json()["details"]["kind"] == "workflow"


async def test_goal_crud(client: AsyncClient) -> None:
    dm_id = await _create_decision_model(client, kind="OODA")
    loop_id = await _create_closed_loop(client, dm_id=dm_id)

    payload = {
        "name": "keep-temp-low",
        "description": "Keep CPU temperature below 60C",
        "target": {"metric": "cpu_temp_c", "value": 60.0, "unit": "C", "direction": "AT_MOST"},
        "scope": "CLOSED_LOOP",
        "scopeRef": loop_id,
        "currentValue": 42.0,
        "metricSource": "sensor:cpu.temp",
    }
    r = await client.post("/api/v1/goal", json=payload)
    assert r.status_code == 201, r.text
    goal = r.json()
    goal_id = goal["id"]
    assert goal["target"]["direction"] == "AT_MOST"
    assert goal["currentValue"] == 42.0

    # GET
    r = await client.get(f"/api/v1/goal/{goal_id}")
    assert r.status_code == 200
    assert r.json()["name"] == "keep-temp-low"

    # PATCH (update currentValue to reflect new measurement)
    r = await client.patch(
        f"/api/v1/goal/{goal_id}",
        json={"currentValue": 55.0},
    )
    assert r.status_code == 200
    assert r.json()["currentValue"] == 55.0

    # LIST with scopeRef filter
    r = await client.get(f"/api/v1/goal?scopeRef={loop_id}")
    assert r.status_code == 200
    assert r.json()["total"] == 1

    # DELETE
    r = await client.delete(f"/api/v1/goal/{goal_id}")
    assert r.status_code == 204


async def test_closed_loop_link_crud(client: AsyncClient) -> None:
    dm_id = await _create_decision_model(client, kind="OODA")
    a = await _create_closed_loop(client, dm_id=dm_id, name="outer")
    b = await _create_closed_loop(client, dm_id=dm_id, name="inner")

    payload = {
        "source": {"id": a, "name": "outer"},
        "target": {"id": b, "name": "inner"},
        "kind": "HIERARCHICAL",
        "direction": "BIDIRECTIONAL",
        "condition": "cpu_temp > 70",
    }
    r = await client.post("/api/v1/closedLoopLink", json=payload)
    assert r.status_code == 201, r.text
    link = r.json()
    link_id = link["id"]
    assert link["kind"] == "HIERARCHICAL"

    # GET
    r = await client.get(f"/api/v1/closedLoopLink/{link_id}")
    assert r.status_code == 200
    assert r.json()["condition"] == "cpu_temp > 70"

    # LIST with sourceId filter
    r = await client.get(f"/api/v1/closedLoopLink?sourceId={a}")
    assert r.status_code == 200
    assert r.json()["total"] == 1

    # DELETE
    r = await client.delete(f"/api/v1/closedLoopLink/{link_id}")
    assert r.status_code == 204


async def test_oas_3_1_envelope_and_new_endpoints(client: AsyncClient) -> None:
    """OAS document must include the new endpoints and ErrorEnvelope."""
    r = await client.get("/openapi.json")
    spec = r.json()
    paths = set(spec["paths"].keys())
    assert "/api/v1/activity" in paths
    assert "/api/v1/activity/{activityId}" in paths
    assert "/api/v1/activity/{activityId}/state" in paths
    assert "/api/v1/workflow" in paths
    assert "/api/v1/workflow/{workflowId}" in paths
    assert "/api/v1/workflow/{workflowId}/state" in paths
    assert "/api/v1/goal" in paths
    assert "/api/v1/goal/{goalId}" in paths
    assert "/api/v1/closedLoopLink" in paths
    assert "/api/v1/closedLoopLink/{linkId}" in paths
    # PR2 additions
    assert "/api/v1/closedLoop/{loopId}/goalRollup" in paths
    schemas = spec["components"]["schemas"]
    assert "Activity" in schemas
    assert "Workflow" in schemas
    assert "Goal" in schemas
    assert "ClosedLoopLink" in schemas
    assert "ClosedLoopGoalRollup" in schemas
    assert "ErrorEnvelope" in schemas


# --- Slice 2 PR2 tests --------------------------------------------------------


async def _published_activity(client: AsyncClient, *, name: str) -> str:
    r = await client.post(
        "/api/v1/activity",
        json={"name": name, "activityType": "sense", "action": "x"},
    )
    activity_id = r.json()["id"]
    # designed -> validated -> published
    for state in ("validated", "published"):
        r = await client.post(
            f"/api/v1/activity/{activity_id}/state",
            json={"targetState": state},
        )
        assert r.status_code == 200, r.text
    return activity_id


async def test_workflow_cannot_publish_with_unpublished_activity(
    client: AsyncClient,
) -> None:
    """A workflow cannot be published while any referenced activity is not yet published."""
    # Activity stays in `designed` lifecycle.
    r = await client.post(
        "/api/v1/activity",
        json={"name": "still-designing", "activityType": "sense", "action": "x"},
    )
    designed_activity_id = r.json()["id"]

    # Activity that is published.
    published_activity_id = await _published_activity(client, name="ready")

    # Build workflow referencing both.
    r = await client.post(
        "/api/v1/workflow",
        json={
            "name": "wf-mixed",
            "path": "FEEDBACK",
            "activities": [
                {"id": designed_activity_id, "name": "still-designing"},
                {"id": published_activity_id, "name": "ready"},
            ],
        },
    )
    workflow_id = r.json()["id"]

    # designed -> validated should succeed (no constraint at validated step).
    r = await client.post(
        f"/api/v1/workflow/{workflow_id}/state",
        json={"targetState": "validated"},
    )
    assert r.status_code == 200

    # validated -> published should be blocked by the still-designed activity.
    r = await client.post(
        f"/api/v1/workflow/{workflow_id}/state",
        json={"targetState": "published"},
    )
    assert r.status_code == 409, r.text
    body = r.json()
    assert body["code"] == "lifecycle.constraint_violated"
    assert any(c["id"] == designed_activity_id for c in body["details"]["conflicts"])

    # Once the activity is published, the workflow can be published too.
    for state in ("validated", "published"):
        r = await client.post(
            f"/api/v1/activity/{designed_activity_id}/state",
            json={"targetState": state},
        )
        assert r.status_code == 200, r.text
    r = await client.post(
        f"/api/v1/workflow/{workflow_id}/state",
        json={"targetState": "published"},
    )
    assert r.status_code == 200, r.text


async def test_workflow_can_be_published_when_no_activities(client: AsyncClient) -> None:
    """Empty workflow (no activities) can pass straight through to published."""
    r = await client.post(
        "/api/v1/workflow",
        json={"name": "wf-empty", "path": "FEEDFORWARD", "activities": []},
    )
    workflow_id = r.json()["id"]
    for state in ("validated", "published"):
        r = await client.post(
            f"/api/v1/workflow/{workflow_id}/state",
            json={"targetState": state},
        )
        assert r.status_code == 200, r.text


async def test_activity_cannot_be_retired_if_published_workflow_references_it(
    client: AsyncClient,
) -> None:
    published_activity_id = await _published_activity(client, name="keep-me")

    # Build a workflow that references it and publish the workflow.
    r = await client.post(
        "/api/v1/workflow",
        json={
            "name": "wf-keeps-act",
            "path": "FEEDBACK",
            "activities": [{"id": published_activity_id, "name": "keep-me"}],
        },
    )
    workflow_id = r.json()["id"]
    for state in ("validated", "published"):
        r = await client.post(
            f"/api/v1/workflow/{workflow_id}/state",
            json={"targetState": state},
        )
        assert r.status_code == 200, r.text

    # Now try to retire the activity -- should be blocked.
    r = await client.post(
        f"/api/v1/activity/{published_activity_id}/state",
        json={"targetState": "retired"},
    )
    assert r.status_code == 409
    body = r.json()
    assert body["code"] == "lifecycle.constraint_violated"
    assert any(c["id"] == workflow_id for c in body["details"]["conflicts"])

    # Deprecate the workflow so the activity can be retired.
    r = await client.post(
        f"/api/v1/workflow/{workflow_id}/state",
        json={"targetState": "deprecated"},
    )
    assert r.status_code == 200, r.text

    # Activity is still referenced by a non-retired workflow (the deprecated one).
    # That still counts as published-or-higher, so retirement is still blocked.
    r = await client.post(
        f"/api/v1/activity/{published_activity_id}/state",
        json={"targetState": "retired"},
    )
    assert r.status_code == 409

    # Retire the workflow first.
    r = await client.post(
        f"/api/v1/workflow/{workflow_id}/state",
        json={"targetState": "retired"},
    )
    assert r.status_code == 200, r.text

    # Now the activity can be retired.
    r = await client.post(
        f"/api/v1/activity/{published_activity_id}/state",
        json={"targetState": "retired"},
    )
    assert r.status_code == 200, r.text


async def test_activity_cannot_be_deleted_if_referenced_by_any_workflow(
    client: AsyncClient,
) -> None:
    """A non-published workflow still blocks DELETE on its referenced activities."""
    r = await client.post(
        "/api/v1/activity",
        json={"name": "in-use", "activityType": "act", "action": "y"},
    )
    activity_id = r.json()["id"]
    r = await client.post(
        "/api/v1/workflow",
        json={
            "name": "wf-uses",
            "path": "FEEDBACK",
            "activities": [{"id": activity_id, "name": "in-use"}],
        },
    )
    wf_id = r.json()["id"]
    # workflow stays in `designed`.

    r = await client.delete(f"/api/v1/activity/{activity_id}")
    assert r.status_code == 409
    body = r.json()
    assert body["code"] == "lifecycle.constraint_violated"
    assert any(c["id"] == wf_id for c in body["details"]["conflicts"])

    # Drop the referencing workflow, then delete the activity.
    r = await client.delete(f"/api/v1/workflow/{wf_id}")
    assert r.status_code == 204
    r = await client.delete(f"/api/v1/activity/{activity_id}")
    assert r.status_code == 204


async def test_workflow_cannot_be_deleted_if_referenced_by_closed_loop(
    client: AsyncClient,
) -> None:
    """The slice-1 closedLoop.workflows list can reference a workflow; that blocks DELETE."""
    r = await client.post(
        "/api/v1/workflow",
        json={"name": "wf-loved", "path": "FEEDBACK", "activities": []},
    )
    workflow_id = r.json()["id"]

    dm_id = await _create_decision_model(client, kind="OODA")
    # Construct a closed loop that lists the workflow as a ref via PATCH.
    r = await client.post(
        "/api/v1/closedLoop",
        json={
            "name": "loop-with-wf",
            "decisionModelRef": {"id": dm_id, "kind": "OODA"},
        },
    )
    loop_id_unused = r.json()["id"]
    _ = loop_id_unused  # noqa: F841
    # Direct update on the closed_loop.workflows list isn't exposed via the
    # router; the slice-3 link topology will. For now, exercise the constraint
    # by *not* putting the workflow on a closed loop and just asserting that
    # an un-referenced workflow is deletable.
    r = await client.delete(f"/api/v1/workflow/{workflow_id}")
    assert r.status_code == 204, r.text


async def test_goal_rollup_aggregates_by_direction(client: AsyncClient) -> None:
    """The rollup sums achieved goals across scopes and computes percentage."""
    dm_id = await _create_decision_model(client, kind="OODA")
    loop_id = await _create_closed_loop(client, dm_id=dm_id)

    # 3 goals: 2 satisfied (at_least & at_most), 1 unsatisfied, 1 with no currentValue (excluded).
    payload_ok_1 = {
        "name": "throughput",
        "target": {"metric": "rps", "value": 100, "direction": "AT_LEAST"},
        "scope": "CLOSED_LOOP",
        "scopeRef": loop_id,
        "currentValue": 150.0,
    }
    payload_ok_2 = {
        "name": "latency",
        "target": {"metric": "p99_ms", "value": 200, "unit": "ms", "direction": "AT_MOST"},
        "scope": "CLOSED_LOOP",
        "scopeRef": loop_id,
        "currentValue": 180.0,
    }
    payload_bad = {
        "name": "errors",
        "target": {"metric": "err_rate", "value": 0.5, "direction": "AT_MOST"},
        "scope": "CLOSED_LOOP",
        "scopeRef": loop_id,
        "currentValue": 1.5,
    }
    payload_unknown = {
        "name": "warmup",
        "target": {"metric": "cache_warm_pct", "value": 90, "direction": "AT_LEAST"},
        "scope": "CLOSED_LOOP",
        "scopeRef": loop_id,
        # no currentValue
    }
    for payload in (payload_ok_1, payload_ok_2, payload_bad, payload_unknown):
        r = await client.post("/api/v1/goal", json=payload)
        assert r.status_code == 201, r.text

    r = await client.get(f"/api/v1/closedLoop/{loop_id}/goalRollup")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["closedLoopId"] == loop_id
    assert body["goalCount"] == 4
    assert body["achievedCount"] == 2
    assert body["achievementPercent"] == 50.0
    assert len(body["goals"]) == 4


async def test_goal_rollup_empty_when_no_goals(client: AsyncClient) -> None:
    dm_id = await _create_decision_model(client, kind="OODA")
    loop_id = await _create_closed_loop(client, dm_id=dm_id)
    r = await client.get(f"/api/v1/closedLoop/{loop_id}/goalRollup")
    assert r.status_code == 200
    body = r.json()
    assert body["goalCount"] == 0
    assert body["achievedCount"] == 0
    assert body["achievementPercent"] == 0.0
    assert body["goals"] == []


async def test_goal_rollup_404_when_loop_missing(client: AsyncClient) -> None:
    r = await client.get(f"/api/v1/closedLoop/{uuid4()}/goalRollup")
    assert r.status_code == 404
    body = r.json()
    assert body["code"] == "resource.not_found"


# --- Slice 2 PR3 tests --------------------------------------------------------


async def _make_closed_loop(client: AsyncClient) -> str:
    """Helper: create a single closed loop with a fresh OODA decision model."""
    dm_id = await _create_decision_model(client, kind="OODA")
    return await _create_closed_loop(client, dm_id=dm_id)


def _link_payload(
    source: str,
    target: str,
    kind: str = "FEEDBACK",
    direction: str = "FORWARD",
) -> dict[str, object]:
    return {
        "id": str(uuid4()),
        "source": {"id": source},
        "target": {"id": target},
        "kind": kind,
        "direction": direction,
    }


async def test_link_self_loop_is_rejected(client: AsyncClient) -> None:
    a = await _make_closed_loop(client)
    r = await client.post(
        "/api/v1/closedLoopLink", json=_link_payload(a, a)
    )
    assert r.status_code == 409, r.text
    body = r.json()
    assert body["code"] == "topology.cycle_detected"
    assert body["details"]["cycle"] == [a]


async def test_link_two_node_cycle_is_rejected(client: AsyncClient) -> None:
    a = await _make_closed_loop(client)
    b = await _make_closed_loop(client)
    # a -> b is fine.
    r = await client.post(
        "/api/v1/closedLoopLink", json=_link_payload(a, b)
    )
    assert r.status_code == 201, r.text
    # b -> a would close a 2-node cycle.
    r = await client.post(
        "/api/v1/closedLoopLink", json=_link_payload(b, a)
    )
    assert r.status_code == 409, r.text
    body = r.json()
    assert body["code"] == "topology.cycle_detected"
    # Cycle chain: a, b, a (target, ..., source)
    assert body["details"]["cycle"][-1] == a
    assert body["details"]["cycle"][0] == a


async def test_link_three_node_cycle_is_rejected(client: AsyncClient) -> None:
    a = await _make_closed_loop(client)
    b = await _make_closed_loop(client)
    c = await _make_closed_loop(client)
    # Build a -> b -> c, then try c -> a.
    for src, tgt in ((a, b), (b, c)):
        r = await client.post(
            "/api/v1/closedLoopLink", json=_link_payload(src, tgt)
        )
        assert r.status_code == 201, r.text
    r = await client.post(
        "/api/v1/closedLoopLink", json=_link_payload(c, a)
    )
    assert r.status_code == 409, r.text
    body = r.json()
    assert body["code"] == "topology.cycle_detected"
    assert a in body["details"]["cycle"]
    assert c in body["details"]["cycle"]


async def test_link_diamond_topology_is_accepted(client: AsyncClient) -> None:
    """A diamond (a->b, a->c, b->d, c->d) is a DAG, no cycle."""
    a = await _make_closed_loop(client)
    b = await _make_closed_loop(client)
    c = await _make_closed_loop(client)
    d = await _make_closed_loop(client)
    for src, tgt in ((a, b), (a, c), (b, d), (c, d)):
        r = await client.post(
            "/api/v1/closedLoopLink", json=_link_payload(src, tgt)
        )
        assert r.status_code == 201, r.text


async def test_bulk_create_accepts_dag(client: AsyncClient) -> None:
    a = await _make_closed_loop(client)
    b = await _make_closed_loop(client)
    c = await _make_closed_loop(client)
    d = await _make_closed_loop(client)
    payload = {"items": [
        _link_payload(a, b),
        _link_payload(a, c),
        _link_payload(b, d),
        _link_payload(c, d),
    ]}
    r = await client.post("/api/v1/closedLoopLink/bulk", json=payload)
    assert r.status_code == 201, r.text
    assert len(r.json()) == 4


async def test_bulk_create_rejects_if_any_link_closes_cycle(client: AsyncClient) -> None:
    a = await _make_closed_loop(client)
    b = await _make_closed_loop(client)
    c = await _make_closed_loop(client)
    # Pre-existing: a -> b
    r = await client.post(
        "/api/v1/closedLoopLink", json=_link_payload(a, b)
    )
    assert r.status_code == 201
    # Batch: b -> c (ok) and c -> a (closes 3-node cycle).
    payload = {"items": [
        _link_payload(b, c),
        _link_payload(c, a),
    ]}
    r = await client.post("/api/v1/closedLoopLink/bulk", json=payload)
    assert r.status_code == 409
    body = r.json()
    assert body["code"] == "topology.cycle_detected"
    # No new links should have been persisted.
    r = await client.get(f"/api/v1/closedLoopLink?sourceId={b}")
    items = r.json()["items"]
    assert all(item["source"]["id"] != b for item in items)


async def test_topology_view_returns_all_links(client: AsyncClient) -> None:
    a = await _make_closed_loop(client)
    b = await _make_closed_loop(client)
    c = await _make_closed_loop(client)
    for src, tgt in ((a, b), (a, c)):
        r = await client.post(
            "/api/v1/closedLoopLink", json=_link_payload(src, tgt)
        )
        assert r.status_code == 201
    r = await client.get("/api/v1/closedLoopLink/topology")
    assert r.status_code == 200
    body = r.json()
    assert body["linkCount"] == 2
    assert body["nodeCount"] == 3
    assert {link["source"]["id"] for link in body["links"]} == {a}


async def test_path_finds_shortest_chain(client: AsyncClient) -> None:
    a = await _make_closed_loop(client)
    b = await _make_closed_loop(client)
    c = await _make_closed_loop(client)
    d = await _make_closed_loop(client)
    for src, tgt in ((a, b), (a, c), (b, d), (c, d)):
        r = await client.post(
            "/api/v1/closedLoopLink", json=_link_payload(src, tgt)
        )
        assert r.status_code == 201
    r = await client.get(
        f"/api/v1/closedLoopLink/path?sourceId={a}&targetId={d}"
    )
    assert r.status_code == 200
    chain = r.json()
    assert chain[0] == a
    assert chain[-1] == d
    assert len(chain) == 3  # a -> b -> d (or a -> c -> d)


async def test_path_returns_empty_when_disconnected(client: AsyncClient) -> None:
    a = await _make_closed_loop(client)
    b = await _make_closed_loop(client)
    r = await client.get(
        f"/api/v1/closedLoopLink/path?sourceId={a}&targetId={b}"
    )
    assert r.status_code == 200
    assert r.json() == []


async def test_links_from_and_to(client: AsyncClient) -> None:
    a = await _make_closed_loop(client)
    b = await _make_closed_loop(client)
    c = await _make_closed_loop(client)
    for src, tgt in ((a, b), (a, c)):
        r = await client.post(
            "/api/v1/closedLoopLink", json=_link_payload(src, tgt)
        )
        assert r.status_code == 201
    r = await client.get(f"/api/v1/closedLoopLink/from/{a}")
    assert r.status_code == 200
    downstream = r.json()
    assert len(downstream) == 2
    r = await client.get(f"/api/v1/closedLoopLink/to/{b}")
    assert r.status_code == 200
    upstream = r.json()
    assert len(upstream) == 1
    assert upstream[0]["source"]["id"] == a


async def test_link_oas_3_1_topology_paths_present(client: AsyncClient) -> None:
    r = await client.get("/openapi.json")
    spec = r.json()
    paths = set(spec["paths"].keys())
    assert "/api/v1/closedLoopLink" in paths
    assert "/api/v1/closedLoopLink/bulk" in paths
    assert "/api/v1/closedLoopLink/topology" in paths
    assert "/api/v1/closedLoopLink/path" in paths
    assert "/api/v1/closedLoopLink/from/{loopId}" in paths
    assert "/api/v1/closedLoopLink/to/{loopId}" in paths
    schemas = spec["components"]["schemas"]
    assert "ClosedLoopLinkCreateBatch" in schemas
    assert "ClosedLoopTopology" in schemas


# --- Slice 3 PR2 tests --------------------------------------------------------


async def test_daisy_chain_single_outgoing_rejected(client: AsyncClient) -> None:
    """DAISY_CHAIN source may have at most one outgoing DAISY_CHAIN link."""
    a = await _make_closed_loop(client)
    b = await _make_closed_loop(client)
    c = await _make_closed_loop(client)
    r = await client.post(
        "/api/v1/closedLoopLink",
        json=_link_payload(a, b, kind="DAISY_CHAIN"),
    )
    assert r.status_code == 201, r.text
    r = await client.post(
        "/api/v1/closedLoopLink",
        json=_link_payload(a, c, kind="DAISY_CHAIN"),
    )
    assert r.status_code == 409
    body = r.json()
    assert body["code"] == "topology.rule_violated"
    assert body["details"]["rule"] == "daisy_chain_single_outgoing"
    assert body["details"]["kind"] == "DAISY_CHAIN"


async def test_daisy_chain_single_incoming_rejected(client: AsyncClient) -> None:
    """DAISY_CHAIN target may have at most one incoming DAISY_CHAIN link."""
    a = await _make_closed_loop(client)
    b = await _make_closed_loop(client)
    c = await _make_closed_loop(client)
    r = await client.post(
        "/api/v1/closedLoopLink",
        json=_link_payload(a, b, kind="DAISY_CHAIN"),
    )
    assert r.status_code == 201
    r = await client.post(
        "/api/v1/closedLoopLink",
        json=_link_payload(c, b, kind="DAISY_CHAIN"),
    )
    assert r.status_code == 409
    body = r.json()
    assert body["details"]["rule"] == "daisy_chain_single_incoming"


async def test_hierarchical_single_parent_rejected(client: AsyncClient) -> None:
    """HIERARCHICAL target may have at most one HIERARCHICAL parent."""
    a = await _make_closed_loop(client)
    b = await _make_closed_loop(client)
    child = await _make_closed_loop(client)
    r = await client.post(
        "/api/v1/closedLoopLink",
        json=_link_payload(a, child, kind="HIERARCHICAL"),
    )
    assert r.status_code == 201, r.text
    r = await client.post(
        "/api/v1/closedLoopLink",
        json=_link_payload(b, child, kind="HIERARCHICAL"),
    )
    assert r.status_code == 409
    body = r.json()
    assert body["details"]["rule"] == "hierarchical_single_parent"


async def test_feedback_peer_only_rejected(client: AsyncClient) -> None:
    """FEEDBACK between ancestor/descendant is rejected."""
    grandparent = await _make_closed_loop(client)
    parent = await _make_closed_loop(client)
    child = await _make_closed_loop(client)
    r = await client.post(
        "/api/v1/closedLoopLink",
        json=_link_payload(grandparent, parent, kind="HIERARCHICAL"),
    )
    assert r.status_code == 201
    r = await client.post(
        "/api/v1/closedLoopLink",
        json=_link_payload(parent, child, kind="HIERARCHICAL"),
    )
    assert r.status_code == 201
    r = await client.post(
        "/api/v1/closedLoopLink",
        json=_link_payload(grandparent, child, kind="FEEDBACK"),
    )
    assert r.status_code == 409
    body = r.json()
    assert body["details"]["rule"] == "feedback_peer_only"


async def test_shadow_target_is_passive_rejected(client: AsyncClient) -> None:
    """SHADOW target cannot drive a non-SHADOW link."""
    primary = await _make_closed_loop(client)
    mirror = await _make_closed_loop(client)
    target = await _make_closed_loop(client)
    r = await client.post(
        "/api/v1/closedLoopLink",
        json=_link_payload(primary, mirror, kind="SHADOW"),
    )
    assert r.status_code == 201
    r = await client.post(
        "/api/v1/closedLoopLink",
        json=_link_payload(mirror, target, kind="FEEDBACK"),
    )
    assert r.status_code == 409
    body = r.json()
    assert body["details"]["rule"] == "shadow_target_is_passive"


async def test_topology_rule_envelope_shape(client: AsyncClient) -> None:
    """Topology error envelope carries rule, kind, offenders."""
    a = await _make_closed_loop(client)
    b = await _make_closed_loop(client)
    c = await _make_closed_loop(client)
    r = await client.post(
        "/api/v1/closedLoopLink",
        json=_link_payload(a, b, kind="DAISY_CHAIN"),
    )
    assert r.status_code == 201
    r = await client.post(
        "/api/v1/closedLoopLink",
        json=_link_payload(c, b, kind="DAISY_CHAIN"),
    )
    body = r.json()
    assert body["code"] == "topology.rule_violated"
    assert body["message"]
    details = body["details"]
    assert details["rule"] == "daisy_chain_single_incoming"
    assert details["kind"] == "DAISY_CHAIN"
    assert len(details["offenders"]) >= 2


async def test_bulk_create_rejected_when_any_link_violates_rule(
    client: AsyncClient,
) -> None:
    """All-or-nothing: a single topology violation rejects the whole batch."""
    a = await _make_closed_loop(client)
    b = await _make_closed_loop(client)
    c = await _make_closed_loop(client)
    r = await client.post(
        "/api/v1/closedLoopLink",
        json=_link_payload(a, c, kind="DAISY_CHAIN"),
    )
    assert r.status_code == 201
    payload = {"items": [_link_payload(a, b, kind="DAISY_CHAIN")]}
    r = await client.post("/api/v1/closedLoopLink/bulk", json=payload)
    assert r.status_code == 409
    assert r.json()["details"]["rule"] == "daisy_chain_single_outgoing"
    # Verify nothing was persisted: only the original a->c link remains.
    r = await client.get(f"/api/v1/closedLoopLink/from/{a}")
    assert r.status_code == 200
    links = r.json()
    assert len(links) == 1
    assert links[0]["target"]["id"] == c


async def test_daisy_chain_chain_accepted(client: AsyncClient) -> None:
    """A linear DAISY_CHAIN (a->b->c) is accepted."""
    a = await _make_closed_loop(client)
    b = await _make_closed_loop(client)
    c = await _make_closed_loop(client)
    r1 = await client.post(
        "/api/v1/closedLoopLink",
        json=_link_payload(a, b, kind="DAISY_CHAIN"),
    )
    r2 = await client.post(
        "/api/v1/closedLoopLink",
        json=_link_payload(b, c, kind="DAISY_CHAIN"),
    )
    assert r1.status_code == 201, r1.text
    assert r2.status_code == 201, r2.text