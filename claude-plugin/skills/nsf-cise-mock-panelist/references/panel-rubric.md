# NSF CISE panel rubric

Use the exact solicitation first. This rubric supplies a consistent internal lens, not additional official NSF criteria.

## Overall rating anchors

In machine-readable JSON, use `excellent`, `very_good`, `good`, `fair`, `poor`, or `unrated`. Put an optional second, adjacent band in `rating.adjacent_split`; for example, a human-facing `V/G` is encoded as `{"value": "very_good", "adjacent_split": "good"}`. Human-facing Markdown may abbreviate the bands as `E`, `V`, `G`, `F`, and `P`, but never put those abbreviations or `NO_RATING` in JSON.

- `E — Excellent`: compelling, well-supported case with exceptional strengths; remaining weaknesses are minor and do not threaten the central contribution or execution.
- `V — Very Good`: strong and competitive; important strengths clearly outweigh bounded, repairable weaknesses.
- `G — Good`: credible value but one or more material weaknesses limit enthusiasm or confidence.
- `F — Fair`: some merit, but major weaknesses in premise, novelty, approach, feasibility, broader impacts, or communication substantially reduce competitiveness.
- `P — Poor`: central premise is unsupported, contribution is unclear or already subsumed, approach cannot answer the question, or the package is too incomplete to justify support.

Do not calculate the overall rating as an arithmetic average. Explain which strengths and weaknesses dominate and why. Confidence is separate from rating.

## Required dimensions

For every dimension, record `strong`, `adequate`, `weak`, or `not_assessable`, with proposal evidence and consequences.

### 1. Importance and gap

- Is the problem important to the target CISE community and program?
- Is the knowledge or capability gap precise, current, and evidenced?
- Does the proposal separate the field-level gap from a local engineering inconvenience?

### 2. Novelty and transformative potential

- What exactly is new: question, theory, mechanism, method, evidence, dataset, integration, scale, or operating regime?
- What is the closest prior work and funded activity?
- Is the claimed delta substantive, obvious, incremental, or unresolved?
- Would success change understanding or only improve an implementation?

### 3. Contribution and intellectual merit

- Will success yield generalizable knowledge, reusable methods, defensible empirical findings, or a new explanatory model?
- Are contributions explicitly mapped to aims and evidence?
- Does the project remain scientifically valuable under null or negative results?

### 4. Approach and mechanism

- Does the proposal explain why the approach should work?
- Are hypotheses, assumptions, units of analysis, data, baselines, measures, and decision rules explicit?
- Can the evaluation distinguish the central claim from plausible alternatives?
- Are failure modes and alternative strategies technically credible?
- Are definitions, assumptions, units of analysis, thresholds, margins, sample or power logic, and analysis decisions precise enough for an expert to audit?

### 5. Feasibility, team, and resources

- Is scope coherent with time, effort, access, compute, participants, data rights, and facilities?
- Does preliminary evidence de-risk the hardest step without being overstated?
- Does expertise map to work packages and risks?

### 6. Broader Impacts

- Are beneficiaries, activities, owners, partners, schedule, resources, outputs, outcome measures, and sustainability explicit?
- Are commitments evidenced rather than invented?
- Is the plan integrated with the research and proportionate to resources?
- Does it go beyond dissemination-only claims?

### 7. Solicitation and program fit

- Does the project answer the exact opportunity rather than a generic NSF call?
- Are track-specific priorities and additional criteria directly addressed?
- Is the scope scientific research rather than product development or routine deployment?

### 8. Presentation and organization

- Can a general computer-science panelist with no assumed proposal-subarea expertise identify the problem, gap, insight, aims, evaluation, and payoff after one cold read?
- Is the argument coherent across the summary, project description, figures, timeline, and broader impacts?
- Does page allocation reflect decision importance?

### 9. General-CS accessibility

- Can the reviewer reconstruct the problem, gap, central idea, aims, decisive tests, and expected knowledge without guessing?
- Does the proposal introduce intuition and purpose before subarea notation, protocol mechanics, or edge cases?
- Are deep examples limited to the mechanics needed to understand the general contribution, with an explicit return to that contribution?

### 10. Writing precision and professionalism

- Are load-bearing terms defined once and used consistently across prose, equations, figures, tables, and aims?
- Do sentences expose the actor, action, qualification, and evidence without rereading?
- Are claims bounded to the evidence, and are current results separated from proposed work?
- Are grammar, typographic, numbering, and cross-reference errors rare enough not to lower confidence in quality control?

### 11. Technical precision and integrity

- Do equations, symbols, units, counts, denominators, thresholds, schedules, and resource arithmetic agree internally?
- Are threat models, mechanisms, baselines, ablations, estimands, decision rules, uncertainty, and validity limits stated where relevant?
- Can the proposed evaluation distinguish the central claim from plausible alternatives and yield useful knowledge under null results?

Score dimensions 9 and 11 independently. A proposal can be accessible but technically shallow, or technically detailed but inaccessible; either weakness remains material when it affects panel judgment.

## CISE domain overlays

Apply only those relevant to the proposal.

### AI and data-centric work

Check dataset provenance and rights, train/development/test separation, leakage and contamination, contemporary baselines, ablations, uncertainty, distribution shift, compute/model access, reproducibility, fairness, privacy, safety, and misuse.

### Cybersecurity and privacy

Define assets, trust boundaries, adversary goals/capabilities, defender knowledge, out-of-scope assumptions, false positives/negatives, adaptive attacks, prevalence versus exploitability, operational cost, responsible disclosure, dual use, and safe artifact release.

### Systems and networking

Check workload realism, scale, baselines, end-to-end and component measurements, overhead, compatibility, failure recovery, deployment constraints, reproducibility, and whether evaluation captures real bottlenecks.

### HCI, usable security, and computing education

Check population and recruitment, instruments, construct validity, power or saturation rationale, analysis plan, privacy, accessibility, demographic limits, researcher effects, implementation fidelity, and transfer beyond the study setting.

## Finding contract

Each weakness must state:

1. stable finding ID and severity;
2. proposal location;
3. what the proposal says or omits;
4. why this matters under a stated criterion;
5. likely consequence for confidence or competitiveness;
6. concrete correction or evidence needed;
7. status as verified, inference, or open question.

Each material strength uses the same evidence discipline and states what should be preserved. Every finding begins with a `plain_panel_concern` and then gives the `technical_basis`; it also identifies affected audiences, impact type, and revision type. Label defects professionally as scientific flaws, confidence-lowering credibility defects, reviewer friction, or copyedits.

Preserve material strengths with the same specificity. Do not reward or penalize fashionable terminology, institutional prestige, or writing style independently of the stated criteria.
