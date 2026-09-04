# ADR 0001: Make the Authoring Graph canonical Writer state

- Status: Accepted
- Date: 2026-09-03
- Decision owner: Chenglong Fu
- RKA decision: `dec_01M1MZZXK74SNS0ZNMHE47QJPB`

## Context

Draft text alone cannot preserve why a sentence exists, which claim it
expresses, what evidence supports it, or which researcher decision authorized
its meaning. A chat transcript is similarly unsuitable as durable state.

## Decision

Writer's canonical structured state is a versioned Authoring Graph. First-class
artifacts include paper questions, publication claims, evidence uses, narrative
moves, paragraph contracts, sentence intents, term locks, and sentence
realizations. Manuscript text is a mapped output of this graph, not its
replacement.

Core remains authoritative for research records and provenance. Writer remains
authoritative for manuscript organization, authoring decisions, and expression.

## Consequences

- Every accepted sentence can be traced to structured meaning.
- Writer requires versioned artifact storage and stable source maps.
- Direct manuscript edits need later reconciliation with Authoring Graph state.
- A prose-only generation pipeline cannot satisfy the product contract.
