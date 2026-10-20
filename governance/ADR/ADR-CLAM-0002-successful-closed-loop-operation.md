---
adr_id: ADR-CLAM-0002
title: Defining successful closed-loop operation -- verified outcomes against declared intent and constraints
status: Proposed (pending Section 10 Decision B)
date: 2026-10-18
source_review: CR-CLAM-000 (Section 10, Decision B)
decides: What counts as a successful closed-loop operation
---

# ADR-CLAM-0002: Definition of successful closed-loop operation

## Status

Proposed. Terminology is formalised through CR-CLAM-002 (semantic
model and state separation) and CR-CLAM-006 (evidence and outcome
verification framework). This ADR states the decision in
human-readable terms and is the canonical pointer when those CRs
land their binding definitions.

## Context

The current repository can answer "did the lifecycle API respond
successfully?", "did the workflow reach completion?", "did the
action return success?", and "did the KPI improve in isolation?"
But none of these answers is sufficient evidence that the loop
achieved its declared purpose under its declared constraints.

The capability review calls this out as one of the most
consequential gaps. A loop should not be marked successful
because it was busy.

## Decision

Define the success of a closed loop in terms of **verified
outcomes against declared intent and declared constraints**.

A loop is **not** successful merely because:

- Its lifecycle state is `active`.
- Its API request succeeded.
- Its workflow completed.
- Its action returned successfully.
- A KPI improved in isolation.

A loop's outcome is a three-valued judgment:

1. **Satisfied** -- the required outcome has been verified against
   acceptance criteria under the applicable constraints, with
   sufficient supporting evidence.
2. **Not satisfied** -- available evidence demonstrates that the
   acceptance criteria were not met.
3. **Indeterminate** -- available evidence is insufficient to
   establish either conclusion; further evidence collection or
   verification work is required before a verdict is reached.

The exact schema for this judgment lives in CR-CLAM-006. The state
dimension in which the verdict is recorded lives in CR-CLAM-002
(the `goal_disposition` dimension).

## Consequences

Positive:

- Decisions to operate, suspend, retire, or escalate a loop are
  grounded in evidence rather than in liveness signals.
- Loops that are technically running but no longer converging are
  distinguishable from loops that are running and converging.
- Auditors can reconstruct why a loop was judged successful
  (or not) by following the evidence chain.

Negative / costs:

- Operators and reviewers must learn the three-valued semantics;
  binary "success/failure" mindsets must be unlearned.
- The evidence-collection and verification work is non-trivial;
  loops that previously relied on heuristics (KPI improvements
  alone) must now produce acceptance criteria and evidence.
- Reporting dashboards need a column for "indeterminate" rather
  than collapsing it into either success or failure.

Operational consequences:

- The status dashboard for any managed loop carries four signals
  per the four state dimensions (see CR-CLAM-002):
  management lifecycle, execution condition, goal disposition,
  assurance disposition.
- "Indeterminate" is the default disposition when a loop is first
  activated; it transitions to `satisfied` or `not satisfied`
  only after a verification result lands (see CR-CLAM-006).

## Alternatives considered

- **Binary success/failure** was rejected because it cannot
  represent the situation where a loop has not yet produced
  enough evidence to judge.
- **KPI-as-success** was rejected because KPI improvements can
  occur for reasons unrelated to the loop (external changes,
  measurement noise, attribution errors).
- **Lifecycle-state-as-success** (i.e. `active` means successful)
  was rejected because it conflates governance state with
  outcome state.

## Follow-on

- Formalises through CR-CLAM-002 (state dimensions) and
  CR-CLAM-006 (evidence and outcome verification).
- Tied to the evaluation logic in CR-CLAM-005 (scenario-based
  simulation) for design-time verification.
- Drives the maturity scoring in CR-CLAM-010.

## References

- CR-CLAM-000 (`governance/reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md`), Section 10 Decision B.
- CR-CLAM-001 (`governance/CR/CR-CLAM-001-normative-capability-model.md`).
- CR-CLAM-002 (state dimensions: `management_lifecycle`, `execution_condition`, `goal_disposition`, `assurance_disposition`).
- CR-CLAM-006 (evidence schema and outcome verification contract).
