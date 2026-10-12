# Compare-decisions (`clam-compare-decisions`)

Slice 7 PR2 toolkit. Runs the same closed-loop spec through
two decision model kinds (default: OODA vs MAPE) and prints
a side-by-side comparison.

## Spec shape

Same as `clam-goalsim` -- see
[machines/toolkits/goalsim/README.md](../goalsim/README.md).

## CLI

```bash
clam-compare-decisions \
    --spec loop.json \
    --loop-id my-loop \
    --kind-a OODA \
    --kind-b MAPE \
    --ticks 20 \
    --format table
```

`--format json` emits a single JSON document with two
`sides` keys (`<kind-a>` / `<kind-b>`). `--trace`
writes one JSONL line per side (the line carries the full
trajectory).

## Public Python API

```python
from machines.toolkits.compare_decisions import (
    CompareResult, compare, render_comparison,
)
from machines.toolkits.goalsim import GoalSimSpec

spec = GoalSimSpec(
    loop_id="my-loop",
    decision_model_kind="OODA",  # ignored by compare; kinds override
    goals=10,
    achieved_per_tick_active=1,
)
result_ooda, result_mape = compare(
    spec=spec, kind_a="OODA", kind_b="MAPE", ticks=20,
)
print(render_comparison(result_ooda, result_mape, loop_id="my-loop"))
```
