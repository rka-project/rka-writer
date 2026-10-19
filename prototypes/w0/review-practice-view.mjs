import { esc } from './html.mjs';
import { semanticReviewCases, reviewSource } from './review-fixtures.mjs';
import { practiceCases, reviewRules, practiceCase, assessPractice, practicePreviewCurrent,
  inspectPractice, editPractice, usePracticeAlternative, previewPractice, confirmPractice,
  deferPractice, selectPractice } from './review-practice.mjs';

const action = (label, name, attrs = '') => `<button type="button" data-review-action="${name}" ${attrs}>${label}</button>`;
const statusLabel = c => ({ open: c.inspected ? 'In review' : 'Ready to inspect', confirmed: 'Confirmed in practice',
  deferred: 'Deferred', 'evidence-review': 'Evidence needed', rejected: 'Draft rejected' })[c.disposition];
const caseFixture = id => semanticReviewCases.find(f => f.id === id);
const draftStatus = (state, warning) => warning ? 'Not saved. Export the draft; confirmation is blocked.'
  : practiceCase(state).disposition === 'confirmed' ? 'Confirmed in practice. Resume review, or edit to start a new draft.'
  : practiceCase(state).disposition !== 'open' ? 'Review paused. Resume review, or edit to start a new draft.'
  : ['no-change','equivalent-under-annotations'].includes(assessPractice(state).status)
    ? 'Supplied assessment available. Preview before confirming.' : 'Not assessed or meaning changed. Draft saved; confirmation is blocked.';
