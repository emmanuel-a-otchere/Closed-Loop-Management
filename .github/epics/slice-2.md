# Epic -- Slice 2: Workflow + Activity + Goal CRUD

**Milestone:** v1.0.0 MVP
**Issue:** #2 (file after Slice 1 lands)
**Cards (Kanban):** see http://192.168.50.160:7000/board/14

## Goal

Expand CLAM beyond the Slice 1 surfaces. CRUD Goals (per closed loop,
workflow, or activity), Workflows (with feedforward / feedback path
semantics), and Activities (the unit of work within a workflow). The
data model is already defined at
`docs/data-model/clam-data-model-1.0.md`; Slice 2 makes it reachable.

## Acceptance criteria

- [ ] `POST/GET/PATCH/DELETE /api/v1/closedLoop/{id}/goal`
- [ ] `POST/GET/PATCH/DELETE /api/v1/closedLoop/{id}/workflow`
- [ ] `POST/GET/PATCH/DELETE /api/v1/closedLoop/{id}/workflow/{wid}/activity`
- [ ] Goal target direction (AT_LEAST / AT_MOST / EXACTLY) enforced at the Pydantic layer.
- [ ] Workflow path (FEEDFORWARD / FEEDBACK) enforced.
- [ ] 12+ new pytest tests.
- [ ] Downloadable examples for workflows and activities.
- [ ] OAS regenerated; `openapi/openapi.json` snapshot updated.

## Non-goals (Slice 2)

- ClosedLoopLink CRUD (Slice 3).
- Authentication (Slice 4).