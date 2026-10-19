# RKA Writer Status

- Phase: W0 — Workflow and feasibility learning
- Product status: design; no supported authoring runtime
- Decision owner: Chenglong Fu
- Last reviewed: 2026-10-19 (review-practice UI and design review; no runtime qualification)
- Governing RKA decision: `dec_01M1MZZXK74SNS0ZNMHE47QJPB`
- Runtime boundary: `dec_01M1PKYTMA70XG0EVZPD7QSM2S`
- Current UI direction: `dec_01M1PY0THCZN1V9Y3VEF9W02M7` (supersedes UI-1)
- Current style direction: `dec_01M1PY0X8EG51QGGQC9X9YAZ75` (supersedes STYLE-1)
- Validation refinement: `dec_01M1PY125H61RR3GXB0KWV571W`
- Legacy baseline: `writer-skill-v0.2.0`

## Accepted principles versus unvalidated proposals

[ADR 0008](docs/adr/0008-paper-centered-incremental-commitment.md) preserves the
foundational authority and generation boundaries while superseding the fixed
UI and rules-only style commitments in ADR 0006/0007.

Accepted: researcher-owned meaning, Core/Writer separation, explicit approvals,
sentence-level agent generation, exact historical lineage, no silent rewrite,
subscription-included-only execution, paper-centered views and early learning.

Provisional: exact layout, approval bundle size, paper-capsule representation,
dependency granularity, storage, style onboarding, optional example contexts,
host protocol and billing/isolation enforcement mechanisms. RFC 0001–0003 remain
Provisional. Approval of this documentation does not approve every technical
choice or qualify an adapter.

The [September 14 synthesis](docs/design/writer-framework-synthesis.md) adds
proposed term-selection, grounded-review and revision-accounting protocols.
PI scope record `jrn_01M2GMBXSFMASNFEYK9F1H866B` authorizes organized local RKA
records and repository design-document updates, without a commit. It does not
ratify each proposal or authorize implementation. See the
[record index](docs/research/writer-rka-index.md) for evidence and history.

The [October 18 refinement](docs/research/2026-10-18-humanizer-review.md) adapts
Humanizer patterns into grounded expression review and adds H1/H2 offline
regressions under PI scope `jrn_01M580RKGCSMZW2K528QT4PHW7`. No external skill is
installed. The deterministic probe consumes manually supplied semantic atoms;
it does not assess arbitrary prose. The October 19 follow-up connects exact
supplied cases to a separate **Review practice** area under PI scope
`jrn_01M58AM4YFGGKJNZFEE4R0HQSA`. It does not write paper state. The
[design review](docs/evaluation/2026-10-19-workbench-review.md) records observed
interactions and remaining limits. Production and human-validation gates remain open.

## Evidence and open gates

| Item | Current evidence | Gate |
|---|---|---|
| PI direction and revision authorization | Recorded with verbatim attribution in RKA | Accepted direction |
| Repository rebaseline and preserved legacy | Existing Git history and compatibility tests | Available baseline |
| W0 walkthrough | Script, case-intake template and local clickable mock exist | Not run with a researcher |
| W0 prototype | English Console-aligned mock now includes question/scope and evidence-use decisions, terminology review, scoped profiles, and fixed-case review/repair; see verification record | Not a production runtime or W0 exit |
| W1 paper/paragraph scenario | Explicit synthetic design fixture | Not an executed runtime |
| Codex official interfaces | Documented candidate capabilities | Installed auth/billing/isolation probe not completed |
| Claude host | Policy source identified | Not qualified; not required for W1 |
| Style calibration | Supplied same-intent candidates and explicit customizable advisory profiles; optional author-supplied sample/interpretation | No extraction or automatic learning; benefit and burden unmeasured |
| Language and convergence protocol | Bounded term-lock, no-change, qualifier-repair and upstream-routing fixtures implemented and engineering-checked | General protocol and researcher outcomes remain unvalidated |
| Humanizer review adaptation | E1–E7 prompts; H1/H2 supplied review/revise/confirm exercises, separate history/storage and annotated contract checks | No arbitrary-text analysis, model semantic detection or human preference result |
| Structural repository checks | Testable links/ADR lifecycle/legacy integrity | Not semantic or usability evidence |

## Next bounded work

1. Try the [local clickable prototype](prototypes/w0/README.md), select a real
   case using the [intake](docs/evaluation/w0-case-intake.md), then run the
   [paper-centered walkthrough](docs/evaluation/w0-walkthrough.md) with consented
   author observations. See [prototype verification](docs/evaluation/w0-prototype-verification.md)
   for the separate engineering checks.
   Include a manageable subset of the
   [language and convergence cases](docs/evaluation/w0-language-and-convergence-cases.md),
   especially valid no-change outcomes and scope-restoring repairs.
   The separate **Review practice** entry is available now for H1/H2. Its local
   confirmations do not count as a completed researcher evaluation.
2. Inspect an installed host read-only. Record unknown billing/isolation
   properties separately; do not run inference to discover whether it bills.
3. Revise the minimal contracts from those observations.
4. Explicitly authorize the bounded W1 implementation only after its gates pass.

Workflow experiments can proceed while host feasibility is unresolved.
See [Roadmap](ROADMAP.md) for stage exits.

## Not implemented or authorized by a design merge

No production UI/database/adapter, automatic paragraph drafting, autonomous
Core write-back, API/paid-credit/local-model fallback, broad editor, second-host
parity or public deployment. Hugging Face is outside this task.

The protected full researcher design source remains local, ignored and
untracked. Historical ADRs and legacy assets remain recoverable.
