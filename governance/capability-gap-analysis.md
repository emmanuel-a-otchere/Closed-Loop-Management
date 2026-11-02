---
artifact_id: capability-gap-analysis-2026-10
cr_id: CR-CLAM-001
stage: 2 (Capability analysis against the seven domains)
status: Complete (draft for Stage 2 review)
prepared: 2026-10-20
baseline: main at 95f7714
inputs:
  - governance/capability-inventory.md (Stage 1)
  - governance/CR/CR-CLAM-001-normative-capability-model.md (domain index)
  - governance/reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md (assessment context)
plan: governance/PLANS/RECON-CLOSURE-PLAN-2026-10.md
---

# CLAM Capability Gap Analysis (Stage 2)

## 1. Purpose

Analyse the repository's actual capability against the seven
CLAM capability domains and produce the explicit implemented /
partial / proposed / unverified classification that CR-CLAM-001
AC-004, AC-005, and AC-006 require. Each row cites repository
evidence (source file, endpoint, test, or CI job); where the
evidence is absent the status is unverified and the row names the
CR that carries the closure.

Status vocabulary (per AC-006, statuses are explicit):

- **Implemented**: working code with passing tests as evidence.
- **Partial**: working code exists but a named dimension of the
  capability is absent or untested.
- **Proposed**: a governance artefact (CR, schema proposal, plan)
  exists but no working code.
- **Unverified**: claimed but without test or contract evidence.

## 2. Domain-by-domain analysis

### 2.1 Closed-Loop Engineering (CLAM-CAP-ENG)

| Capability | Status | Evidence | Gap / carrier |
| --- | --- | --- | --- |
| Closed-loop CRUD (design record, identity) | Implemented | `routers/closed_loop.py` (14 routes); `tests/test_api.py` | -- |
| Decision-model specification (OODA / MAPE / CUSTOM) | Implemented | `routers/decision_model.py`; `datasets/examples/decision-model-*.json` | -- |
| Goal and constraint modelling | Partial | `routers/goal.py` (goals + targets) | Constraints not modelled; carried by CR-CLAM-002 / CR-CLAM-007 (policy schema proposal-0.1) |
| Workflow / activity composition | Implemented | `routers/workflow.py`, `routers/activity.py`; `datasets/examples/workflow-feedback-fan-control.json` | -- |
| Intent / requirements / acceptance criteria | Proposed | `governance/schemas/proposals/` + `CR-requirements.csv` | No intent entity; carried by CR-CLAM-003 |
| Design verification (fitness for operation) | Partial | `machines/toolkits/compare_decisions/`, `topology_script/` | No requirements-bound verdict; carried by CR-CLAM-004 |
| Simulation / scenario analysis | Partial | `machines/toolkits/loop_simulator/`, `goalsim/` (simulated, no versioned scenario contract) | Carried by CR-CLAM-005 |

### 2.2 Closed-Loop Lifecycle Management (CLAM-CAP-LCM)

| Capability | Status | Evidence | Gap / carrier |
| --- | --- | --- | --- |
| Typed lifecycle state machine | Implemented | `routers/closed_loop.py` state routes; state-machine diagram; 179-test suite | -- |
| Lifecycle record with identity + version | Partial | `store.py` entity tables | Provenance/version conventions partial; carried by CR-CLAM-002 (MODEL-002) |
| Transition authorisation | Partial | `auth.py` scope model on mutating routes | Transition-guard-level authorisation policy not modelled; carried by CR-CLAM-007 |
| Lifecycle evidence (state-change record) | Implemented | audit log + `routers/audit.py`, `stream.py` | -- |
| Separate state dimensions (lifecycle / execution / goal / assurance) | Proposed | CR-CLAM-002 (MODEL-001) | Single lifecycle state today |

### 2.3 Execution Integration and Control Boundaries (CLAM-CAP-EXE)

| Capability | Status | Evidence | Gap / carrier |
| --- | --- | --- | --- |
| External execution separation (no runtime in-repo) | Implemented (as a boundary) | No `machines/runtime/`; ADR-CLAM-0001 scope | -- |
| Activity interface referencing | Implemented | `routers/activity.py` kinds (sense / decide / act) | -- |
| Execution participation contracts | Proposed | CR-CLAM-002 / enrichment proposal | No contract vocabulary for execution mechanisms |
| Operational health vs lifecycle state | Partial | `routers/health.py` probes + metrics | No health vocabulary; carried by CR-CLAM-009 (OPS-001) |

### 2.4 Operational Management (CLAM-CAP-OPS)

| Capability | Status | Evidence | Gap / carrier |
| --- | --- | --- | --- |
| Liveness / readiness / metrics | Implemented | `routers/health.py`; metrics snapshot persistence (Slice 6 PR2) | -- |
| Operational event model | Proposed | CR-CLAM-009 (OPS-001/002) | Only probes + request-log tail exist |
| Stale / missing telemetry detection | Unverified | No code, no fixtures | Carried by CR-CLAM-009 (OPS-002) |
| Recovery traces and revalidation | Proposed | CR-CLAM-009 | No recovery-record concept |
| Audit retention / prune | Implemented | `routers/audit.py` prune routes (Slice 6 PR1) | -- |

