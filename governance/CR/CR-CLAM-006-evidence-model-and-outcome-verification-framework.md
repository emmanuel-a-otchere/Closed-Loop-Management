# CR-CLAM-006: Evidence Model and Outcome Verification Framework

| Field | Value |
|---|---|
| CR ID | CR-CLAM-006 |
| Status | Proposed |
| Priority | P1 |
| Change class | Cross-cutting data model and verification |
| Repository | `emmanuel-a-otchere/Closed-Loop-Management` |
| Dependencies | CR-CLAM-002, CR-CLAM-003, and CR-CLAM-005. |

## 1. Problem statement

Simulator traces and KPI reports are useful artefacts, but without a common evidence contract, provenance, version binding, and explicit verification dispositions, results are difficult to compare, audit, or use in governed lifecycle decisions.

## 2. Objective

Define a common evidence and verification model that connects claims and acceptance criteria to observations, measurements, decisions, actions, and outcomes, while distinguishing success, failure, and insufficient evidence.

## 3. Scope

- Define EvidenceRecord, VerificationResult, Outcome, Measurement/MetricObservation, provenance, subject, source, timestamps, integrity metadata, and links to requirements and deployment/model versions.
- Define verification dispositions: satisfied, not satisfied, and indeterminate (final terminology subject to review).
- Specify evidence quality, freshness, completeness, source trust, and integrity metadata where applicable.
- Define evidence aggregation and acceptance-criteria evaluation without presuming one universal algorithm.
- Update simulator and KPI report contracts to reference the common model.
- Define retention, redaction, and sensitive-data minimisation requirements for evidence records.

## 4. Required deliverables

- Evidence and verification model.
- Proposed JSON Schema and example records.
- Outcome-verification rules and report format.
- Provenance and integrity requirements.
- Migration/adaptation plan for current JSONL traces and KPI reports.

## 5. Acceptance criteria

- [ ] **AC-006-01:** Each verification result identifies the evaluated criterion, subject, relevant model/configuration version, time/window, and disposition.
- [ ] **AC-006-02:** Evidence records identify their source and provenance to the extent available.
- [ ] **AC-006-03:** Missing or low-quality evidence can yield indeterminate rather than false success.
- [ ] **AC-006-04:** Evidence records distinguish simulated, test, and operational origins.
- [ ] **AC-006-05:** Evidence is linkable to requirements, goals, outcomes, and claims.
- [ ] **AC-006-06:** Existing trace/KPI artefacts have a documented migration or adapter strategy.

## 6. Out of scope

Claiming cryptographic non-repudiation without an implemented trust model; defining one universal causal-attribution method; collecting unnecessary personal or sensitive data.

## 7. Dependencies and sequencing

CR-CLAM-002, CR-CLAM-003, and CR-CLAM-005.

This CR is a proposed specification and change boundary. Dependencies must be verified against the repository's accepted CR/ADR state before implementation. A dependency listed here is not evidence that the upstream CR has been approved or implemented.

## 8. Verification approach

Schema validation, provenance-link tests, incomplete-evidence tests, version-mismatch tests, and trace/KPI adapter tests.

## 9. Data-model impact

This CR is expected to enrich or consume the CLAM information model as described in `docs/data-model/CLAM-DATA-MODEL-ENRICHMENT-PROPOSAL.md`. Candidate concepts are not automatically binding entities. Before implementation, reconcile them with existing Pydantic models, OpenAPI schemas, persistence, examples, and API operations. Avoid duplicating a concept already represented adequately.

## 10. Compatibility and migration

Preserve the current binding model and API behaviour until the required compatibility decision is accepted. Any breaking change must specify a versioning strategy, migration/adapter path, deprecation period where appropriate, and regression evidence.

## 11. Follow-on work

CR-CLAM-007, 009, and 010.

## 12. Governance notes

- Investigation precedes implementation where semantics or architecture remain uncertain.
- Record material architectural decisions in ADRs under repository governance.
- Implement only the scope approved for this CR.
- Update traceability and conformance tests with each delivered requirement.
- Do not claim a capability is implemented until evidence supports the claim.
