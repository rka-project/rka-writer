# W0 Paper Studio: disposable interaction prototype

This is a clickable, local, supplied-text mockup under
[ADR 0008](../../docs/adr/0008-paper-centered-incremental-commitment.md), not a
production Writer runtime. It answers a narrow question: can a researcher move
between argument, paper structure and sentence work without losing meaning,
control, edits or the whole-paper context?

## Open locally

From the repository root:

```sh
python3 -m http.server 8766 --bind 127.0.0.1 --directory prototypes/w0
```

Open `http://127.0.0.1:8766`, not `index.html` through a `file://` URL (browser
module restrictions can prevent the app from loading). Stop the server with Ctrl-C when finished. Serve
only this directory, not the repository root. Do not place private materials in
this directory: all its files are available to local browser clients. There is
no package installation, build step, CDN, model call, Core connection or API key.
This Python development server is loopback-only and is not a deployment server.

## Visual alignment with RKA Console

The shell follows the current Console: 224px desktop sidebar, 56px header,
24px workspace inset, system sans-serif type, neutral surfaces, thin borders,
and the same button/card radii. Writer's argument/structure/writing views and
discussion sidecar remain authoring-specific; this is not the Core dashboard.

`console-theme.css` mirrors the relevant light/dark tokens from Core's
`web/src/index.css` at `f8db01b33acc76cfa6f9fff804868c21cd08d58b`.
The app icon is an unchanged copy of Core's
`assets/brand/rka-project-plugin-app-icon.svg`; its MIT notice is in
[LICENSE](LICENSE). The marketing navy/teal/amber palette is not substituted
for the Console's neutral component palette. No Core source is imported at
runtime, and no production shared component package is being frozen in W0.

**Theme** offers light, dark and system (default), matching Console's theme
choices. The preference uses the separate `rka-writer:w0:theme` browser key.
It does not change authoring state, reset forms, or read/write Console's own
settings. Separate origins do not automatically synchronize their theme choice.

## Try the shortest meaningful path

1. In **Argument**, choose both supplied cases or the relocation-only branch.
   Inspect claim boundaries, include/exclude evidence uses, and edit the inference
   warrants. A required missing use blocks admission. A different question can
   be submitted for upstream discussion; the fixture does not infer its answer.
2. Add a note explicitly to the proposed plan. In **Structure**, inspect the paper
   outline, p1's purpose and sentence functions. Review the proposed definitions
   and contrasts, then lock that small terminology bundle. This does not approve
   claims or prose. Change the entry order if desired; inspect and approve the
   exact displayed plan, including selected uses and author-reviewed warrants.
3. In **Writing**, the paragraph still has no accepted prose. Compare the supplied
   alternatives for one intent and accept just one. Style promotion is separate.
4. Save a human edit. Preview its intent mapping, close the dialog, edit again,
   and try accepting the old preview. It must refuse without overwriting text.
5. Withdraw e3. Both directly and indirectly affected original intents need
   review; manuscript text and original approvals stay unchanged. Narrow to the
   relocation case, inspect a new plan and continue with its supported intents.
6. Leave a note or sentence draft unsubmitted and refresh. Stored context,
   approvals, drafts, impact and an outstanding mapping preview should resume.

### Language and revision exercises

- **Customize term / prose / tone** opens an editable, authored starter template.
  Optionally supply a passage, its source/locator and what you value about it.
  This is manual preference capture, not sample analysis. Drafts autosave, but
  only **Approve this scoped profile** adopts a paragraph/section advisory rule
  set. Past versions remain intact. No style change rewrites text, overrides
  locked terminology or changes a scientific approval.
- **Review this saved sentence** matches explicitly supplied cases only. A
  supplied valid sentence supports **Keep this wording**, without a patch.
  Other custom wording is **Not assessed**, not a silent pass.
- Under **Try a supplied failure case**, stage the missing-qualifier example,
  explicitly save it, then review. The exact-span issue explains the contract
  basis, reader consequence and expressed-proposition delta. Applying its
  one-sentence repair preserves the previous version and still requires intent
  mapping review. Nothing else in the paragraph changes.
- The unsupported-safety example routes to claims/evidence and offers no polish
  patch. A changed document, draft, plan or adopted profile expires an earlier
  review preview. Defer/no-change decisions are recorded without rewriting.

These are bounded mock interactions. They do not implement all cases in the
[language protocol](../../docs/design/language-and-revision-protocol.md).

The **Walkthrough** is voluntary self-report, not automatic human validation.
Follow the full [walkthrough protocol](../../docs/evaluation/w0-walkthrough.md).

## State and privacy

The app explains that actions, notes and unsubmitted drafts are autosaved to
this browser's localStorage under `rka-writer:w0:paper-studio:en:v2`. No analytics,
background transmission, inference, sample scanning or timing collection is
performed. Human observations must be recorded explicitly and consensually.
The UI's “0 model calls” is a description of this static build, not a host audit.

