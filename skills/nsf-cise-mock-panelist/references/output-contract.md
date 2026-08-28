# Output contract

Use Markdown for human review and JSON for deterministic checking. The JSON schemas in `assets/` define the machine-readable shape.

## Contents

- Directory layout
- Individual review Markdown
- Finding object
- Specialist audit contract
- Append-only issue ledger
- Panel summary Markdown
- Revision priority

## Directory layout

```text
mock-panel/
  packet-manifest.json
  authority-snapshot.md
  compliance-screen.md
  review-r1.md
  review-r1.json
  review-r2.md
  review-r2.json
  review-r3.md
  review-r3.json
  novelty-audit.md
  methods-audit.md
  broader-impacts-audit.md
  presentation-audit.md
  kill-argument.md
  kill-adjudication.md
  issue-ledger.jsonl
  pre-deliberation-validation.json
  panel-aggregate.json
  panel-summary.md
  panel-summary.json
  review-quality-audit.md
  human-calibration-record.json  # optional; only after a real held-out evaluation
  run-artifact-manifest.json
  validation-report.json
  revision-priorities.md
  traces/
```

## Individual review Markdown

Use this order:

1. proposal/version, reviewer background card, limitations, and independence disclosure;
2. one-sentence synopsis;
3. cold-read argument reconstruction and first comprehension breakpoint;
4. overall rating and confidence;
5. Intellectual Merit strengths and weaknesses;
6. Broader Impacts strengths and weaknesses;
7. writing and general-CS accessibility;
8. technical depth, precision, and integrity;
9. additional solicitation criteria;
10. remaining rubric-dimension findings;
11. questions for panel discussion;
12. prioritized revisions;
13. uncertainty, conflicts, and sources checked.

Avoid a long proposal summary. Cite proposal locations for every material comment.

The reviewer background card is a simulated perspective, not a claim about a real person and not evidence of model independence. In a full panel, the profile IDs must be exactly `general_cs`, `adjacent_cise`, and `domain_methods`, one each. Every reviewer remains holistic.

`reviewer_route` records the unique execution route and the provenance of the model-family label. `runtime_metadata` means the runtime supplied the route/model facts; `human_attestation` means a responsible human checked them against runtime records; `self_reported` and `unavailable` are not independent route evidence. Multi-family assurance requires trusted route provenance, distinct route IDs, consistent model-to-family mapping, and genuine family diversity. A simulated background never counts toward this assurance.

The cold-read reconstruction must be written from the proposal before consulting external explanations, author explanations, style guides, narrative guides, before/after examples, or prior reviews. Freeze it before any contract-aware editorial pass. It is the single authoritative record of the problem, gap, central idea, aims, decisive tests, expected knowledge, and first point of breakdown. If no breakdown is found, say so explicitly. `dimensions.general_cs_accessibility.assessment` is the authoritative accessibility verdict, and `dimensions.technical_precision_integrity.assessment` is the authoritative depth/integrity verdict. The dedicated sections hold evidence-linked findings and audit notes; do not duplicate the verdicts there.

The JSON `rating` is the sealed individual rating. If a reviewer changes position during bounded deliberation, preserve the sealed value and append a `rating_changed` event to `issue-ledger.jsonl`; do not edit the original review.

## Finding object

```json
{
  "id": "R1-IM-W01",
  "issue_key": "evaluation.missing_decisive_baseline",
  "severity": "major",
  "stance": "weakness",
  "criterion_group": "intellectual_merit",
  "audiences_affected": ["general_cs", "domain_or_methods_specialist"],
  "impact_types": ["scientific_validity", "reviewer_confidence"],
  "location": "Project Description p. 8, Evaluation",
  "claim": "The evaluation cannot isolate the claimed mechanism from scale.",
  "plain_panel_concern": "The proposed comparison cannot show whether the new mechanism, rather than a larger model, caused the gain.",
  "technical_basis": "The only comparator changes both parameter count and mechanism, so the mechanism effect is not identifiable.",
  "evidence": [
    {"source": "proposal.pdf", "location": "p. 8", "note": "Only the larger model is compared."}
  ],
  "criterion": "Intellectual Merit - sound plan and mechanism to assess success",
  "rationale": "A gain could be explained by model size rather than the proposed method.",
  "consequence": "Reduces confidence in Aim 2's central inference.",
  "action": "Add a parameter-matched baseline and predefine the discriminating analysis.",
  "revision_type": "study_redesign",
  "epistemic_status": "verified"
}
```

