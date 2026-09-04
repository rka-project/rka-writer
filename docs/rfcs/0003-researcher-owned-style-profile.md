# RFC 0003: Researcher-Owned Style Profile

- Status: Provisional
- Owner: Chenglong Fu
- Start date: 2026-09-04
- Governing refinement: [ADR 0008](../adr/0008-paper-centered-incremental-commitment.md)
- Related RFCs: [0001](0001-authoring-ir-and-convergence-protocol.md), [0002](0002-subscription-host-and-paper-studio.md)

## Summary

Help authors articulate and retain the term, prose, and tone choices they
actually prefer. Start with optional selected samples and a few understandable
observations; calibrate through comparisons for the same admitted sentence
intent. Do not require a long style questionnaire or rule-by-rule onboarding.

Style is a researcher-owned, versioned preference layer, not a model's hidden
imitation prompt. It never supplies research facts, strengthens claims or
overrides concept correctness.

## Early direction, later calibration

During paper setup, ask what the author likes about a selected paper or passage,
which section it should influence, and what to avoid. Two to five papers is a
starting suggestion, not a quality threshold; zero samples is valid. Do not
issue a warning merely because the author provides one strong example.

An early Style Brief guides planning without blocking epistemic work. Use
transparent defaults if desired, labeled suggestions rather than inferred
author voice. Exact concepts/terms and the target intent must be ready before
agent-generated sentence comparisons. Style setup is not a loophole for
drafting unapproved paragraphs.

## Selected sources and observations

| Source role | Appropriate influence | Limit |
|---|---|---|
| Author-written | Endorsed personal expression | Not automatically correct terminology or permission to copy coauthored text |
| Admired exemplar | Specific desired rhetorical/prose quality | Not an author's identity or a sentence bank |
| Venue exemplar | Genre and presentation conventions | Does not override scientific accuracy |
| Negative exemplar | Specific pattern to avoid | Not a blanket ban on a word or grammar form |

The author selects files/passages and allowed analysis scope. Record source
identity, hash, locator, authorship/rights context, role and rationale.
Observations include the relevant passage/measurement, section/function,
interpretation, uncertainty and possible confounders. Frequency does not imply
approval. No silent scanning of the research library.

Start by surfacing a few consequential differences, not every measurable
feature. Source observations can be grouped in a reviewed preference bundle;
the author can inspect each source and exclude individual proposed rules.

## Contrastive calibration

1. Hold the approved proposition, scope, evidence, terms and rhetorical function
   fixed for a target sentence.
2. Compare a small candidate set differing in one declared expression
   dimension, such as actor placement or explanation density.
3. Let the author choose, edit, reject all, or explain what the contrast missed.
4. Ask whether the preference is local, applies to a section type, or should
   become a paper rule. No automatic global learning from an accepted edit.
5. Preview any rule promotion, examples and affected scope as an explicit
   approval bundle. Record the accepted rule separately from the sentence.

All candidates pass ordinary admission; changed meaning is a new semantic
proposal, not a style variant. The author can inspect supplied example text
before admission, but the agent cannot generate new manuscript prose then.
Use the [walkthrough](../evaluation/w0-walkthrough.md) to test comprehension.

## Minimal logical records

Keep selected sources, grounded observations, approved profile versions and a
resolved target contract. A rule stores:

- dimension: term, prose or tone;
- behavior and rationale;
- polarity: prefer or avoid;
- enforcement: advisory or required;
- scope: project, paper, section type, section or paragraph;
- supporting observations or direct author instruction;
- explicit overrides/exceptions and approval event.

Polarity is not strength: "avoid noun stacks" may be advisory, whereas a
forbidden alias can be required. A calibration event links the same-intent
comparison, author response and optional promoted rule. Do not require an
independent database table for each concept before the prototype.

## Scientific terminology versus voice

Concept definition, field precedent and technical correctness come first.
Samples suggest labels, but author habit cannot establish synonym equivalence.
Approved Term Locks retain definition, allowed variants and first-use policy.

