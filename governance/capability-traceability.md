---
artifact_id: capability-traceability-1.0
cr_id: CR-CLAM-001
stage: 3 (Normative specification)
status: Complete (draft for Stage 3 review)
prepared: 2026-10-20
normative: true
inputs:
  - governance/capability-requirements.md
  - governance/capability-inventory.md
  - governance/capability-gap-analysis.md
---

# CLAM Capability Traceability Matrix

## 1. Purpose

Maps every normative requirement in
[`capability-requirements.md`](capability-requirements.md) to its
domain, implementation artefacts, verification method, evidence,
status, dependencies, and follow-on CR. Satisfies AC-004 and
AC-008. Where implementation is absent, the follow-on CR column
carries the requirement instead; no requirement is left
unowned.

## 2. Matrix

| Requirement | Implementation | Verification | Evidence | Status | Follow-on CR |
| --- | --- | --- | --- | --- | --- |
| ENG-001 | -- (requirements entity absent) | Design review fixtures | -- | Proposed | CR-CLAM-003 (TRACE-001) |
| ENG-002 | `routers/closed_loop.py`, `routers/decision_model.py`, `routers/goal.py`, `routers/workflow.py` | `tests/test_api.py` CRUD + validation | 179-test suite green | Implemented | -- |
| ENG-003 | `machines/toolkits/loop_simulator/`, `goalsim/` (traces only) | Scenario acceptance tests | -- | Proposed | CR-CLAM-005 (SIM-001) |
| LCM-001 | `routers/closed_loop.py` + `store.py` entities | API identity tests | test suite | Implemented | -- |
| LCM-002 | `routers/closed_loop.py` state routes + `routers/audit.py`, `stream.py`, `auth.py` | Audit + scope tests | test suite; SSE fixtures | Implemented | -- |
| LCM-003 | -- (single lifecycle state today) | State-dimension interaction tests | -- | Proposed | CR-CLAM-002 (MODEL-001) |
| LCM-004 | `store.py` entity tables (identity + version partial) | Model/schema review | binding model 1.0 | Partial | CR-CLAM-002 (MODEL-002) |
| EXE-001 | No runtime code; `routers/activity.py` reference model | Boundary review; repo inspection | repo tree | Implemented (boundary B-04) | -- |
| EXE-002 | -- | Contract conformance fixtures | -- | Proposed | CR-CLAM-002 / enrichment |
| OPS-001 | `routers/health.py` probes + metrics snapshot | Model + API tests | test suite | Partial | CR-CLAM-009 (OPS-001) |
| OPS-002 | -- | Event-sequence tests | -- | Unverified | CR-CLAM-009 (OPS-002) |
| COO-001 | `routers/closed_loop_link.py` (typed links, bulk, daisy-chain) | Link fixtures + compatibility fixtures | test suite; link datasets | Partial | CR-CLAM-008 (COORD-001) |
| COO-002 | -- | Conflict scenario tests | -- | Unverified | CR-CLAM-008 (COORD-002) |
| VER-001 | -- (proposal schema `evidence-record.schema.json` proposal-0.1) | Schema + reference tests | -- | Proposed | CR-CLAM-006 (EVID-001) |
| VER-002 | -- (ADR-CLAM-0002 Proposed) | Outcome-verification tests | -- | Proposed | CR-CLAM-006 (EVID-002) |
| VER-003 | `machines/toolkits/loop_simulator/` traces (no origin tag) | Trace schema tests | -- | Unverified | CR-CLAM-005 (SIM-002) |
| VER-004 | `machines/toolkits/oas_validator/` (single-stage) + CI oas-validate job | CI and fixture suite | CI green | Partial | CR-CLAM-004 (CONF-001/002) |
| GOV-001 | `governance/CR/`, `ADR/`, `decisions/`, `PLANS/`; this matrix | Traceability review | governance tree | Implemented (documents); validation proposed | CR-CLAM-003 (TRACE-001) |
| GOV-002 | `governance/traceability/CR-requirements.csv` (manual) | Negative fixture tests | -- | Unverified | CR-CLAM-003 (TRACE-002) |
| GOV-003 | `governance/schemas/proposals/policy.schema.json` (proposal-0.1) | Policy + decision-table tests | -- | Proposed | CR-CLAM-007 (GOV-001/002) |
| GOV-004 | `machines/toolkits/maturity_assessment/` (questionnaire + CSV) | Scoring tests | -- | Partial | CR-CLAM-010 (MAT-001/002) |

## 3. Interpretation rules

1. A row with an empty implementation and a follow-on CR is a
   governed gap, not an unowned one.
2. Status transitions to Implemented only when the Evidence
   column cites a concrete passing artefact (test run, CI job,
   fixture, or governance review record).
3. When CR-CLAM-003 lands the formal traceability register, this
   matrix is superseded by it and this file records the
   succession (supersession rule from the requirements
   catalogue).
