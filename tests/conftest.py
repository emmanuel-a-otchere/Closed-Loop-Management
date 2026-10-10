"""Test configuration.

Isolates the test database from the dev one.
"""

import os
from pathlib import Path

# Default to an in-memory-like temp file under tmp so tests cannot collide
# with the dev SQLite database.
os.environ.setdefault("CLAM_DB_PATH", str(Path("/tmp/clam-test.db")))