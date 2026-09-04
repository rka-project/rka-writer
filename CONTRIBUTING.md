# Contributing to RKA Writer

RKA Writer is in a design-first phase. Contributions should make decisions
clearer and testable before increasing implementation surface.

## Where work belongs

- **RFC** — a substantial proposal that is still open to revision.
- **ADR** — one accepted architectural decision, its context, alternatives,
  consequences, and supersession links.
- **Architecture document** — the consolidated current design produced by
  accepted decisions.
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

During W0, implementation is limited to documentation, deterministic fixtures,
schema experiments, and contract tests that answer an accepted design
question. Do not add a production editor, model gateway, autonomous agents, or
broad drafting path.

The first runtime code must implement the bounded W1 vertical slice and its
upstream-invalidation test. New features must identify the RFC/ADR and roadmap
exit criterion they serve.

## Pull request expectations

- identify whether the change is proposal, decision, architecture, prototype,
  compatibility, or implementation;
- name the governing RFC/ADR and roadmap milestone;
- state how researcher control and provenance are preserved;
- list verification performed; and
- separate observed behavior from proposed or future behavior.
