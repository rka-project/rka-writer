# RFC 0001: Authoring IR and Convergence Protocol

- Status: Provisional
- Owner: Chenglong Fu
- Start date: 2026-09-03
- Governing refinement: [ADR 0008](../adr/0008-paper-centered-incremental-commitment.md)
- Related RFCs: [0002](0002-subscription-host-and-paper-studio.md), [0003](0003-researcher-owned-style-profile.md)
- Supersedes in part: [platform design v0](../history/platform-design-v0.md)

## Summary

Writer helps a researcher decide what a paper should say, why the evidence
supports it, and how readers should encounter it. A versioned Authoring Graph
preserves those decisions. It is not an automatic proof of correctness and
does not require the author to operate a graph editor.

The progression is question → claim portfolio and evidence uses → narrative
and Paper Spine → section/paragraph outline → paragraph contract → sentence
intents → term locks → sentence realizations. It is a dependency structure,
not a compulsory global wizard. The three loops below can reopen each other
through explicit, scoped decisions.

## Goals and non-goals

Preserve meaning, provenance, researcher control, full-paper awareness and
recoverability across revisions. Make interactions worth the researcher's
attention and expose uncertainty instead of treating fluent prose as evidence.

Do not generate a paper or section in one step, move research truth into
Writer, expose the whole Core database to a model, or freeze storage/UI
technology before the narrow workflow is evaluated. HF work is independent.
Provider APIs, paid continuation and local-model fallback remain excluded.

## Three connected loops

### Epistemic: what can this paper responsibly claim?

Start from the researcher's question and retrieve reviewed, project-scoped Core
records. Compare candidate claims, selected evidence, counterevidence,
uncertainty, warrants and prohibited extensions. Retrieval success and
researcher preference are not proof of support. An unsupported attractive claim
can be narrowed, parked or returned to research; it must not be rescued by prose.

### Discourse: what does the reader need, and in what order?

Select a Paper Spine, section roles, paragraph allocation and narrative moves.
For each paragraph, establish its reader question, takeaway, entry/exit state
and evidence obligations. Plan sentence functions together where they form one
argument. New insight here may reopen a claim; reopening is not itself failure.

### Linguistic: how should this approved meaning be expressed?

Establish an early optional Style Brief. Stabilize concepts, then lock needed
terms before realizing an intent. Generate one sentence candidate set at a time
with paper and paragraph awareness. Meaning-changing edits return to the
appropriate loop. A cohesion pass proposes bounded changes; it cannot silently
merge, split or change approved intents.

## Granularity and approval

| Layer | Unit | Example |
|---|---|---|
| Storage | Individual versioned artifact | Evidence Use or Sentence Intent |
| Discussion | One consequential question | Why does this paragraph belong here? |
| Approval | Exact displayed coupled changes | Paragraph purpose plus its intent plan |
| Generation | One admitted intent | One sentence candidate set |

A Decision Card is a rendering of a decision, not a required form for every
object. Natural-language input can become a proposal. The researcher sees what
the interpretation changes, what stays unchanged, alternatives and impact.
Do not ask again when a direct UI action already clearly approves the exact
displayed versions; ambiguous conversation cannot count as that action.

An approval bundle records actor, event time, selected artifact/version IDs,
base revisions, exclusions and a digest of the reviewed preview. Partial
approval is permitted only for an independently ready subset. Recompute the
preview if any base changes. Never append hidden approvals for omitted fields,
future revisions, unreviewed children or subsequently generated sentences.

The scheduler prioritizes contradictions, missing central evidence and scope
before local wording. It recommends, explains and allows the author to park or
change focus. Coupled choices may be reviewed together; measure comprehension
and effort rather than enforcing an arbitrary universal batch size.

## Minimal logical model

These are logical records, not a committed table-per-type database schema:

- paper question and thesis kernel;
- publication claim portfolio, including rejected/parked alternatives;
- Evidence Uses with warrants, qualifiers and exact Core bindings;
- Paper Spine, section roles, paragraph allocation and narrative selection;
- Paragraph Contracts and Sentence Intent plans;
- concept/term entries and approved Term Locks;
- sentence proposals, accepted realizations and document anchors;
- researcher decisions, approval bundles and immutable artifact versions.

RFC 0003 adds a minimal profile and its selected-source provenance. RFC 0002
adds host observations and execution records. Operational records cannot stand
in for author approval.

## Paper and paragraph context

A version-bound paper context capsule contains the active question, thesis,
selected claims and boundaries, Paper Spine, current section role, paragraph
allocation, relevant definitions/first-use locations, and what is already
established versus deferred. It references exact approved artifacts rather
than a free-running model summary. Provisional neighboring plans are labeled
orientation only and cannot authorize new facts.

The detailed context adds the whole paragraph contract and intent sequence,
accepted neighbors, current intent's evidence, terms and applicable style.
Differentiate context-only material from evidence authorized to support this
sentence. Inspecting or mentioning a source in the capsule does not select it
as evidence. Neither rejected wording nor whole conversation histories are
silently carried into realization.