### 2.5 Inter-Loop Coordination (CLAM-CAP-COO)

| Capability | Status | Evidence | Gap / carrier |
| --- | --- | --- | --- |
| Typed inter-loop links (incl. bulk, daisy-chain) | Implemented | `routers/closed_loop_link.py` (11 routes); link fixtures | -- |
| Contract compatibility on links | Proposed | CR-CLAM-008 (COORD-001) | Link types exist, contracts do not |
| Conflict handling (goal, resource, failure propagation) | Unverified | No code, no scenarios | Carried by CR-CLAM-008 (COORD-002) |
| System-level outcome evaluation | Proposed | CR-CLAM-008 | -- |

### 2.6 Verification and Assurance (CLAM-CAP-VER)

| Capability | Status | Evidence | Gap / carrier |
| --- | --- | --- | --- |
| Test evidence pipeline | Implemented | 179 pytest tests + CI (test job) | -- |
| KPI reporting from traces | Partial | `machines/toolkits/kpi_calculator/` | Not bound to acceptance criteria |
| Evidence records (criterion, subject, version, origin) | Proposed | `governance/schemas/proposals/evidence-record.schema.json` (proposal-0.1) | Carried by CR-CLAM-006 (EVID-001/002) |
| Three-valued verification (satisfied / not / indeterminate) | Proposed | ADR-CLAM-0002 (Proposed), CR-CLAM-006 | -- |
| Simulated vs operational evidence separation | Unverified | Simulator emits traces without origin tags | Carried by CR-CLAM-005 (SIM-002) |
| Staged conformance validation | Partial | `machines/toolkits/oas_validator/` (single-stage) | Staged rule architecture carried by CR-CLAM-004 (CONF-001/002) |

### 2.7 Governance and Continuous Improvement (CLAM-CAP-GOV)

| Capability | Status | Evidence | Gap / carrier |
| --- | --- | --- | --- |
| Audit trail (append-only record of state changes) | Implemented | audit tables, SSE fan-out, `machines/toolkits/audit_consumer/` | -- |
| AuthN/AuthZ with scopes + token lifecycle | Implemented | `auth.py`, durable token store + rotation (Slice 6 PR3) | -- |
| Event export (webhooks + SSE) | Implemented | `routers/webhook.py` (HMAC), `stream.py` | -- |
| Traceability (requirement-to-artefact chain) | Partial | `governance/traceability/CR-requirements.csv` (manual, 18 rows) | No validator, no CI enforcement; carried by CR-CLAM-003 (TRACE-001/002) |
| CR / ADR governance programme | Implemented (as documents) | `governance/CR/`, `governance/ADR/`, plans, decision records | ADRs remain Proposed until Stage 4 ratification |
| Bounded-autonomy policy model | Proposed | `governance/schemas/proposals/policy.schema.json` (proposal-0.1) | Carried by CR-CLAM-007 (GOV-001/002) |
| Evidence-based maturity | Partial | `machines/toolkits/maturity_assessment/` (questionnaire + CSV) | Not evidence-bound; carried by CR-CLAM-010 (MAT-001/002) |

## 3. Aggregate status

| Domain | Implemented | Partial | Proposed | Unverified |
| --- | --- | --- | --- | --- |
| ENG | 3 | 3 | 1 | 0 |
| LCM | 2 | 3 | 1 | 0 |
| EXE | 2 | 1 | 1 | 0 |
| OPS | 2 | 0 | 2 | 1 |
| COO | 1 | 0 | 2 | 1 |
| VER | 1 | 2 | 2 | 1 |
| GOV | 3 | 2 | 1 | 0 |

The pattern matches the 2026-10-18 capability review: management
and lifecycle foundations are solid; the assurance
(VER), operational (OPS), and coordination (COO) domains carry the
concentration of partial / proposed / unverified capability, and
every one of those gaps is already carried by a named CR with
named requirements and acceptance criteria.

## 4. Conclusions feeding Stage 3

1. No finding in this analysis requires a new CR; every gap maps
   to CR-CLAM-002..010 already in the programme. Stage 3 should
   not open new scope.
2. The four unverified rows (stale-telemetry detection, conflict
   handling, simulated-evidence separation, and by extension
   KPI-to-criterion binding) are the highest-assurance-risk items;
   they map to the P1 slices 5 and 6 of the implementation plan.
3. AC-004 is satisfied by this analysis plus the Stage 1
   inventory (component-to-capability mapping). AC-005 is
   satisfied by the evidence column of every row. AC-006 is
   satisfied by the explicit four-value status classification.
4. The binding model is unchanged by this analysis; no
   compatibility assessment is triggered (AC-011 preserved).
