---
adr_id: ADR-CLAM-0001
title: CLAM is a normative management model with a reference implementation and supporting engineering toolchain
status: Proposed (pending Section 10 Decision A)
date: 2026-10-18
source_review: CR-CLAM-000 (Section 10, Decision A)
decides: CLAM scope (spec vs impl vs both)
---

# ADR-CLAM-0001: CLAM scope -- normative specification with reference implementation

## Status

Proposed. Lands as **Accepted** only when this decision is ratified
through the governance review required by CR-CLAM-001 (Stage 4) and
the resulting update to this ADR carries a recorded acceptance date.

## Context

The repository currently presents a paradigm expressed through a
service, data model, schemas, and supporting toolkits while
explicitly stating that CLAM is not the execution runtime. The
CR-CLAM-000 capability review identifies this as the most
important strategic decision to settle before expanding the scope:
the conceptual position of CLAM determines what counts as a
conforming implementation, what counts as an API contract change,
and what authority the OpenAPI document holds relative to the
service code.

Three positions are credible:

1. **Management specification only.** CLAM is a normative document;
   the implementation in this repository is one reference build.
2. **Reference implementation only.** CLAM is what this service and
   data model do; deviations from the implementation are deviations
   from CLAM.
3. **Both: normative management model + reference implementation +
   supporting engineering toolchain.** The conceptual model and
   conformance requirements remain authoritative even if the
   reference implementation changes; alternative implementations
   can support the same CLAM contracts without using this
   repository's specific Python service.

## Decision

Adopt position **3**.

Concretely:

- The conceptual model (entity types, relationships, lifecycle
  transitions, conformance rules) is normative and authoritative.
- The OpenAPI 3.1 document served at `/openapi.json` is the binding
  contract for the reference implementation.
- The reference implementation must demonstrate the model, not
  define the limits of the model.
- Alternative implementations are admissible as long as they pass
  the CLAM conformance toolkit (see CR-CLAM-004).
- Each release records the applicable model version, API version,
  and conformance version.

This preserves the management-vs-execution separation already in
the repository and aligns with the project's stated position that
"CLAM is not the closed-loop runtime."

## Consequences

Positive:

- The conceptual model can evolve without API breakage as long as
  the conformance contract holds.
- Alternative implementations (in other languages, in other
  frameworks, or in vendor integrations) can adopt CLAM without
  depending on the Python reference implementation.
- Conformance testing becomes a first-class artefact of the
  repository rather than an internal property of one implementation.

Negative / costs:

- Two things can disagree: the model and the implementation.
  Authors must keep the conformance test suite authoritative.
- Alternative implementations have to learn the conformance
  contract from documentation rather than read the Python source.
- The repository now requires explicit version pinning for the
  model, the API, and the conformance rules.

Operational consequences:

- CHANGELOG entries must distinguish model changes from
  API changes from conformance changes.
- The OAS-first cardinal rule (see `context/AGENT-DOCTRINE.md`)
  remains intact: source-of-truth is the Pydantic models, and the
  OpenAPI document is regenerated.

## Alternatives considered

- **Management specification only** (position 1) was rejected
  because the repository is already a reference implementation
  and the user has invested in shipping it.
- **Reference implementation only** (position 2) was rejected
  because it would block alternative implementations and tie the
  model to one language stack.

## Follow-on

- Tracked by CR-CLAM-001 Stage 3 (normative specification).
- The conformance contract that alternative implementations must
  satisfy is established by CR-CLAM-004.
- CR-CLAM-002 (semantic model) is the first place this ADR's
  decision is realised as binding schema changes.

## References

- CR-CLAM-000 (`governance/reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md`), Section 10 Decision A.
- CR-CLAM-001 (`governance/CR/CR-CLAM-001-normative-capability-model.md`).
