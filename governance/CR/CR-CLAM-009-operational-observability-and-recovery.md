---
cr_id: CR-CLAM-009
title: Operational Observability and Recovery
status: Proposed
priority: P2
type: Operational tooling
repository: emmanuel-a-otchere/Closed-Loop-Management
dependencies: [CR-CLAM-006, CR-CLAM-007]
source_review: CR-CLAM-000 (Section 7, CR-CLAM-009)

---

# CR-CLAM-009: Operational Observability and Recovery

## Change summary

Define a common event, telemetry, and health model for operational closed loops, including health/degraded definitions, alert requirements, failure classification, recovery and restart rules, and audit history.

## Problem statement

Current documentation identifies monitoring and reporting as management capabilities, but does not establish a complete operational telemetry and recovery contract.

## Motivation and rationale

An operator must be able to reconstruct the relevant sequence of events for an incident. Stale, missing, or ambiguous observations must be distinguishable from healthy operation; otherwise the system cannot tell normal from abnormal.

## Proposed change

Define a closed-loop event/telemetry/health model:

- **Event taxonomy**: lifecycle, operational, exceptional, recovery.
- **Telemetry**: structured fields, unit conventions, time stamps, freshness policy.
- **Health model**: per-dimension health (lifecycle, execution, goal, assurance) recomputed from CR-CLAM-002 state dimensions.
- **Degraded-condition semantics**: explicit states (e.g. stale observations) distinct from failure.
- **Alert policy**: what fires, who receives, escalation order.
- **Failure classification**: by causal class (input, action, dependency, control) not just by HTTP status.
- **Recovery rules**: restart, revalidate, escalate, suspend -- tied to CR-CLAM-007.
- **Operational history**: audit retention, minimum retention period, redaction rules.


## Repository changes (deliverables)

- `docs/assurance/operational-assurance.md`
- `schemas/telemetry/event-1.0.md`
- `machines/toolkits/clam-health-aggregator/`
- `machines/scripts/retention_pruner.py`
- `Operator runbook in `docs/runbooks/incident-recovery.md``

## Acceptance criteria

1. Relevant lifecycle and operational events are recorded with stable identifiers.
2. Telemetry can be associated with the applicable loop and deployment version.
3. Stale or missing observations can be distinguished from healthy operation.
4. Recovery actions follow declared policies and emit evidence.
5. Operators can reconstruct the relevant sequence of events for an incident from the recorded history.

## Out of scope

- Mandating a particular observability platform.
- Replacing existing monitoring stacks.
- Cross-domain SIEM integration.

## Dependencies

- Depends on: CR-CLAM-006, CR-CLAM-007

## Follow-on relationship

- CR-CLAM-010 (maturity) uses recovery and observability metrics in its scoring.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Event taxonomy drifts across releases. | Event identifiers carry a version; old identifiers remain routable; deprecation has a documented grace window. |

## Source

This CR is a harvest of the canonical proposal in
[`governance/reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md`](../../reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md),
Section 7, CR-CLAM-009. The full prose, including its tables and rationale, is
preserved verbatim in that file.
