---
cr_id: CR-CLAM-008
title: Inter-Loop Coordination and Conflict Management
status: Proposed
priority: P1
type: Architecture and operational management
repository: emmanuel-a-otchere/Closed-Loop-Management
dependencies: [CR-CLAM-002, CR-CLAM-005, CR-CLAM-007]
source_review: CR-CLAM-000 (Section 7, CR-CLAM-008)

---

# CR-CLAM-008: Inter-Loop Coordination and Conflict Management

## Change summary

Specify inter-loop contracts for input/output compatibility, dependency ordering, shared-resource allocation, conflicting goals, conflicting actions, failure propagation, escalation, and system-wide outcome verification.

## Problem statement

The existing model can represent relationships between loops, but a relationship alone does not establish that connected loops are compatible or that their combined behaviour is safe and effective.

## Motivation and rationale

Two loops that are individually safe can be unsafe together (resource starvation, conflicting actions, cascading failure). The inter-loop contract makes those interactions explicit and detect failure propagation at the system level rather than the loop level.

## Proposed change

Define contracts for five interaction classes:

- **Compatibility**: input/output type matching, schema version compatibility, coordinate-system compatibility.
- **Dependency ordering**: precedence rules, ordering locks, time-ordered events.
- **Shared resources**: allocation strategies, contention detection, recovery rules.
- **Conflicting goals**: detection rules, resolution policies (priority, override, escalate).
- **Conflicting actions**: lockout rules, ordering, conflict resolution traces.

In addition, define failure-propagation semantics (does a loop's `error` state abort downstream?) and system-level outcome verification criteria.

## Repository changes (deliverables)

- `docs/architecture/inter-loop-coordination.md`
- `schemas/data-model/inter-loop-contract-1.0.md`
- `machines/toolkits/inter-loop-validator/ (conflict and compatibility checks)`
- `datasets/examples/inter-loop-coordination-2-loops.json and -3-loops.json`
- `Coordination scenarios in `datasets/scenarios/inter-loop-*``

## Acceptance criteria

1. Incompatible links can be identified before publication (validator failure in CI).
2. Resource and goal conflicts have defined resolution policies.
3. Failures can be traced across dependent loops via the trace model from CR-CLAM-003.
4. Coordination decisions are auditable (evidence records per decision).
5. System-wide outcomes can be evaluated independently of individual loop status.

## Out of scope

- Building a distributed runtime for multi-loop execution.
- Global optimisation across all loops (each loop's envelope remains its own boundary).

## Dependencies

- Depends on: CR-CLAM-002, CR-CLAM-005, CR-CLAM-007

## Follow-on relationship

- CR-CLAM-009 (observability) reuses the failure-propagation semantics to scope alerts.
- CR-CLAM-010 (maturity) scores inter-loop coordination maturity separately.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Coordination rules become incompatible with each other across versions. | Inter-loop contracts declare a contract version; the validator rejects combinations whose version matrix is not closed. |

## Source

This CR is a harvest of the canonical proposal in
[`governance/reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md`](../../reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md),
Section 7, CR-CLAM-008. The full prose, including its tables and rationale, is
preserved verbatim in that file.
