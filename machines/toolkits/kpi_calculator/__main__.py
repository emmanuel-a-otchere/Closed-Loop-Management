"""CLAM KPI calculator -- entry point for ``python -m machines.toolkits.kpi_calculator``."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())