# The CLAM Paradigm

> Position paper. Why closed loops need management, what management
> means, and how the CLAM paradigm expresses it as a body of machine
> assets.

## The argument

Every operational system that adapts to its environment is, at heart, a
**closed loop**. A web service that back-pressures when downstream
saturates. A thermostat that opens a vent when temperature rises. An
auto-scaler that adds capacity when CPU crosses a threshold. A trading
engine that rebalances when volatility shifts. Each takes in a signal,
makes a decision, applies an action, and the action changes the signal
that comes back in.

Three things are usually missing when organisations try to scale closed
loops:

1. **A typed representation of the loop itself.** Most closed loops live
   inside a single application's source code, indistinguishable from the
   rest of the application. You can't audit them. You can't move them.
   You can't retire them.
2. **A lifecycle that is explicit and managed.** The loop is born, the
   loop is validated, the loop is published into an environment, the
   loop runs, the loop is paused, the loop retires. Each transition has
   implications. Without an explicit state machine, transitions are
   hidden in code paths.
3. **A separation of feedforward and feedback paths.** A loop's control
   action is not the same shape as the signal that comes back in.
   Conflating them hides bugs.

CLAM is the paradigm that answers these three problems.

## What management means

**Management** is the set of operations that you can perform on a closed
loop without going through its implementation. Concretely:

- **Discover** -- list every closed loop currently in operation.
- **Design** -- define a new closed loop: a goal, a decision model, the
  workflows that execute it.
- **Validate** -- prove that the closed loop meets its goal before it
  sees production traffic.
- **Publish** -- move the closed loop into an environment where it can
  run.
- **Activate** -- start the loop.
- **Pause** -- temporarily stop the loop without retiring it.
- **Retire** -- permanently stop the loop and remove it from the
  catalog.
- **Interlink** -- connect this loop to other loops so one loop's
  outputs feed another's inputs.
- **Observe** -- emit metrics, logs, and traces for the loop's
  behaviour.

The set of operations is closed: every operation is reachable from every
other operation through an explicit transition. That closure is what
makes closed loops **manageable** rather than merely **observed**.

## How CLAM expresses it

The paradigm is realised as a body of machine assets in this repository:

| Asset | Path | Purpose |
| --- | --- | --- |
| **Service** | `machines/service/clam/` | The FastAPI REST API. CRUD over closed loops, decision models, goals, workflows, activities, and links. |
| **Data model** | `schemas/data-model/` | The binding OAS-backed entity definitions (the `clam-data-model-1.0.md` doc) plus the lineage source (the legacy 2022 ERD). |
| **OAS schema** | `schemas/openapi/openapi.json` | The OAS 3.1 contract, generated from Pydantic, validated in CI. |
| **Postman collection** | `schemas/openapi/postman/clam.postman_collection.json` | Downloadable Postman v2.1 collection that mirrors every endpoint. |
| **Toolkit: oas-validator** | `machines/toolkits/oas_validator/` | Profile-level OAS validator (CLAM rules on top of OAS 3.1). |
| **Toolkit: loop-simulator** | `machines/toolkits/loop_simulator/` | Drives an OODA/MAPE/CUSTOM decision cycle against a live API; emits a JSONL trace. |
| **Toolkit: erd-to-oas** | `machines/toolkits/erd_to_oas/` | Reads an .xlsx ERD and emits an OAS schema fragment. |
| **Toolkit: maturity-assessment** | `machines/toolkits/maturity_assessment/` | Non-technical questionnaire + CSV scoring template for assessing a deployment's maturity. |
| **Toolkit: kpi-calculator** | `machines/toolkits/kpi_calculator/` | Consumes a simulator trace and emits a KPI report. |
| **Datasets** | `datasets/examples/` | Reference payloads (OODA closed loop, OODA / MAPE / CUSTOM decision models). |
| **Diagrams** | `docs/diagrams/` | Mermaid + PlantUML sources for ERD, lifecycle, state machine, sequence, use cases. |

Every asset is downloadable, machine-readable, and tested in CI.

## What this is not

CLAM is not:

- A closed-loop runtime. The CLAM API records the lifecycle of closed
  loops; it does not execute them. Execution belongs to the underlying
  activities, which are referenced by `action` strings in the data model.
- A replacement for the underlying application logic. CLAM manages
  closed loops the way Kubernetes manages pods: the lifecycle plane,
  not the work plane.
- A vendor product. It is an open-source paradigm expressed as a
  service, schemas, toolkits, datasets, and diagrams.

## See also

- `docs/api/OVERVIEW.md` -- tour of the API surface
- `schemas/data-model/clam-data-model-1.0.md` -- the binding data model
- `machines/toolkits/maturity_assessment/questionnaire.md` -- the
  maturity model
- `context/AGENT-DOCTRINE.md` -- governance rules for agents working
  on this repository