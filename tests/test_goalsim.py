"""Tests for the goalsim toolkit (Slice 7 PR1)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from machines.toolkits.goalsim import (
    GoalSimSpec,
    render_report,
    simulate,
)
from machines.toolkits.goalsim.cli import _load_spec, main


def _run_cli(args: list[str]) -> int:
    """Invoke the CLI main() with a sys.argv override."""
    saved = sys.argv
    sys.argv = ["clam-goalsim", *args]
    try:
        return main()
    finally:
        sys.argv = saved


# --- Pure-function tests ----------------------------------------------------


def test_simulate_ooda_walks_full_path() -> None:
    """OODA oscillates active <-> paused; achievement grows on active ticks."""
    spec = GoalSimSpec(
        loop_id="l1",
        decision_model_kind="OODA",
        goals=10,
        achieved_per_tick_active=1,
    )
    results = simulate(spec, ticks=8)
    states = [r.state for r in results]
    # OODA path: designed, validated, published, active, paused, active, paused, active
    assert states == [
        "validated",
        "published",
        "active",
        "paused",
        "active",
        "paused",
        "active",
        "paused",
    ]
    # Achieved grows by 1 per 'active' tick.
    achieved = [r.achieved for r in results]
    # active ticks at indices 2, 4, 6 -> 1, 2, 3
    assert achieved == [0, 0, 1, 1, 2, 2, 3, 3]


def test_simulate_mape_walks_full_path() -> None:
    """MAPE oscillates the same way as OODA at the state level."""
    spec = GoalSimSpec(
        loop_id="l2",
        decision_model_kind="MAPE",
        goals=5,
        achieved_per_tick_active=1,
    )
    results = simulate(spec, ticks=6)
    states = [r.state for r in results]
    assert states[0] == "validated"
    assert states[2] == "active"
    assert states[3] == "paused"
    assert states[4] == "active"
    assert states[5] == "paused"


def test_simulate_custom_retires() -> None:
    """CUSTOM one-shot lifecycle reaches retired and stops."""
    spec = GoalSimSpec(
        loop_id="l3",
        decision_model_kind="CUSTOM",
        goals=4,
        achieved_per_tick_active=1,
    )
    results = simulate(spec, ticks=20)
    assert len(results) == 4  # validated, published, active, retired
    last = results[-1]
    assert last.state == "retired"
    assert last.transition_event == "retire"
    # Achieved grows while active.
    assert last.achieved == 1


def test_simulate_unknown_kind_raises() -> None:
    spec = GoalSimSpec(
        loop_id="x",
        decision_model_kind="UNKNOWN",
        goals=1,
    )
    with pytest.raises(ValueError, match="Unknown decision model kind"):
        simulate(spec, ticks=1)


def test_simulate_zero_goals_does_not_divide_by_zero() -> None:
    spec = GoalSimSpec(
        loop_id="x",
        decision_model_kind="OODA",
        goals=0,
    )
    results = simulate(spec, ticks=4)
    assert all(r.achievement_percent == 0.0 for r in results)
    assert all(r.achieved == 0 for r in results)


def test_simulate_achievement_caps_at_goal_count() -> None:
    """Achieved cannot exceed the spec's goal count."""
    spec = GoalSimSpec(
        loop_id="x",
        decision_model_kind="CUSTOM",
        goals=2,
        achieved_per_tick_active=10,
    )
    results = simulate(spec, ticks=4)
    final = next(r for r in results if r.state == "retired")
    assert final.achieved == 2
    assert final.pending == 0


def test_simulate_starting_state_honoured() -> None:
    """If the spec starts at published, the first transition is active."""
    spec = GoalSimSpec(
        loop_id="x",
        decision_model_kind="OODA",
        goals=5,
        achieved_per_tick_active=1,
        starting_state="published",
    )
    results = simulate(spec, ticks=1)
    assert results[0].state == "active"


def test_simulate_negative_ticks_returns_empty() -> None:
    """Zero or negative ticks yields no ticks."""
    spec = GoalSimSpec(
        loop_id="x",
        decision_model_kind="OODA",
        goals=5,
    )
    assert simulate(spec, ticks=0) == []


def test_render_report_includes_table_and_final_state() -> None:
    spec = GoalSimSpec(
        loop_id="r",
        decision_model_kind="CUSTOM",
        goals=2,
    )
    results = simulate(spec, ticks=10)
    rendered = render_report(results, spec)
    assert "Goal simulation: loop=r kind=CUSTOM goals=2" in rendered
    assert "| tick | state | achieved | pending | achievement% | event |" in rendered
    assert "final state=retired" in rendered


# --- _load_spec tests -------------------------------------------------------


def test_load_spec_dict() -> None:
    p = Path("/tmp/goalsim-spec.json")
    p.write_text(
        json.dumps(
            {
                "loopId": "alpha",
                "decisionModelKind": "OODA",
                "goals": 7,
                "achievedPerTickActive": 2,
            }
        )
    )
    spec = _load_spec(p, "alpha")
    assert spec.loop_id == "alpha"
    assert spec.decision_model_kind == "OODA"
    assert spec.goals == 7
    assert spec.achieved_per_tick_active == 2


def test_load_spec_list() -> None:
    p = Path("/tmp/goalsim-spec-list.json")
    p.write_text(
        json.dumps(
            [
                {"loopId": "alpha", "decisionModelKind": "OODA", "goals": 3},
                {"loopId": "beta", "decisionModelKind": "MAPE", "goals": 5},
            ]
        )
    )
    spec = _load_spec(p, "beta")
    assert spec.loop_id == "beta"
    assert spec.decision_model_kind == "MAPE"
    assert spec.goals == 5


def test_load_spec_unknown_loop_raises() -> None:
    p = Path("/tmp/goalsim-spec-missing.json")
    p.write_text(
        json.dumps({"loopId": "alpha", "decisionModelKind": "OODA", "goals": 1})
    )
    with pytest.raises(KeyError, match="loop_id"):
        _load_spec(p, "gamma")


# --- CLI tests --------------------------------------------------------------


def test_cli_table_output(tmp_path: Path, capsys) -> None:
    spec = tmp_path / "spec.json"
    spec.write_text(
        json.dumps(
            {
                "loopId": "l1",
                "decisionModelKind": "CUSTOM",
                "goals": 2,
                "achievedPerTickActive": 1,
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
            "5",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "Goal simulation: loop=l1 kind=CUSTOM" in out
    assert "| tick |" in out
    assert "final state=retired" in out


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
            "--ticks",
            "3",
            "--format",
            "json",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    body = json.loads(out)
    assert body["loopId"] == "l1"
    assert body["kind"] == "OODA"
    assert len(body["ticks"]) == 3


def test_cli_kind_override(tmp_path: Path, capsys) -> None:
    spec = tmp_path / "spec.json"
    spec.write_text(
        json.dumps(
            {
                "loopId": "l1",
                "decisionModelKind": "CUSTOM",
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
            "--kind",
            "OODA",
            "--ticks",
            "3",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "kind=OODA" in out


def test_cli_trace_writes_jsonl(tmp_path: Path, capsys) -> None:
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
    trace = tmp_path / "trace.jsonl"
    rc = _run_cli(
        [
            "--spec",
            str(spec),
            "--loop-id",
            "l1",
            "--ticks",
            "3",
            "--trace",
            str(trace),
        ]
    )
    assert rc == 0
    assert trace.exists()
    lines = [
        line
        for line in trace.read_text().splitlines()
        if line.strip()
    ]
    assert len(lines) == 3
    first = json.loads(lines[0])
    assert first["event"] == "tick"
    assert "tick" in first
    assert "state" in first