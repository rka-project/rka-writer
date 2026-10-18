import { fixture, intentsFor } from './fixture.mjs';
import { createThemeController } from './theme.mjs';
import { migrateLegacy } from './legacy-session.mjs';
import { STORAGE_KEY, PREVIOUS_STORAGE_KEY, LEGACY_STORAGE_KEY, createState, planBundle, planToken, currentApproval, blockers,
  previewPlan, approvePlan, changePlan, acceptCandidate, withdrawEvidence, impact,
  changeMetadata, stageEdit, saveEdit, previewMapping, reconcile,
  documentStatus, addNote, serialize, deserialize, sourceBindings, migratePrevious, previewReview, resolveReview } from './state.mjs';
import { termBundle, termToken, lockTerms, toggleEvidence, approveProfile, reviewExamples, styleFields } from './workflow.mjs';
import { questionControls, evidenceControls, terminologyPanel, styleContent, reviewPanel, reviewContent } from './workflow-view.mjs';
import { esc, button } from './html.mjs';

const app = document.querySelector('#app');
const modal = document.querySelector('#modal');
const tag = (text, tone = '') => `<span class="tag ${tone}">${esc(text)}</span>`;
let state = createState();
let lastStored = null;
let saveMessage = 'Demo not started';
let storageBlocked = false;
let planPreview = null;
let candidateToken = null;
let terminologyPreview = null;
let reviewPreview = null;
let toastTimer;
let resumed = false;
let legacyStored = null;
let sourceStorageKey = null;
const theme = createThemeController({
  root: document.documentElement,
  // Defer access so a denied localStorage getter also has a graceful fallback.
  storage: {
    getItem: key => localStorage.getItem(key),
    setItem: (key, value) => localStorage.setItem(key, value),
  },
  media: window.matchMedia('(prefers-color-scheme: dark)'),
  onStorageError: () => notify('Theme changed, but the browser could not save this preference.'),
});

try {
  lastStored = localStorage.getItem(STORAGE_KEY);
  if (lastStored !== null) { state = deserialize(lastStored); resumed = true; saveMessage = 'Local demo restored'; }
  else {
    sourceStorageKey = localStorage.getItem(PREVIOUS_STORAGE_KEY) !== null ? PREVIOUS_STORAGE_KEY : LEGACY_STORAGE_KEY;
    legacyStored = localStorage.getItem(sourceStorageKey);
    if (legacyStored !== null) {
      state = sourceStorageKey === PREVIOUS_STORAGE_KEY ? migratePrevious(legacyStored) : migrateLegacy(legacyStored);
      resumed = true;
      saveMessage = 'Previous demo preserved';
    }
  }
} catch (error) { storageBlocked = true; saveMessage = 'Archive unavailable · Original preserved'; }

function notify(message) {
  const toast = document.querySelector('#toast');
  toast.textContent = message;
  toast.classList.add('visible');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('visible'), 6500);
}
function save() {
  try {
    if (storageBlocked || localStorage.getItem(STORAGE_KEY) !== lastStored
      || (legacyStored !== null && localStorage.getItem(sourceStorageKey) !== legacyStored)) throw Error('Another tab or an incompatible archive occupies this save slot. Export this page, then reload. Nothing was overwritten.');
    const raw = serialize(state);
    localStorage.setItem(STORAGE_KEY, raw);
    lastStored = raw;
    saveMessage = 'Demo saved locally';
  } catch (error) { storageBlocked = true; saveMessage = 'Not saved · Export this page'; notify(error.message); }
  document.querySelectorAll('[data-save-label]').forEach(el => { el.textContent = saveMessage; });
  const planStatus = document.querySelector('[data-plan-status]');
  if (planStatus) planStatus.textContent = currentApproval(state) ? 'Plan approved in simulation' : 'Still discussing';
  const planHelp = document.querySelector('[data-plan-help]');
  if (planHelp) planHelp.textContent = blockers(state).length ? 'Review the implications before committing the plan. Your drafts stay available.' : 'Accept a candidate for one intent at a time.';
  const readiness = document.querySelector('[data-readiness]');
  if (readiness) readiness.innerHTML = blockers(state).filter(r => r !== 'The current plan has not been explicitly approved.').map(r => `<li>${esc(r)}</li>`).join('');
}
window.addEventListener('storage', event => {
  if (event.key !== null && event.key !== STORAGE_KEY && !(legacyStored !== null && event.key === sourceStorageKey)) return;
  storageBlocked = true;
  saveMessage = 'Changed in another tab · Saving paused';
  document.querySelectorAll('[data-save-label]').forEach(el => { el.textContent = saveMessage; });
  notify('Another tab changed the archive. Edits on this page remain in memory. Export this page before reloading.');
});

