# Audit consumer (`clam-audit-consumer`)

Slice 7 PR3 toolkit. Reads audit rows from a live CLAM
service via `GET /api/v1/audit?since=<ISO-8601>`
(cursor-paginated, newest first) and dumps them to CSV or
JSON Lines.

## CLI

```bash
# CSV export
clam-audit-consumer --base http://localhost:8000 \
    --since 2026-10-01T00:00:00+00:00 \
    --format csv --out audit.csv

# JSON Lines export filtered by entity kind
clam-audit-consumer --base http://localhost:8000 \
    --entity-kind ClosedLoop \
    --format jsonl --out audit.jsonl

# With bearer auth (CLAM_AUTH_ENABLED=true)
clam-audit-consumer --base http://localhost:8000 \
    --token $CLAM_TOKEN --format csv --out audit.csv
```

Flags mirror the audit endpoint query parameters:
`--since`, `--until`, `--entity-kind`, `--entity-id`,
`--actor`, `--action`, `--limit` (1..1000, default 100).
The consumer walks `nextCursor` until exhausted.

## Output

- **CSV** columns: `id, ts, actor, action, entityKind,
  entityId, correlationId, before, after`. Complex values
  (`before` / `after`) are JSON-encoded inline.
- **JSONL** emits the full audit entry per line, unchanged.

## Public Python API

```python
from machines.toolkits.audit_consumer import (
    iter_audit_rows, write_csv, write_jsonl,
)
from pathlib import Path

rows = iter_audit_rows(
    base="http://localhost:8000",
    since="2026-10-01T00:00:00+00:00",
)
n = write_csv(rows, Path("audit.csv"))
print(f"exported {n} rows")
```
