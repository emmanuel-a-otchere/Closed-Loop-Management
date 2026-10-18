# CLAM Data Model Enrichment Proposal

**Status:** Proposed for investigation and review  
**Applies to:** CR-CLAM-002 through CR-CLAM-010  
**Binding status:** None of the proposed extensions in this document are binding until accepted through the relevant CR and contract/model governance.

## 1. Why enrich the model?

The current binding CLAM 1.0 model contains `ClosedLoop`, `DecisionModel`, `Goal`, `Workflow`, `Activity`, `ClosedLoopLink`, and `ClosedLoopState`. It is intentionally compact and is backed by the repository's OpenAPI contract and Pydantic models.

The next iteration should enrich the semantics without turning every operational concern into a separate resource. The model must make it possible to trace intent to requirements, constraints, design, execution references, observations, outcomes, verification, and evidence. It must also distinguish lifecycle from runtime condition and from whether a goal has been achieved.

## 2. Modelling principles

1. **Meaning before representation.** Agree on definitions and relationships before editing the binding OpenAPI schema or Pydantic classes.
2. **One concept, one authoritative meaning.** Do not duplicate `Goal`, `Activity`, or lifecycle concepts under new names.
3. **Separate semantic concepts from API resources.** A concept may be an embedded value object, a referenced resource, an event, or an external-system reference.
4. **Separate state dimensions.** Lifecycle, execution condition, goal disposition, and assurance disposition are related but not interchangeable.
5. **Traceability is a first-class relationship.** Requirements, constraints, outcomes, verification results, and evidence must be linkable.
6. **Version and provenance matter.** Records should identify the model/configuration version and source/time context relevant to interpretation.
7. **Do not infer success.** Successful execution does not prove outcome achievement; absent evidence must not become a positive verification.
8. **Keep execution external by default.** CLAM governs interfaces and evidence; it does not become an execution engine by implication.
9. **Backward compatibility is deliberate.** Additive, optional changes are preferred in compatible releases; breaking semantic changes require explicit versioning and migration.
10. **Minimise entity proliferation.** Introduce a standalone entity only when identity, lifecycle, reuse, access, or query requirements justify it.

## 3. Existing concepts to preserve and clarify

| Existing concept | Clarification/enrichment to investigate |
|---|---|
| `ClosedLoop` | Managed asset identity, description, intent reference, design/configuration version, applicable requirements and constraints, decision-model reference, workflows, links, lifecycle status, and status history. |
| `DecisionModel` | Pattern/type and version; references to activities or external decision mechanisms; declared inputs/outputs and required assumptions where justified. |
| `Goal` | Target metric, unit, direction, evaluation window, scope, threshold/tolerance, applicability, and verification criteria. Preserve existing fields through compatible evolution. |
| `Workflow` | Path/role, ordered activities, dependencies, declared inputs/outputs, and execution contract reference where needed. |
| `Activity` | Implementation reference, typed input/output contract, preconditions/postconditions, failure semantics, idempotency/reversibility declarations where applicable. Do not make an activity record itself an execution log. |
| `ClosedLoopLink` | Semantic relationship type, source/target, contract/version compatibility, dependency semantics, exchanged information references, and failure/coordination policy references. |
| `ClosedLoopState` | Keep lifecycle semantics explicit; do not overload it with health, execution, goal, or assurance status. |

## 4. Candidate model concepts

These are candidates for review, not a mandate to create every entity as an independent API resource.

| Candidate concept | Purpose | Likely modelling form | Introduced/assessed by |
|---|---|---|---|
| `Intent` | Declares the intended change/result and operating context. | Referenced resource or structured value, depending on reuse and lifecycle. | CR-003 |
| `Requirement` | Normative, testable obligation derived from intent or governance. | Versioned resource/value with stable ID. | CR-003 |
| `Constraint` | Defines a boundary or condition that applicable designs/actions must respect. | Versioned resource/value; may reference a policy. | CR-003, CR-007 |
| `Assumption` | Declares a condition on which design/verification relies. | Versioned value or resource with validation/review status. | CR-003 |
| `CapabilitySpecification` / `CapabilityClaim` | States the ability a loop is intended to realise and the claim being assessed. | Reuse existing canonical capability semantics if available; avoid local redefinition. | CR-003 |
| `Observation` | Represents an observed state/signal with time, source, quality, and context. | Event/measurement record or external reference. | CR-006, CR-009 |
| `DecisionRecord` | Records a decision instance or decision outcome and its relevant references. | Event/record; reasoning details only where needed and permitted. | CR-006, CR-007 |
| `ActionExecution` | Records an attempted action and its result, distinct from an `Activity` definition. | Execution event/record, usually emitted by external execution. | CR-006, CR-007, CR-009 |
| `Outcome` | Represents a resulting condition evaluated against a goal or criterion. | Result record linked to subject and evaluation window. | CR-006 |
| `VerificationResult` | Records evaluation of a requirement/criterion. | Versioned result with disposition, method, evidence references. | CR-006 |
| `EvidenceRecord` | Identifies an evidence item, provenance, integrity metadata, and claims supported. | Reusable record/schema; source payload may be external. | CR-006 |
| `Policy` | Declares an applicable rule/permission and its governance metadata. | Versioned resource/reference; enforcement may be external. | CR-007 |
| `Deployment` or `ConfigurationVersion` | Binds operation/evidence to a released configuration. | Versioned release record/reference. | CR-002, CR-006, CR-007 |
| `OperationalEvent` | Records a lifecycle/health/incident/recovery-relevant occurrence. | Append-oriented event record. | CR-009 |
| `HealthAssessment` | Summarises condition at a point/window using declared criteria. | Derived assessment record, not a lifecycle state. | CR-009 |
| `Scenario` | Declares initial conditions, disturbances, expectations, and acceptance criteria. | Versioned simulation/test artefact. | CR-005 |
| `CoordinationContract` | Defines interaction expectations for linked loops. | Versioned contract/reference, potentially attached to a link. | CR-008 |
| `ImprovementProposal` | Links assessed gaps to controlled change proposals. | Governance artefact/reference; avoid duplicating the CR system. | CR-010 |

