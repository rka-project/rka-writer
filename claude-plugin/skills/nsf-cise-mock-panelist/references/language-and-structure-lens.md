# Language, accessibility, depth, and organization lens

Review communication as evidence transmission. The proposal must work for two audiences at once:

- a capable general computer-science panelist who may know neither CPS nor cybersecurity; and
- a domain or methods expert who will challenge definitions, mechanism, evidence, and validity.

These are independent gates. Accessibility cannot compensate for missing technical substance, and density cannot compensate for an argument that a broad panelist cannot reconstruct.

## Contents

1. Cold-read protocol
2. Progressive exposition and fast-read diagnostics
3. General-CS accessibility and expert-depth gates
4. Terminology, sentence mechanics, and rule density
5. Science/artifact separation and organization
6. Broader Impacts and visual presentation
7. Credibility-defect sweep and reviewer-output readability

## Cold-read protocol

Before using outside explanations or the author's summary, read the proposal in its presented order and reconstruct:

1. important problem;
2. precise knowledge or capability gap;
3. central insight;
4. aims and their dependencies;
5. decisive test for each aim;
6. expected generalizable knowledge under positive, null, or negative results; and
7. societal outcomes and how they will be assessed.

Record the reconstruction even when it differs from the author's intended framing. Identify the first location where the mental model breaks and why: undefined concept, missing logical bridge, hidden assumption, premature detail, inconsistent term, or absent test. Do not hide the failure behind generic advice to “improve clarity.”

## Progressive exposition

Test whether decision-critical material follows this order:

`problem -> evidenced gap -> intuitive insight -> precise claim -> method -> decisive test -> expected knowledge`

Put the roadmap and contribution early. Introduce an example only after the reader knows the general question it illustrates. Give the minimum domain mechanics needed to understand the example, then reconnect it to the general claim. Flag a passage that starts with protocol internals, notation, implementation detail, or an edge case before explaining why the detail matters.

Assign each paragraph one primary job: problem, evidence, gap, insight, aim, method, evaluation, risk, expected knowledge, broader impact, or transition. Flag paragraphs with no decision-relevant job or too many competing jobs.

## Fast-read and paragraph diagnostics

Run two nested tests before line editing:

1. **Twenty-second/first-page test.** State the consequential problem, missing knowledge, central insight, CAREER objective, linked aims, and scientific payoff using only what appears before the first dense technical section. Mark every field that requires later backfilling or guessing.
2. **Paragraph claim test.** For each decision-critical paragraph, state its one job and check whether sentence one exposes that job. Diagnose a late point, hidden actor/action, missing transition, or premise-method-exception pileup rather than merely asking for “stronger BLUF.”

For motivating examples, run a scene test: can a broad reader state the mechanism, consequence or harm, and the one relevant difference that illustrates the general claim? An example that supplies only comparison structure or domain detail without this scene fails. An example that is vivid but never reconnects to the general claim also fails.

Separate motivation from operationalization. A motivation paragraph may name the decisive kind of evidence, but it should not carry the full estimand, gate, threshold, confidence-bound, or edge-case machinery before the reader understands why the question matters.

For each load-bearing scientific object, test whether the text makes four slots recoverable: what it is, what information or assumptions it receives, what operation or objective defines its role, and what constraint or boundary limits it. Do not force these into one sentence when that would damage readability; require a compact local definition.

## General-CS accessibility gate

After one reading, a broad CS panelist should be able to explain accurately:

- what problem matters and to whom;
- what existing work cannot yet explain or do;
- what the project will discover, not merely build;
- why the approach could close the gap;
- what observation would support or weaken the central claim;
- why the scope is feasible; and
- what scientific and societal outcomes success would produce.

The panelist need not reproduce subarea formalism. They must not need to guess what a term, aim, or example is doing in the argument. Treat inaccurate reconstruction as evidence of communication failure, even if a specialist can decode the passage.

## Expert-depth gate

A specialist should be able to locate, where relevant:

