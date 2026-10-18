# Changelog

All notable changes to the CLAM REST API are documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/) and this project
adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Documentation
- Governance programme land (CR-CLAM-000 harvest). Adds the
  `governance/` tree with: `reviews/` (verbatim preserves of the
  CR-CLAM-000 capability review and CR-CLAM-001 canonical
  proposal, both .docx -> .md), `CR/` (canonical CR docs for
  CR-CLAM-001..010 with stable identifiers, frontmatter,
  acceptance criteria, out-of-scope boundaries, and explicit
  dependency statements), `ADR/` (ADR-CLAM-0001 on CLAM scope
  and ADR-CLAM-0002 on the definition of successful operation),
  and a top-level `governance/README.md` indexing the artefacts.
  No API, schema, lifecycle, or runtime behaviour changes in this
  landing; subsequent CR-CLAM-001 PRs will produce the normative
  capability, architecture-boundary, requirement-catalogue, and
  traceability artefacts called for by the canonical proposal.
- Package 1 integration (CR-CLAM-002..010 authoritative spec).
  Replaces the short-form CR-CLAM-002..010 harvests with the
  canonical package versions prepared 2026-10-18. The
  replacement files carry named acceptance criteria
  (`AC-NNN-NN`), a verification-approach section, a
  data-model-impact section, a compatibility/migration section,
  and common governance notes per CR. Adds a new
  `governance/data-model/` tree with three cross-cutting
  documents: the data-model enrichment proposal, the
  Mermaid relationship diagram, and the migration-and-
  compatibility principles. Adds `governance/schemas/proposals/`
  (three proposal JSON Schemas with `proposal-0.1` version),
  `governance/datasets/proposals/` (one illustrative example
  per schema), `governance/traceability/CR-requirements.csv`
  (an 18-row requirement-to-CR mapping with two requirements
  per CR), `governance/PACKAGE1-MANIFEST.json` and
  `governance/PACKAGE1-README.md` (the package's own
  inventory as a referral record), and
  `governance/PLANS/CLAM-IMPLEMENTATION-PLAN-2026-10.md` (the
  holistic multi-CR implementation plan covering all nine
  CRs as eight dependency-ordered slices across two releases).
  The README, traceability CSV, and CHANGELOG entries all
  cross-reference each other for navigation. No binding
  model, schema, lifecycle, or runtime behaviour changes in
  this landing; the canonical proposals remain Proposed
  pending CR-CLAM-001 governance acceptance.

### Added
- Slice 5 PR1 -- SSE audit stream endpoint. GET /api/v1/_stream/audit
  exposes text/event-stream per-process fan-out from the audit log
  writer; optional entityKind / entityId filters. A bounded
  asyncio.Queue[AuditEntry] per subscriber keeps the writer off
  the critical path on slow consumers (queue full => drop).
- Slice 5 PR2 -- webhook subscriptions CRUD. POST
  /api/v1/webhookSubscriptions (issue plaintext secret once),
  GET /api/v1/webhookSubscriptions (list), DELETE
  /{webhookId} (delete), GET /{webhookId}/deliveries (paginated).
  HMAC-SHA256 over the JSON body using the subscription's
  secret_hash; headers X-Clam-Signature (hex digest) and
  X-Clam-Event (action value). webhook_subscription +
  webhook_delivery tables; _fanout_webhooks fires per audit row.
- Slice 6 PR1 -- audit log retention + prune. POST
  /api/v1/audit/prune?before=<ISO-8601> (ADMIN; deletes
  every audit row with ts < before). POST
  /api/v1/audit/pruneByDays?days=<int 1..3650> (ADMIN;
  convenience wrapper around `today - N days`). The audit
  log is the durable record of state changes; pruning is
  destructive. External archive before invoking in
  production. New Store methods prune_audit_before +
  count_audit.
- Slice 6 PR2 -- persistent metrics counters (60s snapshot).
  /metrics now survives process restarts. New
  `metrics_snapshot` table; Store.snapshot_metrics /
  latest_metrics_snapshot / restore_metrics_from_snapshot.
  Lifespan restores from the latest snapshot on startup,
  background task takes one every
  CLAM_METRICS_SNAPSHOT_INTERVAL seconds (default 60),
  one final snapshot on shutdown. New GET /metrics/snapshot
  returns the latest row as JSON. Prometheus body appends
  `clam_metrics_snapshot_ts` so operators can tell whether
  the counter is freshly accumulated or restored from a
  snapshot.
