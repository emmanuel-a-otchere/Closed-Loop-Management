"""KPI calculator.

Reads a JSONL trace produced by ``clam-loop-simulator`` and emits a
human-readable KPI report.

The report includes:

- Total events
- Total transitions (excluding rejections and halts)
- Transition matrix (from -> to counts)
- Average state residence (when timestamps are present)
- Error / retired counts

CLI usage::

    clam-kpi-calculator --in loop-trace.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


def _parse_ts(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def report(trace: Path) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    with trace.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    transitions = [e for e in events if e.get("event") == "transition"]
    rejections = [e for e in events if e.get("event") == "transition-rejected"]
    halts = [e for e in events if e.get("event") == "halt"]

    matrix: Counter[tuple[str, str]] = Counter()
    for t in transitions:
        matrix[(t["from"], t["to"])] += 1

    residences: list[float] = []
    last_ts: datetime | None = None
    last_state: str | None = None
    for t in transitions:
        ts = _parse_ts(t.get("ts"))
        if ts and last_ts and last_state:
            residences.append((ts - last_ts).total_seconds())
        last_ts = ts
        last_state = t.get("to")

    error_count = sum(matrix.get((src, "error"), 0) for src in [k[0] for k in matrix])
    retired_count = sum(matrix.get((src, "retired"), 0) for src in [k[0] for k in matrix])

    return {
        "total_events": len(events),
        "total_transitions": len(transitions),
        "total_rejections": len(rejections),
        "total_halts": len(halts),
        "transition_matrix": [
            {"from": k[0], "to": k[1], "count": v} for k, v in sorted(matrix.items())
        ],
        "mean_state_residence_seconds": (
            round(sum(residences) / len(residences), 2) if residences else None
        ),
        "transitions_to_error": error_count,
        "transitions_to_retired": retired_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="trace", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=None, help="write JSON report here")
    args = parser.parse_args()

    if not args.trace.exists():
        print(f"trace not found: {args.trace}", file=sys.stderr)
        return 2

    result = report(args.trace)
    text = json.dumps(result, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
        print(f"Wrote KPI report to {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())