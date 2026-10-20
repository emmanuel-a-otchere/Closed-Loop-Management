# Closed-Loop-Management: Capability Review and Change Request Roadmap
Repository: 
Review date: 18 October 2026
Review focus: Conceptual completeness, capability coverage, information model, API and tooling, operational architecture, assurance, and governance.
## 1. Executive assessment
The repository has developed beyond its original information-engineering proposal into a more substantial foundation for Closed-Loop Automation Management (CLAM).
The current README identifies a FastAPI service, an OpenAPI 3.1 contract, a defined data model, a closed-loop lifecycle, five supporting toolkits, reference datasets, diagrams, tests, and CI controls. It also distinguishes the management plane from the execution mechanisms that perform the underlying work. 
This is a meaningful foundation. However, there is an important distinction between having tools that represent and manage closed loops and having a sufficiently complete management capability for engineering, validating, operating, governing, and continuously improving them.
My overall assessment is that the repository has a credible management-plane foundation, but its advertised capability needs a more explicit specification of operational semantics, assurance, control boundaries, and evidence.
The principal question is no longer whether CLAM can represent a closed loop and manage its lifecycle. It is whether the model and supporting tools can establish that a loop:
Has a well-defined purpose and measurable outcomes.
Is engineered against explicit requirements and constraints.
Can be validated before deployment.
Operates within its authorised control boundaries.
Produces verified outcomes supported by evidence.
Can be monitored, recovered, and improved safely.
Can coordinate with other loops without compromising system-wide objectives.
Remains traceable and governable throughout its lifecycle.
These should become explicit requirements of the CLAM capability rather than assumptions distributed across documentation and implementation.
### 1.1 Capability scorecard
The following scores are my qualitative assessment of the repository's documented capability, not measured implementation coverage or an audit of every source file.

| Capability area | Assessment | Principal finding |
| --- | --- | --- |
| Conceptual foundation | Strong foundation | The management paradigm and core concepts are established. |
| Closed-loop information model | Foundational | Core entities and relationships exist, but important operational semantics require further specification. |
| Lifecycle management | Foundational | The state machine exists; transition guards, authorisation, recovery, and lifecycle evidence need strengthening. |
| API and machine-readable contracts | Good foundation | OpenAPI 3.1 and a downloadable Postman collection provide a useful interface foundation. |
| Design and modelling | Partial | Model construction is represented, but requirements traceability and formal design verification need clearer treatment. |
| Simulation and testing | Partial | A simulator and KPI calculator exist; their ability to establish behavioural correctness remains to be demonstrated. |
| Runtime observability | Partial | Monitoring is an identified capability, but the available evidence does not establish complete telemetry and event semantics. |
| Safety and assurance | Material gap | The documented model does not yet establish a comprehensive assurance and bounded-control framework. |
| Inter-loop coordination | Foundational | Links between loops are modelled, but system-wide conflict resolution and coordinated behaviour require stronger contracts. |
| Governance and auditability | Partial | Lifecycle and CI controls exist; operational decision provenance, approvals, and evidence management need further definition. |
| Integration and portability | Partial | An API-first structure exists, but interoperability contracts and deployment-independent execution interfaces need strengthening. |
| Maturity assessment | Present, depth unverified | A questionnaire and CSV scoring toolkit exist, but their coverage and scoring validity need to be assessed. |

The strongest documented assets are the explicit lifecycle, the distinction between feedforward and feedback paths, the typed decision-model variants, and the separation between CLAM and the underlying execution logic. 
The weakest areas are not necessarily missing software packages. They are the capabilities and guarantees that must exist across those packages.

# 2. First principle: establish exactly what CLAM is responsible for
Before introducing more tools, I recommend establishing a normative capability boundary.
The repository's conceptual paper explicitly states that CLAM is not a closed-loop runtime. Its API records and manages loop lifecycle information, while execution belongs to underlying activities referenced by the model. It compares this separation to Kubernetes managing pods rather than performing their work. 
This is an important architectural decision that should be preserved.
However, the distinction needs to become more precise.
## 2.1 The three architectural responsibilities
I recommend distinguishing three responsibilities.
### A. Closed-loop engineering
Responsible for defining what a loop is intended to accomplish and determining whether its design is fit for operation.
Capabilities include:
Intent and requirement definition.
Goal and constraint modelling.
Closed-loop design and composition.
Decision-model specification.
Workflow and activity definition.
Resource and dependency specification.
Design verification.
Simulation and scenario analysis.
Acceptance criteria and evidence requirements.
### B. Closed-loop management
Responsible for governing the loop as a managed asset throughout its lifecycle.
Capabilities include:
Registration and discovery.
Configuration and version management.
Validation and approval.
Publication and deployment coordination.
Activation, suspension, resumption, and retirement.
Operational monitoring.
Incident and exception management.
Inter-loop coordination.
Audit and compliance.
Performance and outcome assessment.
### C. Closed-loop execution and control
Responsible for carrying out the decision and control functions that change the operating environment.
Capabilities include:
Observing relevant state.
Interpreting observations.
Evaluating conditions and constraints.
Selecting actions.
Executing actions through authorised mechanisms.
Observing resulting state transitions.
Determining whether the intended outcome was achieved.
Returning feedback to the decision process.
These responsibilities may be implemented by different services, products, or components. They do not necessarily require three separate deployable applications.
The architectural requirement is that their responsibilities and interfaces remain explicit.
## 2.2 The critical distinction: management is not execution
CLAM should not attempt to become another general-purpose workflow engine, orchestration runtime, or AI-agent framework.
Instead, it should define the management contracts under which such systems can participate in a closed loop.
For example, CLAM might manage a loop whose execution is delegated to an existing network controller, an industrial control system, a workflow engine, or an autonomous software agent.
CLAM should be able to establish:
What the loop is authorised to achieve.
Which execution mechanism it uses.
Which actions and resources are within scope.
Which constraints govern execution.
What observations and outcomes must be reported.
What evidence is required to accept an outcome.
What happens when execution violates a constraint or fails to converge.
This preserves implementation neutrality while making the management model useful across different technologies and domains.

