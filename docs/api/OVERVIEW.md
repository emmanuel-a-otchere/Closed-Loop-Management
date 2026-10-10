# CLAM API Overview

This document is a tour of the CLAM REST API. The authoritative contract
is the **OpenAPI 3.1** document served at `/openapi.json`; this file is the
human-readable companion.

## Base URL

```
http://localhost:8000
```

Production deployments are configured per-environment via `CLAM_BASE_URL`.

## Versioning

The API is versioned in the URL: `/api/v1/...`. Breaking changes require a
new major version; non-breaking additions ship under the current version.

## Resource roots

| Path | Slice | Description |
| --- | --- | --- |
| `/health` | 1 | Liveness probe. Returns 200 with `{"status":"ok"}`. |
| `/openapi.json` | 1 | The OAS 3.1 document, generated from Pydantic models. |
| `/docs` | 1 | Swagger UI rendered from the OAS. |
| `/redoc` | 1 | ReDoc rendered from the OAS. |
| `/api/v1/closedLoop` | 1 | CRUD over closed loops. |
| `/api/v1/closedLoop/{id}/state` | 1 | State transitions (activate, pause, retire, etc). |
| `/api/v1/decisionModel` | 1 | CRUD over decision models (OODA / MAPE / CUSTOM). |
| `/api/v1/closedLoop/{id}/goal` | 2 | CRUD over goals attached to a closed loop. |
| `/api/v1/closedLoop/{id}/workflow` | 2 | CRUD over workflows in a closed loop. |
| `/api/v1/closedLoop/{id}/workflow/{wid}/activity` | 2 | CRUD over activities in a workflow. |
| `/api/v1/closedLoop/{id}/link` | 3 | CRUD over closed-loop interlinks (daisy-chain, hierarchical). |

## Pagination

List endpoints return a paginated envelope:

```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "pageSize": 20
}
```

Query parameters: `?page=1&pageSize=20`. `pageSize` capped at 100.

## Error envelope

All error responses share the same shape:

```json
{
  "code": "closed_loop.not_found",
  "message": "ClosedLoop with id 7b6c... was not found",
  "details": {}
}
```

`code` is a stable, machine-readable identifier; `message` is a human-readable
string. `details` is an optional object with field-level errors for 422
responses.

## Authentication

Slice 1 ships without authentication. The HTTP server is local-only by
default. Production deployments MUST add an authentication layer (Slice 4).

## Idempotency

POST endpoints accept an optional `Idempotency-Key` header. Repeating a
request with the same key returns the original response.

## Versioning the OAS

The OAS document is generated from Pydantic models at runtime. The CI
pipeline lints it with `spectral` and validates it against the
[OAS 3.1 schema](https://github.com/OAI/OpenAPI-Specification/blob/main/schemas/v3.1/schema.yaml).
The linted output is committed to `openapi/openapi.json` as a snapshot.