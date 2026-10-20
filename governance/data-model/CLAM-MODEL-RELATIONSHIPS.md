# CLAM Enriched Model: Relationship View

**Status:** Conceptual proposal; not a binding schema.

```mermaid
flowchart TD
    I[Intent] --> R[Requirement]
    I --> G[Goal]
    R --> C[Constraint]
    R --> A[Acceptance Criterion]
    C --> D[Closed-Loop Design]
    G --> D
    D --> L[ClosedLoop]
    L --> DM[Decision Model]
    L --> W[Workflow]
    W --> AC[Activity Definition]
    L --> P[Policy / Operating Envelope]
    L --> DEP[Deployment or Configuration Version]
    L <--> LINK[Typed Inter-Loop Link]
    LINK <--> L2[Related ClosedLoop]

    DM --> DEC[Decision Record]
    AC --> AX[Action Execution Record]
    OBS[Observation / Measurement] --> DEC
    DEC --> AX
    AX --> OUT[Outcome]
    OUT --> VR[Verification Result]
    A --> VR
    C --> VR
    G --> VR
    VR --> E[Evidence Record]
    OBS --> E
    DEC --> E
    AX --> E
    DEP --> E
    E --> HA[Assurance / Health Assessment]
    HA --> IMP[Improvement Proposal]
    IMP --> D
```

## Interpretation

- `Activity` describes work; `ActionExecution` records an execution instance. They are not interchangeable.
- `Goal` declares a target; `Outcome` records a resulting condition; `VerificationResult` states whether a criterion is met.
- `EvidenceRecord` supports a claim or result but does not itself guarantee truth or sufficiency.
- `ClosedLoopState` remains lifecycle state. Operational health, execution condition, goal disposition, and assurance disposition are separate dimensions.
- `Policy` and `Constraint` declarations do not automatically enforce themselves. The enforcement point and evidence of enforcement must be identified.
- Inter-loop links require typed contracts and compatibility rules, not merely source/target identifiers.
