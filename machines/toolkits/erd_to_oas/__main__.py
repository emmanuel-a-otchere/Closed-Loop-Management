"""CLAM ERD-to-OAS -- entry point for ``python -m machines.toolkits.erd_to_oas``."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())