# Novelty and contribution protocol

Novelty review is an evidence search, not a stylistic impression. Run it at claim level.

## Privacy gate

Before external search, determine whether query terms could disclose unpublished ideas, sensitive systems, partners, datasets, or security weaknesses. Obtain explicit authorization for external searching. If needed, use sanitized concept-level queries approved by the PI and record the coverage limitation.

## Step 1: Extract contribution claims

Create 3-8 atomic claims. For each, record:

- claimed novelty type;
- problem/task and setting;
- mechanism or technical delta;
- proposed evidence;
- language used in the proposal;
- proposal location.

Do not search only the proposal's preferred terminology. Generate synonyms, older terminology, neighboring disciplines, method components, and problem-first queries.

## Step 2: Search in layers

For each claim, use at least three materially different query formulations and search:

1. recent primary papers and preprints;
2. seminal older work and surveys for terminology drift;
3. citation and related-work neighborhoods around the closest candidates;
4. NSF Award Search and exact-program awards;
5. relevant standards, datasets, systems, patents, or deployed tools only when they bear on the claimed delta.

Prefer publisher pages, DOI/Crossref records, arXiv records, OpenAlex/Semantic Scholar metadata, and full papers. Search snippets are never final evidence. Verify identifiers, titles, authors, dates, and the actual overlapping method or finding.

Record the search date, databases, date range, query strings, filters, and unavailable sources. Avoid claims such as "no prior work exists"; say what was searched and what was not found.

## Step 3: Build the overlap/delta matrix

For every close work or award, compare:

| Axis | Proposed work | Prior work | Material delta | Evidence | Confidence |
|---|---|---|---|---|---|
| Question | | | | | |
| Mechanism/method | | | | | |
| Assumptions/setting | | | | | |
| Data/population | | | | | |
| Evaluation | | | | | |
| Expected knowledge | | | | | |

Classify each proposed claim:

- `supported`: retrieved evidence supports a material delta;
- `partially_supported`: some delta exists, but scope or significance is overstated;
- `contradicted`: prior work appears to subsume the claim;
- `insufficient_evidence`: search coverage or proposal specificity is inadequate.

## Step 4: Test contribution significance

Ask separately:

- Is the delta new?
- Is it non-obvious?
- Is it scientifically important?
- Does the evaluation isolate that delta?
- Will success produce generalizable knowledge?

An application of X to Y, a larger scale, a new dataset, or an integration may be valuable, but it is not automatically a research contribution. Explain the knowledge gained that could transfer beyond the artifact or deployment.

## Step 5: Adversarial verification

Give a fresh reviewer the atomic claims, raw proposal, search log, and full closest-work evidence. Ask it to find:

- missed terminology and neighboring literatures;
- a stronger subsuming reference;
- exaggerated difference statements;
- novelty that depends on an unstated assumption;
- claims that are new only because the evaluation target is narrow.

Preserve unresolved disputes and lower confidence instead of forcing a binary verdict.

## Required novelty output

Include:

- atomic claims and locations;
- complete search log;
- closest-work/award table;
- overlap/delta matrix;
- per-claim classification and confidence;
- strongest skeptical counter-position;
- safer positioning language;
- known coverage gaps and next search action.
