# Governance

This directory is the durable home for the formal governance
artefacts of the `Closed-Loop-Management` repository. It was
introduced by the harvest landing that mapped the
`CR-CLAM-000` capability review (2026-10-18) and the proposed
`CR-CLAM-001..010` programme into the repository's persistent
record.

## Layout

```
governance/
|-- reviews/         # Source artefacts preserved verbatim from
|                    # the originating documents (.docx -> .md).
|-- CR/              # Canonical Change Request (CR) documents.
|-- ADR/             # Architectural Decision Records (ADR).
|-- decisions/       # Operational or tactical decisions that are
|                    # not architectural (separate from ADR/).
|-- README.md        # This file.
```

## Reviews

The starting point for the CR-CLAM programme is the comprehensive
capability review prepared on 2026-10-18 and submitted for
harvest. The full text of the review and the originating CR-CLAM-001
specification is preserved as markdown:

- [`reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md`](reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md)
  -- the 12-section capability review covering executive
  assessment, three architectural responsibilities, semantic
  gaps, tool enhancements, evidence-based capability realisation,
  bounded autonomy, the proposed CR programme, implementation
  sequencing, repository-level enhancements, two strategic
  decisions to settle first, the recommended first CR, and the
  final recommendation.
- [`reviews/2026-10-18-CR-CLAM-001-normative-capability-model.md`](reviews/2026-10-18-CR-CLAM-001-normative-capability-model.md)
  -- the full canonical proposal for CR-CLAM-001 (the P0
  foundational CR) preserved verbatim.

These documents are the source of truth for the programme context.

## Change Requests (CR)

The CR catalogue consists of ten change requests in four phases:

| CR | Title | Phase | Priority |
| --- | --- | --- | --- |
| [CR-CLAM-001](CR/CR-CLAM-001-normative-capability-model.md) | Normative capability model (with 7 capability domains A-G) | 1 | P0 |
| [CR-CLAM-002](CR/CR-CLAM-002-closed-loop-semantic-model-and-state-separation.md) | Semantic model and state separation | 1 | P0 |
| [CR-CLAM-003](CR/CR-CLAM-003-intent-constraints-and-capability-traceability.md) | Intent/constraints/capability traceability | 1 | P0 |
| [CR-CLAM-004](CR/CR-CLAM-004-clam-conformance-and-design-validation-toolkit.md) | Conformance and design validation toolkit | 2 | P1 |
| [CR-CLAM-005](CR/CR-CLAM-005-scenario-based-simulation-and-behavioural-verification.md) | Scenario-based simulation | 2 | P1 |
| [CR-CLAM-006](CR/CR-CLAM-006-evidence-and-outcome-verification-framework.md) | Evidence and outcome verification | 2 | P1 |
| [CR-CLAM-007](CR/CR-CLAM-007-runtime-governance-and-bounded-autonomy.md) | Runtime governance and bounded autonomy | 3 | P1 |
| [CR-CLAM-008](CR/CR-CLAM-008-inter-loop-coordination-and-conflict-management.md) | Inter-loop coordination | 3 | P1 |
| [CR-CLAM-009](CR/CR-CLAM-009-operational-observability-and-recovery.md) | Operational observability and recovery | 4 | P2 |
| [CR-CLAM-010](CR/CR-CLAM-010-evidence-based-maturity-and-improvement.md) | Evidence-based maturity and improvement | 4 | P2 |

CR-CLAM-001 is the only CR with no upstream dependency. The other
nine are sequenced by their declared dependencies; the explicit
dependency map is in their frontmatter.

## Architectural Decision Records (ADR)

Two strategic decisions must settle before the programme can
expand beyond CR-CLAM-001:

- [ADR-CLAM-0001](ADR/ADR-CLAM-0001-clam-scope-spec-plus-reference-impl.md)
  -- CLAM is a normative management model with a reference
  implementation and supporting engineering toolchain (the
  "spec + impl + toolchain" position from CR-CLAM-000 Section 10,
  Decision A).
- [ADR-CLAM-0002](ADR/ADR-CLAM-0002-successful-closed-loop-operation.md)
  -- successful closed-loop operation is defined in terms of
  verified outcomes against declared intent and constraints,
  with a three-valued judgement (satisfied / not satisfied /
  indeterminate). Anchors CR-CLAM-002 and CR-CLAM-006.

Both ADRs are currently **Proposed** and become **Accepted** when
the governance review in CR-CLAM-001 Stage 4 completes.

## Operational discipline

- Every CR has a stable identifier (`CR-CLAM-NNN`) and a YAML
  frontmatter block at the top of its file.
- Every ADR carries its status in frontmatter; transitions move
  from `Proposed` to `Accepted` (or `Superseded`/`Deprecated`)
  through a dated commit that updates the file.
- All governance files are subject to the cardinal rules in
  `context/AGENT-DOCTRINE.md` (cardinal author, D-004, D-005,
  the external SDO references safeguard, OAS-first, surgical
  changes, branch per task).
- The kanban board at
  `http://192.168.50.160:7000/board/14`
  (project `discord-closed-loop-automation`) carries cards for
  every CR/ADR/recon/test/task on this channel. Each card links
  back to the matching `governance/` file by ID.
