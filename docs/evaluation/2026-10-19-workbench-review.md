# Workbench review-practice implementation and design review

- Date: 2026-10-19; work authorized in the October 18 continuation
- PI scope: `jrn_01M58AM4YFGGKJNZFEE4R0HQSA`
- RKA implementation/design-review record: `jrn_01M5A20Y9SDC4W996HYNBS3BMR`
- Standing: local W0 engineering observations and design assessment, not a user study
- Base: merged PR 7, `fba50e9482a8d2ca6078b75cd2dfbea64163a703`
- Branch: `codex/w0-review-workbench`; initial implementation handoff was uncommitted
- Subsequent publication authorization: `jrn_01M5B02KQ060TKD98XWJQPBWC3` (commit/push, PR and merge after checks pass)

## What is now exercisable

The English **Review practice** workspace reuses the existing Console shell,
theme tokens, typography, cards and controls. It exposes E1–E7 as inspectable
questions with legitimate exceptions. Only H1/H2 have supplied text assessments;
there is no suggestion that all seven categories have automated analysis.

Each case shows the source, sentence function, protected meaning, deliberately
flawed draft and supplied finding. The author can select an equivalent or
source-wording candidate, edit a draft, defer, reject or request evidence review.
Confirmation requires an exact before/after preview and current version. A
confirmed version and prior decisions remain inspectable after reload.

The gallery and algorithm examples live outside the synthetic paper, in a
separate browser key. They cannot enter its document, approvals or style profile.
There is no schema migration of existing paper state. Custom wording is kept
as unassessed, not discarded or silently approved. Upstream routing records a
local pending question; it does not create a Core mission.

## Design findings and repairs

| Finding | Change made | Evidence / remaining limit |
|---|---|---|
| A test-only Node import prevented direct browser reuse of the probe | Replace it with JSON-compatible structural equality; retain the original regression suite | Probe tests plus successful browser module loading; no semantic extractor |
| Practice examples could look like content in the active paper | Separate route/storage; label the paper paused and remove its active-section highlight | Return-to-paper preserves note bytes; no exercise data in the paper archive |
| Draft edits could leave the case picker showing a prior confirmation | Update the case status and short live draft assessment on input | Browser recheck shows In review / blocked confirmation for custom text |
| A skip link changed the URL hash and exited practice | Focus the main region without changing the route | Browser readback: focus main, hash remains review-practice |
| An old paper dialog could remain visible after hash navigation | Close presentation-only dialogs on a route change without altering drafts | Targeted route check; confirmations must be reopened in their own context |
| Style improvement could be mistaken for semantic approval | Show protected meaning and a concrete semantic delta; only a separate exact-preview action confirms | H1/H2 both block the bad draft and allow supplied corrections; still simulation |
| A repeated interaction could imply accepted text was overwritten | Preserve confirmations and displaced drafts; stale previews cannot be reused | Unit checks for edits, edit/revert, source changes, duplicate/forged confirms and case isolation |
| Corrupt storage could invent a current confirmation or crash rendering | Validate record presence, wording and revision; preserve the unreadable original | Malformed/unknown archives fail closed; storage is still not authenticated or transactional |
| Repeating the same explanation increased scrolling | Remove duplicate explanation and collapse rules/provenance/history | Visual inspection only; whether this reduces author effort is unmeasured |

## Engineering observations

- Node: **124 passed**, comprising the previous 92 and 32 practice interaction,
  persistence, rendering and guard checks. Python repository/legacy: **37 passed**.
- H1 browser path: inspected lower-bound change; chose supplied wording;
  previewed; entered a custom sentence; observed Not assessed and disabled stale
  confirmation; restored the supplied candidate; explicitly confirmed.
- H2 browser path: inspected the mechanism and complexity issues separately;
  requested evidence review; saw the specific missing question and no task-sent
  claim; resumed, selected the supported sentence, previewed and confirmed.
- Reload restored selected case and recorded confirmation. A synthetic paper
  note remained byte-identical while practice actions ran and reappeared on
  return to the paper. Tests used `localhost:8766`, separate from the author's
  `127.0.0.1:8766` origin; no author-origin notes were reset.
- Keyboard: preview focused the confirmation region; Tab reached Confirm no
  change; Enter recorded the decision and focused the outcome. The skip link
  kept the practice route. This is not a full assistive-technology audit.
- Effective CSS widths **390, 768 and 1280px**, each in light and dark mode:
  document scroll width equaled client width; UI text was English. The narrow
  draft area was 332px wide. Inspected screenshots at narrow and desktop sizes.
- Neutral backgrounds, sidebar colors, radius and system-font family match
  the current Core CSS tokens checked in `rka/web/src/index.css`. The existing
  local stylesheet mirror and icon were retained; no new visual brand introduced.
- Successful final browser runs reported no console errors/warnings. Restored
  the test page to desktop size and System theme after the responsive checks.

Initial browser checks were not all successful. The initial sandboxed preview
server returned connection resets and later 404s for files present on disk.
Only the task-started server was replaced with an explicit prototype-only
directory on loopback and a larger request queue. Isolated tool tabs also
closed, and a cached module caused a test harness selector to miss a new status
element. A normal localhost test tab with cache-bypassing reload loaded the
current files and passed the checks above. These recoveries do not establish
the original infrastructure failure's root cause. One resize request for390px
produced500px; the reported390px result is from explicit device emulation, not
that clamped window resize.

## Overall design judgment and next learning step

The authority boundary is understandable enough to exercise: seeing a finding,
choosing wording and confirming a displayed version are distinct actions. The
UI uses one final confirmation, not approval forms for every semantic atom.
Read-only context stays visible without requiring the author to operate a graph.
This is a design assessment backed by bounded interaction checks, not evidence
that researchers find the process efficient or that prose quality improves.

Remaining priorities:

1. **Ground the same flow in one real paragraph.** Practice is intentionally
   separate; production review still needs actual intent/evidence/source anchors
   and the existing W1 authorization and host gates. Do not insert the gallery
   and algorithm examples into the paper to simulate integration.
2. **Test author comprehension before adding rules.** Ask the researcher to
   explain why H1 changed meaning, what H2 does not establish, and whether
   Confirm affects the paper. Observe confusion and effort with consent.
3. **Evaluate real review separately.** A correct annotation comparison does
   not prove correct annotations. Measure missed changes, false alarms and
   unsupported repairs on unseen text against independently reviewed cases.
4. **Resolve upstream work in context.** The current evidence request is a
   local placeholder. A future workflow must return to claim/evidence discussion
   and later revalidate the exact sentence, without a hidden auto-rewrite.
5. **Keep human editing practical.** Custom drafts remain usable but cannot
   complete the supplied assessment path. That limitation must not become a
   production rule banning an author's own expression. Broader editing and
   reconciliation require a separately validated implementation.

No production editor, AI critique, arbitrary prose validation, Core integration,
author study, runtime qualification or W0/W1 exit is claimed. This work leaves
the researcher's original ignored design source intact and changes no accepted
ADR or subscription-only boundary.
