# W1 Acceptance Criteria

Validate one traceable paragraph in a paper scaffold, not a paragraph detached
from the whole argument. Use the [fixture](w1-fixture-spec.md) and record
observed results, failed cases and open limitations.

## Entry gate

The W0 author walkthrough has produced findings and a usable minimal contract;
the chosen host's auth, included-only billing and actual isolation are
established; and the researcher explicitly authorizes the bounded prototype.
A design PR merge or fake-host test is not entry evidence.

## Required slice

- Question and claim alternatives, including a rejected overgeneralization.
- Selected evidence, qualification and counterevidence with real fixture
  locators, versions and hashes.
- Paper Spine, section outline, paragraph allocation and narrative choice.
- One exact reviewed purpose/intent approval bundle; no hidden child approval.
- Minimal scoped style and required terms; one same-intent comparison and a
  declined generalization.
- One-intent candidate sets, separate acceptance and mapped document bytes.
- Evidence withdrawal, claim revision, metadata change and advisory style
  change, each with explicit impact expectations.
- Human direct editing, stale-patch refusal, duplicate result handling and
  cold-start recovery.

## Three validation layers

### Structural and state safety

Automated tests exercise authorization scope, version/locator validity,
evidence-reference allowlists, configured term checks, output bounds, impact
traversal, immutable history and document reconciliation. Test failures as well
as success, including si-01's dependency on the withdrawn e3 observation.

Require zero unauthorized accepted-state mutations, silent upstream-triggered
rewrites, silent rebinding of historical approvals, overwritten human edits,
cross-project bindings, direct provider API calls or paid-continuation paths
in the exercised cases. This is bounded test evidence, not a universal proof.

### Scientific assessment

A reviewer checks every fixture sentence against its evidence, scope and
warrant, including transitions and material counterevidence. Known support gaps
must be corrected/narrowed or left unresolved outside accepted scientific text.
Track assessor, evidence, uncertainty and disposition. Human approval is not
automatically scientific verification.

Report unsupported statements, missed broadening and false alarms. A supplied
negative example can test workflow handling but cannot establish a general
semantic detector's accuracy.

### Author and reader assessment

The author can explain the question → section → paragraph → sentence
relationship, the approved bundle and each change's impact. Observe effort,
misunderstanding, repeated confirmations and justified versus accidental
reopening. A separate reader should recover the intended bounded claim and
not infer unsupported safety/generalization results.

Record style preference separately from scientific fidelity. Do not evaluate
voice only by compliance with the system's own generated profile.

## Runtime evidence

Require supported, current authentication, host-enforced included-only usage
and actual context/tool/file isolation. Unknown properties fail closed.
A quota observation alone does not meet the billing gate. A narrow task
envelope alone does not meet the isolation gate.

Use synthetic conformance cases for auth/policy change, expiry, exhaustion,
forbidden access, stale result, timeout, cancellation and duplicate delivery.
Do not purchase or consume extra paid credits to test the boundary.
Record observed host behavior separately from fake-host results.

## Completion

Retain test artifacts, reviewer dispositions, author observations, recovery
traces and remaining limits. W1 passes only when all applicable structural,
scientific, author/reader and execution gates pass. Partial success stays
partial. Explicitly decide which contracts can freeze before expanding to W2.
