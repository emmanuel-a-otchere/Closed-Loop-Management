# CR-CLAM-004: CLAM Semantic Conformance and Design Validation Toolkit

| Field | Value |
|---|---|
| CR ID | CR-CLAM-004 |
| Status | Proposed |
| Priority | P1 |
| Change class | Validation tooling |
| Repository | `emmanuel-a-otchere/Closed-Loop-Management` |
| Dependencies | CR-CLAM-001, CR-CLAM-002, and CR-CLAM-003. |

## 1. Problem statement

OpenAPI structural validation can establish contract-level validity but cannot, by itself, establish semantic completeness, lifecycle legality, traceability integrity, policy admissibility, or inter-loop compatibility.

## 2. Objective

Define and implement a layered conformance-validation approach that evaluates CLAM artefacts against the normative requirements and emits deterministic, machine-readable findings.

## 3. Scope

- Separate OpenAPI/schema validation from semantic, reference-integrity, lifecycle, traceability, policy, compatibility, and release-readiness validation.
- Define validation rule identifiers, severity, diagnostic format, affected artefact, and remediation guidance.
- Validate relationships, required fields, enum values, references, version compatibility, workflow paths, and state-transition legality.
- Add requirement/constraint completeness checks after CR-CLAM-003 is defined.
- Add CLI and CI integration consistent with current repository conventions.
- Keep validation rules independently invocable and testable.

## 4. Required deliverables

- Validation architecture and rule catalogue.
- Machine-readable report schema and example reports.
- CLI behaviour and CI integration.
- Positive and negative fixtures for each rule family.
- Compatibility report for existing v1.0 models and API payloads.

## 5. Acceptance criteria

- [ ] **AC-004-01:** Each implemented rule has a stable identifier and at least one positive and one negative test where applicable.
- [ ] **AC-004-02:** Reports distinguish errors, warnings, and informational findings.
- [ ] **AC-004-03:** Every finding identifies the rule, affected artefact/location, explanation, and remediation guidance.
- [ ] **AC-004-04:** Equivalent inputs and tool versions produce deterministic reports.
- [ ] **AC-004-05:** Schema validation does not claim to prove behavioural correctness.
- [ ] **AC-004-06:** CI fails on the agreed blocking severities and reports non-blocking findings explicitly.

## 6. Out of scope

Replacing OpenAPI 3.1; forcing all validation into JSON Schema; claiming formal proof or safety certification from ordinary conformance checks.

## 7. Dependencies and sequencing

CR-CLAM-001, CR-CLAM-002, and CR-CLAM-003.

This CR is a proposed specification and change boundary. Dependencies must be verified against the repository's accepted CR/ADR state before implementation. A dependency listed here is not evidence that the upstream CR has been approved or implemented.

## 8. Verification approach

Unit tests, fixture suite, CI execution, regression tests against current OpenAPI and examples.

## 9. Data-model impact

This CR is expected to enrich or consume the CLAM information model as described in `docs/data-model/CLAM-DATA-MODEL-ENRICHMENT-PROPOSAL.md`. Candidate concepts are not automatically binding entities. Before implementation, reconcile them with existing Pydantic models, OpenAPI schemas, persistence, examples, and API operations. Avoid duplicating a concept already represented adequately.

## 10. Compatibility and migration

Preserve the current binding model and API behaviour until the required compatibility decision is accepted. Any breaking change must specify a versioning strategy, migration/adapter path, deprecation period where appropriate, and regression evidence.

## 11. Follow-on work

CR-CLAM-005, 006, 007, and 008.

## 12. Governance notes

- Investigation precedes implementation where semantics or architecture remain uncertain.
- Record material architectural decisions in ADRs under repository governance.
- Implement only the scope approved for this CR.
- Update traceability and conformance tests with each delivered requirement.
- Do not claim a capability is implemented until evidence supports the claim.