# 3. Review of the proposal and information model
The existing data model defines seven principal entities: ClosedLoop, DecisionModel, Goal, Workflow, Activity, ClosedLoopLink, and ClosedLoopState.
It also distinguishes OODA, MAPE, and custom decision models, and gives workflows explicit feedforward or feedback paths. 
These are appropriate starting points, but they do not yet constitute a complete semantic model for managing a closed loop.
## 3.1 Missing or under-specified semantic responsibilities
The following table identifies the principal model enhancements I recommend investigating.

| Area | Existing foundation | Required enhancement |
| --- | --- | --- |
| Intent | Goals with metric targets | Explicit intent, requirements, operational context, priorities, and success conditions. |
| Constraints | Some conditional link logic | First-class constraints, applicability, severity, enforcement, and violation handling. |
| State | Closed-loop lifecycle state | Separation of management lifecycle state, execution state, environmental state, and outcome status. |
| Observation | Feedback activities | Observation definitions, timestamps, provenance, freshness, quality, and uncertainty. |
| Decision | OODA, MAPE, and custom models | Decision inputs, applicable policies, decision outputs, rationale references, and authorisation requirements. |
| Action | Activity with an implementation reference | Typed action contracts, preconditions, postconditions, idempotency, reversibility, and failure semantics. |
| Outcome | Goal and metric targets | Expected outcomes, observed outcomes, acceptance criteria, verification results, and outcome evidence. |
| Capability | Implicitly represented through loop functionality | Explicit capability definitions and the relationship between capability and its realisation. |
| Resources | Activity implementation references | Resource requirements, allocation, availability, ownership, and operational dependencies. |
| Inter-loop relationships | Typed loop links | Input/output contracts, dependency semantics, compatibility, and coordination rules. |
| Policy | Partially represented through the earlier conceptual proposal | Policy identity, version, scope, precedence, enforcement, and traceability. |
| Risk and assurance | Lifecycle and validation concepts | Hazard scenarios, risk thresholds, safety constraints, assurance cases, and approval gates. |
| Versioning | Identifiers and timestamps | Immutable design versions, deployment versions, compatibility rules, and rollback references. |
| Evidence | Simulator traces and KPI reports | A common evidence model linking requirements, decisions, actions, outcomes, and verification. |

These are proposed enhancements, not a claim that every underlying implementation is absent. The current public documentation does not establish all these capabilities or their implementation depth.
## 3.2 Separate lifecycle state from behavioural state
This is one of the most important changes.
The current lifecycle includes:
designed → validated → published → active → paused → error → retired
This provides a useful management state machine. 
But a loop can be active while its operational behaviour is ineffective.
For example:
The loop is active, but its goal is no longer achievable.
The loop is active, but observations are stale.
The loop is active, but its controller is repeatedly retrying a failed action.
The loop is active, but its outcomes violate a business constraint.
The loop is active, but its environment has changed beyond its validated assumptions.
Therefore, CLAM should distinguish at least four state dimensions.

| State dimension | Example states | Purpose |
| --- | --- | --- |
| Management lifecycle | Designed, validated, published, active, retired | Controls the managed asset's lifecycle. |
| Execution condition | Idle, running, blocked, recovering, failed | Describes execution progress and condition. |
| Goal disposition | Not evaluated, progressing, satisfied, violated, unattainable | Describes the relationship between current conditions and the goal. |
| Assurance disposition | Unassessed, accepted, degraded, rejected | Describes whether available evidence supports continued operation. |

These are proposed semantic categories, not final enum definitions.
They should be investigated and formalised through a change request before changing the binding data model.
Important: Do not create one enormous state machine combining all four dimensions. Their interactions should be governed by explicit rules.
For example, stale observations might move a loop into a degraded assurance disposition and trigger a policy-dependent execution response without necessarily changing its management lifecycle state.

# 4. Review of the tools and their completeness
The repository currently advertises five toolkits alongside its service, data model, and schemas:
OAS validator.
Loop simulator.
ERD-to-OAS generator.
Maturity assessment.
KPI calculator.
These are a sensible initial collection. 
The question is whether they form an integrated engineering and management toolchain.
My recommendation is to organise the tools around the lifecycle of a closed loop rather than treat them as independent utilities.
## 4.1 Recommended capability-to-tool mapping

