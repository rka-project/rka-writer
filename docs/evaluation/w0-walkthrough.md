# W0 Paper-Centered Walkthrough

- Status: Protocol prepared; not executed with a researcher
- Purpose: test the interaction before freezing schemas or layout
- Basis: [ADR 0008](../adr/0008-paper-centered-incremental-commitment.md)
- Materials: [W1 fixture](w1-fixture-spec.md)

This is a study/inspection script, not evidence that the proposed workflow
works. Example responses below are hypothetical, not PI quotations or approvals.

## Setup and safety

Use a real-project-derived sanitized scenario with an approved question,
competing claims, source excerpts, a compact paper outline and one target
paragraph. Use supplied candidate text or static cards in W0; do not invoke a
model before its separate execution gates pass. An author can revise the
scenario rather than being forced into the facilitator's expected answer.

Keep the same research material available in a simple document-plus-contextual-
chat comparison. Do not make the baseline artificially uninformed. A single
walkthrough is formative evidence, not an effectiveness study.

The facilitator records time, decisions, confusion and author corrections.
Observation capture must be consented; do not record unrelated research data.

## Walkthrough tasks

| Step | Ask the researcher to do | Observe, without coaching the answer |
|---|---|---|
| 1. Orient | Explain the question, contribution boundary and intended reader | Can they see the paper, not just objects? |
| 2. Challenge | Compare a tempting broad claim with the bounded alternative and counterevidence | Does the workflow allow narrowing/parking without prose? |
| 3. Allocate | Locate the target paragraph in the whole-paper outline | Can they explain what belongs elsewhere? |
| 4. Discuss | Explain how this paragraph should move the reader | Is natural language enough to express intent? |
| 5. Commit | Review purpose, evidence and sentence-function plan together | Does the exact bundle make omissions and impact visible? |
| 6. Realize | Inspect supplied candidates for one admitted intent in context | Can they detect scope changes and choose expression independently? |
| 7. Calibrate | Pick/edit a same-meaning variant; decline a proposed global rule | Is local acceptance kept separate from learning? |
| 8. Reconsider | Withdraw evidence e3 and show the impact list | Is si-01 correctly included for review? Can the author choose a revision? |
| 9. Edit | Change a mapped sentence directly; introduce a second edit before acceptance | Are bytes preserved and stale patches refused? |
| 10. Resume | Close the mock session; resume from stored state, not chat | Can the author recover branch, edits and unresolved decisions? |
| 11. Read | Ask a separate reader what the paragraph argues and what it does not establish | Does correctness coexist with readable prose? |

Include a metadata-only change, advisory style change and unrelated parked
branch to check whether impact warnings are understandable rather than noisy.
Repeat the target task after removing redundant approval steps; compare effort
and comprehension, not merely click count.

## Example interaction to inspect

Researcher: "Start with the replacement example, distinguish the command from
its physical consequence, and end with the representation question."

Writer preview: "This changes the paragraph entry and intent order; it retains
the selected evidence and scenario boundary. The paper thesis and other
sections are unchanged. Here is the proposed plan and what would be affected."

The author can edit that interpretation or approve the exact displayed plan.
Do not ask for six duplicate confirmations after a clear bundle approval.
Conversely, approving the plan does not accept unseen candidate sentences.

When evidence is withdrawn, ask whether to narrow the paragraph, find new
support or park the branch. Do not suggest that merely reapproving the old
sentence restores missing evidence.

## Recording template

For each task, record:

- fixture/version, participant role, date and consent scope;
- time and number of consequential versus mechanical interactions;
- task completed unaided, with help, or not completed;
- the author's explanation of the approved meaning and scope;
- misinterpreted input, missed hidden changes, redundant confirmations;
- system-caused versus justified reopening and the author's stated reason;
- preserved/lost edits and recovery errors;
- style preference and whether its intended scope was understood;
- observed reader comprehension and any scientific mismatch;
- design change proposed, evidence, owner and unresolved concern.

Mark every result as observed, participant-reported or facilitator inference.
Do not fill this template with invented results.

## Exit and stop conditions

W0 workflow readiness requires an observed walkthrough where the author can
explain the paper/paragraph relationship, approve a bounded plan, decline style
generalization, reconsider evidence and recover direct edits without hidden
meaning changes. Record remaining problems; do not average away lost work,
unseen approvals or unsupported scientific claims.

The initial pass identifies friction; it does not establish a universal
latency/click threshold or prove superiority. Set practical effort targets
with the author before a subsequent comparison.

If the author is confused or effort exceeds their ordinary workflow, simplify
and rerun the affected tasks before freezing the contract. A successful
walkthrough still does not qualify the host or authorize production UI.

## Separate host feasibility checklist

Use supported official interfaces, synthetic context and redacted outputs:

1. Read installed host version, account type and available quota observations.
2. Determine whether an enforceable included-only/no-extra-paid-usage policy
   exists. Record unsupported or unknown explicitly.
3. Inspect effective session, instruction, tool, MCP and filesystem policy.
   Identify all ambient context and mutation routes.
4. Define a bounded canary test for forbidden reads/writes, inherited sample
   content, duplicate/late results and identity changes.
5. Run any inference-consuming conformance test only after billing protection,
   scope and researcher authorization are established.

A read-only auth probe can establish only its own observations. Never buy
credits, redeem credits, change account settings or deliberately exhaust quota
to claim qualification. If a gate is unavailable, continue manual workflow
learning and report automated inference unsupported.
