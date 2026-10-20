---
plan_id: CLAM-IMPLEMENTATION-PLAN-2026-10
title: Holistic implementation plan for CR-CLAM-002 through CR-CLAM-010
status: Proposed (informs slice planning; binding-model changes still require per-CR compatibility review)
prepared: 2026-10-19
scope: Nine CRs from the 2026-10-18 CR-CLAM-002..010 package plus the data-model enrichment and migration principles that accompany them
baseline_repository: emmanuel-a-otchere/Closed-Loop-Management (main at 99816c9; harvest PR #31 in Review)
source_package: governance/PACKAGE1-MANIFEST.json
applies_to_release: v2.0.0 Architecture (semantic and assurance) and v2.1.0 Operations (bounded autonomy and inter-loop coordination)
---

# Holistic implementation plan: CR-CLAM-002 through CR-CLAM-010

## 1. Purpose

Lay out a sequenced, dependency-aware, slice-shaped implementation
roadmap that turns the nine specification-first change requests
landed via the 2026-10-18 package into a coherent multi-release
programme for the `Closed-Loop-Management` repository. The plan is
deliberately conservative: it follows the user's stated principle
that meaning precedes representation, binding-model changes arrive
after separate compatibility review, and every implementation
landing supports a documented acceptance criterion with evidence.

This plan does not itself approve any CR. Each CR proceeds through
the repository's existing governance process (this plan is the
context that document refers to). Where the plan proposes a slice
shape for a CR, the slice PR is the artefact that carries the CR
forward.

## 2. Prerequisites and ordering rules

The plan assumes:

- **PR #31** (the CR-CLAM-000 harvest) is merged into `main`.
- **CR-CLAM-001** has been approved in its Stage 4 governance
  review (it is the only CR with no upstream dependency and its
  outcomes -- the normative capability catalogue and the two
  ADRs -- establish the authority for every subsequent CR).
- The **external-SDO safeguard** in `context/AGENT-DOCTRINE.md`
  is observed at all times. No references to embargoed external
  SDOs or their frameworks.
- All commits observe D-004, D-005, the cardinal author rule,
  OAS-first, branch-per-task, and the surgical-changes rule.

Three ordering rules govern the slices:

1. **Meaning before representation.** A slice that changes the
   binding model only lands AFTER a normative specification has
   been accepted for the relevant concept.
2. **Compatibility is a separate review.** Any binding-model
   change is preceded by a compatibility assessment per
   `governance/data-model/MIGRATION-AND-COMPATIBILITY.md` and
   lands as a separate, smaller PR from the conceptual
   specification.
3. **Evidence before claim.** A capability is not recorded as
   implemented until a `governance/traceability/CR-requirements.csv`
   row points at concrete passing evidence.

## 3. Governance node map

