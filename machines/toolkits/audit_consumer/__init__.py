"""CLAM audit-consumer toolkit (Slice 7 PR3).

CLI: ``clam-audit-consumer``. See ``cli.py``.
"""

from .cli import iter_audit_rows, write_csv, write_jsonl

__all__ = ["iter_audit_rows", "write_csv", "write_jsonl"]
