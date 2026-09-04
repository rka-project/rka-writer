# RKA Writer Status

- Phase: W0 — Authoring IR and Core boundary
- Product status: design; no supported authoring runtime
- Decision owner: Chenglong Fu
- Governing RKA decision: `dec_01M1MZZXK74SNS0ZNMHE47QJPB`
- Legacy baseline: `writer-skill-v0.2.0`
- Last reviewed: 2026-09-03

## Accepted direction

- Keep the existing `rka-writer` repository and re-baseline it through ordinary
  history-preserving commits.
- Make the Authoring Graph, not a draft buffer, the canonical Writer state.
- Require researcher-approved questions, claims, evidence uses, narrative
  moves, paragraph contracts, sentence intents, and term locks before prose.
- Generate one sentence at a time with full paragraph awareness.
- Mark downstream artifacts stale after upstream changes; never silently
  rewrite them.
- Keep Core authoritative for research truth and access it through a
  project-scoped Evidence Gateway.
- Preserve legacy import until a separate compatibility-sunset decision.
- Keep Reviewer execution explicitly invoked, isolated, and outside the active
  Writer distribution.

## Current gate

W0 is complete only when:

1. RFC 0001 is accepted or replaced;
2. the four foundational ADRs remain internally consistent;
3. the artifact hierarchy and dependency semantics are precise enough to
   express the W1 fixture without prose generation;
4. Core read and write-back permissions fail closed; and
5. W1 acceptance criteria can be evaluated deterministically.

## Not yet authorized by this phase

- a production database schema;
- a general-purpose editor or Paper Studio UI;
- an LLM provider integration;
- automatic paragraph or section generation;
- automatic rewrite after upstream changes;
- Writer deployment on the public Hugging Face Core demo; or
- retirement of the legacy Core import contract.
