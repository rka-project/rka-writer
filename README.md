# RKA Writer

RKA Writer is a researcher-controlled research-to-prose compiler and
convergence workbench. It progressively compiles reviewed research knowledge
and explicit researcher decisions into a versioned authoring graph. Public
prose is produced only as a bounded realization of approved sentence intents.

> **Status: W0 design phase.** This repository is being re-baselined from the
> former Writer 0.2 skill distribution. It does not yet contain a supported
> authoring runtime or end-user release.

## Product boundary

The researcher owns scientific meaning and semantic convergence. Writer owns
retrieval, authoring-state management, dependency tracking, decision support,
and bounded language realization.

Writer is built around five invariants:

1. **Question before retrieval; story commitment after evidence review.**
2. **No prose before semantic admission.**
3. **One sentence of output, full paragraph awareness.**
4. **Concepts early; exact terms locked before realization.**
5. **Upstream changes invalidate; they never silently regenerate.**

[RKA Core](https://github.com/rka-project/rka-core) remains authoritative for
research records, claims, evidence, and provenance. Writer owns how approved
research meaning is organized and expressed in a manuscript. Writer never
imports Core internals or opens Core storage directly.

## Start here

| Document | Purpose |
|---|---|
| [Status](STATUS.md) | Current phase, accepted decisions, and immediate gate |
| [Roadmap](ROADMAP.md) | W0-W5 milestones and exit criteria |
| [Vision](docs/vision.md) | Product problem, user, goals, and non-goals |
| [Principles](docs/principles.md) | Product invariants and researcher-control rules |
| [RFC 0001](docs/rfcs/0001-authoring-ir-and-convergence-protocol.md) | Proposed Authoring IR and convergence protocol |
| [Architecture](docs/architecture/authoring-graph.md) | Current consolidated authoring-graph view |
| [W1 evaluation](docs/evaluation/w1-acceptance-criteria.md) | First vertical-slice acceptance contract |
| [Contributing](CONTRIBUTING.md) | RFC, ADR, issue, and implementation workflow |

## What is preserved

- The complete Writer 0.2 plugin distribution is frozen at local tag
  `writer-skill-v0.2.0` and remains the W5 comparison baseline.
- The verified legacy Core bundle importer remains under
  [`legacy/core-import-v1`](legacy/core-import-v1/README.md).
- The previous platform design is retained as
  [design history](docs/history/platform-design-v0.md).
- The isolated academic Reviewer suite has been separated from the active
  Writer product. Its old integration contract remains
  [historical context](docs/history/reviewer-integration-v0.md).

## Current implementation rule

Do not add a general editor, autonomous drafting agents, broad prose
generation, or production schemas during W0. First accept the Authoring IR and
focused ADRs. Then implement only the W1 path from one approved paper question
to one fully traceable paragraph, including an upstream-change invalidation
test.

## Repository process

Large design changes begin as RFCs. Accepted architectural decisions are
recorded as focused ADRs. GitHub issues and pull requests track work in flight;
the roadmap records durable sequencing and exit gates.

This repository is licensed under the [MIT License](LICENSE).
