# CR-CLAM-008: Inter-Loop Coordination and Conflict Management

| Field | Value |
|---|---|
| CR ID | CR-CLAM-008 |
| Status | Proposed |
| Priority | P1 |
| Change class | Cross-loop model and coordination contracts |
| Repository | `emmanuel-a-otchere/Closed-Loop-Management` |
| Dependencies | CR-CLAM-002, CR-CLAM-003, CR-CLAM-005, and CR-CLAM-007. |

## 1. Problem statement

A typed link between loops expresses connectivity but does not establish interface compatibility, dependency semantics, shared-resource behaviour, conflict resolution, or system-level outcome correctness.

## 2. Objective

Define the information model and validation requirements for coordinated loops, including contracts, dependencies, conflicts, failure propagation, and system-level verification.

## 3. Scope

- Specify link/coordination contract semantics: source, target, relationship type, direction, exchanged information, timing/quality expectations, and version compatibility.
- Represent dependency ordering and availability requirements.
- Define conflict categories covering incompatible goals, actions, policies, and shared-resource demand.
- Define coordination policy references, resolution responsibility, escalation, and unresolved-conflict handling.
- Specify propagation and containment of dependency failure.
- Define system-level outcome and assurance assessment across participating loops.

## 4. Required deliverables

- Inter-loop coordination model.
- Compatibility and conflict rules.
- Coordination scenarios and fixtures.
- System-level verification requirements.
- Migration guidance for existing ClosedLoopLink records.

## 5. Acceptance criteria

- [ ] **AC-008-01:** Every link has a defined semantic type and valid source/target references.
- [ ] **AC-008-02:** Incompatible interface/model versions can be detected.
- [ ] **AC-008-03:** Conflict handling is explicit; unresolved material conflicts cannot be reported as resolved.
- [ ] **AC-008-04:** Dependency failures and their affected loops can be traced.
- [ ] **AC-008-05:** System-level goal assessment does not rely solely on the individual status of each loop.
- [ ] **AC-008-06:** Existing links remain interpretable or have a documented migration.

## 6. Out of scope

Building a distributed scheduler or consensus engine; prescribing a specific graph database or message broker; assuming all loops require central orchestration.

## 7. Dependencies and sequencing

CR-CLAM-002, CR-CLAM-003, CR-CLAM-005, and CR-CLAM-007.

This CR is a proposed specification and change boundary. Dependencies must be verified against the repository's accepted CR/ADR state before implementation. A dependency listed here is not evidence that the upstream CR has been approved or implemented.

## 8. Verification approach

Reference-integrity tests, incompatible-link fixtures, conflict scenarios, dependency-failure tests, and system-level outcome tests.

## 9. Data-model impact

This CR is expected to enrich or consume the CLAM information model as described in `docs/data-model/CLAM-DATA-MODEL-ENRICHMENT-PROPOSAL.md`. Candidate concepts are not automatically binding entities. Before implementation, reconcile them with existing Pydantic models, OpenAPI schemas, persistence, examples, and API operations. Avoid duplicating a concept already represented adequately.

## 10. Compatibility and migration

Preserve the current binding model and API behaviour until the required compatibility decision is accepted. Any breaking change must specify a versioning strategy, migration/adapter path, deprecation period where appropriate, and regression evidence.

## 11. Follow-on work

CR-CLAM-009 and 010.

## 12. Governance notes

- Investigation precedes implementation where semantics or architecture remain uncertain.
- Record material architectural decisions in ADRs under repository governance.
- Implement only the scope approved for this CR.
- Update traceability and conformance tests with each delivered requirement.
- Do not claim a capability is implemented until evidence supports the claim.
