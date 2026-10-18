# CLAM Data Model Migration and Compatibility Principles

**Status:** Proposed principles for CR review.

## 1. Baseline

Treat the current `clam-data-model-1.0.md`, OpenAPI 3.1 contract, Pydantic models, existing persisted records, reference payloads, and tests as the compatibility baseline. Confirm the exact current state during reconnaissance.

## 2. Change classification

Classify each model change before implementation:

- **Additive-compatible:** new optional property or new independent schema that does not alter interpretation of existing data.
- **Conditionally compatible:** field extension or enum addition that may affect strict clients, validators, generated SDKs, or exhaustive switches.
- **Breaking:** removal/rename, changed meaning, changed cardinality, newly required field, changed state transition, or altered interpretation of existing values.
- **Semantic-only:** clarifies meaning without wire change; still requires documentation and conformance review if behaviour is affected.

Do not assume an additive JSON property is compatible with every generated client or strict validator.

## 3. Required migration artefacts

Any binding-model change must identify:
- source and target model/API versions;
- affected entities, fields, relationships, and persisted records;
- defaulting rules, if any, and why they are semantically safe;
- migration/adapter logic;
- rollback or recovery approach;
- deprecation and removal policy;
- regression fixtures and compatibility tests;
- traceability from change request to implementation and tests.

## 4. Preserve meaning and history

Do not silently rewrite historical evidence to fit a new schema. Use explicit version metadata and, where necessary, a documented adapter or migration record. Preserve the original source/provenance for evidence records where retention policy permits.

## 5. Avoid speculative binding changes

The candidate concepts in `CLAM-DATA-MODEL-ENRICHMENT-PROPOSAL.md` must pass a concept disposition review before becoming binding. Do not generate production OpenAPI/Pydantic changes solely from this proposal.

## 6. Release gates

A model/API release should not be considered ready until:
- contract validation passes;
- current and new fixtures pass;
- migration behaviour is tested;
- API compatibility is assessed;
- docs and examples agree with the binding contract;
- the traceability matrix identifies the implemented requirements and their evidence.
