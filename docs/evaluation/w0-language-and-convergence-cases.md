# W0 Language and Convergence Cases

- Status: Proposed human protocol; some supplied-text W0 cases have engineering tests, not human validation
- Date: 2026-09-14
- Extended: 2026-10-18 (H1/H2 offline contract regressions)
- Extends: [W0 walkthrough](w0-walkthrough.md), not a second mandatory wizard
- Protocol: [language and revision](../design/language-and-revision-protocol.md)

## Setup

Test term choice, expression review and revision inside one paragraph of a
coherent paper. Use consented, sanitized question/claim/evidence, outline,
paragraph/intent plan, confusing term candidates and optional style examples.
Use supplied text/static cards in W0. These are expected behaviors, not results.
Select a manageable subset; do not require every case in every writing session.
New model prose still requires semantic admission and independent host gates.

## Paired cases

| ID | Situation | Expected behavior | Failure to record |
|---|---|---|---|
| T1 | Attractive labels denote different adjacent concepts | Show definition, precedent and examples; ask what concept is intended | Silent substitution or manufactured consensus |
| T2 | Canonical term is correctly repeated | Pass; allow approved grammatical forms | Substitute to improve vocabulary diversity |
| T3 | New term changes the unit of analysis | Reopen affected science/discourse before locking | Treat reframing as a lexical preference |
| P1 | Importance language adds no useful setting, mechanism or orientation | Anchor issue and missing information; no automatic rewrite | Blacklist an adjective or invent a mechanism |
| P2 | Hedge preserves real uncertainty; transition supplies needed guidance | Preserve or propose reviewed equivalent expression | Remove as defensive/formulaic |
| P3 | Dense technical wording is accurate and clear to the intended specialist | Pass/no change | Simplify away the distinction |
| P4 | Missing warrant recurs through patches | Return to the upstream question | Add connectives and polish again |
| S1 | Author accepts variant but declines generalization | Local acceptance; unchanged profile | Automatic global learning |
| S2 | Tone variant removes a material qualifier | Route to scope review, not same-intent calibration | Treat changed meaning as style |
| R1 | Patch restores an omitted approved condition | Claim record unchanged; expressed proposition corrected | Report only "claims changed: none" |
| R2 | Evidence changes while another branch is parked | Preserve bytes; review dependents, permit unrelated work | Automatic rewrite or global freeze |
| R3 | Author edits again after a patch preview | Preserve newer bytes; refuse stale patch | Overwrite human work |
| H1 | A rewrite retains 3,000 but changes an area lower bound to an exact value | Flag the quantitative relation change; no same-meaning acceptance | Digit matching or a style label hides changed scope |
| H2 | Removing historical narration introduces a hash map and O(1) lookup cost | Flag both unsupported propositions; return to evidence review | Plausible implementation becomes an asserted fact |

Also test preserved numeric digits with a changed metric, unit or comparison.
Token matching must not be reported as semantic safety.

## H1/H2 executable regression contract

The [source assessment](../research/2026-10-18-humanizer-review.md) pins the two
Humanizer examples. Their short adapted texts and manually supplied semantic
atoms live in [review fixtures](../../prototypes/w0/review-fixtures.mjs);
[probe tests](../../prototypes/w0/review-probe.test.mjs) exercise the read-only
[contract probe](../../prototypes/w0/review-probe.mjs). Run with:

```sh
node --test prototypes/w0/review-probe.test.mjs
```

H1 pairs the bad exact-value rewrite with a safe lower-bound paraphrase and
unchanged text. H2 pairs the two invented assertions with a paraphrase that
retains the replacement relation and the old algorithm's cost, while asserting
nothing about the new mechanism or complexity. Also test the invented mechanism
and the invented complexity independently; neither can escape by removing the
other. Removing a supported assertion is a change too.

Both cases require unchanged base text, immutable input snapshots, complete
supplied annotations and exact before/after bindings. Missing or malformed
annotations are unassessed; changed text or revision requires a new review.
Unchanged text and equivalent annotations permit no-change or researcher
review, not automatic acceptance. The same input must produce the same result.

These tests compare reviewer-supplied meaning representations; they do not
extract meanings from the sentences. They are not connected to the browser
reviewer, do not establish Humanizer's failure rate, and do not prove a model
will detect the defects. A future reviewer must be tested on the text, without
receiving the expected annotations or verdicts. Record its misses and false
alarms independently of these deterministic checks.

## Capture and comparison

Record fixture/base versions, participant/consent, author explanation before
and after, assistance, elapsed time, consequential versus mechanical decisions,
issue outcome and semantic changes. Label observed, participant-reported and
inferred items. Never fill this protocol with invented observations.

Separate detected defects, misses, false alarms and no-change outcomes. Record
whether reopening came from new evidence, author reframing, reader confusion
or system drift. Acceptance/rejection rates alone do not prove comprehension.

For style, compare another admitted intent against concise direct preferences.
For workflow, give a competent document-plus-contextual-chat baseline the same
materials. Seeded mock cases do not establish real-world detector accuracy.

## W1 handoff

Use observations to select the smallest viable term proposal, issue record,
semantic-change report and approval preview. Keep usability/host unknowns
visible. W1 should exercise a term distinction, a legitimate no-change or
qualification case, declined rule promotion and a scope-restoring patch with
its existing evidence-change/recovery cases.

A protocol file, green repository test or successful embedding backfill does
not satisfy W0/W1's human validation gate.
