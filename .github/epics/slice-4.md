# Epic -- Slice 4: Runtime + Auth + Multi-tenant

**Milestone:** v1.1.0 Features
**Issue:** #4 (file after Slice 3 lands)
**Cards (Kanban):** see http://192.168.50.160:7000/board/14

## Goal

Make CLAM production-shaped. Authentication, multi-tenant isolation, a
pluggable backend (Postgres via SQLAlchemy, in addition to SQLite), a
runtime that actually executes the closed loop decision model, and the
condition engine that evaluates CEL expressions on ClosedLoopLinks.

## Acceptance criteria

- [ ] OAuth2 / OIDC bearer-token auth on every `/api/v1/*` endpoint.
- [ ] Tenant id extracted from token; queries scoped per tenant.
- [ ] Pluggable backend interface; SQLite and Postgres implementations.
- [ ] Decision-model executor (OODA / MAPE / CUSTOM) that consumes the
      referenced activities and emits state transitions.
- [ ] CEL engine for ClosedLoopLink condition evaluation.
- [ ] Dockerfile + compose for local stack.
- [ ] Deployment guide under `docs/deploy/`.
- [ ] 25+ new pytest tests (auth, tenant isolation, runtime).