# CLAM OAS Validator

A profile-level validator for OpenAPI 3.1 documents that conform to the
CLAM (Closed Loop Automation Management) API conventions.

## Why

`openapi-spec-validator` enforces the OAS 3.1 schema. The CLAM profile
enforces **project-level** rules on top:

1. `operation-id-required` (warning) -- every operation declares an
   `operationId` so machine-generated clients have a stable handle.
2. `closed-loop-state-completeness` (error) -- the `ClosedLoopState` enum
   must contain all 7 lifecycle states.
3. `request-body-must-be-object` (error) -- POST/PUT/PATCH bodies must
   declare an object schema, not a primitive.
4. `error-envelope-required` (error) -- the OAS must define an
   `ErrorEnvelope` schema with `code` and `message` fields.

## Install

```bash
pip install -e ".[toolkit-oas-validator]"
```

## Usage

```bash
clam-oas-validator schemas/openapi/openapi.json
# or as a module
python -m machines.toolkits.oas_validator schemas/openapi/openapi.json
```

Exit code: `0` on success (no errors; warnings allowed), `1` on errors,
`2` on usage error.

## Output

Each finding is printed on its own line in the format
`[ERROR|WARN] <rule> @ <json-pointer>: <message>`. A summary line follows.

## Programmatic use

```python
from machines.toolkits.oas_validator import validate
findings = validate("schemas/openapi/openapi.json")
```