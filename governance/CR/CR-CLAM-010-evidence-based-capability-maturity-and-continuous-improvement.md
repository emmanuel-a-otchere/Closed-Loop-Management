# CR-CLAM-010: Evidence-Based Capability Maturity and Continuous Improvement

| Field | Value |
|---|---|
| CR ID | CR-CLAM-010 |
| Status | Proposed |
| Priority | P2 |
| Change class | Assessment, governance, and improvement |
| Repository | `emmanuel-a-otchere/Closed-Loop-Management` |
| Dependencies | CR-CLAM-001, CR-CLAM-006, and CR-CLAM-007; consume CR-CLAM-002/003 capability and traceability definitions. |

## 1. Problem statement

A questionnaire and aggregate score provide a starting point, but without capability-linked definitions, evidence requirements, prerequisites, and remediation mapping, maturity results may be difficult to compare or may conceal critical weaknesses.

## 2. Objective

Align the maturity-assessment toolkit with the normative CLAM capability model and require scores to be justified by declared evidence and explicit scoring rules.

## 3. Scope

- Define maturity dimensions and levels from the accepted capability taxonomy.
- Specify level criteria, prerequisites, evidence expectations, scoring rules, and confidence/unknown handling.
- Distinguish capability maturity from operational performance and current health.
- Prevent critical control/assurance gaps from being masked by a high aggregate score.
- Map assessment findings to capabilities, requirements, risks, and proposed improvement work.
- Define assessment versioning, repeatability, comparison, and report schema.

## 4. Required deliverables

- Capability-based maturity model.
- Scoring rubric and evidence guidance.
- Machine-readable assessment report format.
- Updated questionnaire and scoring template proposal.
- Gap-to-remediation mapping and repeat-assessment rules.

## 5. Acceptance criteria

- [ ] **AC-010-01:** Every score is traceable to a defined criterion and evidence or explicitly marked self-reported/unverified.
- [ ] **AC-010-02:** Unknown evidence is not silently scored as achieved.
- [ ] **AC-010-03:** Critical prerequisites and non-compensable weaknesses are explicit.
- [ ] **AC-010-04:** Maturity is not conflated with live operational health or KPI performance.
- [ ] **AC-010-05:** Assessment results map to specific capability gaps and governed improvement actions.
- [ ] **AC-010-06:** Assessment versions and scoring changes are traceable for longitudinal comparison.

## 6. Out of scope

Claiming independent certification or industry benchmarking without validation; inventing universal maturity scores before pilot assessment.

## 7. Dependencies and sequencing

CR-CLAM-001, CR-CLAM-006, and CR-CLAM-007; consume CR-CLAM-002/003 capability and traceability definitions.

This CR is a proposed specification and change boundary. Dependencies must be verified against the repository's accepted CR/ADR state before implementation. A dependency listed here is not evidence that the upstream CR has been approved or implemented.

## 8. Verification approach

Scoring test cases, edge cases for missing evidence, critical-gap tests, repeatability tests, and review against representative use cases.

## 9. Data-model impact

This CR is expected to enrich or consume the CLAM information model as described in `docs/data-model/CLAM-DATA-MODEL-ENRICHMENT-PROPOSAL.md`. Candidate concepts are not automatically binding entities. Before implementation, reconcile them with existing Pydantic models, OpenAPI schemas, persistence, examples, and API operations. Avoid duplicating a concept already represented adequately.

## 10. Compatibility and migration

Preserve the current binding model and API behaviour until the required compatibility decision is accepted. Any breaking change must specify a versioning strategy, migration/adapter path, deprecation period where appropriate, and regression evidence.

## 11. Follow-on work

Future improvement CRs identified by assessment findings.

## 12. Governance notes

- Investigation precedes implementation where semantics or architecture remain uncertain.
- Record material architectural decisions in ADRs under repository governance.
- Implement only the scope approved for this CR.
- Update traceability and conformance tests with each delivered requirement.
- Do not claim a capability is implemented until evidence supports the claim.
