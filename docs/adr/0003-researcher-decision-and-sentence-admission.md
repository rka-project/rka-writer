# ADR 0003: Require researcher authorization before sentence realization

- Status: Accepted
- Date: 2026-09-03
- Decision owner: Chenglong Fu
- RKA decision: `dec_01M1MZZXK74SNS0ZNMHE47QJPB`

## Context

A language model can silently choose claim strength, evidence meaning,
paragraph purpose, and terminology while generating fluent prose. Post-draft
review does not reliably reveal all of those choices.

## Decision

Consequential meaning is proposed through reviewable Decision Cards and
semantic patches. Only the researcher may approve it. A Sentence Intent may be
realized only after its paragraph contract, claim and evidence obligations,
scope, rhetorical function, term locks, and dependencies pass admission.

Writer generates one sentence candidate set at a time with full paragraph
awareness. Acceptance, edit-and-accept, rejection, and alternatives are
explicit events. A cohesion pass may not silently change approved meaning.

## Consequences

- Interaction is multi-round by design but focuses on high-impact decisions.
- Prose generation becomes bounded and testable.
- Writer needs permissions and admission diagnostics before an LLM gateway.
- Whole-section generation is outside the initial product contract.
