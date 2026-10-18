---
cr_id: CR-CLAM-003
title: Intent, Constraints, and Capability Traceability
status: Proposed
priority: P0
type: Engineering and semantic traceability
repository: emmanuel-a-otchere/Closed-Loop-Management
dependencies: [CR-CLAM-002]
source_review: CR-CLAM-000 (Section 7, CR-CLAM-003)

---

# CR-CLAM-003: Intent, Constraints, and Capability Traceability

## Change summary

Introduce a traceability model connecting `Intent -> Requirements -> Constraints -> Design -> Actions -> Outcomes -> Evidence`, and define the relationship between a closed loop and the capability it realises.

## Problem statement

The model represents goals and decision mechanisms, but the repository does not yet establish a complete, machine-verifiable chain from requirements and constraints to demonstrated capability. A loop that succeeds at the action level cannot be proven to satisfy the goal it was meant to satisfy.

## Motivation and rationale

Without traceability, success is judged by what the system did rather than what it was meant to achieve. The conceptual model already uses the verb chain **satisfies**, **realises**, **exhibits**, **changes**, **verifies**, and **providesEvidenceFor**; this CR makes those verbs machine-checkable.

## Proposed change

Introduce a normative traceability model with stable identifiers and a graph representation:

- **Intent** -- the declared purpose of a loop.
- **Requirement** -- what must hold for the intent to be met.
- **Constraint** -- what must NOT happen (negation of a requirement).
- **Capability** -- the named ability the loop is responsible for.
- **Design** -- the structural realisation of a capability.
- **Action** -- an executable step in a workflow.
- **Observed state** -- what the environment now shows.
- **Outcome** -- the comparison of observed state against expected state.
- **Verification** -- the documented judgment of an outcome.
- **Evidence** -- the artefact that supports a verification.

Edges in the graph are typed: `satisfies`, `realises`, `exhibits`, `changes`, `verifies`, `providesEvidenceFor`. Add a CLI/validator that flags broken chains and emits a traceability report.

## Repository changes (deliverables)

- `docs/conceptual/traceability-model.md`
- `schemas/data-model/traceability-1.0.md`
- `machines/scripts/validate_traceability.py (CI-invoked)`
- `datasets/examples/traceability-graph-example.json`
- `Validation report format spec (machine-readable JSON schema)`

## Acceptance criteria

1. Every in-scope capability has at least one declared realisation requirement.
2. Applicable constraints are traceable to the relevant design and verification criteria.
3. Outcome verification is linkable to the goals it evaluates.
4. Evidence is linkable to the claims it supports.
5. Broken traceability links are reported automatically with a stable error identifier.

## Out of scope

- External requirements-management toolchains.
- Introducing new entities beyond what the traceability schema defines.
- Production deployment of AI-assisted traceability mining.

## Dependencies

- Depends on: CR-CLAM-002

## Follow-on relationship

- CR-CLAM-004 (conformance and design validation) consumes this trace model.
- CR-CLAM-005 (scenario-based simulation) attaches evidence to simulations via this trace.
- CR-CLAM-006 (evidence and outcome verification) reuses the trace as its substrate.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Traceability graph becomes a duplicate authority alongside the data model. | The traceability model is a derived view over the binding model; the binding model remains authoritative. |
| Operators hand-craft trace links instead of deriving them from code. | Where possible, derive links from declared artefacts (config, decorators, schema annotations); allow manual links only for intent/goal which are inherently human-authored. |

## Source

This CR is a harvest of the canonical proposal in
[`governance/reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md`](../../reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md),
Section 7, CR-CLAM-003. The full prose, including its tables and rationale, is
preserved verbatim in that file.
