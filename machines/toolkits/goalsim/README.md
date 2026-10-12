# Goal simulator (`clam-goalsim`)

Slice 7 PR1 toolkit. Loads a closed-loop JSON spec, projects
goal achievement over N ticks using a configurable decision
model kind (OODA / MAPE / CUSTOM), and emits a per-tick
achievement table.

## Spec shape

The spec file is either a single object or a list of objects;
when a list is given, `--loop-id` selects the entry.

```json
{
  "loopId": "my-loop",
  "decisionModelKind": "OODA",
  "goals": 10,
  "achievedPerTickActive": 1,
  "startingState": "designed"
}
```

- `decisionModelKind`: one of `OODA`, `MAPE`, `CUSTOM`.
- `goals`: total goal count for the loop.
- `achievedPerTickActive` (optional, default 1): how many
  goals flip from pending to achieved on every tick where
  the loop is in the `active` state.
- `startingState` (optional, default `designed`).

## CLI

```bash
clam-goalsim \
    --spec loops.json \
    --loop-id my-loop \
    --kind OODA \
    --ticks 20 \
    --trace goalsim.jsonl
```

`--format json` emits one JSON document with the per-tick
list. `--trace` writes the per-tick results as JSONL.

## Public Python API

```python
from machines.toolkits.goalsim import (
    GoalSimSpec, simulate, render_report,
)

spec = GoalSimSpec(
    loop_id="my-loop",
    decision_model_kind="OODA",
    goals=10,
    achieved_per_tick_active=2,
)
results = simulate(spec, ticks=20)
print(render_report(results, spec))
```