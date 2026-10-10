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
    ClosedLoop,
    ClosedLoopCreate,
    ClosedLoopState,
    ClosedLoopUpdate,
    CustomDecisionModel,
    DecisionModel,
    MapeDecisionModel,
    OodaDecisionModel,
    StateTransitionRequest,
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

CREATE INDEX IF NOT EXISTS idx_closed_loop_state ON closed_loop(state);
CREATE INDEX IF NOT EXISTS idx_decision_model_kind ON decision_model(kind);
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


class StateTransitionError(Exception):
    """Raised when a state transition is not allowed from the current state."""

    def __init__(self, current: ClosedLoopState, target: ClosedLoopState) -> None:
        self.current = current
        self.target = target
        super().__init__(
            f"Cannot transition closed loop from {current.value} to {target.value}"
        )


class NotFoundError(Exception):
    """Raised when an entity lookup fails."""


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
            raise StateTransitionError(loop.state, request.targetState)
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
    "NotFoundError",
    "StateTransitionError",
    "Store",
]