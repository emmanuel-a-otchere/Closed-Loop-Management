CR-CLAM-001: Establish the Normative Closed-Loop Management Capability Model

Attribute	Value

CR ID	CR-CLAM-001
Title	Establish the Normative Closed-Loop Management Capability Model
Repository	emmanuel-a-otchere/Closed-Loop-Management
Change type	Foundational / Normative
Priority	P0
Status	Proposed
Scope	Capability specification, architecture boundaries, conformance, and repository governance
Dependencies	None
Implementation approach	Investigation and specification first; implementation changes require subsequent CRs

Change summary

Establish a normative capability model for Closed-Loop Automation Management (CLAM) that defines its purpose, scope, responsibilities, architectural boundaries, and conformance requirements.

The model shall establish a traceable relationship between the capabilities CLAM is intended to provide, the information model and interfaces that support those capabilities, the tools that implement or validate them, and the evidence required to demonstrate that they work as specified.

This change establishes the authoritative foundation for subsequent enhancements to the CLAM information model, API, engineering toolkits, simulation capabilities, operational governance, and assurance framework.

This CR establishes what CLAM must be capable of doing and how that capability is demonstrated. It does not implement the subsequent enhancements.

Problem statement

The Closed-Loop-Management repository establishes a conceptual paradigm for managing closed-loop automation. It provides a REST API, an OpenAPI contract, a data model, lifecycle states, supporting toolkits, reference artefacts, and automated tests.

These components provide a useful foundation. However, their collective scope is not yet governed by a single normative capability specification that establishes:

The complete set of capabilities within CLAM’s responsibility.

The distinction between closed-loop engineering, management, and execution.

The relationship between capabilities, semantic concepts, API operations, and tools.

The requirements that determine whether a capability is complete.

The evidence required to establish implementation conformance.

The boundaries between implemented, partially implemented, proposed, and unverified functionality.

The dependencies and governance requirements for evolving the capability.

Without this specification, individual components risk evolving independently, creating inconsistencies between the conceptual paradigm, the information model, API behaviour, engineering tools, and operational expectations.

A tool may exist without adequately supporting the intended capability. An API may accept a valid payload without establishing that the underlying closed-loop design is semantically complete. A simulator may execute a decision cycle without demonstrating that the loop achieves its intended outcome.

CLAM therefore requires an explicit capability model and a corresponding conformance baseline.

Motivation and architectural rationale

The primary motivation is to establish capability completeness and conformance as governed properties of CLAM, rather than assumptions inferred from the existence of its components.

The repository should evolve around a normative specification that remains authoritative independently of the particular implementation technology.

This requires three architectural principles.

Capability before implementation

Every normative capability must have a defined purpose, scope, requirements, dependencies, and acceptance criteria before implementation changes are proposed.

Existing implementations must be assessed against these requirements rather than automatically treated as the complete definition of the capability.

Management distinct from execution

CLAM shall define the management contracts for closed loops without assuming responsibility for the execution mechanisms that perform their underlying work.

CLAM may specify how execution mechanisms are referenced, governed, validated, monitored, and assessed. It shall not be assumed to implement those mechanisms itself.

3.3 Evidence before conformance claims

A capability shall not be classified as fully implemented merely because it is described in documentation, represented in a schema, or exposed through an API.

Implementation claims must be supported by appropriate repository evidence, such as source code, contract tests, behavioural tests, conformance tests, or demonstrated end-to-end behaviour.

Where sufficient evidence is unavailable, the implementation status must remain explicitly unverified.

Proposed change

Establish the CLAM Normative Capability Model as the authoritative specification for the capabilities and responsibilities of Closed-Loop Automation Management.

The model shall define the following capability domains.

Capability domain A: Closed-Loop Engineering

Purpose: Define and validate a closed-loop design against its intended purpose and operating requirements.

The specification shall determine the requirements for:

Intent and requirement definition.

Goal and constraint specification.

Closed-loop design and configuration.

Decision-model definition.

Workflow and activity modelling.

Dependency and resource specification.

Design completeness and consistency.

Simulation and pre-deployment verification.

Acceptance criteria.

This domain establishes whether a proposed loop has a sufficiently complete and consistent design to proceed through the management lifecycle.

It does not require CLAM to implement a general-purpose design environment or simulation engine.

Capability domain B: Closed-Loop Lifecycle Management

