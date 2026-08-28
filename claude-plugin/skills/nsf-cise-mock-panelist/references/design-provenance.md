# Design provenance and maintenance register

Read this file only when maintaining or recalibrating the skill. Recheck activity before adopting upstream behavior.

## Contents

- ARIS
- NSF Proposal Evaluation System
- OpenReview
- Agent Review Panel
- AI Research Feedback grant-review skill
- Inspect AI
- PaperQA2
- ASReview
- Evaluation and regression harnesses
- Current peer-review evaluation evidence
- Proposal-writing and audience guidance
- Author-derived CAREER narrative and style lessons
- Derived reviewer design

## ARIS

- Project: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep
- Audited snapshot: commit `c5f3d5bfc694a812012729841e9697223e4f2130`, 2026-07-15.
- Reused patterns: raw-artifact cold review, fresh reviewer contexts, structure-before-prose checks, claim-level novelty searches, novelty-source existence/metadata/support checks, zero-context claim audits, strongest-objection (`kill argument`) adjudication, atomic issue tracking, frozen input hashes, trace files, typed failure states, and revision loops driven by raw diffs.
- Deliberately changed: the linked ARIS grant skill is primarily a proposal-writing orchestrator. Its review stage calls one generic external panelist and uses static per-section scoring; broader repository skills supply many of its stronger audit patterns. This skill does not inherit hard-coded page limits, default agency guessing, per-section arithmetic scoring, unrestricted shell fallback, same-family independence claims, or proposal transfer without authorization. It adds live solicitation extraction, NSF/PES-shaped reviews, Broader Impacts, presentation/terminology review, sealed holistic panelists, deterministic schemas, and a calibration protocol plus forward-test specification. No behavioral calibration is claimed until an authorized human-anchored evaluation is actually completed.

## NSF Proposal Evaluation System

- Public FAQ: https://www.nsf.gov/policies/document/faq-proposal-evaluation-system-pes-panelists
- Verified: 2026-07-20.
- Reused patterns: individual reviews are frozen before visibility, required Intellectual Merit and Broader Impacts strengths/weaknesses, additional criteria, separate summary statement, lead/scribe roles, collaborative panel summary, and explicit agreement.

## OpenReview

- Project: https://github.com/openreview/openreview-py
- Maintenance evidence checked 2026-07-20: active repository; v2.3.1 released 2026-07-08.
- Reused patterns: structured review forms, role separation, immutable/versioned records, and discussion after initial review.
- Not copied: conference-specific accept/reject thresholds and social/reputation metadata.

## Agent Review Panel

- Project: https://github.com/wan-huiyan/agent-review-panel
- Maintenance evidence checked 2026-07-20: active project; v3.6.0 released 2026-06-28.
- Reused patterns: sealed initial opinions, private reflection, bounded debate, blind final synthesis, completeness checks, claim validation, and post-judge verification.
- Not treated as validation evidence: its agents may share one model family and many reported tests are workflow/schema tests. Those facts do not establish expert-review validity or independence.

## AI Research Feedback grant-review skill

- Project: https://github.com/claesbackman/AI-research-feedback/blob/main/Skills/review-grant/SKILL.md
- Maintenance evidence checked 2026-07-20: the grant-review skill was updated in an active repository on 2026-04-16.
- Reused pattern: six parallel specialist passes, a consolidating pass, grant-specific feedback categories, and actionable author-facing presentation.
- Deliberately extended: specialist decomposition alone is insufficient for independent holistic judgment, novelty verification, disagreement preservation, and calibrated assurance; this skill adds those layers.

## Inspect AI

- Project: https://github.com/UKGovernmentBEIS/inspect_ai
- Docs: https://inspect.aisi.org.uk/
- Maintenance evidence checked 2026-07-20: active commits through 2026-07-18 and current 2026 documentation.
- Reused patterns: first-class logs, scorer separation, re-scoring from frozen logs, status/error recording, and inspectable model/tool events.
- Not copied: benchmark infrastructure unnecessary for a lightweight local skill.

## PaperQA2

- Project: https://github.com/Future-House/paper-qa
- Maintenance evidence checked 2026-07-20: active commits through 2026-06-05; release v2026.03.18.
- Reused patterns: evidence retrieval from scientific documents, source metadata verification, ranked/diversified passages, and contradiction-oriented queries.
- Not copied: automatic external-provider defaults, because confidential proposals require an explicit privacy decision.

## ASReview

- Project: https://github.com/asreview/asreview
- Maintenance evidence checked 2026-07-20: v3.0.8 released 2026-06-18.
- Reused pattern: track screened records and use active-learning-like query iteration to expose search coverage rather than claiming exhaustive novelty search.
- Not copied: binary systematic-review inclusion logic; novelty depends on claim-level overlap and material delta.

## Evaluation and regression harnesses

- Promptfoo: https://github.com/promptfoo/promptfoo — v0.121.15 released 2026-06-05; documentation activity checked through 2026-07-14.
- DeepEval: https://github.com/confident-ai/deepeval — v4.1.0 released 2026-07-12.
- Microsoft Agent Framework: https://github.com/microsoft/agent-framework — active commits checked through 2026-07-19.
- Reused patterns: versioned scenarios, deterministic assertions, model-route metadata, adversarial inputs, repeated-run stability checks, and evaluator separation.
- Not copied: generic LLM-judge scores as proof of scientific-review correctness. Calibration must use authorized proposal material and qualified-human anchors.

## Current peer-review evaluation evidence

- PRISM benchmark: https://prism-benchmark.github.io/ (2026).
- Reused patterns: decompose reviews into grounded atomic units; evaluate novelty support, critical-flaw prioritization, and constructiveness separately; avoid a single opaque judge score.
- Review Feedback Agent study: https://doi.org/10.1038/s42256-026-01188-x (2026).
- Reused pattern: audit the review for specificity, factual misunderstanding, actionability, and professional tone before presenting it to authors.

