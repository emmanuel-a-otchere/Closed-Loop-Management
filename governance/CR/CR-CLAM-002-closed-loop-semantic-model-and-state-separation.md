# CR-CLAM-002: Semantic Model Enrichment and State Separation

| Field | Value |
|---|---|
| CR ID | CR-CLAM-002 |
| Status | Proposed |
| Priority | P0 |
| Change class | Foundational information model |
| Repository | `emmanuel-a-otchere/Closed-Loop-Management` |
| Dependencies | CR-CLAM-001; reconcile against the current repository baseline before approval. |

## 1. Problem statement

The binding CLAM model provides a compact set of core entities and a lifecycle state, but it does not normatively separate management lifecycle, execution condition, goal disposition, and assurance disposition. Several concepts needed to describe requirements, constraints, observations, actions, outcomes, and evidence are not yet represented as a coherent model. Adding fields ad hoc would risk semantic ambiguity and incompatible extensions.

## 2. Objective

Define a versioned, implementation-neutral semantic and information model for CLAM, including state dimensions, core relationships, identity, temporal/provenance requirements, and extension rules. This CR enriches the underlying data model at the conceptual and specification levels; binding OpenAPI/Pydantic changes are permitted only after review of compatibility and migration implications.

## 3. Scope

- Review the existing binding model, Pydantic types, API contract, diagrams, legacy ERD lineage, examples, and tests.
- Define the meaning and boundaries of ClosedLoop, DecisionModel, Goal, Workflow, Activity, ClosedLoopLink, and ClosedLoopState.
- Specify candidate concepts for Intent, Requirement, Constraint, Observation, DecisionRecord, ActionExecution, Outcome, VerificationResult, EvidenceRecord, Policy, Deployment/ConfigurationVersion, OperationalEvent, Resource, and CoordinationContract.
- Define separate state dimensions for management lifecycle, execution condition, goal disposition, and assurance disposition; define their valid values and interaction rules without combining them into one state machine.
- Specify identity, version, timestamps, provenance, status history, cardinality, referential integrity, and extensibility conventions.
- Define the relationship between conceptual semantics, binding JSON/OpenAPI schemas, Pydantic implementation, persistence, and API resources.

## 4. Required deliverables

- Accepted conceptual data-model specification and entity/relationship glossary.
- State-dimension specification and transition/interaction table.
- Data-model change-impact and compatibility assessment.
- Updated model diagrams and representative records.
- List of concepts retained, merged, deferred, or rejected with rationale.

## 5. Acceptance criteria

- [ ] **AC-002-01:** Each retained concept has a definition, purpose, scope, identity rule where applicable, and authoritative relationships.
- [ ] **AC-002-02:** Lifecycle, execution, goal, and assurance status are independently represented and their interactions are specified.
- [ ] **AC-002-03:** Goal achievement is not inferred solely from lifecycle state or successful action execution.
- [ ] **AC-002-04:** Every new relationship has defined direction, cardinality, meaning, and integrity constraints.
- [ ] **AC-002-05:** The proposal distinguishes semantic concepts from API resources and storage tables.
- [ ] **AC-002-06:** No binding contract is silently changed; required compatibility decisions are documented.
- [ ] **AC-002-07:** Existing v1.0 payloads have a documented compatibility/migration disposition.

## 6. Out of scope

Implementing a production execution runtime; choosing a database or graph platform; immediately renaming/removing existing v1.0 fields; claiming that candidate entities must each become standalone endpoints.

## 7. Dependencies and sequencing

CR-CLAM-001; reconcile against the current repository baseline before approval.

This CR is a proposed specification and change boundary. Dependencies must be verified against the repository's accepted CR/ADR state before implementation. A dependency listed here is not evidence that the upstream CR has been approved or implemented.

## 8. Verification approach

Architecture and data-model review; contract inventory; consistency review of examples and diagrams; compatibility analysis against existing payloads and tests.

## 9. Data-model impact

This CR is expected to enrich or consume the CLAM information model as described in `docs/data-model/CLAM-DATA-MODEL-ENRICHMENT-PROPOSAL.md`. Candidate concepts are not automatically binding entities. Before implementation, reconcile them with existing Pydantic models, OpenAPI schemas, persistence, examples, and API operations. Avoid duplicating a concept already represented adequately.

## 10. Compatibility and migration

Preserve the current binding model and API behaviour until the required compatibility decision is accepted. Any breaking change must specify a versioning strategy, migration/adapter path, deprecation period where appropriate, and regression evidence.

## 11. Follow-on work

CR-CLAM-003, 004, 005, 006, 007, 008, and 009.

## 12. Governance notes

- Investigation precedes implementation where semantics or architecture remain uncertain.
- Record material architectural decisions in ADRs under repository governance.
- Implement only the scope approved for this CR.
- Update traceability and conformance tests with each delivered requirement.
- Do not claim a capability is implemented until evidence supports the claim.
