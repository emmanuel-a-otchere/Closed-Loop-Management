"""Test configuration.

Isolates the test database from the dev one.
"""

import os
import sys
from pathlib import Path

# Make `api/` importable as `clam` for the test runner.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "api"))

# Default to an in-memory-like temp file under tmp so tests cannot collide
# with the dev SQLite database.
os.environ.setdefault("CLAM_DB_PATH", str(Path("/tmp/clam-test.db")))