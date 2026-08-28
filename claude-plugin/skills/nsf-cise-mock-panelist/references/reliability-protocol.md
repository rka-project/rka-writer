# Reliability protocol

The goal is not maximal reviewer volume. It is inspectable judgment with independent evidence paths, explicit uncertainty, and failure detection.

## Contents

- Independence sequence
- Evidence discipline
- Bias controls
- Panel deliberation
- Review-quality audit
- Trace and freshness
- Calibration and regression evaluation
- Validation status and semantic assurance

## Independence sequence

1. Freeze and hash the proposal packet.
2. Give each reviewer the raw artifacts, criteria, output schema, and exactly one bounded profile: `general_cs`, `adjacent_cise`, or `domain_methods`.
3. Require a proposal-only cold-read reconstruction before outside explanation, author narrative/style guidance, before/after examples, or other review material; freeze the result.
4. Prevent access to other reviews until individual reviews are frozen.
5. Require every reviewer to complete the whole review; complementary expertise is not criterion ownership.
6. Record simulated profile and limitations separately from model, family, context route, route-provenance source, confidence, conflicts, and files reviewed.
7. Run non-voting novelty, methods, Broader Impacts, presentation, and compliance audits against raw artifacts.
8. Reveal frozen reviews and audits to the chair only during deliberation.
9. Preserve initial and revised ratings with reasons; never overwrite the history.

Fresh context reduces anchoring but does not create cross-family independence. Same-family reviews remain `provisional_advisory` even when they agree. So do routes whose family labels are merely self-reported or unavailable.

An author-supplied style or narrative guide is supporting material, not reviewer evidence. Hash-pin it, record its scope/version and applicability state, and withhold it from sealed reviewers and the proposal-only presentation cold read. Reveal it only for the second editorial pass. Compare Pass B with frozen Pass A so author intent cannot rewrite the record of what the proposal itself communicated.

The three simulated backgrounds diversify attention; they are not real reviewer identities and do not make model outputs independent. Validator profile coverage is a workflow guarantee, not proof that the model adopted the perspective faithfully.

Do not use number of agents as a proxy for reliability. Agreement among agents sharing a model family, prompt, retrieval path, or mistaken premise is correlated evidence.

## Evidence discipline

Every substantive review comment must be:

- `proposal_grounded`: cites a page, section, paragraph, figure, table, or line;
- `literature_grounded`: cites verified external work;
- `policy_grounded`: cites live authoritative language;
- `inference`: explains the reasoning and uncertainty;
- `open_question`: identifies missing information without treating absence as failure.

Generic praise and criticism are review defects. Evidence existence can be checked deterministically; correctness of interpretation remains semantic.

## Bias controls

- Apply the same rubric and anchors before reading the proposal.
- Ignore prestige, fame, writing accent, and demographic cues except where team qualifications are substantively evidenced.
- Require a devil's-advocate pass against the reviewer's initial recommendation.
- Compare the severity assigned to similar issues within the same review.
- Do not let one vivid weakness erase unrelated strengths.
- Preserve minority views and confidence differences.
- Do not infer missing expertise, access, or commitments without checking the package.
- Do not assign demographic traits, institutions, prestige, or personal histories to simulated reviewers.
- Do not let the specialist's fluency excuse an accessibility failure or the generalist's comfort excuse missing technical detail.
- Do not convert an author-house-style preference into an NSF criterion or merit penalty without a demonstrated effect on comprehension, precision, evidence, or reviewer confidence.
- Do not let a clarity-oriented rewrite erase scientifically necessary scope, assumptions, uncertainty, limitations, or null-result conditions.

## Panel deliberation

Do not average away disagreement. Build a table containing topic, reviewer positions, cited evidence, whether the dispute is factual or judgmental, resolution, and minority view. Resolve factual disputes from primary artifacts. Leave judgmental disputes explicit.

The chair synthesizes; it does not invent portfolio priorities or declare an award decision. The overall assessment must identify the few considerations that dominate the panel judgment.

Use a bounded sequence:

1. sealed reviews;
2. private reflection against specialist-audit evidence;
3. at most two evidence-specific replies per material dispute;
4. blind chair synthesis using reviewer IDs rather than identities;
5. post-chair verification of blocker/major and chair-introduced claims.

Before deliberation, run a `kill argument`: the strongest compact case that a skeptical panelist could make against enthusiasm. A separate adjudicator must test every premise against the raw packet. This catches central failure modes without allowing a red-team narrative to anchor the chair unchallenged.

