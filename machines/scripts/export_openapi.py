#!/usr/bin/env python
"""Export the OAS 3.1 document from the FastAPI app.

Usage:

    python machines/scripts/export_openapi.py --out schemas/openapi/openapi.json

The output is the snapshot the CI pipeline lints. Do not hand-edit the
output -- re-run this script after any change to the Pydantic models.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from machines.service.clam.main import app


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    spec = app.openapi()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(spec, indent=2, sort_keys=True))
    print(f"Wrote OAS 3.1 document to {args.out} ({args.out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()