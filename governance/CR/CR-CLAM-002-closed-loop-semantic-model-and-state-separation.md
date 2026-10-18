---
cr_id: CR-CLAM-002
title: Closed-Loop Semantic Model and State Separation
status: Proposed
priority: P0
type: Information-model enhancement
repository: emmanuel-a-otchere/Closed-Loop-Management
dependencies: [CR-CLAM-001]
source_review: CR-CLAM-000 (Section 7, CR-CLAM-002)

---

# CR-CLAM-002: Closed-Loop Semantic Model and State Separation

## Change summary

Define the authoritative conceptual model covering intent, goals, constraints, capabilities, observations, state transitions, decisions, actions, outcomes, evidence, and inter-loop relationships, and separate the four state dimensions before modifying the binding schema.

## Problem statement

The current model provides a closed-loop lifecycle state and core relationships, but does not fully specify the semantic distinction between management lifecycle, execution condition, goal disposition, and assurance disposition. Conflating these dimensions hides bugs and makes operational assurance impossible to reason about.

## Motivation and rationale

Without an explicit semantic model, each tool interprets the same concept differently. A loop can report `active` while its goal is unattainable, while observations are stale, and while assurance is rejected. The system cannot be governed while these states are merged into a single enum.

## Proposed change

Define the authoritative conceptual model for:

- Intent and requirements.
- Goals and constraints.
- Capabilities and their realisation.
- Observations and state transitions.
- Decisions and actions.
- Outcomes and verification.
- Evidence and assurance.
- Resource and inter-loop relationships.

Specify four distinct state dimensions and their interaction rules before changing the binding schema. Introduce per-dimension enums (`management_lifecycle`, `execution_condition`, `goal_disposition`, `assurance_disposition`) rather than one combined state machine.

## Repository changes (deliverables)

- `docs/conceptual/semantic-model.md`
- `docs/conceptual/state-dimensions.md`
- `schemas/data-model/state-dimensions-1.0.md`
- `schemas/openapi/state-dimensions-1.0.json (regenerated via export_openapi.py)`
- `Data-model migration strategy and backward-compatibility assessment`

## Acceptance criteria

1. Lifecycle state is distinct from runtime condition and outcome status in both the conceptual model and the binding schema.
2. Every proposed entity and relationship has an unambiguous definition.
3. Invalid references and inconsistent relationships are detectable by a machine-readable validator.
4. The binding model can evolve without silently changing established meanings (additive migrations only until a major-version decision).
5. Existing API consumers have a documented migration path with concrete examples.

## Out of scope

- Implementation of a new execution runtime.
- Introduction of a specific AI or agent framework.
- Rewriting the existing REST API.
- Replacing the existing lifecycle state machine without explicit ADR approval.

## Dependencies

- Depends on: CR-CLAM-001

## Follow-on relationship

- CR-CLAM-003 (intent/constraints/traceability) builds on this CR.
- CR-CLAM-004 (conformance and design validation) consumes the explicit semantic model.
- CR-CLAM-007 (bounded autonomy) uses the four-dimension state semantics.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Schema change breaks existing API consumers. | Land an additive migration under the current API version, then evaluate a v2 once the new state semantics are validated. |
| Semantic concepts conflict with the canonical semantic foundation. | Record unresolved semantic decisions in `governance/decisions/` and resolve via ADR before binding. |

## Source

This CR is a harvest of the canonical proposal in
[`governance/reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md`](../../reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md),
Section 7, CR-CLAM-002. The full prose, including its tables and rationale, is
preserved verbatim in that file.
