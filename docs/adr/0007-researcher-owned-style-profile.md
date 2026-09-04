# ADR 0007: Make language calibration a researcher-owned Style Profile

- Status: Superseded
- Superseded by: [ADR 0008](0008-paper-centered-incremental-commitment.md)
- Date: 2026-09-04
- Decision owner: Chenglong Fu
- RKA decision: `dec_01M1PSYRNQ630HENRWDR5TBK8X`

## Context

A free-form instruction to write like several papers collapses terminology,
prose structure, tone, venue convention, author preference, and source wording
into an opaque prompt. Frequency in samples is not researcher approval, and
passing complete samples into realization increases copying risk.

The researcher wants to establish language direction from the beginning while
preserving concept-first, sentence-intent-first convergence.

## Decision

Writer asks for explicit style preferences and optionally two to five
researcher-selected sample papers with declared roles. A subscription host may
propose source-grounded Style Observations. Only the researcher may promote,
edit, reject, scope, and assign strength to atomic term, prose, and tone rules.
Approved rules form an immutable `StyleProfileVersion`.

An early Style Brief guides planning. Exact terminology is locked only after
concepts and sentence functions are stable. Before realization, Writer computes
a `ResolvedStyleContract` for the current paragraph or sentence. The Realizer
receives this bounded contract, not complete sample papers.

Scientific meaning, evidence, material qualifications, venue requirements, and
Term Locks outrank prose and tone preferences. Distinctive phrase copying is a
blocking review condition. Style changes produce impact and review state but
never automatic rewriting.

## Consequences

- Author voice becomes inspectable, editable, versioned, and traceable.
- Own writing, admired papers, venue examples, and negative examples remain
  distinguishable.
- Term rules can block realization while soft preferences remain advisory.
- Sample files remain local and explicitly selected.
- W1 must test source locators, conflicts, precedence, minimal realization
  context, copy risk, and style-change impact.

## Alternatives rejected

### Free-form imitation prompt

This is not auditable and can copy source wording or smuggle unapproved
preferences into prose.

### One global style vector

This cannot explain why a rule applies or distinguish section type, tone,
terminology, and prose structure.

### Calibrate from an AI-generated paragraph

This generates prose before semantic admission and entangles style approval
with unapproved scientific meaning.
