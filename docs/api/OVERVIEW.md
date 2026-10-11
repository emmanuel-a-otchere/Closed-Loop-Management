# CLAM REST API Guide

This document is the single-source guide for using the CLAM REST API.
It is the canonical companion to the OpenAPI 3.1 contract served at
`/openapi.json` -- the contract is authoritative, this file is the human
walk-through.

## Base URL

```
http://localhost:8000
```

Production deployments are configured per-environment via
`CLAM_BASE_URL`. The HTTP server is local-only by default; production
deployments MUST add an authentication layer (planned for Slice 4).

## Versioning

The API is versioned in the URL: `/api/v1/...`. Breaking changes
require a new major version; non-breaking additions ship under the
current version.

## Resource roots (Slice 2)

| Path                                                    | Resource                                              |
|---------------------------------------------------------|-------------------------------------------------------|
| `/health`                                               | Liveness probe                                         |
| `/openapi.json`                                         | OAS 3.1 document (generated from Pydantic models)     |
| `/docs`                                                 | Swagger UI                                             |
| `/redoc`                                                | ReDoc UI                                              |
| `/api/v1/closedLoop`                                    | CRUD over closed loops + `/{id}/state` transitions    |
| `/api/v1/closedLoop/{id}/goalRollup`                    | Aggregate goal achievement for a closed loop           |
| `/api/v1/decisionModel`                                 | CRUD over decision models (OODA / MAPE / CUSTOM)      |
| `/api/v1/activity`                                      | CRUD over activities + `/{id}/state` lifecycle        |
| `/api/v1/workflow`                                      | CRUD over workflows + `/{id}/state` lifecycle         |
| `/api/v1/goal`                                          | CRUD over goals                                        |
| `/api/v1/closedLoopLink`                                | CRUD over loop-to-loop links (cycle-checked)          |
| `/api/v1/closedLoopLink/bulk`                           | All-or-nothing bulk link creation                     |
| `/api/v1/closedLoopLink/topology`                       | Full link topology view                               |
| `/api/v1/closedLoopLink/path?sourceId=&targetId=`       | BFS shortest path between two loops                   |
| `/api/v1/closedLoopLink/from/{loopId}`                  | Downstream links from a loop                          |
| `/api/v1/closedLoopLink/to/{loopId}`                    | Upstream links into a loop                            |

## Pagination

List endpoints return a paginated envelope:

```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "pageSize": 20
}
```

Query parameters: `?page=1&pageSize=20`. `pageSize` capped at 100.

## Error envelope

All error responses share the same shape:

```json
{
  "code": "resource.not_found",
  "message": "ClosedLoop with id 7b6c... was not found",
  "details": { "kind": "closed_loop" }
}
```

`code` is a stable, machine-readable identifier; `message` is a
human-readable string. `details` is an optional object whose schema
depends on the error class. Current error codes:

| Code                                 | Meaning                                                |
|--------------------------------------|--------------------------------------------------------|
| `request.validation_error`           | Pydantic-validated request payload failed.             |
| `resource.not_found`                 | The target entity does not exist.                      |
| `closed_loop.state_transition_invalid` | A state transition is not allowed from current state. |
| `lifecycle.constraint_violated`      | A cross-resource lifecycle rule blocks the action.     |
| `topology.cycle_detected`            | The proposed link would close a cycle in the graph.    |
| `server.internal_error`              | Unexpected server-side failure.                        |

## End-to-end examples

The examples below assume the server is running locally on port 8000.

### 1. Create an OODA decision model

```bash
curl -X POST http://localhost:8000/api/v1/decisionModel \
  -H 'Content-Type: application/json' \
  -d '{
    "kind": "OODA",
    "name": "fan-controller",
    "observe":  {"id": "11111111-1111-1111-1111-111111111111"},
    "orient":   {"id": "22222222-2222-2222-2222-222222222222"},
    "decide":   {"id": "33333333-3333-3333-3333-333333333333"},
    "act":      {"id": "44444444-4444-4444-4444-444444444444"}
  }'
```