const mark = (text, anchors) => {
  const locations = anchors.map(anchor => ({ anchor, at: text.indexOf(anchor) })).filter(x => x.at >= 0).sort((a,b) => a.at-b.at);
  let cursor = 0, html = '';
  for (const { anchor, at } of locations) {
    if (at < cursor) continue;
    html += esc(text.slice(cursor, at)) + `<mark>${esc(anchor)}</mark>`; cursor = at + anchor.length;
  }
  return html + esc(text.slice(cursor));
};
export function practiceFeedback(state) {
  const c = practiceCase(state), a = assessPractice(state);
  if (!c.inspected) return '<p class="reason">Inspect the supplied finding before choosing a revision.</p>';
  if (a.status === 'meaning-change') return `<div class="callout"><strong>Meaning change · Confirmation blocked</strong><p>${esc(practiceCases[state.selected].explanation)}</p>
    <ul>${a.issues.map(i => `<li>${i.id === 'area' ? 'An exact value replaces the source lower bound.' : i.id === 'new-mechanism' ? 'The source does not establish a hash map.' : i.id === 'new-cost' ? 'The source does not establish O(1) lookups.' : esc(i.code)}</li>`).join('')}</ul>
    <p>Restore the supported meaning or request evidence review. Style approval cannot supply missing facts.</p></div>`;
  if (['no-change','equivalent-under-annotations'].includes(a.status)) return '<div class="callout good"><strong>Supplied alternative · Ready for your review</strong><p>The fixture annotation preserves the source meaning. This is not a model assessment or permission to confirm automatically.</p></div>';
  return `<div class="callout"><strong>${a.status === 'stale' ? 'Source changed · New review needed' : 'Not assessed · Draft preserved'}</strong><p>There is no supplied assessment for this exact wording and source version. This demo cannot validate custom prose. Keep your draft, request evidence review, or choose a supplied alternative.</p></div>`;
}
export function practiceConfirmation(state, warning = '') {
  const c = practiceCase(state), p = c.preview;
  if (!p) return '';
  const current = practicePreviewCurrent(state) && !warning;
  return `<section class="paper review-confirm" id="review-confirmation" tabindex="-1"><div class="eyebrow">3 / Confirm only this displayed revision</div>
    <h2>What changes, and what stays fixed?</h2><div class="review-compare"><div><h3>${c.confirmations.length ? 'Last confirmed wording' : 'Initial exercise draft'}</h3><blockquote>${esc(p.before)}</blockquote></div><div><h3>Proposed wording</h3><blockquote>${esc(p.after)}</blockquote></div></div>
    <p>${p.before === p.after ? 'No wording change. You can keep the current sentence.' : esc(practiceCases[state.selected].delta)}</p>
    <p class="reason">Only ${esc(state.selected)} at draft revision ${p.revision}. Source ${esc(p.sourceRevision)} remains unchanged. The other case, paper, terms and author profile will not change.</p>
    ${!current ? '<p class="blocked" role="status">Preview expired or saving is paused. The current draft is preserved. Make a new preview before confirming.</p>' : ''}
    ${action(p.before === p.after ? 'Confirm no change' : 'Confirm this revision', 'confirm', `class="primary" ${current ? '' : 'disabled'}`)}
    <p class="reason">Records your choice in this practice session only. Does not approve research or write a manuscript.</p></section>`;
}
export function renderPractice(state, warning = '') {
  const id = state.selected, c = practiceCase(state), f = caseFixture(id), meta = practiceCases[id];
  const checked = assessPractice(state), canPreview = c.inspected && c.disposition === 'open'
    && ['no-change','equivalent-under-annotations'].includes(checked.status) && !warning;
  return `<header class="view-heading"><div class="eyebrow">W0 / Review practice</div><h1>Review meaning before changing prose.</h1>
    <p>Two separate exercises. Review a supplied finding, revise one sentence, then confirm the exact change.</p></header>
    <div class="review-scope"><p>Supplied text and findings, not AI analysis. Your paper stays untouched. Custom wording remains unassessed.</p>${action('Export review record', 'export')}</div>
    <div data-review-storage role="status">${warning ? `<div class="callout"><strong>Saving paused</strong><p>${esc(warning)}</p><p>Unsaved drafts can be exported. No confirmation will be recorded.</p></div>` : '<p class="reason">Practice drafts and decisions save separately in this browser.</p>'}</div>
    <nav class="review-case-picker" aria-label="Review exercises">${Object.entries(practiceCases).map(([key,item]) => action(`<span>${key} · ${esc(item.short)}</span><small>${esc(statusLabel(practiceCase(state,key)))}</small>`, 'case', `data-case="${key}" aria-pressed="${key === id}"`)).join('')}</nav>
    <ol class="review-steps" aria-label="Review workflow"><li>1. Inspect the finding</li><li>2. Revise or return upstream</li><li>3. Confirm a version</li></ol>
    <section class="paper"><div class="section-title review-title"><h2 id="review-case-title" tabindex="-1">${esc(meta.title)}</h2><span class="tag" data-case-status>${esc(statusLabel(c))}</span></div>
      <p class="reason">Sentence function: ${esc(meta.purpose)}</p>
      <div class="review-compare"><div><h3>Source statement</h3><blockquote>${mark(f.base.text,f.before.map(a=>a.anchor))}</blockquote><p class="reason">${esc(meta.protected)}</p></div>
      <div><h3>Initial draft under review</h3><blockquote>${mark(f.candidates.unsafe.text, id === 'H1' ? ['exactly 3,000 square feet'] : ['hash map','O(1) lookups'])}</blockquote><p class="reason">A deliberately flawed, supplied rewrite.</p></div></div>
      <details><summary>Source and exercise provenance</summary><p class="reason">Independently worded adaptation of Humanizer ${reviewSource.version}, section ${esc(f.sourceSection)}. This is not evidence about a real gallery or implementation.</p><a href="${reviewSource.repository}/blob/${reviewSource.commit}/SKILL.md" target="_blank" rel="noreferrer">Inspect the pinned source</a></details>
      ${!c.inspected || c.disposition !== 'open' ? `<div class="row-actions">${action(c.inspected ? 'Resume review' : 'Inspect supplied finding', 'inspect', 'class="primary"')}</div>` : ''}
    </section>
    ${c.inspected ? `<section class="paper" id="review-findings" tabindex="-1"><div class="eyebrow">1 / Supplied review</div><h2>Check the scientific boundary</h2>
      <p class="reason">Responsible layer: evidence and scope. This finding is not a preference about vocabulary or punctuation.</p>
      <div data-review-feedback>${practiceFeedback(state)}</div>
      <div class="row-actions">${action('Request evidence review','evidence')}${action('Defer this case','defer','class="quiet"')}${action('Reject this draft','reject','class="quiet"')}</div></section>
      <section class="paper"><div class="eyebrow">2 / Revise one sentence</div><h2>Choose wording you can support</h2>
        <div class="review-compare"><div class="card"><h3>${esc(meta.repair)}</h3><p>${esc(f.candidates.equivalent.text)}</p>${action('Use this supplied revision','equivalent')}</div>
        <div class="card"><h3>Retain the source wording</h3><p>${esc(f.base.text)}</p>${action('Use source wording','unchanged')}</div></div>
        <label for="review-draft">Your working draft</label><textarea id="review-draft" data-review-field="draft" spellcheck="false">${esc(c.draft)}</textarea>
        <p class="reason" data-draft-assessment role="status">${esc(draftStatus(state,warning))}</p>
        <p class="reason">You can edit freely. Only exact supplied alternatives have assessments in this demo; new wording is saved but cannot be confirmed as assessed.</p>
        <div class="row-actions">${action('Preview this revision','preview',`class="primary" data-review-preview ${canPreview ? '' : 'disabled'}`)}</div>
      </section>` : ''}
    <div data-review-confirmation>${practiceConfirmation(state,warning)}</div>
    <section id="review-outcome" tabindex="-1" aria-live="polite">${c.disposition === 'confirmed' ? `<div class="callout good"><strong>Confirmed in practice · Version ${c.confirmations.length}</strong><p>${esc(c.confirmations.at(-1).text)}</p><p>Previous versions are retained. The paper and the other case are unchanged.</p>${id === 'H1' ? action('Continue to H2','case','data-case="H2"') : action('Return to H1','case','data-case="H1"')}</div>`
      : c.disposition === 'evidence-review' ? `<div class="callout"><strong>Awaiting evidence review</strong><p>${esc(meta.question)}</p><p>No evidence task was sent to RKA. The draft is retained, not confirmed.</p></div>`
      : ['deferred','rejected'].includes(c.disposition) ? `<div class="callout"><strong>${c.disposition === 'deferred' ? 'Review deferred' : 'Draft rejected'}</strong><p>Your draft and prior confirmations are retained. Resume when ready; no rewrite was applied.</p></div>` : ''}</section>
    <details class="paper"><summary>Review rules · E1–E7</summary><p class="reason">These are prompts to inspect a reader problem, not word bans or an AI score. A match alone never authorizes a change.</p>
      ${reviewRules.map(([key,title,question,preserve]) => `<article class="review-rule"><h3>${key} · ${esc(title)}</h3><p>${esc(question)}</p><p class="reason">${esc(preserve)}</p></article>`).join('')}</details>
    <details class="paper"><summary>Practice history and confirmation scope (${c.confirmations.length} versions)</summary>
      ${c.history.length ? `<ol>${c.history.map(h=>`<li><strong>${esc(h.action)}</strong> · draft ${h.revision}<p>${esc(h.text)}</p></li>`).join('')}</ol>` : '<p class="reason">No decisions recorded for this case yet.</p>'}
      <p class="reason">Local simulation records only. No scientific validity, model capability or global style learning is implied.</p></details>`;
}