| Lifecycle stage | Existing tool or asset | Enhancement required |
| --- | --- | --- |
| Define | REST service and data model | Requirements and intent modeller, constraints, acceptance criteria, and traceability. |
| Design | Data model, diagrams, reference payloads | Design completeness validator and dependency analysis. |
| Validate | OAS validator | Semantic validation, cross-reference integrity, policy checks, and model conformance. |
| Simulate | Loop simulator | Scenario-driven simulation, environmental changes, fault injection, and convergence testing. |
| Publish | Lifecycle API | Approval gates, immutable release versions, deployment profiles, and publication evidence. |
| Activate | Lifecycle API | Execution adapter contract, operational preconditions, and controlled activation. |
| Operate | REST service and monitoring-related functions | Telemetry ingestion, operational events, health evaluation, and exception handling. |
| Coordinate | Closed-loop links | Inter-loop contract validation, dependency management, and conflict detection. |
| Verify outcomes | KPI calculator | Acceptance-criteria evaluation and evidence-linked outcome verification. |
| Improve | KPI reports and maturity assessment | Controlled redesign proposals, regression testing, and evidence-based improvement. |
| Govern | CI, repository governance, and lifecycle model | Audit trails, approvals, policy enforcement, version lineage, and assurance reporting. |

This table defines a proposed target capability, not a list of features already implemented.
## 4.2 Tool-specific enhancements
### A. OAS validator
Current role: Validate an OpenAPI document against the CLAM profile.
Recommended evolution: Make it a broader CLAM conformance validator while preserving a distinct OAS-validation function.
The tool should eventually validate:
Structural schema correctness.
Required identifiers and references.
Relationship cardinality and integrity.
Valid decision-model configurations.
Workflow path consistency.
Lifecycle transition legality.
Required goals and acceptance criteria.
Constraint completeness.
Inter-loop link consistency.
Model-version compatibility.
Required evidence declarations.
Not every rule belongs in OpenAPI schema validation. Semantic and lifecycle rules should be separate validation stages with explicit, machine-readable results.
Suggested outputs:
schema-validation-report.json
semantic-validation-report.json
lifecycle-validation-report.json
conformance-report.json
This would make validation reproducible and suitable for CI pipelines.
### B. Loop simulator
Current role: Drive an OODA, MAPE, or custom decision cycle against the API and emit a JSONL trace. 
Recommended evolution: Develop it into a scenario-based verification environment.
A simulator should test more than whether a sequence of steps can be performed.
It should evaluate whether the loop behaves correctly when conditions change.
Required scenario categories should include:
Normal operating conditions.
Disturbance and recovery.
Missing or delayed observations.
Invalid or contradictory input.
Failed or repeated actions.
Goal conflicts.
Resource contention.
Constraint violations.
Loss of an upstream or downstream dependency.
Non-convergence.
Recovery after interruption.
The simulator should support deterministic replay, configurable scenario parameters, and comparison of expected and observed outcomes.
It should produce machine-readable evidence that can be consumed by the KPI calculator and assurance tooling.
A critical distinction is needed between simulation of the management lifecycle and simulation of the loop's actual behaviour. The first does not prove the second.
### C. ERD-to-OAS generator
Current role: Read an Excel ERD and emit an OpenAPI schema fragment.
This tool has value as a migration aid, especially because the repository preserves its original 2022 ERD.
However, an ERD is not a complete semantic specification.
The generator should not become the authoritative source of truth if the binding model is already defined through the OpenAPI-backed data model.
Recommended enhancements:
Explicitly define its supported input profile.
Report constructs that cannot be represented faithfully.
Preserve relationship cardinality and constraints where supported.
Validate generated output.
Produce a generation report.
Add round-trip and regression fixtures.
Detect unsupported or lossy transformations.
The target should be a reliable conversion tool, not a second competing modelling authority.
### D. Maturity assessment
Current role: Provide a non-technical questionnaire and CSV scoring template.
This is useful for assessing organisational readiness, but maturity assessment should be tied to a declared capability model.
I recommend separating the assessment into at least five dimensions:
Engineering maturity: Requirements, modelling, design verification, and testing.
Operational maturity: Monitoring, incident handling, recovery, and service management.
Control maturity: Constraints, permissions, bounded actions, and intervention mechanisms.
Assurance maturity: Verification, evidence quality, risk management, and auditability.
Coordination maturity: Inter-loop dependencies, shared resources, and system-wide outcomes.
The assessment should specify:
What each maturity level means.
Which evidence is required to justify a score.
Which capabilities are prerequisites for higher levels.
How scores are aggregated.
Which critical weaknesses cannot be offset by high scores elsewhere.
For example, a high average maturity score should not compensate for the absence of essential control safeguards.
The proposed maturity model should be validated against real use cases before its scores are treated as benchmarks.
### E. KPI calculator
Current role: Consume simulator traces and generate KPI reports.
This tool could become a particularly valuable part of CLAM because it provides a route from simulated behaviour to measurable performance.
The enhancement should establish a common metric definition model, including:
Metric identifier and definition.
Measurement method.
Unit and aggregation period.
Target and threshold.
Source and provenance.
Confidence or data-quality status.
Applicable goal.
Evaluation window.
Acceptance criteria.
The calculator should distinguish three categories:

