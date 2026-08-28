# Review Output Template

Use this template for `standard` and `full-forensic` review. Shorten it for `quick` or `focused` mode; use a finding-resolution matrix for `re-review`. Do not create empty criticism merely to fill a heading.

## Contents

1. [Layer A: Referee report](#layer-a-referee-report)
2. [Layer B: Author annex](#layer-b-author-annex)
3. [Final consistency gate](#final-consistency-gate)

## Layer A: Referee report

### Review scope and assurance

- Review mode:
- Manuscript version/hash:
- Human-readable initial report label/hash:
- Material scope: full manuscript, partial manuscript, abstract, excerpt, outline, or unknown:
- Target venue/year/track/paper type:
- Materials inspected:
- Materials partial, inaccessible, unrendered, or not supplied:
- External-verification mode and coverage:
- External check IDs/providers/content classes/purpose/source locators/dated authorization, if any:
- Reviewer composition:
- Assurance: `single_pass_advisory` only for exactly one AI/model reviewer; `provisional_advisory` for same-family panels; `cross_model_advisory` for a sealed, registry-substantiated cross-model panel; or `human_panel` only for a substantiated multi-human panel:

For a same-family simulated panel, include the disclosure required by `panel-protocol.md`.

### Paper reconstruction

In one paragraph, state the paper's problem, threat or failure source, core idea, main contribution, evidence, and boundary. Describe the strongest defensible version of the paper, not a promotional version.

### Overall assessment

State:

- recommendation using the verified venue scale, or a venue-neutral readiness judgment;
- confidence separately from recommendation;
- the strongest acceptance case;
- the strongest rejection or revision-blocking case;
- whether the judgment depends on inaccessible material or unverified facts.

Do not present a simulated recommendation as an acceptance probability.

### Strengths to preserve

List specific strengths anchored to the manuscript. Include scientific, technical, empirical, and presentation strengths as applicable.

### Major comments

Report only evidence-backed Critical and Major findings. Use up to ten top priorities, not a quota.

For each finding:

- **ID / category / severity / confidence / conditional / status:** use `conditional: true|false` and lifecycle `status: open|resolved|withdrawn`.
- **Manuscript anchor:** printed or PDF page, section, figure/table/equation, and short observable evidence; or `not_located` with inspection limits.
- **Observation:** what the accessible manuscript says, shows, or makes difficult to locate.
- **Affected claim:**
- **Reviewer consequence:** why this changes correctness, novelty, validity, reproducibility, significance, or comprehension.
- **Repair:** smallest credible response; distinguish required claim narrowing from optional additional work.
- **Verification test:** what evidence would show that the concern is resolved.
- **Source status and verification channel:** dated primary/official source plus `supplied_material` or logged `external_check`; otherwise `not_checked`, `unverified`, or `blocked_by_privacy` with `not_applicable` channel.

Separate observations from interpretations and questions. Do not demand a different paper merely because another method is preferable.

### Minor comments

List local issues with exact anchors and preserve their ID, category, severity, confidence, `conditional`, and lifecycle `status` fields. Consolidate repeated terminology, notation, grammar, caption, and formatting defects instead of producing a line-edit dump.

### Questions for the authors

Ask only questions whose answers could change the judgment, interpretation, or requested repair. Do not disguise accusations as questions.

### Reviewer expertise and limits

State relevant expertise, confidence by dimension when it differs, disagreements among reviewers, and what was not assessed.

## Layer B: Author annex

Keep this layer separate from the realistic referee report.

### Fast-reader and cognitive-load audit

| Test | Reconstruction or score | First breakpoint | Reviewer consequence | Minimal repair |
|---|---|---|---|---|
| 30-second title/abstract/introduction read |  |  |  |  |
| 3-minute headings/figures/captions skim |  |  |  |  |

Report the six reconstruction scores, backtracking locations, terminology or notation hotspots, and strongest navigational aid. Preserve generalist/domain-expert disagreement.

Then provide actionable presentation repairs:

| Priority | Finding ID | Severity | Conditional | Status | Exact anchor | Fast-reader action or likely misreading | Cognitive-load source | Smallest repair | Concrete illustrative suggestion | Precision guard | Cold-read verification test |
|---:|---|---|---|---|---|---|---|---|---|---|---|

Rank the top three load-bearing repairs separately and explain what later sections each repair unlocks. Consider ordering, lead sentences, definitions at first use, terminology alignment, section/paragraph jobs, overview figures, self-contained captions, and claim-to-evidence navigation. Do not respond to cognitive load only by adding prose; moving, deleting, relabeling, or visualizing existing material may be better.

### Claim-evidence ledger

| Claim ID | Exact claim and location | Evidence offered | Assumptions/scope | Gap or uncertainty | Reviewer risk |
|---|---|---|---|---|---|

Do not drop claim location or reviewer risk.

### Threat-model ledger

When applicable, map each security claim to:

| Claim ID | Asset/property | Actor/goal | Capability/access/knowledge/budget | Adaptivity | Trust boundary/TCB | Success/exclusions | Exercised by evidence? |
|---|---|---|---|---|---|---|---|

### Structured issue ledger

Include every live finding and its verification status. Preserve withdrawn or downgraded Critical findings as verification records rather than silently deleting history.

| ID | Claim | Category | Severity | Confidence | Conditional | Anchor | Judgment type | Status | Repair | Verification test |
|---|---|---|---|---|---|---|---|---|---|---|

### Critical-finding verification log

For every proposed Critical finding, preserve the originating record and add a fresh, non-originating verification:

| Finding | Verifier | Anchor checked | Arithmetic/source checked | Counterevidence considered | Status | Rationale |
|---|---|---|---|---|---|---|

Allowed statuses: `confirmed`, `downgraded`, `withdrawn`, `unresolved`. An unverified Critical concern cannot be the sole basis for a reject-level synthesis.

### Decisive experiment and analysis plan

Propose experiments only when they are necessary and feasible. Claim narrowing or clarification may be the correct repair.

| Finding | Research question | Minimal credible design | Fair baselines/ablations | Unit/metrics/uncertainty | Interpretation rule | Claim supported/not supported |
|---|---|---|---|---|---|---|

### Figure and table plan

| Proposed visual | Reviewer question answered | Required elements | Claim mapped | Placement |
|---|---|---|---|---|

### Citation and factuality coverage

- Audit level:
- Items checked / eligible total:
- Selection or sampling rule:
- Verification date:
- Sources used:
- Unchecked or privacy-blocked items:

| Location | Claim/citation | Check performed | Status | Evidence source | Consequence/fix |
|---|---|---|---|---|---|

Keep existence, metadata accuracy, and claim support as separate checks.

### Claim calibration and wording

Provide example wording only where it materially improves precision.

| Current wording and anchor | Evidentiary problem | Illustrative calibrated wording | Meaning-preservation check |
|---|---|---|---|

Never infer AI authorship. Do not apply stock replacements when they alter the scientific meaning.

### Prioritized repair plan

Order work by dependency:

1. correctness, integrity, safety, and verified policy blockers;
2. central claim, threat model, and contribution positioning;
3. evaluation validity, statistics, and reproducibility;
4. organization, fast-reader comprehension, figures, and terminology;
5. local prose and formatting.

For each step, state the finding IDs resolved, required inputs, expected output, and verification check.

### Re-review resolution matrix

Use only in `re-review` mode:

| Prior finding | Prior anchor | Revised anchor | Author action | Independent verification | Status | Residual risk |
|---|---|---|---|---|---|---|

For prior-finding matrix rows, allowed statuses are `resolved`, `partly_resolved`, `unresolved`, and `regressed`. Record newly discovered issues in the current finding ledger with stable new IDs; do not pretend they were prior findings.

### Interactive clarification and rebuttal log

Use in `interactive` mode. Preserve the initial manuscript-only finding.

Declare `interaction_type` as `internal_clarification` or `venue_rebuttal_simulation`, and declare `interaction_phase`:

- `awaiting_author_response`: at least one issued question remains unanswered. On the first turn, `evidence_artifacts`, `author_responses`, `re_evaluations`, and `post_freeze_findings` are empty and `revised_provisional_meta_review` is absent. In a later awaiting round, preserve all real prior-round records, append the new batch, create no response-dependent record for the pending question, and stop;
- `completed`: at least one actual author response and its response-linked re-evaluation are present, and `revised_provisional_meta_review` is present.

For `venue_rebuttal_simulation`, include `venue_rebuttal_rules`: `venue`, `year`, `track`, `paper_type`, `stage`, `verified_at`, `official_source_locators`, `external_check_ids`, `length_rule`, `scope_rule`, `link_rule`, `anonymity_rule`, `new_evidence_rule`, and `round_rule`. Require one or more `official_source_locators` entries, each formatted as an absolute HTTP(S) URL or DOI. For every linked `X-*` check, require a purpose explicitly covering venue, rebuttal, or author-response rules/policy/instructions and an exact locator shared by that check's `source_locators` and `official_source_locators`. Omit `venue_rebuttal_rules` for `internal_clarification` and do not present an internal limit as an official venue constraint.

The machine-readable interaction log keeps these exact collections separate:

- `evidence_artifacts`: hashed post-freeze response text, attachments, analyses, results, or revised manuscripts used as evidence;
- `question_batches`: round-scoped questions plus `issued_at`, a nonempty `rationale`, disclosure mode, new-evidence policy, and treatment;
- `author_responses`: only responses the author actually supplied, with `received_at`, reviewer-assigned answer classes, and evidence links;
- `re_evaluations`: appended finding re-evaluations with `evaluator_reviewer_id` that preserve the frozen finding history;
- `post_freeze_findings`: genuinely new response-revealed concerns, assigned `PF-*` IDs and never inserted into the frozen `findings` collection.

| Finding | Prior status | Decision-relevant question | Reviewer-assigned answer class | Answer/evidence summary and hashed evidence IDs | External disclosure limit | Manuscript availability | Reviewer re-evaluation | Updated status | Required next action |
|---|---|---|---|---|---|---|---|---|---|

Allowed answer classes: `already_supported_clarification`, `new_unpublished_evidence`, `planned_revision`, `concession_or_scope_narrowing`, `disagreement`, `cannot_answer`.

Allowed updated statuses: `resolved_in_manuscript`, `clarified_but_missing_from_manuscript`, `new_evidence_requires_inclusion`, `planned`, `conceded`, `disputed`, `unresolved`.

Record each `post_freeze_findings` item with `origin.label: new_in_rebuttal`, originating round and answered question, `reviewer_id`, nullable `verifier_id`, `verification_status`, nullable `verified_severity`, `checked_evidence`, nullable `verification_performed_at`, nullable `verification_report_sha256`, `verification_rationale`, category, severity, confidence, `conditional`, lifecycle `status` (`open`, `resolved`, or `withdrawn`), observation, `rationale_not_in_initial_review`, linked response evidence IDs, and linked initial finding IDs.

Use the exact state contract:

- `not_required`, `confirmed`, `downgraded`, and `unresolved` require lifecycle `open`; `resolved` requires lifecycle `resolved`; `withdrawn` requires lifecycle `withdrawn`.
- `confirmed` preserves the declared severity; `downgraded` records a strictly lower `verified_severity`; `not_required`, `resolved`, `withdrawn`, and `unresolved` use `verified_severity: null`.
- `not_required` uses a null verifier/time/hash and `checked_evidence: false`. Every other verification status requires a distinct verifier, `checked_evidence: true`, an interaction-specific completion time strictly after the triggering response and linked evidence, and a report hash different from that verifier's pre-interaction report hash. Critical findings additionally require the sealed `critical_verifier` role.
- `withdrawn` uses only `withdrawn_after_verification`; `resolved` uses only `affects_provisional_recommendation` or `documented_no_recommendation_change`; `open` cannot use the withdrawn treatment; and `unresolved` verification cannot use `affects_provisional_recommendation`.

In a completed interaction, provide a revised provisional meta-review that identifies which `re_evaluations` and `PF-*` concerns affect the recommendation, which hashed post-freeze evidence it depends on, and which explanations would still be unavailable to real reviewers. In `post_freeze_finding_treatments`, give every `PF-*` concern exactly one compatible treatment with a rationale. An effective Critical `PF-*` concern blocks an accepting recommendation unless valid interaction verification downgrades, resolves, or withdraws it. Do not create a meta-review on the first `awaiting_author_response` turn; a later awaiting round may preserve an earlier completed meta-review but must not update it for a pending question. Never classify an answer until the author has supplied it or fabricate missing responses.

State the updated assessment's assurance separately. Initial reviewer seals and root assurance cover the frozen reports only; do not describe the response-stage work as `cross_model_advisory` or `human_panel` unless interaction participants and seals were separately recorded and validated.

## Final consistency gate

Before delivery, verify:

- every structured finding records `conditional` and lifecycle `status`;
- every Critical or Major finding has an evidence anchor, consequence, repair, and verification test;
- every `PF-*` lifecycle, verification outcome, verified severity, treatment, interaction-specific time, and report hash obeys the post-freeze state contract;
- every formal rebuttal rules snapshot has an official absolute HTTP(S)/DOI locator, precedes the first batch, and exactly links any declared external check;
- every material fast-reader breakpoint has a concrete meaning-preserving revision suggestion and cold-read test;
- venue-policy and current-fact findings cite dated official or primary sources or remain unverified;
- no recommendation contradicts an unresolved verified Critical finding;
- claim, threat-model, experiment, figure, and artifact mappings agree;
- the report distinguishes inaccessible material from absent material;
- strengths, no-issue-found results, dissent, expertise limits, and confidence remain visible;
- the referee report does not expose internal orchestration or become an author editing memo;
- the author annex does not silently modify the manuscript;
- structural validation is not described as proof of scientific correctness.
