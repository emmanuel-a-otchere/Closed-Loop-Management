# CLAM Data Model 1.0

This document is the **binding** form of the conceptual model that the
2022 ERD introduced. Where the 2022 ERD describes entities in prose and
diagrams, this document defines the OAS 3.1 types, the resource shapes, and
the relationships that the REST API serves.

The legacy 2022 ERD remains at
[`legacy-2022-erd.xlsx`](legacy-2022-erd.xlsx) as the lineage source.

## Entities

| Entity | OAS schema | Description |
| --- | --- | --- |
| `ClosedLoop` | `#/components/schemas/ClosedLoop` | The top-level managed unit. Holds a goal, a decision model reference, and lifecycle state. |
| `DecisionModel` | `#/components/schemas/DecisionModel` | The cognitive loop pattern. Discriminated union of `OodaDecisionModel`, `MapeDecisionModel`, and `CustomDecisionModel`. |
| `Goal` | `#/components/schemas/Goal` | A target on a closed loop or one of its constituents. |
| `Workflow` | `#/components/schemas/Workflow` | An ordered set of activities that realizes a single step in the closed loop. |
| `Activity` | `#/components/schemas/Activity` | A unit of work inside a workflow. Can be on the feedforward (control) or feedback (sensing) path. |
| `ClosedLoopLink` | `#/components/schemas/ClosedLoopLink` | A daisy-chain or hierarchical interlink between two closed loops. |
| `ClosedLoopState` | `#/components/schemas/ClosedLoopState` | Lifecycle state of a closed loop (see [State machine](#state-machine)). |

## ClosedLoop

```yaml
ClosedLoop:
  type: object
  required: [id, name, decisionModelRef, state, createdAt]
  properties:
    id:
      type: string
      format: uuid
      readOnly: true
    name:
      type: string
      description: Short, human-readable identifier (must be unique within a tenant).
    description:
      type: string
      nullable: true
    decisionModelRef:
      $ref: '#/components/schemas/DecisionModelRef'
    goals:
      type: array
      items:
        $ref: '#/components/schemas/Goal'
    workflows:
      type: array
      items:
        $ref: '#/components/schemas/WorkflowRef'
    links:
      type: array
      description: ClosedLoopLinks where this loop participates as source or target.
      items:
        $ref: '#/components/schemas/ClosedLoopLink'
    state:
      $ref: '#/components/schemas/ClosedLoopState'
    createdAt:
      type: string
      format: date-time
      readOnly: true
    updatedAt:
      type: string
      format: date-time
      readOnly: true
```

## DecisionModel

```yaml
DecisionModel:
  oneOf:
    - $ref: '#/components/schemas/OodaDecisionModel'
    - $ref: '#/components/schemas/MapeDecisionModel'
    - $ref: '#/components/schemas/CustomDecisionModel'
  discriminator:
    propertyName: kind
    mapping:
      OODA: '#/components/schemas/OodaDecisionModel'
      MAPE: '#/components/schemas/MapeDecisionModel'
      CUSTOM: '#/components/schemas/CustomDecisionModel'

OodaDecisionModel:
  type: object
  required: [id, kind, observe, orient, decide, act]
  properties:
    id: { type: string, format: uuid }
    kind: { type: string, enum: [OODA] }
    observe: { $ref: '#/components/schemas/ActivityRef' }
    orient:  { $ref: '#/components/schemas/ActivityRef' }
    decide:  { $ref: '#/components/schemas/ActivityRef' }
    act:     { $ref: '#/components/schemas/ActivityRef' }

MapeDecisionModel:
  type: object
  required: [id, kind, monitor, analyze, plan, execute]
  properties:
    id: { type: string, format: uuid }
    kind: { type: string, enum: [MAPE] }
    monitor:  { $ref: '#/components/schemas/ActivityRef' }
    analyze:  { $ref: '#/components/schemas/ActivityRef' }
    plan:     { $ref: '#/components/schemas/ActivityRef' }
    execute:  { $ref: '#/components/schemas/ActivityRef' }

CustomDecisionModel:
  type: object
  required: [id, kind, steps]
  properties:
    id: { type: string, format: uuid }
    kind: { type: string, enum: [CUSTOM] }
    steps:
      type: array
      items:
        type: object
        required: [name, activityRef]
        properties:
          name: { type: string }
          activityRef: { $ref: '#/components/schemas/ActivityRef' }

DecisionModelRef:
  type: object
  required: [id, kind]
  properties:
    id: { type: string, format: uuid }
    kind: { type: string, enum: [OODA, MAPE, CUSTOM] }
```

## Goal

```yaml
Goal:
  type: object
  required: [id, name, target]
  properties:
    id: { type: string, format: uuid }
    name: { type: string }
    description: { type: string, nullable: true }
    target:
      type: object
      required: [metric, value]
      properties:
        metric: { type: string }
        value:  { type: number }
        unit:   { type: string, nullable: true }
        direction:
          type: string
          enum: [AT_LEAST, AT_MOST, EXACTLY]
          default: AT_LEAST
    scope:
      type: string
      enum: [CLOSED_LOOP, WORKFLOW, ACTIVITY]
      default: CLOSED_LOOP
    scopeRef:
      type: string
      format: uuid
      nullable: true
      description: Required when scope is WORKFLOW or ACTIVITY.
```

## Workflow

```yaml
Workflow:
  type: object
  required: [id, name, path]
  properties:
    id: { type: string, format: uuid }
    name: { type: string }
    path:
      type: string
      enum: [FEEDFORWARD, FEEDBACK]
      description: FEEDFORWARD (control) or FEEDBACK (sensing) path within the loop.
    activities:
      type: array
      items: { $ref: '#/components/schemas/ActivityRef' }

WorkflowRef:
  type: object
  required: [id, name]
  properties:
    id: { type: string, format: uuid }
    name: { type: string }
```

## Activity

```yaml
Activity:
  type: object
  required: [id, name, action]
  properties:
    id: { type: string, format: uuid }
    name: { type: string }
    description: { type: string, nullable: true }
    action:
      type: string
      description: Reference to the underlying implementation (e.g. an HTTP endpoint, a function name, a workflow id).
    inputs:
      type: array
      items: { type: string }
    outputs:
      type: array
      items: { type: string }

ActivityRef:
  type: object
  required: [id]
  properties:
    id: { type: string, format: uuid }
    name: { type: string, nullable: true }
```

## ClosedLoopLink

```yaml
ClosedLoopLink:
  type: object
  required: [id, source, target, kind]
  properties:
    id: { type: string, format: uuid }
    source: { $ref: '#/components/schemas/ClosedLoopRef' }
    target: { $ref: '#/components/schemas/ClosedLoopRef' }
    kind:
      type: string
      enum: [DAISY_CHAIN, HIERARCHICAL, FEEDBACK]
      description: |
        DAISY_CHAIN: target's output feeds source's input (peer-to-peer).
        HIERARCHICAL: target is a sub-loop of source (composition).
        FEEDBACK: target's output is consumed by source's feedback path.
    condition:
      type: string
      nullable: true
      description: Optional CEL-like expression that gates the link activation.
```

## State machine

```yaml
ClosedLoopState:
  type: string
  enum: [designed, validated, published, active, paused, error, retired]
```

Transitions are explicit, controlled by the API:

```
designed   --(validate)--> validated
validated  --(publish)-->  published
published  --(activate)--> active
active     --(pause)-->    paused
active     --(error)-->    error
paused     --(activate)--> active
paused     --(retire)-->   retired
error      --(activate)--> active
error      --(retire)-->   retired
*          --(retire)-->   retired   (only valid from non-retired states)
```

The state machine is the same one the 2022 README implied under
"Closed Loop Lifecycle" with minor clarifications.

## Relationship summary

```
ClosedLoop 1 ── * Goal
ClosedLoop 1 ── 1 DecisionModel
ClosedLoop * ── * Workflow   (via WorkflowRef)
ClosedLoop * ── * ClosedLoop (via ClosedLoopLink)
Workflow    1 ── * Activity   (via ActivityRef)
```

The `WorkflowRef` and `ActivityRef` types are lightweight projections used
when embedding one entity inside another; full CRUD lives at
`/workflow` and `/activity` respectively (Slice 2+).

## How this maps to the API

| Entity | API root | HTTP verbs |
| --- | --- | --- |
| `ClosedLoop` | `/closedLoop` | GET, POST, PATCH, DELETE |
| `ClosedLoop` state | `/closedLoop/{id}/state` | GET, POST |
| `DecisionModel` | `/decisionModel` | GET, POST, PATCH, DELETE |
| `Goal` | `/closedLoop/{id}/goal` | GET, POST, PATCH, DELETE |
| `Workflow` | `/closedLoop/{id}/workflow` | GET, POST, PATCH, DELETE |
| `Activity` | `/closedLoop/{id}/activity` | GET, POST, PATCH, DELETE |
| `ClosedLoopLink` | `/closedLoop/{id}/link` | GET, POST, DELETE |

Slice 1 ships `/closedLoop` and `/decisionModel` plus `/health` and
`/openapi.json`. Slice 2 expands to the other resources.