The plan operates on the existing kanban board 14
(`discord-closed-loop-automation`). Card 468 is the programme
parent (currently in Review waiting for PR #31 to merge). Cards
469-478 are the ten CRs in Backlog. Cards 479-480 are the two
strategic ADRs.

| Node | ID | Current column | Move rule |
| --- | --- | --- | --- |
| Programme parent | 468 | Review (58) | "Done" when PR #31 merges |
| CR-CLAM-001 | 469 | Backlog (56) | In Progress on first slice PR open |
| CR-CLAM-002..010 | 470-478 | Backlog (56) | In Progress on their first slice PR open |
| ADR-CLAM-0001/0002 | 479/480 | Backlog (56) | Accepted on CR-CLAM-001 Stage 4 ratification |

The plan adds per-slice cards for the binding-model implementation
PRs. Per-slice cards are tracked in the PR description's task list
and reflected in the snapshot doc; the parent CR card moves to
Done only when every slice for that CR has merged and its declared
acceptance criteria are evidenced.

## 4. Concept decision gate (runs once)

A single CR-CLAM-001-adjacent review -- the "concept disposition
review" -- decides for each candidate concept in
`governance/data-model/CLAM-DATA-MODEL-ENRICHMENT-PROPOSAL.md`
whether it lands as:

- **(A) An embedded value object** within an existing entity.
- **(B) A referenced resource** under a new path.
- **(C) An event record** under an event-streaming endpoint.
- **(D) An external reference** whose payload lives outside CLAM.
- **(E) Deferred** to a future CR with rationale recorded.

The principle "minimise entity proliferation" (modelling principle
10 of the enrichment proposal) is the deciding bias. The
disposition table is committed under
`governance/data-model/concept-disposition-2026-10.md` as part of
the CR-CLAM-001 Stage 3 deliverables. Every CR-CLAM-002..010
binding-model slice cites that table for each concept it
introduces.

## 5. The implementation slices

Each CR is delivered as one to three slice PRs. Slice PRs share
the same template (the existing Slice N PR1..PR4 shape used in
slices 1-7): first PR reconciles and binds, second PR implements
the binding changes, third PR (only when needed) adds tooling or
tests that the first two cannot accommodate. Each CR is closed
with a governance close-out PR that updates CHANGELOG, AGENT-
DOCTRINE if needed, and the kanban snapshot.

### Slice 01 -- Foundational (CR-CLAM-001 + ADR acceptance)

- **Slice PRs**: PR #31 (harvest; in Review), then PR1
  reconnaissance, PR2 gap analysis, PR3 normative spec,
  PR4 governance acceptance.
- **Outputs**: `governance/capability-inventory.md`,
  `governance/capability-gap-analysis.md`,
  `governance/capability-model.md`,
  `governance/architecture-boundaries.md`,
  `governance/capability-requirements.md`,
  `governance/capability-traceability.md`,
  `governance/data-model/concept-disposition-2026-10.md`.
- **Acceptance**: Twelve ACs from canonical CR-CLAM-001 pass.
  ADRs 479 and 480 advance from Proposed to Accepted. Card 469
  moves to Done.

### Slice 02 -- Semantic model and state separation (CR-CLAM-002)

Depends on Slice 01.

- **CR-CLAM-002 PR1 (this slice)** -- produce the binding
  semantic model and state-dimension specification:
  - `governance/data-model/semantic-model-1.0.md`
    (extends the existing
    `schemas/data-model/clam-data-model-1.0.md`)
  - `governance/data-model/state-dimensions-1.0.md` (4 dimensions
    with transition/interaction rules)
  - Compatibility assessment per migration principles.
- **CR-CLAM-002 PR2 (this slice)** -- binding-model PR *only*
  if compatibility assessment concludes additive-compatible.
  Additive v1.1 enums and optional value objects. No removal,
  no rename. Strictly additive to the binding OpenAPI document.
- **Acceptance**: AC-002-01..07 pass; existing v1.0 payloads
  parse unchanged; the CLI regression suite is green.
- **Card moves**: 470 to In Progress on PR1 open, to Review on
  PR1 CI green, to Done on PR2 merge and AC evidence check.

### Slice 03 -- Traceability (CR-CLAM-003)

Depends on Slice 02 (and 01 by transitive closure per the package
dependency statement).

- **CR-CLAM-003 PR1** -- traceability model specification and
  reference implementation: `governance/data-model/traceability-
  model-1.0.md`, `machines/scripts/validate_traceability.py`,
  positive/negative fixtures under `datasets/conformance/trace/`.
- **CR-CLAM-003 PR2** -- CLI integration + CI gate (conformance
  suite extension).
- **Acceptance**: AC-003-01..06 pass.
- **Card moves**: 471.

### Slice 04 -- Conformance and design validation (CR-CLAM-004)

Depends on Slices 02 and 03.

- **CR-CLAM-004 PR1** -- validation architecture and rule
  catalogue: `machines/toolkits/clam-conformance/` (replaces
  the existing `clam-oas-validator` toolkit with the staged
  architecture). Rules listed by stable identifier, severity
  policy explicit, machine-readable report schema published.
- **CR-CLAM-004 PR2** -- CI integration: the existing
  `cardinal-conformance` job consumes the staged validator's
  gate output.
- **Acceptance**: AC-004-01..06 pass; existing v1.0 fixtures
  produce deterministic results.
- **Card moves**: 472.

### Slice 05 -- Simulation, evidence, in parallel (CR-CLAM-005 + CR-CLAM-006)

Two CRs in parallel because they share conceptual substrate but
land as separate binding artefacts. Depends on Slices 03 and 04.

- **CR-CLAM-005 PR1** -- scenario specification and runner;
  binds `schemas/proposals/scenario.schema.json` (with
  `proposal-0.1` -> `scenario-1.0` rename). Replay determinism
  test added.
- **CR-CLAM-005 PR2** -- scenario fixtures + CI regression.
- **CR-CLAM-006 PR1** -- evidence and verification schema;
  binds `schemas/proposals/evidence-record.schema.json` (renamed
  to `evidence-record-1.0`). JSONL trace adapter emits evidence
  records.
- **CR-CLAM-006 PR2** -- KPI report adapter emits
  VerificationResult records.
- **Acceptance**: AC-005-01..06 pass; AC-006-01..06 pass; simulated
  evidence cannot be mistaken for operational (mandatory origin tag).
- **Card moves**: 473 and 474.

### Slice 06 -- Bounded autonomy + inter-loop coordination, in parallel (CR-CLAM-007 + CR-CLAM-008)

Depends on Slices 02, 03, 06 (sim/evidence).

- **CR-CLAM-007 PR1** -- bounded-autonomy specification and
  policy schema: `schemas/proposals/policy.schema.json` binds
  as `policy-1.0`. Decision table for violation responses
  published. Enforcement-responsibility rule is added to the
  concept table per the schema's `enforcementResponsibility`
  field -- Critical: this slice writes the management contract
  for bounded autonomy, not an execution engine.
- **CR-CLAM-007 PR2** -- policy fixtures + decision-table
  conformance tests.
- **CR-CLAM-008 PR1** -- inter-loop coordination model:
  `schemas/data-model/inter-loop-contract-1.0.md`, link
  type extensions to ClosedLoopLink where additive.
- **CR-CLAM-008 PR2** -- coordination scenarios (failure
  propagation, resource contention, goal conflicts) wired into
  the simulation suite.
- **Acceptance**: AC-007-01..06 pass; AC-008-01..06 pass.
- **Card moves**: 475 and 476. Sequencing qualification from
  CR-CLAM-007: this slice establishes governance semantics
  BEFORE any production-oriented autonomous execution adapter
  is authorised. No execution adapter ships under v2.x without
  Slice 06 ratified.

### Slice 07 -- Operational observability and recovery (CR-CLAM-009)

Depends on Slices 06 (sim/evidence + bounded autonomy) and the
failure-propagation contract from CR-CLAM-008.

- **CR-CLAM-009 PR1** -- operational event model and health
  vocabulary. Health and degraded-condition enums additive.
- **CR-CLAM-009 PR2** -- operational-event fixtures and
  recovery trace tests.
- **Acceptance**: AC-009-01..06 pass.
- **Card moves**: 477.

### Slice 08 -- Evidence-based maturity (CR-CLAM-010)

Depends on Slices 01, 06, and the capability catalogue from
CR-CLAM-001.

- **CR-CLAM-010 PR1** -- maturity model with five dimensions
  and scoring rubric. Existing `maturity-assessment` toolkit
  extended with capability-based scoring; CSV template updated.
- **CR-CLAM-010 PR2** -- pilot assessment: at least three
  representative loop profiles scored. Score-determinate path
  records evidence per assessment row.
- **Acceptance**: AC-010-01..06 pass.
- **Card moves**: 478.

## 6. Sequencing table

| Slice | CR(s) | Priority | Depends on | Standalone PRs | Outcome |
| --- | --- | --- | --- | --- | --- |
| 1 | CR-CLAM-001 | P0 | -- | 4 (PR #31 + 3 more) | Normative capability baseline, 2 ADRs ratified |
| 2 | CR-CLAM-002 | P0 | S1 | 2 | Semantic model + 4-state dimension baseline |
| 3 | CR-CLAM-003 | P0 | S1, S2 | 2 | Traceability chain + conformance tooling |
| 4 | CR-CLAM-004 | P1 | S2, S3 | 2 | Conformance validator with staged rules |
| 5 | CR-CLAM-005, CR-CLAM-006 | P1 | S3, S4 | 4 (2 per CR, run in parallel) | Scenario + evidence contracts |
| 6 | CR-CLAM-007, CR-CLAM-008 | P1 | S2, S3, S5 | 4 (2 per CR, run in parallel) | Bounded autonomy + coordination contracts |
| 7 | CR-CLAM-009 | P2 | S5, S6 | 2 | Operational event + recovery contract |
| 8 | CR-CLAM-010 | P2 | S1, S5 | 2 | Capability-based maturity scoring |

Total: ~21 PRs across 8 slices, four phases. The v2.0.0 release
ships at end of Slice 6 (semantic + verification + bounded
autonomy foundation). The v2.1.0 release ships at end of Slice 8
(operational observability + maturity).

## 7. Cross-cutting concerns

- **Schema versioning policy.** Every binding schema lands under
  `schemas/<area>/<name>-1.0.<n>.{md,json}` with an explicit
  `schemaVersion` field. Compatibility per
  `governance/data-model/MIGRATION-AND-COMPATIBILITY.md`. The
  OpenAPI document is regenerated via
  `machines/scripts/export_openapi.py` (OAS-first rule).
- **Capability ID scheme.** The CR-CLAM-001 catalogue uses
  `CLAM-CAP-<DOMAIN>-<NUMBER>` (illustrative per canonical
  proposal). The scheme is applied at first need, not
  pre-allocated, per the standing convention.
- **Traceability CSV.** Every implementation slice PR updates
  `governance/traceability/CR-requirements.csv` (or its successor
  after Slice 3 lands the formal register format) with the
  evidence pointer that demonstrated the AC.
- **Snapshot doc.** Per-slice card moves are appended to
  `~/.hermes/profiles/coder/kanban/closed-loop-automation-kanban-snapshot-2026-10-10.md`
  on every move.
- **Dataset folder expansion.** Existing `datasets/examples/`
  grows with per-slice fixtures. Slices that produce schemas
  also produce `datasets/conformance/` fixtures (positive +
  negative + version-mismatch where relevant).

## 8. Out of scope

- Building a general execution runtime (CLAM remains the
  management contract).
- Mandating a specific AI framework, policy engine, simulation
  engine, telemetry platform, or graph database.
- Replacing v1.0 fields silently (any such change requires a
  separate compatibility CR with a documented migration path).
- Introducing any autonomous execution adapter authorised
  before Slice 6 (CR-CLAM-007) is accepted.

## 9. Risk register (programme-level)

| Risk | Mitigation |
| --- | --- |
| Concept disposition drifts under implementation pressure. | Lock the disposition table in Slice 1; per-CR implementation must cite the table for each binding change. |
| Scenario / evidence fixtures become stale. | Pin fixtures to scenario / schema version; CI rejects fixtures older than the pinned version. |
| Bounded-autonomy PRs grow into a runtime. | Pre-commit review gate: any code under `machines/runtime/` requires an ADR first; Slice 6 explicitly states the management-contract-only scope. |
| Maturity calculator becomes a vanity metric. | Bind every published score to a remediation CR via `traceability/CR-requirements.csv`. |
| Snapshot doc drifts from board state. | Per-slice close-out appends to the snapshot doc as part of CI; gate fails otherwise. |
| External-SDO safeguard slips through under citation. | Cardinal-rules CI gate (which scans for the embargo terms) already runs; each Slice PR must be green before merge. |

## 10. Acceptance for this plan

This plan is itself accepted when:

- The 9 CR-CLAM-002..010 governance files in the repo match
  the canonical package versions (package1 integration merged).
- The `concept-disposition-2026-10.md` file lands as part of
  Slice 1.
- The traceability CSV links each requirement to one or more
  concrete evidence rows.
- The two ADRs (479, 480) are explicitly ratified as part of
  the governance close-out for Slice 1.

This plan is deliberately living: as each slice closes, its
results refine the remaining slices' scope, and the snapshot doc
records every revision.

## References

- Harvest PR #31: the CR-CLAM-000 review + canonical
  CR-CLAM-001 proposal landed.
- `governance/reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md`.
- `governance/reviews/2026-10-18-CR-CLAM-001-normative-capability-model.md`.
- `governance/PACKAGE1-MANIFEST.json`: the 2026-10-18 package
  inventory.
- `governance/CR/CR-CLAM-002..010-*.md`: canonical CR files
  (replaced by package1 integration).
- `governance/data-model/CLAM-DATA-MODEL-ENRICHMENT-PROPOSAL.md`.
- `governance/data-model/CLAM-MODEL-RELATIONSHIPS.md`.
- `governance/data-model/MIGRATION-AND-COMPATIBILITY.md`.
- `governance/schemas/proposals/*.schema.json`.
- `governance/datasets/proposals/*.example.json`.
- `governance/traceability/CR-requirements.csv`.
- `context/AGENT-DOCTRINE.md` for binding cardinal rules.
