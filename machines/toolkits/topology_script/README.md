# Topology script (`clam-topology-script`)

Slice 7 PR3 toolkit. Reads a topology spec (JSON) and emits
a runnable Python script that recreates the topology by
POSTing to a live CLAM API in dependency order.

## Spec shape

```json
{
  "decisionModels": [{"id": "dm-1", "name": "Loop DM", "kind": "OODA"}],
  "activities":     [{"id": "act-1", "name": "Sensor", "kind": "sense"}],
  "workflows":      [{"id": "wf-1", "name": "Main flow"}],
  "goals":          [{"id": "g-1", "name": "Latency < 100ms", "targetValue": 0.99}],
  "closedLoops":    [{"id": "cl-1", "name": "Loop 1", "decisionModelId": "dm-1"}],
  "closedLoopLinks":[{"id": "lnk-1", "sourceLoopId": "cl-1",
                      "targetLoopId": "cl-2", "linkType": "hierarchical"}]
}
```

Any section may be omitted; the emitted script skips it.

## CLI

```bash
clam-topology-script --spec topology.json \
    --base http://localhost:8000 \
    --out reproduce_topology.py
```

The emitted script is self-contained apart from `httpx`
(already a project dependency). Sections are emitted in
dependency order: decision models -> activities -> workflows
-> goals -> closed loops -> links. Each POST tolerates
`200 / 201 / 409` so the script is re-runnable against a
partially-populated service.

## Public Python API

```python
from machines.toolkits.topology_script import load_spec, render_script
from pathlib import Path

spec = load_spec(Path("topology.json"))
script = render_script(spec, base_url="http://staging:8000")
Path("reproduce_topology.py").write_text(script)
```
