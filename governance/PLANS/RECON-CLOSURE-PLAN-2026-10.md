---
plan_id: RECON-CLOSURE-PLAN-2026-10
title: Reconnaissance findings closure plan
status: In progress
prepared: 2026-10-20
scope: Closure of the findings from the 2026-10-20 repository reconnaissance: hygiene fixes, CI gate hardening, and the CR-CLAM-002..010 slice programme per CLAM-IMPLEMENTATION-PLAN-2026-10
baseline_repository: emmanuel-a-otchere/Closed-Loop-Management (main at 29b77d0)
---

# Reconnaissance findings closure plan

## 1. Purpose

Convert the 2026-10-20 reconnaissance findings into a tracked,
dependency-ordered closure programme. This plan is the execution
overlay on
[`CLAM-IMPLEMENTATION-PLAN-2026-10.md`](CLAM-IMPLEMENTATION-PLAN-2026-10.md):
it sequences the hygiene and truthfulness fixes first (they are
cheap, unblock trust in every other artefact), then follows the
existing slice programme for CR-CLAM-002..010 without duplicating
or reordering it.

## 2. Findings register

| ID | Finding | Severity | Owner tranche |
| --- | --- | --- | --- |
| F-01 | Slice 1 (CR-CLAM-001) not started; no capability inventory, gap analysis, capability model, architecture boundaries, or concept-disposition table | P0 | T2 |
| F-02 | README truthfulness: asset table lists 5 of 9 toolkits; epics index stale (slice-{1..5} vs 7 landed); project board link says projects/13 vs doctrine projects/14 | P1 | T1 |
| F-03 | Doctrine contradiction: AGENT-DOCTRINE rule 4 bans TMForum references while README cites TM Forum IG1219A / TR284C | P1 | T1 |
| F-04 | CI OAS snapshot check emits a warning and exits 0; drift never fails the build despite the OAS-first rule | P1 | T1 |
| F-05 | Traceability CSV is manual and unvalidated; no validate_traceability tooling | P2 (CR-CLAM-003 scope) | T3 |
| F-06 | Proposal schemas (scenario, evidence-record, policy) not bound as versioned 1.0 contracts | P2 (CR-CLAM-005/006/007 scope) | T3 |
| F-07 | No staged conformance validator (clam-conformance) replacing clam-oas-validator | P2 (CR-CLAM-004 scope) | T3 |
| F-08 | No inter-loop conflict/cycle validation in topology tooling | P2 (CR-CLAM-008 scope) | T3 |
| F-09 | Maturity toolkit not evidence-bound to traceability rows | P2 (CR-CLAM-010 scope) | T3 |
| F-10 | 130 of 179 tests concentrated in one test_api.py; no per-router negative-path auth tests | P3 | T4 |
| F-11 | Stale open epics #4 (Slice 2) and #5 (Slice 3) although work is merged | P3 | T1 |
| F-12 | No container/demo packaging (Dockerfile, compose, seed profile) for one-command exploration | P3 | T4 |

## 3. Tranches

### Tranche 1 -- Hygiene and truthfulness (this PR)

Closes F-02, F-03, F-04, F-11. Pure docs, decision record, and CI
yaml. No binding-model change.

- README: full asset table (all 9 toolkits), corrected project
  board link (projects/14 per AGENT-DOCTRINE), epics index note
  reflecting the slice-1..7 landing, lineage section rewritten
  without embargoed-SDO references.
- `governance/decisions/D-2026-10-20-standards-references.md`:
  operational decision resolving F-03 (rule 4 applies; lineage
  citations replaced with SDO-neutral substitutes per rule 4).
- `.github/workflows/ci.yml`: OAS snapshot check becomes a hard
  gate (exit 1 on drift).
- Close stale epics #4 and #5 with a comment pointing at the
  merged slice PRs.

### Tranche 2 -- CR-CLAM-001 Slice 1 execution (next PRs)

Closes F-01. Follows the four-stage procedure in
`governance/CR/CR-CLAM-001-normative-capability-model.md`.

- PR A (Stage 1): `governance/capability-inventory.md` mapping
  every repository component (service routers, store, toolkits,
  schemas, tests, CI) to the seven CLAM-CAP domains.
- PR B (Stage 2): `governance/capability-gap-analysis.md` per
  domain with explicit implemented / partial / proposed /
  unverified status and evidence pointers (satisfies AC-004,
  AC-005, AC-006).
- PR C (Stage 3): `governance/capability-model.md`,
  `governance/architecture-boundaries.md`,
  `governance/capability-requirements.md`,
  `governance/data-model/concept-disposition-2026-10.md`
  (satisfies AC-001..AC-003, AC-007..AC-009).
- PR D (Stage 4): acceptance record against AC-001..AC-012,
  traceability CSV evidence rows, CHANGELOG, kanban snapshot.

### Tranche 3 -- CR-CLAM-002..010 slices

Closes F-05..F-09 by executing the existing slice programme
(Slices 02..08 of CLAM-IMPLEMENTATION-PLAN-2026-10) unchanged in
order: semantics (002), traceability (003), conformance (004),
scenario + evidence (005/006), bounded autonomy + coordination
(007/008), operations (009), maturity (010). No re-sequencing;
this plan adds only that each slice PR also resolves its
registering finding above.

### Tranche 4 -- DX and packaging enrichment

Closes F-10, F-12. Low-risk, lands after Slice 02 (002) to avoid
churn during semantic binding changes.

- Split test_api.py per router; add per-endpoint negative-path
  auth tests.
- Dockerfile + loopback-only compose profile + seed_db demo
  profile.
- `clam-doctor` toolkit: one command running OAS validation,
  traceability validation, scenario fixtures, and conformance
  rules.

## 4. Acceptance for this plan

- Every finding in section 2 has a tranche and is either closed
  or carried by a named CR slice.
- Tranche 1 lands in one PR with CI green.
- Tranche 2 proceeds only after this plan lands.
