# Author style-contract protocol

Use this protocol only when the proposer supplies a narrative guide, house style, revision checklist, canonical design, or other author-authored writing authority. Treat it as an optional review input, never as NSF policy or independent evidence that the proposal communicates successfully.

## Contents

1. Applicability and precedence
2. Rule classification
3. Two-pass review boundary
4. Paragraph-level diagnostic
5. Scientific-integrity guardrails
6. Author-facing output

## Applicability and precedence

Hash-pin the guide as a `supporting` packet file. Record:

- title, source, date, and reviewed hash;
- proposal version or section for which it was written;
- whether the author declares it `current`, `advisory`, `stale`, or `superseded`;
- whether it governs the whole package or named sections only; and
- unresolved conflicts with the current proposal, solicitation, or scientific design.

If applicability is not stated, infer only obvious version links and mark the rest `open_question`. A guide derived from an older draft is not automatically binding on a new draft.

Use this precedence order:

1. exact solicitation and current NSF policy for requirements;
2. scientific accuracy, evidence, and internal consistency;
3. current proposal design and author-confirmed claims;
4. current author style contract;
5. general writing heuristics.

A style rule cannot override policy, hide a scientific defect, strengthen a claim beyond its evidence, or erase a necessary scope condition.

## Rule classification

Classify each material guide rule before applying it:

| Class | Meaning | Review treatment |
|---|---|---|
| `transferable_principle` | Broad communication principle such as claim-before-formalism or stable terminology | Apply as a general readability diagnostic |
| `author_house_style` | Chosen syntax, punctuation, voice, or rhetorical preference | Report compliance separately; no merit penalty unless comprehension or professionalism is affected |
| `proposal_strategy` | Project-specific narrative order, example, terminology, or contribution hierarchy | Apply only to the named proposal/version and verify that it remains scientifically accurate |
| `version_constraint` | Page budget, section layout, current figure/table allocation, or revision-specific limitation | Recheck against the rendered current version before enforcing |
| `scientific_assertion` | Claim about prior work, mechanisms, systems, evidence, or expected effects embedded in a writing example | Verify like any proposal claim; do not inherit it as style guidance |

When one rule spans classes, split it. For example, “state the claim directly and never use an em dash” contains a transferable directness principle and an author house-style prohibition.

## Two-pass review boundary

Protect the cold-read test from author-intent leakage.

### Pass A: proposal-only reconstruction

Give holistic reviewers and the first presentation pass only the raw proposal, verified authority, and neutral metadata. Do not show the style guide, canonical intended argument, before/after examples, prior audit, or executor summary.

Freeze:

- the one-read reconstruction;
- the first comprehension breakpoint;
- first-page/section narrative results;
- terminology first-use failures; and
- accessibility and technical-integrity assessments.

### Pass B: contract-aware editorial audit

After Pass A is frozen, give the presentation auditor the guide and its applicability record. Compare the proposal with the author’s intended style without rewriting the cold-read result.

Report separately:

- communication defects independently observed in Pass A;
- author-contract violations that also affect reviewer comprehension;
- house-style-only deviations;
- stale, contradictory, or scientifically unsafe guide rules; and
- places where the proposal is clearer or more accurate than the guide.

The chair may use Pass B to recommend revisions but must not retroactively treat author intent as evidence that Pass A readers should have understood the proposal.

## Paragraph-level diagnostic

Audit only the passages with the highest likely effect on panel reconstruction or confidence. Default to 10–15 entries, not an exhaustive copyedit.

For each entry record:

| Field | Test |
|---|---|
| Location | Exact page, section, paragraph, figure, or table |
| Paragraph job | One primary function: problem, gap, insight, aim, method, evaluation, risk, payoff, impact, or transition |
| First-sentence result | Does the first sentence expose that job and the reviewer-visible decision? |
| Referent or scene | Can a broad reader picture the mechanism, consequence, and relevant difference? |
| Motivation/method boundary | Does formal machinery appear before the question and payoff are clear? |
| Rule load | How many gates, thresholds, exceptions, or frozen choices compete in the passage? |
| Table/prose allocation | Does prose interpret a table or merely repeat it? Is the table itself readable and self-contained? |
| Central-object definition | For the load-bearing object: what is it, what is it given, what does it do or optimize, and what bounds it? |
| Science/artifact distinction | Is the knowledge contribution visible above software, datasets, models, and testbeds? |
| Claim calibration | Are qualifications necessary and proportionate, or is the prose evasive or overbroad? |
| Repair and space effect | Minimal safe repair; expected page effect `negative`, `neutral`, `positive`, or `unknown` |

Treat “more than two or three rules in one paragraph” as a diagnostic trigger, not a universal failure threshold. Dense formal detail can be appropriate after a plain claim-to-decision bridge.

## Scientific-integrity guardrails

- Prefer `claim first, proportionate qualification nearby` over a blanket rule to remove hedging.
- Distinguish necessary uncertainty and boundary conditions from throat-clearing or evasive qualification.
- Do not recommend a vivid example unless its mechanism, harm, and contrast are supported or clearly labeled hypothetical.
- Do not convert a bounded claim into `only`, `always`, `trustworthy only when`, `general`, or another stronger assertion merely to sound direct.
- Do not move a defective decision rule into a table and call the problem solved. Narrative delegation changes placement, not scientific validity.
- Do not require a specific analogy, example, heading order, punctuation choice, or rhetorical template unless the current author contract controls it.
- Preserve specialist detail that is necessary and correctly placed. Accessibility means a broad reader can locate its purpose; it does not require deleting all formalism.

## Author-facing output

In `presentation-audit.md`, add a `Style-contract applicability` section and a bounded `Paragraph diagnostics` table when a guide is supplied. Separate findings into:

1. `panel_communication`: independently affects comprehension, navigation, or confidence;
2. `scientific_precision`: wording exposes or introduces a technical defect;
3. `author_contract`: violates a current author rule but has no demonstrated merit effect; and
4. `stale_or_unsafe_guidance`: the supplied rule is outdated, contradictory, or would weaken accuracy.

Rank panel-communication and scientific-precision findings by decision impact. Put house-style-only deviations in a compact appendix and do not let their count dominate the mock rating.

For every proposed repair, state whether it is a reordering, gloss, terminology alignment, table delegation, page reallocation, prose clarification, new analysis/evidence, or study redesign. A style fix never substitutes for the latter three.