A paragraph can proceed without finalizing all later sections. Its required
question/claim/spine/section commitments must be ready; unrelated parked
branches must not block it.

## Dependency effects and currentness

Every edge names exact upstream versions, the consumed proposition/contract
or field set, its reason, and whether it is a semantic, lexical, structural,
context-only or preference dependency. Exact historical lineage is immutable.

When upstream changes:

1. Preserve the old version, bindings, approval events and manuscript bytes.
2. Traverse relevant edges and create an impact record, never a rewrite.
3. Classify each candidate as known-invalid, needs-review, non-blocking
   preference review, or demonstrably unaffected, with the basis recorded.
4. Block affected production for known-invalid and unknown semantic effects.
   Continue read-only inspection and human editing.
5. Let the researcher revalidate, revise, branch, park or retire. Revalidation
   creates a new compatibility/approval event or artifact version referencing
   the new upstream state; it does not mutate the old approval.

A narrow metadata diff may be classified mechanically only if consumed
content/locators and relevant contracts are verifiably unchanged. A model's
claim that two texts mean the same thing is not such proof. If dependency
granularity is insufficient, conservatively review the reachable subgraph.
A sentence linked to a changed paragraph contract is not automatically
unaffected just because its direct evidence stayed unchanged.

Lifecycle (proposed/accepted/retired) is separate from readiness and review
state. Offline work may retain a deliberately pinned snapshot with visible
freshness uncertainty, not a false claim to latest-Core validity.

## Admission, review and acceptance

Pre-generation admission checks the target branch's dependencies, recorded
researcher decisions, required terms, unresolved blockers and execution gate.
It checks that the prerequisite reviews happened, not that science is proven.

| Layer | Examples | Authority |
|---|---|---|
| Deterministic checks | References, versions, permissions, numeric literals, exact term constraints, output shape | Program-enforced within declared coverage |
| Semantic review | Evidence entailment, implicit broadening, omitted caveat, misleading causality | Evidence-grounded assessment with uncertainty |
| Researcher/reader judgment | Intended emphasis, clarity, voice, contribution visibility | Explicit human judgment |

Results first pass structural checks, then expose semantic/style/copy-risk
findings and their evidence. Semantic suspicion is quarantined for review, not
reported as a proven detector result. Unresolved support or material-scope
problems block admission to the accepted scientific text. A researcher may
correct the assessment or narrow the intent with recorded rationale; approval
alone cannot label unsupported content scientifically verified.

The author accepts, edits-and-accepts, rejects or requests alternatives for one
intent. Changes to function, scope, evidence or terms reopen the relevant
contract. Formatting-only changes can use an explicitly bounded policy.

## Human editing and recovery

The author may write notes or edit prose directly, including before completing
the ladder. This permission is not delegated to the agent. Preserve the actual
file bytes and distinguish scratch/unreconciled text from admitted text.

On external edits, compare against the last mapped document revision, preserve
a recoverable snapshot, show a diff and propose intent/anchor reconciliation.
Meaning-uncertain edits require review. If the base changes during acceptance,
stop and re-preview; do not overwrite a newer edit. Split/merged sentences
require an explicit remapping decision. W1 exercises this on one local document,
without building a collaborative editor.

Cold start restores current branch, exact approvals, unreconciled edits, open
impact reviews and the next decision from stored state, not model memory.

## Core and storage boundaries

Use the public project-scoped read-only Evidence Gateway; preserve identity,
revision/hash, locator, relation and retrieval time. Check scope, evidence
assessment and contradictions before using a Core claim. No direct Core DB or
internal imports. Standalone evidence is provisional and cannot claim Core
provenance.

Durable research write-back is exceptional: exact preview → researcher
confirmation → idempotent write → read-back. Prose, style and review chatter do
not become Core research truth.

Local files versus SQLite remains a narrow prototype question. Export must
preserve authoring state, manuscript bytes, source maps, decisions and bindings
without a model provider. Do not implement both storage engines before learning
what recovery and concurrency the first slice actually needs.

## Validation, alternatives and open questions

Use the [W0 walkthrough](../evaluation/w0-walkthrough.md) and
[W1 fixture](../evaluation/w1-fixture-spec.md). Test whether an author can explain
the resulting argument and changes without becoming a form filler. Keep a
conventional document-plus-contextual-chat baseline with the same material.

Prose-first generation loses authority boundaries; a global approval wizard
over-constrains iteration; a full editor first delays testing the central
interaction. The proposal instead tests a paper scaffold plus one paragraph.

Open: smallest useful approval bundle; sufficient paper capsule; dependency
field granularity; direct-edit remapping; practical style-rule set; storage.
A documentation merge is not acceptance evidence for these questions.

## History

- 2026-09-03: PI ratified the direction; technical RFC opened as Provisional.
- 2026-09-04: Subscription/style proposals added.
- 2026-09-04: PI-approved review separates granularities, restores whole-paper
  context, qualifies guarantees and moves human validation/reconciliation early.
