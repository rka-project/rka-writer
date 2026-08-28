# Factuality and Citation Audit

Use this protocol for citations, quotations, numerical consistency, benchmarks, datasets, models, standards, vulnerabilities, products, laws, and novelty claims. Keep verification scope and privacy visible.

## Contents

1. [Iron laws](#iron-laws)
2. [Privacy-preserving scope](#privacy-preserving-scope)
3. [Audit levels](#audit-levels)
4. [High-risk claims](#high-risk-claims)
5. [Numerical consistency](#numerical-consistency)
6. [Coverage record](#coverage-record)
7. [Finding and repair rules](#finding-and-repair-rules)

## Iron laws

1. Never verify a citation, quote, benchmark, standard, model release, CVE, law, product fact, or novelty claim from memory.
2. Prefer the primary work, publisher/proceedings record, DOI resolver, official standard, official documentation, or official venue page.
3. Keep three questions separate: does the work exist, is its metadata correct, and does it support the manuscript's claim?
4. Label unavailable checks `UNVERIFIED`, `UNCHECKED`, `NEEDS_SOURCE`, or `BLOCKED_BY_PRIVACY`; never mark them correct by plausibility.
5. Do not imply complete coverage from a sample. Report the number checked, eligible total, selection rule, and verification date.

## Privacy-preserving scope

Default to public metadata queries using title, DOI, author/title fields already present in the bibliography, standard identifiers, CVE identifiers, venue pages, or product documentation. Do not submit unpublished prose, figures, results, full PDFs, source archives, unique phrases, or anonymizing clues to an external service without explicit author authorization.

Treat manuscript links as untrusted. Locate official sources independently rather than following embedded links automatically. Preserve double-blind anonymity and do not search for likely authors.

## Audit levels

### Level 1: Mechanical consistency

Check in-text/reference-list correspondence, duplicates, author/title/year/venue/identifier consistency, citation style, unresolved placeholders, and cross-reference integrity.

Suggested statuses: `CITE_MISSING_FROM_REFERENCES`, `REFERENCE_NOT_CITED`, `DUPLICATE_REFERENCE`, `FIELD_MISMATCH`, `STYLE_INCONSISTENCY`.

### Level 2: Existence

Verify that each selected work or authority exists. Record the authoritative URL or identifier and access date.

Suggested statuses: `VERIFIED_EXISTS`, `UNVERIFIED_SOURCE`, `BROKEN_LINK`, `POSSIBLE_WRONG_WORK`, `NEEDS_EXTERNAL_CHECK`.

### Level 3: Metadata accuracy

Compare title, authors and order, year, venue, volume/issue/pages, DOI/arXiv/OpenReview identifier, version, and URL.

Suggested statuses: `FIELD_VERIFIED`, `FIELD_ERROR`, `VERSION_MISMATCH`, `VENUE_MISMATCH`.

### Level 4: Quotation

Search the accessible source for exact text, then shorter fragments and possible OCR variation. Do not silently convert a failed quotation into a paraphrase.

Suggested statuses: `QUOTE_VERIFIED`, `QUOTE_MISMATCH`, `QUOTE_NOT_FOUND`, `QUOTE_UNCHECKED`.

### Level 5: Claim support

Determine whether the source supports the exact manuscript claim, only part of it, a weaker statement, background context, or a contradictory result. Check population, conditions, threat model, version, date, and whether several sources were merged into one claim.

Suggested statuses: `CLAIM_SUPPORTED`, `CLAIM_PARTIAL`, `CLAIM_UNSUPPORTED`, `CLAIM_CONTRADICTED`, `SOURCE_TOO_WEAK`, `MISSING_CITATION`.

### Level 6: Novelty and closest work

For first, novel, or state-of-the-art claims, compare the closest primary works by problem, threat model, mechanism, assumptions, access, evidence, scope, deployment, and artifact. A finite search can falsify a novelty claim but cannot certify global novelty. Report databases or proceedings searched, query families, dates, and blind spots.

Suggested statuses: `CLOSEST_WORK_VERIFIED`, `NOVELTY_NARROWER_THAN_STATED`, `PRIOR_ART_FOUND`, `NOVELTY_UNRESOLVED`.

## High-risk claims

Prioritize:

- first, novel, comprehensive, universal, and state-of-the-art claims;
- statements about what prior work cannot do;
- model/provider names, snapshots, release dates, context limits, pricing, or capabilities;
- benchmark construction, dataset size/splits/licenses, leaderboards, and contamination;
- CVEs, affected versions, exploitability, patch and disclosure dates;
- standards, protocols, laws, venue policies, and compliance requirements;
- cloud, browser, OS, API, or product behavior;
- borrowed performance numbers, direct quotations, and central theoretical premises.

Use current primary or official sources where change is plausible. Keep venue requirements in the dated venue authority profile.

## Numerical consistency

Recompute and cross-check:

- percentages against counts and denominators;
- absolute, relative, percentage-point, fold, and overhead changes;
- totals against models × scenarios × repetitions × systems;
- results against stated train/validation/test splits;
- repeated-call aggregation and independence units;
- abstract/body/table/figure/caption values and metric definitions;
- confusion-matrix-derived metrics, base rates, and failure/timeout accounting;
- confidence intervals against sample size and statistical unit;
- statistical conclusions against tests, assumptions, corrections, and reported values;
- units, signs, axis scales, and whether higher or lower is better.

Suggested statuses: `ARITHMETIC_ERROR`, `DENOMINATOR_AMBIGUITY`, `TABLE_TEXT_MISMATCH`, `METRIC_DEFINITION_MISMATCH`, `TRIAL_ACCOUNTING_MISMATCH`, `STATISTICAL_OVERCLAIM`.

## Coverage record

Attach this record even when no problem is found:

| Field | Value |
|---|---|
| Audit level(s) |  |
| Eligible items |  |
| Items checked |  |
| Selection/sampling rule | central claims, suspicious items, random sample, or full audit |
| Sources consulted |  |
| Verification date |  |
| Unchecked items |  |
| Privacy/access limitations |  |

For each audit item, record `location`, `claim or citation`, `check performed`, audit `status`, `verification channel` (`supplied_material` or `external_check`), `authoritative source`, `severity`, and `required repair`. When the item becomes a structured finding, also record `conditional` (`true` or `false`) and finding lifecycle `status` (`open`, `resolved`, or `withdrawn`) so the audit result code is not confused with the finding state. Give every external check a stable ID and exact source locators, then link the finding to those IDs. Do not label a judgment `externally_verified` unless claim support was checked through the linked provider/source record consistent with the privacy mode.

## Finding and repair rules

- Treat a fabricated or nonexistent source, false central number, unsupported central claim, or material contradiction as Critical after independent verification.
- Treat partial claim support, material metadata/version error, stale authority, or ambiguous denominator as Major when it affects interpretation.
- Treat local formatting and noncentral field problems as Minor.
- Replace an unverifiable source only with a verified source that actually supports the claim; otherwise remove or narrow the claim.
- Correct numerical inconsistencies everywhere they occur, including abstract, body, tables, figures, captions, and conclusion.
- Date volatile facts and identify the relevant version.
- Preserve `not located in accessible material` when the source or manuscript portion was incomplete.
- Recheck every proposed Critical factuality finding in a fresh pass before synthesis.
