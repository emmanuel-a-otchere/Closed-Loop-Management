"""CLAM goal simulation toolkit (Slice 7 PR1).

CLI: ``clam-goalsim``. See ``cli.py`` for the public API and
arguments. The simulator loads a closed-loop JSON spec,
projects goal achievement over N ticks, and emits either a
human-readable table or JSON Lines.
"""

from .cli import GoalSimSpec, TickResult, render_report, simulate

__all__ = ["GoalSimSpec", "TickResult", "render_report", "simulate"]