export function mountPractice(root, store, notify) {
  const render = focus => {
    root.innerHTML = renderPractice(store.state, store.warning);
    if (focus) root.querySelector(focus)?.focus({ preventScroll: false });
  };
  render();
  root.addEventListener('input', event => {
    if (event.target.dataset.reviewField !== 'draft') return;
    const next = structuredClone(store.state); editPractice(next,event.target.value); store.commit(next);
    root.querySelector('[data-review-feedback]').innerHTML = practiceFeedback(store.state);
    root.querySelector('[data-review-confirmation]').innerHTML = practiceConfirmation(store.state,store.warning);
    const a = assessPractice(store.state);
    root.querySelector('[data-review-preview]').disabled = !!store.warning || !['no-change','equivalent-under-annotations'].includes(a.status);
    root.querySelector('[data-case-status]').textContent = statusLabel(practiceCase(store.state));
    const caseLabel = root.querySelector(`[data-review-action="case"][data-case="${store.state.selected}"] small`);
    if (caseLabel) caseLabel.textContent = statusLabel(practiceCase(store.state));
    const live = root.querySelector('[data-draft-assessment]'), message = draftStatus(store.state,store.warning);
    if (live.textContent !== message) live.textContent = message;
    root.querySelector('#review-outcome').innerHTML = '';
    if (store.warning) root.querySelector('[data-review-storage]').textContent = `Saving paused. ${store.warning} Export this draft; confirmation is blocked.`;
  });
  root.addEventListener('click', event => {
    const el = event.target.closest('[data-review-action]'); if (!el || el.disabled) return;
    const name = el.dataset.reviewAction;
    if (name === 'export') {
      const url = URL.createObjectURL(new Blob([JSON.stringify(store.export(),null,2)],{type:'application/json'}));
      const a = document.createElement('a'); a.href = url; a.download = `rka-writer-review-practice-${Date.now()}.json`; a.click();
      setTimeout(()=>URL.revokeObjectURL(url),1000); return;
    }
    try {
      const next = structuredClone(store.state);
      if (name === 'case') selectPractice(next,el.dataset.case);
      else if (name === 'inspect') inspectPractice(next);
      else if (['equivalent','unchanged'].includes(name)) usePracticeAlternative(next,name);
      else if (name === 'preview') previewPractice(next);
      else if (name === 'confirm') confirmPractice(next,practiceCase(store.state).preview);
      else if (['evidence','defer','reject'].includes(name)) deferPractice(next, {evidence:'evidence-review',defer:'deferred',reject:'rejected'}[name]);
      else return;
      store.commit(next,name === 'confirm');
      render(name === 'case' ? '#review-case-title' : name === 'inspect' ? '#review-findings'
        : ['equivalent','unchanged'].includes(name) ? '#review-draft' : name === 'preview' ? '#review-confirmation' : '#review-outcome');
    } catch (error) { render(); notify(error.message); }
  });
}