| Category | Example | What it establishes |
| --- | --- | --- |
| Execution metrics | Action latency, failure rate, retries | How the loop performs operationally. |
| Control effectiveness | Settling time, overshoot, convergence, constraint violations | How effectively the loop controls its target environment. |
| Outcome measures | Availability improvement, cost reduction, target service level | Whether the intended result has been achieved. |

These categories must not be conflated.
A loop can execute successfully while failing to achieve its goal. Equally, a desirable outcome may occur without being attributable to the loop.
The KPI tool should therefore report both measurements and the strength of the evidence supporting outcome attribution.

# 5. The most important architectural enhancement: evidence-based capability realisation
I recommend making this the central organising principle of the next phase of CLAM.
The conceptual relationship should be:
Intent and constraints → control mechanisms → actions and state transitions → verified outcomes → evidence of capability realisation.
This establishes a traceable connection between what a loop is intended to achieve and what it actually achieves.
It also provides a common basis for engineering, runtime management, assurance, and improvement.
## 5.1 Proposed conceptual model
flowchart TD
    I["Intent and Requirements"]
    C["Constraints and Policies"]
    K["Capability Specification"]
    D["Closed-Loop Design"]
    M["Control Mechanisms"]
    A["Actions and State Transitions"]
    O["Observed State"]
    V["Outcome Verification"]
    E["Evidence and Assurance"]
    R["Improvement and Redesign"]

    I --> K
    I --> D
    C --> D
    K --> D
    D --> M
    M --> A
    A --> O
    O --> V
    I --> V
    C --> V
    K --> V
    V --> E
    E --> R
    R --> D
    O --> M
This is a proposed conceptual architecture, not a representation of the repository's current implementation.
The final model should preserve the following distinctions.
Capability: The ability to achieve a specified result under declared conditions.
Control mechanism: The means by which a loop selects or regulates behaviour.
Action: An operation performed by an execution mechanism.
Outcome: A resulting condition or state.
Verified outcome: An outcome shown to satisfy declared acceptance criteria.
Evidence: Information supporting the verification and its conclusions.
These distinctions prevent the system from treating successful API calls, completed workflows, or successful actions as sufficient evidence that a business or operational goal has been achieved.
## 5.2 Introduce explicit traceability relationships
The model should support relationships such as:

| Relationship | Meaning |
| --- | --- |
| satisfies | A requirement or constraint is satisfied by a design or result. |
| realises | A design or mechanism contributes to the realisation of a capability. |
| exhibits | An entity demonstrates a specified behaviour. |
| changes | An action or event changes a state. |
| verifies | An assessment establishes whether a criterion has been met. |
| providesEvidenceFor | An evidence item supports a particular claim. |

These are proposed relationship names that should be reconciled with the canonical semantic foundation before implementation.
Their purpose is to connect the relevant artefacts without forcing every relationship into the ClosedLoop entity.
The resulting traceability chain should allow an engineer or operator to navigate from a declared goal to its requirements, the mechanisms intended to realise it, the actions performed, the resulting state, and the evidence supporting the conclusion.
That would be a significant improvement over a system that can represent the loop but cannot reliably establish whether the loop is delivering its intended capability.

# 6. Introduce bounded autonomy and operational assurance
The existing repository explicitly accommodates automation and identifies AI-enabled closed-loop automation in its historical conceptual model. Its current management-plane framing is broader than any particular decision technology. 
The next step should be to make the degree of autonomy and the associated control boundaries explicit.
This is particularly important if CLAM is intended to support autonomous networks, enterprise operations, industrial systems, or AI-enabled control.
## 6.1 Do not equate autonomy with AI
CLAM should remain technology-neutral.
A closed loop can be autonomous without using AI. Conversely, a loop can use an AI model without having authority to act autonomously.
The model should distinguish:
Whether a decision mechanism uses AI.
Whether actions are automated.
Whether the loop can progress independently.
Which decisions require human approval.
Which actions are prohibited.
Which operating conditions require suspension or intervention.
These characteristics should be modelled independently rather than encoded into one maturity label.
## 6.2 Required control boundaries
I recommend investigating a bounded-control model with explicit support for:
Permitted actions.
Prohibited actions.
Operating envelopes.
Resource and budget limits.
Maximum action rates.
Preconditions for execution.
Escalation conditions.
Human approval requirements.
Emergency suspension.
Recovery and reactivation conditions.
For example, a network loop may be permitted to adjust traffic routing automatically within a declared operating envelope but require approval before making a change that affects a critical service boundary.
CLAM should be able to represent and validate the relevant control requirements without needing to implement the network controller itself.
## 6.3 Assurance must influence lifecycle decisions
Validation should not be a single event that permanently qualifies a loop for operation.
A loop can become unsafe or ineffective when its operating environment changes.
The management model should therefore define which changes require:
Revalidation.
Regression testing.
Reapproval.
Temporary suspension.
Rollback.
Retirement.
These conditions should be explicit, machine-testable, and traceable to the relevant requirements and risks.

