# Reviewer integration design

## Decision

RKA Writer and the reviewer suite share one repository and plugin distribution,
but remain separate skills with separate context. Installation exposes four
explicit-only entrypoints:

- `rka-writer` drafts and revises prose;
- `ai-cyber-paper-reviewer` reviews AI, security, and related CS papers;
- `nsf-cise-mock-panelist` reviews proposer-owned NSF CISE proposals; and
- `holistic-academic-reviewer` routes an explicitly requested review to one of
  the two specialist reviewers.

The router contains no embedded engine copies. The two sibling specialist skill
directories are the canonical runtime sources in this repository. The router's
manifest hashes those directories so drift is detected without maintaining a
second editable copy.

## Why the contexts stay separate

Writer optimizes for coherent argument, plain academic language, and authorial
control. Reviewers intentionally adopt skeptical roles, inventories, ratings,
and verification protocols. Loading both while drafting can turn prose into a
point-by-point response, overexpose caveats, or make read-only and editing
instructions conflict.

All four skills therefore disable implicit invocation on Codex and model-driven
invocation on Claude. A reviewer never becomes a mandatory Writer gate, hook,
session persona, or automatic postprocessor.

## Supported workflow

```text
Writer draft
    -> identify/freeze reviewed version
    -> explicit read-only reviewer in a fresh task/session or isolated subagent
    -> preserve native report and limitations
    -> researcher selects or authorizes triage of findings
    -> fresh Writer context receives only the frozen report and selected findings
    -> cold read, evidence check, and rendered-layout verification
```

Reviewer output is advice, not a rewrite plan that executes automatically. The
handoff carries only selected findings, anchors, the underlying reader or
validity problem, and precision constraints. It does not inject panel scores,
adversarial language, issue-ledger structure, or every reviewer caveat into the
drafting context.

Merely invoking the reviewer and Writer in two passes of the same task is not
context isolation: the reviewer's instructions remain loaded. If a fresh task,
session, or isolated subagent is unavailable, stop after producing the review
and begin revision in a new Writer task.

For a packet containing both a paper and a proposal, the router runs separate
native reviews. It never blends scores, recommendations, or assurance labels.

## Maintenance invariants

1. Reviewer skill descriptions and UI policies remain explicit-only.
2. Claude mirrors differ only in invocation frontmatter and the resulting
   host-specific engine-manifest hashes; all other assets are byte-identical to
   the canonical Codex tree.
3. The Holistic manifest must match the two canonical specialist directories.
4. Reviewer tests run against the canonical `skills/` paths, not copied test
   fixtures inside a release tree.
5. Writer's entrypoint stays small; reviewer rubrics and schemas are never
   referenced during ordinary drafting.

If the reviewer suite later needs a separate release cadence, it can move to an
`academic-reviewer-suite` repository without changing this handoff. The same
four-phase boundary should remain.

## Imported snapshot and updates

The three reviewer skills were imported on 2026-08-27 from the researcher-owned
local reviewer trees. Before integration, the paper, NSF, and Holistic source
trees passed 84, 41, and 16 tests respectively. The integrated copies change
invocation metadata and router paths, so older protocol digests or forward-test
result records do not attest this version.

Make future changes first in the canonical `skills/` tree. Then synchronize the
Claude tree, add Claude-only invocation frontmatter, regenerate both host-specific
Holistic manifests, and run the complete repository test suite. Do not copy an
older standalone directory over these canonical sources.