function heading(kicker, title, subtitle) {
  return `<header class="view-heading"><div class="eyebrow">${kicker}</div><h1>${title}</h1><p>${subtitle}</p></header>`;
}
function evidenceCard(e, editable = false) {
  const withdrawn = e.id === 'e3' && state.withdrawn;
  const title = e.id === 'e1' && state.metadataRevision > 1 ? `Example interface · Title revision ${state.metadataRevision}` : e.title;
  return `<article class="card"><div class="card-head"><h3>${esc(e.id)} · ${esc(title)}</h3>${tag(withdrawn ? 'Consequence use invalid' : e.role, withdrawn ? 'warn' : '')}</div>
    <p class="reason">${esc(e.limit)}</p><details><summary>Source text and use boundaries</summary><blockquote>${esc(e.text)}</blockquote><div class="source">${esc(e.locator)} · mock v${e.version} · Synthetic material</div></details>${editable ? evidenceControls(state,e) : ''}</article>`;
}
function argumentView() {
  const bundle = planBundle(state);
  const claimReason = state.plan.scope === 'relocation'
    ? 'e2 supports the relocation precondition; e1 supplies context and e4 limits scope. The narrowed plan no longer uses e3.'
    : state.withdrawn ? 'The consequence support in e3 was withdrawn. Review the original claim; reapproval cannot restore missing evidence.' : fixture.claims[0].reason;
  return `${heading('01 / ARGUMENT', 'What should this paper establish?', 'Discuss the question and evidence before committing to an argument.')}
    <article class="paper"><div class="eyebrow">Paper question · Example starting point for your review</div><div class="research-question">${esc(bundle.question)}</div>
    <div class="boundary">${esc(fixture.boundary)}</div><div class="plan-meta"><div><h3>Audience</h3><p>${esc(fixture.audience)}</p></div><div><h3>This round</h3><p>Introduction, p1: use concrete cases to motivate the representation problem.</p></div></div>${questionControls(state)}</article>
    <div class="section-title"><h2>Choose a defensible claim</h2><span class="muted">1 candidate · 2 alternatives</span></div>
    ${fixture.claims.map((c, i) => `<article class="card ${i === 0 && state.plan.selected ? 'selected' : ''}"><div class="card-head"><h3>${esc(c.label)}</h3>${tag(i === 0 ? state.plan.selected ? 'In the proposed plan' : 'Parked' : c.disposition, i ? 'neutral' : '')}</div><p>${esc(i === 0 ? bundle.claim : c.text)}</p><p class="reason">${esc(i === 0 ? claimReason : c.reason)}</p>${i === 0 ? button(state.plan.selected ? 'Park this claim' : 'Return to plan', 'toggle-claim') : button('Discuss this judgment', 'discuss-claim', `data-id="${c.id}" class="quiet"`)}</article>`).join('')}
    <div class="section-title"><h2>Evidence and boundaries</h2><span class="muted">Select for purpose, not volume</span></div>
    <div class="evidence-grid">${sourceBindings(state).map(e => evidenceCard(e,true)).join('')}</div>
    <div class="plan-actions row-actions">${button('Continue to structure →', 'view', 'data-view="structure" class="primary"')}<small>Changing views does not approve anything.</small></div>`;
}
function outlineView() {
  const section = fixture.sections.find(s => s.id === state.section) ?? fixture.sections[0];
  return `${heading('02 / STRUCTURE', 'Give every paragraph a clear purpose.', 'Place this paragraph in the paper. Other sections can remain provisional.')}
    <article class="paper"><div class="eyebrow">Paper spine · Provisional</div><h2>From command availability to physical meaning</h2><div class="sequence"><span>Concrete cases</span>→<span>Representation problem</span>→<span>Approach</span>→<span>Evaluation needed</span></div>
    <div class="boundary">Current section: ${esc(section.title)} · ${esc(section.job)}</div><div class="plan-meta">${section.paragraphs.map(p => `<div><h3>${esc(p)}</h3><p>${p.startsWith('p1') ? 'Develop this paragraph now, keeping the paper question in view.' : 'Keep as context; no prose is required now.'}</p></div>`).join('')}</div></article>
    ${state.section !== 'intro' ? `<div class="empty">This section provides paper-level context. W0 does not implement a full-paper editor. ${button('Return to Introduction · p1', 'section', 'data-section="intro"')}</div>` : ''}
    <article class="paper"><div class="eyebrow">Introduction / p1 · Paragraph contract</div><h2>Where does the reader start and end?</h2>
    <label for="purpose">Paragraph purpose (editable)</label><textarea id="purpose" data-field="purpose">${esc(state.plan.purpose)}</textarea>
    <label for="narrative">Narrative entry point</label><select id="narrative" data-field="narrative"><option value="scenario" ${state.plan.narrative === 'scenario' ? 'selected' : ''}>Replacement case first, then the interface and gap</option><option value="representation" ${state.plan.narrative === 'representation' ? 'selected' : ''}>Interface first, then the cases and gap</option></select>
    ${state.plan.scope === 'relocation' ? '<p class="reason">The plan is narrowed to relocation. Both entry points now use the relocation intent sequence.</p>' : ''}
    <div class="plan-meta"><div><h3>Reader entry state</h3><p>Knows that agents can invoke device commands.</p></div><div><h3>Reader exit state</h3><p>Understands why we need to study physical ${state.plan.scope === 'relocation' ? 'preconditions' : 'preconditions and consequences'}.</p></div></div>
    <div class="boundary">Keep out: method details, invented evaluation results, and background already covered in p0.</div>
    <label for="plan-note">Your additional plan constraints</label><textarea id="plan-note" data-field="plan-note" placeholder="For example: do not turn a limitation of this interface into a claim about all platforms.">${esc(state.plan.note)}</textarea>
    <p class="reason">Your text is preserved verbatim. The prototype does not interpret constraints, reorder intents, or adapt candidates. Flag mismatches during the walkthrough.</p>
    <div class="section-title"><h2>Define sentence functions first</h2><small>No prose generated here</small></div>
    ${intentsFor(state.plan).map((intent, index) => `<div class="intent-row"><span class="intent-no">${index + 1}</span><div><h3>${esc(intent.function)}</h3><p>${esc(intent.meaning)}</p><div class="source">${esc(intent.id)} · ${intent.evidence.join(' / ') || 'Author argument transition; no new empirical facts'}</div></div>${button('Inspect sentence', 'focus', `data-id="${intent.id}"`)}</div>`).join('')}
    ${terminologyPanel(state)}
    <div class="plan-actions">${currentApproval(state) ? '<p class="reason">This version has a mock approval. Review a new preview after making changes.</p>' : ''}${button('Preview plan and approval scope', 'preview-plan', 'class="primary"')}</div></article>`;
}
function writingView() {
  const intents = intentsFor(state.plan);
  const intent = fixture.intents.find(i => i.id === state.focus) ?? intents[0];
  const reasons = blockers(state);
  const inPlan = intents.some(i => i.id === intent.id);
  const doc = state.documents[intent.id];
  const priorIds = Object.keys(state.documents).filter(id => !intents.some(i => i.id === id));
  const row = i => `<button type="button" data-action="focus" data-id="${i.id}" class="sentence ${state.focus === i.id ? 'active' : ''}"><span class="prose ${state.documents[i.id] ? '' : 'placeholder'}">${state.documents[i.id] ? esc(state.documents[i.id].text || '(Empty text preserved by the author)') : `[${esc(i.function)}] ${esc(i.meaning)}`}</span><span class="sentence-meta"><span>${esc(i.id)} · ${esc(i.function)}</span><span>${documentStatus(state, i.id)}</span></span></button>`;
  candidateToken = planToken(state);
  return `${heading('03 / WRITING', 'One sentence at a time, in context.', 'Candidates are supplied demo text. Approving a plan and accepting prose are separate actions.')}
    <article class="paper"><div class="eyebrow">${esc(fixture.title)} / Introduction</div><h2 class="paper-title">From commands to physical meaning</h2><div class="neighbor">p0 · Planned role: establish that device commands can be invoked. Only the role is shown; no prose is drafted.</div>
    ${intents.map(row).join('')}
    ${priorIds.length ? `<details open><summary>Previous-plan text is preserved, not silently deleted</summary>${priorIds.map(id => row(fixture.intents.find(i => i.id === id))).join('')}</details>` : ''}
    <div class="neighbor">p2 · Planned role: introduce the scoped contribution. Keep method details out of p1.</div></article>
    <div class="section-title"><h2>${esc(intent.function)}</h2>${tag(intent.id)}</div>
    ${reasons.length || !inPlan ? `<div class="callout"><strong>Review the plan before accepting a candidate.</strong><br>${reasons.map(esc).join('<br>')}${!inPlan ? '<br>This intent is outside the current plan. Previous text remains available for inspection and editing.' : ''}<div class="row-actions">${button('Review current plan', 'view', 'data-view="structure"')}${state.withdrawn ? button('Inspect evidence impact', 'impact') : ''}</div></div>` : '<div class="callout good">The mock plan is approved. Compare expressions of this one intent; the next sentence is not approved.</div>'}
    ${doc?.unreconciled || state.drafts[intent.id] ? '<div class="callout">Your manual version is preserved. Save any draft and review its intent mapping before replacing it with a supplied candidate.</div>' : ''}
    <p class="reason">Fixed meaning: ${esc(intent.meaning)} Support: ${intent.evidence.join(' / ') || 'Approved argument transition'}.</p>
    ${intent.candidates.map((text, index) => `<article class="card candidate"><div class="card-head"><span class="eyebrow">Supplied candidate ${index === 0 ? 'A' : 'B'}</span>${tag('Supplied text · Not model output', 'neutral')}</div><p class="prose">${esc(text)}</p><div class="row-actions">${button('Accept this sentence (mock)', 'accept', `data-id="${intent.id}" data-index="${index}" class="primary" ${reasons.length || !inPlan || doc?.unreconciled || state.drafts[intent.id] ? 'disabled' : ''}`)}${button('Discuss style preference', 'style', 'class="quiet"')}</div></article>`).join('')}
    <details><summary>Source evidence and boundaries for this sentence</summary>${sourceBindings(state).filter(e => intent.evidence.includes(e.id)).map(e => evidenceCard(e)).join('') || '<p>This is an argument transition, not a new experimental observation.</p>'}</details>
    <article class="card"><h3>Write your own version</h3><p class="reason">Edit freely. Saving does not validate scientific meaning or teach a global style rule.</p>
    <label for="sentence-edit">${esc(intent.id)} · Manual text</label><textarea id="sentence-edit" data-field="sentence-edit" data-id="${intent.id}" placeholder="Write a draft here, even before the upstream plan is approved.">${esc(state.drafts[intent.id]?.text ?? doc?.text ?? '')}</textarea>
    <div class="row-actions">${button('Save manual edit', 'save-edit', `data-id="${intent.id}"`)}${button('Preview intent mapping', 'preview-mapping', `data-id="${intent.id}" ${!doc ? 'disabled' : ''}`)}</div>
    ${state.mapping ? `<div class="callout">Saved preview for ${esc(state.mapping.id)} (document v${state.mapping.version}). Continue editing to test whether the old preview is refused.${button('Inspect saved mapping preview', 'show-mapping')}</div>` : ''}</article>${reviewPanel(state,intent.id)}`;
}

