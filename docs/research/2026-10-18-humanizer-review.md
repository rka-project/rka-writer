# Humanizer: grounded expression review assessment

- Reviewed: 2026-10-18
- Standing: source observations and PI-authorized design integration; not a model evaluation
- PI scope: `jrn_01M580RKGCSMZW2K528QT4PHW7`
- RKA source observations: `jrn_01M58108ZRBHW7RSWY4XKB03G1`
- RKA design interpretation: `jrn_01M5810A836GX6KDZ2ZPYG1EC0`
- RKA verification: `jrn_01M5811R67JA952ZQEXD0WZQBV`
- Authority: CONVERGENCE-2 and STYLE-2; no replacement decision or production gate change

## Source identity

Reviewed `blader/humanizer`, `SKILL.md` metadata version 3.1.0, at commit
`8c307f367c91bd974002f10f2be2965d642c13df`.
[Pinned skill](https://github.com/blader/humanizer/blob/8c307f367c91bd974002f10f2be2965d642c13df/SKILL.md),
[README](https://github.com/blader/humanizer/blob/8c307f367c91bd974002f10f2be2965d642c13df/README.md),
[change log](https://github.com/blader/humanizer/blob/8c307f367c91bd974002f10f2be2965d642c13df/CHANGELOG.md).
The fetched skill's UTF-8 SHA256 is
`0612f1dfb1672b0ea9b97e139bf1f06cabe98d8b27424fe8ff01e1fb4cc99cad`.
The upstream project declares MIT licensing. No skill is installed or vendored;
the Writer catalog is an independent, attributed adaptation of review ideas.
External instructions remain source material, not execution authority.

## Observations versus interpretation

The skill has 26 patterns, a mark/rewrite/check/final workflow, factual-preservation
instructions and sample-based voice matching. It includes exceptions for real
qualifications, informative contrasts and technical uses. These are useful
review prompts, but its paragraph rewrite permissions and strong dash rule are
not adopted by Writer. The exact integration and false-positive guards are E1–E7
in the [language protocol](../design/language-and-revision-protocol.md).

Two illustrative rewrites conflict with factual preservation:

| Case | Source locator and observed change | Writer interpretation |
|---|---|---|
| H1 | §18: gallery area changes from a strict lower bound of 3,000 square feet to an exact total of 3,000 | The numeral survives but the quantitative proposition changes. Preserve the comparator, not just digits. |
| H2 | §25, first example: replacing an older O(n²) traversal becomes a claim about a hash map and O(1) lookups | The supplied before-text establishes neither the new implementation nor its complexity. Treat both as unsupported additions, not concise paraphrase. |

These are observations about the published examples, not observed outputs from
running Humanizer and not claims about the actual gallery or software.
Our regression sentences are short, independently worded adaptations. H2's
fixture explicitly distinguishes the old algorithm's cost from the current
function's unknown mechanism and cost. Removing either invented detail alone
must not make the other acceptable.

## Evaluation limits

The README's 16/16 quality preference refers to a community
[evaluation report, issue 229](https://github.com/blader/humanizer/issues/229).
The report states that all judges were language models from one family and
77 of 144 planned quality comparisons ran. This is not a human-author trial,
an evaluation of our Writer workflow, or proof of semantic preservation.
We reviewed the report, not independently reran its study. Its findings must
not be attached to the current skill revision as a fresh benchmark result.

## Adopted design interpretation

Keep patterns as candidate inspections. Require an anchored reader problem and
contract/evidence basis before proposing action. Separate factual defects,
discourse defects, expression defects and personal preferences. Scientific
meaning and concept identity constrain all style advice. Same-meaning sentence
proposals follow admission and researcher review; upstream changes reopen their
own decisions. No forced revision, global learning, AI detection or auto-apply
policy is introduced.

The resulting hypothesis is that this grounded catalog helps authors notice
avoidable reading work without losing scope or voice. It remains unvalidated.
False alarms on useful hedges, repeated terms, signposting and quantitative
notation are required evaluation outcomes, not acceptable collateral changes.

## Executable regression scope

See H1/H2 in the [case protocol](../evaluation/w0-language-and-convergence-cases.md)
and the [W0 probe](../../prototypes/w0/review-probe.mjs).
The probe compares manually supplied semantic atoms bound to exact before/after
text snapshots. It exercises routing of changed, added, missing, unknown and
stale annotations. Safe controls remain proposals for researcher review; they
never become accepted text. It performs no natural-language parsing, inference,
MCP calls or manuscript writes and is not wired into the browser mock.

Passing these tests demonstrates only the declared contract behavior over these
annotations. A model could miss a fact while producing plausible annotations;
that risk is not solved by this probe. Future end-to-end evaluation must measure
misses, false alarms and author comprehension on unseen text with independently
reviewed gold labels. No W0 exit, W1 authorization or semantic-safety guarantee
follows from these regressions.

## Engineering verification — 2026-10-18

- `node --test prototypes/w0/review-probe.test.mjs`: 28 passing checks.
- `node --test prototypes/w0/*.test.mjs`: 92 passing checks, including the existing 64.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider`: 37 passing checks.
- Existing Ruff targets and `git diff --check`: passed.

No model or browser evaluation was run for this addition; the browser mock was
not modified. Existing uncommitted changes remain intact. No commit or push is
part of this record. The separate validation limits above remain applicable.
