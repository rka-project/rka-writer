# Contributing to RKA Writer

RKA Writer is in a design-first phase. Contributions should make decisions
clearer and testable before increasing implementation surface.

## Where work belongs

- **RFC** — a substantial proposal that is still open to revision.
- **ADR** — one accepted architectural decision, its context, alternatives,
  consequences, and supersession links.
- **Architecture document** — a concise current view, distinguishing accepted
  principles from provisional implementation details and observed capabilities.
- **Roadmap** — durable dependency order and exit criteria.
- **Issue or pull request** — work currently being discussed or executed.
- **History** — superseded design that remains useful for provenance.
- **Prototype** — disposable code used to answer a named design question.

## RFC workflow

1. Copy [`docs/rfcs/0000-template.md`](docs/rfcs/0000-template.md).
2. Set status to `Provisional` and name the decision owner and tracking issue.
3. State the problem, goals, non-goals, user workflow, proposal, alternatives,
   risks, unresolved questions, and acceptance evidence.
4. Discuss the RFC through a focused pull request. Do not mix unrelated runtime
   changes into the RFC pull request.
5. When accepted, extract architecturally significant decisions into focused
   ADRs and update the current architecture documents.

## ADR workflow

- Keep one irreversible or cross-cutting decision per ADR.
- Use `Proposed`, `Accepted`, `Rejected`, `Deprecated`, or `Superseded` status.
- Do not silently rewrite an accepted ADR when direction changes. Add a new ADR
  and link both records.
- Keep long design exploration in the RFC; an ADR must stand alone but remain
  concise.

## Implementation gate

During W0, use documentation, supplied-text mockups, design fixtures and
disposable experiments to answer named questions. Start with the author
walkthrough and read-only host inspection. Do not add a production editor,
model gateway, autonomous agents or broad drafting path. Inference-consuming
probes need established billing/isolation protection and scoped authorization.

No contribution may add provider API credentials, direct model API calls,
metered fallback, local-model fallback, or a cross-provider model selector
without a new PI decision that explicitly supersedes ADR 0005.

The first authoring runtime implements only the explicitly authorized W1 slice
after the entry gate. It includes paper context, impact review, manual-edit
reconciliation and recovery. New features must name the learning/exit gate they
serve. Do not treat a merged RFC draft or repository lint as runtime evidence.

## Validation labels

Separate repository integrity, fixture consistency, runtime conformance,
scientific assessment and author/reader evidence. Tests checking that a sentence
appears in a Markdown file do not test the behavior it describes. Do not lock
the number of ADRs or require superseded decisions to remain Accepted.

Never stage the local-only full researcher design source. Its exact path is
ignored intentionally; use an explicit staging list and inspect the staged diff.

## Pull request expectations

- identify whether the change is proposal, decision, architecture, prototype,
  compatibility, or implementation;
- name the governing RFC/ADR and roadmap milestone;
- state how researcher control and provenance are preserved;
- list verification performed; and
- separate observed behavior from proposed or future behavior.
