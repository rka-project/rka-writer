# W1 Fixture: One Paragraph Within a Paper

- Status: Synthetic design fixture, not an executed application test
- Purpose: make exact commitments, context and change expectations reviewable
- Scenario: device-command meaning after relocation or replacement
- Scope: no claim of measured performance, prevalence or universal platform limits

## Paper brief and questions

Audience: systems researchers who know that agents can invoke exposed commands.
The target paragraph motivates a representation question, not a result claim.

- Provisional question q1: How should an agent understand device behavior?
- Approved question q2: What representation supports reasoning about the
  physical preconditions and consequences of exposed commands after relocation
  or replacement in the selected scenarios?

"Approved" describes the fixture's supplied state, not a real PI approval or
proof that this research question is good.

## Claim portfolio and evidence

| Claim | Fixture disposition | Reason |
|---|---|---|
| c1: Command labels alone omit action-relevant preconditions or consequences in the selected traces | Selected, scenario-bounded | e2/e3 support only these cases |
| c2: All smart-home platforms lack semantics | Rejected | e5 and limited scope contradict the extension |
| c3: The proposed representation improves safety | Parked, unsupported | No evaluation result exists |

| Evidence use | Exact fixture role | Supported content | Cannot support |
|---|---|---|---|
| e1-v1 | Background | Command/attribute labels in the example interface | Cross-platform generalization |
| e2-v1 | Support | Selected relocation trace requires an unencoded physical precondition | Frequency or performance |
| e3-v1 | Support | Selected replacement trace changes a physical consequence while command availability remains | End-to-end safety |
| e4-v1 | Qualification | Findings apply to selected devices/traces only | Generality to all devices |
| e5-v1 | Counterevidence | Another interface exposes some semantic metadata | Adequacy for every action |

W1 must instantiate these as actual synthetic source texts with exact project,
entity, version, content hash and locator bindings. e3-v1 must explicitly
contain both command availability and the consequence observation. No "exact
binding" claim is made until the source fixtures exist and locators are checked.
e5 informs claim selection but is not selected as support for this paragraph.

## Paper Spine and section/paragraph allocation

Spine: distinguish exposed commands from action-relevant physical context,
show the bounded representation need, then define and evaluate a representation.

| Section | Reader task | Paragraph allocation |
|---|---|---|
| Introduction | Understand the bounded problem and paper question | p0: context; p1: target scenario/representation gap; p2: proposed contribution boundary |
| Representation | Understand concepts and mechanisms | Definitions first; representation and examples after |
| Evaluation plan | Understand what evidence would test the proposal | Obligations and conditions only; no invented results |
| Limitations | Understand demonstrated versus untested scope | Devices, scenarios and generality limits |

The evaluation section may remain provisional. q2, c1, the spine, Introduction
role and p1 allocation are committed for this branch. A parked alternative
branch beginning from metadata taxonomy remains independent.

Narrative options for p1: n1 representation-first; n2 scenario-first.
The supplied branch selects n2 and preserves n1 without accepting its prose.

## Target paragraph contract p1-v1

- Reader question: why is command availability insufficient in these traces?
- Job: move from a concrete scenario to the bounded representation question.
- Takeaway: an available command and its action-relevant physical meaning are
  distinct in the selected cases.
- Entry: the reader knows commands can be invoked.
- Exit: the reader understands why preconditions/consequences need examination.
- Evidence obligations: e1, e2, e3 and e4, each for its stated role.
- Must not imply: universal absence of semantics, safety gains or completed
  evaluation.
- Allocation: no Methods detail or repetition of p0's platform introduction.

## Sentence intent plan

| Intent | Function | Semantic content, not draft wording | Direct evidence |
|---|---|---|---|
| si-01 | Establish scenario | Replacement keeps a command available while changing its consequence | e3 |
| si-02 | Establish representation | Labels identify exposed commands and attributes | e1 |
| si-03 | Explain first gap | The relocation trace requires an unencoded physical precondition | e2, e4 |
| si-04 | Relate consequence to gap | The replacement consequence is not determined by command availability alone in this trace | e3, e4 |
| si-05 | Transition | Ask how to represent the relevant preconditions and consequences | Authorial warrant over c1/p1; no new empirical claim |

All five depend on p1's approved contract and plan as well as their direct
evidence. A transition is not fabricated evidence; its trace names its
rhetorical role and approved warrant.

