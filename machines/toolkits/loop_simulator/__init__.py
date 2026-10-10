"""CLAM loop simulator toolkit.

Drives an OODA / MAPE decision cycle against a live CLAM API and emits a
JSONL trace of state transitions. CLI: ``clam-loop-simulator``.
"""

from .cli import main

__all__ = ["main"]