- definitions, assumptions, scope, and boundary conditions;
- the mechanism linking intervention, system behavior, and observable outcome;
- assets, trust boundaries, adversary or environment model, and out-of-scope cases;
- hypotheses or research questions and their units of analysis;
- baselines, ablations, controls, comparison conditions, and decision rules;
- metrics, estimands, thresholds, margins, uncertainty, sample or power logic, and multiplicity handling;
- data, participant, system, compute, access, and throughput requirements;
- threats to validity, failure modes, alternatives, and knowledge gained from null results; and
- traceability from each contribution claim to evidence that can distinguish it from plausible alternatives.

Readable but shallow prose fails this gate. Do not accept “we will evaluate,” “statistically significant,” “robust,” or “realistic” without enough operational detail to determine what would count as success and what rival explanation remains.

## Terminology and word selection

Create a terminology ledger for every load-bearing construct:

| Field | Required content |
|---|---|
| Canonical term | The one term used throughout |
| Plain-language gloss | Meaning intelligible to a general CS reader |
| Concrete referent | Scenario, object, or operation that lets the reader picture the construct |
| First definition | Page or section where meaning is established |
| Abbreviation or symbol | One stable form, only if it reduces burden |
| Near-synonyms to avoid | Alternate wording that could imply a different construct |
| Inputs, role, and boundary | What it receives or assumes, what it does, and what constrains it |

Flag only consequential issues:

- undefined, late-defined, or multiply defined terms;
- acronyms that save little space or overload working memory;
- synonyms used for the same construct, dataset, threat model, population, aim, or artifact;
- one term used for different concepts;
- vague verbs such as `explore`, `leverage`, `enhance`, `enable`, or `address` where a measurable action is required;
- unsupported absolutes and superlatives such as `first`, `only`, `unprecedented`, `guarantees`, `solves`, `robust`, `secure`, or `general`;
- ambiguous referents across dense technical passages;
- anthropomorphic or causal wording not supported by the design;
- proposed work written as if already achieved; and
- inconsistent distinction among objective, hypothesis, task, method, deliverable, output, outcome, and expected knowledge.

Preserve technical meaning. Offer a replacement only when the correct term is clear; otherwise ask a targeted question. Prefer a plain term followed by the exact term in parentheses on first use, then use one stable term.

## Sentence and paragraph mechanics

- Prefer direct sentences with visible actors and actions where agency matters.
- Put the main claim before secondary qualification, then keep necessary scope and uncertainty close enough to prevent overstatement. Flag both empty hedging and clarity edits that strengthen a claim beyond its evidence.
- Put known context before new information so the reader can attach each claim to an existing mental model.
- Keep the subject and main verb close enough to expose the claim.
- Split sentences that combine premise, method, qualification, exception, and consequence.
- Mark any sentence that requires rereading and diagnose the reason.
- Use lists or tables when several parallel conditions, work packages, or comparisons would otherwise be buried in prose.
- Remove repetition, digression, throat-clearing, and background that never supports the gap or design.
- Correct grammar, typos, punctuation, and malformed cross-references when they create friction or signal carelessness; distinguish copyediting from scientific revision.
- Treat analogies, contrast constructions, punctuation, and other rhetorical devices by function. Penalize them only when they carry an unsupported claim, obscure the positive assertion, or violate a current author-supplied style contract.

## Rule density and prose-table allocation

Identify paragraphs that stack gates, thresholds, counts, exceptions, sensitivity levels, or contingency branches. More than two or three formal rules is a trigger for inspection, not an automatic defect. Ask:

- Is the reviewer-visible decision stated before the rule set?
- Which details are necessary in prose for interpretation?
- Which details can move to an existing or improved table without hiding scientific logic?
- Does the table define symbols, units, conditions, and terminal outcomes well enough to stand alone?
- Do prose and table agree, or does duplication create inconsistency risk?

Moving detail into a table is a narrative repair only. It does not cure an invalid threshold, missing estimand, contradictory outcome region, or unsupported assumption.

## Science above artifacts

For each aim, separate:

- scientific object or question;
- generalizable knowledge or mechanism expected;
- evidence that distinguishes the claim from alternatives; and
- enabling software, data, models, testbeds, specifications, or educational artifacts.

Flag a section whose contribution is recoverable only as “we will build” or whose artifact inventory appears before the knowledge claim. Preserve concrete implementation evidence that supports feasibility; do not erase it in pursuit of abstraction.