Purpose: Manage closed loops as governed assets throughout their lifecycle.

The specification shall determine the requirements for:

Registration and identification.

Configuration and version management.

Lifecycle-state management.

Validation and approval.

Publication.

Activation and suspension.

Resumption and recovery.

Retirement.

Lifecycle transition validation.

Release and deployment traceability.

Lifecycle management shall remain distinct from the execution state of a loop and from the status of its intended outcomes.

4.3 Capability domain C: Execution Integration and Control Boundaries

Purpose: Establish the contracts under which external execution mechanisms participate in a managed closed loop.

The specification shall determine the requirements for:

Execution-mechanism identification.

Execution interface contracts.

Input and output expectations.

Preconditions and postconditions.

Action permissions and constraints.

Execution status reporting.

Failure and exception reporting.

Human intervention requirements.

Execution provenance.

CLAM shall remain implementation-neutral regarding the technology used to perform the work.

The capability model shall distinguish the management of execution from the execution itself.

Capability domain D: Operational Management

Purpose: Establish how a managed closed loop is assessed and governed during operation.

The specification shall determine the requirements for:

Operational status and health.

Relevant observations and telemetry.

Goal-progress assessment.

Constraint-violation detection.

Exception and incident management.

Degraded-operation handling.

Recovery and revalidation.

Operational history.

Performance assessment.

The model shall not equate an active lifecycle state with successful or healthy operation.

4.5 Capability domain E: Inter-Loop Coordination

Purpose: Govern relationships and dependencies between multiple closed loops.

The specification shall determine the requirements for:

Inter-loop relationship semantics.

Input and output compatibility.

Dependency validation.

Shared-resource considerations.

Conflicting goals and actions.

Failure propagation.

Coordination and escalation.

System-level outcome assessment.

The specification shall distinguish the existence of a relationship from the compatibility and safe operation of the connected loops.

Capability domain F: Verification and Assurance

Purpose: Establish whether a closed-loop design and its observed behaviour satisfy declared requirements and constraints.

The specification shall determine the requirements for:

Design conformance.

Behavioural verification.

Scenario-based testing.

Outcome verification.

Evidence provenance.

Evidence integrity.

Verification results and their interpretation.

Assurance status.

Revalidation triggers.

The model shall distinguish successful execution from verified outcome achievement.

It shall also distinguish a demonstrated failure from a conclusion that cannot be established because the available evidence is insufficient.

4.7 Capability domain G: Governance and Continuous Improvement

Purpose: Govern the evolution of closed loops and the CLAM capability itself.

The specification shall determine the requirements for:

Policy and approval governance.

Version and change traceability.

Auditability.

Conformance reporting.

Capability maturity assessment.

Evidence-based improvement.

Regression verification.

Change impact assessment.

Compatibility management.

Improvements to a loop or to CLAM itself shall remain subject to the applicable change-governance requirements.

Important qualification

These seven domains are the proposed initial capability taxonomy for investigation and formalisation.

Their inclusion in this CR does not establish that every domain is already fully implemented, nor does it pre-empt the investigation of whether some domains should be merged, separated, or refined.

The resulting normative model must be justified by the repository’s existing architecture, intended use cases, and identified capability gaps.

Architectural boundaries

The CR shall explicitly establish the following responsibility boundaries.

Concern	CLAM responsibility	Boundary

Closed-loop design	Define and manage design artefacts and their conformance requirements.	Does not require a particular design application.
Decision models	Represent and validate supported decision-model configurations.	Does not mandate a specific decision engine.
Workflow management	Define and manage workflow references, relationships, and relevant lifecycle contracts.	Does not require CLAM to execute the workflow.
Runtime execution	Define integration and governance contracts.	Execution remains with the designated execution mechanism.
Operational monitoring	Define management requirements for status, observations, and exceptions.	Does not require CLAM to replace domain-specific monitoring systems.
Simulation	Define scenario and verification requirements where applicable.	Does not mandate a particular simulation engine.
Outcome verification	Define acceptance criteria and evidence requirements.	Verification must be supported by appropriate evidence.
Autonomy governance	Define the management requirements for permissions, constraints, intervention, and recovery.	Does not imply unrestricted autonomous execution.
Improvement	Govern changes and assess their effect on declared capabilities.	Does not permit unverified changes to bypass required controls.

