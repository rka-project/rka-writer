# Permission Model

Permissions describe enforceable authority, not merely instructions to a model.
See [RFC 0002](../rfcs/0002-subscription-host-and-paper-studio.md) for the actual
host isolation that must support this design.

| Action | Model role | Researcher role | Automatic state change |
|---|---|---|---|
| Read selected Core context | Scoped read-only proposal work | Establish task/source scope | No Core mutation |
| Discuss, inspect or compare | May suggest and explain | Free to explore, park or change focus | No approval inferred |
| Select question, claims, evidence or narrative | Propose exact changes | Approve displayed versions/bundle | None |
| Approve paragraph purpose/intent plan | Propose coupled bundle | Review/edit/approve exact preview | No hidden child approvals |
| Lock terms or promote style rule | Propose with scope | Explicit approval, including override scope | None |
| Realize sentence | One admitted intent, qualified host | Accept/edit/reject candidate | Never auto-accept |
| Human scratch/direct editing | No broad agent drafting permission | May write or edit freely | Preserve bytes; mark reconciliation |
| Apply formatting-only change | Bounded proposal | Explicit policy may permit | Only within that policy |
| Classify upstream impact | May assist semantic assessment | Resolve uncertain meaning | Deterministic traversal; never rewrite |
| Revalidate affected artifact | Propose assessment | Approve new compatibility/version event | Never silently rebind history |
| Review whole paper | Explicitly scoped, isolated, read-only | Request review and select findings | No auto-import or edits |
| Analyze style samples | Selected-source observations | Authorize source/processing scope | No promotion to rule |
| Learn from an edit | May propose a scoped preference | Separate consent to generalize | No hidden learning |
| Resolve copy-risk flag | Present evidence | Replace, quote/cite, or substantiate false positive | No blanket bypass |
| Write durable research meaning to Core | No Realizer capability | Exact separate preview/confirmation | Idempotent authorized write/read-back |
| Dispatch host task | Request bounded proposal | Task-dependent authorization | Only after auth, billing, isolation and target gates |
| API, extra-paid or local fallback | Not available | Outside baseline | Never |

Mentor, Realizer and reviewer are logical roles. Agent count is not a feature.
The Realizer cannot approve itself, invoke the Core write-back route, or edit
canonical documents through ambient filesystem/tool access.

Structural checks enforce scope, bases and mutation rules. Semantic assessments
remain evidence-grounded judgments with uncertainty. Unresolved material
support/scope concerns block accepted scientific text; researcher approval
does not certify scientific truth.
