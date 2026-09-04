# RFC 0002: Subscription Host and Paper Studio Interaction

- Status: Provisional
- Owner: Chenglong Fu
- Start date: 2026-09-04
- Governing decisions: [ADR 0005](../adr/0005-subscription-hosted-inference-only.md), [ADR 0008](../adr/0008-paper-centered-incremental-commitment.md)
- Related RFCs: [0001](0001-authoring-ir-and-convergence-protocol.md), [0003](0003-researcher-owned-style-profile.md)

## Summary and goals

Paper Studio is a local, paper-centered workspace. Argument, structure and
writing views share the same Authoring Graph. Researchers discuss the paper,
not database rows. A connected subscription host may propose but cannot approve
or directly mutate canonical Writer state.

Validate two independent hypotheses: this workflow improves author control
without excessive effort, and a supported host can actually enforce the
subscription-included-only and isolation boundaries. Neither is established by
this RFC. No production editor, host adapter or UI framework is selected here.

## Interaction proposal

### Three views, one paper

| View | Main content | Contextual help |
|---|---|---|
| Argument | Question, claim portfolio, evidence, warrants and alternatives | What can we responsibly say? |
| Structure | Paper Spine, sections and paragraph allocation | What must the reader understand here? |
| Writing | Manuscript, selected paragraph and sentence | How should this admitted meaning be expressed? |

A document/outline-centered layout with a collapsible discussion sidecar is the
first mockup candidate, not a frozen panel contract. Keep readable prose or
outline in the center. Expose provenance, graph edges and execution diagnostics
on demand. Selected paper/section/paragraph context survives view changes.

The sidebar may contain ordinary conversation. A transcript is useful working
material but cannot silently become approval. A contextual summary of a
discussion must distinguish author's words, model interpretation and unresolved
questions. Do not force every conversational turn into a Decision Card.

### A consequential decision

Ask a concrete question, show why it matters, show relevant evidence and
genuine alternatives, and let the author discuss, edit, select, combine or park.
The recommended next decision is advisory. Explain blockers when the author
chooses a target that is not ready; do not force unrelated decisions first.

When ready to commit, show the exact coupled changes as one preview with
versions, exclusions and affected text. An explicit approval of that preview
is sufficient. A generic "continue" in exploratory chat does not approve hidden
details. Subsequent generation needs its own target and accepted output.

### State transitions

| Action | Prerequisite | Result | Must not happen |
|---|---|---|---|
| Discuss or inspect | Workspace access | Working notes, no canonical meaning change | Implicit approval |
| Propose a plan | Scoped task and execution gate if model-assisted | Untrusted version-bound proposal | Accepted prose |
| Approve displayed plan | Current bases, readable exact preview | Approval event for selected versions | Approval of unshown children |
| Realize sentence | Target admission and all host gates | Candidate set for one intent | Broad drafting |
| Accept/edit candidate | Current bases and resolved review blockers | Realization/anchor event | Reuse of stale approval |
| Direct human edit | Author controls document | Preserved bytes, pending reconciliation | Overwrite from old source map |
| Reopen upstream | Researcher request or reviewed new evidence | New version and impact review | Cascading rewrite |
| Review paper | Explicit review scope and isolation | Anchored advisory findings | Auto-import or auto-edit |
| Resume | Stored branch and document snapshot | Restored decisions, diffs and blockers | Guessing from chat history |

Mechanical formatting can follow an explicit bounded policy. A change that
might affect meaning is reviewed even when introduced by a human; the review
governs the system's admitted state, not the human's freedom to write.

### Sentence and style work

A candidate set contains a small number of alternatives for one admitted
intent. Review them in their paragraph, with access to paper context. Acceptance
is not a style-learning signal unless the researcher also approves a proposed
rule and its scope. Preserve keyboard/direct-edit routes; measure approval
effort in the walkthrough rather than designing a form for every object.

### Review, impact and trace

Requested full-paper review is permitted as read-only work on a frozen snapshot
with an isolated reviewer context. Findings are deduplicated and anchored.
Only selected findings enter the authoring decision queue. The reviewer cannot
approve its own advice or become the Realizer's hidden persona.

Impact shows known-invalid, needs-review and non-blocking changes separately.
Trace connects text to intent, paragraph/section role, paper claims, exact
evidence uses and decisions; operational receipts are a separate inspection.

## Execution boundary

### Preferred W1 control flow, subject to feasibility

The local Writer coordinator owns admission and canonical writes. It dispatches
an isolated request to an officially supported host interface, initially
investigating Codex App Server. Do not assume Writer can remotely control an
already-open desktop conversation.

1. The researcher initiates a scoped action in Writer.
2. Writer checks current bases, approval scope and execution gates.
3. A task-specific host context receives a read-only approved bundle.
4. The result returns as untrusted proposal data to the local coordinator.
5. Local structural checks, semantic review and researcher action determine
   whether any canonical mutation is allowed.

An alternative host-native/MCP design would have the host pull a pending ticket
and return a result; it is a separate integration experiment. An MCP connection
alone does not implement Writer-initiated dispatch or prove host isolation.
Do not blend these two control planes in one purportedly supported adapter.

