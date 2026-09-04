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
