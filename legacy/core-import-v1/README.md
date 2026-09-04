# Legacy Core Writer Import v1

This directory preserves the verified, staging-only importer for
`rka-legacy-writer-export/v1` bundles produced by RKA Core.

It exists for compatibility and recovery. It does not define the new Writer
Authoring Graph, switch Writer authority, mutate Core, or authorize migration
of a live manuscript.

## Contents

- `rka_writer_staging.py` — strict content-addressed staging and verification;
- `contracts/rka-legacy-writer-export-v1.json` — frozen bundle contract; and
- `tests/` — golden bundle and tamper, scope, reference, and publication tests.

Run the compatibility tests from the repository root:

```bash
python3 -m pytest -q legacy/core-import-v1/tests
```

Retirement requires a separate compatibility-sunset decision after supported
legacy databases have migrated and recovery no longer depends on this path.
