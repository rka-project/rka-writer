# RFC 0001: Authoring IR and Convergence Protocol

- Status: Provisional
- Owner: Chenglong Fu
- Start date: 2026-09-03
- Tracking issue: not yet created
- Supersedes in part: `docs/history/platform-design-v0.md`
- Related RKA decision: `dec_01M1MZZXK74SNS0ZNMHE47QJPB`
- Related ADRs: ADR 0001 through ADR 0004

## Summary

RKA Writer should treat academic writing as progressive semantic convergence,
not prompt-to-prose generation. It compiles reviewed Core knowledge and
researcher decisions into a versioned Authoring Graph. Sentence text is emitted
only after a paper question, publication claim, evidence use, narrative move,
paragraph contract, sentence intent, and terminology constraints are ready.

## Motivation

The previous platform design correctly separated research, argument, and
document truth, but still moved too quickly from a paper spine to multi-
paragraph drafting and relied on post-draft grounding. That allows the model to
make consequential choices while realizing prose and makes repeated revision
prone to semantic drift or oscillation.

The Writer must instead preserve which researcher decision authorized each
meaning, which exact upstream versions it depends on, and what becomes stale
when an upstream assumption changes.

## Goals

- create a typed path from paper question to sentence realization;
- preserve exact claim, evidence, narrative, paragraph, and terminology
  decisions;
- make researcher interaction multi-round but high-information-density;
- separate artifact lifecycle from computed downstream readiness;
- invalidate stale dependents without automatic rewriting;
- support cold-start recovery and oscillation detection; and
- provide exact traceability from manuscript sentences to Core sources and
  researcher authorization.

## Non-goals

- generating a whole section or paper from a single prompt;
- forcing the researcher to edit raw schemas;
- exposing all RKA records to the drafting model;
- making Reviewer findings automatic drafting inputs;
- freezing production storage or UI technology before W1; or
- coupling Writer development to the Hugging Face Core demo.

## Three convergence loops

### Epistemic convergence

Converge from Core research questions, claims, observations, and sources to the
paper question, publication claims, evidence uses, scope, and warrants that the
paper may responsibly express.

### Discourse convergence

Converge from approved meaning to the Paper Spine, section roles, narrative
moves, paragraph contracts, sentence intents, and transitions that guide the
reader.

### Linguistic convergence

Converge from concepts and community terminology to locked terms and bounded
sentence realizations. Language choices may vary; approved meaning may not.

## Authoring Graph

Every first-class artifact has an immutable version, status, author or
proposer, approval event, exact upstream versions, and downstream edges.

Minimum W1 artifact types are:

- `PaperQuestionVersion`;
- `PublicationClaimVersion`;
- `EvidenceUse`;
- `NarrativeMove`;
- `ParagraphContract`;
- `SentenceIntent`;
- `TermEntry` and `TermLock`; and
- `SentenceRealization`.

Global infrastructure includes `CoreBindingSnapshot`, `WriterArtifact`,
`ArtifactVersion`, `DependencyEdge`, `DecisionCard`, `SemanticPatch`, and
`SourceMap`.

## Dependency and staleness semantics

An artifact version depends on exact upstream version identifiers, not only
logical object identifiers. Changing an accepted upstream object creates a new
version and computes downstream impact. Affected dependents become stale; no
dependent text is regenerated automatically.

The researcher chooses whether to revalidate, revise, branch, or retire stale
artifacts. The system records that decision. Repeated reopening of settled
high-level artifacts without new evidence is surfaced as possible semantic
oscillation.

## Lifecycle and readiness

Stored lifecycle records states such as proposed, accepted, rejected, locked,
superseded, and retired. Readiness is computed from current dependencies,
required approvals, unresolved contradictions, term locks, evidence bindings,
and staleness.

Downstream production is allowed only when the artifact's admission rule
passes. A stored `accepted` state is insufficient if an upstream dependency has
changed.

## Researcher interaction

Writer presents the next consequential decision through a `DecisionCard` with
the current question, recommendation, genuinely different alternatives,
evidence, affected artifacts, and reversibility. The researcher may respond in
natural language; Writer converts that response into a previewed semantic
patch and asks for confirmation when meaning would change.

