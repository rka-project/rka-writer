# Detailed Review Rubric

Use this rubric to review AI and cybersecurity research manuscripts. Not every item applies to every paper, but the review should explicitly address each major category that is relevant.

Route the paper by archetype and apply the hard tests in `domain-gates.md` before using this general checklist. Run `fast-reader-audit.md` before specialist reading so later expertise does not erase an initial comprehension failure.

## Contents

1. [Preflight, authority, and fast read](#0-preflight-authority-and-fast-read)
2. [Topic and audience fit](#1-topic-fit-and-audience-fit)
3. [Novelty and related work](#2-novelty-and-related-work-positioning)
4. [Motivation and claims](#3-motivation-problem-statement-and-claim-clarity)
5. [Threat model](#4-threat-model-assumptions-and-security-goals)
6. [System design](#5-system-design-architecture-algorithms-and-implementation)
7. [Organization](#6-content-organization-and-narrative-flow)
8. [Figures and tables](#7-figure-diagram-and-table-design)
9. [Experiments and statistics](#8-experiment-design-baselines-metrics-and-statistics)
10. [Interpretation and validity](#9-results-interpretation-and-external-validity)
11. [Factuality and citations](#10-factuality-citation-and-reference-integrity)
12. [Writing and presentation](#11-writing-presentation-and-prose-artifacts)

## 0. Preflight, Authority, and Fast Read

Before detailed review:

- record supplied, inspected, partial, inaccessible, and unrendered material;
- distinguish PDF page numbers from printed page numbers;
- lock the venue/year/track/paper type or label venue conclusions advisory;
- separate verified desk-policy blockers from scientific merit;
- complete the 30-second reconstruction and three-minute navigation sweep;
- record the first mental-model breakpoint, backtracking, acronym/notation load, and whether a general CS/security expert can explain the contribution;
- convert every material breakpoint into an anchored likely-misreading, smallest concrete repair, precision guard, and fresh cold-read verification test;
- build the claim-evidence and threat-model ledgers.

Do not state that an item is absent when it was only not located in incomplete or unreliable extraction.

## 1. Topic Fit and Audience Fit

Check:

- Does the paper clearly belong in the target community: security, privacy, systems, AI/ML, software engineering, networking, HCI, or a cross-disciplinary venue?
- Is the security/privacy relevance central rather than incidental?
- Is the AI component central to the method, threat, or evaluation, or merely a tool used for convenience?
- Does the paper explain why the problem matters now?
- Does the introduction make the intended reader care within the first one or two pages?
- Does the paper use vocabulary and assumptions appropriate for the target venue?

Common problems:

- The paper reads like an AI paper with weak security contribution.
- The paper reads like a security paper with shallow AI methodology.
- The system is useful but not clearly a research contribution.
- The venue fit depends on evaluation details that are not shown.

Actionable fixes:

- Add a one-paragraph venue-facing problem statement.
- Reframe the contribution around the security bottleneck, not the tool used.
- Add a threat model, deployment model, or evaluation setting that matches the venue.
- Move nonessential background out of the introduction and use the space for the research gap.

## 2. Novelty and Related-Work Positioning

Check:

- What exactly is new: problem, threat model, method, system architecture, dataset, benchmark, measurement, theory, or empirical finding?
- Is the baseline comparison fair and current?
- Does related work compare mechanisms and assumptions, not just list papers?
- Does the paper distinguish itself from obvious adjacent work?
- Does it state what it does not claim?
- Is novelty incremental but still useful? If so, is the incremental value measured?

Common problems:

- Related work is a survey instead of a positioning argument.
- The claimed novelty is really an engineering combination.
- The closest prior work is missing or treated superficially.
- The paper says "first" without enough evidence.

Actionable fixes:

- Add a comparison table with columns for threat model, core mechanism, trust assumptions, data required, deployment requirement, and evaluation scope.
- Replace "to the best of our knowledge, first" with a narrower, verifiable claim.
- Identify the closest two to four papers and explain the exact difference in assumptions and evidence.
- Add an ablation or baseline that proves the new component is load-bearing.

## 3. Motivation, Problem Statement, and Claim Clarity

Check:

- Is the research question stated precisely?
- Does the paper separate motivation, problem, approach, and contribution?
- Are claims traceable to experiments or proofs?
- Does the abstract overstuff numbers or underexplain the contribution?
- Does the introduction end with a crisp contribution list?
- Are limitations stated as boundaries rather than buried disclaimers?

Common problems:

- The introduction describes a broad risk but not the paper's exact problem.
- The contribution list mixes implementation details, evaluation facts, and claims.
- The abstract reports many metrics without explaining why they matter.
- The paper claims generality from a narrow benchmark.

Actionable fixes:

- Add a "This paper asks..." paragraph.
- Rewrite contributions as 3-5 claims, each mapped to a section and evidence.
- Use a trial-accounting or evidence-accounting table if the evaluation is complex.
- Move speculative claims to discussion or future work.

## 4. Threat Model, Assumptions, and Security Goals

Check:

- Who is the attacker?
- What can the attacker observe, control, modify, or compromise?
- What assets are protected?
- What is the defender allowed to know or deploy?
- What is trusted and what is untrusted?
- What are the security goals: confidentiality, integrity, availability, safety, policy compliance, robustness, accountability, or privacy?
- What is explicitly out of scope?
- Are attacks in the evaluation consistent with the threat model?
- Are direct, indirect, adaptive, insider, supply-chain, and physical attacks distinguished when relevant?
- Does a defense face a defense-aware attacker, and is the attack shown to work on the undefended target?
- Does every security experiment map to a stated threat-model row?

Common problems:

- Threat model appears after the system design.
- Attacker capability changes between sections.
- Evaluation includes attacks that the threat model excludes without saying they are stress tests.
- Assumptions are needed for the system to work but are not called out.
- Security goal and metric do not match.

Actionable fixes:

- Add a threat-model table with columns: entity, trusted/untrusted, capability, excluded capability, rationale.
- Add a security-goals paragraph before design.
- Mark out-of-scope attacks as limitations or stress tests.
- Separate attacker success rate, defender utility, false positives, and operational cost.

## 5. System Design, Architecture, Algorithms, and Implementation

Check:

- Is there a clear architecture diagram?
- Are data flow and control flow distinguishable?
- Are trust boundaries shown?
- Is the TCB or privileged component identified?
- Are algorithms specified enough to reimplement?
- Are design alternatives discussed?
- Are failure modes and fallback behavior specified?
- Are parameters, thresholds, prompts, model versions, tools, and dependencies reported?
- Does the system require unrealistic deployment assumptions?
- Are security guarantees formal, empirical, or heuristic? Are they labeled correctly?

Common problems:

- The paper describes the concept but not the implementation.
- Diagrams omit trust boundaries and interfaces.
- The system's strongest claim depends on an unspecified classifier, LLM, threshold, or policy.
- Design choices are presented as obvious without comparison.
- The paper says "verified," "guaranteed," or "complete" when evidence is empirical.

Actionable fixes:

- Add an end-to-end architecture figure with numbered steps.
- Add a table of components: input, output, state, trust level, failure behavior.
- Add pseudocode for the core decision procedure.
- Add a design-rationale table: design choice, alternative, why chosen, evidence.
- Add a limitations paragraph for assumptions that cannot be enforced.

## 6. Content Organization and Narrative Flow

Check:

- Does the paper follow a logical sequence: problem -> threat/model -> design -> implementation -> evaluation -> discussion?
- Does each section have a role in proving the thesis?
- Are background sections too long?
- Are related work and limitations placed where they help the argument?
- Are results introduced before the reader understands the metric?
- Are evaluation subsections ordered by claim importance?

Common problems:

- The paper delays the actual contribution.
- Evaluation results are scattered across unrelated subsections.
- The same point is repeated in abstract, introduction, discussion, and conclusion.
- Limitations are hidden or apologetic.

Actionable fixes:

- Add a roadmap tied to claims, not sections.
- Move secondary experiments to appendix or later evaluation.
- Put the strongest evidence first.
- Use subsection titles that state findings, not topics, when appropriate.
- Remove bridge paragraphs that repeat prior section summaries without advancing the argument.

## 7. Figure, Diagram, and Table Design

Check:

- Does each figure answer a specific reviewer question?
- Are diagrams readable in two-column format?
- Are trust boundaries, attacker-controlled inputs, protected assets, and enforcement points visually clear?
- Do tables align columns with claims and metrics?
- Are denominators, trial counts, model counts, repetitions, and units explicit?
- Are baseline and proposed method comparisons visually easy to parse?
- Are confidence intervals or uncertainty shown when relevant?

Common problems:

- Architecture figure is decorative rather than explanatory.
- Table reports percentages without denominators.
- Figures use unclear acronyms or tiny labels.
- Multiple evaluation settings are mixed in one table.
- The paper lacks a trial-accounting table.

Actionable fixes:

- Add a system diagram with numbered execution path and red/blue trust coloring if color is allowed.
- Add a trial-accounting table for complex evaluations.
- Add an ablation table that isolates each component.
- Rename tables to describe the finding, not just the data source.
- Put definitions and denominators in table captions.

## 8. Experiment Design, Baselines, Metrics, and Statistics

Check:

- What claim does each experiment test?
- Are baselines strong, current, and fairly configured?
- Are ablations sufficient to show which component matters?
- Are metrics aligned with the security and utility goals?
- Are repeated trials, seeds, model versions, prompt templates, and hardware/software reported?
- Are trials independent? If not, are clustered or scenario-level statistics used?
- Are confidence intervals, effect sizes, and significance tests appropriate?
- Are negative results, failure cases, and sensitivity analyses included?
- Are datasets public, representative, and free of leakage?
- Is the evaluation realistic enough for the deployment claim?
- Are split units entity-, group-, family-, or time-aware when examples are correlated?
- Are preprocessing, prompting, model selection, attack selection, and thresholds isolated from the final test set?
- Do baselines receive comparable data, access, tuning, compute, query, and attack budgets?
- Are base rates, precision-recall, operational false-positive rates, timeouts, and abstentions reported when relevant?

Common problems:

- No strong baseline, only no-defense or simple heuristic.
- The main metric hides utility regression or false positives.
- The paper treats repeated runs of the same scenario as independent.
- The benchmark is controlled but claims real-world generality.
- The evaluation does not isolate the proposed mechanism.

Actionable fixes:

- Add a baseline that embodies the strongest obvious alternative.
- Add ablations: no core component, simple version, full version.
- Report both aggregate and scenario-level metrics.
- Add confidence intervals and explain the statistical unit.
- Add sensitivity analysis over thresholds, prompts, model versions, datasets, and attack strength.
- Add a failure taxonomy with representative examples.

## 9. Results Interpretation and External Validity

Check:

- Are results interpreted at the right level of generality?
- Are effect sizes meaningful, not just statistically significant?
- Are limitations connected to deployment settings?
- Are surprising failures explained rather than buried?
- Does the paper distinguish primary evidence from preliminary, stress-test, or appendix evidence?
- Does the discussion identify where the method should not be used?

Common problems:

- The paper overclaims from one benchmark.
- Utility degradation is minimized because security improves.
- Results across models or datasets are mixed but summarized as uniformly positive.
- The conclusion repeats the abstract without explaining implications.

Actionable fixes:

- Use calibrated language: "in our evaluated workloads," "under this threat model," "for these benchmark classes."
- Add a "Where it works best / where it fails" subsection.
- Separate controlled benchmark evidence from external benchmark evidence.
- Add a residual-risk table.
- Explain why each failure happened and how the design could be extended.

## 10. Factuality, Citation, and Reference Integrity

Check:

- Do all cited works exist?
- Do citation fields match the source: authors, title, venue, year, DOI, pages?
- Do quoted passages appear in the source?
- Does the source support the claim being made?
- Are claims about model capabilities, product features, laws, standards, CVEs, benchmarks, datasets, or releases current?
- Are there missing citations for core claims?
- Are references cited in text and listed consistently?

Use `factuality-and-citation-audit.md` for the procedure.

## 11. Writing, Presentation, and Prose Artifacts

Check:

- Is the prose specific, direct, and evidence-bearing?
- Are terms defined before use?
- Are acronyms overused?
- Does the paper avoid hype, vague adjectives, and generic or template-like phrasing?
- Are paragraphs built around claims rather than summaries?
- Are transitions logical and content-specific?
- Are contributions and limitations written in a mature, non-defensive tone?
- Can a general expert recover the idea without deep subfield examples or unexplained prerequisites?
- Does terminology preserve one meaning across abstract, overview, design, and evaluation?

Use `prose-artifact-and-style-audit.md` for the detailed pass. Never infer AI authorship from style.
