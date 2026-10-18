# W0 prototype engineering verification

- Date: 2026-09-04
- Artifact: [local W0 prototype](../../prototypes/w0/README.md)
- Fixture: `synthetic-device-meaning-w0-v1`
- Scope: disposable supplied-text interaction simulation
- Author walkthrough: **not performed**; no PI usability outcome is inferred
- Host qualification: **not performed**; no inference or billing probe

## Local state checks

`node --test prototypes/w0/state.test.mjs`: **22 tests passed**, Node v23.10.0.
The new CI job targets Node 22; it has not run remotely in this local-only task.
These tests execute state transitions, not keyword assertions about design docs.

Covered: explicit exact plan approval, idempotent plan acceptance, rejection of
hidden preview additions and stale bases, author notes without approval,
one-intent supplied-text acceptance, parked claims, full original paragraph
impact after e3 withdrawal, no restoration by mere reapproval, explicit narrowed
plan, title-only change, advisory style scope changes, human editing before
admission, preservation of unsaved drafts, refusal of stale edit reconciliation,
exact refresh serialization and rejection of incompatible/corrupt state.

Repository Python tests: **37 passed** on Python 3.12.9. `node --check`,
the existing Ruff check set and `git diff --check` passed. The protected full
researcher design source remained unchanged and excluded from Git.

## Browser observations

Manually exercised through the Codex in-app browser on loopback HTTP. These are
agent-operated engineering observations, not researcher performance measures.

| Exercise | Observed result |
|---|---|
| Author note → explicit plan constraint | Original note retained; no automatic approval or invented AI reply |
| Plan preview → mock approval | Paper context, evidence uses, functions and terms displayed; all sentence slots initially empty |
| One supplied candidate → manual edit | Only the selected sentence changed; edit labeled pending mapping review |
| Preview mapping → second edit → accept old preview | Refused; latest text remained intact |
| Unsubmitted note → refresh | Note, human text and outstanding mapping restored from browser state |
| e3 withdrawal | Both direct and paragraph-mediated impacts shown; old text retained; candidate acceptance disabled |
| Narrow to relocation → approve new plan | New eligible intent set shown; original replacement text retained separately |
| Decline style promotion → explicitly save section preference | First action changed no rule; second separately recorded a scoped advisory choice |
| Markup-like author input | Rendered literally; no injected `data-w0-probe` element; checked browser error/warning logs were empty |
| Second tab updates state | Original tab reported storage conflict; refresh recovered the other tab's latest synthetic draft |
| Export | A JSON file appeared in Downloads; readback confirmed synthetic label, fixture identity and retained state |
| Narrow viewport | Initial 508px overflow at 390px viewport found; fixed rail min-width; recheck content width = 390px |

The download-event wait timed out in the browser automation, so success was
established from the downloaded file itself, not the click/toast. No retry was
needed. A long sticky discussion column also initially made its bottom controls
hard to reach; capping its height and enabling internal scroll resolved the
observed button-access failure. Temporary viewport overrides were reset.

## Console visual alignment follow-up (2026-09-05)

PI feedback: “这个网页风格和现在的rka console不一致啊”. The original
green/ivory and serif treatment was a mismatch, not an accepted visual identity.
Replaced that presentation with the current Console's neutral tokens, unchanged
RKA app icon, system typography, compact sidebar/header and component geometry.
This does not freeze the three-pane layout or qualify a production framework.

Read-only inspection of the live Console and the revised prototype returned the
same dark background (`oklch(0.145 0 0)`), foreground (`oklch(0.985 0 0)`), body
font (`system-ui, -apple-system, sans-serif`), desktop sidebar width (224px) and
header height (56px). Token/asset source is documented in the prototype README.

Agent-operated checks, separate from an author usability evaluation:

- Inspected desktop argument, structure and writing views in Chrome, plus
  light/dark rendering and theme selection in the local prototype.
- In a separate Chrome test page, an unsubmitted synthetic note survived theme
  switching and reload; the mock plan remained unapproved. The test text was
  cleared through keyboard input and read back empty. Existing in-app author
  notes and approvals were not edited or reset.
