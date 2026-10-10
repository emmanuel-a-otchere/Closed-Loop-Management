#!/usr/bin/env python
"""Seed the dev SQLite with two sample closed loops + their decision models.

Usage:

    python machines/scripts/seed_db.py
    CLAM_DB_PATH=/tmp/clam.db python machines/scripts/seed_db.py
"""

from __future__ import annotations

from machines.service.clam.cli import main

if __name__ == "__main__":
    main()