# CLAM Loop Simulator

Drives a closed loop's state machine through one or more decision cycles
against a live CLAM API. Emits a JSONL trace of every transition.

## Why

A closed loop's correctness is determined by the interaction between its
decision model and the API state machine. The simulator exercises that
interaction so you can verify the lifecycle wiring before deploying.

## Install

```bash
pip install -e ".[toolkit-loop-simulator]"
```

## Usage

```bash
# Seed the dev DB first
python machines/scripts/seed_db.py

# Run the simulator against one of the seeded loops
clam-loop-simulator --base http://localhost:8000 \\
    --loop-id <id-from-seed> --cycles 10 --trace trace.jsonl
```

The simulator reads the loop's decision-model kind (OODA / MAPE / CUSTOM)
and walks a state path appropriate to that kind. Every transition is
appended to the trace file as one JSON object per line.

## Output

```jsonl
{"event": "transition", "from": "designed", "to": "validated", "cycle": 0, "ts": "..."}
{"event": "transition", "from": "validated", "to": "published", "cycle": 1, "ts": "..."}
...
```

The trace file is overwritten on each run (the CLI deletes any existing
file at the same path before starting).