# 7. Proposed Change Request programme
I recommend implementing the enhancements through a sequence of bounded CRs.
The order matters: strengthening the tools before clarifying the semantics risks producing several utilities that use different interpretations of the same concepts.
The first CR should establish the capability baseline and the intended architecture. Subsequent CRs should implement the agreed requirements.
The identifiers below are proposed identifiers, not existing repository records.
## Phase 1: Establish the normative capability foundation
### CR-CLAM-001: Closed-Loop Capability Model and Conformance Baseline
Priority: P0
Type: Foundational and normative
Problem
The repository describes the CLAM paradigm, its lifecycle, information model, and tools, but the complete capability scope and the criteria for demonstrating conformance are not yet consolidated into a single normative specification.
Proposed change
Establish a canonical CLAM capability model covering:
Closed-loop engineering.
Lifecycle management.
Execution and control interfaces.
Operational management.
Coordination.
Verification and assurance.
Governance and continuous improvement.
Define the responsibilities and boundaries of each capability.
Create a requirements-to-capabilities matrix that maps each capability to its information model, API operations, tools, evidence, and conformance criteria.
Required deliverables
docs/conceptual/capability-model.md
docs/conceptual/architecture-boundaries.md
docs/conformance/capability-requirements.md
A capability-to-tool traceability matrix.
A documented list of implemented, partial, proposed, and unverified capabilities.
Acceptance criteria
Every normative capability has a defined purpose and scope.
Every capability has explicit requirements and acceptance criteria.
Every existing tool is mapped to the capabilities it supports.
Gaps between documented intent and verified implementation are identifiable.
Execution responsibilities remain distinct from management responsibilities.
Dependency: None. This CR establishes the baseline for the subsequent programme.

### CR-CLAM-002: Closed-Loop Semantic Model and State Separation
Priority: P0
Type: Information-model enhancement
Problem
The current model provides a closed-loop lifecycle state and core relationships, but does not fully specify the semantic distinction between management lifecycle, execution condition, goal disposition, and assurance disposition.
Proposed change
Define the authoritative conceptual model for:
Intent and requirements.
Goals and constraints.
Capabilities and their realisation.
Observations and state transitions.
Decisions and actions.
Outcomes and verification.
Evidence and assurance.
Resource and inter-loop relationships.
Specify state dimensions and their interaction rules before modifying the binding schema.
Required deliverables
Revised conceptual entity model.
Normative relationship definitions.
State and transition specifications.
Cardinality and integrity rules.
Data-model migration strategy.
Backward-compatibility assessment.
Acceptance criteria
Lifecycle state is distinct from runtime condition and outcome status.
Every proposed entity and relationship has an unambiguous definition.
Invalid references and inconsistent relationships are detectable.
The binding model can evolve without silently changing established meanings.
Existing API consumers have a documented migration path.
Dependency: CR-CLAM-001.

### CR-CLAM-003: Intent, Constraints, and Capability Traceability
Priority: P0
Type: Engineering and semantic traceability
Problem
The model represents goals and decision mechanisms, but the repository does not yet establish a complete, machine-verifiable chain from requirements and constraints to demonstrated capability.
Proposed change
Introduce a traceability model connecting:
Intent → Requirements → Constraints → Design → Actions → Outcomes → Evidence
Define the relationship between a closed loop and the capabilities it is intended to realise.
Required deliverables
Traceability specification.
Machine-readable relationship definitions.
Example traceability graph.
Completeness and consistency rules.
Validation report format.
Acceptance criteria
Every in-scope capability has declared realisation requirements.
Applicable constraints are traceable to the relevant design and verification criteria.
Outcome verification can be linked to the goals it evaluates.
Evidence can be traced to the claims it supports.
Missing or broken traceability links are reported automatically.
Dependency: CR-CLAM-002.

## Phase 2: Strengthen engineering and validation
### CR-CLAM-004: CLAM Conformance and Design Validation Toolkit
Priority: P1
Type: Tool enhancement
Problem
The OAS validator provides a foundation for contract validation, but structural schema validity alone cannot establish that a closed-loop design is semantically complete or operationally admissible.
Proposed change
Expand validation into distinct stages:
Schema validation.
Reference and relationship validation.
Semantic validation.
Lifecycle validation.
Requirements and constraint completeness.
Inter-loop compatibility.
Release-readiness validation.
Required deliverables
Reusable validation rules.
Machine-readable validation reports.
Positive and negative test fixtures.
CI integration.
Documented severity and failure policies.
Acceptance criteria
Invalid models fail validation for the appropriate reasons.
Validation results identify the failing artefact and rule.
Equivalent inputs produce deterministic results.
Validation stages can be invoked independently.
Release-readiness rules are explicit and testable.
Dependency: CR-CLAM-002 and CR-CLAM-003.

