---
name: rka-writer
description: "Draft or revise an academic manuscript only when the user explicitly invokes $rka-writer or explicitly requests this standalone Writer workflow. Do not load for ordinary RKA retrieval, research discussion, coding, project maintenance, or general writing."
metadata:
  version: "0.2.0"
---

# RKA Writer

Use this skill only after explicit invocation. It is a writing assistant, not a
session-wide research persona. Do not let its rules affect ordinary research,
coding, retrieval, or project-maintenance work.

## Objective

Turn the researcher's evidence and ideas into a coherent academic argument in
plain, professional language. The evidence constrains what can be claimed; it
does not dictate sentence order or paragraph structure. Never translate
journals, claims, or database records into prose one by one.

## Inputs

Work from whichever sources the researcher provides:

- manuscript files, notes, figures, tables, URLs, repositories, and datasets;
- selected related papers that establish terminology and field conventions;
- optional RKA Core records exposed through a separately configured MCP
  connection.

RKA Core is optional. If it is available, pin `project_id` on every call and
use public read operations such as `context`, `search`, `collect_report_context`,
`research_map`, `entity`, and `provenance`. Do not assume Writer-specific CLI
commands, a manuscript service, or an active RKA project. If Core is absent,
continue from the supplied sources and maintain a simple local evidence map.

## Working method

### 1. Establish the writing task

Identify the target section or revision, intended venue and audience, source
files, claims that must be preserved, and any selected papers whose terminology
or presentation style should guide the draft. Ask only for information that is
actually missing and consequential.

### 2. Build an evidence map

Privately summarize the small set of load-bearing propositions, the evidence
for each, important scope conditions, and unresolved gaps. When using RKA,
retrieve with several short angles and follow provenance links so a complete
story is recovered rather than a single matching node. Treat decisions as
rationale and scope, not empirical evidence.

Do not expose this evidence map as the manuscript's structure. It is a factual
constraint and audit aid.

### 3. Form the discourse plan

Before drafting, decide the reader-facing logic:

1. What question or problem does this passage address?
2. What is the main answer or claim?
3. Why should the reader believe it?
4. What consequence leads naturally to the next paragraph?

Organize paragraphs around this logic ladder. Combine related evidence into a
single explanation, remove record-by-record repetition, and keep transitions
causal and explicit. Prefer a few coherent paragraphs over many small fragments.

### 4. Draft with language freedom

Write fluent prose from the discourse plan. Use common technical terms and
plain academic language. Define a project-specific term before its first use.
Avoid invented labels, unnecessary adjectives, inflated claims, and unfamiliar
synonyms when a standard term is available. Do not use words such as “frozen”
when “pre-trained” is what the field normally says.

Match terminology and description patterns from the researcher-selected
related works, but do not copy their sentences. The selected papers are a style
and vocabulary corpus, not evidence for claims they do not support.

For summaries and introductions, emphasize the problem, insight, contributions,
and principal results. Defer implementation detail until the reader needs it.
For methods, define the system and threat model before abbreviations or named
sequences. For results, lead with the research question and interpretation,
then explain the evidence.

### 5. Ground after drafting

After the prose is coherent, check every factual, empirical, comparative, and
literature claim against a source. Add citations or provenance annotations at
this stage. Transitions, framing, and evidence-bounded interpretation do not
need artificial record IDs.

If support is missing, either narrow the claim, mark a clearly visible author
placeholder, or ask the researcher. Never fabricate an experiment, citation,
result, or RKA entity. Present material limitations accurately; do not volunteer
speculative weaknesses that are irrelevant to the claim or venue requirements.

### 6. Revise as a manuscript, not a database

Read the whole affected section in fresh context. Check that terms are
introduced before use, paragraphs have one clear purpose, claims build on each
other, and the section reaches its promised conclusion. Preserve useful detail
and important main-text results; do not shorten merely to make prose look
cleaner. Apply narrow edits when the user asks for revision rather than a
rewrite.

For LaTeX work, compile and inspect the rendered pages after edits. Treat
figures, tables, captions, cross-references, and page balance as part of the
manuscript, while keeping content decisions under researcher control.

## Domain reminders for CS, AI, and security

- State the problem and contribution before implementation detail.
- Define the system model, threat model, attacker capabilities, assumptions,
  and evaluation questions in the order needed by a non-specialist reader.
- Distinguish design, implementation, experiment, observation, and inference.
- Use ablations, baselines, and limitations only to the extent supported by the
  available study; do not imply experiments that were not performed.
- Prefer concrete verbs and measurable statements over promotional adjectives.

## Researcher control

The researcher owns venue choice, framing, substantive claims, disclosure
choices, and final wording. Offer alternatives when a choice materially changes
the paper; otherwise make the best evidence-preserving edit directly. Do not
create commits, upload manuscripts, submit papers, or modify RKA records unless
the researcher separately authorizes that action.

## Optional references

Load only what the task requires:

- [`references/discourse_synthesis.md`](references/discourse_synthesis.md) for
  section logic and paragraph formation;
- [`references/persuasive_framing.md`](references/persuasive_framing.md) for
  evidence-bounded advocacy and limitation triage;
- [`references/manuscript_review.md`](references/manuscript_review.md) for a
  lightweight pre-submission self-check;
- [`references/separate_review_handoff.md`](references/separate_review_handoff.md)
  only when revising from a separately frozen reviewer report;
- [`references/latex_audit.md`](references/latex_audit.md) for rendered-layout
  checks.

For venue rules, consult the current official call or template at the time of
the task. Do not rely on bundled static deadlines or formatting limits.
