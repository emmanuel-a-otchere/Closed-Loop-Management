# Agent Doctrine -- `emmanuel-a-otchere/Closed-Loop-Management`

This document is binding on every agent that lands on this repo. It mirrors
the cardinal rules of the Discord channel that owns this work and makes the
kanban / project-board discipline structural rather than aspirational.

## Cardinal rules (apply to every change)

1. **Cardinal author rule**: every commit on `main` must be authored by
   `@emmanuel-a-otchere`. The CI gate (`cardinal-rules` job) verifies the
   last commit's author.
2. **D-004** (GitHub language): no em-dash (U+2014), en-dash (U+2013), or
   triple-punctator (U+2E3B) in any GitHub artefact (markdown, YAML, TOML,
   Python source). CI runs `grep -rln` over the tree and fails on a hit.
3. **D-005**: no triple-punctator semicolons in prose. The two-semicolon divider is preserved.
4. **No TMForum references**: never reference TMForum, eTOM, Frameworx, SID,
   GB921, TAM, ODF, OSS/BSS in this repo. Substitutes are ITU-T M.3050.x,
   ETSI TS, ISO/IEC, NIST, or SDO-neutral standardization.
5. **OAS-first**: the OAS 3.1 document served at `/openapi.json` is the
   contract. Source-of-truth is the Pydantic models in
   `machines/service/clam/models.py`. Do not hand-edit
   `schemas/openapi/openapi.json`; regenerate via
   `machines/scripts/export_openapi.py`.
6. **Surgical changes**: every changed line traces to a stated user request
   or an explicit acceptance criterion. Do not "improve" adjacent code as
   a side effect.
7. **Reversibility**: every change lives on a branch off `main`. No direct
   commits to `main` without explicit user approval.

## Per-channel kanban discipline

The Discord channel `#closed-loop-automation` (thread 1558338973213003777,
parent 1558335528297041981, guild 1496909480783249428) owns this repo. Every
action, CR, ADR, test, task, activity, recon, or decision that touches the
CLAM API MUST produce a kanban card.

### Boards

| Surface | URL | Identifier |
| --- | --- | --- |
| Kanban board | http://192.168.50.160:7000/board/14 | `discord-closed-loop-automation` |
| GitHub Project | https://github.com/users/emmanuel-a-otchere/projects/14 | (project N) |

The Kanban columns are `Backlog / In Progress / Review / Done`.

### Lifecycle

| Event | Card move |
| --- | --- |
| Branch pushed to remote | `Backlog` -> `In Progress` |
| PR opened | (no move; comment with PR URL) |
| PR CI green, awaiting review | `In Progress` -> `Review` |
| PR merged | `Review` -> `Done` |
| Cardinal author flag raised | card stays put, `blocker` tag attached |
| Blocked on user input | `kanban_block` (comment thread captures question) |

### Skill

The companion skill `closed-loop-automation-kanban-discipline` (in the
agent profile) encodes the channel-specific scope-lock, tag set, and
commands. Load it on every entry to this channel.

## Project governance

- **GitHub Project board** (project N): WBS epic issues linked from
  `.github/epics/`.
- **Repo milestones**: `v1.0.0 MVP`, `v1.1.0 Features`, `v1.2.0 Extensions`,
  `v2.0.0 Architecture`.
- **CHANGELOG.md**: every PR updates the unreleased section.
- **CHANGELOG entry commits**: keep a `chore(release)` or `docs(changelog)`
  commit separate from feature commits.

## Definition of done -- Slice N

A slice is "done" when:

1. All acceptance criteria on the matching epic issue are checked off.
2. `pytest`, `ruff check`, and `mypy api/` are green in CI.
3. `openapi/openapi.json` matches the live OAS served at `/openapi.json`.
4. D-004 / D-005 / cardinal-author gates pass in CI.
5. CHANGELOG.md has a slice entry.
6. The corresponding kanban card is in `Done`.
7. The corresponding epic issue is closed with a `Closes #N` link.

## Snapshot discipline

The agent profile's snapshot doc for this channel is:

```
~/.hermes/profiles/coder/kanban/closed-loop-automation-kanban-snapshot-2026-10-10.md
```

The snapshot is regenerated after every card move. Future snapshots are
dated siblings; the diff between snapshots is the audit trail.

## Related

- `docs/data-model/clam-data-model-1.0.md` -- the binding data model
- `docs/api/OVERVIEW.md` -- API tour (single-source integration guide)
- `docs/diagrams/` -- Mermaid / PlantUML source for the system diagrams
- `docs/conceptual/paradigm.md` -- position paper
- `.github/epics/` -- WBS epic specs
- `CHANGELOG.md` -- release log

## Slice 2 close-out (2026-10-11)

Slice 2 was split into 3 PRs, all merged into `main`:

- **Slice 2 PR1** -- Activity / Workflow / Goal / ClosedLoopLink first-class
  CRUD with their own IDs and lifecycles. Denormalised columns on the
  SQLite tables for filtered listing.
- **Slice 2 PR2** -- Cross-resource lifecycle constraints
  (publish-workflow-with-unpublished-activities, retire-activity-still-in-use,
  delete-blocked-by-reference) + GET /closedLoop/{id}/goalRollup
  aggregating achievement across CLOSED_LOOP / WORKFLOW / ACTIVITY scopes.
- **Slice 2 PR3** -- ClosedLoopLink cycle detection (single + bulk),
  topology view, BFS path query, downstream/upstream neighbour endpoints.

Slice 2 deferred (kept on the books):

- Authentication layer (planned for Slice 4).
- Per-kind topology semantics on top of cycle detection (DAISY_CHAIN
  linear-only enforcement, HIERARCHICAL parent/child acyclic tree,
  FEEDBACK peer rules, SHADOW read-only mirrors). The `kind` field is
  carried on the model; rules are a layer above cycle detection.
- Junction tables for activity/workflow references -- the slice-2
  constraint checks walk the relevant table payloads (O(N) per check).
  Fine for the MVP SQLite store; a junction table is the proper fix at
  scale.
- Cross-loop goal rollups (an outer loop's achievement stats summing
  weighted rollups of its child links).