### Three independent gates

| Gate | Required evidence | Insufficient evidence |
|---|---|---|
| Authentication | Official supported subscription account/session identity | Login file, environment variable or model assertion |
| Billing | Host-enforced included-usage-only route with no extra paid-credit continuation | Account type, a remaining quota percentage, or Writer refusing to buy credits |
| Isolation | Actual session/context, tool and filesystem policy verified on the installed host | A narrow prompt or read-only bundle sent into an unrestricted session |

All must be supported for the actual run. API-key, metered, exhausted, unknown,
expired or changed identity/policy states refuse new dispatch. Never route to an
API, paid credits, local model or another host on failure.

A preflight quota check is vulnerable to concurrent usage and does not reserve
capacity. Do not claim a billing guarantee unless the host enforces it
throughout execution. If the official interface cannot establish that property,
report the host unsupported for automated Writer inference and keep manual
work available. A fake adapter cannot resolve this feasibility question.

### Context and capability isolation

Use a fresh/task-scoped execution context or demonstrate an equivalent reset.
Do not inherit previous sample-analysis sessions, rejected proposals, arbitrary
conversation history, user-global instructions, unrelated MCP servers or
unrestricted workspace access without accounting for them in the policy.

The host may read only the approved bundle and write only a proposal output
location/channel. It must not have Writer acceptance credentials, Core write
tools, or filesystem write access to canonical documents. A separate
researcher-controlled write-back path remains outside the Realizer. If a host
cannot restrict ambient access through supported controls, it fails this gate.

Document the effective configuration, not just intended tool allowlists.
Tests use synthetic canaries to detect inherited context, forbidden reads and
writes; passing a finite test does not prove universal isolation.

### Logical records, not a frozen SDK

A capability observation records host/adapter version, official auth report,
billing policy evidence, isolation configuration, quota observation, supported
operations, probe time, expiry and explicit unknown fields. Never invent a
subscription attestation unsupported by the host.

A task envelope records request ID, operation, exact targets and base versions,
approval scope, paper/paragraph context manifest, support allowlist, term/style
constraints, output bound/schema and deadline. Context-only material cannot
satisfy evidence obligations.

A run receipt records observable host/session identity, policy/configuration
references, context/output hashes, times, status and host-reported usage when
available. Distinguish observed from inferred fields. A locally generated
receipt proves neither billing nor scientific correctness.

### Result handling and recovery

Validate output structure, target identity, selected references, bounded count,
exact term rules and current bases. Treat semantic broadening, evidence
entailment and copy risk as separate assessments with uncertainty. Failed
structural results are rejected; unresolved semantic concerns enter quarantine
and cannot be silently accepted.

On cancellation, timeout or lost connection, mark the request outcome unknown
until reconciled. Deduplicate late/duplicate results by request identity and
base versions. Do not automatically retry an uncertain consuming request;
verify host outcome or request an explicit new action. Canonical acceptance is
idempotent even if proposal delivery is duplicated.

Host, account or effective policy changes during a run quarantine the result.
Cancellation is not represented as a guarantee of zero usage. Offline actions
include inspection, human editing, explicit decisions, deterministic impact
analysis, export and recovery; generation and model-assisted review stop.

## Current source evidence and feasibility limits

As checked on 2026-09-04, Codex App Server documents account type/plan inspection,
rate-limit reads and structured turn output. These make it a candidate for a
probe, not a qualified adapter. OpenAI's pricing documentation also permits
credits beyond included usage, so `chatgpt` authentication is insufficient to
prove our billing boundary.
[App Server](https://learn.chatgpt.com/docs/app-server),
[pricing](https://learn.chatgpt.com/docs/pricing).

Anthropic's June 15 update pauses a previously announced SDK policy change and
currently says SDK/third-party usage draws from subscription limits. It does
not establish our isolation or no-extra-usage gate. Treat that notice's
superseded announcement below the update as historical, not current policy.
[Official SDK notice](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan).

Recheck supported interfaces and policies at implementation time. No installed
host probe or inference conformance run has been completed for this design.

## Privacy

Local-first describes storage, recovery and control. Selected content sent to a
cloud-backed subscription host leaves the machine under that host's data
controls. Show the content manifest and obtain scoped authorization before
such processing; local file selection is not permission to send unrelated
files. Store no reusable credentials and avoid manuscript text in routine logs.

## Validation and open questions

Follow the [walkthrough](../evaluation/w0-walkthrough.md). Compare the simple
document/outline-plus-sidecar layout with alternative arrangements before
freezing it. PaperMentor motivates contextual inline feedback, not our approval
workflow or a ban on whole-paper review.
[PaperMentor](https://arxiv.org/html/2606.08857v1).

Open: host-enforced no-extra-usage policy; available isolation controls; result
protocol subset; expiry and identity changes; interruption behavior; best
layout and disclosure density. Second-host parity is not a W1 requirement.

## History

- 2026-09-04: Initial subscription-host/Paper Studio proposal.
- 2026-09-04: Revised under ADR 0008: paper-centered views, explicit control
  plane, independent billing/isolation gates, review and honest receipts.