- At a 390px in-app viewport, document content width equaled client width
  (375px with the native scrollbar); no page-level horizontal overflow. The
  compact theme selector remained visible. Temporary viewport overrides reset.
- Browser error/warning logs were empty in the inspected pages.
- `node --test prototypes/w0/*.test.mjs`: **27 passed** (22 unchanged state
  checks and 5 appearance-preference checks). Python repository tests:
  **37 passed**. CI includes both test files; remote CI has not run for these
  local changes.

`state.mjs` and `fixture.mjs` retained their pre-change SHA-256 hashes; this
follow-up changes neither the supplied claims/prose nor semantic transitions.
Theme preferences use a distinct key, default to system, and still work in
memory if browser storage is denied. They do not synchronize with or write to
the separate Console origin. No API, Core connection or deployment was added.

## English prototype follow-up (2026-09-05)

PI request: “这个原型我需要是英文的”. Translated the interface, supplied
scenario descriptions, paragraph/intent/term definitions, plan previews,
status/error messages, style controls, and walkthrough. Set document language
to `en`; existing English evidence quotations and supplied sentence candidates
remain unchanged. This is demo localization, not autonomous manuscript drafting.

The English fixture has a separate identity and save slot. The bounded legacy
upgrade preserves notes, custom purpose/constraints, documents, drafts, original
approval bundles/tokens, history, and mapping previews. Only two exact supplied
Chinese purpose defaults are translated; their originals are retained. The old
browser save slot is never overwritten. Old approval/mapping tokens cannot
authorize the translated plan. Unknown or malformed archives fail closed.

- Node checks: **32 passed**, including five localization/legacy-session checks.
- Repository Python checks: **37 passed**; Ruff and syntax checks passed.
- Browser checked Argument, Structure, and Writing at 390px, 768px, and 1280px.
  Document content width equaled client width in all nine checks; no page-level
  horizontal overflow or untranslated interface copy was found in the loaded
  seed session. Viewport overrides were reset.
- Inspected the English plan-approval preview, advisory-style dialog and
  walkthrough. Did not approve a plan, accept prose, or change author notes.
- The in-app browser initially mixed a cached old state module with the new UI
  module and reported a missing export. A cache-bypassing reload resolved it
  without clearing browser storage. The loaded English UI and upgrade notice
  were then read back successfully. This initial error is not a passing check.

Historical records and author input may legitimately retain Chinese. No source
text is sent to a model or external translation service. These checks remain
agent-operated engineering observations, not a researcher usability result.

## Researcher-workflow refinement (2026-09-15)

PI authorized the proposed local Workbench work (verbatim: “你可以动手干了”).
Scope remains the synthetic whole-paper scaffold and one target paragraph.
No model, Core integration, production runtime, commit or push is included.

Implemented interaction subset:

- Two supplied question/claim scopes; editable evidence-use inclusion and
  inference warrants; a different question is explicitly unresolved or parked
  as an author note. Excluding required support blocks admission.
- Proposed concept definitions and contrasts, author naming rationale, and an
  exact terminology-bundle lock. The lock is not a claim or prose approval.
- Editable term/prose/tone starter preferences, optional explicitly supplied
  passage with source/locator and author interpretation, and separately approved
  paragraph/section advisory profile versions. No paper analysis or extraction.
- Fixed-case sentence review: valid no-change, unassessed custom wording,
  qualifier restoration with a semantic delta, and unsupported safety language
  routed upstream. A patch creates one manual version pending mapping review;
  original text, neighbors and prior approvals are preserved.

### Engineering checks

`node --test prototypes/w0/*.test.mjs`: **64 passed** on Node v23.10.0
(32 existing regression checks, 32 new workflow checks). Repository Python:
**37 passed**, Python 3.12.9; Ruff, JavaScript syntax and `git diff --check`
passed. Remote CI was not run. Passing tests is not a W0 exit or author benefit.

The new tests cover missing support, empty/changed warrants, counterevidence
protection, new-question gating, exact term previews, explicit/scoped profile
adoption, source/interpretation requirements, no-change versus unassessed,
single-sentence semantic-delta repairs, upstream routing, stale/forged previews,
document/plan/profile changes, manual draft protection, serialization and
malformed-input rejection, migration, and HTML encoding of authored input.

