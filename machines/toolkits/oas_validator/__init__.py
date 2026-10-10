"""CLAM OAS validator toolkit.

Validates an OAS 3.1 document against the CLAM profile (extra rules on top
of the standard OAS 3.1 schema). CLI: ``clam-oas-validator <path>``.
"""

from .cli import main

__all__ = ["main"]