# Closed-Loop-Management

REST API and OAS 3.1 data model for **Closed Loop Automation Management (CLAM)**.

> This repo began in 2022 as an information-engineering exercise around managing
> closed loops. The legacy 2022 conceptual model and ERD are preserved at
> [`docs/data-model/legacy-2022-erd.xlsx`](docs/data-model/legacy-2022-erd.xlsx)
> and in the original README history. Slice 1 (current) promotes that model into
> a typed, served REST API that conforms to OAS 3.1.

## What CLAM is

CLAM is the management plane for closed loops running inside a closed-loop
automation platform. A *closed loop* is a set of workflows with a control
point, feedback path, and a goal. The API lets you:

- CRUD a **decision model** (OODA, MAPE, or custom).
- CRUD **feedback and feedforward activities** and the **workflows** they compose.
- Set a **goal or target** for constituent parts of a closed loop.
- **Activate or deactivate** a closed loop and read its state.
- **Daisy-chain or hierarchically interlink** closed loops so that one loop
  can consume the outputs of another.

The data model is described in detail under [`docs/data-model/`](docs/data-model/).
The API surface is described in detail under [`docs/api/`](docs/api/).

## Quick start (downloadable and testable)

Requires Python 3.12.

```bash
git clone https://github.com/emmanuel-a-otchere/Closed-Loop-Management.git
cd Closed-Loop-Management
pip install -e .
uvicorn clam.main:app --reload --port 8000
```

Then open:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- Raw OpenAPI 3.1: <http://localhost:8000/openapi.json>

A runnable Postman collection is generated at `docs/examples/postman-collection.json`
and cURL examples are in [`docs/api/EXAMPLES.md`](docs/api/EXAMPLES.md).

## Repository layout

```
api/clam/              # FastAPI application (the service itself)
  main.py              # app entry, router wiring, OpenAPI metadata
  models.py            # Pydantic v2 models (the OAS source-of-truth)
  store.py             # SQLite-backed store (aiosqlite)
  routers/
    closed_loop.py     # /closedLoop CRUD + state endpoints
    decision_model.py  # /decisionModel CRUD
docs/
  data-model/
    legacy-2022-erd.xlsx        # Original 2022 conceptual ERD (preserved)
    clam-data-model-1.0.md      # OAS-backed entities (binding form)
  api/
    OVERVIEW.md                 # Tour of the API surface
    EXAMPLES.md                 # Copy-paste cURL examples
openapi/
  openapi.json                   # Snapshot of generated OAS (CI artifact)
.github/
  ISSUE_TEMPLATE/               # Issue templates
  workflows/                     # CI: pytest + OAS lint + Spectral
  epics/                         # WBS epic specs (one per slice phase)
context/
  AGENT-DOCTRINE.md              # Channel-binding governance doc
examples/
  closed-loop-oooda.json        # Sample closed loop (OODA decision model)
  decision-model-mape.json      # Sample decision model (MAPE)
scripts/
  seed_db.py                     # Populate SQLite with examples
pyproject.toml                   # Project + dependency manifest
```

## Repository governance

| Area | Where it lives |
| --- | --- |
| Project board | https://github.com/users/emmanuel-a-otchere/projects/14 |
| Kanban board | http://192.168.50.160:7000/board/14 (discord-closed-loop-automation) |
| Card doctrine | `context/AGENT-DOCTRINE.md` |
| WBS epics | `.github/epics/` (one file per phase) |
| Milestones | GitHub milestones `v1.0.0 MVP` ... `v2.0.0 Architecture` |

## Development

```bash
pytest                    # run the test suite
pytest --cov=clam         # with coverage
ruff check api/           # linter
mypy api/                 # type-checker
```

CI runs the same set on every push (see `.github/workflows/ci.yml`).

## Lineage

The 2022 README + ERD define a comprehensive conceptual model: closed loop
design studio, closed loop manager, closed loop controller, with sub-functions
for design, validation, publication, catalog, monitoring, orchestration,
administration, and choreography. That conceptual model is the foundation;
this repo layers a typed, served, OAS-backed API on top of it.

The original README content from 2022-2023 is retained verbatim in the git
history (commit `be64beb`). The current README is the v1.0 framing.

## License

Apache 2.0. Copyright 2022-2026 Emmanuel A. Otchere.
See [LICENSE](LICENSE).