Use stable `issue_key` values so deterministic aggregation can identify recurrence. Do not force semantically distinct findings under the same key.

Use `criterion_group: presentation` for accessibility, terminology, organization, figures, and professional writing findings. Use `criterion_group: technical_integrity` for equation/prose mismatches, symbols, units, arithmetic, thresholds, denominators, cross-artifact inconsistencies, and other technical quality-control findings. A technical-integrity finding may also affect Intellectual Merit, but it is linked to Intellectual Merit through its consequence and rubric dimensions rather than relabeled.

Use `revision_type: preserve_or_reinforce` for strengths. For weaknesses, choose the smallest honest repair class: `copyedit`, `prose_clarification`, `reorganization`, `terminology_alignment`, `figure_revision`, `new_analysis`, `new_evidence`, `study_redesign`, `institutional_confirmation`, or `policy_verification`. Do not describe a missing experiment as a prose fix.

## Specialist audit contract

Every audit begins with scope, inputs and hashes, reviewer route/family, authorization boundary, and non-assessed areas. Findings use the same location/evidence/reason/consequence/action contract as individual reviews. Specialist audits are advisory evidence and do not contain a panel rating.

`presentation-audit.md` includes two clearly separated parts:

1. **Pass A - proposal-only audit:** the frozen general-CS cold read, 20-second and first-page tests, first-breakpoint analysis, progressive-exposition map, terminology ledger, scene and deep-example discipline, rendered-page and figure checks, consistency checks, and professional copy-quality sweep.
2. **Pass B - contract-aware audit, only when an author-supplied guide is present:** the guide hash and applicability state, its rule classifications, and proposal-grounded findings that show whether a guide violation creates panel communication cost, scientific-precision risk, author-house-style drift, or only stale/inapplicable guidance.

For the 10-15 highest-leverage paragraphs, add a compact diagnostic table with location, paragraph job, first-sentence claim, scene or concrete referent, motivation/method separation, terminology or rule load, prose-versus-table allocation, central-object completeness, science-versus-artifact emphasis, claim calibration, smallest repair, expected decision effect, and estimated space effect. Do not turn this into line editing of every paragraph.

Author-house-style-only deviations receive editorial notes but no merit or rating penalty unless the audit demonstrates an effect on comprehension, precision, evidentiary support, or reviewer confidence. A guide cannot justify deleting necessary assumptions or qualification, strengthening a claim beyond its evidence, moving scientific logic into an unreadable table, or masking a method/evaluation defect as a narrative repair.

`methods-audit.md` includes the specialist-depth gate plus a technical-integrity sweep of equations, symbols, units, counts, denominators, thresholds, margins, sample or power logic, statistical choices, threat model, tables/figures, schedule, resources, and cross-references.

The kill argument contains one dominant adverse case, its necessary premises, evidence anchors, and what evidence would defeat it. The adjudication addresses every premise and must not silently introduce a second attack.

## Append-only issue ledger

Write one JSON object per line. Required fields are:

```json
{
  "timestamp": "2026-07-20T18:00:00Z",
  "proposal_hash": "sha256:...",
  "actor": "chair-01",
  "finding_id": "R1-IM-W01",
  "event": "disputed",
  "prior_state": "open",
  "new_state": "under_adjudication",
  "evidence": [{"source": "proposal.pdf", "location": "p. 8"}],
  "reason": "R2 identifies a parameter-matched baseline in Appendix A."
}
```

