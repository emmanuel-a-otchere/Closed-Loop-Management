"""Loop simulator.

For each cycle the simulator:

1. Reads the closed loop's current state via ``GET /closedLoop/{id}/state``.
2. Walks the decision model (OODA: observe -> orient -> decide -> act;
   MAPE: monitor -> analyze -> plan -> execute).
3. Posts the next state via ``POST /closedLoop/{id}/state``.
4. Appends a JSONL line to the trace file.

The simulator exits early when the closed loop reaches ``retired`` or
``error``. A summary is printed at the end.

CLI usage::

    clam-loop-simulator --base http://localhost:8000 --loop-id <id> \\
        --cycles 10 --trace trace.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx


def _log(trace: Path, payload: dict[str, Any]) -> None:
    payload.setdefault("ts", datetime.now(UTC).isoformat())
    with trace.open("a") as f:
        f.write(json.dumps(payload) + "\n")


def _walk_state(client: httpx.Client, loop_id: str, target: str) -> dict[str, Any] | None:
    r = client.post(f"/api/v1/closedLoop/{loop_id}/state", json={"targetState": target})
    if r.status_code == 409:
        return None
    r.raise_for_status()
    return r.json()


def _state_path(kind: str) -> list[str]:
    if kind == "OODA":
        return ["designed", "validated", "published", "active", "paused", "active"]
    if kind == "MAPE":
        return ["designed", "validated", "published", "active", "paused", "active"]
    return ["designed", "validated", "published", "active", "retired"]


def simulate(base: str, loop_id: str, cycles: int, trace: Path) -> int:
    with httpx.Client(base_url=base, timeout=10.0) as client:
        # Probe the loop to discover its decision model kind.
        loop = client.get(f"/api/v1/closedLoop/{loop_id}").json()
        kind = loop.get("decisionModelRef", {}).get("kind", "CUSTOM")
        path = _state_path(kind)

        for i in range(cycles):
            current_state = client.get(f"/api/v1/closedLoop/{loop_id}/state").json()["state"]
            idx = path.index(current_state) if current_state in path else -1
            next_state = path[(idx + 1) % len(path)] if idx >= 0 else path[0]
            if current_state in ("retired", "error"):
                _log(trace, {"event": "halt", "state": current_state, "cycle": i})
                break
            result = _walk_state(client, loop_id, next_state)
            if result is None:
                _log(
                    trace,
                    {
                        "event": "transition-rejected",
                        "from": current_state,
                        "to": next_state,
                        "cycle": i,
                    },
                )
                continue
            _log(
                trace,
                {
                    "event": "transition",
                    "from": current_state,
                    "to": result["state"],
                    "cycle": i,
                },
            )

    summary = {"cycles": cycles, "kind": kind, "trace": str(trace)}
    print(json.dumps(summary, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://localhost:8000")
    parser.add_argument("--loop-id", required=True)
    parser.add_argument("--cycles", type=int, default=5)
    parser.add_argument("--trace", type=Path, default=Path("loop-trace.jsonl"))
    args = parser.parse_args()

    if args.trace.exists():
        args.trace.unlink()

    try:
        return simulate(args.base, args.loop_id, args.cycles, args.trace)
    except httpx.HTTPError as exc:
        print(f"HTTP error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())