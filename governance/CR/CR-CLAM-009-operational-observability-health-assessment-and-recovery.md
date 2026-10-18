# CR-CLAM-009: Operational Observability, Health Assessment, and Recovery

| Field | Value |
|---|---|
| CR ID | CR-CLAM-009 |
| Status | Proposed |
| Priority | P2 |
| Change class | Operational model and tooling |
| Repository | `emmanuel-a-otchere/Closed-Loop-Management` |
| Dependencies | CR-CLAM-002, CR-CLAM-006, and CR-CLAM-007; coordinate with CR-CLAM-008 for dependency failure propagation. |

## 1. Problem statement

A lifecycle state and periodic KPI report do not provide a complete operational account of a loop's condition, telemetry freshness, incidents, degradation, recovery actions, or event history.

## 2. Objective

Define a common operational event and health model, including telemetry references, condition assessment, incident linkage, recovery history, and lifecycle interactions.

## 3. Scope

- Define OperationalEvent, HealthAssessment, incident/exception references, telemetry/observation metadata, and recovery-action records or equivalent structures.
- Separate lifecycle state from health condition, execution progress, goal disposition, and assurance disposition.
- Specify observation timestamps, event time versus ingestion time, freshness, quality, source, correlation, and version association.
- Define degraded conditions, alerts, incident classifications, and recovery outcomes.
- Specify how operational events can trigger review, suspension, revalidation, or other policy-governed transitions.
- Define retention, volume, and data-minimisation considerations without mandating a telemetry platform.

## 4. Required deliverables

- Operational event and health model.
- Health and degraded-condition vocabulary.
- Recovery and incident traceability requirements.
- Example operational event sequence.
- Integration contract for operational telemetry and existing API/tooling.

## 5. Acceptance criteria

- [ ] **AC-009-01:** Lifecycle state and operational health are separately represented.
- [ ] **AC-009-02:** Stale, missing, invalid, and healthy observations are distinguishable.
- [ ] **AC-009-03:** Events can be correlated with loop, configuration/deployment version, and relevant incident/recovery record.
- [ ] **AC-009-04:** Recovery outcomes and subsequent validation status are traceable.
- [ ] **AC-009-05:** Operational events do not automatically authorise actions outside the policy contract.
- [ ] **AC-009-06:** Event ordering, clock assumptions, and retention limitations are documented.

## 6. Out of scope

Replacing a full observability stack; requiring a specific monitoring vendor; retaining unlimited raw telemetry in the CLAM management store.

## 7. Dependencies and sequencing

CR-CLAM-002, CR-CLAM-006, and CR-CLAM-007; coordinate with CR-CLAM-008 for dependency failure propagation.

This CR is a proposed specification and change boundary. Dependencies must be verified against the repository's accepted CR/ADR state before implementation. A dependency listed here is not evidence that the upstream CR has been approved or implemented.

## 8. Verification approach

Event-schema tests, stale/missing telemetry cases, recovery trace tests, and lifecycle-interaction tests.

## 9. Data-model impact

This CR is expected to enrich or consume the CLAM information model as described in `docs/data-model/CLAM-DATA-MODEL-ENRICHMENT-PROPOSAL.md`. Candidate concepts are not automatically binding entities. Before implementation, reconcile them with existing Pydantic models, OpenAPI schemas, persistence, examples, and API operations. Avoid duplicating a concept already represented adequately.

## 10. Compatibility and migration

Preserve the current binding model and API behaviour until the required compatibility decision is accepted. Any breaking change must specify a versioning strategy, migration/adapter path, deprecation period where appropriate, and regression evidence.

## 11. Follow-on work

CR-CLAM-010.

## 12. Governance notes

- Investigation precedes implementation where semantics or architecture remain uncertain.
- Record material architectural decisions in ADRs under repository governance.
- Implement only the scope approved for this CR.
- Update traceability and conformance tests with each delivered requirement.
- Do not claim a capability is implemented until evidence supports the claim.