Prose preferences include actor/action placement, information density,
definition/citation integration, paragraph rhythm and transition style.
Tone preferences include directness, formality and reader orientation.
Neither average sentence length nor sample similarity becomes a quota.

Material qualifications and claim strength belong to the scientific contract.
"May improve" → "improves" is not an ordinary tone adjustment.

## Resolving rules

Scientific meaning and applicable venue/disclosure requirements must both be
satisfied; a conflict is escalated, not silently resolved by making science
false. Concept definitions and Term Locks outrank stylistic preferences.

Within a compatible style dimension, a narrower approved scope may override a
broader one only through an explicit override relation. Scope order is
paragraph → section → section type → paper → project. Required/advisory status
does not create permission to override a scientific or term contract.
Contradictory required rules without an explicit exception block target
acceptance pending review. Conflicting advisory rules are shown and may remain
optional; do not let them block scientific work.

Resolved target contracts contain applicable approved rules, locks, overrides
and exact version references. An empty/default profile is valid when explicitly
chosen; a full Style Lab is not a prerequisite to writing.

## Rules versus examples

The initial path is rules-only. Whole sample papers are excluded from realization
context. Evaluate a separate rules-plus-small-approved-examples path only if
rules-only calibration fails to preserve useful expression choices.

An optional example must be explicitly approved for model context, short,
source/locator-bound, relevant to the current rhetorical function, and cleared
for that use. Prefer author-supplied examples or independently written
same-meaning contrasts where appropriate. Selection for style analysis does not
automatically authorize reuse as a generation example. The manifest records
the example, rights/context declaration and content hash.

Examples supply expression guidance, never factual support. Reusing source
claims requires a separate reviewed Evidence Use. Distinctive source prose
cannot enter the manuscript as unattributed original writing.

This optional path is a hypothesis, not a supported feature or a claim that
examples outperform rules.

## Copy risk, review and privacy

Compare candidates with selected samples and any approved examples. Exact
seeded overlap can be tested deterministically; general plagiarism or semantic
similarity cannot be certified absent. Conventional terms require different
treatment from distinctive phrasing.

Flagged text remains blocked until replaced, appropriately quoted/cited, or
the flag is reviewed and documented as a false positive (for example, a
required conventional term). A generic "ignore warning" is not permission to
copy. Source licences and confidentiality still apply.

Only selected content is analyzed. Local storage does not mean inference stays
local: content sent through a cloud-backed subscription host is subject to its
data controls. Use RFC 0002's manifest, authorization and actual isolation.
An extraction session that saw whole samples must not become the realization
session by default.

## Changes and provenance

| Change | Effect |
|---|---|
| Definition or required term changes | Block affected target pending lexical/semantic review |
| Required style rule changes | Review conformance before new acceptance |
| Advisory preference changes | Non-blocking review suggestion; no rewrite |
| Source text or role changes | Review observation lineage and affected use permissions |
| Sample removed | Keep historical lineage; stop future source use as requested; review affected rules |
| Author edits a sentence | Preserve edit; no global profile mutation without consent |

An approved preference is an author decision, not a perpetual factual claim
about its sample. If source wording changes, review whether its observation
still holds without automatically revoking a directly endorsed preference.
The author may retain the rule as a direct preference with a recorded decision.
Historical versions and source-use permissions remain distinguishable.
Style state stays in Writer, not Core.

## Evaluation and open questions

W1 needs only a small profile, optional synthetic sources, one same-intent
contrast, one declined rule promotion, one explicit scope override and one
copy-risk case. Compare author understanding, effort and blinded style preference
against simple direct instructions. Measure generalization on another admitted
intent, not just the calibration sentence.

Open: which observations help authors; useful sample amount; example benefit
versus copying risk; scope negotiation among coauthors; false positives;
minimum inspection UI. No universal overlap threshold or style score is frozen.

## History

- 2026-09-04: Initial sample-to-rule proposal.
- 2026-09-04: Revised under ADR 0008: contrastive calibration, consent to
  generalize, polarity/enforcement separation and an optional bounded-example
  experiment. The rules-only path remains the initial implementation target.
