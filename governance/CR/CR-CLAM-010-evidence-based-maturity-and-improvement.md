---
cr_id: CR-CLAM-010
title: Evidence-Based Maturity and Improvement
status: Proposed
priority: P2
type: Assessment and improvement
repository: emmanuel-a-otchere/Closed-Loop-Management
dependencies: [CR-CLAM-001, CR-CLAM-006, CR-CLAM-007]
source_review: CR-CLAM-000 (Section 7, CR-CLAM-010)

---

# CR-CLAM-010: Evidence-Based Maturity and Improvement

## Change summary

Establish a capability-based maturity model with explicit scoring criteria, evidence requirements, prerequisites, and improvement recommendations mapped to governed CRs.

## Problem statement

The maturity-assessment toolkit offers an initial mechanism for assessment, but a maturity score becomes more useful when linked to specific capabilities, objective evidence, and remediation priorities.

## Motivation and rationale

Aggregate scores can mask critical weaknesses. A high average cannot compensate for missing control safeguards. The maturity model must make critical control gaps non-overridable.

## Proposed change

Define five maturity dimensions (engineering, operational, control, assurance, coordination) with five levels each. Each (dimension, level) pair has:

- A level definition in plain language.
- Required evidence artefacts and their schemas.
- Prerequisites (which lower-level capabilities must be present).
- Scoring policy (cannot promote past a failed-critical control even if other dimensions are high).
- A remediation mapping pointing at the most relevant CR-CLAM-NNN that closes the gap.

The maturity calculator reads evidence records (CR-CLAM-006) and emits an assessment report (JSON) plus a human-readable HTML/PDF.

## Repository changes (deliverables)

- `docs/assurance/maturity-model.md`
- `schemas/maturity/assessment-report-1.0.md`
- `machines/toolkits/maturity-calculator/`
- `docs/conformance/capability-traceability.md (covered by CR-CLAM-001)`
- `Sample assessment in `datasets/maturity/sample-assessment-v1.json``

## Acceptance criteria

1. Every maturity score has a documented basis (linked evidence + scoring rule).
2. Critical control weaknesses cannot be obscured by aggregate scores.
3. Assessment results map to specific capability gaps (with stable identifiers).
4. Improvement recommendations map to governed CRs or other approved changes.
5. Assessments can be repeated and compared consistently (deterministic outputs).

## Out of scope

- Vendor comparison studies.
- Certification programmes (organisations can wrap this model later).
- Auto-remediation (remediations are tracked as separate work).

## Dependencies

- Depends on: CR-CLAM-001, CR-CLAM-006, CR-CLAM-007

## Follow-on relationship

- Drives prioritisation of subsequent capability gaps surfaced by CR-CLAM-001.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Maturity model becomes vanity metric. | Tie every published score to a remediation plan tracked on the kanban board; reject assessments that lack a remediation plan from CRs. |

## Source

This CR is a harvest of the canonical proposal in
[`governance/reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md`](../../reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md),
Section 7, CR-CLAM-010. The full prose, including its tables and rationale, is
preserved verbatim in that file.
