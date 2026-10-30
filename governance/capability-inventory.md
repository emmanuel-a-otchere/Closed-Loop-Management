---
artifact_id: capability-inventory-2026-10
cr_id: CR-CLAM-001
stage: 1 (Repository reconnaissance)
status: Complete (draft for Stage 1 review)
prepared: 2026-10-20
baseline: main at 29b77d0
plan: governance/PLANS/RECON-CLOSURE-PLAN-2026-10.md
---

# CLAM Repository Capability Inventory (Stage 1)

## 1. Purpose

Per the CR-CLAM-001 implementation procedure, Stage 1 produces a
repository capability inventory: a factual map of every
repository component, what it does, and which of the seven
capability domains (CLAM-CAP-ENG / LCM / EXE / OPS / COO / VER /
GOV) it supports today. This inventory makes no normative claims;
the gap analysis (Stage 2) and the capability model (Stage 3)
build on it.

## 2. Service components (`machines/service/clam/`)

| Component | Function | Domain support (observed) |
| --- | --- | --- |
| `routers/closed_loop.py` | CRUD + state transitions over closed loops (14 routes) | LCM, ENG |
| `routers/decision_model.py` | CRUD over OODA / MAPE / CUSTOM decision models | ENG |
| `routers/goal.py` | CRUD over goals, target values, achievement state | ENG, VER (partial) |
| `routers/workflow.py` | CRUD over workflows (feedforward / feedback paths) | ENG |
| `routers/activity.py` | CRUD over activities (sense / decide / act kinds) | ENG, EXE (interface only) |
| `routers/closed_loop_link.py` | CRUD over typed inter-loop links, bulk import, daisy chains | COO |
| `routers/audit.py` | Audit log read + prune (retention) | GOV |
| `routers/auth.py` | Token issue / list / revoke / rotate, scope model | GOV |
| `routers/webhook.py` | Outbound webhook subscriptions + HMAC-signed deliveries | GOV (event export) |
| `routers/stream.py` | SSE audit stream with entity filters | GOV (event export) |
| `routers/request_log.py` | Request log tail | OPS (partial) |
| `routers/health.py` | Liveness / readiness probes, Prometheus /metrics, metrics snapshot | OPS |
| `store.py` | SQLite (aiosqlite) persistence for all entities, audit, tokens, webhook tables, metrics snapshots, retention/prune | (cross-cutting) |
| `models.py` | Pydantic v2 binding models, source of truth for the OAS 3.1 contract | (cross-cutting) |
| `auth.py` | Scope enum, principal resolution, durable TokenStore with fingerprinting | GOV |
| `main.py` | App entry, lifespan (metrics restore/snapshot), OpenAPI metadata | (cross-cutting) |

## 3. Toolkits (`machines/toolkits/`)

| Toolkit | Function | Domain support (observed) |
| --- | --- | --- |
| `oas_validator` | Profile-level OAS 3.1 validation with CLAM rules | GOV (conformance, partial) |
| `loop_simulator` | Drives an OODA / MAPE / CUSTOM decision cycle against the API, emits traces | VER (behaviour, partial), ENG (simulation, partial) |
| `erd_to_oas` | Reads .xlsx ERD, emits OAS schema fragment | ENG (modelling aid) |
| `maturity_assessment` | Questionnaire + CSV scoring template | GOV (maturity, unverified depth) |
| `kpi_calculator` | Consumes simulator trace, emits KPI report | VER (metrics, partial) |
| `goalsim` | Goal-achievement projection over N ticks per decision-model kind | VER (goal satisfaction, simulated only) |
| `compare_decisions` | Side-by-side decision-model outcome comparison | ENG (design evaluation) |
| `topology_script` | Topology-as-script; emits runnable script recreating a loop graph via the API | ENG, COO (composition) |
| `audit_consumer` | Tails SSE audit stream, exports CSV/JSON | GOV (audit consumption) |

## 4. Schemas, datasets, docs

| Artefact | Function | Domain support (observed) |
| --- | --- | --- |
| `schemas/openapi/openapi.json` | Generated OAS 3.1 contract snapshot, CI-validated | GOV (contract governance) |
| `schemas/openapi/postman/` | Postman v2.1 collection export | ENG (onboarding) |
| `schemas/data-model/clam-data-model-1.0.md` | Binding entity model | LCM, ENG |
| `governance/schemas/proposals/{scenario,evidence-record,policy}.schema.json` | Proposal-stage JSON Schemas (proposal-0.1) | VER, GOV (proposed, unbound) |
| `governance/traceability/CR-requirements.csv` | 18-row requirement-to-CR mapping (manual) | GOV (traceability, unvalidated) |
| `governance/CR/CR-CLAM-001..010` | Canonical CR programme with AC-NNN criteria | GOV |
| `governance/ADR/ADR-CLAM-0001/0002` | Scope + successful-operation decisions (Proposed) | GOV |
| `datasets/examples/` | 20+ reference payloads per endpoint/toolkit | ENG (examples) |
| `docs/conceptual/paradigm.md` | Position paper, management plane vs execution | (conceptual) |
| `docs/diagrams/` | ERD, lifecycle, state machine, sequence, use cases | ENG (documentation) |

## 5. Quality and CI

| Component | Function | Domain support (observed) |
| --- | --- | --- |
| `tests/` | 179 pytest tests (130 in test_api.py, 4 toolkit suites) | VER (test evidence) |
| `.github/workflows/ci.yml` | pytest + coverage, ruff, mypy, OAS 3.1 validation, oas-validator, cardinal-rules gates (D-004/D-005/author), snapshot check (hardened 2026-10-20) | GOV (assurance pipeline) |
| `context/AGENT-DOCTRINE.md` | Cardinal rules, kanban discipline, branch-per-task | GOV |

## 6. Inventory observations (non-normative)

- No component under `machines/runtime/` exists; execution
  remains external, consistent with the scope ADR.
- Evidence production is simulated-only: the loop_simulator and
  goalsim toolkits produce traces/tables, but no evidence-record
  binding exists yet (CR-CLAM-005/006 scope).
- The traceability CSV has no validator and no CI enforcement
  (CR-CLAM-003 scope).
- The conformance surface is a single-stage OAS validator
  (CR-CLAM-004 calls for a staged architecture).
- Operational event model and health vocabulary beyond probes +
  metrics are absent (CR-CLAM-009 scope).
- Maturity scoring is not bound to evidence rows (CR-CLAM-010
  scope).

These observations feed the Stage 2 gap analysis.
