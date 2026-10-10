"""CLAM loop simulator -- entry point for ``python -m machines.toolkits.loop_simulator``."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())