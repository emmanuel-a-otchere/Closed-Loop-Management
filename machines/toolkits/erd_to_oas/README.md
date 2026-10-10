# CLAM ERD-to-OAS Generator

Reads an entity-relationship diagram in .xlsx form and emits an OAS 3.1
schema fragment compatible with the CLAM API.

## Why

The CLAM data model lives in two forms:

- The 2022 reference ERD at `schemas/data-model/legacy-2022-erd.xlsx`.
- The binding OAS-backed model at `schemas/data-model/clam-data-model-1.0.md`.

This toolkit bridges the two. Drop a new ERD .xlsx in the same shape and
emit the corresponding OAS fragment; a downstream step merges it into the
live `openapi.json`.

## Workbook convention

- One sheet per entity.
- Row 1: header (`Attribute | Type | Description`).
- Row 2+: one row per attribute.

Supported type strings: `string`, `text`, `uuid`, `datetime`, `date`,
`integer`, `int`, `number`, `float`, `boolean`, `bool`.

## Install

```bash
pip install -e ".[toolkit-erd-to-oas]"
```

## Usage

```bash
clam-erd-to-oas schemas/data-model/legacy-2022-erd.xlsx \\
    --out schemas/openapi/erd-fragment.json
```

The output is a JSON object with the shape
`{"components": {"schemas": {"EntityName": {...}, ...}}}`.