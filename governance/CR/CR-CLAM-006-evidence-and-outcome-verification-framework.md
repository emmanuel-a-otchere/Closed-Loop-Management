---
cr_id: CR-CLAM-006
title: Evidence and Outcome Verification Framework
status: Proposed
priority: P1
type: Cross-cutting capability
repository: emmanuel-a-otchere/Closed-Loop-Management
dependencies: [CR-CLAM-003, CR-CLAM-005]
source_review: CR-CLAM-000 (Section 7, CR-CLAM-006)

---

# CR-CLAM-006: Evidence and Outcome Verification Framework

## Change summary

Define a common evidence model that links requirements, goals, constraints, decisions, actions, observed state, verification results, operational metrics, and capability realisation claims under a stable provenance chain.

## Problem statement

The repository has simulator traces and KPI reports, but these need a common evidence contract if they are to support verification, operational decisions, and auditability consistently. Without a contract, every tool invents its own.

## Motivation and rationale

Evidence has to support three states with crisp semantics: **satisfied** (criterion verified), **not satisfied** (evidence demonstrates failure), and **indeterminate** (insufficient evidence). Conflating these states produces false confidence, especially when evidence is missing for mundane reasons.

## Proposed change

Define an evidence schema with five elements:

1. Stable evidence identity.
2. Provenance chain (source, generator, hash, timestamp).
3. Subject (the claim or criterion the evidence supports).
4. Type (observation, trace, report, attestation, signature).
5. Verification result bound to the subject with one of {satisfied, not satisfied, indeterminate}.

Define an `OutcomeVerification` contract separate from the `Action` it represents. Define retention rules (how long evidence is kept, what redaction rules apply).

## Repository changes (deliverables)

- `schemas/evidence/evidence-1.0.md (schema spec)`
- `schemas/evidence/outcome-verification-1.0.md`
- `docs/conformance/evidence-requirements.md`
- `machines/scripts/validate_evidence.py`
- `datasets/conformance/evidence/fixture-evidence-set.json`

## Acceptance criteria

1. Evidence has a stable identity and provenance.
2. Evidence identifies the claim or criterion it supports.
3. Verification distinguishes success, failure, and insufficient evidence as distinct outcomes.
4. Results can be reproduced or independently inspected to the extent supported by the evidence.
5. Evidence remains associated with the relevant design and deployment versions.

## Out of scope

- Building a unified evidence store (the schema is the contract; storage is a separate decision).
- Cross-org evidence sharing protocols.

## Dependencies

- Depends on: CR-CLAM-003, CR-CLAM-005

## Follow-on relationship

- CR-CLAM-007 (bounded autonomy) consumes evidence for reauthorisation.
- CR-CLAM-009 (observability) emits operational evidence into this contract.
- CR-CLAM-010 (maturity) scores improvements by evidence density.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Evidence schema forks across toolkits. | The first implementation pin is normative; future versions follow ADR-controlled schema evolution. |

## Source

This CR is a harvest of the canonical proposal in
[`governance/reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md`](../../reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md),
Section 7, CR-CLAM-006. The full prose, including its tables and rationale, is
preserved verbatim in that file.