function sidecarView() {
  const prompts = {
    argument: 'Which part of this question matters to you? Is a claim too broad, or its evidence too weak?',
    structure: 'What should the reader take away? Would you start with a concrete case or explain a concept first?',
    writing: 'Does this sentence express only the approved meaning? Which version do you prefer, and why?',
  };
  return `<aside class="sidecar" aria-label="Discussion and review of the current content"><div class="eyebrow">Researcher’s space</div><h2>Start with your judgment</h2><p>${prompts[state.view]}</p>
    <label for="note-draft">Your thoughts · Not an approval</label><textarea id="note-draft" data-field="note-draft" placeholder="Think aloud. No need to fill out internal data structures.">${esc(state.noteDraft)}</textarea><div class="row-actions">${button('Save note', 'add-note', 'class="primary"')}</div>
    <p class="reason">W0 has no AI replies. Notes are saved verbatim; add them to the plan explicitly.</p>
    ${state.notes.slice(-3).map((note, index) => `<div class="note"><div class="source">Author note · ${esc(note.view)} / ${esc(note.section)}</div><p>${esc(note.text)}</p>${button('Add as a proposed constraint', 'note-to-plan', `data-index="${state.notes.length - Math.min(3, state.notes.length) + index}" class="quiet"`)}</div>`).join('')}
    <section class="side-section"><div class="eyebrow">Current commitment</div><h2 data-plan-status>${currentApproval(state) ? 'Plan approved in simulation' : 'Still discussing'}</h2><p data-plan-help>${blockers(state).length ? 'Review the implications before committing the plan. Your drafts stay available.' : 'Accept a candidate for one intent at a time.'}</p><ul class="readiness" data-readiness>${blockers(state).filter(r => r !== 'The current plan has not been explicitly approved.').map(r => `<li>${esc(r)}</li>`).join('')}</ul><div class="row-actions">${button('Plan and boundaries', 'preview-plan')}${button('History', 'history')}</div></section>
    <section class="side-section"><div class="eyebrow">Walkthrough controls</div><h2>Try changing a premise</h2><p>These controls affect only the local synthetic example, not RKA.</p><div class="row-actions">${button(state.withdrawn ? 'Inspect withdrawal impact' : 'Withdraw e3 (mock)', state.withdrawn ? 'impact' : 'withdraw', 'class="danger"')}${button('Change title only', 'metadata')}${button('Advisory style', 'style')}</div></section>
    <section class="side-section"><div class="eyebrow">Not connected</div><p>Subscription host: not connected<br>RKA Core: not connected<br>Model calls: 0 · No API path<br>Walkthrough: not evidence of effectiveness</p></section></aside>`;
}
function render() {
  app.innerHTML = `<div class="layout"><aside class="rail"><div class="brand"><img src="brand/rka-project-plugin-app-icon.svg" width="28" height="28" alt=""><div>RKA Writer<small>Paper Studio · W0</small></div></div><div class="rail-scroll">
    <div class="project"><div class="eyebrow">Research paper / W0</div><h2>${fixture.title}</h2><p>${fixture.subtitle}</p></div>
    <nav aria-label="Paper outline"><div class="eyebrow">Paper outline</div><div class="outline">${fixture.sections.map((section, index) => `${button(`<span class="outline-number">0${index + 1}</span>${section.title}<small>${index === 0 ? 'Target paragraph located' : 'Provisional · Not blocking'}</small>`, 'section', `data-section="${section.id}" class="${state.section === section.id ? 'active' : ''}" aria-current="${state.section === section.id ? 'true' : 'false'}"`)}${index === 0 ? '<div class="target-label">p1 · Cases and the representation gap</div>' : ''}`).join('')}</div></nav>
    </div><div class="rail-footer"><div class="walkthrough-info"><div class="eyebrow">Local walkthrough</div><p>Synthetic case, not a research finding.<br>Fine-grained state, meaningful approvals.</p><div class="row-actions">${button('Walkthrough', 'walkthrough', 'class="quiet"')}${button('About', 'about', 'class="quiet"')}</div></div><div class="theme-control"><label for="theme-mode">Theme</label><select id="theme-mode" aria-label="Appearance theme">${[['system','System'],['light','Light'],['dark','Dark']].map(([mode,label]) => `<option value="${mode}" ${theme.mode === mode ? 'selected' : ''}>${label}</option>`).join('')}</select></div></div></aside>
    <div class="surface"><header class="topbar"><nav class="view-tabs" aria-label="Authoring views">${[['argument','Argument'],['structure','Structure'],['writing','Writing']].map(([view,label]) => button(label,'view',`data-view="${view}" class="${view === state.view ? 'active' : ''}" aria-pressed="${view === state.view}"`)).join('')}</nav><div class="top-actions"><span class="save-label" data-save-label>${esc(saveMessage)}</span>${button(state.sidecar ? 'Hide discussion' : 'Show discussion','toggle-sidecar',`aria-expanded="${state.sidecar}"`)}${button('Export demo','export')}${button('Walkthrough','walkthrough','class="mobile-only"')}${button('New demo','new-demo','class="quiet"')}</div></header>
    <div class="banner">W0 prototype · Supplied text, no model or Core connection. Actions, notes, and drafts stay in this browser. No automatic evaluation tracking. Do not enter sensitive material. ${storageBlocked ? '<strong class="error">Saving is paused. Export this page first.</strong>' : ''}</div>
    ${state.languageUpgrade && !currentApproval(state) ? '<div class="banner">English demo content updated. Your notes, drafts, and historical approvals are preserved in their original language. Review the translated plan before accepting new sentences; previous approvals do not carry over. The original browser archive is untouched.</div>' : ''}
    ${state.workflowUpgrade && !currentApproval(state) ? '<div class="banner">Workflow updated. Previous browser archives are untouched; drafts, notes and history were copied intact. Review terminology and the new exact plan before accepting more text. Old approvals do not authorize the new workflow.</div>' : ''}
    <div class="workspace ${state.sidecar ? '' : 'focus-mode'}"><main class="main-content" id="main" tabindex="-1">${state.view === 'argument' ? argumentView() : state.view === 'structure' ? outlineView() : writingView()}<div class="footer-line">For interaction testing only. This is not a production architecture, verified research evidence, or a qualified subscription host.</div></main>${state.sidecar ? sidecarView() : ''}</div></div></div>`;
}
function openModal(title, content, footer = '') {
  modal.innerHTML = `<div class="modal-head"><h2 id="modal-title">${title}</h2>${button('Close','close-modal','aria-label="Close dialog" class="quiet"')}</div><div class="modal-content">${content}</div>${footer ? `<div class="modal-footer">${footer}</div>` : ''}`;
  if (!modal.open) modal.showModal();
}
function showPlan() {
  planPreview = previewPlan(state);
  const b = planPreview.bundle;
  openModal('Review exactly what you are approving', `<p class="eyebrow">Exact preview · Local simulation only</p><h3>Question and claim</h3><p>${esc(b.question)}</p><p>${esc(b.claim)}</p><div class="callout">${esc(b.boundary)}</div>
    <h3>Paper context and paragraph purpose</h3><p>${esc(b.spine)}</p><p>${esc(b.section)} / ${esc(b.paragraph)}</p><p>${esc(b.purpose)}</p><p>${esc(b.neighboringRoles.join('; '))}</p><p>Author additions: ${esc(b.authorNote || 'None')}</p>
    <h3>Selected evidence and uses</h3>${b.evidence.map(e => `<details><summary>${esc(e.id)} v${e.version} · ${esc(e.role)} · ${esc(e.title)}</summary><blockquote>${esc(e.text)}</blockquote><p>${esc(e.limit)}</p><p>Inference warrant: ${esc(e.warrant)}</p><div class="source">${esc(e.locator)}</div></details>`).join('')}
    <p class="reason">e5 is retained as counterevidence, not as positive support for this paragraph.</p><h3>Sentence functions included in this approval</h3><ol>${b.intents.map(i => `<li><strong>${esc(i.function)}</strong>: ${esc(i.meaning)} <span class="source">${i.evidence.join('/') || 'Author argument transition'}</span></li>`).join('')}</ol>
    <h3>Terminology in this plan</h3>${b.terminology.concepts.map(t => `<p><strong>${esc(t.term)}</strong>: ${esc(t.meaning)} ${esc(t.contrast)}</p>`).join('')}<p>Author naming rationale: ${esc(b.terminology.authorNote || 'None')}</p>
    <h3>Explicitly excluded</h3><p>${b.exclusions.map(esc).join('; ')}.</p><details><summary>Full mock version record</summary><pre>${esc(JSON.stringify(b,null,2))}</pre></details>
    ${blockers(state).filter(r => r !== 'The current plan has not been explicitly approved.').map(r => `<div class="callout">${esc(r)}</div>`).join('')}`,
    `${button('Keep discussing','close-modal')}${button(currentApproval(state) ? 'Plan approved · Go to writing' : 'Approve plan only (mock)','approve-plan','class="primary"')}`);
}
function showImpact() {
  openModal('Evidence changed. Your text did not.', `<p>e3 v2 retains only the observation that the command is available; physical-consequence attribution is withdrawn. These are fixed-case dependency effects, not general semantic detection.</p><ul class="review-list">${impact(state).map(i => `<li><strong>${esc(i.label)} ${tag(i.status, i.status === 'Unaffected' ? 'neutral' : 'warn')}</strong>${esc(i.reason)}</li>`).join('')}</ul><div class="callout">Original approvals, sentences, and manual drafts are preserved. Clicking approve again cannot restore missing evidence.</div><h3>What can you do next?</h3><p>Narrow to the relocation case supported by e2, or park the claim and gather evidence. W0 implements only these two mock paths; record other proposals as discussion notes.</p>`,`${button('Keep for later review','close-modal')}${button('Park this claim','park-impact')}${button('Propose relocation-only plan','narrow','class="primary"')}`);
}
function showStyle() {
  openModal('Your term, prose and tone profile',styleContent(state),`${button('Keep draft; do not adopt','close-modal')}${button('Approve this scoped profile','approve-profile','class="primary"')}`);
}
function showTerms() {
  terminologyPreview = { token: termToken(state), bundle: termBundle(state) };
  openModal('Review the concepts behind these labels', `<p>Lock this small set of definitions together. This is not an approval of claims or prose. Any changed naming rationale requires a new review.</p>${terminologyPreview.bundle.concepts.map(t => `<h3>${esc(t.term)}</h3><p>${esc(t.meaning)}</p><div class="boundary">${esc(t.contrast)}</div>`).join('')}<h3>Your rationale</h3><p>${esc(terminologyPreview.bundle.authorNote || 'No additional rationale.')}</p>`,`${button('Keep discussing','close-modal')}${button('Lock these definitions (mock)','lock-terms','class="primary"')}`);
}
function showReview(id) {
  reviewPreview = previewReview(state,id);
  const blocked = blockers(state).length > 0;
  openModal('Review before revising',reviewContent(reviewPreview,blocked),`${button('Defer this review','defer-review')}${reviewPreview.issue?.layer === 'Science' ? button('Return to claims and evidence','route-review') : ''}${reviewPreview.status === 'no-change' ? button('Keep this wording','keep-review','class="primary"') : ''}${reviewPreview.issue?.repair ? button('Apply this one-sentence repair','apply-review',`class="primary" ${blocked ? 'disabled' : ''}`) : ''}`);
}
function showMapping() {
  const m = state.mapping;
  if (!m) throw Error('Create a mapping preview for a saved sentence first.');
  const intent = fixture.intents.find(i => i.id === m.id);
  openModal('Review the mapping of your manual edit', `<p>Mapping ${esc(m.id)} / document v${m.version}. This confirms a mock mapping, not evidence entailment.</p><h3>Your saved text</h3><blockquote>${esc(m.text)}</blockquote><h3>Intended sentence function</h3><p>${esc(intent.function)}: ${esc(intent.meaning)}</p><div class="callout">Confirm only if meaning, scope, and evidence obligations still match. If meaning changed, close this dialog and revise the plan in Structure.</div>`,`${button('Keep editing; retain preview','close-modal')}${button('Confirm reviewed mapping (mock)','reconcile','class="primary"')}`);
}
const tasks = [
  ['orient','Explain the paper question, audience, and contribution boundaries.'], ['challenge','Inspect an overbroad claim and explain why to narrow or park it.'],
  ['allocate','Locate p1 and explain what belongs in other paragraphs.'], ['discuss','Write a discussion note, then explicitly add it to the plan.'],
  ['commit','Review and mock-approve the exact plan; explain what remains unapproved.'], ['realize','Compare and accept one supplied candidate in context.'],
  ['calibrate','Keep a style draft unadopted, then explicitly approve a scoped term/prose/tone profile.'], ['reconsider','Withdraw e3 and inspect why si-01 and the original paragraph are affected.'],
  ['edit','Edit a sentence, preview its mapping, edit again, and check that the stale preview is refused.'], ['resume','Reload and check that notes, drafts, and pending reviews are restored.'],
  ['read','Ask another reader what the paragraph says and does not establish. The prototype does not simulate human outcomes.'],
  ['terms','Review concept definitions and contrasts before locking the terminology bundle.'],
  ['review','Keep a valid supplied sentence, inspect a qualifier repair and its semantic delta, and route an unsupported safety claim upstream.'],
];
function showWalkthrough() {
  openModal('W0 walkthrough · No automatic pass', `<p>A checkmark records participation, not a test pass or canonical PI approval. Feedback is voluntary and stays in this browser. Review it before export.</p>${tasks.map(([id,label], i) => `<div class="walk-step"><label><input type="checkbox" data-walk="${id}" ${state.walkthrough[id] ? 'checked' : ''}><span>${i + 1}. ${label}</span></label></div>`).join('')}<label for="walk-note">Optional feedback: confusion, omissions, repeated approvals, and improvements</label><textarea id="walk-note" data-field="walk-note">${esc(state.walkthroughDraft)}</textarea><p class="reason">Distinguish observations, participant impressions, and facilitator interpretations. The prototype does not time or evaluate behavior automatically.</p>`,`${button('Export current demo record','export')}${button('Return to prototype','close-modal','class="primary"')}`);
}
function exportState() {
  const payload = { label:'W0 synthetic simulation; not canonical PI decisions or human validation evidence', state,
    storageWarning:storageBlocked ? saveMessage : null };
  const url = URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)], { type:'application/json' }));
  const link = document.createElement('a'); link.href = url; link.download = `rka-writer-w0-${Date.now()}.json`; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  notify('Demo download requested. Safeguard any manually entered content in the file.');
}