The refined workflow uses schema 2 and a new `en:v2` save slot. Migration prefers
the old English slot, otherwise the older Chinese slot. It preserves original
authored fields, tokens and histories; neither old slot is written. New contract
fields and a protocol discriminator prevent reusing old approvals. Terms start
unreviewed. Cross-tab source-slot changes and storage-clear events pause saving.
The original protected design source still has SHA256
`de2547ea6c62a6bc500fef396a6a7babfe7de634505b6eef19a02f9e79d291fa`
and remains ignored/untracked. A pre-change prototype copy was made outside
the repository for local recovery; no existing repository files were deleted.

### Agent-operated browser observations

Mutation exercises used the separate Chrome `http://localhost:8766` origin,
leaving the author's `http://127.0.0.1:8766` sessions out of those tests.
Only a read-only refresh was performed on the existing in-app author page;
the new workflow migration notice and controls appeared without resetting it.

| Exercise | Observed result |
|---|---|
| Plan approval before terminology review | Refused with an actionable definition-review message |
| Lock definitions, approve plan, accept one supplied candidate | Separate commitments; other sentence slots stayed empty |
| Review valid supplied text | No-change outcome recorded; no text modified |
| Stage/save missing-qualifier example, inspect and apply repair | Exact span, contract basis and narrowed proposition displayed; one new version marked mapping pending |
| Missing sample provenance, then complete and adopt section profile | Missing source/interpretation refused; completed profile saved separately and read back as version 1 |
| Markup-like sample input | Literal text retained; zero injected `img[src="x"]` elements |
| Unsubmitted note and pending mapping after reload | Note recovered exactly; repaired sentence remained mapping pending |
| Exclude e2, then attempt reapproval | Refused; restoring the exact original use restored the unchanged plan basis |
| Switch to relocation-only branch | Question and claim narrowed; original text remained preserved |
| Submit a different question, then park it | Admission paused; proposal retained as an author note when parked |
| Unsupported-safety exercise | Science issue and missing support shown; no prose repair offered; route returned to Argument |
| Three views at 390/768/1280px | Nine checks: content width equaled client width (375/753/1265px with scrollbar) |
| Style dialog at 390px | Dialog content width equaled its client width (324px); controls remained accessible |

Light and dark views were inspected. Temporary viewport overrides were reset.
Chrome logged `Access to storage is not allowed from this context` on reload,
including an extension content-script source and duplicate page-attributed
entries. Prototype autosave/reload checks succeeded. The in-app refresh reported
no error/warning entries. These observations suggest extension involvement,
but do not establish a root-cause diagnosis; no extension settings were changed
and the Chrome run is not reported as having a clean console.

No real author participated, no sample-based inference ran, and no claim of
better writing, lower cognitive load, or convergent human behavior follows.

## Security/data-flow review

Reviewed typed author input and local JSON state through HTML rendering,
localStorage persistence and Blob download. Dynamic authored strings are HTML
escaped; no dynamic code evaluation, network client, credential handling or Core
mutation path exists in the prototype. A restrictive CSP blocks connections and
external scripts. The static server serves only the prototype directory on
127.0.0.1, not the repository root. Private case preparation is Git-ignored and
outside that directory.

This is a best-effort bounded review, not production security certification.
localStorage is not encrypted or transactional, other local code can read it,
browser data clearing can erase it, and the cross-tab check is not a concurrency
protocol. No dependency scanner, penetration test or adversarial host probe ran.

## Still unvalidated

- A real researcher's understanding, effort, author voice and reader comprehension.
- Whether the selected layout or approval-bundle size is best.
- General semantic entailment, scope/copy-risk detection or arbitrary dependency impact.
- Real-case ingestion, sample-based style extraction or model-generated candidates.
- Core version/hash/locator bindings and actual file/editor reconciliation.
- Host authentication, included-only billing and effective execution isolation.

W0 remains open. Prepare a consented case with the
[intake template](w0-case-intake.md), conduct the
[walkthrough](w0-walkthrough.md), and use observed problems to revise the prototype.
Do not freeze production contracts or start W1 because these checks pass.
