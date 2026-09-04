# ADR 0006: Use a semantic-zoom Paper Studio and Decision Surface

- Status: Superseded
- Superseded by: [ADR 0008](0008-paper-centered-incremental-commitment.md)
- Date: 2026-09-04
- Decision owner: Chenglong Fu
- RKA decision: `dec_01M1PSYMEJVEEGYP7CN5C7D3HY`

## Context

An editor with a generic chat panel is familiar but lets broad requests bypass
the Authoring Graph. A linear wizard makes dependency order visible but is too
rigid for research iteration. Writer needs a familiar interface that keeps
paper-level meaning, local paragraph work, evidence, and downstream impact
connected.

## Decision

The primary interface is a semantic-zoom Paper Studio. Its left pane navigates
paper, section, paragraph, sentence, and style artifacts; its center canvas
renders the selected artifact, source, diff, or PDF; its right Decision Surface
presents the next consequential Decision Card; and a collapsible drawer shows
selected evidence and provenance.

Natural-language discussion is available within the selected decision context.
Any meaning-changing interpretation returns as a previewed semantic patch. The
primary actions resolve decisions, compare branches, inspect evidence and
impact, plan a paragraph, lock required terms, and realize one admitted
sentence.

Paper Studio does not center broad paper or section generation, full-manuscript
improvement, automatic review, generic chat, or a Writer-owned model selector.
The subscription host appears as read-only operational status.

## Consequences

- Researchers can move between levels without bypassing admission rules.
- The current artifact and its unresolved decision remain visible together.
- Conversation is useful for thinking but cannot become an unreviewed mutation
  path.
- Paper-level branches and rejected alternatives remain inspectable.
- UI implementation follows W1 contract validation; the ADR does not select a
  web, desktop, or extension technology.

## Alternatives rejected

### Generic chat plus editor

This makes a transcript the practical source of intent and hides structured
dependencies.

### Strict sequential wizard

This over-constrains legitimate research iteration and makes cross-level
inspection cumbersome.

### Model-centric control panel

Model selection belongs to the subscription host and does not authorize
scientific meaning.
