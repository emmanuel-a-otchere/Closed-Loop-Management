"""CLAM compare-decisions toolkit (Slice 7 PR2).

CLI: ``clam-compare-decisions``. See ``cli.py`` for the public
API and arguments. Runs the same closed-loop spec through
two decision model kinds (default: OODA vs MAPE) and prints
a side-by-side comparison.
"""

from .cli import CompareResult, compare, render_comparison

__all__ = ["CompareResult", "compare", "render_comparison"]