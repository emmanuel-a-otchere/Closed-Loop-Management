# Changelog

All notable changes to the CLAM REST API are documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/) and this project
adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Slice 2 PR1 -- Activity / Workflow / Goal / ClosedLoopLink CRUD with their
  own IDs, lifecycles, and resource-scoped links.
- Slice 2 PR2 -- Cross-resource lifecycle constraints
  (workflow-publish-with-unpublished-activities, retire-activity-still-in-use,
  delete-blocked-by-reference). New GET /closedLoop/{id}/goalRollup endpoint
  aggregating goal achievement across CLOSED_LOOP / WORKFLOW / ACTIVITY scopes.
- Slice 2 PR3 -- ClosedLoopLink cycle detection (single + bulk), topology
  view, BFS path query, downstream/upstream neighbour endpoints.

## [0.1.0] -- 2026-10-10

### Added
- Slice 1 -- repo revamp, FastAPI skeleton, OAS 3.1 data model, ClosedLoop +
  DecisionModel CRUD, ClosedLoop state transitions, error envelope, pagination,
  downloadable examples, GitHub Project + Kanban board, CI lint + test gates.
