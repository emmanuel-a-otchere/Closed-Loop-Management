# Changelog

All notable changes to the CLAM REST API are documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/) and this project
adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Slice 3 PR1 -- opt-in bearer-token authentication. CLAM_AUTH_ENABLED env
  var defaults to false; production deployments flip it to true. Scope levels
  READ < WRITE < ADMIN (higher implicitly grants lower). New endpoints
  POST /auth/tokens (issue), GET /auth/tokens (list), DELETE
  /auth/tokens/{tokenId} (revoke), GET /auth/whoami (current principal).
  Middleware enforces WRITE on POST/PUT/PATCH/DELETE; ADMIN on
  /api/v1/auth/tokens. Bootstrap path: first issuance on a fresh install
  bypasses auth so the operator can mint the first admin token. New error
  codes auth.unauthorized (401) and auth.forbidden (403). In-memory
  TokenStore (SHA-256-fingerprinted) with the interface shaped for swap to
  a DB-backed implementation.
- Slice 3 PR2 -- per-kind topology rules layered on top of cycle detection:
  DAISY_CHAIN linear-only (at most one incoming + one outgoing DAISY_CHAIN
  edge per node), HIERARCHICAL single-parent (at most one HIERARCHICAL
  parent per node), FEEDBACK peer-only (no ancestor/descendant relationship
  through HIERARCHICAL closure), SHADOW read-only mirror (mirror targets
  cannot drive non-SHADOW links). All-or-nothing bulk semantics preserve
  a single-rule-violation rejection across the whole batch. New error
  code topology.rule_violated (409) with details {rule, kind, offenders}.
- Slice 3 PR3 -- junction tables (workflow_activity, closed_loop_workflow)
  replace the prior O(N*M) payload walks used by the Slice 2 PR2 lifecycle
  constraint checks. Write paths maintain the junction tables on
  create / update / delete of workflows and closed loops. New endpoint
  POST /closedLoop/{loopId}/workflow/{workflowId} links a workflow to a
  loop (idempotent; 404 if either entity is missing).
- Slice 3 PR4 -- cross-loop nested goal rollup. The GET
  /closedLoop/{id}/goalRollup endpoint now traverses outgoing
  HIERARCHICAL + DAISY_CHAIN edges (default; configurable via
  include_nested / nested_kinds / max_depth) and includes reachable
  loops' goals in the unified rollup. FEEDBACK peers and SHADOW mirrors
  are excluded from the rollup. New fields on the rollup response:
  nested[] (per-child-loop rollup snapshots) and depth (max nested depth
  traversed).

## [0.1.0] -- 2026-10-10

### Added
- Slice 1 -- repo revamp, FastAPI skeleton, OAS 3.1 data model, ClosedLoop +
  DecisionModel CRUD, ClosedLoop state transitions, error envelope, pagination,
  downloadable examples, GitHub Project + Kanban board, CI lint + test gates.