One displayed bundle can approve p1's purpose and intent plan against exact
q2/c1/evidence/spine/outline versions. It cannot accept future sentence text.
If a base changes during preview, rebuild it. A partial bundle cannot omit
required evidence review.

## Context and style

Each realization sees the version-bound paper capsule, Introduction role and
p1 allocation; p1's full intent sequence and accepted neighbors; and only
evidence authorized for the current intent as factual support. Paper orientation
and counterevidence summaries are not a hidden support allowlist.

Minimal style: direct language, visible actor/action, scenario-appropriate
qualification and approved labels for "device capability" and "physical
consequence". Keep scientific scope in c1, not merely in a tone preference.
Required labels are locks; prose preferences are advisory.

Optional synthetic author-written and admired samples can ground observations.
Use a same-intent contrast for si-02 with meaning held fixed. The author accepts
a local expression but declines a paper-wide rule. A second case explicitly
promotes a section-scoped preference and records its override relationship.
The initial realization context is rules-only. Small approved examples are a
separate variant, never an implicit dependency of the baseline.

## Change cases and exact expectations

### A. Withdraw the consequence observation

Replace e3-v1 with e3-v2 stating that command availability was observed but the
consequence attribution is unverified. This is a real loss of support, not a
rename of what e3 already said.

| Object | Expected impact |
|---|---|
| e3's original consequence use | Known-invalid against the new source |
| c1, selected spine/outline obligations and p1 | Needs-review through their dependency on that use |
| si-01 and si-04 | Needs-review directly and through p1 |
| si-02, si-03 and si-05 | Needs-review through p1/plan; unchanged direct evidence does not automatically clear them |
| Old realizations and approvals | Retained as historical, not silently relabeled current |
| Independent parked branch and style source files | No impact absent an actual dependency |
| All manuscript bytes | Unchanged by impact detection |

The researcher may narrow the paragraph to the e2-supported relocation case,
seek new evidence, or park it. A revalidated surviving intent gets a new
compatibility/approval record; its old lineage remains intact. Do not leave
si-01 unaffected as the earlier fixture did.

### B. Narrow the publication claim

Create c1-v2 restricting the selected interpretation to the relocation case.
Traverse the actual spine/outline/p1/intent dependencies; review the replacement
scenario and transition rather than regenerating them. No accepted text changes
until a reviewed patch is explicitly accepted.

### C. Metadata-only source revision

Change e1's display title but retain identical consumed source text, locator
and proposition. Record the new binding and a verifiable non-semantic
classification/compatibility event. Old approvals keep their old bindings;
no semantic rewrite or global reapproval is required. If consumed fields cannot
be verified unchanged, classify needs-review instead.

### D. Advisory style change

Change an advisory actor-placement preference. Recommend scoped style review;
do not mark c1 unsupported or alter manuscript bytes. A required term change is
a separate lexical review case.

### E. External edit and interrupted acceptance

The author edits an accepted sentence directly. Preserve bytes, snapshot the
base and show reconciliation. If the author edits it again before accepting
the proposed mapping, refuse the old patch and re-preview. Simulate a crash
after a recorded approval but before file update; recover to a consistent,
auditable outcome without applying the patch twice.

## Failure cases

- Broadening candidate: review detects loss of scenario scope; quarantine until
  corrected or assessment resolved. A labeled fixture is not a general detector.
- Forbidden alias: structural term check catches an exact configured alias;
  this says nothing about unlisted synonyms.
- Distinctive copied phrase: a synthetic seeded phrase is flagged; replacement
  or quotation/false-positive review is required.
- Hidden approval: added intent not in the reviewed bundle cannot be accepted.
- Unselected source: a factual support reference to e5 is refused for this
  target; the author may propose a separately reviewed selection.
- Stale/duplicate result: quarantine stale bases and deduplicate delivery.
- Host `chatgpt` auth with unknown extra-credit policy: refuse dispatch.
- Host with all three verified gates: eligible only after target admission.
- Inherited unrestricted tools or prior sample context: fail isolation.
- Exhausted/disconnected host: preserve manual editing, review and export.

## Evidence still to be produced

Concrete synthetic source files, candidate texts, exact version IDs/hashes,
approval events, document snapshots and expected transition traces are W1 test
data to implement after the gate. W0 uses the explicit scenario for walkthroughs.
Runtime behavior, billing, semantic validity and user benefit are not established
by this specification.