The next-question scheduler selects the unresolved decision with the greatest
downstream impact, subject to dependency order and cognitive load. It does not
ask the researcher to approve every mechanical detail.

## Sentence admission and realization

A Sentence Intent is eligible for realization only when:

- its Paragraph Contract is accepted and current;
- its publication claim and evidence obligations are current;
- required terms are locked;
- the intended rhetorical function and scope are explicit;
- no blocking contradiction or unresolved researcher decision remains; and
- the requesting actor has permission to realize prose.

Writer emits one sentence candidate set at a time. The model receives the
approved Paragraph Contract, all sentence intents in the paragraph, accepted
neighboring realizations, locked terminology, and only the evidence required
for the current intent. The researcher accepts, edits-and-accepts, rejects, or
requests alternatives. A later cohesion pass may adjust bounded connective
language but cannot change claims, evidence use, term locks, or sentence
functions silently.

## Core integration

RKA-backed mode is the primary product path. A project-scoped, read-only
Evidence Gateway retrieves only selected Core entities and records project ID,
entity ID and type, revision, content hash, locator, relation, and retrieval
time. Standalone import may create provisional local evidence, but it must not
pretend to have Core provenance.

Write-back is exceptional. Only researcher-confirmed durable research meaning
is eligible. Writer previews the exact Core mutation, receives confirmation,
performs an idempotent write, and reads the resulting entity back. Draft prose,
reviewer chatter, rejected alternatives, and style edits are ineligible.

## Storage boundary

Writer's canonical structured state is local and versioned; the initial
implementation choice between repository files and SQLite remains open until a
narrow W1 prototype measures both. Canonical manuscript bytes live in a local
Git repository and are connected to Writer artifacts through stable source
maps. Portable export must include structured state, manuscript bytes, source
maps, approvals, and Core bindings without requiring a model provider.

## Alternatives

### Continue the Writer 0.2 skill

It is small and usable but cannot enforce exact dependencies, readiness,
permission boundaries, staleness, or bounded realization.

### Build the editor first

This would create a large integration surface before validating whether the
semantic convergence model improves writing.

### Generate paragraphs and ground afterward

This is simpler, but it allows hidden claim, evidence, narrative, and term
choices to enter prose before researcher approval.

### Put authoring state back in Core

This would reverse the product boundary and make research truth depend on an
optional writing application.

## Risks and mitigations

- **Over-structuring creativity:** keep interaction natural-language-first and
  require approval only for consequential meaning.
- **Decision fatigue:** schedule the highest-impact unresolved decision and
  batch only genuinely coupled choices.
- **False convergence:** expose branch comparison, reopening reasons, and
  oscillation signals.
- **State complexity:** validate only one paragraph before generalizing the
  schema.
- **Context leakage:** compile minimal task-specific context and isolate
  Reviewer execution.
- **Premature architecture:** keep storage, UI, and provider choices provisional
  until W1 evidence exists.

## Acceptance evidence

RFC implementation may begin only when a sanitized fixture can express the W1
artifact chain, exact version dependencies, permissions, admission result,
source trace, and upstream invalidation without relying on generated prose.

W1 succeeds only when one real-project-derived, sanitized scenario produces a
fully grounded paragraph and a subsequent upstream claim change marks the
correct dependents stale without changing manuscript text.

## Unresolved questions

- Does W1 structured state begin as repository files or local SQLite?
- What is the minimum semantic patch representation needed for natural-language
  researcher input?
- Which Core read operations provide the smallest stable Evidence Gateway?
- Which sentence-level edits qualify for a non-semantic cohesion patch?
- What interaction cadence minimizes cognitive load without hiding decisions?

## Future possibilities

After W1, Writer may add semantic zoom, richer branch comparison, Git/LaTeX
integration, isolated review import, and a synthetic guided demonstration. None
of those possibilities is evidence for accepting a broader W0 implementation.

## History

- 2026-09-03: Product direction ratified by the PI and RFC opened as
  Provisional for technical refinement.
