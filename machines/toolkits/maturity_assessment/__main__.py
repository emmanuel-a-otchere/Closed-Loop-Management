"""CLAM maturity assessment -- entry point for ``python -m machines.toolkits.maturity_assessment``."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())