## Proposal-writing and audience guidance

Checked 2026-07-21. These sources inform reviewer heuristics and author-facing diagnostics, not policy. The exact solicitation and current NSF policy control requirements. Official NSF advice has greater authority than university or commercial tutorials, but it still does not override a solicitation or the PAPPG.

### NSF Broader Impacts guidance

- Source: https://www.nsf.gov/science-matters/nsf-101-five-tips-your-broader-impacts-statement
- Reused patterns: know the review audience; distinguish Broader Impacts from broadening participation; align activities with the team's interests, expertise, and community needs; use available institutional resources; and assess whether the plan is beneficial, creative, well reasoned, organized, measurable, feasible, and resourced.
- Boundary: this is official general guidance, not the controlling solicitation or a complete compliance specification.

### Carnegie Mellon proposal-writing advice

- Source: https://www.cs.cmu.edu/~sfinger/advice/advice.html
- Reused patterns: a research description must satisfy both a leading subarea expert and a smart reviewer outside the subarea; expose what, why, and how; distinguish knowledge contributions from deliverables; remove repetition and digression; and include enough detail for a technically exacting reviewer.
- Maintenance note: the page identifies a 2015 update. It is strategic advice, not NSF policy.

### Montclair-hosted successful-proposal guide

- Source: https://www.montclair.edu/sponsored-programs/wp-content/uploads/sites/194/2019/02/nsf-successful-proposal.pdf
- Reused patterns: simultaneous expert/non-subarea readability, a detailed feasible research plan, respectful and complete related-work treatment, and emphasis on knowledge rather than merely building a system.
- Boundary: the PDF is an older copy derived from Susan Finger's advice. It corroborates but does not independently multiply the weight of the CMU source, and its dated procedural details are not used.

### Baruch/CUNY writing seminar

- Source: https://spar.baruch.cuny.edu/wp-content/uploads/sites/37/2020/12/StrategiesandTacticsofWritingNIHandNSFResearchGrantProposals-1.pdf
- Reused transferable patterns: give a broad audience a roadmap; make importance easy to find; use clear direct sentences and known-before-new sequencing; reduce jargon and wordiness; mark sentences that require rereading; use tables for complex parallel material; and make figures and captions self-contained.
- Boundary: the seminar is dated 2009 and much of it uses NIH examples and old procedures. Only general writing practices were adopted; no page, submission, or policy rule was imported.

### Granted AI Broader Impacts examples

- Source: https://grantedai.com/blog/nsf-broader-impacts-examples
- Reused heuristics: name beneficiaries and partners, specify activities, schedule, participant scale when supportable, measurable outcomes, research integration, feasibility evidence, budget alignment, and sustainability. Detect a Broader Impacts section that is tacked on rather than integrated.
- Boundary: this is commercial guidance with composite examples. Examples and numerical claims are prompts for verification, not evidence of NSF preference or policy.

### GrantCopilot NSF proposal guide

- Source: https://www.grantcopilot.ai/blog/nsf-grant-proposals-guide
- Reused heuristics: make the Project Summary accessible rather than overly technical; use visible organization and explicit Intellectual Merit/Broader Impacts signposting; require a realistic method and timeline; and treat small inconsistencies and proofreading defects as possible credibility signals without inflating them into scientific flaws.
- Boundary: this is commercial, non-authoritative guidance. Static recommendations and any implied success claims are not used as policy or calibration evidence.

## Author-derived CAREER narrative and style lessons

- Source: a proposer-owned narrative/style guide supplied on 2026-07-21 and derived from an earlier version of the proposer's own CAREER Project Description.
- Reused transferable diagnostics: claim or concrete picture before formal machinery; paragraph-level BLUF; a scene or concrete referent for abstract systems; explicit motivation/method separation; detection of prose rule dumps that should be split between prose and tables; a four-slot test for a central scientific object (what it is, what it is given, what it does, and where it applies); explicit separation of scientific contribution from implementation artifact; and page-budget-aware repairs.
- Preserved as author-specific or version-specific rather than universal: exact introduction beats, exact project vocabulary and examples, blanket punctuation or contrast-construction preferences, section-preview conventions, and assumptions about a particular aim count or page budget.
- Scientific guardrails: “clarity” cannot remove necessary qualification or uncertainty, strengthen causality or generality beyond the evidence, replace a missing method or experiment, or bury decisive scientific logic in a table.
- Contamination boundary: the proposal-only cold read is frozen before the guide is revealed. The guide informs a second editorial pass and cannot retroactively change what a panelist could reconstruct unaided.
- Distribution boundary: the source guide and its draft-specific examples are not included in the portable package; only generalized, versioned reviewer behavior is included.

### Derived reviewer design

The combined guidance supports the `wide -> bridge -> deep` roster: a general-CS panelist, an adjacent-CISE expert, and a risk-selected domain/methods specialist. All are holistic. The skill requires cold-read argument reconstruction, progressive exposition, a terminology ledger, bounded paragraph diagnostics, separate accessibility and expert-depth verdicts, a credibility-defect sweep, page-budget-aware repairs, and plain-first reviewer comments. When an author guide is supplied, the skill adds a contamination-controlled contract-aware editorial pass. These design choices remain provisional until tested against authorized, qualified-human review anchors.

`AgentReview` was screened during maintenance but not used as a design dependency because its recent maintenance signal was weaker than the projects above. Recheck all activity claims before a future recalibration.

These sources inform architecture, not NSF policy. The exact solicitation and current NSF sources always control proposal criteria.
