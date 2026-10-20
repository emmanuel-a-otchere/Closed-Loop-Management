# CR-CLAM-007: Runtime Governance and Bounded Autonomy

| Field | Value |
|---|---|
| CR ID | CR-CLAM-007 |
| Status | Proposed |
| Priority | P1 |
| Change class | Operational governance and control boundaries |
| Repository | `emmanuel-a-otchere/Closed-Loop-Management` |
| Dependencies | CR-CLAM-002, CR-CLAM-003, and CR-CLAM-006; CR-CLAM-004 supplies conformance checks. |

## 1. Problem statement

Lifecycle control does not, by itself, establish which actions a loop is permitted to take, under what conditions, or how it must respond to constraint violations, uncertainty, or loss of assurance.

## 2. Objective

Define technology-neutral management contracts for bounded autonomy, policy applicability, action authorisation, operating envelopes, human intervention, suspension, recovery, and revalidation.

## 3. Scope

- Model permitted/prohibited action classes, operating envelope, resource/budget limits, rate limits, preconditions, postconditions, escalation triggers, and required approvals where applicable.
- Distinguish AI usage, automation level, decision authority, and degree of autonomy as separate attributes.
- Define policy identity, version, scope, priority/precedence, effective period, and enforcement responsibility.
- Define responses to violated constraints, stale observations, unavailable dependencies, and degraded assurance.
- Specify conditions for suspend, safe-stop, recovery, revalidation, reapproval, and rollback.
- State explicitly that policy enforcement may be performed by an external execution/control component; CLAM must define and verify the management contract.

## 4. Required deliverables

- Bounded-autonomy and runtime-governance specification.
- Proposed policy/constraint schema and examples.
- Decision table for violation and recovery handling.
- Human intervention and approval requirements.
- Test scenarios and assurance evidence requirements.

## 5. Acceptance criteria

- [ ] **AC-007-01:** Applicable permissions and constraints can be identified for a governed loop/action.
- [ ] **AC-007-02:** Each defined violation class has an explicit response or documented escalation.
- [ ] **AC-007-03:** Recovery cannot bypass required validation and approval gates.
- [ ] **AC-007-04:** AI use is not treated as equivalent to autonomy or permission to act.
- [ ] **AC-007-05:** Enforcement responsibility is identified for each normative policy class.
- [ ] **AC-007-06:** Any unresolved high-consequence control requirement is flagged as a release blocker rather than silently defaulted.

## 6. Out of scope

Implementing an unrestricted action executor; defining domain-specific safety certification; claiming that a policy schema alone enforces runtime safety.

## 7. Dependencies and sequencing

CR-CLAM-002, CR-CLAM-003, and CR-CLAM-006; CR-CLAM-004 supplies conformance checks.

This CR is a proposed specification and change boundary. Dependencies must be verified against the repository's accepted CR/ADR state before implementation. A dependency listed here is not evidence that the upstream CR has been approved or implemented.

## 8. Verification approach

Policy validation, decision-table tests, fault scenarios, authorisation-boundary tests, and review of safe-stop/recovery cases.

## 9. Data-model impact

This CR is expected to enrich or consume the CLAM information model as described in `docs/data-model/CLAM-DATA-MODEL-ENRICHMENT-PROPOSAL.md`. Candidate concepts are not automatically binding entities. Before implementation, reconcile them with existing Pydantic models, OpenAPI schemas, persistence, examples, and API operations. Avoid duplicating a concept already represented adequately.

## 10. Compatibility and migration

Preserve the current binding model and API behaviour until the required compatibility decision is accepted. Any breaking change must specify a versioning strategy, migration/adapter path, deprecation period where appropriate, and regression evidence.

## 11. Follow-on work

CR-CLAM-008, 009, and 010.

## 12. Governance notes

- Investigation precedes implementation where semantics or architecture remain uncertain.
- Record material architectural decisions in ADRs under repository governance.
- Implement only the scope approved for this CR.
- Update traceability and conformance tests with each delivered requirement.
- Do not claim a capability is implemented until evidence supports the claim.