- Slice 6 PR3 -- durable (DB-backed) token store + rotation.
  Tokens issued at runtime are persisted to the new
  `auth_token` table (token_id, secret_hash, name,
  scopes_json, issued_at, expires_at, revoked_at + 2
  indexes). They survive process restarts and remain
  authenticable after a fresh process boots. TokenStore is
  async-aware; constructed with a Store it delegates to the
  durable path. New endpoints GET
  /api/v1/auth/tokens/{tokenId} (single-token read with
  expiresAt + revokedAt) and POST
  /api/v1/auth/tokens/{tokenId}/rotate (201 with new
  plaintext; old token retired; auth.token.rotate audit
  row written). New model AuthTokenDetail; new audit
  action AuditAction.AUTH_TOKEN_ROTATE.
- Slice 7 PR1 -- clam-goalsim toolkit. New console script
  drives a closed loop through its canonical state path
  offline and projects goal achievement over N ticks.
  OODA / MAPE oscillate active <-> paused; CUSTOM one-shots
  to retired. GoalSimSpec + simulate + render_report; CLI
  flags --spec / --loop-id / --kind / --ticks / --trace /
  --format (table|json).
- Slice 7 PR2 -- clam-compare-decisions toolkit. Runs the
  same loop spec through two decision model kinds (default
  OODA vs MAPE) and renders a side-by-side markdown
  comparison (final state, transition count,
  ticks-to-active, per-tick trajectories) or JSON. Reuses
  goalsim.simulate so all kinds share one state machine.
- Slice 7 PR3 -- topology-as-script + audit-consumer
  toolkits. clam-topology-script converts a topology spec
  (JSON) into a runnable Python reproduction script that
  POSTs to a live CLAM API in dependency order
  (tolerates 200/201/409 for re-runnability).
  clam-audit-consumer walks GET /api/v1/audit with cursor
  pagination and dumps to CSV or JSON Lines; all endpoint
  filters are CLI flags; optional bearer token for
  auth-enabled deployments.
- Slice 5 PR3 -- one-shot /eval + async transitions via jobs.
  POST /api/v1/closedLoop/{loopId}/eval (synchronous decision +
  apply); POST /api/v1/closedLoop/{loopId}/eval/async
  (enqueue + 202 with job id); GET /api/v1/closedLoop/{loopId}/
  jobs/{jobId}. eval_job table; forward heuristic with OODA /
  MAPE / CUSTOM surfaced on the rationale. Audit row fires from
  transition_state so PR1 SSE and PR2 webhooks carry through.
- Slice 4 PR1 -- structured request log + correlation id middleware.
  Every request writes a row to `request_log` (id, ts, method, path,
  status, latency_ms, request_id, principal_id, source_ip, user_agent)
  with an index on `ts DESC`. The `X-Correlation-Id` header propagates
  from client to server; when absent the middleware generates a fresh
  UUID4 and echoes it on the response. New endpoint
  `GET /api/v1/_log/recent` returns the most recent rows (limit 1..1000,
  default 100, cursor-paginated).
- Slice 4 PR2 -- audit log + write hooks on ClosedLoop / Activity /
  Workflow state transitions, Goal updates, ClosedLoopLink create +
  delete, Auth token issue + revoke. Audit rows are written only on
  successful operations; cycle + topology errors do not write audit
  rows (the request log is the diagnostic). Correlation id propagates
  via a per-request ContextVar set by the PR1 middleware. New audit
  columns: id, ts, actor (USER / SYSTEM), action, entity_kind,
  entity_id, before_payload, after_payload, correlation_id. Token
  entity_id is a stable uuid5 of the token id (token ids are URL-safe
  tokens, not UUIDs).
- Slice 4 PR3 -- GET /api/v1/audit (paginated, filterable by
  entityKind / entityId / actor / action / since / until) +
  GET /api/v1/audit/{auditId}. All filters optional, AND-combined.
- Slice 4 PR4 -- split /health into /health/live (trivial 200) and
  /health/ready (200 when DB + token store are up; 503 otherwise).
  New /metrics endpoint exposing Prometheus text-format counters
  (clam_request_total, clam_request_duration_ms_{sum,count},
  clam_audit_total, clam_token_total). New dataset examples
  audit-snapshot.json + request-log-tail.json. Updated
  docs/api/OVERVIEW.md with an observability section.
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
