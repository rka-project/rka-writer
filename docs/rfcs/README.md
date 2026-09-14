# RKA Writer RFCs

RFCs hold substantial proposals while they are being discussed. Each RFC names
its status, owner, tracking issue, superseded material, unresolved questions,
and acceptance evidence.

Statuses are `Provisional`, `Accepted`, `Rejected`, `Deferred`, or `Replaced`.
An accepted RFC may guide implementation, but architecturally significant
choices should also be captured as focused ADRs.

| RFC | Status | Subject |
|---|---|---|
| [0001](0001-authoring-ir-and-convergence-protocol.md) | Provisional | Authoring IR and convergence protocol |
| [0002](0002-subscription-host-and-paper-studio.md) | Provisional | Subscription host and Paper Studio interaction |
| [0003](0003-researcher-owned-style-profile.md) | Provisional | Researcher-owned term, prose, and tone profile |

[ADR 0008](../adr/0008-paper-centered-incremental-commitment.md) accepts the
revised product principles, not the untested layout, schemas or host mechanism.
The [W0 walkthrough](../evaluation/w0-walkthrough.md) and independent execution
gates provide evidence for accepting a narrow implementation subset. Merging
these proposals does not mark W0/W1 complete.

## Consolidated working design

Start with the [framework synthesis](../design/writer-framework-synthesis.md)
for the author-facing scientific, reader-path and expression loops. The
[language and revision protocol](../design/language-and-revision-protocol.md)
elaborates the three RFCs with term selection, anchored issues and change
accounting; it is not a separate accepted architecture or installed skill.

The [source observations](../research/2026-09-14-writing-workflow-observations.md)
separate source findings from design hypotheses. The
[RKA index](../research/writer-rka-index.md) identifies approved authority and
preserved history. Test the proposed refinements through the
[W0 language cases](../evaluation/w0-language-and-convergence-cases.md).
