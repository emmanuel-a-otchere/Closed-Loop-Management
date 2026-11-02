---
artifact_id: architecture-boundaries-1.0
cr_id: CR-CLAM-001
stage: 3 (Normative specification)
status: Complete (draft for Stage 3 review)
prepared: 2026-10-20
normative: true
inputs:
  - governance/reviews/2026-10-18-CR-CLAM-001-normative-capability-model.md (canonical boundaries table)
  - governance/ADR/ADR-CLAM-0001-clam-scope-spec-plus-reference-impl.md
---

# CLAM Architecture Boundaries

## 1. Purpose

Establish, normatively, the responsibility boundaries between
CLAM and everything else. These boundaries satisfy AC-003
(management and execution responsibilities are unambiguously
distinguished) and are reflected consistently in the capability
model, the requirements catalogue, and the conformance rules.

## 2. Boundary table

| # | Concern | CLAM responsibility | Boundary (what CLAM must not do) |
| --- | --- | --- | --- |
| B-01 | Closed-loop design | Define and manage design artefacts and their conformance requirements | Not require or mandate a particular design application |
| B-02 | Decision models | Represent and validate supported decision-model configurations (OODA / MAPE / CUSTOM) | Not mandate or implement a specific decision engine |
| B-03 | Workflow management | Define and manage workflow references, relationships, and lifecycle contracts | Not execute the workflow |
| B-04 | Runtime execution | Define integration and governance contracts for execution mechanisms | Execution remains with the designated external mechanism; no code under `machines/runtime/` without a prior ADR |
| B-05 | Operational monitoring | Define management requirements for status, observations, and exceptions | Not replace domain-specific monitoring or telemetry systems |
| B-06 | Simulation | Define scenario and verification requirements | Not mandate a particular simulation engine |
| B-07 | Outcome verification | Define acceptance criteria and evidence requirements | Verification claims without appropriate evidence are non-conformant |
| B-08 | Autonomy governance | Define management requirements for permissions, constraints, intervention, and recovery | Not imply unrestricted autonomous execution; enforcement responsibility is declared, external by default |
| B-09 | Improvement | Govern changes and assess their effect on declared capabilities | Not permit unverified changes to bypass required controls |

## 3. The load-bearing distinction

The single boundary from which all others derive is **B-04**:
CLAM manages; execution mechanisms execute. Concretely, in this
repository:

- The API surface (`machines/service/clam/`) only records,
  governs, links, and observes. No route performs loop work.
- Activities reference execution mechanisms by kind and
  contract; the work itself is external.
- Toolkits simulate, project, validate, and report; they drive
  the management API, never a runtime.
- Any future adapter that executes must arrive via a CR with an
  ADR and an explicit Slice-6 (CR-CLAM-007) governance
  authorisation, per the standing sequencing rule.

## 4. Boundary conformance

A change is boundary-conformant when:

1. It does not add execution responsibility to the service,
   store, or toolkits.
2. It does not couple a binding-model change to a conceptual
   one (meaning precedes representation; compatibility review
   is separate).
3. New external-facing contracts cite the boundary table row
   they operate under.

Boundary violations are review blockers in the CR process and
should be flagged against the relevant B-NN row.
