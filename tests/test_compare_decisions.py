"""Tests for the compare-decisions toolkit (Slice 7 PR2)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from machines.toolkits.compare_decisions import (
    CompareResult,
    compare,
    render_comparison,
)
from machines.toolkits.compare_decisions.cli import main
from machines.toolkits.goalsim import GoalSimSpec


def _run_cli(args: list[str]) -> int:
    saved = sys.argv
    sys.argv = ["clam-compare-decisions", *args]
    try:
        return main()
    finally:
        sys.argv = saved


# --- Pure-function tests ----------------------------------------------------


def test_compare_ooda_vs_mape_yields_same_trajectory() -> None:
    """OODA and MAPE share the same state path, so their
    trajectories match tick-for-tick (state-machine level)."""
    spec = GoalSimSpec(
        loop_id="x",
        decision_model_kind="OODA",
        goals=4,
        achieved_per_tick_active=1,
    )
    result_ooda, result_mape = compare(
        spec=spec, kind_a="OODA", kind_b="MAPE", ticks=8
    )
    ooda_states = [t["state"] for t in result_ooda.trajectory]
    mape_states = [t["state"] for t in result_mape.trajectory]
    assert ooda_states == mape_states
    # Ticks-to-active is identical (first active tick at index 2).
    assert result_ooda.ticks_to_active == 2
    assert result_mape.ticks_to_active == 2


def test_compare_ooda_vs_custom_yields_different_paths() -> None:
    """OODA oscillates; CUSTOM one-shots to retired."""
    spec = GoalSimSpec(
        loop_id="x",
        decision_model_kind="OODA",
        goals=5,
    )
    result_ooda, result_custom = compare(
        spec=spec, kind_a="OODA", kind_b="CUSTOM", ticks=10
    )
    assert result_ooda.final_state in {"active", "paused"}
    assert result_custom.final_state == "retired"
    # OODA runs the full tick budget (still oscillating), so
    # its trajectory length is at least as long as CUSTOM's.
    assert len(result_ooda.trajectory) >= len(result_custom.trajectory)


def test_compare_ticks_to_active_when_starting_active() -> None:
    """If the spec starts at active, the goalsim advances the
    state on tick 0 (active -> paused); the next 'active'
    tick is the second transition. ``ticks_to_active``
    surfaces that second tick.
    """
    spec = GoalSimSpec(
        loop_id="x",
        decision_model_kind="OODA",
        goals=1,
        starting_state="active",
    )
    result_a, result_b = compare(
        spec=spec, kind_a="OODA", kind_b="MAPE", ticks=2
    )
    # active at tick 1.
    assert result_a.ticks_to_active == 1
    assert result_b.ticks_to_active == 1


def test_compare_ticks_to_active_none_when_never_reached() -> None:
    """If the tick budget ends before 'active' is reached,
    ticks_to_active is None."""
    spec = GoalSimSpec(
        loop_id="x",
        decision_model_kind="OODA",
        goals=1,
        starting_state="designed",
    )
    # 2 ticks: designed -> validated -> published (still no active).
    result_a, _ = compare(
        spec=spec, kind_a="OODA", kind_b="MAPE", ticks=2
    )
    assert result_a.ticks_to_active is None


def test_compare_zero_ticks_returns_starting_state() -> None:
    """ticks=0 yields a 1-row summary with the starting state."""
    spec = GoalSimSpec(
        loop_id="x",
        decision_model_kind="OODA",
        goals=1,
        starting_state="designed",
    )
    result_a, result_b = compare(
        spec=spec, kind_a="OODA", kind_b="MAPE", ticks=0
    )
    assert result_a.final_state == "designed"
    assert result_a.transition_count == 0
    assert result_a.ticks_to_active is None
    assert result_b.final_state == "designed"


def test_compare_unknown_kind_raises() -> None:
    spec = GoalSimSpec(
        loop_id="x",
        decision_model_kind="OODA",
        goals=1,
    )
    with pytest.raises(ValueError, match="Unknown decision model kind"):
        compare(spec=spec, kind_a="OOPS", kind_b="OODA", ticks=1)


def test_render_comparison_includes_summary_and_trajectory() -> None:
    """render_comparison produces both summary metrics and
    a per-tick trajectory table."""
    spec = GoalSimSpec(
        loop_id="loop-1",
        decision_model_kind="OODA",
        goals=2,
    )
    result_a, result_b = compare(
        spec=spec, kind_a="OODA", kind_b="CUSTOM", ticks=8
    )
    rendered = render_comparison(result_a, result_b, loop_id="loop-1")
    assert "# Decision model comparison: loop=loop-1" in rendered
    assert "| final state |" in rendered
    assert "| transitions |" in rendered
    assert "| ticks to active |" in rendered
    assert "## Trajectories" in rendered
    assert f"| {result_a.kind} | {result_b.kind} |" in rendered


def test_compare_result_to_dict_round_trips() -> None:
    """to_dict + CompareResult(**...) round-trips cleanly."""
    spec = GoalSimSpec(
        loop_id="x",
        decision_model_kind="OODA",
        goals=1,
    )
    result_a, _ = compare(
        spec=spec, kind_a="OODA", kind_b="MAPE", ticks=4
    )
    payload = result_a.to_dict()
    rebuilt = CompareResult(**payload)
    assert rebuilt == result_a


# --- CLI tests --------------------------------------------------------------


def test_cli_table_output(tmp_path: Path, capsys) -> None:
    spec = tmp_path / "spec.json"
    spec.write_text(
        json.dumps(
            {
                "loopId": "l1",
                "decisionModelKind": "OODA",
                "goals": 2,
            }
        )
    )
    rc = _run_cli(
        [
            "--spec",
            str(spec),
            "--loop-id",
            "l1",
            "--kind-a",
            "OODA",
            "--kind-b",
            "MAPE",
            "--ticks",
            "4",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "Decision model comparison: loop=l1" in out
    assert "| final state |" in out


def test_cli_json_output(tmp_path: Path, capsys) -> None:
    spec = tmp_path / "spec.json"
    spec.write_text(
        json.dumps(
            {
                "loopId": "l1",
                "decisionModelKind": "OODA",
                "goals": 1,
            }
        )
    )
    rc = _run_cli(
        [
            "--spec",
            str(spec),
            "--loop-id",
            "l1",
            "--kind-a",
            "OODA",
            "--kind-b",
            "CUSTOM",
            "--ticks",
            "5",
            "--format",
            "json",
        ]
    )
    assert rc == 0
    body = json.loads(capsys.readouterr().out)
    assert body["loopId"] == "l1"
    assert "OODA" in body["sides"]
    assert "CUSTOM" in body["sides"]
    # CUSTOM one-shots to retired.
    assert body["sides"]["CUSTOM"]["final_state"] == "retired"


def test_cli_trace_writes_jsonl(tmp_path: Path, capsys) -> None:
    spec = tmp_path / "spec.json"
    spec.write_text(
        json.dumps(
            {
                "loopId": "l1",
                "decisionModelKind": "OODA",
                "goals": 1,
            }
        )
    )
    trace = tmp_path / "compare.jsonl"
    rc = _run_cli(
        [
            "--spec",
            str(spec),
            "--loop-id",
            "l1",
            "--kind-a",
            "OODA",
            "--kind-b",
            "MAPE",
            "--ticks",
            "3",
            "--trace",
            str(trace),
        ]
    )
    assert rc == 0
    lines = [
        line for line in trace.read_text().splitlines() if line.strip()
    ]
    assert len(lines) == 2
    sides = {json.loads(line)["side"]: json.loads(line) for line in lines}
    assert "OODA" in sides
    assert "MAPE" in sides


def test_cli_default_kinds_are_ooda_vs_mape(tmp_path: Path, capsys) -> None:
    spec = tmp_path / "spec.json"
    spec.write_text(
        json.dumps(
            {
                "loopId": "l1",
                "decisionModelKind": "OODA",
                "goals": 1,
            }
        )
    )
    rc = _run_cli(
        [
            "--spec",
            str(spec),
            "--loop-id",
            "l1",
            "--ticks",
            "4",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    # Default kinds are OODA and MAPE.
    assert "| OODA | MAPE |" in out
