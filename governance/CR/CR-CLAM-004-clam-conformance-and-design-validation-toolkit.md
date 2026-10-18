---
cr_id: CR-CLAM-004
title: CLAM Conformance and Design Validation Toolkit
status: Proposed
priority: P1
type: Tool enhancement
repository: emmanuel-a-otchere/Closed-Loop-Management
dependencies: [CR-CLAM-002, CR-CLAM-003]
source_review: CR-CLAM-000 (Section 7, CR-CLAM-004)

---

# CR-CLAM-004: CLAM Conformance and Design Validation Toolkit

## Change summary

Expand OAS validation into distinct stages covering schema, reference and relationship, semantic, lifecycle, requirements/constraint completeness, inter-loop compatibility, and release-readiness.

## Problem statement

The OAS validator provides a foundation for contract validation, but structural schema validity alone cannot establish that a closed-loop design is semantically complete or operationally admissible.

## Motivation and rationale

A model that passes JSON-schema validation can still be incoherent (missing goals, dangling references, lifecycle transitions that violate guards). Separating the validation stages makes each failure mode addressable independently and produces machine-readable reports fit for CI gates.

## Proposed change

Replace the single OAS validator with a staged CLAM conformance validator:

1. **Schema validation** -- pure OAS/JSON-schema correctness.
2. **Reference and relationship validation** -- all `id`/`ref` pointers resolve; cardinality constraints hold.
3. **Semantic validation** -- entities match their definitions from CR-CLAM-002.
4. **Lifecycle validation** -- transitions are guarded correctly.
5. **Requirements/constraint completeness** -- every loop has a goal, a constraint set, and acceptance criteria.
6. **Inter-loop compatibility** -- links between loops respect the compatibility rules from CR-CLAM-008.
7. **Release-readiness validation** -- required approvals, evidence, and signatures are present.

Each stage emits a JSON report with stable identifiers. Severity policy is explicit.

## Repository changes (deliverables)

- `machines/toolkits/clam-conformance-validator/`
- `machines/toolkits/clam-conformance-validator/README.md (CLI and CI usage)`
- `datasets/conformance/positive-fixtures/ and negative-fixtures/`
- `Severity and failure policy in docs/conformance/validation-rules.md`
- `CI integration: `cardinal-conformance` job gate on every PR`

## Acceptance criteria

1. Invalid models fail validation for the appropriate reasons (one stage at a time, deterministic).
2. Validation results identify the failing artefact and the exact rule that failed.
3. Equivalent inputs produce deterministic results (no time/randomness dependencies).
4. Validation stages can be invoked independently via the CLI.
5. Release-readiness rules are explicit and testable.

## Out of scope

- Performance/load testing (covered by separate ops tooling).
- Production-lifecycle enforcement (covered by CR-CLAM-007).

## Dependencies

- Depends on: CR-CLAM-002, CR-CLAM-003

## Follow-on relationship

- CR-CLAM-005 (scenario simulation) consumes the design-validation report.
- CR-CLAM-007 (bounded autonomy) reuses the release-readiness stage.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Too many validation stages slow PRs. | Run schema + reference checks by default; full suite is opt-in via CLI flag or release branch. |
| Rule proliferation makes the toolkit hard to maintain. | Each rule carries a stable ID, owner, and lifecycle policy in docs/conformance/validation-rules.md. |

## Source

This CR is a harvest of the canonical proposal in
[`governance/reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md`](../../reviews/2026-10-18-CR-CLAM-000-capability-review-and-roadmap.md),
Section 7, CR-CLAM-004. The full prose, including its tables and rationale, is
preserved verbatim in that file.