Response (201 Created):

```json
{
  "id": "<dm-uuid>",
  "kind": "OODA",
  "name": "fan-controller",
  "observe":  {"id": "11111111-1111-1111-1111-111111111111"},
  ...
}
```

### 2. Create a closed loop that uses the decision model

```bash
DM_ID="<paste the dm-uuid from step 1>"
curl -X POST http://localhost:8000/api/v1/closedLoop \
  -H 'Content-Type: application/json' \
  -d "{
    \"name\": \"cpu-fan\",
    \"decisionModelRef\": {\"id\": \"$DM_ID\", \"kind\": \"OODA\"}
  }"
```

### 3. Create and lifecycle-publish a workflow

```bash
WF_BODY='{
  "name": "feedback-fan-control",
  "path": "FEEDBACK",
  "activities": [
    {"id": "11111111-1111-1111-1111-111111111111", "name": "sense-temp"},
    {"id": "22222222-2222-2222-2222-222222222222", "name": "analyse"},
    {"id": "33333333-3333-3333-3333-333333333333", "name": "decide"},
    {"id": "44444444-4444-4444-4444-444444444444", "name": "act"}
  ]
}'
WF_ID=$(curl -s -X POST http://localhost:8000/api/v1/workflow \
  -H 'Content-Type: application/json' \
  -d "$WF_BODY" | jq -r .id)

# Each referenced activity must be published first (or the workflow
# publish will be blocked with lifecycle.constraint_violated).
for ACT in 11111111-1111-1111-1111-111111111111 \
           22222222-2222-2222-2222-222222222222 \
           33333333-3333-3333-3333-333333333333 \
           44444444-4444-4444-4444-444444444444; do
  curl -X POST http://localhost:8000/api/v1/activity \
    -H 'Content-Type: application/json' \
    -d "{\"name\": \"act-$ACT\", \"activityType\": \"sense\", \"action\": \"x\"}"
  curl -X POST "http://localhost:8000/api/v1/activity/$ACT/state" \
    -H 'Content-Type: application/json' \
    -d '{"targetState": "validated"}'
  curl -X POST "http://localhost:8000/api/v1/activity/$ACT/state" \
    -H 'Content-Type: application/json' \
    -d '{"targetState": "published"}'
done

# Now publish the workflow.
curl -X POST "http://localhost:8000/api/v1/workflow/$WF_ID/state" \
  -H 'Content-Type: application/json' \
  -d '{"targetState": "validated"}'
curl -X POST "http://localhost:8000/api/v1/workflow/$WF_ID/state" \
  -H 'Content-Type: application/json' \
  -d '{"targetState": "published"}'
```

### 4. Set a goal on the closed loop and read the rollup

```bash
LOOP_ID="<the closed-loop uuid>"
curl -X POST http://localhost:8000/api/v1/goal \
  -H 'Content-Type: application/json' \
  -d "{
    \"name\": \"keep-cpu-cool\",
    \"target\": {\"metric\": \"cpu_temp_c\", \"value\": 80, \"unit\": \"celsius\", \"direction\": \"AT_MOST\"},
    \"scope\": \"CLOSED_LOOP\",
    \"scopeRef\": \"$LOOP_ID\",
    \"currentValue\": 72.0
  }"

curl "http://localhost:8000/api/v1/closedLoop/$LOOP_ID/goalRollup"
```

### 5. Daisy-chain loops with cycle-checked links

