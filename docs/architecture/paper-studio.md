# Paper Studio

Paper Studio keeps the paper central and projects the same authoring state
through argument, structure and writing views. Contextual conversation supports
thinking; explicit reviewed commitments authorize state changes.

## First layout hypothesis

```text
Paper / section / paragraph location          Execution status (details on demand)
[ Argument | Structure | Writing ]

Document or outline                          Contextual discussion
Current paragraph in its surrounding paper   Current question and alternatives
                                             Preview coupled changes / approve

Evidence · impact · trace · style: expand when relevant
```

This is a mockup candidate, not a fixed three-pane architecture. Graph rows,
hashes and receipts are inspection detail. The author can change focus without
losing context; blocked production explains its prerequisites.

## Views

- **Argument:** question, claims, evidence/warrants, uncertainty and alternatives.
- **Structure:** Paper Spine, section tasks and paragraph allocation.
- **Writing:** manuscript, current intent, terms and candidate expressions.

The author can approve a displayed paragraph-purpose/intent bundle rather
than approving every storage node separately. Acceptance of prose remains
one intent at a time. Discussion, navigation and silence cannot create approval.

Requested full-paper review is read-only and isolated. Selected anchored
findings can enter the decision queue without automatically editing text.
Direct human edits are preserved and reconciled with the graph.

## Proposed term and expression interactions

Keep these interactions attached to the selected concept, paragraph or sentence
rather than introducing a required standalone Style Lab:

- **Term selection:** show the meaningful contrast between candidate labels,
  with definitions, source examples and affected uses. Let the researcher
  select, revise or defer before a Term Lock.
- **Expression issue:** highlight the passage and explain the concrete reader
  consequence against its intent/evidence/term contract. Offer discussion,
  dismissal or a selected bounded repair; do not apply criticism automatically.
- **Repair preview:** distinguish unchanged research records from corrected
  expressed meaning, show protected scope and require current base versions.
  Preserve no-change outcomes and the author's newer direct edits.

Conceptual and evidential problems lead back to argument/structure discussion.
Personal preferences can remain local; accepting a repair does not approve a
global style rule. These are proposed interactions, not capabilities already
present in the supplied-text mock. The
[language protocol](../design/language-and-revision-protocol.md) defines their
logical contracts; the [paired cases](../evaluation/w0-language-and-convergence-cases.md)
test comprehension, false alarms and effort before UI commitments are frozen.

Validate this interaction with the
[walkthrough](../evaluation/w0-walkthrough.md) before choosing a UI framework or
freezing layout. The detailed proposal is
[RFC 0002](../rfcs/0002-subscription-host-and-paper-studio.md).
