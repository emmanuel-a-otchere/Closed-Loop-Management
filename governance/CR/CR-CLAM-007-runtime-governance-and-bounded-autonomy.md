---
cr_id: CR-CLAM-007
title: Runtime Governance and Bounded Autonomy
status: Proposed
priority: P1
type: Operational safety and governance
repository: emmanuel-a-otchere/Closed-Loop-Management
dependencies: [CR-CLAM-002, CR-CLAM-003, CR-CLAM-006]
source_review: CR-CLAM-000 (Section 7, CR-CLAM-007)

---

# CR-CLAM-007: Runtime Governance and Bounded Autonomy

## Change summary

Define the management contracts under which a running loop may act, recover, suspend, or escalate -- covering permitted/prohibited actions, operating envelopes, preconditions, escalation, human-approval requirements, and emergency suspension.

## Problem statement

A lifecycle API does not by itself establish the conditions under which a running loop may act, recover, or continue operating. Without explicit governance, a loop in `active` state has no documented upper bound on its actions.

## Motivation and rationale

Autonomy is not the same as AI. A loop can be autonomous without using AI; a loop can use an AI model without having authority to act autonomously. The model must distinguish these characteristics independently and apply different controls to each.

## Proposed change

Define a bounded-autonomy specification with the following controls, each machine-readable:

- Permitted actions and prohibited actions.
- Operating envelope (numeric ranges, time windows, scope tags).
- Resource and budget limits.
- Maximum action rates and concurrency caps.
- Preconditions for execution.
- Escalation conditions and routes.
- Human approval requirements (which actions require a human signer).
- Emergency suspension triggers and procedures.
- Recovery and reactivation conditions, including mandatory revalidation.

Sequence qualification from the source review: this CR establishes governance semantics before any production-oriented autonomous execution adapter is authorised. The programme is NOT a green light for unrestricted execution.

## Repository changes (deliverables)

- `docs/architecture/control-boundaries.md`
- `schemas/policies/bounded-autonomy-1.0.md`
- `machines/scripts/enforce_envelope.py`
- `docs/governance/reauthorisation-procedure.md`
- `Example envelopes for two representative loop profiles`

## Acceptance criteria

1. Every governed action is subject to explicitly defined permissions and constraints.
2. Violations have specified responses (block, alert, escalate, suspend) keyed by type.
3. Recovery cannot bypass required validation or authorisation.
4. AI usage and autonomy level are represented as distinct characteristics with distinct controls.
5. Human intervention requirements are machine-readable where applicable.

## Out of scope

- Authorising any specific autonomous execution adapter.
- Mandating a particular policy engine.
- Building real-time human-in-the-loop UI flows (separate ADR required).

## Dependencies

- Depends on: CR-CLAM-002, CR-CLAM-003, CR-CLAM-006

## Follow-on relationship

- CR-CLAM-008 (inter-loop coordination) reuses the envelope model for system-wide reasoning.
- CR-CLAM-009 (observability) emits alerts when envelope breaches occur.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Envelope model becomes too rigid for adaptive loops. | Envelopes are time-windowed; a loop with adaptive envelopes must declare its adaptive rule as part of its specification, subject to the same review as the loop itself. |
| Operators bypass controls to fix incidents. | Emergency override paths are themselves part of the model and emit evidence; override without evidence is a violation. |

## Source

This CR is a harvest of the canonical proposal in
[`governance/reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md`](../../reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md),
Section 7, CR-CLAM-007. The full prose, including its tables and rationale, is
preserved verbatim in that file.
