# Output and Session Envelope

Use the root envelope only to organize a session. Never replace or mutate native engine outputs.

## Route directories

Write each review target to a separate directory, for example:

```text
review-session/
  session-index.md
  paper-review/
    academic-session-envelope.json
    ...native paper-engine artifacts...
  nsf-proposal-review/
    academic-session-envelope.json
    ...native proposal-engine artifacts...
```

Use only the applicable route directory for a single-target session. Let each engine choose its required artifact names and machine-readable layout. For a file-based review run, create one `academic-session-envelope.json` in that route directory from `schemas/academic-session-envelope.schema.json`.

## Session index

Keep `session-index.md` concise and human-readable. Record:

- session label and date;
- primary artifact type and selected engine;
- reviewed filenames, versions, and hashes when available;
- native mode and scope;
- venue or NSF authority status;
- privacy and external-search boundary;
- native output directory and principal human-readable report;
- native validator command and result, or why validation was not applicable or unavailable;
- material limitations and unresolved routing or authority questions.

Do not create a root score, rating, recommendation, disposition, confidence, or assurance label. Link to the native values instead.

## Machine envelope

Use the common JSON envelope only as a provenance and integrity index. Record the selected artifact kind and engine, privacy mode, authority snapshot linkage, packaged engine-manifest hash, input hashes, native-output hashes and roles, declared native-validator status with a linked report when completed, and limitations. Do not copy native judgments into it. Envelope validation checks structure, hashes, roles, and link consistency; it does not independently prove that the native validator executed or that its report is scientifically correct.

Validate it with:

```bash
python3 -B <skill-dir>/scripts/validate_academic_review.py validate-session <route-dir>/academic-session-envelope.json
```

Before invoking a native validator, verify the vendored engines with:

```bash
python3 -B <skill-dir>/scripts/validate_academic_review.py verify-engines
```

Then invoke only the selected engine's validator by its full namespaced path and follow that engine's native instructions. Override bare Python examples by using `python3 -B` for every packaged entrypoint. Place every generated review artifact, report, and validator output in the declared route directory outside `<skill-dir>`. Never point an output option at an input artifact or any packaged skill file.

## Mixed targets

For a paper-plus-proposal session, give each route its own section and its own machine envelope. The common schema intentionally represents one native route; do not create a mixed JSON envelope. State each native outcome exactly as produced and keep its confidence and assurance beside it. Cross-artifact observations may identify consistent terminology, shared evidence, or conflicting claims, but must cite both artifacts and remain narrative.

End the session index with: `Separate native reviews; no blended score, joint acceptance/funding prediction, or cross-engine assurance claim.`

Do not feed one native verdict into the other's sealed review. If a user later requests a comparison, compare the frozen outputs without changing them.

## Validation and sharing

Run only the selected engine's validator against its native artifacts. Preserve validation reports, manifests, hashes, and disclosed limitations. Structural validation establishes declared shape, traceability, and consistency only; it does not prove correctness, novelty, likely publication, or likely funding.

When packaging outputs, include the session index and each complete native route directory. Compute an archive checksum separately. Do not claim that an archive was revalidated on a different machine when native manifests are origin-path-bound.