## Organization and reviewer navigation

- Put decision-critical claims early enough to frame details.
- Use headings that express the claim or function, not generic labels alone.
- Keep aim names, numbering, terminology, and outputs identical across sections and figures.
- Ensure each aim has rationale, approach, evaluation, expected result, risk, alternative, and knowledge payoff.
- Use topic sentences and explicit transitions where the logical relation is not obvious.
- Separate current evidence from planned work.
- Align timeline and personnel with technical dependencies.
- Put the claim-to-test map before the densest technical exposition, not after it.
- Make Intellectual Merit and Broader Impacts easy to locate and clearly distinguished while showing their integration.
- When an author-supplied narrative or style guide exists, apply [author-style-contract.md](author-style-contract.md) only after freezing the proposal-only cold read. Separate universal communication defects from house-style and version-specific deviations.

## Page-budget-aware repairs

Inspect the rendered current version before treating page space as constrained. For each material narrative repair, estimate whether it is space-negative, neutral, positive, or unknown and identify likely duplicated text that can pay for additions. Do not recommend smaller fonts, compressed figures, or removal of necessary qualifications merely to make room. A full formal page count can still contain reallocatable whitespace; a stale guide's page-budget statement does not control the current version.

## Broader Impacts communication

Check for an explicit chain:

`named beneficiary -> activity -> responsible owner or partner -> schedule and resources -> output -> measurable outcome -> assessment -> continuation or sustainability`

The plan should align with the team's expertise and community needs, distinguish Broader Impacts from broadening participation, and integrate with the research where appropriate. Do not reward large participant counts or generic outreach by themselves. Verify commitments, feasibility, budget alignment, and outcome measures; never invent them.

## Visual presentation

Inspect rendered pages, not extracted text alone.

- Check font size, density, whitespace, hierarchy, alignment, color contrast, and grayscale legibility.
- Verify that every figure has a claim-bearing purpose, readable labels, a self-contained caption, and nearby textual interpretation.
- Check that arrows, legends, colors, symbols, and panel labels have unambiguous semantics.
- Ensure plots expose units, uncertainty, baselines, sample sizes, and provenance where applicable.
- Flag decorative diagrams that consume space without reducing reviewer uncertainty.
- Verify that figures, tables, equations, captions, and prose use identical terms, symbols, counts, and cross-references.

## Credibility-defect sweep

Run a separate slow pass for errors that can lower expert confidence even when the main idea is sound:

- inconsistent symbols, subscripts, units, ranges, signs, thresholds, margins, or denominators;
- arithmetic that does not match stated rates, sample counts, schedules, storage, compute, or throughput;
- equation/prose, table/prose, figure/prose, summary/aim, or timeline/method contradictions;
- missing definitions or changed meanings for assumptions, threat models, populations, datasets, baselines, or outcomes;
- unqualified causal claims, guarantees, universality, equivalence, or generalization;
- citations that do not support the nearby claim, incorrect attributions, or claims of closest/first work without a defensible search;
- impossible dependencies, missing personnel responsibility, or resource commitments not evidenced in the packet;
- grammar, typographic, numbering, and cross-reference errors that obscure meaning or imply poor quality control.

Classify each issue:

- `scientific flaw`: threatens the claim or the ability to test it;
- `confidence-lowering credibility defect`: likely repairable, but makes an expert question care or command of the work;
- `reviewer friction`: slows or distorts comprehension without changing the underlying science; or
- `copyedit`: local polish with little decision impact.

Do not use insults or the label “stupid error.” State the evidence, likely panel consequence, minimum repair, and verification test.

## Reviewer-output readability

The mock review must meet the same audience standard as the proposal. For each material finding, write:

1. `plain_panel_concern`: one sentence a general CS panelist can understand;
2. `technical_basis`: the precise mechanism, omission, inconsistency, or validity problem;
3. proposal location and evidence;
4. audience affected and decision consequence;
5. minimal correction or evidence needed; and
6. a test that would verify the revision.

Define specialized reviewer terms on first use. Do not make the writer decode phrases such as “identifiability failure,” “estimand mismatch,” or “equivalence-qualified” without a plain explanation.
