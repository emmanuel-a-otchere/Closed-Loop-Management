# Epic -- Slice 5: Architecture (REST Hooks + Webhooks + Observability)

**Milestone:** v2.0.0 Architecture
**Issue:** #5 (file after Slice 4 lands)
**Cards (Kanban):** see http://192.168.50.160:7000/board/14

## Goal

Expose CLAM events to the outside world. Outbound webhooks on closed-loop
state transitions, inbound REST hooks for activity completion, Prometheus
metrics, and a tracing shim (OpenTelemetry).

## Acceptance criteria

- [ ] `POST/GET/DELETE /api/v1/webhook` (subscriber CRUD).
- [ ] Outbound webhook fires on every `ClosedLoop.state` transition.
- [ ] Inbound REST hook endpoint for activity completion.
- [ ] `/metrics` Prometheus endpoint.
- [ ] OpenTelemetry tracing on every request.
- [ ] 15+ new pytest tests (webhook delivery, signature verification,
      metrics scraping).