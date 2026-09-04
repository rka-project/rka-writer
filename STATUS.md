# RKA Writer Status

- Phase: W0 — Workflow and feasibility learning
- Product status: design; no supported authoring runtime
- Decision owner: Chenglong Fu
- Last reviewed: 2026-09-04
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

## Evidence and open gates

| Item | Current evidence | Gate |
|---|---|---|
| PI direction and revision authorization | Recorded with verbatim attribution in RKA | Accepted direction |
| Repository rebaseline and preserved legacy | Existing Git history and compatibility tests | Available baseline |
| W0 walkthrough | Script and recording template exist | Not run with a researcher |
| W1 paper/paragraph scenario | Explicit synthetic design fixture | Not an executed runtime |
| Codex official interfaces | Documented candidate capabilities | Installed auth/billing/isolation probe not completed |
| Claude host | Policy source identified | Not qualified; not required for W1 |
| Style calibration | Proposed same-intent workflow | Benefit and burden unmeasured |
| Structural repository checks | Testable links/ADR lifecycle/legacy integrity | Not semantic or usability evidence |

## Next bounded work

1. Walk through the [paper-centered scenario](docs/evaluation/w0-walkthrough.md)
   with supplied text and record author effort, misunderstanding and revisions.
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
