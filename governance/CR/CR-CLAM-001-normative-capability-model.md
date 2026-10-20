---
cr_id: CR-CLAM-001
title: Establish the Normative Closed-Loop Management Capability Model
status: Proposed
priority: P0
type: Foundational
repository: emmanuel-a-otchere/Closed-Loop-Management
dependencies: []
source_review: CR-CLAM-000 (Section 11)
---

# CR-CLAM-001: Establish the Normative Closed-Loop Management Capability Model

## Change summary

Establish a normative capability model for CLAM that defines its
purpose, scope, responsibilities, architectural boundaries, and
conformance requirements. The model shall provide the foundation for
all subsequent capability, semantic, validation, simulation,
evidence, and governance enhancements.

This CR establishes what CLAM must be capable of doing and how that
capability is demonstrated. It does not implement the subsequent
enhancements.

## Status of the canonical proposal

The full canonical proposal for CR-CLAM-001 -- the version submitted
to the repository on 18 October 2026 and accepted as the
specification-first basis for the CR-CLAM programme -- is preserved
verbatim at:

- [`governance/reviews/2026-10-18-CR-CLAM-001-normative-capability-model.md`](../../reviews/2026-10-18-CR-CLAM-001-normative-capability-model.md)

That document is authoritative for the full change set, acceptance
criteria, and out-of-scope boundaries. It is the seed of the
CR-CLAM-001 implementation procedure (Stage 1 reconnaissance, Stage 2
capability analysis, Stage 3 normative specification, Stage 4 review
and acceptance) reproduced here as a concise index.

## Capability domain index (per the canonical proposal)

The canonical proposal defines seven capability domains with stable
identifier prefix `CLAM-CAP-<DOMAIN>-<NUMBER>`:

| Domain | Prefix | Purpose |
| --- | --- | --- |
| Closed-Loop Engineering | `CLAM-CAP-ENG-` | Define and validate a closed-loop design against its intended purpose and operating requirements. |
| Closed-Loop Lifecycle Management | `CLAM-CAP-LCM-` | Manage closed loops as governed assets throughout their lifecycle. |
| Execution Integration and Control Boundaries | `CLAM-CAP-EXE-` | Establish the contracts under which external execution mechanisms participate in a managed closed loop. |
| Operational Management | `CLAM-CAP-OPS-` | Assess and govern a managed closed loop during operation. |
| Inter-Loop Coordination | `CLAM-CAP-COO-` | Govern relationships and dependencies between multiple closed loops. |
| Verification and Assurance | `CLAM-CAP-VER-` | Establish whether a design and its observed behaviour satisfy declared requirements and constraints. |
| Governance and Continuous Improvement | `CLAM-CAP-GOV-` | Govern the evolution of closed loops and the CLAM capability itself. |

Illustrative identifiers from the canonical proposal:

- `CLAM-CAP-LCM-001`: a managed closed loop shall have a uniquely identifiable lifecycle record.
- `CLAM-CAP-ENG-001`: a closed-loop design shall be assessable against its declared requirements.
- `CLAM-CAP-VER-001`: a verification result shall identify the criterion being evaluated.
- `CLAM-CAP-OPS-001`: operational status shall be distinguishable from verified goal achievement.

These IDs are illustrative; the working catalogue is established in
Stage 3 of the implementation procedure and recorded in the
capability-requirements.md deliverable.

## Implementation procedure (stages)

The canonical proposal defines a four-stage procedure. Only Stage 1
(reconnaissance) is permitted to land before CR-CLAM-001's
acceptance; Stages 2-4 ship as the follow-on deliverables.

| Stage | Output | When |
| --- | --- | --- |
| 1. Repository reconnaissance | Repository capability inventory | First PR after this CR is approved. |
| 2. Capability analysis against the seven domains | Capability gap analysis | After Stage 1 review. |
| 3. Normative specification | Capability model, architecture boundaries, requirement catalogue, traceability matrix | After Stage 2 review. |
| 4. Review and acceptance | Acceptance record, follow-on backlog | Final PR. |

## Acceptance criteria

CR-CLAM-001 is complete when all twelve AC-NNN criteria in the
canonical proposal pass -- `AC-001` through `AC-012` -- covering
completeness, traceability, manageability of partial/unverified
status, stable requirement identifiers, and unchanged binding
contracts.

## Out of scope

CR-CLAM-001 explicitly excludes ten items per the canonical proposal's
out-of-scope section. Highlights:

- Replacing the existing information model.
- Introducing a new execution runtime.
- Implementing AI agents or a specific AI framework.
- Changing the existing lifecycle state machine without an ADR.
- Mandating a particular telemetry or observability platform.

These subjects may become subsequent CRs once the normative baseline
establishes their requirements and dependencies.

## Dependencies and follow-on

CR-CLAM-001 has no dependencies. Its outputs feed CR-CLAM-002
through CR-CLAM-010 (see those CRs for their explicit dependency
statements).

## Source

The full proposal lives at
[`governance/reviews/2026-10-18-CR-CLAM-001-normative-capability-model.md`](../../reviews/2026-10-18-CR-CLAM-001-normative-capability-model.md)
and the broader context in
[`governance/reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md`](../../reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md),
section 11.
