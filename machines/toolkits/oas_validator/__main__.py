"""CLAM OAS validator -- entry point for ``python -m machines.toolkits.oas_validator``."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())