### CR-CLAM-005: Scenario-Based Simulation and Behavioural Verification
Priority: P1
Type: Tool enhancement
Problem
A simulator that successfully drives decision cycles does not necessarily establish that a loop achieves its goals or remains within its operational constraints.
Proposed change
Extend the simulator to support declared scenarios, expected behaviours, fault injection, deterministic replay, and outcome verification.
Required deliverables
Scenario definition format.
Scenario execution and replay.
Fault-injection support.
Expected-versus-observed outcome comparison.
Convergence and recovery measurements.
Simulation evidence report.
Acceptance criteria
A scenario specifies its initial conditions, disturbances, expected outcomes, and acceptance criteria.
The simulator records relevant actions, observations, and state transitions.
Failed acceptance criteria produce explicit verification failures.
Regression scenarios can be executed in CI.
Simulation results can be consumed by the KPI and assurance tools.
Dependency: CR-CLAM-003 and CR-CLAM-004.

### CR-CLAM-006: Evidence and Outcome Verification Framework
Priority: P1
Type: Cross-cutting capability
Problem
The repository has simulator traces and KPI reports, but these need a common evidence contract if they are to support verification, operational decisions, and auditability consistently.
Proposed change
Define a common evidence model linking:
Requirements.
Goals.
Constraints.
Decisions.
Actions.
Observed state.
Verification results.
Operational metrics.
Capability realisation claims.
Required deliverables
Evidence schema.
Outcome verification contract.
Evidence provenance rules.
Evidence integrity and retention requirements.
Example end-to-end evidence record.
Acceptance criteria
Evidence has a stable identity and provenance.
Evidence identifies the claim or criterion it supports.
Verification distinguishes success, failure, and insufficient evidence.
Results can be reproduced or independently inspected to the extent supported by the evidence.
Evidence remains associated with the relevant design and deployment versions.
Dependency: CR-CLAM-003 and CR-CLAM-005.

## Phase 3: Strengthen operations and coordination
### CR-CLAM-007: Runtime Governance and Bounded Autonomy
Priority: P1
Type: Operational safety and governance
Problem
A lifecycle API does not by itself establish the conditions under which a running loop may act, recover, or continue operating.
Proposed change
Define the management contracts for operating envelopes, action permissions, constraint enforcement, intervention, and recovery.
Required deliverables
Bounded-autonomy specification.
Operational precondition and postcondition rules.
Policy and authorisation requirements.
Suspension and recovery criteria.
Revalidation and reapproval triggers.
Acceptance criteria
Every governed action is subject to explicitly defined permissions and constraints.
Violations have specified responses.
Recovery cannot bypass required validation or authorisation.
AI usage and autonomy level are represented as distinct characteristics.
Human intervention requirements are machine-readable where applicable.
Dependency: CR-CLAM-002, CR-CLAM-003, and CR-CLAM-006.

### CR-CLAM-008: Inter-Loop Coordination and Conflict Management
Priority: P1
Type: Architecture and operational management
Problem
The existing model can represent relationships between loops, but a relationship alone does not establish that connected loops are compatible or that their combined behaviour is safe and effective.
Proposed change
Specify inter-loop contracts for:
Input and output compatibility.
Dependency ordering.
Shared-resource allocation.
Conflicting goals.
Conflicting actions.
Failure propagation.
Coordination and escalation.
System-wide outcome verification.
Required deliverables
Inter-loop relationship semantics.
Compatibility rules.
Conflict-detection requirements.
Coordination scenarios.
System-level verification criteria.
Acceptance criteria
Incompatible links can be identified before publication.
Resource and goal conflicts have defined resolution policies.
Failures can be traced across dependent loops.
Coordination decisions are auditable.
System-wide outcomes can be evaluated independently of individual loop status.
Dependency: CR-CLAM-002, CR-CLAM-005, and CR-CLAM-007.

### CR-CLAM-009: Operational Observability and Recovery
Priority: P2
Type: Operational tooling
Problem
The current documentation identifies monitoring and reporting as management capabilities, but does not establish a complete operational telemetry and recovery contract.
Proposed change
Define a common event, telemetry, and health model for operational closed loops.
Required deliverables
Event and telemetry specifications.
Health and degraded-condition definitions.
Operational alert requirements.
Failure classification.
Recovery and restart rules.
Operational history and audit requirements.
Acceptance criteria
Relevant lifecycle and operational events are recorded.
Telemetry can be associated with the applicable loop and deployment version.
Stale or missing observations can be distinguished from healthy operation.
Recovery actions follow declared policies.
Operators can reconstruct the relevant sequence of events for an incident.
Dependency: CR-CLAM-006 and CR-CLAM-007.

## Phase 4: Establish continuous improvement and maturity
### CR-CLAM-010: Evidence-Based Maturity and Improvement
Priority: P2
Type: Assessment and improvement
Problem
The maturity-assessment toolkit offers an initial mechanism for assessment, but a maturity score becomes more useful when linked to specific capabilities, objective evidence, and remediation priorities.
Proposed change
Establish a capability-based maturity model with explicit scoring criteria, evidence requirements, prerequisites, and improvement recommendations.
Required deliverables
Maturity dimension definitions.
Level definitions and prerequisites.
Evidence-based scoring rules.
Assessment report schema.
Capability-gap analysis.
Remediation mapping.
Acceptance criteria
Every maturity score has a documented basis.
Critical control weaknesses cannot be obscured by aggregate scores.
Assessment results map to specific capability gaps.
Improvement recommendations map to governed CRs or other approved changes.
Assessments can be repeated and compared consistently.
Dependency: CR-CLAM-001, CR-CLAM-006, and CR-CLAM-007.

