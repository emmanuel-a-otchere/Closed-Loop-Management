"""CLAM ERD-to-OAS toolkit.

Reads a .xlsx entity-relationship diagram and emits an OAS 3.1 schema
fragment that can be merged into the CLAM API's openapi.json. CLI:
``clam-erd-to-oas``.
"""

from .cli import main

__all__ = ["main"]