The **Export demo** action requests a local JSON download. Inspect it before
sharing: it includes whatever you typed. This prototype has no file-import UI.
Browser data clearing can lose local state; an export is the portable backup.
**New demo** archives the old state under a timestamped key before starting fresh.
Archives are retained as raw JSON; an archive picker and file restore are not
implemented. A new or conflicting tab cannot silently overwrite the stored
snapshot; the conflict notice asks you to export the current tab and refresh.
This is a convenience check, not transactional cross-tab collaboration.

All choices are labeled simulation and never written to RKA as canonical PI
decisions. Existing research files are neither read nor modified by the app.
Browser storage is not encrypted research storage; do not enter sensitive data.

## English demo and previous sessions

The UI, supplied scenario, plan previews, status/error messages, and walkthrough
are English. The document language is `en`. Author-entered text is never
translated automatically.

The scenario identity is `synthetic-device-meaning-w0-en-v1`; the refined
workflow uses schema 2 and a new `en:v2` save key. If that slot is empty, the app
copies a valid English `en:v1` session, or otherwise the older
`rka-writer:w0:paper-studio:v1` session, into memory. Notes, manual text, drafts,
decisions and mapping previews are retained.
The original save slot is never overwritten. Only the two exact old preset
paragraph purposes are replaced with their English equivalents; their originals
are retained in the upgrade record. Custom purposes remain verbatim.

Historical approval bundles and tokens remain unchanged. The new workflow
protocol, evidence warrants and concept definitions change the approval basis;
old approvals cannot authorize it. New terminology starts unreviewed. A notice
asks for review of the new plan. The first normal save writes only to `en:v2`;
subsequent reloads prefer that slot. Editing the old slot from another tab while
the migration is in progress pauses saving, rather than overwriting either slot.
Corrupt/unknown archives are not silently reset. The original historical record
may contain Chinese, and so may author input; neither is interface copy.
The legacy-session test fixture contains only synthetic authored data.

## Replace the scenario carefully

The initial device example is **synthetic**, not an empirical study or a
researcher-approved question. The related [real-case intake](../../docs/evaluation/w0-case-intake.md)
must be completed before a real-project walkthrough. No real case has yet been
selected. Keep private source materials outside the served prototype directory.

- `fixture.mjs`: supplied scenario, claims, excerpts, outline, intents and
  candidates. It is a fixture module, not a general import format.
- `state.mjs`: disposable deterministic state transitions, snapshots and guards.
- `workflow.mjs`: term/profile state, use selection, fixed review cases and input validation.
- `workflow-view.mjs` and `html.mjs`: workflow panels and shared author-text encoding.
- `studio.mjs` and `studio.css`: presentation, local persistence and interactions.
- `console-theme.css` and `theme.mjs`: Console-aligned UI tokens and a separate
  local appearance preference; no authoring-state access.
- `state.test.mjs`: bounded simulation-state tests, not semantic/host proofs.
- `workflow.test.mjs`: new workflow gates, migration, exact-base repairs and safe rendering.

For a new approved sanitized scenario, update the fixture **and** its explicit
impact/narrowing transitions/tests, and change `fixture.id`. Do not merely swap
paper titles and pretend hard-coded impact logic generalizes. There are no real
Core IDs, cryptographic source hashes or validated public-contract bindings.

## Deliberately not implemented

- Model reasoning, natural-language interpretation or semantic checking.
- Arbitrary claim/source editing, customizable intent lists or term vocabularies.
  The mock supports selecting/parking c1, two predefined scopes, selecting
  their supplied evidence uses, and author-written warrants. Different question
  proposals remain unresolved or explicitly parked as notes, not auto-realized.
- Automatic style extraction, article ingestion, prose adaptation or source copying.
- A real Evidence Gateway, authoring database, host adapter or document export.
- File/Overleaf synchronization, split/merge remapping or transactional recovery
  across file and database writes.

Free-form purpose/constraint edits are preserved verbatim; they do not magically
update the supplied candidates or prove meaning compatibility. The walkthrough
must surface mismatches. Metadata-only classification is limited to the seeded
display-title edit. Evidence effects are the fixture's explicit expected edges.

## Verify

```sh
node --test prototypes/w0/*.test.mjs
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
```

The state tests use built-in Node modules only. Browser interaction observations
belong in the [prototype verification record](../../docs/evaluation/w0-prototype-verification.md).
Passing them does not mark W0 complete or authorize W1.

### Offline expression-review contract probe

`review-probe.mjs`, `review-fixtures.mjs` and `review-probe.test.mjs` add the
H1/H2 [Humanizer-derived regressions](../../docs/evaluation/w0-language-and-convergence-cases.md).
These run under the same Node test command above, without models or dependencies.
The probe compares manually reviewed semantic atoms bound to exact text and
revision snapshots. It exercises lower-bound loss, invented implementation and
complexity, legitimate equivalents, no-change, unknown and stale outcomes.
It never accepts or writes text and is not connected to the browser mock.

This is an executable design contract, not a general semantic detector. The
tests explicitly demonstrate that an incorrect annotation can hide a prose
defect. They do not establish the quality of a model's annotations or prove
full semantic preservation. No production schema is adopted.
