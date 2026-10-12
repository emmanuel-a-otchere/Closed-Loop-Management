"""CLAM compare-decisions toolkit (Slice 7 PR2).

Runs the same closed-loop spec through two decision model
kinds (default: OODA vs MAPE) and prints a side-by-side
comparison:

- per-tick state trajectory for each kind
- final state
- transition count
- ticks-to-active

The compare tool reuses the goalsim pure-function API so
both paths are simulated by the same deterministic
state-machine.

CLI usage::

    clam-compare-decisions --spec loop.json --loop-id my-loop \\
        --kind-a OODA --kind-b MAPE --ticks 20 \\
        [--format table|json] [--trace compare.jsonl]
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from machines.toolkits.goalsim import GoalSimSpec, simulate
from machines.toolkits.goalsim.cli import _load_spec

__all__ = [
    "CompareResult",
    "compare",
    "render_comparison",
    "main",
]


@dataclass
class CompareResult:
    """One side of a comparison run (per decision model kind)."""

    kind: str
    final_state: str
    transition_count: int
    ticks_to_active: int | None
    trajectory: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _summarise(kind: str, results: list, starting_state: str) -> CompareResult:
    if not results:
        return CompareResult(
            kind=kind,
            final_state=starting_state,
            transition_count=0,
            ticks_to_active=None,
            trajectory=[],
        )
    ticks_to_active: int | None = None
    for r in results:
        if r.state == "active":
            ticks_to_active = r.tick
            break
    return CompareResult(
        kind=kind,
        final_state=results[-1].state,
        transition_count=len(results),
        ticks_to_active=ticks_to_active,
        trajectory=[
            {
                "tick": r.tick,
                "state": r.state,
                "achieved": r.achieved,
                "achievementPercent": r.achievement_percent,
                "event": r.transition_event,
            }
            for r in results
        ],
    )


def compare(
    *,
    spec: GoalSimSpec,
    kind_a: str,
    kind_b: str,
    ticks: int,
) -> tuple[CompareResult, CompareResult]:
    """Run ``simulate`` twice and return both summaries."""
    spec_a = GoalSimSpec(
        loop_id=spec.loop_id,
        decision_model_kind=kind_a,
        goals=spec.goals,
        achieved_per_tick_active=spec.achieved_per_tick_active,
        starting_state=spec.starting_state,
    )
    spec_b = GoalSimSpec(
        loop_id=spec.loop_id,
        decision_model_kind=kind_b,
        goals=spec.goals,
        achieved_per_tick_active=spec.achieved_per_tick_active,
        starting_state=spec.starting_state,
    )
    results_a = simulate(spec_a, ticks=ticks)
    results_b = simulate(spec_b, ticks=ticks)
    return (
        _summarise(kind_a, results_a, spec.starting_state),
        _summarise(kind_b, results_b, spec.starting_state),
    )


def render_comparison(
    result_a: CompareResult,
    result_b: CompareResult,
    *,
    loop_id: str,
) -> str:
    """Render a side-by-side markdown comparison table."""
    a_str = (
        str(result_a.ticks_to_active)
        if result_a.ticks_to_active is not None
        else "n/a"
    )
    b_str = (
        str(result_b.ticks_to_active)
        if result_b.ticks_to_active is not None
        else "n/a"
    )
    lines = [
        f"# Decision model comparison: loop={loop_id}",
        "",
        f"| metric | {result_a.kind} | {result_b.kind} |",
        "| ------ | -------- | -------- |",
        f"| final state | {result_a.final_state} | {result_b.final_state} |",
        f"| transitions | {result_a.transition_count} | {result_b.transition_count} |",
        f"| ticks to active | {a_str} | {b_str} |",
        "",
        "## Trajectories",
        "",
        f"| tick | {result_a.kind} | {result_b.kind} |",
        "| ---- | " + " | ".join(["----------"] * 2) + " |",
    ]
    n = max(len(result_a.trajectory), len(result_b.trajectory))
    for i in range(n):
        a_state = (
            result_a.trajectory[i]["state"]
            if i < len(result_a.trajectory)
            else "-"
        )
        b_state = (
            result_b.trajectory[i]["state"]
            if i < len(result_b.trajectory)
            else "-"
        )
        lines.append(f"| {i} | {a_state} | {b_state} |")
    lines.append("")
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
    parser.add_argument("--kind-a", default="OODA")
    parser.add_argument("--kind-b", default="MAPE")
    parser.add_argument("--ticks", type=int, default=10)
    parser.add_argument(
        "--trace", type=Path, default=None, help="Optional JSONL trace output"
    )
    parser.add_argument(
        "--format",
        choices=("table", "json"),
        default="table",
    )
    args = parser.parse_args()

    spec = _load_spec(args.spec, args.loop_id)

    result_a, result_b = compare(
        spec=spec,
        kind_a=args.kind_a,
        kind_b=args.kind_b,
        ticks=args.ticks,
    )

    if args.trace is not None:
        args.trace.write_text("")
        _log(
            args.trace,
            {"event": "compare", "side": args.kind_a, **result_a.to_dict()},
        )
        _log(
            args.trace,
            {"event": "compare", "side": args.kind_b, **result_b.to_dict()},
        )

    if args.format == "json":
        json.dump(
            {
                "loopId": spec.loop_id,
                "sides": {
                    args.kind_a: result_a.to_dict(),
                    args.kind_b: result_b.to_dict(),
                },
            },
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        sys.stdout.write(
            render_comparison(result_a, result_b, loop_id=spec.loop_id)
        )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
