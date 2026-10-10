#!/usr/bin/env python
"""Seed the dev SQLite with two sample closed loops + their decision models.

Usage:

    python scripts/seed_db.py
    CLAM_DB_PATH=/tmp/clam.db python scripts/seed_db.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the api package is importable when invoked from the repo root.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "api"))

from clam.cli import main  # noqa: E402

if __name__ == "__main__":
    main()