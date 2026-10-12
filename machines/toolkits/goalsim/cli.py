"""CLAM goal simulation toolkit (Slice 7 PR1).

Loads a closed loop from a JSON spec (decision model + goals),
projects KPI / goal achievement over N ticks using a
configurable decision model kind (OODA / MAPE / CUSTOM),
and prints a per-tick achievement table.

The simulator drives the canonical state path for the chosen
decision model kind:

- OODA: designed -> validated -> published -> active ->
  paused -> active (oscillating maintenance loop).
- MAPE: designed -> validated -> published -> active ->
  paused -> active (monitor/analyze/plan/execute cycle).
- CUSTOM: designed -> validated -> published -> active ->
  retired (one-shot lifecycle).

At each tick the simulator advances the loop state by one
step, applies a tick-rate of goal achievement (a fraction
of the total goals that flips from pending to achieved
once the loop reaches `active`), and emits a per-tick
table. Output is JSON Lines to ``--trace`` for downstream
consumers.

CLI usage::

    clam-goalsim --spec loops.json --loop-id my-loop \\
        --kind OODA --ticks 20 --trace goalsim.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

__all__ = [
    "TickResult",
    "GoalSimSpec",
    "simulate",
    "render_report",
    "main",
]


_STATE_PATHS: dict[str, list[str]] = {
    "OODA": ["designed", "validated", "published", "active", "paused", "active"],
    "MAPE": ["designed", "validated", "published", "active", "paused", "active"],
    "CUSTOM": ["designed", "validated", "published", "active", "retired"],
}

_TERMINAL_STATES = frozenset({"retired", "error"})


@dataclass
class GoalSimSpec:
    """In-memory spec for a goalsim run.

    ``goals`` is the total goal count for the loop;
    ``achieved_per_tick_active`` is the number of goals that
    flip from pending to achieved on every tick where the
    loop is in the ``active`` state.
    """

    loop_id: str
    decision_model_kind: str
    goals: int
    achieved_per_tick_active: int = 1
    starting_state: str = "designed"


@dataclass
class TickResult:
    """One tick of the goalsim run."""

    tick: int
    state: str
    achieved: int
    pending: int
    achievement_percent: float
    transition_event: str  # "advance" | "oscillate" | "retire" | "halt"
    ts: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


def _load_spec(path: Path, loop_id: str) -> GoalSimSpec:
    """Load a spec file and return one GoalSimSpec for ``loop_id``."""
    data = json.loads(path.read_text())
    if isinstance(data, list):
        for entry in data:
            if entry.get("loopId") == loop_id:
                data = entry
                break
        else:
            raise KeyError(f"loop_id {loop_id!r} not found in spec")
    if data.get("loopId") != loop_id:
        raise KeyError(f"loop_id {loop_id!r} not found in spec")
    kind = data.get("decisionModelKind", "CUSTOM")
    goals = int(data.get("goals", 0))
    per_tick = int(data.get("achievedPerTickActive", 1))
    starting = data.get("startingState", "designed")
    return GoalSimSpec(
        loop_id=loop_id,
        decision_model_kind=kind,
        goals=goals,
        achieved_per_tick_active=per_tick,
        starting_state=starting,
    )


def _next_state(
    current: str, path: list[str]
) -> tuple[str, str]:
    """Return ``(next_state, event)``.

    event is one of ``advance`` / ``oscillate`` / ``retire`` /
    ``halt``. ``retire`` and ``halt`` mean the run ends at this
    tick; callers should stop further simulation.
    """
    if current in _TERMINAL_STATES:
        return current, "halt"
    if current not in path:
        return path[0], "advance"
    idx = path.index(current)
    nxt = path[(idx + 1) % len(path)]
    if nxt == path[0]:
        event = "retire" if len(path) <= 1 else "oscillate"
    elif nxt in _TERMINAL_STATES:
        event = "retire"
    else:
        event = "advance"
    return nxt, event


def simulate(spec: GoalSimSpec, ticks: int) -> list[TickResult]:
    """Run the goalsim for ``ticks`` ticks and return one TickResult each."""
    path = _STATE_PATHS.get(spec.decision_model_kind)
    if path is None:
        raise ValueError(
            f"Unknown decision model kind {spec.decision_model_kind!r}; "
            f"valid kinds: {sorted(_STATE_PATHS)}"
        )
    achieved = 0
    state = spec.starting_state
    out: list[TickResult] = []
    for tick in range(ticks):
        if state in _TERMINAL_STATES:
            event = "halt"
        else:
            state, event = _next_state(state, path)
            if state == "active" and spec.achieved_per_tick_active:
                achieved = min(
                    spec.goals, achieved + spec.achieved_per_tick_active
                )
        pending = max(0, spec.goals - achieved)
        percent = (achieved / spec.goals * 100.0) if spec.goals else 0.0
        out.append(
            TickResult(
                tick=tick,
                state=state,
                achieved=achieved,
                pending=pending,
                achievement_percent=round(percent, 2),
                transition_event=event,
            )
        )
        if event in {"retire", "halt"}:
            break
    return out


def render_report(results: Iterable[TickResult], spec: GoalSimSpec) -> str:
    """Render a human-readable table."""
    rows = list(results)
    lines = [
        f"# Goal simulation: loop={spec.loop_id} kind={spec.decision_model_kind} "
        f"goals={spec.goals}",
        "",
        "| tick | state | achieved | pending | achievement% | event |",
        "| ---- | ----- | -------- | ------- | ------------- | ----- |",
    ]
    for r in rows:
        lines.append(
            f"| {r.tick} | {r.state} | {r.achieved} | {r.pending} "
            f"| {r.achievement_percent} | {r.transition_event} |"
        )
    if rows:
        final = rows[-1]
        lines.append("")
        lines.append(
            f"final state={final.state} achieved={final.achieved}/{spec.goals} "
            f"({final.achievement_percent}%) over {len(rows)} tick(s)"
        )
    return "\n".join(lines) + "\n"


def _log(trace: Path | None, payload: dict[str, Any]) -> None:
    if trace is None:
        return
    payload.setdefault("ts", datetime.now(UTC).isoformat())
    with trace.open("a") as f:
        f.write(json.dumps(payload) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--loop-id", required=True)
    parser.add_argument(
        "--kind",
        choices=sorted(_STATE_PATHS),
        default=None,
        help="Override decision model kind (defaults to spec)",
    )
    parser.add_argument("--ticks", type=int, default=10)
    parser.add_argument(
        "--trace", type=Path, default=None, help="Optional JSONL trace output"
    )
    parser.add_argument(
        "--format",
        choices=("table", "json"),
        default="table",
        help="Output format (default: table)",
    )
    args = parser.parse_args()

    spec = _load_spec(args.spec, args.loop_id)
    if args.kind is not None:
        spec = GoalSimSpec(
            loop_id=spec.loop_id,
            decision_model_kind=args.kind,
            goals=spec.goals,
            achieved_per_tick_active=spec.achieved_per_tick_active,
            starting_state=spec.starting_state,
        )

    results = simulate(spec, ticks=args.ticks)
    if args.trace is not None:
        # Truncate the trace file at the start of the run.
        args.trace.write_text("")
        for r in results:
            _log(
                args.trace,
                {"event": "tick", **asdict(r)},
            )

    if args.format == "json":
        json.dump(
            {
                "loopId": spec.loop_id,
                "kind": spec.decision_model_kind,
                "ticks": [asdict(r) for r in results],
            },
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_report(results, spec))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())