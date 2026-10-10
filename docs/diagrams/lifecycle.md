# CLAM Lifecycle

The closed-loop lifecycle has three high-level phases: **Strategy to
Capability**, **Lifecycle Management**, and **Operations Management**.

```mermaid
flowchart LR
    S[Strategy] -->|design| C[Capability Readiness]
    C -->|validate + publish| L[Lifecycle Mgmt]
    L -->|activate| O[Operations Mgmt]
    O -->|deactivate / retire| L
    L -->|redesign| S

    classDef phase fill:#1F6FEB,stroke:#0E4DAF,color:#fff
    class S,C,L,O phase
```

Source: `docs/diagrams/src/lifecycle.mmd`.