These boundaries shall be reflected consistently in the capability model, architecture documentation, and conformance requirements.

Capability-to-implementation traceability

The CR shall introduce a normative traceability approach connecting the capability model to the repository’s implementation.

Every normative capability requirement shall have a stable identifier.

The identifiers should follow a consistent scheme, provisionally:

CLAM-CAP-<DOMAIN>-<NUMBER>

For example:

CLAM-CAP-LCM-001: A managed closed loop shall have a uniquely identifiable lifecycle record.

CLAM-CAP-ENG-001: A closed-loop design shall be assessable against its declared requirements.

CLAM-CAP-VER-001: A verification result shall identify the criterion being evaluated.

CLAM-CAP-OPS-001: Operational status shall be distinguishable from verified goal achievement.

These are illustrative identifiers, not final normative requirements. The actual identifiers and wording shall be established during implementation of this CR.

Each requirement shall be mapped to the following:

Traceability element	Required information

Requirement	Stable identifier and normative statement.
Capability	The capability domain and function it establishes.
Semantic concepts	Relevant entities, relationships, and constraints.
API or interface	Applicable endpoint, contract, or external interface.
Implementation	Source files or components responsible for satisfying the requirement.
Verification	Test, inspection, or demonstration used to verify the requirement.
Evidence	Results supporting the conformance claim.
Status	Implemented, partially implemented, proposed, or unverified.
Dependencies	Other requirements or capabilities that must be satisfied first.

Not every requirement will map to an API operation. Some may be satisfied by repository governance, architectural constraints, documentation, or external execution contracts.

The traceability model shall accommodate these differences.

Repository changes

The CR shall make the minimum repository changes necessary to establish the normative baseline.

The proposed artefacts are:

Docs/
├── conceptual/
│   ├── capability-model.md
│   └── architecture-boundaries.md
│
└── conformance/
    ├── capability-requirements.md
    └── capability-traceability.md

capability-model.md

Defines the normative capability domains, their purpose, scope, responsibilities, and relationships.

architecture-boundaries.md

Defines the boundaries between engineering, management, execution, operational control, and external systems.

capability-requirements.md

Defines the requirements derived from the capability model, including stable identifiers, normative statements, and acceptance criteria.

capability-traceability.md

Maps requirements to existing implementation artefacts, verification methods, evidence, and follow-on CRs.

These paths are proposed. The implementation may adapt them to the repository’s existing conventions, provided that the normative responsibilities remain clear.

Existing documentation shall be updated where necessary to reference the new authoritative artefacts. The CR shall not unnecessarily duplicate or replace existing conceptual material.

Implementation procedure

This CR shall be completed in four controlled stages.

Stage 1: Repository reconnaissance

Inspect the existing:

README and conceptual documentation.

Data model and OpenAPI contract.

API implementation.

Toolkits.

Schemas and reference datasets.

Tests and CI workflows.

Existing CRs, ADRs, and governance artefacts.

Record the relevant implementation evidence and identify discrepancies between documented capabilities and demonstrated behaviour.

Output: Repository capability inventory.

Stage 2: Capability analysis

Assess the existing capabilities against the seven proposed domains.

Identify:

Capabilities already implemented and verified.

Capabilities partially implemented.

Capabilities documented but not demonstrated.

Capabilities requiring new semantic concepts.

Capabilities requiring changes to existing interfaces.

Capabilities that belong to external execution mechanisms.

Gaps that do not require additional implementation.

Output: Capability gap analysis.

Stage 3: Normative specification

Develop the capability model, architectural boundaries, requirement catalogue, and traceability matrix.

Resolve ambiguities in the proposed taxonomy and identify architectural decisions requiring separate ADRs.

Output: Normative capability baseline.

Stage 4: Review and acceptance

Review the specification for:

Completeness.

Internal consistency.

Clear management/execution boundaries.

Traceability.

Testability.

Compatibility with the existing repository.

Clear dependencies for follow-on CRs.

Obtain the required review and approval under the repository’s established governance process.

Output: Accepted CR-CLAM-001 and an implementation-ready follow-on backlog.

Acceptance criteria

CR-CLAM-001 shall be considered complete only when all the following criteria are satisfied.

ID	Acceptance criterion	Verification

