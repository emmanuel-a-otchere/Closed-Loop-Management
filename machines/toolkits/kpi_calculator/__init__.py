"""CLAM KPI calculator toolkit.

Consumes a JSONL trace of loop state transitions (produced by
``clam-loop-simulator``) and emits a KPI report: total cycles, mean
state residence, transition counts, error/retired rates.
CLI: ``clam-kpi-calculator``.
"""

from .cli import main

__all__ = ["main"]