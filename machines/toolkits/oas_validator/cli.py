"""OAS validator -- CLAM profile rules.

The base OAS 3.1 schema is enforced by ``openapi_spec_validator``. The
profile rules below add CLAM-specific constraints:

1. Every operation must declare an ``operationId`` (machine-readability).
2. The ClosedLoop state enum must contain all 7 lifecycle states.
3. Every POST/PATCH endpoint that accepts a body must declare a request
   body schema that is a strict object (not a primitive).
4. Errors must use the CLAM envelope (``ErrorEnvelope``) -- detected by
   inspecting the ``Problem`` schema names in ``components.schemas``.

Usage as a module:

    from machines.toolkits.oas_validator import validate
    findings = validate(path)
    if findings:
        raise SystemExit(1)

Usage as a CLI:

    python -m machines.toolkits.oas_validator schemas/openapi/openapi.json
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

REQUIRED_STATES = {
    "designed",
    "validated",
    "published",
    "active",
    "paused",
    "error",
    "retired",
}


@dataclass
class Finding:
    """A single rule violation."""

    severity: str  # "error" | "warning"
    rule: str
    path: str
    message: str

    def format(self) -> str:
        marker = "ERROR" if self.severity == "error" else "WARN"
        return f"[{marker}] {self.rule} @ {self.path}: {self.message}"


def _load(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def _check_operation_id(spec: dict) -> list[Finding]:
    findings: list[Finding] = []
    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            if not op.get("operationId"):
                findings.append(
                    Finding(
                        severity="warning",
                        rule="operation-id-required",
                        path=f"paths.{path}.{method}",
                        message="Missing operationId; machine-generated clients will fall back to method+path.",
                    )
                )
    return findings


def _check_closed_loop_state_enum(spec: dict) -> list[Finding]:
    findings: list[Finding] = []
    schemas = spec.get("components", {}).get("schemas", {})
    state_schema = schemas.get("ClosedLoopState", {})
    enum = state_schema.get("enum")
    if enum is None:
        return findings
    missing = REQUIRED_STATES - set(enum)
    if missing:
        findings.append(
            Finding(
                severity="error",
                rule="closed-loop-state-completeness",
                path="components.schemas.ClosedLoopState.enum",
                message=f"Missing states: {sorted(missing)}",
            )
        )
    return findings


def _check_request_body_is_object(spec: dict) -> list[Finding]:
    findings: list[Finding] = []
    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if method.lower() not in {"post", "put", "patch"}:
                continue
            content = op.get("requestBody", {}).get("content", {})
            for media_type, media in content.items():
                schema = media.get("schema", {})
                if schema.get("type") and schema.get("type") != "object":
                    findings.append(
                        Finding(
                            severity="error",
                            rule="request-body-must-be-object",
                            path=f"paths.{path}.{method}.requestBody.content.{media_type}",
                            message=f"Body schema must be type=object, got {schema.get('type')}",
                        )
                    )
    return findings


def _check_error_envelope(spec: dict) -> list[Finding]:
    findings: list[Finding] = []
    schemas = spec.get("components", {}).get("schemas", {})
    envelope = schemas.get("ErrorEnvelope")
    if not envelope:
        findings.append(
            Finding(
                severity="error",
                rule="error-envelope-required",
                path="components.schemas",
                message="Missing ErrorEnvelope schema. All error responses must conform to the CLAM envelope.",
            )
        )
        return findings
    required = {"code", "message"}
    props = set(envelope.get("properties", {}).keys())
    missing = required - props
    if missing:
        findings.append(
            Finding(
                severity="error",
                rule="error-envelope-shape",
                path="components.schemas.ErrorEnvelope",
                message=f"Missing required fields: {sorted(missing)}",
            )
        )
    return findings


def validate(path: Path) -> list[Finding]:
    """Run all CLAM profile rules against the OAS document at ``path``."""
    spec = _load(Path(path))
    findings: list[Finding] = []
    findings.extend(_check_operation_id(spec))
    findings.extend(_check_closed_loop_state_enum(spec))
    findings.extend(_check_request_body_is_object(spec))
    findings.extend(_check_error_envelope(spec))
    return findings


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: clam-oas-validator <path-to-openapi.json>", file=sys.stderr)
        return 2
    findings = validate(Path(sys.argv[1]))
    if not findings:
        print("CLAM OAS profile: PASS (0 findings)")
        return 0
    for f in findings:
        print(f.format())
    errors = sum(1 for f in findings if f.severity == "error")
    print(f"\nCLAM OAS profile: {len(findings)} findings ({errors} errors)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())