AC-001	The normative CLAM capability model is documented and reviewed.	Documentation review.
AC-002	Every capability domain has an explicit purpose, scope, and responsibility boundary.	Capability-model inspection.
AC-003	Management and execution responsibilities are unambiguously distinguished.	Architecture-boundary review.
AC-004	Existing repository components are mapped to their supported capabilities.	Traceability-matrix inspection.
AC-005	Capability implementation status is supported by repository evidence.	Source, test, and contract inspection.
AC-006	Partial, proposed, and unverified capabilities are explicitly identified.	Gap-analysis review.
AC-007	Normative requirements have stable identifiers and testable acceptance criteria.	Requirements review.
AC-008	Each requirement identifies an applicable verification method.	Traceability review.
AC-009	Required semantic and architectural decisions are recorded for governance.	ADR and decision review.
AC-010	Follow-on CRs have defined scope, dependencies, and acceptance criteria.	CR backlog review.
AC-011	Existing binding contracts are not changed without explicit authorisation.	Change-scope inspection.
AC-012	Existing documentation references the normative capability baseline where applicable.	Documentation review.

No API, schema, lifecycle, or runtime changes are required merely to satisfy this CR. Such changes must be proposed and approved separately where necessary.

Out of scope

The following are explicitly excluded from CR-CLAM-001:

Replacing the existing information model.

Introducing a new execution runtime.

Implementing AI agents or a specific AI framework.

Introducing a new simulation engine.

Rewriting the REST API.

Changing the existing lifecycle state machine.

Mandating a particular telemetry or observability platform.

Implementing a new policy engine.

Establishing production safety certification.

Implementing all identified capability gaps.

These subjects may become subsequent CRs once the normative baseline establishes their requirements and dependencies.

Dependencies and follow-on changes

CR-CLAM-001 has no dependencies.

Its outputs should inform the following proposed changes:

Proposed CR	Subject	Dependency on CR-CLAM-001

CR-CLAM-002	Semantic model and state separation	Establishes the capabilities and requirements that the model must support.
CR-CLAM-003	Intent, constraints, and capability traceability	Establishes the normative requirements and traceability approach.
CR-CLAM-004	Conformance and design validation	Establishes which capabilities and requirements must be validated.
CR-CLAM-005	Scenario-based simulation	Establishes behavioural verification requirements.
CR-CLAM-006	Evidence and outcome verification	Establishes the evidence and conformance requirements.
CR-CLAM-007	Runtime governance and bounded autonomy	Establishes the management and execution boundaries.
CR-CLAM-008	Inter-loop coordination	Establishes the scope of coordination and system-level capabilities.
CR-CLAM-009	Operational observability and recovery	Establishes operational management requirements.
CR-CLAM-010	Evidence-based maturity and improvement	Establishes the capability taxonomy against which maturity is assessed.

This is an initial dependency map. The reconnaissance stage may identify additional dependencies or justify a different implementation order.

Risks and mitigations

Risk	Mitigation

The capability taxonomy becomes too broad.	Keep CLAM focused on management contracts and avoid absorbing execution-engine responsibilities.
Existing documentation is duplicated.	Identify authoritative artefacts and update references instead of creating competing definitions.
Requirements become too abstract to test.	Require explicit acceptance criteria and a verification method for every normative requirement.
Existing implementation is incorrectly classified as complete.	Require source-level, contract-level, or behavioural evidence.
The CR triggers premature implementation changes.	Restrict scope to reconnaissance, specification, and governance.
New concepts conflict with the existing semantic model.	Record unresolved semantic decisions and resolve them before binding-model changes.
Follow-on CRs overlap.	Use the capability-to-requirement traceability matrix to define scope and dependencies.

Expected outcome

Upon acceptance, the repository will have an authoritative answer to four questions:

What must CLAM be capable of doing?

Which responsibilities belong to CLAM, and which belong to external execution mechanisms?

How do its information model, API, and tools support those capabilities?

What evidence demonstrates that each capability has been implemented and verified?

This baseline will provide the basis for strengthening the repository without introducing unnecessary components or prematurely changing existing contracts.

Recommendation

Approve CR-CLAM-001 as a specification-first, foundational change.

The immediate implementation should be limited to repository reconnaissance, capability analysis, normative documentation, and traceability.

The first substantive engineering change should follow only after the resulting baseline identifies and prioritises the actual gaps.

That sequence gives subsequent CRs a stable architectural foundation and makes the evolution of Closed-Loop Management measurable, reviewable, and governed.