"""SQLite-backed store for CLAM entities.

A single-file SQLite database via aiosqlite. Suitable for local development,
tests, and the downloadable-and-testable UX; production should swap in a
proper RDBMS via the same async interface.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

import aiosqlite

from .models import (
    Activity,
    ActivityCreate,
    ActivityLifecycleState,
    ActivityStateTransitionRequest,
    ActivityType,
    ActivityUpdate,
    ClosedLoop,
    ClosedLoopCreate,
    ClosedLoopLink,
    ClosedLoopState,
    ClosedLoopUpdate,
    CustomDecisionModel,
    DecisionModel,
    Goal,
    GoalCreate,
    GoalDirection,
    GoalUpdate,
    LinkKind,
    MapeDecisionModel,
    OodaDecisionModel,
    StateTransitionRequest,
    Workflow,
    WorkflowCreate,
    WorkflowStateTransitionRequest,
    WorkflowUpdate,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS closed_loop (
    id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    state TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS decision_model (
    id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    kind TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS activity (
    id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    lifecycle_state TEXT NOT NULL,
    activity_type TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workflow (
    id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    lifecycle_state TEXT NOT NULL,
    path TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS goal (
    id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    scope TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS closed_loop_link (
    id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_closed_loop_state ON closed_loop(state);
CREATE INDEX IF NOT EXISTS idx_decision_model_kind ON decision_model(kind);
CREATE INDEX IF NOT EXISTS idx_activity_lifecycle ON activity(lifecycle_state);
CREATE INDEX IF NOT EXISTS idx_activity_type ON activity(activity_type);
CREATE INDEX IF NOT EXISTS idx_workflow_lifecycle ON workflow(lifecycle_state);
CREATE INDEX IF NOT EXISTS idx_workflow_path ON workflow(path);
CREATE INDEX IF NOT EXISTS idx_goal_scope ON goal(scope);
CREATE INDEX IF NOT EXISTS idx_link_source ON closed_loop_link(source_id);
CREATE INDEX IF NOT EXISTS idx_link_target ON closed_loop_link(target_id);
"""


_VALID_TRANSITIONS: dict[ClosedLoopState, set[ClosedLoopState]] = {
    ClosedLoopState.DESIGNED: {ClosedLoopState.VALIDATED, ClosedLoopState.RETIRED},
    ClosedLoopState.VALIDATED: {ClosedLoopState.PUBLISHED, ClosedLoopState.RETIRED},
    ClosedLoopState.PUBLISHED: {ClosedLoopState.ACTIVE, ClosedLoopState.RETIRED},
    ClosedLoopState.ACTIVE: {ClosedLoopState.PAUSED, ClosedLoopState.ERROR, ClosedLoopState.RETIRED},
    ClosedLoopState.PAUSED: {ClosedLoopState.ACTIVE, ClosedLoopState.RETIRED},
    ClosedLoopState.ERROR: {ClosedLoopState.ACTIVE, ClosedLoopState.RETIRED},
    ClosedLoopState.RETIRED: set(),
}


_VALID_ACTIVITY_TRANSITIONS: dict[ActivityLifecycleState, set[ActivityLifecycleState]] = {
    ActivityLifecycleState.DESIGNED: {
        ActivityLifecycleState.VALIDATED,
        ActivityLifecycleState.RETIRED,
    },
    ActivityLifecycleState.VALIDATED: {
        ActivityLifecycleState.PUBLISHED,
        ActivityLifecycleState.RETIRED,
    },
    ActivityLifecycleState.PUBLISHED: {
        ActivityLifecycleState.DEPRECATED,
        ActivityLifecycleState.RETIRED,
    },
    ActivityLifecycleState.DEPRECATED: {
        ActivityLifecycleState.PUBLISHED,
        ActivityLifecycleState.RETIRED,
    },
    ActivityLifecycleState.RETIRED: set(),
}


class StateTransitionError(Exception):
    """Raised when a state transition is not allowed from the current state."""

    def __init__(self, current: Any, target: Any, *, kind: str = "closed_loop") -> None:
        self.current = current
        self.target = target
        self.kind = kind
        if hasattr(current, "value"):
            current_v = current.value
        else:
            current_v = str(current)
        if hasattr(target, "value"):
            target_v = target.value
        else:
            target_v = str(target)
        super().__init__(f"Cannot transition {kind} from {current_v} to {target_v}")


# Lifecycle states that mean "this entity is in production use".
# Used by cross-resource lifecycle constraints (PR2).
_PUBLISHED_OR_HIGHER = {
    ActivityLifecycleState.PUBLISHED,
    ActivityLifecycleState.DEPRECATED,
}


class LifecycleConstraintError(Exception):
    """Raised when a lifecycle transition / delete would violate a
    cross-resource constraint.

    Examples:

    - Cannot publish a workflow that still references an activity that
      has not itself been published (designed/validated).
    - Cannot retire an activity that is still referenced by a published
      workflow.
    - Cannot delete an activity that is referenced by any workflow, or a
      workflow that is referenced by any published closed loop.

    The exception carries a ``conflicts`` list of dicts, each describing
    one offending entity, so the API can surface a structured error
    envelope to the caller.
    """

    def __init__(
        self,
        *,
        message: str,
        conflicts: list[dict[str, object]],
    ) -> None:
        self.conflicts = conflicts
        super().__init__(message)


def hierarchical_closure(
    graph: dict[UUID, list[tuple[UUID, LinkKind]]],
) -> dict[UUID, set[UUID]]:
    """Compute the transitive closure of HIERARCHICAL edges.

    Returns ``source -> {all nodes reachable through HIERARCHICAL edges}``.
    """
    closure: dict[UUID, set[UUID]] = {}
    for src in graph:
        seen: set[UUID] = set()
        stack: list[UUID] = [src]
        while stack:
            cur = stack.pop()
            for nxt, k in graph.get(cur, []):
                if k is LinkKind.HIERARCHICAL and nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        closure[src] = seen
    return closure


class NotFoundError(Exception):
    """Raised when an entity lookup fails."""


class CycleError(Exception):
    """Raised when a link would close a cycle in the topology graph."""

    def __init__(self, *, cycle: list[UUID], message: str) -> None:
        self.cycle = cycle
        super().__init__(message)