document.addEventListener('input', event => {
  const el = event.target;
  if (el.dataset.field === 'note-draft') state.noteDraft = el.value;
  else if (el.dataset.field === 'walk-note') state.walkthroughDraft = el.value;
  else if (el.dataset.field === 'sentence-edit') stageEdit(state, el.dataset.id, el.value);
  else if (el.dataset.field === 'purpose') state.plan.purpose = el.value;
  else if (el.dataset.field === 'plan-note') state.plan.note = el.value;
  else if (el.dataset.field === 'question-draft') state.workflow.questionDraft = el.value;
  else if (el.dataset.field === 'term-note') state.workflow.termNote = el.value;
  else if (el.dataset.warrant && Object.hasOwn(state.workflow.warrants,el.dataset.warrant)) state.workflow.warrants[el.dataset.warrant] = el.value;
  else if (styleFields.includes(el.dataset.style)) state.workflow.styleDraft[el.dataset.style] = el.value;
  else return;
  save(); // Persist exact draft, without re-rendering and disturbing the caret.
});
document.addEventListener('change', event => {
  if (event.target.id === 'theme-mode') { theme.set(event.target.value); return; }
  if (event.target.dataset.field === 'narrative') { changePlan(state,{ narrative:event.target.value }); save(); render(); }
  if (event.target.dataset.walk) { state.walkthrough[event.target.dataset.walk] = event.target.checked; save(); }
  if (event.target.dataset.evidence) { toggleEvidence(state,event.target.dataset.evidence); save(); render(); }
  if (event.target.dataset.style === 'scope' && ['paragraph','section'].includes(event.target.value)) { state.workflow.styleDraft.scope = event.target.value; save(); }
});
document.addEventListener('click', event => {
  const el = event.target.closest('button[data-action]');
  if (!el || el.disabled) return;
  const a = el.dataset.action;
  try {
    if (a === 'close-modal') { modal.close(); return; }
    if (a === 'export') { exportState(); return; }
    if (a === 'preview-plan') { showPlan(); return; }
    if (a === 'impact') { showImpact(); return; }
    if (a === 'style') { showStyle(); return; }
    if (a === 'preview-terms') { showTerms(); return; }
    if (a === 'review-sentence') { showReview(el.dataset.id); return; }
    if (a === 'walkthrough') { showWalkthrough(); return; }
    if (a === 'show-mapping') { showMapping(); return; }
    if (a === 'history') { openModal('Preserved demo state and history', `<p>There are ${state.approvals.length} plan approvals and ${state.history.length} historical sentence snapshots. These records support demo recovery, not canonical research decisions.</p><h3>Action log</h3><pre>${esc(JSON.stringify(state.events,null,2))}</pre><h3>Historical text</h3><pre>${esc(JSON.stringify(state.history,null,2))}</pre>`); return; }
    if (a === 'about') { openModal('A disposable W0 prototype', '<p>This tests views, approval granularity, evidence changes, style consent, and recovery. All research content is synthetic. There are no RKA, model, telemetry, or external network requests.</p><h3>Storage and limits</h3><p>Demo actions, notes, and unsubmitted drafts are autosaved in this browser. Clearing browser data can erase them; use Export demo to keep a copy. This is not a production database, cross-tab collaboration, or file sync. Saving pauses when another tab writes to the same slot.</p><p>Supplied content and state logic live in fixture.mjs and state.mjs. Layout, approval-bundle size, and style controls remain hypotheses for the walkthrough.</p>'); return; }
    if (a === 'new-demo') { openModal('Preserve the archive, then start a new demo', '<p>The old state is retained under a separate browser archive key, not deleted. Export a copy first. Archives are inspectable as raw JSON; there is no restore picker yet.</p>', `${button('Export a copy first','export')}${button('Cancel','close-modal')}${button('Archive and start new','confirm-new','class="primary"')}`); return; }
    if (a === 'confirm-new') {
      if (storageBlocked || localStorage.getItem(STORAGE_KEY) !== lastStored || (legacyStored !== null && localStorage.getItem(sourceStorageKey) !== legacyStored)) throw Error('Export and reload to resolve the archive conflict before starting a new demo.');
      localStorage.setItem(`${STORAGE_KEY}:archive:${Date.now()}`, serialize(state));
      state = createState(); planPreview = null; candidateToken = null; terminologyPreview = null; reviewPreview = null; modal.close();
    } else if (a === 'view') { state.view = el.dataset.view; }
    else if (a === 'section') { state.section = el.dataset.section; state.view = 'structure'; }
    else if (a === 'focus') { state.focus = el.dataset.id; state.section = 'intro'; state.view = 'writing'; }
    else if (a === 'toggle-sidecar') state.sidecar = !state.sidecar;
    else if (a === 'toggle-claim') changePlan(state,{ selected:!state.plan.selected });
    else if (a === 'discuss-claim') { const c = fixture.claims.find(c => c.id === el.dataset.id); state.noteDraft = [state.noteDraft,`Regarding “${c.label}”, my judgment is: `].filter(Boolean).join('\n'); state.sidecar = true; }
    else if (a === 'choose-scope') { changePlan(state,{ scope:el.dataset.scope }); notify('Question, claim, and intent branch updated. Review the paragraph purpose and evidence; no text was rewritten.'); }
    else if (a === 'propose-question') {
      if (!state.workflow.questionDraft.trim()) throw Error('Write the question you want to discuss.');
      if (state.workflow.questionProposal) state.notes.push({ text:state.workflow.questionProposal, view:'argument', section:'intro', intent:state.focus });
      state.workflow.questionProposal = state.workflow.questionDraft;
      notify('Question submitted for upstream discussion. Supplied candidates are paused.');
    }
    else if (a === 'park-question') {
      state.notes.push({ text:state.workflow.questionProposal, view:'argument', section:'intro', intent:state.focus });
      state.workflow.questionProposal = '';
      notify('Proposal preserved as an author note. The supplied question is active again.');
    }
    else if (a === 'lock-terms') { lockTerms(state,terminologyPreview); modal.close(); notify('Definitions locked for this exact naming rationale. Claims and prose remain unapproved.'); }
    else if (a === 'approve-profile') { approveProfile(state); modal.close(); notify('Scoped advisory profile approved. No sentence or scientific commitment changed.'); }
    else if (a === 'stage-exercise') {
      const example = reviewExamples.find(e => e.id === el.dataset.example);
      if (!example || state.drafts[example.intent]) throw Error('An unsaved draft exists. Save it first; it will not be replaced.');
      stageEdit(state,example.intent,example.text); state.focus = example.intent; state.view = 'writing';
      notify('Exercise staged in the manual editor for si-01. Save it explicitly to review it. Previous saved text remains intact.');
    }
    else if (['keep-review','defer-review','apply-review','route-review'].includes(a)) {
      resolveReview(state,reviewPreview,a === 'apply-review' ? 'apply' : a === 'keep-review' ? 'keep' : 'defer');
      if (a === 'route-review') state.view = 'argument';
      modal.close(); notify(a === 'apply-review' ? 'One repair saved as a new manual version. Review its intent mapping; previous text is retained.' : 'Review decision recorded. No text changed.');
    }
    else if (a === 'add-note') { addNote(state); notify('Note saved. No plan was approved and no reply was generated.'); }
    else if (a === 'note-to-plan') { const n = state.notes[Number(el.dataset.index)]; changePlan(state,{ note:[state.plan.note,n.text].filter(Boolean).join('\n') }); state.view = 'structure'; notify('Added as a proposed plan constraint. Not yet approved.'); }
    else if (a === 'approve-plan') { approvePlan(state,planPreview); state.view = 'writing'; state.focus = intentsFor(state.plan)[0].id; modal.close(); notify('Only the displayed mock plan was approved. Review prose one sentence at a time.'); }
    else if (a === 'accept') { acceptCandidate(state,el.dataset.id,Number(el.dataset.index),candidateToken); notify('This sentence was mock-accepted. Other sentences and style rules did not change.'); }
    else if (a === 'withdraw') { withdrawEvidence(state); save(); render(); showImpact(); return; }
    else if (a === 'narrow') { changePlan(state,{ scope:'relocation', selected:true, purpose:'Use the selected relocation case to explain a physical precondition absent from the label, then motivate its representation.' }); state.view = 'structure'; state.focus = 'si-02'; modal.close(); notify('A narrowed plan is proposed. Original text and approvals are preserved; review the new plan.'); }
    else if (a === 'park-impact') { changePlan(state,{ selected:false }); modal.close(); }
    else if (a === 'metadata') { changeMetadata(state); notify('Only the display title changed. Source text, uses, and bindings are unchanged. No reapproval or rewrite is needed.'); }
    else if (a === 'save-edit') { saveEdit(state,el.dataset.id); notify('Manual text preserved, pending your intent-mapping review.'); }
    else if (a === 'preview-mapping') { previewMapping(state,el.dataset.id); save(); showMapping(); return; }
    else if (a === 'reconcile') { reconcile(state); modal.close(); notify('Mock mapping explicitly confirmed. Historical text remains preserved.'); }
    if (['choose-scope','propose-question','park-question','lock-terms','approve-profile','stage-exercise'].includes(a)) {
      state.revision += 1; state.events.push({ sequence:state.revision, type:a, simulation:true });
    }
    save(); render();
    if (['view','section','focus','approve-plan','narrow','note-to-plan','confirm-new'].includes(a)) {
      document.querySelector('#main').focus({ preventScroll:true });
      window.scrollTo({ top:0 });
    }
  } catch (error) { notify(error.message); }
});
render();
if (resumed) notify('Restored local notes, drafts, history, and pending reviews, without relying on chat memory.');
if (storageBlocked) notify('The existing archive was not overwritten. This page can be used temporarily and exported. Inspect the old archive first.');
