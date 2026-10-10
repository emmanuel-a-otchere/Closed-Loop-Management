# CLAM KPI Calculator

Consumes a JSONL trace produced by `clam-loop-simulator` and emits a KPI
report covering transition counts, mean state residence, error/retired
rates, and a transition matrix.

## Why

The CLAM API records state transitions; the simulator drives cycles;
this calculator turns a trace into operational metrics that can be
ingested into dashboards or alerting pipelines.

## Install

```bash
pip install -e ".[toolkit-kpi-calculator]"
```

## Usage

```bash
clam-loop-simulator --base http://localhost:8000 --loop-id <id> --cycles 20 --trace trace.jsonl
clam-kpi-calculator --in trace.jsonl
# or save the JSON report
clam-kpi-calculator --in trace.jsonl --out kpi-report.json
```

## Report shape

```json
{
  "total_events": 42,
  "total_transitions": 36,
  "total_rejections": 4,
  "total_halts": 2,
  "transition_matrix": [
    {"from": "designed", "to": "validated", "count": 12},
    {"from": "validated", "to": "published", "count": 8},
    ...
  ],
  "mean_state_residence_seconds": 12.34,
  "transitions_to_error": 1,
  "transitions_to_retired": 1
}
```