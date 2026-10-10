"""Tiny CLI to seed the SQLite store with example data."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from uuid import UUID

from .main import create_app
from .models import (
    ActivityRef,
    ClosedLoopCreate,
    DecisionModelKind,
    DecisionModelRef,
    MapeDecisionModel,
    OodaDecisionModel,
)

SAMPLE_OODA = OodaDecisionModel(
    name="sample-ooda",
    observe=ActivityRef(id=UUID("11111111-1111-1111-1111-111111111111"), name="observe"),
    orient=ActivityRef(id=UUID("22222222-2222-2222-2222-222222222222"), name="orient"),
    decide=ActivityRef(id=UUID("33333333-3333-3333-3333-333333333333"), name="decide"),
    act=ActivityRef(id=UUID("44444444-4444-4444-4444-444444444444"), name="act"),
)


SAMPLE_MAPE = MapeDecisionModel(
    name="sample-mape",
    monitor=ActivityRef(id=UUID("55555555-5555-5555-5555-555555555555"), name="monitor"),
    analyze=ActivityRef(id=UUID("66666666-6666-6666-6666-666666666666"), name="analyze"),
    plan=ActivityRef(id=UUID("77777777-7777-7777-7777-777777777777"), name="plan"),
    execute=ActivityRef(id=UUID("88888888-8888-8888-8888-888888888888"), name="execute"),
)


async def _seed() -> None:
    db_path = Path(os.environ.get("CLAM_DB_PATH", "clam.db"))
    app = create_app(db_path)
    async with app.router.lifespan_context(app):
        store = app.state.store
        await store.create_decision_model(SAMPLE_OODA)
        await store.create_decision_model(SAMPLE_MAPE)
        await store.create_closed_loop(
            ClosedLoopCreate(
                name="cpu-thermal-loop",
                description="Closed loop that monitors CPU temperature and adjusts fan speed.",
                decisionModelRef=DecisionModelRef(
                    id=SAMPLE_OODA.id, kind=DecisionModelKind.OODA
                ),
            )
        )
        await store.create_closed_loop(
            ClosedLoopCreate(
                name="memory-pressure-loop",
                description="Closed loop that monitors memory pressure and reclaims pages.",
                decisionModelRef=DecisionModelRef(
                    id=SAMPLE_MAPE.id, kind=DecisionModelKind.MAPE
                ),
            )
        )
    print(f"Seeded {db_path}")


def main() -> None:
    try:
        asyncio.run(_seed())
    except Exception as exc:
        print(f"seed failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


__all__ = ["SAMPLE_OODA", "SAMPLE_MAPE", "main"]