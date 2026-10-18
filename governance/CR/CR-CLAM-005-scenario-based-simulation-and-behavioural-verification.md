---
cr_id: CR-CLAM-005
title: Scenario-Based Simulation and Behavioural Verification
status: Proposed
priority: P1
type: Tool enhancement
repository: emmanuel-a-otchere/Closed-Loop-Management
dependencies: [CR-CLAM-003, CR-CLAM-004]
source_review: CR-CLAM-000 (Section 7, CR-CLAM-005)

---

# CR-CLAM-005: Scenario-Based Simulation and Behavioural Verification

## Change summary

Extend the loop simulator into a scenario-based verification environment with deterministic replay, fault injection, scenario definitions, expected-vs-observed comparison, and machine-readable evidence output.

## Problem statement

A simulator that successfully drives decision cycles does not necessarily establish that a loop achieves its goals or remains within its operational constraints. The current simulator can replay a happy path; the missing piece is negative-path verification.

## Motivation and rationale

Required scenario categories include normal conditions, disturbance and recovery, missing/delayed observations, invalid/contradictory input, failed/repeated actions, goal conflicts, resource contention, constraint violations, dependency loss, non-convergence, and recovery after interruption. Only structured scenario definitions enable regression testing in CI.

## Proposed change

Add scenario execution to the simulator:

- **Scenario definition format** -- a typed YAML/JSON describing initial conditions, disturbances, expected outcomes, acceptance criteria.
- **Replay** -- deterministic execution with a pinned RNG seed and timestamps; replay reproduces observed state exactly.
- **Fault injection** -- declare faults at named injection points (observation delay, action failure, dependency loss).
- **Comparison engine** -- compares expected vs observed action sequences, observed states, and goal progression.
- **Evidence output** -- emits per-scenario evidence records consumable by CR-CLAM-006.

Critical distinction: simulation of the management lifecycle (state machine) is not the same as simulation of the loop's actual behaviour. Scenarios must target both.

## Repository changes (deliverables)

- `machines/toolkits/loop-simulator/scenario.md (scenario definition spec)`
- `machines/toolkits/loop-simulator/replay.py`
- `machines/toolkits/loop-simulator/fault-injection.py`
- `datasets/scenarios/ (positive and negative fixtures with ground truth)`
- `Regression scenarios wired into `.github/workflows/conformance.yml``

## Acceptance criteria

1. A scenario specifies initial conditions, disturbances, expected outcomes, and acceptance criteria.
2. The simulator records relevant actions, observations, and state transitions.
3. Failed acceptance criteria produce explicit verification failures with stable identifiers.
4. Regression scenarios execute in CI on every PR.
5. Simulation evidence is consumable by the KPI calculator and assurance tooling.

## Out of scope

- Production traffic replay against live systems.
- Vendor-specific simulation engines (the toolkit remains technology-neutral).

## Dependencies

- Depends on: CR-CLAM-003, CR-CLAM-004

## Follow-on relationship

- CR-CLAM-006 (evidence framework) consumes the simulation evidence.
- CR-CLAM-008 (inter-loop coordination) defines coordination scenarios.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Scenarios become stale as the model evolves. | Each scenario carries an explicit model-version pin; CI rejects scenarios older than the pinned version. |
| Non-determinism undermines replay value. | All time and randomness pass through a scenario-controlled clock and RNG; sources of environmental drift must be injected or stubbed. |

## Source

This CR is a harvest of the canonical proposal in
[`governance/reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md`](../../reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md),
Section 7, CR-CLAM-005. The full prose, including its tables and rationale, is
preserved verbatim in that file.
