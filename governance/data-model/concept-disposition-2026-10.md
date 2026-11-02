---
artifact_id: concept-disposition-2026-10
cr_id: CR-CLAM-001
stage: 3 (Normative specification)
status: Complete (draft for Stage 3 review)
prepared: 2026-10-20
decision_gate: governance/data-model/CLAM-DATA-MODEL-ENRICHMENT-PROPOSAL.md section 4
principle_bias: minimise entity proliferation (modelling principle 10)
---

# Concept Disposition Table (2026-10)

## 1. Purpose

Record the binding disposition for every candidate concept in
the enrichment proposal, per the concept decision gate defined
in `CLAM-IMPLEMENTATION-PLAN-2026-10.md` section 4. Every
CR-CLAM-002..010 binding-model slice must cite this table for
each concept it introduces.

Disposition values:

- **(A) Embedded value object** within an existing entity.
- **(B) Referenced resource** under a new path.
- **(C) Event record** under an event-streaming endpoint.
- **(D) External reference** whose payload lives outside CLAM.
- **(E) Deferred** to a future CR with rationale.

## 2. Disposition table

| Concept | Disposition | Rationale | Cited by |
| --- | --- | --- | --- |
| `Intent` | (B) Referenced resource | Declares purpose + context; reused across loops and versions; own lifecycle and audit requirements | CR-CLAM-003 |
| `Requirement` | (B) Referenced resource | Stable identity is normative (ENG-001, GOV-001); versioned, cross-loop reuse | CR-CLAM-003 |
| `Constraint` | (A) Embedded value object on Intent/Requirement first; promotes to (B) only if cross-loop reuse demands it | Minimises entity proliferation; constraints are usually scoped to one design | CR-CLAM-003, CR-CLAM-007 |
| `Assumption` | (A) Embedded value object | Validation/review status is an attribute of the design context, not an independent resource | CR-CLAM-003 |
| `CapabilitySpecification` / `CapabilityClaim` | (E) Deferred | Reuse canonical capability semantics rather than local redefinition; no binding change justified before the capability model is exercised | -- |
| `Observation` | (C) Event record | High-volume, append-oriented, time-stamped; streaming endpoint fits the existing SSE/audit fan-out pattern | CR-CLAM-006, CR-CLAM-009 |
| `DecisionRecord` | (C) Event record | Per-instance outcome; identity is the event, not a managed resource | CR-CLAM-006, CR-CLAM-007 |
| `ActionExecution` | (D) External reference + (C) thin event record | Attempted actions are emitted by external execution; CLAM stores the record and references the external payload | CR-CLAM-006/007/009 |
| `Outcome` | (A) Embedded value object on VerificationResult | Evaluated condition; no independent lifecycle beyond the verification that records it | CR-CLAM-006 |
| `VerificationResult` | (B) Referenced resource | Versioned result with disposition, method, evidence references; independently queryable (VER-001/002) | CR-CLAM-006 |
| `EvidenceRecord` | (B) Referenced resource | Reusable across verification results; provenance + integrity metadata require stable identity | CR-CLAM-006 |
| `Policy` | (B) Referenced resource | Versioned governance object; enforcement external by default (B-08) | CR-CLAM-007 |
| `Deployment` / `ConfigurationVersion` | (B) Referenced resource | Binds operation/evidence to a released configuration; cross-entity references demand stable identity (LCM-004) | CR-CLAM-002, CR-CLAM-006/007 |
| `OperationalEvent` | (C) Event record | Append-only occurrence stream; matches the audit-event architecture | CR-CLAM-009 |
| `HealthAssessment` | (A) Embedded value object | Derived assessment at a point/window; explicitly not a lifecycle state (OPS-001) | CR-CLAM-009 |
| `Scenario` | (B) Referenced resource | Versioned simulation/test artefact, reused across regressions (ENG-003) | CR-CLAM-005 |
| `CoordinationContract` | (A) Embedded value object on ClosedLoopLink first | Attached to an existing governed relationship; promotes to (B) only if contracts are shared across links | CR-CLAM-008 |
| `ImprovementProposal` | (E) Deferred | The CR system already carries this role; a second proposal entity would duplicate governance (GOV-001) | -- |

## 3. Promotion rules

A concept lands as (A), (C), or (D) first wherever possible. It
is promoted to (B) only when a landed slice demonstrates at
least one of: cross-loop reuse, independent lifecycle/audit
requirements, or stable-identity references from other entities.
Promotion requires a compatibility assessment per
`MIGRATION-AND-COMPATIBILITY.md` in the promoting CR's slice.

## 4. Review

This table is binding for the CR-CLAM-002..010 programme from
the date above. Changes to a disposition require a dated
amendment in this file plus a reference from the CR that needs
the change; they do not require a new CR when the change occurs
inside the CR that cites the concept.
