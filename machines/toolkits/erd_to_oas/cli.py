"""ERD-to-OAS generator.

The CLAM project ships a reference ERD at
``schemas/data-model/legacy-2022-erd.xlsx``. This toolkit reads an Excel
workbook that follows a simple convention:

- One sheet per entity.
- First row is the header (column names).
- First column is the attribute name.
- Second column is the data type (string / integer / number / boolean / uuid / datetime).
- Third column (optional) is the description.

It emits an OAS 3.1 schema fragment under ``components.schemas`` that
matches the column shape, suitable for splicing into the live OAS
document via a small follow-up step.

CLI usage::

    clam-erd-to-oas schemas/data-model/legacy-2022-erd.xlsx \\
        --out schemas/openapi/erd-fragment.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

_TYPE_MAP: dict[str, dict[str, Any]] = {
    "string": {"type": "string"},
    "text": {"type": "string"},
    "uuid": {"type": "string", "format": "uuid"},
    "datetime": {"type": "string", "format": "date-time"},
    "date": {"type": "string", "format": "date"},
    "integer": {"type": "integer"},
    "int": {"type": "integer"},
    "number": {"type": "number"},
    "float": {"type": "number"},
    "boolean": {"type": "boolean"},
    "bool": {"type": "boolean"},
}


def _sheet_to_schema(sheet) -> dict[str, Any] | None:
    rows = list(sheet.iter_rows(values_only=True))
    if len(rows) < 2:
        return None
    # Row 0: header. Row 1+: data rows.
    properties: dict[str, Any] = {}
    for row in rows[1:]:
        if not row or row[0] is None:
            continue
        attr = str(row[0]).strip()
        raw_type = str(row[1]).strip().lower() if len(row) > 1 and row[1] is not None else "string"
        description = str(row[2]).strip() if len(row) > 2 and row[2] is not None else None
        schema = _TYPE_MAP.get(raw_type, {"type": "string"})
        if description:
            schema["description"] = description
        properties[attr] = schema
    return {"type": "object", "properties": properties}


def convert(workbook_path: Path) -> dict[str, Any]:
    wb = load_workbook(workbook_path, data_only=True, read_only=True)
    schemas: dict[str, Any] = {}
    for sheet in wb.worksheets:
        schema = _sheet_to_schema(sheet)
        if schema is not None:
            schemas[sheet.title] = schema
    return {"components": {"schemas": schemas}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    if not args.workbook.exists():
        print(f"workbook not found: {args.workbook}", file=sys.stderr)
        return 2

    fragment = convert(args.workbook)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(fragment, indent=2, sort_keys=True))
    print(
        f"Wrote OAS fragment with {len(fragment['components']['schemas'])} schemas to {args.out}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())