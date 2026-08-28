# Internal NSF PI Clarification Sidecar

Use this sidecar only for a proposer-owned or institution-authorized NSF proposal after the native mock review has been completed and frozen. This is an internal diagnostic conversation with the PI, not an NSF rebuttal, panel response, Program Officer exchange, or official review stage.

## Freeze before asking

Retain the reviewed proposal version, authority snapshot, sealed individual reviews, panel summary, ratings, assurance label, validation report, and their hashes when available. Do not overwrite or append fields to native JSON. Record the frozen review identifiers and hashes at the top of `pi-clarification-sidecar.md`.

Do not ask the PI to explain the science before the cold review is frozen. Doing so would teach the reviewer the intended argument and invalidate the self-containment test.

## Ask decision-relevant questions

Ask a small numbered batch only when an answer could change the internal diagnosis, confidence, requested repair, or interpretation of a finding. Prioritize premise, novelty, evaluation, feasibility, Broader Impacts, and severe comprehension ambiguities. Ask for a concise answer and an existing proposal location when one exists.

On the first clarification turn, deliver the frozen review and question batch, then stop and wait. Never infer, simulate, or pre-fill PI answers. Unanswered questions remain unresolved.

Use this response prompt:

```text
Question ID:
Concise PI response:
Existing proposal/supplement location, if any:
New internal evidence, if any:
Claim or scope change, if any:
Planned proposal revision, if any:
Confidentiality or external-verification restriction:
```

## Preserve the sidecar distinction

For each actual response, record:

- linked native finding and question ID;
- faithful PI response and supplied time;
- whether support was already in the frozen proposal, is new internal evidence, is a planned revision, narrows a claim, disputes the review, or cannot be provided;
- linked post-freeze artifact hashes and confidentiality limits;
- internal re-evaluation, remaining proposal weakness, and required proposal action; and
- whether the explanation would be visible to a real reviewer in the submitted package.

Only a verified pointer to sufficient material already in the frozen proposal can resolve the concern in that frozen version. A credible private explanation remains missing-from-proposal; new evidence requires inclusion and fresh review; a planned change is not a completed repair.

Do not change native reviewer ratings, panel disposition, assurance, sealed findings, or validation records in response to the sidecar. If useful, add a clearly labeled `internal clarification note` that states what the PI's answers suggest about revision feasibility, without presenting a revised official or mock-panel rating.

## End or transition

End when remaining issues require proposal revision, new evidence, or another round would not change the diagnosis. Preserve every round append-only.

When a revised proposal is supplied, freeze it separately and invoke the NSF engine's native `revision-check`. Link the sidecar as history, but judge resolution from the original finding, both frozen proposal versions, and the actual diff—not from the PI's claim that an issue was fixed.
