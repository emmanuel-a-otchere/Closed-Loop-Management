# CLAM Change Request Package: CR-CLAM-002-010

**Repository target:** `emmanuel-a-otchere/Closed-Loop-Management`  
**Package status:** Proposed change set; not merged or applied to the target repository  
**Prepared:** 18 October 2026

## Purpose

This package contains proposed CR-CLAM-002 through CR-CLAM-010 and a coordinated proposal for enriching the underlying CLAM data model. It is intended for review and adaptation into the repository's established governance conventions.

The package is deliberately specification-first. It does not replace the current binding OpenAPI contract, mutate the existing `clam-data-model-1.0.md`, or claim that the proposed concepts and schemas are already implemented.

## Contents

- `governance/CR/CR-CLAM-002.md` through `CR-CLAM-010.md`: individual change requests.
- `docs/data-model/CLAM-DATA-MODEL-ENRICHMENT-PROPOSAL.md`: cross-cutting semantic and information-model proposal.
- `docs/data-model/CLAM-MODEL-RELATIONSHIPS.md`: conceptual relationships and Mermaid diagram.
- `docs/data-model/MIGRATION-AND-COMPATIBILITY.md`: versioning and migration principles.
- `schemas/proposals/evidence-record.schema.json`: proposed evidence record schema.
- `schemas/proposals/scenario.schema.json`: proposed simulation scenario schema.
- `schemas/proposals/policy.schema.json`: proposed policy/constraint schema.
- `datasets/proposals/evidence-record.example.json`: illustrative evidence record.
- `datasets/proposals/scenario.example.json`: illustrative scenario.
- `datasets/proposals/policy.example.json`: illustrative policy.
- `traceability/CR-requirements.csv`: proposed requirement-to-CR mapping.
- `MANIFEST.json`: package inventory and status.

## Recommended application sequence

1. Review this package alongside CR-CLAM-001 and the current repository source.
2. Reconcile proposed concepts with existing Pydantic models, OpenAPI schemas, lifecycle rules, and toolkit behaviour.
3. Accept/revise CRs under the repository's governance process.
4. Implement the normative model and compatibility decisions before generating binding schemas.
5. Deliver binding-model/API changes in separately reviewed implementation CRs where scope requires them.

## Important modelling rule

The model proposal identifies candidate concepts and relationships for investigation. It is not a mandate to create a separate API resource for every candidate. The implementation should prefer a small, coherent canonical model, explicit semantics, and stable relationships over unnecessary entity proliferation.

## Current repository baseline considered

The public README describes a FastAPI service, an OAS 3.1 contract, the binding `schemas/data-model/clam-data-model-1.0.md`, lifecycle states, and toolkits for OAS validation, loop simulation, ERD-to-OAS conversion, maturity assessment, and KPI calculation. The existing binding model includes `ClosedLoop`, `DecisionModel`, `Goal`, `Workflow`, `Activity`, `ClosedLoopLink`, and `ClosedLoopState`.

This package treats those as the baseline to be verified during implementation, not as a guarantee that every documented behaviour is fully tested.
