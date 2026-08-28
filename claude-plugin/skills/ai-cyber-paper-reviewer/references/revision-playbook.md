# Revision Playbook

Use this playbook to convert review findings into author-facing repair advice for AI and cybersecurity papers. Keep the submitted manuscript read-only. Examples are proposals for the author, not permission to edit manuscript files.

## Contents

1. [Priority order](#priority-order)
2. [Claim calibration](#claim-calibration-workflow)
3. [Experiment planning](#experiment-planning-template)
4. [Decisive experiments](#common-decisive-experiments)
5. [Figure and table patterns](#figure-and-table-revision-patterns)
6. [Fast-reader presentation repair](#fast-reader-presentation-repair)
7. [Wording patterns](#revision-wording-patterns)
8. [Interactive review and rebuttal](#interactive-review-and-rebuttal-use)

## Priority Order

Fix issues in this order:

1. Correctness: arithmetic errors, inconsistent metrics, unsupported claims, fake citations, contradictory assumptions.
2. Core framing: problem statement, threat model, contribution, novelty, venue fit.
3. Design clarity: architecture, algorithms, trust boundaries, TCB, assumptions, failure modes.
4. Evaluation validity: baselines, ablations, metrics, statistics, benchmarks, reproducibility.
5. Interpretation: claim calibration, limitations, failure analysis, external validity.
6. Presentation: figures, tables, captions, section organization.
7. Prose polish: clarity, concision, terminology consistency, citation formatting.

## Claim Calibration Workflow

For each major claim, write:

1. Current claim.
2. Evidence supporting it.
3. Evidence missing.
4. Safe claim if no new work is added.
5. Stronger claim if the proposed experiment or analysis is added.

Template:

| Current claim | Current evidence | Risk | Safe revision | Stronger revision after added evidence |
|---|---|---|---|---|

## Experiment Planning Template

Use this when a review concern can be answered with a feasible additional experiment.

### Experiment: [name]

- Reviewer concern:
- Research question:
- Hypothesis:
- Dataset or benchmark:
- Task subset and why it is sufficient:
- Models or systems:
- Baselines:
- Ablations:
- Metrics:
- Number of runs or repetitions:
- Statistical unit:
- Confidence interval or test:
- Expected table or figure:
- Claim this can support:
- Claim this cannot support:
- If time is limited, minimal version:

## Common Decisive Experiments

### Baseline-strengthening experiment

Use when reviewers may say the baseline is weak.

Design:

- Add the closest prior system or strongest obvious heuristic.
- Match access to data, oracle knowledge, tuning budget, and compute.
- Report performance, utility, cost, and failure modes.

### Ablation experiment

Use when reviewers may say the proposed component is not load-bearing.

Design:

| Configuration | Purpose |
|---|---|
| full system | target performance |
| no core component | tests whether component matters |
| simple component | tests whether complexity matters |
| policy/rule/model-only baseline | tests whether the design is more than baseline capability |
| conservative upper/lower bound | shows tradeoff limits |

### Sensitivity experiment

Use when a result depends on a threshold, model, prompt, dataset, or attack strength.

Report:

- x-axis: parameter or setting;
- y-axis: security metric and utility metric;
- interpretation: stability region and failure region.

### External benchmark experiment

Use when reviewers may say the benchmark is too controlled.

Design:

- Choose one public benchmark or dataset aligned with the claim.
- State how tasks, tools, labels, or metrics are mapped.
- Freeze mapping rules before reporting results when possible.
- Report negative or mixed results as limitations, not failures to hide.

### Failure-analysis experiment

Use when aggregate numbers hide residual risk.

Design:

- Cluster failures by mechanism, data source, attack class, model, scenario, or tool type.
- Provide representative examples.
- Explain whether each failure is due to model behavior, policy/design gap, implementation bug, metric limitation, or benchmark ambiguity.

### Statistical robustness analysis

Use when repeated trials are not independent.

Options:

- scenario-level bootstrap;
- clustered bootstrap by scenario, user, model, app, or dataset;
- mixed-effects regression;
- per-scenario success rate table;
- confidence intervals over the correct unit of analysis.

## Figure and Table Revision Patterns

### Architecture figure

Include:

- actors;
- trusted and untrusted inputs;
- system components;
- data flow;
- control flow;
- trust boundaries;
- enforcement or decision points;
- outputs and logged state.

### Threat model table

| Entity | Trusted? | Attacker capability | Excluded capability | Rationale |
|---|---|---|---|---|

### Trial-accounting table

Use when evaluation includes multiple models, datasets, systems, repetitions, or task classes.

| Evaluation | Models | Scenarios/tasks | Repetitions | Systems | Total trials | Main metric |
|---|---:|---:|---:|---:|---:|---|

### Results table

Include denominators and uncertainty.

| Method | Security metric | Utility metric | Cost/overhead | 95% CI | Notes |
|---|---:|---:|---:|---:|---|

### Failure taxonomy table

| Failure class | Count | Example | Root cause | Fix or limitation |
|---|---:|---|---|---|

## Fast-Reader Presentation Repair

For each cognitive-load finding, start from the reader failure rather than a generic request to “improve clarity”:

1. Record `conditional` (`true` or `false`) and lifecycle `status` (`open`, `resolved`, or `withdrawn`).
2. Quote or locate the exact breakpoint.
3. State the rushed reviewer's likely reconstruction.
4. State the intended technical meaning.
5. Identify the working-memory burden: missing prerequisite, delayed definition, terminology drift, too many actors or symbols, mechanism before purpose, claim after evidence, or weak navigation.
6. Choose the smallest repair that changes the reading path.
7. Protect the assumption, scope, and technical distinction that must not be lost.
8. Re-run the 30-second or three-minute reconstruction with a fresh reader.

Useful repair patterns:

- **Purpose before mechanism:** add or move one sentence that states input, decision, output, and security consequence before component details.
- **Invariant before example:** explain the general property first; keep the niche example as evidence, not as the reader's only route to the idea.
- **Definition at first use:** move the existing definition and use one stable label thereafter.
- **One paragraph, one job:** split background, gap, design, and evidence into separately signposted moves.
- **Claim before table:** precede a dense result table with the question and expected comparison; make the caption state the supported takeaway and boundary.
- **Overview before internals:** use an overview figure that identifies actors, trust boundaries, data/control flow, decision point, and output before algorithmic details.
- **Qualification near claim:** place the most decision-relevant scope limit where the claim first appears, not only in limitations.

Illustrative wording is optional. Never prescribe a polished sentence without checking that it preserves technical meaning and evidentiary strength.

## Revision Wording Patterns

### Abstract

Good abstract structure:

1. Concrete problem and why existing approaches fail.
2. Proposed method in one sentence.
3. Core design mechanism.
4. Main evaluation evidence with denominators.
5. Calibrated implication and limitation.

Avoid cramming every number into the abstract. Report the two or three numbers that prove the main claim.

### Introduction

Good introduction structure:

1. Concrete security/AI problem.
2. Why current methods or assumptions break.
3. Key insight.
4. System/method overview.
5. Evidence summary.
6. Contributions.

### Contributions

Write contributions as claims, not activities.

Weak:

- We implement a system.
- We evaluate on a dataset.

Better:

- We introduce [mechanism] that enables [security/AI capability] under [assumption].
- We show through [evaluation] that [effect] holds against [baseline] on [scope].

### Limitations

Limitations should be precise and non-defensive:

- Where the method works best.
- Where it fails.
- Which assumptions are required.
- Which deployment settings are not covered.
- Which benchmarks or attacks were not evaluated.
- Which future work is needed to remove the limitation.

## Interactive Review and Rebuttal Use

Use `interactive-review-protocol.md` when the author wants to clarify missing information, challenge a finding, or prepare for rebuttal. Preserve the original manuscript-only finding before considering an answer.

If the user is responding to reviewer comments:

1. Convert each reviewer comment into a concern.
2. Identify whether the answer is a manuscript-supported clarification, new evidence, planned revision, concession/scope narrowing, disagreement, or inability to answer.
3. Distinguish `resolved in the manuscript` from `clarified in conversation but still missing from the manuscript`.
4. For each concern, draft a concise response:
   - thank the reviewer;
   - state what was changed or will be changed;
   - report new evidence if available;
   - calibrate or concede when needed;
   - point to revised section/table/figure.

Use "concede and narrow" when the reviewer is correct. Do not defend an overclaim; recommend a safer claim and explain the needed clarification. Do not claim that conversational explanations repair the submitted manuscript until the information is incorporated and re-reviewed.