# 8. Recommended implementation sequence
I would not implement all ten CRs concurrently.
The following sequence minimises rework by establishing the semantic contracts before extending the tools.

| Order | CR | Principal outcome | Priority |
| --- | --- | --- | --- |
| 1 | CR-CLAM-001 | Normative capability model and baseline | P0 |
| 2 | CR-CLAM-002 | Semantic model and state separation | P0 |
| 3 | CR-CLAM-003 | Intent-to-evidence traceability | P0 |
| 4 | CR-CLAM-004 | Design and conformance validation | P1 |
| 5 | CR-CLAM-005 | Scenario-based behavioural verification | P1 |
| 6 | CR-CLAM-006 | Common evidence and outcome verification | P1 |
| 7 | CR-CLAM-007 | Bounded autonomy and runtime governance | P1 |
| 8 | CR-CLAM-008 | Inter-loop coordination | P1 |
| 9 | CR-CLAM-009 | Operational observability and recovery | P2 |
| 10 | CR-CLAM-010 | Evidence-based maturity and improvement | P2 |

Important sequencing qualification: CR-CLAM-007 should establish the required governance semantics before any production-oriented autonomous execution adapter is authorised. The sequence does not imply that an unrestricted execution runtime should be built.
## What should happen before implementation?
CR-CLAM-001 should begin with a focused repository reconnaissance.
The investigation should verify:
Which capabilities are implemented in source code.
Which are documented but not implemented.
Which are implemented but inadequately tested.
Which are represented only by examples or reference artefacts.
Which require changes to the binding data model.
Which can be delivered through existing tools.
This prevents the programme from creating duplicate implementations or adding abstractions that are not justified by actual gaps.

# 9. Repository-level enhancements
The CR programme should be supported by a more explicit repository structure.
The current README already identifies separate directories for the service, schemas, toolkits, datasets, documentation, tests, and governance. 
I would preserve that structure and make its authority boundaries clearer.
A possible target is:
Closed-Loop-Management/
│
├── docs/
│   ├── conceptual/
│   │   ├── paradigm.md
│   │   ├── capability-model.md
│   │   ├── architecture-boundaries.md
│   │   └── semantic-model.md
│   │
│   ├── architecture/
│   │   ├── reference-architecture.md
│   │   ├── control-boundaries.md
│   │   └── inter-loop-coordination.md
│   │
│   ├── conformance/
│   │   ├── capability-requirements.md
│   │   ├── validation-rules.md
│   │   └── evidence-requirements.md
│   │
│   └── assurance/
│       ├── verification-model.md
│       └── operational-assurance.md
│
├── schemas/
│   ├── data-model/
│   ├── openapi/
│   ├── evidence/
│   ├── scenarios/
│   └── policies/
│
├── machines/
│   ├── service/
│   ├── scripts/
│   └── toolkits/
│
├── datasets/
│   ├── examples/
│   ├── scenarios/
│   └── conformance/
│
├── tests/
│   ├── unit/
│   ├── contract/
│   ├── semantic/
│   ├── lifecycle/
│   ├── simulation/
│   └── conformance/
│
├── governance/
│   ├── ADR/
│   ├── CR/
│   └── decisions/
│
└── CHANGELOG.md
This is a proposed target structure, not a requirement to create every directory immediately.
The governing principle should be that each artefact has one clearly identified authority.
For example:
The normative capability model defines what CLAM must support.
The semantic model defines what its concepts and relationships mean.
The OpenAPI contract defines the API representation.
The conformance rules define what constitutes a valid model.
The implementation provides the actual behaviour.
The tests and evidence establish which requirements have been demonstrated.
Avoid allowing the README, a diagram, the OpenAPI schema, and the source code to become competing definitions of the same capability.
## Additional repository controls
I recommend adding the following controls through the appropriate CRs:
Requirement traceability: Every normative requirement has a stable identifier.
Conformance tests: Every machine-testable requirement has a corresponding test.
Contract compatibility: Changes to the OpenAPI contract trigger compatibility checks.
Semantic consistency: Changes to the data model trigger relationship and reference validation.
Evidence validation: Evidence records are checked against their declared schemas.
Decision governance: Material architectural changes require an approved ADR where appropriate.
Change governance: Each CR specifies scope, dependencies, acceptance criteria, and verification evidence.
Release governance: A release records the applicable model, API, and conformance versions.
The result should be a repository in which changes are evaluated against an explicit capability model rather than primarily through documentation review or successful unit tests.

