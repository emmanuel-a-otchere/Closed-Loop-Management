# D-2026-10-20: Standards references in repository artefacts

## Status

Accepted

## Context

Cardinal rule 4 of
[`context/AGENT-DOCTRINE.md`](../../context/AGENT-DOCTRINE.md)
prohibits referencing TMForum, eTOM, Frameworx, SID, GB921, TAM,
ODF, OSS/BSS in this repository, substituting ITU-T M.3050.x,
ETSI TS, ISO/IEC, NIST, or SDO-neutral standardization. The README
"Related Standards" section nonetheless cited two embargoed
external-SDO resources (IG1219A and TR284C), a contradiction
identified in the 2026-10-20 reconnaissance (finding F-03 of
[`../PLANS/RECON-CLOSURE-PLAN-2026-10.md`](../PLANS/RECON-CLOSURE-PLAN-2026-10.md)).

## Decision

Rule 4 applies to all repository artefacts, including the README.
The embargoed citations are removed and replaced with
SDO-neutral substitutes: ITU-T M.3050 series (management-plane
and assurance frameworks), ISO/IEC/IEEE 42010 (architecture
description and boundaries), and NIST SP 800-160 Vol.1
(assurance-evidence and traceability discipline). The substitutes
were chosen because they anchor the same three concerns the
embargoed citations anchored: closed-loop management frameworks,
architecture description, and assurance practice.

## Consequences

- The README standards section is compliant with rule 4 and the
  cardinal-rules CI gate.
- No normative content depended on the removed citations; the
  binding contracts, lifecycle, and data model are unchanged.
- Future standards citations must pass the rule 4 vocabulary and
  cite only the permitted substitutes.
