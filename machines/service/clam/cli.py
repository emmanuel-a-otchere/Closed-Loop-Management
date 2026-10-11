"""CLI for the CLAM service.

Subcommands:

- ``seed``: populate the SQLite store with the bundled sample data.
- ``topology``: print the persisted closed-loop link topology as JSON.
- ``path``: BFS the link graph to find the shortest path between two
  closed loops.
- ``serve``: run uvicorn against the FastAPI app on the configured host
  and port.

Run ``machines-service --help`` for the full argument matrix.
"""

from __future__ import annotations

import argparse
import asyncio
import json
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


async def _topology(db_path: Path) -> None:
    app = create_app(db_path)
    async with app.router.lifespan_context(app):
        store = app.state.store
        links = await store.topology_view()
    payload = {
        "linkCount": len(links),
        "links": [json.loads(link.model_dump_json()) for link in links],
    }
    print(json.dumps(payload, indent=2))


async def _path(db_path: Path, source: UUID, target: UUID) -> None:
    app = create_app(db_path)
    async with app.router.lifespan_context(app):
        store = app.state.store
        chain = await store.find_link_path(source, target)
    print(json.dumps({"chain": [str(n) for n in chain]}, indent=2))


def _serve(host: str, port: int, db_path: Path) -> None:
    """Start uvicorn against the FastAPI app.

    Imported lazily so the ``--help`` path stays fast and works on
    environments where uvicorn isn't installed (CI lint job).
    """
    import uvicorn

    os.environ.setdefault("CLAM_DB_PATH", str(db_path))
    uvicorn.run(
        "machines.service.clam.main:app",
        host=host,
        port=port,
        log_level="info",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="machines-service",
        description="Command-line interface for the CLAM service.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    seed_cmd = sub.add_parser("seed", help="Seed the SQLite store with sample data.")
    seed_cmd.add_argument(
        "--db-path",
        type=Path,
        default=Path(os.environ.get("CLAM_DB_PATH", "clam.db")),
        help="Path to the SQLite database (default: $CLAM_DB_PATH or clam.db).",
    )

    topo_cmd = sub.add_parser(
        "topology", help="Print the persisted closed-loop link topology."
    )
    topo_cmd.add_argument(
        "--db-path",
        type=Path,
        default=Path(os.environ.get("CLAM_DB_PATH", "clam.db")),
        help="Path to the SQLite database.",
    )

    path_cmd = sub.add_parser(
        "path", help="BFS shortest path between two closed loops."
    )
    path_cmd.add_argument("source", type=UUID, help="Source closed loop UUID.")
    path_cmd.add_argument("target", type=UUID, help="Target closed loop UUID.")
    path_cmd.add_argument(
        "--db-path",
        type=Path,
        default=Path(os.environ.get("CLAM_DB_PATH", "clam.db")),
        help="Path to the SQLite database.",
    )

    serve_cmd = sub.add_parser("serve", help="Run uvicorn against the FastAPI app.")
    serve_cmd.add_argument("--host", default="127.0.0.1", help="Bind host.")
    serve_cmd.add_argument(
        "--port", type=int, default=int(os.environ.get("CLAM_PORT", "8000")),
        help="Bind port (default: $CLAM_PORT or 8000).",
    )
    serve_cmd.add_argument(
        "--db-path",
        type=Path,
        default=Path(os.environ.get("CLAM_DB_PATH", "clam.db")),
        help="Path to the SQLite database.",
    )

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    try:
        if args.command == "seed":
            os.environ["CLAM_DB_PATH"] = str(args.db_path)
            asyncio.run(_seed())
        elif args.command == "topology":
            asyncio.run(_topology(args.db_path))
        elif args.command == "path":
            asyncio.run(_path(args.db_path, args.source, args.target))
        elif args.command == "serve":
            _serve(args.host, args.port, args.db_path)
        else:  # pragma: no cover -- guarded by argparse
            parser.error(f"unknown command {args.command!r}")
            sys.exit(2)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:
        print(f"{args.command} failed: {exc}", file=sys.stderr)
        sys.exit(1)


__all__ = [
    "SAMPLE_MAPE",
    "SAMPLE_OODA",
    "main",
]


if __name__ == "__main__":
    main()