```bash
LOOP_A="<uuid>"
LOOP_B="<uuid>"
LO_RESP=$(curl -s -w '\n%{http_code}' -X POST http://localhost:8000/api/v1/closedLoopLink \
  -H 'Content-Type: application/json' \
  -d "{
    \"source\": {\"id\": \"$LOOP_A\"},
    \"target\": {\"id\": \"$LOOP_B\"},
    \"kind\": \"DAISY_CHAIN\",
    \"direction\": \"FORWARD\"
  }")
echo "$OP_RESP"

# If you try to add a back-edge that closes a cycle, the server returns 409:
curl -X POST http://localhost:8000/api/v1/closedLoopLink \
  -H 'Content-Type: application/json' \
  -d "{
    \"source\": {\"id\": \"$LOOP_B\"},
    \"target\": {\"id\": \"$LOOP_A\"},
    \"kind\": \"DAISY_CHAIN\",
    \"direction\": \"FORWARD\"
  }"
# -> 409 with
# {
#   "code": "topology.cycle_detected",
#   "message": "Link ... would close a cycle ...",
#   "details": {"cycle": ["<LOOP_A>", "<LOOP_B>", "<LOOP_A>"]}
# }
```

### 6. Topology queries

```bash
# Full topology snapshot
curl http://localhost:8000/api/v1/closedLoopLink/topology

# Shortest path from LOOP_A to LOOP_C
curl "http://localhost:8000/api/v1/closedLoopLink/path?sourceId=$LOOP_A&targetId=$LOOP_C"

# Downstream links from LOOP_A
curl "http://localhost:8000/api/v1/closedLoopLink/from/$LOOP_A"

# Upstream links into LOOP_B
curl "http://localhost:8000/api/v1/closedLoopLink/to/$LOOP_B"
```

### 7. Bulk creation (all-or-nothing)

```bash
curl -X POST http://localhost:8000/api/v1/closedLoopLink/bulk \
  -H 'Content-Type: application/json' \
  -d '{
    "items": [
      {"source": {"id": "'"$LOOP_A"'"}, "target": {"id": "'"$LOOP_B"'"}, "kind": "DAISY_CHAIN", "direction": "FORWARD"},
      {"source": {"id": "'"$LOOP_B"'"}, "target": {"id": "'"$LOOP_C"'"}, "kind": "DAISY_CHAIN", "direction": "FORWARD"}
    ]
  }'
```

If any link in the batch would close a cycle, the entire batch is
rejected and nothing is persisted.

## Lifecycle state machines

### ClosedLoop

`designed -> validated -> published -> active -> paused | error -> retired`

State transitions are explicit: `POST /api/v1/closedLoop/{id}/state` with
`{"targetState": "<state>"}`. The full state machine is enforced by the
`closed_loop.state_transition_invalid` envelope.

### Activity / Workflow

`designed -> validated -> published -> deprecated -> retired`

Cross-resource rules:

- A workflow cannot transition to `published` while any referenced
  activity is not yet `published` (or `deprecated`).
- An activity cannot transition to `retired` while a `published`
  workflow still references it.
- An activity cannot be `DELETEd` while ANY workflow references it.
- A workflow cannot be `DELETEd` while any closed loop references it.

## Daisy-chaining and topology semantics

A `ClosedLoopLink` connects two closed loops with a directed edge.
Allowed `kind` values:

| Kind            | Meaning                                                |
|-----------------|--------------------------------------------------------|
| `DAISY_CHAIN`   | Linear forward link between peer loops.                |
| `HIERARCHICAL`  | Parent -> child supervision / decomposition.           |
| `FEEDBACK`      | Bidirectional coupling between peer loops.              |
| `SHADOW`        | Read-only mirror; queries only, never mutates.          |

The server enforces cycle-freedom (no link may close a directed cycle in
the existing graph) for every write, but does NOT enforce
kind-specific topology rules. Those are an application-layer concern;
see the Slice 3 deferred-work note.

## Downloading the OpenAPI contract

```bash
curl http://localhost:8000/openapi.json > openapi.json
```

The committed snapshot lives at `schemas/openapi/openapi.json`. The
Postman collection is regenerated into `schemas/openapi/postman/`.

## Authentication

Slice 1-3 ship without authentication. The HTTP server is local-only by
default. Production deployments MUST add an authentication layer
(planned for Slice 4).

## OAS validation

The committed OAS document is validated by:

- `openapi-spec-validator` against the OAS 3.1 schema.
- The in-repo `clam-oas-validator` toolkit against the CLAM OAS
  profile.

Both checks are wired into the CI test job.
