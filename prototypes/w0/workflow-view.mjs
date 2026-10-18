import { esc, button } from './html.mjs';
import { fixture } from './fixture.mjs';
import { contrasts, requiredEvidence, termsReady, styleFields, reviewExamples } from './workflow.mjs';

export function questionControls(state) {
  const w = state.workflow;
  return `<div class="decision-strip"><h3>Choose this round's scope</h3><p class="reason">These two supplied branches have different claims and sentence functions. You can also propose a different question for discussion.</p>
    <div class="row-actions">${button('Both selected cases','choose-scope',`data-scope="both" aria-pressed="${state.plan.scope === 'both'}"`)}${button('Relocation only','choose-scope',`data-scope="relocation" aria-pressed="${state.plan.scope === 'relocation'}"`)}</div>
    <details ${w.questionProposal ? 'open' : ''}><summary>Propose a different paper question</summary><label for="question-draft">Your proposed question</label><textarea id="question-draft" data-field="question-draft">${esc(w.questionDraft)}</textarea>
    <p class="reason">Saved verbatim. W0 cannot infer new claims or adapt the supplied paragraph. Submitting a different question pauses candidate admission until the proposal is resolved.</p>
    ${button('Submit for upstream discussion','propose-question')}${w.questionProposal ? `<div class="callout"><strong>Unresolved proposal</strong><p>${esc(w.questionProposal)}</p>${button('Keep as note; use supplied question','park-question')}</div>` : ''}</details></div>`;
}
export function evidenceControls(state, e) {
  if (e.id === 'e5') return '<p class="reason">Retained as counterevidence. This cannot be converted into support by a checkbox.</p>';
  const selected = state.workflow.selection.includes(e.id);
  const relevant = requiredEvidence(state).includes(e.id);
  return `<div class="evidence-use"><label class="check-row"><input type="checkbox" data-evidence="${e.id}" ${selected ? 'checked' : ''}><span>${relevant ? 'Include this evidence use' : 'Retain for the parked replacement branch'}</span></label>
    <p class="source">${relevant ? 'Required by the current supplied paragraph contract' : 'Not consumed by the relocation-only plan'}</p>
    <label for="warrant-${e.id}">Why does this source support this use?</label><textarea id="warrant-${e.id}" data-warrant="${e.id}">${esc(state.workflow.warrants[e.id])}</textarea><p class="reason">Author-reviewed warrant, not an automated entailment check.</p></div>`;
}
export function terminologyPanel(state) {
  return `<section class="decision-strip"><div class="section-title"><h2>Concepts before labels</h2><span class="tag">${termsReady(state) ? 'Definitions locked' : 'Proposals need review'}</span></div>
    <p class="reason">Check the distinction each term must preserve. These are synthetic term proposals, not literature-derived recommendations. Renaming a concept needs a new plan; the demo does not replace words automatically.</p>
    ${fixture.terms.map((t,i) => `<details><summary>${esc(t.term)}</summary><p>${esc(t.meaning)}</p><div class="boundary">Do not conflate: ${esc(contrasts[i])}</div><p class="source">Basis: supplied W0 concept definition ${i+1}; no external precedent claimed.</p></details>`).join('')}
    <label for="term-note">Naming rationale or a contrast to protect</label><textarea id="term-note" data-field="term-note" placeholder="Explain what these labels must distinguish. A naming change belongs in upstream discussion.">${esc(state.workflow.termNote)}</textarea>
    <div class="row-actions">${button('Review and lock terminology','preview-terms')}${button('Customize term / prose / tone','style','class="quiet"')}</div></section>`;
}
export function styleContent(state) {
  const d = state.workflow.styleDraft, current = state.workflow.profiles.at(-1);
  const labels = { source: 'Source title and precise locator', passage: 'A passage you explicitly choose (optional)', admired: 'What do you like, and what should not transfer?', term: 'Term preferences', prose: 'Prose preferences', tone: 'Tone preferences' };
  return `<p>Start from your own preferences, or paste a short passage you are permitted to use. You decide which qualities transfer. W0 stores your input but does not read papers or infer style.</p>
    <div class="callout">The initial template below is authored demo guidance, not extracted from a paper. Choosing a sentence does not learn a style rule. Profile approval is a separate action.</div>
    <details ${d.passage ? 'open' : ''}><summary>Optional author-supplied sample and interpretation</summary>${styleFields.slice(0,3).map(k => `<label for="style-${k}">${labels[k]}</label><textarea id="style-${k}" data-style="${k}">${esc(d[k])}</textarea>`).join('')}</details>
    ${styleFields.slice(3).map(k => `<label for="style-${k}">${labels[k]}</label><textarea id="style-${k}" data-style="${k}">${esc(d[k])}</textarea>`).join('')}
    <label for="profile-scope">Explicit scope</label><select id="profile-scope" data-style="scope"><option value="paragraph" ${d.scope === 'paragraph' ? 'selected' : ''}>This paragraph only</option><option value="section" ${d.scope === 'section' ? 'selected' : ''}>Introduction section</option></select>
    <p class="reason">Draft preferences autosave. Only the separate approval below creates a profile version. Profiles remain advisory: they cannot override locked terms, qualifiers, claims or evidence, and do not rewrite supplied candidates.</p>
    <h3>Current approved profile</h3>${current ? `<p>Version ${current.version} · ${esc(current.profile.scope)}</p><pre>${esc(JSON.stringify(current.profile,null,2))}</pre>` : '<p>None. The template has not been adopted.</p>'}
    <details><summary>Preference history (${state.workflow.profiles.length} versions)</summary><pre>${esc(JSON.stringify(state.workflow.profiles,null,2))}</pre><p>Earlier actor-first advice is retained in the legacy preference record; it was not promoted into this profile.</p></details>`;
}
export function reviewPanel(state, id) {
  return `<article class="paper"><div class="eyebrow">Reader-grounded review · Fixed-case exercise</div><h2>Is a change actually needed?</h2><p class="reason">Review one saved sentence against its function, scope and terms. This matches explicit fixtures only: it is not an AI-tic detector, a model critique, or validation of arbitrary text.</p>
    ${button('Review this saved sentence','review-sentence',`data-id="${id}" ${!state.documents[id] || state.drafts[id] ? 'disabled' : ''}`)}
    <details><summary>Try a supplied failure case (optional)</summary><p class="reason">Place one example into the manual editor for si-01. Nothing is accepted or saved as a sentence until you choose Save manual edit. Existing saved text remains intact; unsaved drafts are never replaced.</p>
    ${reviewExamples.map(e => `<div class="card"><h3>${esc(e.label)}</h3><p>${esc(e.text)}</p>${button('Stage this exercise text','stage-exercise',`data-example="${e.id}" ${state.drafts[e.intent] ? 'disabled' : ''}`)}</div>`).join('')}</details></article>`;
}
export function reviewContent(preview, blocked) {
  const issue = preview.issue;
  return `<p class="eyebrow">${esc(preview.id)} · Saved document v${preview.version} · Exact text and plan basis</p><blockquote>${esc(preview.text)}</blockquote>
    ${issue ? `<h3>${esc(issue.layer)} issue · ${esc(issue.label)}</h3><p><strong>Anchor:</strong> ${esc(issue.span)}</p><p><strong>Contract basis:</strong> ${esc(issue.basis)}</p><p><strong>Reader consequence:</strong> ${esc(issue.consequence)}</p>
    <h3>Minimal repair and semantic delta</h3><p>${esc(issue.semanticDelta)}</p>${issue.repair ? `<blockquote>${esc(issue.repair)}</blockquote><p class="reason">Applying creates one new manual sentence version. It still needs your intent-mapping review. Neighbors, claims, term locks, and prior text are unchanged.</p>` : '<div class="callout">No prose patch offered. Revisit the question, claim and evidence.</div>'}`
    : `<h3>${preview.status === 'no-change' ? 'No change proposed' : 'Not assessed'}</h3><p>${esc(preview.basis)}</p>`}
    ${blocked ? '<div class="callout">Upstream readiness is incomplete. This local fixture assessment is not scientific approval, and no repair can be applied yet.</div>' : ''}`;
}
