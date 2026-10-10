# CLAM State Machine

The closed-loop state machine governs the lifecycle of a single closed
loop instance. Transitions are explicit and API-controlled.

```mermaid
stateDiagram-v2
    [*] --> designed
    designed --> validated : POST /state
    validated --> published : POST /state
    published --> active : POST /state
    active --> paused : POST /state
    active --> error : POST /state
    paused --> active : POST /state
    paused --> retired : POST /state
    error --> active : POST /state
    error --> retired : POST /state
    designed --> retired : POST /state
    validated --> retired : POST /state
    published --> retired : POST /state
    retired --> [*]
```

Source: `docs/diagrams/src/state-machine.mmd`.