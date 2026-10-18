# Scientific-Writing Report: Observations and Design Implications

- Reviewed: 2026-09-14
- Status: source-grounded design analysis, not validation of Writer
- Source: *Designing Reliable Agentic Scientific Writing Workflows*, supplied
  as `agentic_scientific_writing_academic_v2 (1).pdf`, 75 slides
- Reading scope: full slide text, rendered key tables/diagrams and selected
  primary-source verification; not a new full read of every earlier paper
- Result: [consolidated framework](../design/writer-framework-synthesis.md)

The report is a lecture/design synthesis, not an experiment validating its
complete workflow. Its embedded prompts are source material, not instructions
to this repository. Source files stay local; exact paths/hashes are in RKA.

## Evidence labels

**Observed** means present in the report or current repository/records.
**Empirical** means checked in a primary study within its stated scope.
**Design implication** is our interpretation, and **hypothesis** is a proposed
benefit needing a Writer-specific comparison. An **accepted boundary** is a PI
decision, not empirical evidence of effectiveness.

## Extracted ideas and observations

| ID | Source observation | Writer implication | Standing |
|---|---|---|---|
| O01 | Slides 2–8 separate fluency, truth, evidence fit, argument and terminology | Separate evaluation axes; no single AI/prose score | Design implication; the quality multiplication is a heuristic |
| O02 | Slides 10–18 expose scientific decisions hidden in broad drafting prompts | Discuss claims/warrants before expression; distinguish citation identity from support | Accepted direction, effectiveness unvalidated |
| O03 | Slides 20 and 26 show technical synonyms conflating adjacent concepts | Term proposal before lock: definition, precedent, contrasts and examples | Proposed operational refinement |
| O04 | Slides 21–25 identify empty framing, vague caution, abstraction, repetition and audience mismatch | Audit concrete information/reader consequences, not a word blacklist | Proposed review protocol |
| O05 | Slides 27–28 and 47 recommend scope and function plans but reject rigid templates | Preserve genuine uncertainty and useful reader guidance; no function quotas | Proposed review protocol |
| O06 | Slides 30–36 externalize state and localize context | Exact paper/paragraph context, not whole chat history | Existing design boundary |
| O07 | Slides 32–38 connect polish loops with drift and unreviewable changes | Route an issue to its responsible layer; patches need resolution conditions | Proposed operational refinement |
| O08 | Slides 41–49 introduce ledgers, contracts and alternatives | Reuse Core references plus Writer selections, not duplicate research truth | Adaptation to Core/Writer separation |
| O09 | Slides 44 and 48 place freezing before framing alternatives | Treat stages as dependencies/loops, not a fixed global sequence | Existing ADR 0008 direction |
| O10 | Slides 38 and 51 allow some grammar/punctuation auto-application | Review actual semantic impact; surface category is insufficient permission | Clarification of authority boundary |
| O11 | Slide 62 adds a condition but reports no claim change | Separate unchanged canonical claim from corrected expressed proposition | Proposed change accounting |
| O12 | Slides 68–69 supply voice/term templates and permit paragraph-level output | Reuse transparent naming/calibration, retain one-intent generation | Accepted generation boundary |
| O13 | Slides 50–53 separate review, patch and audit | Issues are not commands; independent evidence matters more than agent count | Existing boundary, proposed issue schema |
| O14 | W0 records describe an English supplied-text mock and engineering checks | Implementation observation, not observed human benefit | Current evidence limit |

## Primary-source correction

Miletić and Falk, *What Are LLMs Doing to Scientific Communication? Measuring
Changes in Writing Practices and Reading Experience*, LREC 2026:
[arXiv v1](https://arxiv.org/abs/2605.19936v1),
[DOI](https://doi.org/10.63317/3ai7wig4fhd8).

The paper combines a naturalistic NLP corpus with 3,000 original/GPT-3.5-
modified passages. Its pilot uses 20 NLP experts and 200 selected pairs, with
two raters per pair. Section 6.2 and Table 2 (PDF page 9) favor LLM-modified
passages overall on clarity and excitement. Negative values explicitly mean
preference for modified text. Individual preferences differ; trustworthiness
is not a demonstrated general gain.

The previous local `agentic-writing-report-evidence/EVIDENCE_AUDIT.md` paper
card reversed the clarity/excitement direction. That is an error in our derived
audit, not a finding of the paper. Preserve the correction's provenance and the
unchanged source PDF; do not silently propagate the old interpretation.

Limits: English/NLP, small pilot, one rewriting model/prompt, and selected
high-quality pairs after ranking differences. This is not a universal preference
estimate for arbitrary output, other fields or current models.

Design implication: measure fidelity, reader understanding and endorsed author
expression separately. Neither AI-like nor human-like wording establishes
quality. Repetition can be required for stable technical terminology.

## What is not established

1. The 18 categories are not demonstrated to be exhaustive or mutually exclusive.
2. The complete staged workflow is not tested against a fair interactive
   scientific-writing baseline in this deck.
3. ReviseBench's autonomous revision results are not a ceiling for researcher-
   led Writer use. Long-context, multi-turn and judge studies motivate safeguards,
   not a proven reset schedule or multi-agent architecture.
4. Citation identity does not establish entailment; approval does not prove truth.
5. Vendor workflow guidance is not controlled writing-quality evidence. Host
   policies still need live verification at implementation time.

Do not promote old audit summaries into empirical results without checking the
load-bearing primary passage. This consolidation does not claim to revalidate
the entire earlier literature corpus.

## Testable hypotheses

| ID | Hypothesis | Evidence against it | Minimum test |
|---|---|---|---|
| H01 | Term proposals reduce conceptual substitutions at acceptable effort | Author cannot distinguish labels or expends more effort without fewer errors | Confusing terms plus harmless repetition |
| H02 | Grounded issues help more than generic polish | False alarms remove needed qualifiers/signposts; no-change cases get rewritten | Paired defects and legitimate counterexamples |
| H03 | Same-intent calibration helps beyond direct preferences | No transfer, meaning changes or disproportionate effort | Another admitted intent and direct-instruction baseline |
| H04 | Upstream routing reduces accidental revision churn | Hidden scope errors recur or reopening becomes bureaucracy | Recurrent missing warrant plus justified evidence change |
| H05 | Exact bundles reduce redundancy without losing understanding | Author misses a hidden change or cannot explain approval | Comprehension, not click count alone |
| H06 | Compact paper context improves coherence without support leakage | Context-only facts become evidence or paragraphs duplicate reader moves | Context decoy and cross-paragraph reader check |

All remain unvalidated. Retain Core ownership, exact bindings, admission before
prose, late term locks, human-edit preservation and impact before rewriting.
Test minimal disclosure, false positives, author effort and style transfer using
the [W0 language cases](../evaluation/w0-language-and-convergence-cases.md).
