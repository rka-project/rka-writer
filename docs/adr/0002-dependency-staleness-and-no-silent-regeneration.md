# ADR 0002: Invalidate dependents instead of silently regenerating them

- Status: Accepted
- Refined by: [ADR 0008](0008-paper-centered-incremental-commitment.md); impact classification replaces blanket invalidation, while no silent rewriting remains in force.
- Date: 2026-09-03
- Decision owner: Chenglong Fu
- RKA decision: `dec_01M1MZZXK74SNS0ZNMHE47QJPB`

## Context

When an upstream question, claim, evidence interpretation, or term changes,
automatic rewriting can hide the semantic consequence and produce oscillation
across repeated revisions.

## Decision

Each artifact version records exact upstream version dependencies. An upstream
change creates a new version, computes impact, and marks affected downstream
artifacts stale. It never rewrites them. The researcher explicitly revalidates,
revises, branches, or retires affected artifacts.

Stored lifecycle and computed readiness remain separate. An accepted artifact
may be unready because a dependency is stale or a required approval is missing.

## Consequences

- Impact is visible before any rewrite.
- Dependency and readiness checks become core runtime requirements.
- The system retains obsolete versions for audit and recovery.
- W1 must test an upstream claim change as part of its exit gate.
