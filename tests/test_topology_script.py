"""Tests for the topology_script toolkit (Slice 7 PR3)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from machines.toolkits.topology_script import load_spec, render_script
from machines.toolkits.topology_script.cli import main


def _run_cli(args: list[str]) -> int:
    saved = sys.argv
    sys.argv = ["clam-topology-script", *args]
    try:
        return main()
    finally:
        sys.argv = saved


def _full_spec() -> dict:
    return {
        "decisionModels": [
            {"id": "dm-1", "name": "Loop DM", "kind": "OODA"},
        ],
        "activities": [
            {"id": "act-1", "name": "Sensor", "kind": "sense"},
        ],
        "workflows": [
            {"id": "wf-1", "name": "Main flow"},
        ],
        "goals": [
            {"id": "g-1", "name": "Latency", "targetValue": 0.99},
        ],
        "closedLoops": [
            {"id": "cl-1", "name": "Loop 1", "decisionModelId": "dm-1"},
        ],
        "closedLoopLinks": [
            {
                "id": "lnk-1",
                "sourceLoopId": "cl-1",
                "targetLoopId": "cl-2",
                "linkType": "hierarchical",
            },
        ],
    }


# --- load_spec ---------------------------------------------------------------


def test_load_spec_full(tmp_path: Path) -> None:
    p = tmp_path / "topology.json"
    p.write_text(json.dumps(_full_spec()))
    spec = load_spec(p)
    assert len(spec["decisionModels"]) == 1
    assert len(spec["closedLoopLinks"]) == 1


def test_load_spec_missing_sections_default_empty(tmp_path: Path) -> None:
    p = tmp_path / "topology.json"
    p.write_text(json.dumps({"decisionModels": []}))
    spec = load_spec(p)
    assert spec["activities"] == []
    assert spec["closedLoopLinks"] == []


def test_load_spec_rejects_non_object(tmp_path: Path) -> None:
    p = tmp_path / "topology.json"
    p.write_text(json.dumps([1, 2, 3]))
    with pytest.raises(ValueError, match="must be a JSON object"):
        load_spec(p)


def test_load_spec_rejects_non_list_section(tmp_path: Path) -> None:
    p = tmp_path / "topology.json"
    p.write_text(json.dumps({"goals": {"id": "g-1"}}))
    with pytest.raises(ValueError, match="must be a list"):
        load_spec(p)


# --- render_script -----------------------------------------------------------


def test_render_script_dependency_order() -> None:
    """Sections appear in dependency order in the emitted script."""
    script = render_script(_full_spec(), base_url="http://x:1")
    idx_dm = script.index("/api/v1/decisionModels")
    idx_act = script.index("/api/v1/activities")
    idx_wf = script.index("/api/v1/workflows")
    idx_goal = script.index("/api/v1/goals")
    idx_cl = script.index("/api/v1/closedLoops")
    idx_link = script.index("/api/v1/closedLoopLinks")
    assert idx_dm < idx_act < idx_wf < idx_goal < idx_cl < idx_link


def test_render_script_bakes_base_url() -> None:
    script = render_script(_full_spec(), base_url="http://staging:9000")
    assert 'BASE = \'http://staging:9000\'' in script


def test_render_script_skips_empty_sections() -> None:
    spec = _full_spec()
    spec["workflows"] = []
    script = render_script(spec)
    assert "/api/v1/workflows" not in script


def test_render_script_tolerates_200_201_409() -> None:
    """Each POST asserts the idempotent-friendly status set."""
    script = render_script(_full_spec())
    assert "assert r.status_code in (200, 201, 409)" in script


def test_render_script_is_valid_python() -> None:
    """The emitted script parses as valid Python."""
    script = render_script(_full_spec())
    compile(script, "<topology_script>", "exec")


def test_render_script_empty_spec_still_valid() -> None:
    script = render_script({})
    compile(script, "<topology_script>", "exec")
    assert "httpx" in script


# --- CLI ---------------------------------------------------------------------


def test_cli_writes_script(tmp_path: Path, capsys) -> None:
    spec_path = tmp_path / "topology.json"
    spec_path.write_text(json.dumps(_full_spec()))
    out = tmp_path / "reproduce.py"
    rc = _run_cli(
        ["--spec", str(spec_path), "--out", str(out)]
    )
    assert rc == 0
    assert out.exists()
    content = out.read_text()
    assert "/api/v1/decisionModels" in content
    assert "6 entities" in capsys.readouterr().out


def test_cli_missing_spec_returns_2(tmp_path: Path, capsys) -> None:
    rc = _run_cli(
        [
            "--spec",
            str(tmp_path / "nope.json"),
            "--out",
            str(tmp_path / "out.py"),
        ]
    )
    assert rc == 2
    assert "spec not found" in capsys.readouterr().err
