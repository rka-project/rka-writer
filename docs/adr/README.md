# Architecture Decision Records

ADRs record accepted, architecturally significant RKA Writer decisions. Each
record states context, decision, consequences, and links to a later decision if
superseded. Accepted records are not silently rewritten when direction changes.

| ADR | Status | Decision |
|---|---|---|
| [0001](0001-authoring-state-and-ownership.md) | Accepted | Make the Authoring Graph canonical Writer state |
| [0002](0002-dependency-staleness-and-no-silent-regeneration.md) | Accepted | Track exact dependencies and never silently regenerate |
| [0003](0003-researcher-decision-and-sentence-admission.md) | Accepted | Require researcher authorization and sentence admission |
| [0004](0004-rka-core-read-and-writeback-boundary.md) | Accepted | Use a read-only Core gateway and explicit write-back |
| [0005](0005-subscription-hosted-inference-only.md) | Accepted | Delegate inference only to an authenticated subscription host |
| [0006](0006-semantic-zoom-paper-studio.md) | Superseded | Initial fixed-panel Paper Studio; replaced by 0008 |
| [0007](0007-researcher-owned-style-profile.md) | Superseded | Initial rules-only Style Profile; replaced by 0008 |
| [0008](0008-paper-centered-incremental-commitment.md) | Accepted | Paper-centered incremental commitments and validation before freeze |

ADR 0008 refines 0002, 0003 and 0005 without removing their authority,
sentence-generation or subscription-included-only boundaries. Historical bodies
are preserved; follow the refinement/supersession links for the current rule.
Accepted principles do not make the three technical RFCs validated or frozen.
