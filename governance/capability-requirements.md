---
artifact_id: capability-requirements-1.0
cr_id: CR-CLAM-001
stage: 3 (Normative specification)
status: Complete (draft for Stage 3 review)
prepared: 2026-10-20
normative: true
inputs:
  - governance/capability-model.md
  - governance/architecture-boundaries.md
  - governance/capability-gap-analysis.md (status values)
  - governance/traceability/CR-requirements.csv (carrier CRs)
---

# CLAM Capability Requirements Catalogue

## 1. Purpose

The normative requirement catalogue for the CLAM capability.
Every requirement has a stable identifier (per the AC-007 and
AC-008 acceptance criteria), a testable statement, an applicable
verification method, a status, and dependencies. The mapping of
each requirement to implementation, evidence, and follow-on CR
lives in
[`capability-traceability.md`](capability-traceability.md).

Status values are the Stage 2 classification: **implemented**,
**partial**, **proposed**, **unverified**.

## 2. ENG: Closed-Loop Engineering

- **CLAM-CAP-ENG-001.** A closed-loop design shall be assessable
  against its declared requirements and acceptance criteria.
  Verification: requirements-bound design review; test fixtures.
  Status: proposed (CR-CLAM-003). Depends on: ENG-002.
- **CLAM-CAP-ENG-002.** A closed-loop design shall declare its
  decision model (OODA / MAPE / CUSTOM), goals, and workflow
  composition before it may enter lifecycle validation.
  Verification: API validation tests. Status: implemented.
- **CLAM-CAP-ENG-003.** A closed-loop design shall be simulatable
  against versioned scenarios with disturbances and acceptance
  criteria before activation.
  Verification: scenario acceptance tests. Status: proposed
  (CR-CLAM-005, SIM-001). Depends on: ENG-001.

## 3. LCM: Closed-Loop Lifecycle Management

- **CLAM-CAP-LCM-001.** A managed closed loop shall have a
  uniquely identifiable lifecycle record.
  Verification: API identity tests. Status: implemented.
- **CLAM-CAP-LCM-002.** Every lifecycle transition shall be
  explicit, authorised, and recorded in an append-only audit
  trail.
  Verification: audit + auth tests. Status: implemented.
- **CLAM-CAP-LCM-003.** Lifecycle state, execution state, goal
  state, and assurance state shall be represented as separate
  dimensions that may change independently.
  Verification: state-dimension interaction tests. Status:
  proposed (CR-CLAM-002, MODEL-001).
- **CLAM-CAP-LCM-004.** Identity, version, provenance, and
  relationship integrity conventions shall be defined and
  enforced for every managed artefact.
  Verification: model/schema review. Status: partial
  (CR-CLAM-002, MODEL-002).

## 4. EXE: Execution Integration and Control Boundaries

- **CLAM-CAP-EXE-001.** Every activity that performs work shall
  reference an external execution mechanism through a declared
  contract; CLAM shall not execute loop work.
  Verification: boundary review; absence of runtime code.
  Status: implemented (as a boundary, B-04).
- **CLAM-CAP-EXE-002.** Execution participation contracts shall
  state input/output expectations, preconditions, postconditions,
  failure-reporting obligations, and provenance requirements.
  Verification: contract conformance fixtures. Status: proposed
  (CR-CLAM-002 / enrichment proposal).

## 5. OPS: Operational Management

- **CLAM-CAP-OPS-001.** Operational health shall be distinguishable
  from lifecycle state and from verified goal achievement.
  Verification: model + API tests. Status: partial (probes and
  metrics exist; vocabulary proposed by CR-CLAM-009, OPS-001).
- **CLAM-CAP-OPS-002.** Stale or missing telemetry shall be
  detectable, and recovery events shall be traceable including
  revalidation requirements.
  Verification: event-sequence tests. Status: unverified
  (CR-CLAM-009, OPS-002).

## 6. COO: Inter-Loop Coordination

- **CLAM-CAP-COO-001.** Typed inter-loop links shall be validatable
  for contract compatibility between the connected loops.
  Verification: compatibility fixtures. Status: partial (typed
  links implemented; contracts proposed by CR-CLAM-008,
  COORD-001).
- **CLAM-CAP-COO-002.** Conflict handling (goal, resource,
  failure-propagation conflicts) and system-level outcomes shall
  be traceable across linked loops.
  Verification: conflict scenario tests. Status: unverified
  (CR-CLAM-008, COORD-002).

## 7. VER: Verification and Assurance

- **CLAM-CAP-VER-001.** A verification result shall identify the
  criterion being evaluated, the subject, and the applicable
  model/configuration version.
  Verification: schema and reference tests. Status: proposed
  (CR-CLAM-006, EVID-001).
- **CLAM-CAP-VER-002.** Verification shall represent three
  values: satisfied, not satisfied, and indeterminate.
  Verification: outcome-verification tests. Status: proposed
  (CR-CLAM-006, EVID-002; anchored by ADR-CLAM-0002).
- **CLAM-CAP-VER-003.** Simulated evidence shall be distinguishable
  from operational evidence by a mandatory origin tag.
  Verification: trace schema tests. Status: unverified
  (CR-CLAM-005, SIM-002).
- **CLAM-CAP-VER-004.** Validation shall be layered (schema,
  semantic, lifecycle, traceability, release) and emit
  deterministic diagnostic reports.
  Verification: CI and fixture suite. Status: partial
  (single-stage OAS validator; staged architecture proposed by
  CR-CLAM-004, CONF-001/002).

## 8. GOV: Governance and Continuous Improvement

- **CLAM-CAP-GOV-001.** Every change to a managed loop or to the
  CLAM capability shall be traceable to an approved change
  record (CR / ADR / decision) with stable identifiers.
  Verification: traceability review. Status: implemented for the
  programme; traceability chain validation proposed by
  CR-CLAM-003 (TRACE-001).
- **CLAM-CAP-GOV-002.** Dangling, contradictory, or unverified
  links in the requirement-to-artefact chain shall be detectable.
  Verification: negative fixture tests. Status: unverified
  (CR-CLAM-003, TRACE-002).
- **CLAM-CAP-GOV-003.** Applicable permissions, constraints, and
  enforcement responsibility for bounded autonomy shall be
  declared, with safe-response, recovery, and revalidation
  requirements defined.
  Verification: policy and decision-table tests. Status: proposed
  (CR-CLAM-007, GOV-001/002).
- **CLAM-CAP-GOV-004.** Maturity scores shall be traceable to
  criteria and evidence, and critical gaps shall not be maskable
  by aggregate scores.
  Verification: scoring tests. Status: partial (toolkit exists;
  evidence binding proposed by CR-CLAM-010, MAT-001/002).

## 9. Catalogue rules

1. Identifiers are stable; a requirement is never renumbered or
   reused. Changes to a requirement create a superseding ID with
   a dated note.
2. A requirement's status may only move to **implemented** when
   the traceability matrix cites passing evidence (evidence
   before claim).
3. New requirements arrive through the CR process and must cite
   their domain and the boundary row they operate under.
