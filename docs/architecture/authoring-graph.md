# Authoring Graph

The graph preserves authoring intent and lineage. It is not a proof of
scientific truth and is not the default UI. This is a logical view under
[ADR 0008](../adr/0008-paper-centered-incremental-commitment.md), not a frozen
database schema.

The [framework synthesis](../design/writer-framework-synthesis.md) explains
the connected scientific, reader-path and expression loops. The graph below
shows their dependencies; it does not require a global sequence of forms.

```mermaid
flowchart TD
    Core["Selected Core snapshots"] --> EU["Evidence uses and warrants"]
    Q["Paper question"] --> C["Publication claim portfolio"]
    EU --> C
    C --> Spine["Narrative and Paper Spine"]
    Spine --> O["Section outline and paragraph allocation"]
    O --> PC["Paragraph contract"]
    PC --> SI["Sentence intent plan"]
    EU --> SI
    Q --> Capsule["Version-bound paper context"]
    C --> Capsule
    Spine --> Capsule
    O --> Capsule
    Capsule --> R["One-intent realization proposal"]
    SI --> R
    Concepts["Concept definitions and candidate labels"] --> TP["Reviewable term proposal"]
    TP --> T["Researcher-approved term locks"]
    T --> R
    S["Approved scoped style"] --> R
    R --> Review["Structural checks, semantic review, researcher acceptance"]
    Review --> Text["Mapped manuscript"]
```

Evidence and claim candidates can be explored together. The diagram describes
dependencies of a committed version, not a chronological rule that every
provisional record must already be finalized.

## Four granularities

Store individual artifacts. Discuss meaningful questions. Approve exact bundles
of coupled versions. Generate one admitted sentence candidate set at a time.
No approval is inferred from navigation, silence, chat history or a model's
report. An approval cannot cover unseen future versions.

## Proposed language and review records

A term proposal exposes the concept, scope, source-bound precedents, contrasts
and examples before the researcher chooses a label. A changed concept returns
to scientific/discourse review; a lexical preference cannot silently change it.

An anchored review issue records the selected document revision/span, observed
defect, source or contract basis, reader consequence, uncertainty and minimum
repair scope. It may route to scientific meaning, the reader plan, terminology
or same-meaning expression. An issue is not an approved patch; pass/no change
is a valid result.

A selected repair records canonical claim changes separately from changes to
expressed scope, evidence use, quantitative meaning and concept identity.
These elaborate existing logical records, not new production tables. See the
[language and revision protocol](../design/language-and-revision-protocol.md)
for proposed fields and paired validation cases.

## Currentness

Edges retain exact upstream version, consumed content/contract, reason and
effect. A new upstream version creates impact candidates; known-invalid and
unknown semantic effects block affected production. Preference-only changes
are non-blocking. Demonstrable non-semantic changes can be classified without
claiming a model proved semantic equivalence.

Keep historical versions and manuscript bytes unchanged. Revalidation records
compatibility/approval against a new upstream version instead of silently
rebinding the old artifact. Conservative review is required when dependency
granularity cannot establish non-impact. See
[RFC 0001](../rfcs/0001-authoring-ir-and-convergence-protocol.md).

## Trace and recovery

A sentence explains its question, claim, section/paragraph role, intent,
selected evidence, terms and author decisions. Background orientation is not
evidence authorization. Human-edited bytes are preserved and marked for
reconciliation rather than forced back to graph output. Operational host
receipts remain separate from scientific and authorial authority.