## Review-quality audit

Decompose each review into atomic comments. For each, test:

- specificity;
- proposal or literature grounding;
- justification;
- correct severity;
- actionable next step;
- professional, neutral tone;
- plain-first explanation followed by the precise technical basis;
- correct audience affected and honest revision type;
- a proposal-specific verification test rather than generic “clarify” advice;
- correct separation of proposal-only diagnosis from contract-aware diagnosis;
- correct classification of supplied-guide rules as transferable principle, author house style, proposal strategy, version constraint, or scientific assertion;
- preservation of necessary technical qualification and evidentiary boundaries in the proposed repair;
- consistency with the overall rating.

Flag comments that merely restate the proposal, ask for unlimited extra work, impose non-solicitation criteria, enforce house style as universal merit, strengthen claims beyond evidence, hide scientific logic in tables, or recommend a different project instead of evaluating the proposed one.

## Trace and freshness

Store local traces containing prompts, responses, model route, timestamps, and file hashes unless the user requests metadata-only or no tracing. For every author-supplied guide, also record its hash, stated version/scope, applicability state (`current`, `advisory`, `stale`, or `superseded`), and the point at which it became visible to the editorial reviewer. Keep traces out of version control. Recompute hashes before relying on any review. A review of an older proposal version is stale even if the filename is unchanged.

Maintain an append-only issue ledger. Each event records timestamp, proposal hash, actor/route, finding ID, action, prior state, new state, evidence anchors, and reason. For revision checks, pass the raw old version, raw new version, and their diff to a fresh adjudicator; never rely only on an executor's repair summary.

## Calibration and regression evaluation

Operational reliability must be measured on material the organization is authorized to use. Build a deidentified calibration set of historical drafts with qualified-human annotations, keep a held-out evaluation split, and report:

- criterion coverage and location-anchor accuracy;
- precision/recall for known major weaknesses and false-positive rate on clean controls;
- weighted agreement on rating bands, with confidence intervals where sample size allows;
- review stability across harmless paraphrase, document order, reviewer order, and repeated runs;
- novelty-source validity and support/contradiction classification accuracy;
- percentage of blocker/major claims surviving independent adjudication;
- usefulness and professionalism rated blind by qualified proposal writers or former panelists.

Include injected-defect cases: fabricated citation; novelty contradicted by prior work; dependent aims; absent decisive baseline; unsupported preliminary claim; generic Broader Impacts; contradictory timeline; missing risk/alternative; jargon-dense but potentially sound passages; clear but technically shallow passages; undefined or inconsistent terminology; mechanism overclaim; unit or throughput arithmetic errors; deep examples presented before the general claim; vivid examples with no bridge to the general claim; rule dumps that duplicate tables; fuzzy central objects; motivation/method collapse; science displaced by artifact description; scope overclaim; appropriate qualification falsely labeled as hedging; clarity rewrites that overclaim; house-style-only deviations; stale style contracts; correctly staged specialist detail; and clean controls. Synthetic forward tests are regression probes, not human calibration. Keep all target thresholds versioned in a local calibration profile; do not invent universal pass thresholds.

Re-run the suite after changing prompts, model routes, schemas, retrieval, rating anchors, or aggregation logic. Tool schema tests establish plumbing, not reviewer validity.

## Validation status and semantic assurance

Deterministic validation reports `PASS`, `WARN`, or `FAIL` for schema, coverage, provenance, freshness, and artifact completeness. A conflict, missing packet, stale hash, unverified criterion, or failed required review produces a failed/blocked run rather than a panel assurance label.

Semantic advisory labels are:

- `provisional_advisory`: semantic review was same-family, single-context, or lacked trusted route provenance.
- `multi_family_advisory`: at least two genuine model families independently reviewed raw artifacts, with distinct routes and runtime-recorded or human-attested route provenance.
- `human_calibrated_advisory`: a validated, versioned calibration record covers the exact protocol-bundle hash, participating families and exact model identifiers, and the current independent-reviewer/chair route topology, and shows that held-out evaluation against qualified-human anchors met locally defined thresholds. A person merely reading one output does not establish calibration.

The validator derives the applicable label from run evidence; a reviewer or chair cannot self-declare it. The skill's regression tests currently establish deterministic plumbing only. Until an authorized human-anchored calibration set is run, semantic agreement with qualified CISE panelists is unproven.

No label means official, correct, submission-ready, or likely to be funded.
