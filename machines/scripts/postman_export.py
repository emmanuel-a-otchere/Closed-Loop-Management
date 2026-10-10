#!/usr/bin/env python
"""Generate a Postman collection from the live OAS document.

Usage:

    python machines/scripts/postman_export.py --out schemas/openapi/postman/clam.postman_collection.json

The script reads the OAS produced by ``machines/scripts/export_openapi.py`` and
emits a Postman v2.1 collection that targets ``{{baseUrl}}`` (default
``http://localhost:8000``).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from machines.service.clam.main import app

METHOD_TO_POSTMAN: dict[str, dict[str, Any]] = {
    "get":    {"request": {"method": "GET"}},
    "post":   {"request": {"method": "POST"}},
    "patch":  {"request": {"method": "PATCH"}},
    "delete": {"request": {"method": "DELETE"}},
}


def _example_body(schema: dict[str, Any] | None) -> Any:
    if not schema:
        return {}
    example = schema.get("example")
    if example is not None:
        return example
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    spec = app.openapi()
    items: list[dict[str, Any]] = []

    for path, methods in spec.get("paths", {}).items():
        for method, operation in methods.items():
            if method.lower() not in METHOD_TO_POSTMAN:
                continue
            summary = operation.get("summary", method.upper())
            description = operation.get("description", "")
            url_path = path.replace("{", "{{").replace("}", "}}")
            item: dict[str, Any] = {
                "name": summary,
                "request": {
                    "method": METHOD_TO_POSTMAN[method.lower()]["request"]["method"],
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "url": {
                        "raw": "{{baseUrl}}" + url_path,
                        "host": ["{{baseUrl}}"],
                        "path": [p for p in url_path.split("/") if p],
                    },
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps(_example_body(operation.get("requestBody")), indent=2),
                    },
                },
            }
            if description:
                item["request"]["description"] = description
            items.append(item)

    collection = {
        "info": {
            "name": spec.get("info", {}).get("title", "CLAM"),
            "description": spec.get("info", {}).get("summary", ""),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": items,
        "variable": [
            {"key": "baseUrl", "value": "http://localhost:8000"},
        ],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(collection, indent=2, sort_keys=True))
    print(
        f"Wrote Postman collection ({len(items)} requests) to {args.out} "
        f"({args.out.stat().st_size} bytes)"
    )


if __name__ == "__main__":
    main()