Allowed lifecycle events are `created`, `corroborated`, `disputed`, `resolved`, `partially_resolved`, `unresolved`, `superseded`, `reopened`, `regressed`, `not_comparable`, `rating_changed`, and `chair_claim_verified`. Never delete or rewrite earlier lines.

Every review finding must begin with `created: absent -> open`; later events must continue from the prior recorded state. Use `not_comparable` when two frozen versions cannot support a defensible resolution comparison. Use the special ID `rating:<reviewer-id>` for a rating change, with states exactly matching the panel summary's sealed `initial` and final `revised` values. Give every chair-introduced claim a stable ID and use that ID for `chair_claim_verified: unverified -> verified|qualified|rejected|unresolved`, with the new state exactly matching the panel claim's verification status. Unknown IDs, state jumps, missing evidence anchors, decreasing timestamps, or contradictory panel/ledger histories are validation failures.

## Panel summary Markdown

Use:

- brief synopsis;
- internal mock disposition and confidence;
- Intellectual Merit consensus strengths;
- Intellectual Merit consensus weaknesses;
- Broader Impacts consensus strengths;
- Broader Impacts consensus weaknesses;
- writing and general-CS accessibility, including any background-specific disagreement;
- technical depth, precision, and integrity;
- additional criteria;
- material disagreements and minority views;
- conditions that would change the assessment;
- prioritized revision plan;
- assurance and limitations.

Do not paste or concatenate individual reviews. Synthesize the discussion while preserving attribution by reviewer ID.

Write the panel summary plain-first. Define any specialist term used by the panel, and do not reproduce opaque proposal language as the explanation. Accessibility and technical-integrity sections must cite at least one sealed strength or weakness finding; a clean proposal may use strength-only coverage.

The machine-readable summary records the chair model/family, unique route ID, route-provenance source and basis, hashes of every frozen review, confidence, any rating changes, and any claim first introduced by the chair. A post-chair checker verifies the latter against raw evidence. The chair route must be distinct from all sealed-review routes.

Every disagreement in `panel-aggregate.json.disagreements_requiring_chair_review` must appear in `panel-summary.json.disagreements` with the same `topic_key` and `kind`, evidence checked, resolution, and a nonempty minority-view statement. The chair may add `chair_identified` disagreements but may not suppress mechanically detected rating, dimension, stance, or severity conflicts.

The chair's `assurance_label` is a requested output field, not accepted evidence. The validator derives the permissible value from reviewer-family and trusted route metadata plus any validated calibration record. `human_calibrated_advisory` requires the schema in `assets/human-calibration-record.schema.json`, the exact current protocol-bundle hash, every participating family and exact model identifier, the recorded three-independent-reviewers-plus-fresh-chair topology, a deidentified authorized held-out calibration set, independent qualified-human anchors, the required metrics, and a versioned threshold profile whose thresholds are actually met. Compute the canonical digest with `python3 <skill-dir>/scripts/protocol_digest.py`. Do not create this record merely because a person glanced at one review.

For scoped-only `section-review`, `editorial-audit`, or `revision-check`, use Markdown and state that holistic JSON validation is `not_applicable`. Do not create schema-valid-looking placeholders for criteria that were outside scope.

The packet and run manifests retain absolute origin paths. A ZIP checksum can verify that a shared archive is byte-identical, but the internal validator is path-bound to the origin run. Extraction elsewhere requires a new packet/run identity and regenerated dependent hashes; it is not a continuation of the original validated run.

## Revision priority

For each revision include finding IDs, expected decision impact, exact target section, evidence needed, owner, verification test, and estimated page-space effect. Distinguish a prose clarification or narrative reorganization from new analysis, new preliminary evidence, redesign, institutional confirmation, or policy verification. Never present a narrative repair as sufficient when the scientific claim, design, or evidence remains defective.

For revision comparison, store both packet hashes and the raw diff. Use `resolved`, `partially_resolved`, `unresolved`, `regressed`, or `not_comparable`; a changed sentence is not proof that the underlying issue was fixed.
