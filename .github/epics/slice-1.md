# Epic -- Slice 1: Repo revamp + API skeleton

**Milestone:** v1.0.0 MVP
**Issue:** #1 (open this when slicing)
**Cards (Kanban):** see http://192.168.50.160:7000/board/14

## Goal

Reopen `emmanuel-a-otchere/Closed-Loop-Management` as a live, served REST API
project. Preserve the 2022 conceptual model; layer a typed, OAS-3.1-backed
FastAPI service on top of it. Land repo scaffolding, governance, GitHub
Project board, Kanban board, CI gates, and downloadable-and-testable
artefacts.

## Acceptance criteria

- [ ] Repo has new README framing CLAM as the API.
- [ ] Legacy 2022 ERD preserved at `docs/data-model/legacy-2022-erd.xlsx`.
- [ ] OAS-backed data model at `docs/data-model/clam-data-model-1.0.md`.
- [ ] FastAPI app in `api/clam/` serving:
  - [ ] `/health`
  - [ ] `/docs` (Swagger UI)
  - [ ] `/redoc` (ReDoc)
  - [ ] `/openapi.json` (OAS 3.1)
  - [ ] `POST/GET/PATCH/DELETE /api/v1/closedLoop`
  - [ ] `GET/POST /api/v1/closedLoop/{id}/state`
  - [ ] `POST/GET/DELETE /api/v1/decisionModel`
- [ ] State machine: `designed -> validated -> published -> active -> paused/error -> retired`
- [ ] Error envelope `{code, message, details}` consistent across endpoints.
- [ ] Pagination envelope on list endpoints.
- [ ] 9+ pytest tests, all green.
- [ ] `ruff check` and `mypy api/` clean.
- [ ] CI workflow `.github/workflows/ci.yml` runs pytest, ruff, mypy, OAS validation, D-004/D-005/cardinal-author gate.
- [ ] GitHub Project v2 board linked to repo.
- [ ] Kanban board 14 seeded with WBS epic cards.
- [ ] Downloadable examples: OODA closed loop JSON, MAPE decision model JSON.
- [ ] Postman collection generated from the live OAS.
- [ ] `context/AGENT-DOCTRINE.md` linking repo to channel + kanban + cron.

## Non-goals (Slice 1)

- Goal / Workflow / Activity CRUD (Slice 2).
- ClosedLoopLink CRUD and the choreograph interlink semantics (Slice 3).
- Authentication / authorization (Slice 4).
- Multi-tenant isolation (Slice 4).
- Live deployment (Slice 4).

## Tasks (WBS)

1. Repo revamp (move ERD, write new README).
2. OAS data model doc.
3. FastAPI skeleton + Pydantic models + SQLite store.
4. ClosedLoop CRUD + state endpoints + tests.
5. DecisionModel CRUD + tests.
6. CI workflow + Spectral config + D-004/D-005 gate.
7. GitHub Project v2 board + WBS epics as issues.
8. Kanban board 14 seed.
9. Downloadable example payloads + Postman collection.
10. AGENT-DOCTRINE.md + companion kanban-discipline skill.
11. Snapshot doc at `~/.hermes/profiles/coder/kanban/closed-loop-automation-kanban-snapshot-2026-10-10.md`.