class TopologyError(Exception):
    """Raised when a proposed link violates a per-kind topology rule.

    PR2 of Slice 3 layers per-kind semantics on top of cycle detection.
    The rule that failed and the offending nodes are exposed for the
    error envelope.
    """

    def __init__(
        self,
        *,
        rule: str,
        kind: str,
        offenders: list[UUID],
        message: str,
    ) -> None:
        self.rule = rule
        self.kind = kind
        self.offenders = offenders
        self.message = message
        super().__init__(message)


class Store:
    """Thin async wrapper around an aiosqlite connection."""

    def __init__(self, db_path: Path | str) -> None:
        self.db_path = Path(db_path)

    async def init(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(SCHEMA)
            await db.commit()

    # --- ClosedLoop ---------------------------------------------------------

    async def create_closed_loop(self, payload: ClosedLoopCreate) -> ClosedLoop:
        now = datetime.now(UTC)
        loop = ClosedLoop(
            name=payload.name,
            description=payload.description,
            decisionModelRef=payload.decisionModelRef,
            createdAt=now,
            updatedAt=now,
        )
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO closed_loop (id, payload, state, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (
                    str(loop.id),
                    loop.model_dump_json(),
                    loop.state.value,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )
            await db.commit()
        return loop

    async def get_closed_loop(self, loop_id: UUID) -> ClosedLoop:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT payload FROM closed_loop WHERE id = ?", (str(loop_id),)
            ) as cur:
                row = await cur.fetchone()
        if row is None:
            raise NotFoundError(f"ClosedLoop {loop_id} not found")
        return ClosedLoop.model_validate_json(row["payload"])

    async def list_closed_loops(
        self, *, page: int = 1, page_size: int = 20
    ) -> tuple[list[ClosedLoop], int]:
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 1
        if page_size > 100:
            page_size = 100
        offset = (page - 1) * page_size
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT COUNT(*) AS c FROM closed_loop") as cur:
                total_row = await cur.fetchone()
                total = int(total_row["c"]) if total_row else 0
            async with db.execute(
                "SELECT payload FROM closed_loop ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (page_size, offset),
            ) as cur:
                rows = await cur.fetchall()
        items = [ClosedLoop.model_validate_json(r["payload"]) for r in rows]
        return items, total

    async def update_closed_loop(
        self, loop_id: UUID, patch: ClosedLoopUpdate
    ) -> ClosedLoop:
        loop = await self.get_closed_loop(loop_id)
        data = loop.model_dump()
        if patch.name is not None:
            data["name"] = patch.name
        if patch.description is not None:
            data["description"] = patch.description
        if patch.decisionModelRef is not None:
            data["decisionModelRef"] = patch.decisionModelRef.model_dump()
        data["updatedAt"] = datetime.now(UTC)
        updated = ClosedLoop.model_validate(data)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE closed_loop SET payload = ?, updated_at = ? WHERE id = ?",
                (updated.model_dump_json(), updated.updatedAt.isoformat(), str(loop_id)),
            )
            await db.commit()
        return updated

    async def delete_closed_loop(self, loop_id: UUID) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "DELETE FROM closed_loop WHERE id = ?", (str(loop_id),)
            )
            await db.commit()
            if cur.rowcount == 0:
                raise NotFoundError(f"ClosedLoop {loop_id} not found")

    async def transition_state(
        self, loop_id: UUID, request: StateTransitionRequest
    ) -> ClosedLoop:
        loop = await self.get_closed_loop(loop_id)
        allowed = _VALID_TRANSITIONS.get(loop.state, set())
        if request.targetState not in allowed:
            raise StateTransitionError(loop.state, request.targetState, kind="closed_loop")
        loop.state = request.targetState
        loop.updatedAt = datetime.now(UTC)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE closed_loop SET payload = ?, state = ?, updated_at = ? WHERE id = ?",
                (
                    loop.model_dump_json(),
                    loop.state.value,
                    loop.updatedAt.isoformat(),
                    str(loop_id),
                ),
            )
            await db.commit()
        return loop

    # --- Activity -----------------------------------------------------------

    async def create_activity(self, payload: ActivityCreate) -> Activity:
        now = datetime.now(UTC)
        activity = Activity(
            name=payload.name,
            description=payload.description,
            activityType=payload.activityType,
            action=payload.action,
            inputs=payload.inputs,
            outputs=payload.outputs,
            params=payload.params,
            executor=payload.executor,
            expectedDurationMs=payload.expectedDurationMs,
            createdAt=now,
            updatedAt=now,
        )
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO activity (id, payload, lifecycle_state, activity_type, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    str(activity.id),
                    activity.model_dump_json(),
                    activity.lifecycleState.value,
                    activity.activityType.value,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )
            await db.commit()
        return activity

    async def get_activity(self, activity_id: UUID) -> Activity:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT payload FROM activity WHERE id = ?", (str(activity_id),)
            ) as cur:
                row = await cur.fetchone()
        if row is None:
            raise NotFoundError(f"Activity {activity_id} not found")
        return Activity.model_validate_json(row["payload"])

    async def list_activities(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        lifecycle_state: ActivityLifecycleState | None = None,
        activity_type: ActivityType | None = None,
    ) -> tuple[list[Activity], int]:
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 1
        if page_size > 100:
            page_size = 100
        offset = (page - 1) * page_size
        where_clauses: list[str] = []
        params: list[Any] = []
        if lifecycle_state is not None:
            where_clauses.append("lifecycle_state = ?")
            params.append(lifecycle_state.value)
        if activity_type is not None:
            where_clauses.append("activity_type = ?")
            params.append(activity_type.value)
        where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                f"SELECT COUNT(*) AS c FROM activity{where_sql}", params
            ) as cur:
                total_row = await cur.fetchone()
                total = int(total_row["c"]) if total_row else 0
            async with db.execute(
                f"SELECT payload FROM activity{where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?",
                [*params, page_size, offset],
            ) as cur:
                rows = await cur.fetchall()
        items = [Activity.model_validate_json(r["payload"]) for r in rows]
        return items, total

    async def update_activity(
        self, activity_id: UUID, patch: ActivityUpdate
    ) -> Activity:
        activity = await self.get_activity(activity_id)
        data = activity.model_dump()
        for field in (
            "name",
            "description",
            "activityType",
            "action",
            "inputs",
            "outputs",
            "params",
            "executor",
            "expectedDurationMs",
        ):
            value = getattr(patch, field)
            if value is not None:
                data[field] = value
        if patch.lifecycleState is not None:
            data["lifecycleState"] = patch.lifecycleState.value
        data["updatedAt"] = datetime.now(UTC)
        updated = Activity.model_validate(data)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE activity SET payload = ?, lifecycle_state = ?, activity_type = ?, updated_at = ? WHERE id = ?",
                (
                    updated.model_dump_json(),
                    updated.lifecycleState.value,
                    updated.activityType.value,
                    updated.updatedAt.isoformat(),
                    str(activity_id),
                ),
            )
            await db.commit()
        return updated

    async def delete_activity(self, activity_id: UUID) -> None:
        # Cross-resource check (PR2): cannot delete if any workflow references the activity.
        await self.assert_activity_can_be_deleted(activity_id)
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "DELETE FROM activity WHERE id = ?", (str(activity_id),)
            )
            await db.commit()
            if cur.rowcount == 0:
                raise NotFoundError(f"Activity {activity_id} not found")

    async def transition_activity_state(
        self, activity_id: UUID, request: ActivityStateTransitionRequest
    ) -> Activity:
        activity = await self.get_activity(activity_id)
        allowed = _VALID_ACTIVITY_TRANSITIONS.get(activity.lifecycleState, set())
        if request.targetState not in allowed:
            raise StateTransitionError(
                activity.lifecycleState,
                request.targetState,
                kind="activity",
            )
        # Cross-resource check (PR2): cannot retire if a published workflow still references this activity.
        if request.targetState == ActivityLifecycleState.RETIRED:
            await self.assert_activity_can_be_retired(activity_id)
        activity.lifecycleState = request.targetState
        activity.updatedAt = datetime.now(UTC)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE activity SET payload = ?, lifecycle_state = ?, updated_at = ? WHERE id = ?",
                (
                    activity.model_dump_json(),
                    activity.lifecycleState.value,
                    activity.updatedAt.isoformat(),
                    str(activity_id),
                ),
            )
            await db.commit()
        return activity

    # --- Workflow -----------------------------------------------------------

    async def create_workflow(self, payload: WorkflowCreate) -> Workflow:
        now = datetime.now(UTC)
        workflow = Workflow(
            name=payload.name,
            description=payload.description,
            path=payload.path,
            activities=payload.activities,
            goals=payload.goals,
            targetCycleTimeMs=payload.targetCycleTimeMs,
            createdAt=now,
            updatedAt=now,
        )
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO workflow (id, payload, lifecycle_state, path, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    str(workflow.id),
                    workflow.model_dump_json(),
                    workflow.lifecycleState.value,
                    workflow.path.value,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )
            await db.commit()
        return workflow

    async def get_workflow(self, workflow_id: UUID) -> Workflow:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT payload FROM workflow WHERE id = ?", (str(workflow_id),)
            ) as cur:
                row = await cur.fetchone()
        if row is None:
            raise NotFoundError(f"Workflow {workflow_id} not found")
        return Workflow.model_validate_json(row["payload"])

    async def list_workflows(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        lifecycle_state: ActivityLifecycleState | None = None,
        path: str | None = None,
    ) -> tuple[list[Workflow], int]:
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 1
        if page_size > 100:
            page_size = 100
        offset = (page - 1) * page_size
        where_clauses: list[str] = []
        params: list[Any] = []
        if lifecycle_state is not None:
            where_clauses.append("lifecycle_state = ?")
            params.append(lifecycle_state.value)
        if path is not None:
            where_clauses.append("path = ?")
            params.append(path)
        where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                f"SELECT COUNT(*) AS c FROM workflow{where_sql}", params
            ) as cur:
                total_row = await cur.fetchone()
                total = int(total_row["c"]) if total_row else 0
            async with db.execute(
                f"SELECT payload FROM workflow{where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?",
                [*params, page_size, offset],
            ) as cur:
                rows = await cur.fetchall()
        items = [Workflow.model_validate_json(r["payload"]) for r in rows]
        return items, total

    async def update_workflow(
        self, workflow_id: UUID, patch: WorkflowUpdate
    ) -> Workflow:
        workflow = await self.get_workflow(workflow_id)
        data = workflow.model_dump()
        for field in (
            "name",
            "description",
            "path",
            "activities",
            "goals",
            "targetCycleTimeMs",
        ):
            value = getattr(patch, field)
            if value is not None:
                data[field] = value
        if patch.lifecycleState is not None:
            data["lifecycleState"] = patch.lifecycleState.value
        data["updatedAt"] = datetime.now(UTC)
        updated = Workflow.model_validate(data)
        # Determine the path column value (matches whatever the payload now says).
        path_value = updated.path.value
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE workflow SET payload = ?, lifecycle_state = ?, path = ?, updated_at = ? WHERE id = ?",
                (
                    updated.model_dump_json(),
                    updated.lifecycleState.value,
                    path_value,
                    updated.updatedAt.isoformat(),
                    str(workflow_id),
                ),
            )
            await db.commit()
        return updated

    async def delete_workflow(self, workflow_id: UUID) -> None:
        # Cross-resource check (PR2): cannot delete if any closed loop references the workflow.
        await self.assert_workflow_can_be_deleted(workflow_id)
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "DELETE FROM workflow WHERE id = ?", (str(workflow_id),)
            )
            await db.commit()
            if cur.rowcount == 0:
                raise NotFoundError(f"Workflow {workflow_id} not found")

    async def transition_workflow_state(
        self, workflow_id: UUID, request: WorkflowStateTransitionRequest
    ) -> Workflow:
        workflow = await self.get_workflow(workflow_id)
        allowed = _VALID_ACTIVITY_TRANSITIONS.get(workflow.lifecycleState, set())
        if request.targetState not in allowed:
            raise StateTransitionError(
                workflow.lifecycleState,
                request.targetState,
                kind="workflow",
            )
        # Cross-resource check (PR2): cannot publish a workflow whose referenced
        # activities are not yet published.
        if request.targetState == ActivityLifecycleState.PUBLISHED:
            await self.assert_workflow_can_be_published(workflow_id)
        workflow.lifecycleState = request.targetState
        workflow.updatedAt = datetime.now(UTC)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE workflow SET payload = ?, lifecycle_state = ?, updated_at = ? WHERE id = ?",
                (
                    workflow.model_dump_json(),
                    workflow.lifecycleState.value,
                    workflow.updatedAt.isoformat(),
                    str(workflow_id),
                ),
            )
            await db.commit()
        return workflow

    # --- Goal ---------------------------------------------------------------

    async def create_goal(self, payload: GoalCreate) -> Goal:
        now = datetime.now(UTC)
        goal = Goal(
            name=payload.name,
            description=payload.description,
            target=payload.target,
            scope=payload.scope,
            scopeRef=payload.scopeRef,
            timeframe=payload.timeframe,
            currentValue=payload.currentValue,
            metricSource=payload.metricSource,
            createdAt=now,
            updatedAt=now,
        )
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO goal (id, payload, scope, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (
                    str(goal.id),
                    goal.model_dump_json(),
                    goal.scope.value,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )
            await db.commit()
        return goal

    async def get_goal(self, goal_id: UUID) -> Goal:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT payload FROM goal WHERE id = ?", (str(goal_id),)
            ) as cur:
                row = await cur.fetchone()
        if row is None:
            raise NotFoundError(f"Goal {goal_id} not found")
        return Goal.model_validate_json(row["payload"])

    async def list_goals(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        scope: str | None = None,
        scope_ref: UUID | None = None,
    ) -> tuple[list[Goal], int]:
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 1
        if page_size > 100:
            page_size = 100
        offset = (page - 1) * page_size
        where_clauses: list[str] = []
        params: list[Any] = []
        if scope is not None:
            where_clauses.append("scope = ?")
            params.append(scope)
        if scope_ref is not None:
            # scopeRef is in the payload; we have to filter via JSON extraction.
            where_clauses.append("json_extract(payload, '$.scopeRef') = ?")
            params.append(str(scope_ref))
        where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                f"SELECT COUNT(*) AS c FROM goal{where_sql}", params
            ) as cur:
                total_row = await cur.fetchone()
                total = int(total_row["c"]) if total_row else 0
            async with db.execute(
                f"SELECT payload FROM goal{where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?",
                [*params, page_size, offset],
            ) as cur:
                rows = await cur.fetchall()
        items = [Goal.model_validate_json(r["payload"]) for r in rows]
        return items, total

    async def update_goal(self, goal_id: UUID, patch: GoalUpdate) -> Goal:
        goal = await self.get_goal(goal_id)
        data = goal.model_dump()
        if patch.name is not None:
            data["name"] = patch.name
        if patch.description is not None:
            data["description"] = patch.description
        if patch.target is not None:
            data["target"] = patch.target.model_dump()
        if patch.scope is not None:
            data["scope"] = patch.scope.value
        if patch.scopeRef is not None:
            data["scopeRef"] = str(patch.scopeRef)
        if patch.timeframe is not None:
            data["timeframe"] = patch.timeframe.model_dump()
        if patch.currentValue is not None:
            data["currentValue"] = patch.currentValue
        if patch.metricSource is not None:
            data["metricSource"] = patch.metricSource
        data["updatedAt"] = datetime.now(UTC)
        updated = Goal.model_validate(data)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE goal SET payload = ?, scope = ?, updated_at = ? WHERE id = ?",
                (
                    updated.model_dump_json(),
                    updated.scope.value,
                    updated.updatedAt.isoformat(),
                    str(goal_id),
                ),
            )
            await db.commit()
        return updated

    async def delete_goal(self, goal_id: UUID) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute("DELETE FROM goal WHERE id = ?", (str(goal_id),))
            await db.commit()
            if cur.rowcount == 0:
                raise NotFoundError(f"Goal {goal_id} not found")

    # --- ClosedLoopLink -----------------------------------------------------

    async def create_closed_loop_pairwise_graph(self) -> dict[UUID, list[UUID]]:
        """Load all closed loop links as a forward adjacency map source -> [targets]."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT source_id, target_id FROM closed_loop_link"
            ) as cur:
                rows = await cur.fetchall()
        graph: dict[UUID, list[UUID]] = {}
        for row in rows:
            src = UUID(row["source_id"])
            tgt = UUID(row["target_id"])
            graph.setdefault(src, []).append(tgt)
        return graph

    async def create_closed_loop_pairwise_graph_with_kinds(
        self,
    ) -> dict[UUID, list[tuple[UUID, LinkKind]]]:
        """Forward adjacency map with link kind attached.

        Used by per-kind topology rules. Returns
        ``source -> [(target, kind), ...]``.
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT source_id, target_id, kind FROM closed_loop_link"
            ) as cur:
                rows = await cur.fetchall()
        graph: dict[UUID, list[tuple[UUID, LinkKind]]] = {}
        for row in rows:
            src = UUID(row["source_id"])
            tgt = UUID(row["target_id"])
            kind = LinkKind(row["kind"])
            graph.setdefault(src, []).append((tgt, kind))
        return graph

    async def validate_kind_topology(
        self,
        *,
        source_id: UUID,
        target_id: UUID,
        kind: LinkKind,
        proposed_edges: list[tuple[UUID, UUID, LinkKind]] | None = None,
    ) -> None:
        """Raise TopologyError if the proposed link violates per-kind rules.

        Rules per kind (Slice 3 PR2):

        - DAISY_CHAIN: linear-only. The source may have at most one
          outgoing DAISY_CHAIN edge and the target may have at most
          one incoming DAISY_CHAIN edge. A node cannot appear in
          multiple positions of a daisy chain.
        - HIERARCHICAL: parent/child acyclic tree. Cycle detection
          already enforces acyclicity; here we additionally enforce
          that the target has no other HIERARCHICAL parent and the
          source has no other HIERARCHICAL child for this slot
          (i.e., a node has at most one HIERARCHICAL parent).
        - FEEDBACK: peer-only. The source and target must NOT have an
          ancestor / descendant relationship in the HIERARCHICAL
          subgraph (neither is the parent/child of the other in
          any depth).
        - SHADOW: read-only mirror. A SHADOW target cannot itself be
          a source of any non-SHADOW link (the shadow mirror must
          stay passive).

        ``proposed_edges`` is an optional batch of edges that the
        caller is about to commit (used by bulk_create); when given,
        those edges are merged with the persisted graph for
        validation.
        """
        # Build a working graph.
        persisted = await self.create_closed_loop_pairwise_graph_with_kinds()
        if proposed_edges:
            for src, tgt, k in proposed_edges:
                persisted.setdefault(src, []).append((tgt, k))

        # Short-circuit on self-loop; cycle detection handles this
        # already and the per-kind rules only add structure.
        if source_id == target_id:
            return

        if kind is LinkKind.DAISY_CHAIN:
            # Source may have at most one outgoing DAISY_CHAIN.
            outgoing = persisted.get(source_id, [])
            existing_daisy_out = [
                tgt for tgt, k in outgoing if k is LinkKind.DAISY_CHAIN
            ]
            if existing_daisy_out:
                raise TopologyError(
                    rule="daisy_chain_single_outgoing",
                    kind=kind.value,
                    offenders=[source_id, *existing_daisy_out],
                    message=(
                        f"DAISY_CHAIN source {source_id} already has "
                        f"{len(existing_daisy_out)} downstream DAISY_CHAIN "
                        "link(s); only one is allowed (linear chain)."
                    ),
                )
            # Target may have at most one incoming DAISY_CHAIN.
            for src, edges in persisted.items():
                for tgt, k in edges:
                    if tgt == target_id and k is LinkKind.DAISY_CHAIN:
                        raise TopologyError(
                            rule="daisy_chain_single_incoming",
                            kind=kind.value,
                            offenders=[target_id, src],
                            message=(
                                f"DAISY_CHAIN target {target_id} already "
                                f"has an incoming DAISY_CHAIN link from "
                                f"{src}; only one is allowed."
                            ),
                        )

        elif kind is LinkKind.HIERARCHICAL:
            # Target may have at most one HIERARCHICAL parent.
            for src, edges in persisted.items():
                for tgt, k in edges:
                    if tgt == target_id and k is LinkKind.HIERARCHICAL:
                        raise TopologyError(
                            rule="hierarchical_single_parent",
                            kind=kind.value,
                            offenders=[target_id, src],
                            message=(
                                f"HIERARCHICAL target {target_id} already "
                                f"has a HIERARCHICAL parent {src}; each node "
                                "may have at most one parent."
                            ),
                        )

        elif kind is LinkKind.FEEDBACK:
            # Source and target must be peers (no ancestor/descendant
            # relationship through HIERARCHICAL edges).
            hier = hierarchical_closure(persisted)
            for a, b in (
                (source_id, target_id),
                (target_id, source_id),
            ):
                if b in hier.get(a, set()):
                    raise TopologyError(
                        rule="feedback_peer_only",
                        kind=kind.value,
                        offenders=[source_id, target_id],
                        message=(
                            f"FEEDBACK link between {source_id} and "
                            f"{target_id} violates peer-only rule "
                            "(ancestor/descendant relationship exists)."
                        ),
                    )

        elif kind is LinkKind.SHADOW:
            # SHADOW target must not itself be a source of any
            # non-SHADOW link (the shadow mirror is passive).
            for tgt, k in persisted.get(target_id, []):
                if k is not LinkKind.SHADOW:
                    raise TopologyError(
                        rule="shadow_target_is_passive",
                        kind=kind.value,
                        offenders=[target_id, tgt],
                        message=(
                            f"SHADOW target {target_id} already drives a "
                            f"non-SHADOW link to {tgt}; SHADOW mirrors "
                            "must be read-only."
                        ),
                    )
        # The mirror itself (source of a non-SHADOW link) must not be a
        # SHADOW target of another node: SHADOW targets stay passive.
        if kind is not LinkKind.SHADOW:
            for src, edges in persisted.items():
                for tgt, k in edges:
                    if tgt == source_id and k is LinkKind.SHADOW:
                        raise TopologyError(
                            rule="shadow_target_is_passive",
                            kind=kind.value,
                            offenders=[source_id, src],
                            message=(
                                f"Non-SHADOW source {source_id} is itself a "
                                f"SHADOW target of {src}; SHADOW mirrors "
                                "must be read-only and cannot drive links."
                            ),
                        )

    async def detect_cycle(
        self, source_id: UUID, target_id: UUID
    ) -> list[UUID]:
        """Return the cycle chain if adding source -> target would close a cycle.

        Walks the existing forward adjacency starting from ``target_id``;
        if ``source_id`` is reachable from there, the proposed link would
        close a cycle. Returns the visited-node chain that demonstrates
        it (target_id, ..., source_id). Empty list means the link is safe.

        Self-loops (source_id == target_id) are reported immediately as
        a 1-node cycle.
        """
        if source_id == target_id:
            return [source_id]
        graph = await self.create_closed_loop_pairwise_graph()
        visited: set[UUID] = set()
        parents: dict[UUID, UUID | None] = {}
        queue: list[UUID] = [target_id]
        visited.add(target_id)
        parents[target_id] = None
        while queue:
            current = queue.pop(0)
            neighbours = graph.get(current, [])
            for nbr in neighbours:
                if nbr == source_id:
                    chain: list[UUID] = [source_id]
                    cursor: UUID | None = current
                    if cursor is not None:
                        chain.insert(0, cursor)
                        cursor = parents[cursor]
                    while cursor is not None:
                        chain.insert(0, cursor)
                        cursor = parents[cursor]
                    # Close the cycle by appending target_id (the
                    # proposed source->target edge would close it back).
                    if chain[-1] != target_id:
                        chain.append(target_id)
                    return chain
                if nbr not in visited:
                    visited.add(nbr)
                    parents[nbr] = current
                    queue.append(nbr)
        return []

    async def find_link_path(
        self, source_id: UUID, target_id: UUID
    ) -> list[UUID]:
        """BFS the link graph to find the shortest path source -> target."""
        if source_id == target_id:
            return [source_id]
        graph = await self.create_closed_loop_pairwise_graph()
        parents: dict[UUID, UUID | None] = {source_id: None}
        visited: set[UUID] = {source_id}
        queue: list[UUID] = [source_id]
        while queue:
            current = queue.pop(0)
            for nbr in graph.get(current, []):
                if nbr in visited:
                    continue
                parents[nbr] = current
                if nbr == target_id:
                    chain: list[UUID] = [target_id]
                    cursor: UUID | None = current
                    while cursor is not None:
                        chain.insert(0, cursor)
                        cursor = parents[cursor]
                    return chain
                visited.add(nbr)
                queue.append(nbr)
        return []

    async def topology_view(self) -> list[ClosedLoopLink]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT payload FROM closed_loop_link ORDER BY created_at"
            ) as cur:
                rows = await cur.fetchall()
        return [ClosedLoopLink.model_validate_json(r["payload"]) for r in rows]

    async def list_links_from(self, node_id: UUID) -> list[ClosedLoopLink]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT payload FROM closed_loop_link WHERE source_id = ?",
                (str(node_id),),
            ) as cur:
                rows = await cur.fetchall()
        return [ClosedLoopLink.model_validate_json(r["payload"]) for r in rows]

    async def list_links_to(self, node_id: UUID) -> list[ClosedLoopLink]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT payload FROM closed_loop_link WHERE target_id = ?",
                (str(node_id),),
            ) as cur:
                rows = await cur.fetchall()
        return [ClosedLoopLink.model_validate_json(r["payload"]) for r in rows]

    async def bulk_create_closed_loop_links(
        self, links: list[ClosedLoopLink]
    ) -> list[ClosedLoopLink]:
        """All-or-nothing bulk insert with cycle validation across the batch."""
        if not links:
            return []
        for i, link in enumerate(links):
            src, tgt = link.source.id, link.target.id
            if src == tgt:
                raise CycleError(
                    cycle=[src],
                    message=(
                        f"Link index {i} ({link.id}) is a self-loop: "
                        f"source and target are the same loop."
                    ),
                )
        existing = await self.create_closed_loop_pairwise_graph()
        proposed: list[tuple[UUID, UUID, LinkKind]] = []
        for i, link in enumerate(links):
            src, tgt = link.source.id, link.target.id
            merged = {k: list(v) for k, v in existing.items()}
            for prev in links[:i]:
                merged.setdefault(prev.source.id, []).append(prev.target.id)
            cycle_chain = self._detect_cycle_in_graph(src, tgt, merged)
            if cycle_chain:
                raise CycleError(
                    cycle=cycle_chain,
                    message=(
                        f"Link index {i} ({link.id}) would close a cycle "
                        "with the existing link graph."
                    ),
                )
            # Per-kind topology rules: validate against the persisted
            # graph + the proposed edges accepted so far.
            await self.validate_kind_topology(
                source_id=src,
                target_id=tgt,
                kind=link.kind,
                proposed_edges=proposed,
            )
            proposed.append((src, tgt, link.kind))
        now = datetime.now(UTC)
        async with aiosqlite.connect(self.db_path) as db:
            for link in links:
                await db.execute(
                    "INSERT INTO closed_loop_link (id, payload, source_id, target_id, kind, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        str(link.id),
                        link.model_dump_json(),
                        str(link.source.id),
                        str(link.target.id),
                        link.kind.value,
                        now.isoformat(),
                    ),
                )
            await db.commit()
        return links

    @staticmethod
    def _detect_cycle_in_graph(
        source_id: UUID,
        target_id: UUID,
        graph: dict[UUID, list[UUID]],
    ) -> list[UUID]:
        if source_id == target_id:
            return [source_id]
        visited: set[UUID] = set()
        parents: dict[UUID, UUID | None] = {}
        queue: list[UUID] = [target_id]
        visited.add(target_id)
        parents[target_id] = None
        while queue:
            current = queue.pop(0)
            for nbr in graph.get(current, []):
                if nbr == source_id:
                    chain: list[UUID] = [source_id]
                    cursor: UUID | None = current
                    if cursor is not None:
                        chain.insert(0, cursor)
                        cursor = parents[cursor]
                    while cursor is not None:
                        chain.insert(0, cursor)
                        cursor = parents[cursor]
                    if chain[-1] != target_id:
                        chain.append(target_id)
                    return chain
                if nbr not in visited:
                    visited.add(nbr)
                    parents[nbr] = current
                    queue.append(nbr)
        return []

    async def create_closed_loop_link(self, link: ClosedLoopLink) -> ClosedLoopLink:
        """Insert a single link; raise on cycle or topology rule violation."""
        cycle = await self.detect_cycle(link.source.id, link.target.id)
        if cycle:
            raise CycleError(
                cycle=cycle,
                message=(
                    f"Link {link.id} would close a cycle in the existing "
                    "link graph."
                ),
            )
        await self.validate_kind_topology(
            source_id=link.source.id,
            target_id=link.target.id,
            kind=link.kind,
        )
        now = datetime.now(UTC)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO closed_loop_link (id, payload, source_id, target_id, kind, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    str(link.id),
                    link.model_dump_json(),
                    str(link.source.id),
                    str(link.target.id),
                    link.kind.value,
                    now.isoformat(),
                ),
            )
            await db.commit()
        return link

    async def get_closed_loop_link(self, link_id: UUID) -> ClosedLoopLink:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT payload FROM closed_loop_link WHERE id = ?", (str(link_id),)
            ) as cur:
                row = await cur.fetchone()
        if row is None:
            raise NotFoundError(f"ClosedLoopLink {link_id} not found")
        return ClosedLoopLink.model_validate_json(row["payload"])

    async def list_closed_loop_links(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        source_id: UUID | None = None,
        target_id: UUID | None = None,
        kind: str | None = None,
    ) -> tuple[list[ClosedLoopLink], int]:
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 1
        if page_size > 100:
            page_size = 100
        offset = (page - 1) * page_size
        where_clauses: list[str] = []
        params: list[Any] = []
        if source_id is not None:
            where_clauses.append("source_id = ?")
            params.append(str(source_id))
        if target_id is not None:
            where_clauses.append("target_id = ?")
            params.append(str(target_id))
        if kind is not None:
            where_clauses.append("kind = ?")
            params.append(kind)
        where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                f"SELECT COUNT(*) AS c FROM closed_loop_link{where_sql}", params
            ) as cur:
                total_row = await cur.fetchone()
                total = int(total_row["c"]) if total_row else 0
            async with db.execute(
                f"SELECT payload FROM closed_loop_link{where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?",
                [*params, page_size, offset],
            ) as cur:
                rows = await cur.fetchall()
        items = [ClosedLoopLink.model_validate_json(r["payload"]) for r in rows]
        return items, total

    async def delete_closed_loop_link(self, link_id: UUID) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "DELETE FROM closed_loop_link WHERE id = ?", (str(link_id),)
            )
            await db.commit()
            if cur.rowcount == 0:
                raise NotFoundError(f"ClosedLoopLink {link_id} not found")

    # --- Cross-resource lifecycle constraints (PR2) ---------------------------

    async def _activities_referenced_by_workflows(
        self, activity_ids: list[UUID]
    ) -> dict[UUID, list[dict[str, object]]]:
        """For each activity id, return the workflows (id + name + path) that reference it.

        Scans the ``workflow`` table's payload blobs for ``activities[].id``
        matches; the cost is fine for the MVP SQLite store and avoids
        maintaining a separate junction table.
        """
        if not activity_ids:
            return {}
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT id, payload FROM workflow") as cur:
                rows = await cur.fetchall()
        found: dict[UUID, list[dict[str, object]]] = {a: [] for a in activity_ids}
        targets = {str(a) for a in activity_ids}
        for row in rows:
            workflow = Workflow.model_validate_json(row["payload"])
            for ref in workflow.activities:
                if str(ref.id) in targets:
                    found[UUID(str(ref.id))].append(
                        {
                            "id": row["id"],
                            "name": workflow.name,
                            "lifecycleState": workflow.lifecycleState.value,
                            "path": workflow.path.value,
                        }
                    )
        return found

    async def _workflows_referenced_by_closed_loops(
        self, workflow_ids: list[UUID]
    ) -> dict[UUID, list[dict[str, object]]]:
        """For each workflow id, return the closed loops (id + name + state) that reference it."""
        if not workflow_ids:
            return {}
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT id, payload FROM closed_loop") as cur:
                rows = await cur.fetchall()
        found: dict[UUID, list[dict[str, object]]] = {w: [] for w in workflow_ids}
        targets = {str(w) for w in workflow_ids}
        for row in rows:
            loop = ClosedLoop.model_validate_json(row["payload"])
            for ref in loop.workflows:
                if str(ref.id) in targets:
                    found[UUID(str(ref.id))].append(
                        {
                            "id": row["id"],
                            "name": loop.name,
                            "state": loop.state.value,
                        }
                    )
        return found

    async def assert_workflow_can_be_published(self, workflow_id: UUID) -> None:
        """raise LifecycleConstraintError if any referenced activity is not yet published."""
        workflow = await self.get_workflow(workflow_id)
        if not workflow.activities:
            return
        ids = [ref.id for ref in workflow.activities]
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            placeholders = ",".join("?" for _ in ids)
            async with db.execute(
                f"SELECT id, payload FROM activity WHERE id IN ({placeholders})",
                [str(i) for i in ids],
            ) as cur:
                rows = await cur.fetchall()
        conflicts: list[dict[str, object]] = []
        for row in rows:
            activity = Activity.model_validate_json(row["payload"])
            if activity.lifecycleState not in _PUBLISHED_OR_HIGHER:
                conflicts.append(
                    {
                        "id": row["id"],
                        "name": activity.name,
                        "activityType": activity.activityType.value,
                        "lifecycleState": activity.lifecycleState.value,
                    }
                )
        if conflicts:
            raise LifecycleConstraintError(
                message=(
                    f"Cannot publish workflow {workflow_id}: "
                    f"{len(conflicts)} referenced activit"
                    f"{'y' if len(conflicts) == 1 else 'ies'} not yet published."
                ),
                conflicts=conflicts,
            )

    async def assert_activity_can_be_retired(self, activity_id: UUID) -> None:
        """raise LifecycleConstraintError if any published workflow still references the activity."""
        references = await self._activities_referenced_by_workflows([activity_id])
        # Filter to published-or-higher workflows only.
        published_refs = [
            ref for ref in references.get(activity_id, []) if ref["lifecycleState"] in (
                ActivityLifecycleState.PUBLISHED.value,
                ActivityLifecycleState.DEPRECATED.value,
            )
        ]
        if published_refs:
            raise LifecycleConstraintError(
                message=(
                    f"Cannot retire activity {activity_id}: still referenced by "
                    f"{len(published_refs)} published workflow"
                    f"{'s' if len(published_refs) != 1 else ''}."
                ),
                conflicts=published_refs,
            )

    async def assert_activity_can_be_deleted(self, activity_id: UUID) -> None:
        """raise LifecycleConstraintError if any workflow references the activity."""
        references = await self._activities_referenced_by_workflows([activity_id])
        all_refs = references.get(activity_id, [])
        if all_refs:
            raise LifecycleConstraintError(
                message=(
                    f"Cannot delete activity {activity_id}: still referenced by "
                    f"{len(all_refs)} workflow"
                    f"{'s' if len(all_refs) != 1 else ''}."
                ),
                conflicts=all_refs,
            )

    async def assert_workflow_can_be_deleted(self, workflow_id: UUID) -> None:
        """raise LifecycleConstraintError if any closed loop references the workflow."""
        references = await self._workflows_referenced_by_closed_loops([workflow_id])
        all_refs = references.get(workflow_id, [])
        if all_refs:
            raise LifecycleConstraintError(
                message=(
                    f"Cannot delete workflow {workflow_id}: still referenced by "
                    f"{len(all_refs)} closed loop"
                    f"{'s' if len(all_refs) != 1 else ''}."
                ),
                conflicts=all_refs,
            )

    async def aggregate_closed_loop_goals(
        self, loop_id: UUID
    ) -> dict[str, object]:
        """Aggregate all goals scoped to the closed loop (PR2).

        Includes goals with:
        - ``scope=CLOSED_LOOP`` and ``scopeRef=loop_id``
        - ``scope=WORKFLOW`` and ``scopeRef`` in any of the loop's workflow refs
        - ``scope=ACTIVITY`` and ``scopeRef`` in any of those workflows' activity refs
        - the goal blobs nested inside the ``ClosedLoop.goals`` field

        For each goal, evaluate whether the latest ``currentValue`` satisfies
        the target direction (``AT_LEAST``, ``AT_MOST``, ``EXACTLY``).
        """
        loop = await self.get_closed_loop(loop_id)
        direct_goals: list[Goal] = list(loop.goals)

        # Workflow / activity scopes that contribute to this loop's rollup.
        workflow_ids: set[UUID] = {ref.id for ref in loop.workflows}
        activity_ids: set[UUID] = set()
        for workflow_id in workflow_ids:
            try:
                workflow = await self.get_workflow(workflow_id)
            except NotFoundError:
                continue
            activity_ids.update(ref.id for ref in workflow.activities)

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            # CLOSED_LOOP scoped
            async with db.execute(
                "SELECT payload FROM goal WHERE scope = 'CLOSED_LOOP' "
                "AND json_extract(payload, '$.scopeRef') = ?",
                (str(loop_id),),
            ) as cur:
                closed_loop_goals = [
                    Goal.model_validate_json(r["payload"]) for r in await cur.fetchall()
                ]
            # WORKFLOW scoped
            workflow_scoped_rows: list[Goal] = []
            if workflow_ids:
                placeholders = ",".join("?" for _ in workflow_ids)
                async with db.execute(
                    f"SELECT payload FROM goal WHERE scope = 'WORKFLOW' "
                    f"AND json_extract(payload, '$.scopeRef') IN ({placeholders})",
                    [str(w) for w in workflow_ids],
                ) as cur:
                    workflow_scoped_rows = [
                        Goal.model_validate_json(r["payload"]) for r in await cur.fetchall()
                    ]
            # ACTIVITY scoped
            activity_scoped_rows: list[Goal] = []
            if activity_ids:
                placeholders = ",".join("?" for _ in activity_ids)
                async with db.execute(
                    f"SELECT payload FROM goal WHERE scope = 'ACTIVITY' "
                    f"AND json_extract(payload, '$.scopeRef') IN ({placeholders})",
                    [str(a) for a in activity_ids],
                ) as cur:
                    activity_scoped_rows = [
                        Goal.model_validate_json(r["payload"]) for r in await cur.fetchall()
                    ]

        # Deduplicate by goal id, keeping the row from the deepest scope.
        by_id: dict[UUID, Goal] = {}
        for goal in (
            *direct_goals,
            *closed_loop_goals,
            *workflow_scoped_rows,
            *activity_scoped_rows,
        ):
            by_id[goal.id] = goal

        # Achievement evaluation.
        achieved_count = 0
        for goal in by_id.values():
            if goal.currentValue is None:
                continue
            target_value = goal.target.value
            direction = goal.target.direction
            if direction == GoalDirection.AT_LEAST:
                satisfied = goal.currentValue >= target_value
            elif direction == GoalDirection.AT_MOST:
                satisfied = goal.currentValue <= target_value
            else:  # EXACTLY
                satisfied = goal.currentValue == target_value
            if satisfied:
                achieved_count += 1

        total = len(by_id)
        percent = (achieved_count / total * 100.0) if total else 0.0
        return {
            "closedLoopId": loop_id,
            "goalCount": total,
            "achievedCount": achieved_count,
            "achievementPercent": round(percent, 2),
            "goals": list(by_id.values()),
        }

    # --- DecisionModel ------------------------------------------------------

    async def create_decision_model(self, payload: DecisionModel) -> DecisionModel:
        now = datetime.now(UTC)
        # Tag the payload with an updated timestamp so subsequent writes are
        # monotonically newer.
        if isinstance(payload, OodaDecisionModel):
            kind = "OODA"
        elif isinstance(payload, MapeDecisionModel):
            kind = "MAPE"
        elif isinstance(payload, CustomDecisionModel):
            kind = "CUSTOM"
        else:  # pragma: no cover - exhaustive
            raise ValueError(f"Unknown decision model type: {type(payload)!r}")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO decision_model (id, payload, kind, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (
                    str(payload.id),
                    payload.model_dump_json(),
                    kind,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )
            await db.commit()
        return payload

    async def get_decision_model(self, model_id: UUID) -> DecisionModel:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT payload FROM decision_model WHERE id = ?", (str(model_id),)
            ) as cur:
                row = await cur.fetchone()
        if row is None:
            raise NotFoundError(f"DecisionModel {model_id} not found")
        return _deserialize_decision_model(row["payload"])

    async def list_decision_models(
        self, *, page: int = 1, page_size: int = 20
    ) -> tuple[list[DecisionModel], int]:
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 1
        if page_size > 100:
            page_size = 100
        offset = (page - 1) * page_size
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT COUNT(*) AS c FROM decision_model") as cur:
                total_row = await cur.fetchone()
                total = int(total_row["c"]) if total_row else 0
            async with db.execute(
                "SELECT payload FROM decision_model ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (page_size, offset),
            ) as cur:
                rows = await cur.fetchall()
        items = [_deserialize_decision_model(r["payload"]) for r in rows]
        return items, total

    async def delete_decision_model(self, model_id: UUID) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "DELETE FROM decision_model WHERE id = ?", (str(model_id),)
            )
            await db.commit()
            if cur.rowcount == 0:
                raise NotFoundError(f"DecisionModel {model_id} not found")


def _deserialize_decision_model(payload: str) -> DecisionModel:
    raw: dict[str, Any] = json.loads(payload)
    kind = raw.get("kind")
    if kind == "OODA":
        return OodaDecisionModel.model_validate(raw)
    if kind == "MAPE":
        return MapeDecisionModel.model_validate(raw)
    if kind == "CUSTOM":
        return CustomDecisionModel.model_validate(raw)
    raise ValueError(f"Unknown decision model kind: {kind!r}")


__all__ = [
    "CycleError",
    "LifecycleConstraintError",
    "NotFoundError",
    "StateTransitionError",
    "Store",
]