# 10. Two strategic decisions to settle before expanding the scope
There are two decisions I would make explicit in the first phase.
## Decision A: Is CLAM a management specification, a reference implementation, or both?
The repository currently presents a paradigm expressed through a service, data model, schemas, and supporting toolkits. It also explicitly states that CLAM is not the execution runtime. 
I recommend treating CLAM as a normative management model with a reference implementation and supporting engineering toolchain.
This means the conceptual model and conformance requirements should remain authoritative even if the service implementation changes.
It also allows alternative implementations to support the same CLAM contracts without having to use the repository's specific Python service.
The reference implementation should demonstrate the model, not define the limits of the model.
## Decision B: What constitutes successful closed-loop operation?
This question deserves explicit treatment because it determines how the simulator, KPI calculator, assurance model, and operational controller fit together.
I recommend defining success in terms of verified outcomes against declared intent and constraints.
A loop should not be considered successful merely because:
Its lifecycle state is active.
Its API request succeeded.
Its workflow completed.
Its action returned successfully.
A KPI improved in isolation.
Instead, the system should determine whether the relevant acceptance criteria were satisfied under the applicable constraints and whether sufficient evidence exists to support that conclusion.
The outcome may be:
Satisfied: The required outcome has been verified.
Not satisfied: Available evidence demonstrates that the criteria were not met.
Indeterminate: Available evidence is insufficient to establish either conclusion.
The exact terminology should be formalised through CR-CLAM-002 and CR-CLAM-006.
This is essential if CLAM is to support both ordinary automation and consequential autonomous operations.

# 11. Recommended first CR: ready-to-adapt proposal
I would start with the following change request rather than immediately changing the data model or implementing additional tooling.
## CR-CLAM-001: Establish the Normative CLAM Capability Model and Conformance Baseline
Status: Proposed
Priority: P0
Change class: Foundational
Scope: Closed-Loop-Management repository
### 11.1 Problem statement
The repository has established a conceptual closed-loop management paradigm and provides a REST service, binding information model, lifecycle state machine, and supporting engineering tools.
However, the complete normative capability scope is not yet consolidated into a single specification that establishes the relationship between intended capabilities, their supporting artefacts, and the evidence required to demonstrate conformance.
This creates a risk that individual tools and implementation components evolve without a consistent definition of the capabilities they are expected to realise.
### 11.2 Objective
Establish a normative CLAM capability model that defines the scope, responsibilities, requirements, and conformance expectations of closed-loop management.
The model shall provide the foundation for subsequent changes to the semantic model, API, validation toolkit, simulator, evidence framework, and operational governance.
### 11.3 Scope
The CR shall:
Identify the complete set of CLAM management capabilities.
Define the boundary between management and execution.
Map existing entities, API operations, tools, and documentation to those capabilities.
Identify implemented, partial, proposed, and unverified requirements.
Define stable identifiers for normative requirements.
Establish a capability-to-artefact traceability matrix.
Identify semantic and architectural decisions requiring separate ADRs.
Define the acceptance criteria for subsequent capability-enhancement CRs.
### 11.4 Out of scope
This CR shall not:
Implement a new execution runtime.
Introduce a specific AI or agent framework.
Replace the existing API or data model.
Mandate a particular simulation engine.
Introduce new canonical concepts without the required semantic review.
Treat unverified implementation claims as demonstrated capabilities.
### 11.5 Deliverables
The change shall produce:
A normative capability model.
An architecture-boundary specification.
A capability inventory and gap analysis.
A capability-to-tool traceability matrix.
A list of required semantic and architectural decisions.
A prioritised, dependency-ordered follow-on CR backlog.
### 11.6 Acceptance criteria
The CR is complete when:
Every in-scope capability has a defined purpose and boundary.
Existing tools and artefacts have been mapped to the capabilities they support.
Implementation status is supported by repository evidence.
Identified gaps have explicit requirements and acceptance criteria.
Management and execution responsibilities are unambiguous.
No proposed change silently alters the meaning of an existing binding concept.
Follow-on CRs have explicit dependencies and measurable completion criteria.
### 11.7 Dependencies
None.
### 11.8 Verification
Verification shall include a review of the repository's current source, schemas, tests, documentation, and CI configuration.
The final deliverables shall distinguish demonstrated behaviour from documented intent and proposed future capability.

# 12. Final recommendation
The repository has a useful foundation: it treats closed loops as managed assets, makes lifecycle transitions explicit, separates feedback from feedforward, and provides a machine-readable API and supporting toolkits.
The next phase should not be driven primarily by adding more tools.
It should be driven by establishing the semantic and operational contracts that make those tools collectively trustworthy.
I recommend three immediate priorities:
First: establish the normative capability model. Determine what CLAM must support, what it currently supports, and what evidence demonstrates that support.
Second: formalise the semantic model and traceability chain. Connect intent, constraints, capability, control mechanisms, actions, outcomes, and evidence without conflating their meanings.
Third: strengthen verification and operational governance. Ensure that the tools can test behaviour against declared expectations and that runtime management can respond appropriately when constraints, goals, or environmental assumptions are violated.
The intended progression is:
Managed closed-loop representation → Governed lifecycle → Verifiable behaviour → Evidence-based assurance → Coordinated autonomous operation.
That progression would strengthen CLAM as a reusable, technology-neutral management foundation for closed loops across enterprise operations, autonomous networks, and other adaptive systems.
It would also provide a coherent basis for the later introduction of higher-autonomy capabilities without making AI a prerequisite for the underlying architecture.
