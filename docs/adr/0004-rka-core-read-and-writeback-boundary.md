# ADR 0004: Read Core through a gateway and write back only by confirmation

- Status: Accepted
- Date: 2026-09-03
- Decision owner: Chenglong Fu
- RKA decision: `dec_01M1MZZXK74SNS0ZNMHE47QJPB`

## Context

Writer needs RKA evidence and provenance but must not import Core internals,
open Core storage, copy the whole database into model context, or allow draft
activity to mutate research truth.

## Decision

RKA-backed mode uses a project-scoped, read-only Evidence Gateway over Core's
public contract. Every durable binding records entity identity, type, revision,
content hash, locator, relation, and retrieval time.

Write-back is exceptional and limited to durable research meaning explicitly
confirmed by the researcher. Writer previews the exact mutation, receives
confirmation, writes idempotently, and reads back the resulting Core entity.
Draft prose, reviewer findings, rejected alternatives, prompts, and style edits
are ineligible.

Standalone import may create provisional evidence but cannot claim Core
authority or provenance.

## Consequences

- Core and Writer remain independently installable and releasable.
- Writer needs a capability-filtered adapter rather than the previous full MCP
  compatibility example.
- Offline work may use a pinned evidence snapshot with visible age.
- Write-back behavior can be audited independently of drafting.