### Decision gate

For every candidate, decide:
- Is it a distinct concept or an attribute of an existing concept?
- Does it require a stable independent identity?
- Is it reused across loops or versions?
- Does it have its own lifecycle or audit requirements?
- Is it managed by CLAM or owned by an external system?
- Does it need an API resource, or only a schema/value object/reference?

Record the disposition and rationale.

## 5. State separation

Do not create a single combined state enum. Use distinct state dimensions with documented rules.

| Dimension | Illustrative values | Meaning |
|---|---|---|
| Management lifecycle | `designed`, `validated`, `published`, `active`, `paused`, `error`, `retired` | Existing lifecycle, subject to current contract review. |
| Execution condition | `idle`, `running`, `blocked`, `recovering`, `failed`, `unknown` | Execution progress/condition, generally reported by an execution mechanism. |
| Goal disposition | `not_evaluated`, `progressing`, `satisfied`, `not_satisfied`, `unattainable`, `indeterminate` | Evaluation against goal criteria. |
| Assurance disposition | `unassessed`, `accepted`, `degraded`, `rejected`, `indeterminate` | Whether declared evidence/criteria support continued operation. |
| Observation quality | `valid`, `stale`, `missing`, `invalid`, `uncertain` | Quality/freshness of an observation, not a loop state. |

These values are illustrative. The final vocabulary, transition rules, and authority for setting each value must be accepted in CR-002 and related CRs.

## 6. Core relationships to define

| Relationship | Intended meaning | Validation concern |
|---|---|---|
| `hasGoal` | Loop has a goal. | Goal identity and scope. |
| `derivedFrom` | Requirement/intent is derived from another authoritative artefact. | Version/provenance. |
| `constrainedBy` | Design, action, or loop is subject to a constraint/policy. | Applicability and precedence. |
| `realises` | Design/mechanism contributes to a capability claim. | Claim scope and verification basis. |
| `dependsOn` | Loop/component requires another component or condition. | Cycles, availability, version compatibility. |
| `observes` | Observation concerns a subject/metric/state. | Source, time, quality. |
| `changes` | Action/event changes a state or subject. | Before/after semantics and attribution. |
| `evaluates` | Verification evaluates a criterion or goal. | Method, window, disposition. |
| `providesEvidenceFor` | Evidence supports a claim or result. | Provenance and integrity. |
| `linksTo` | A typed inter-loop relationship exists. | Direction, contract, compatibility. |
| `supersedes` | A version replaces an earlier version. | No history loss; explicit effective time. |

The final relationship vocabulary must be reconciled with repository conventions and any canonical semantic foundation used by the project.

## 7. Proposed common record metadata

Where appropriate, versioned or evidentiary records should carry a consistent subset of:

- `id`: stable identifier.
- `type` or `kind`: explicit record type where polymorphism requires it.
- `schemaVersion`: version of the record schema.
- `createdAt` / `recordedAt`: record creation/ingestion time.
- `observedAt` / `effectiveAt`: domain time, when applicable.
- `sourceRef`: source component/system or evidence origin.
- `subjectRef`: entity the record concerns.
- `modelVersion` / `configurationRef`: applicable design/configuration version.
- `correlationId`: trace or incident correlation where applicable.
- `provenance`: derivation/source references.
- `status` or `disposition`: only where semantically appropriate.

Do not add all fields to every object mechanically. Define a shared pattern only where it improves consistency and does not create misleading defaults.

## 8. Recommended model layering

1. **Conceptual model:** definitions, relationships, invariants, state semantics.
2. **Binding information model:** normative entity/value-object shapes and constraints.
3. **API contract:** resource operations and wire representations.
4. **Persistence mapping:** storage and indexes.
5. **Runtime contracts:** events, telemetry, execution and policy interfaces.
6. **Conformance artefacts:** schemas, rules, fixtures, tests, and reports.

The layers should be traceable but need not have identical structures. An API resource is not automatically a canonical concept, and a database table is not automatically an entity in the conceptual model.

## 9. Proposed model evolution

- **CLAM 1.0:** current binding model; preserve as the compatibility baseline.
- **CLAM 1.x compatible enrichment:** additive optional metadata and new schemas only when proven backward compatible and approved.
- **CLAM 2.0 candidate:** semantic changes that alter required fields, relationship meaning, state interpretation, or API contract compatibility.

This is a planning convention, not a pre-approved version commitment. A formal version decision must follow impact analysis and governance.

## 10. Minimum review questions

Before binding schema changes are approved:
1. Which current fields already carry the intended meaning?
2. Which candidate concepts are genuinely new?
3. Which records are authoritative, and which are derived?
4. Which facts are asserted by CLAM versus reported by an external execution system?
5. What is the event time versus ingestion time?
6. How are model and policy versions bound to decisions and evidence?
7. How will old payloads and traces be interpreted?
8. Which validations are structural, semantic, behavioural, or operational?
9. Which evidence is required before a lifecycle transition?
10. Which unresolved issues require an ADR rather than a CR implementation detail?
