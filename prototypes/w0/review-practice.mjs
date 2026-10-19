// Separate, supplied-text practice state. Never reads or writes the paper state.
import { semanticReviewCases, annotatedReview, reviewSource } from './review-fixtures.mjs';
import { probeExpressionReview, equalReviewValue } from './review-probe.mjs';

export const REVIEW_KEY = 'rka-writer:w0:review-practice:v1';
export const practiceCases = {
  H1: { title: 'Preserve a quantitative boundary', short: 'Quantity boundary',
    purpose: 'Describe the gallery area without implying an exact measurement.',
    protected: 'A strict lower bound: more than 3,000 square feet. No exact area is established.',
    explanation: 'The draft keeps the digits but changes a lower bound into an exact value.',
    repair: 'Restore the lower bound',
    question: 'What evidence establishes an exact area rather than a lower bound?',
    delta: 'Restores the lower bound. The source record is unchanged; the draft proposition is corrected.' },
  H2: { title: 'Keep unknown implementation details unknown', short: 'Unsupported mechanism',
    purpose: 'Describe replacement of the old traversal without inventing the new implementation.',
    protected: 'The old traversal had O(n²) cost. The new mechanism and lookup cost are not given.',
    explanation: 'Neither a hash map nor O(1) lookups follow from replacing the previous traversal.',
    repair: 'Remove unsupported details',
    question: 'Which source establishes the current data structure and the cost of its lookups?',
    delta: 'Removes unsupported mechanism and lookup-cost assertions. Retains replacement and the old traversal cost.' },
};
export const reviewRules = [
  ['E1', 'Importance and authority', 'Is the claimed significance or authority supported?', 'Preserve bounded contributions and attributed interpretations.'],
  ['E2', 'Framing, contrast and closure', 'Does this move add a distinction or needed orientation?', 'Preserve informative contrasts, signposting and new consequences.'],
  ['E3', 'Parallelism and repetition', 'Does repetition obscure a relationship or add reading work?', 'Preserve genuine lists and repeated canonical terms.'],
  ['E4', 'Actors and relationships', 'Can the reader identify the actor, action and supported relation?', 'Preserve useful passive voice; do not turn association into causation.'],
  ['E5', 'Qualifications and scope', 'Can wording be shortened without changing the boundary?', 'Preserve may, only, conditions, quantitative bounds and uncertainty.'],
  ['E6', 'Chat residue and formatting', 'Does a wrapper or decoration interfere with the document?', 'Preserve quotations, required headings, ranges and mathematical notation.'],
  ['E7', 'Reader fit', 'Is this context already established, or does the reader still need it?', 'Preserve explanations appropriate to this section and audience.'],
];
const fixtureFor = id => {
  const fixture = semanticReviewCases.find(item => item.id === id);
  if (!fixture) throw Error('Unknown review case.');
  return fixture;
};
export const practiceCase = (state, id = state.selected) => {
  fixtureFor(id);
  return state.cases[id];
};
export function createPractice() {
  return { schema: 1, fixtureCommit: reviewSource.commit, selected: 'H1', cases: Object.fromEntries(
    semanticReviewCases.map(f => [f.id, { draft: f.candidates.unsafe.text, revision: 1,
      sourceRevision: f.base.revision, inspected: false, disposition: 'open',
      preview: null, confirmations: [], history: [] }])) };
}
export function assessPractice(state, id = state.selected) {
  const c = practiceCase(state, id), f = fixtureFor(id);
  const variant = c.draft === f.base.text ? 'unchanged'
    : Object.keys(f.candidates).find(key => f.candidates[key].text === c.draft);
  const base = { ...f.base, revision: c.sourceRevision };
  if (!variant) return probeExpressionReview(base, { revision: String(c.revision), text: c.draft }, null);
  const data = annotatedReview(id, variant);
  return probeExpressionReview(base, data.candidate, data.assessment);
}
export function inspectPractice(state) {
  const c = practiceCase(state);
  c.inspected = true; c.disposition = 'open'; c.preview = null;
}
export function editPractice(state, text, origin = 'manual') {
  if (typeof text !== 'string') throw Error('The draft must be text.');
  const c = practiceCase(state);
  if (c.draft === text) return;
  if (origin === 'supplied') c.history.push({ action: 'replace-draft', text: c.draft, revision: c.revision });
  c.draft = text; c.revision += 1; c.disposition = 'open';
  // Keep the prior preview visible, but it can no longer authorize confirmation.
}
export function usePracticeAlternative(state, variant) {
  const f = fixtureFor(state.selected);
  if (!['equivalent', 'unchanged'].includes(variant)) throw Error('Unsupported replacement choice.');
  editPractice(state, variant === 'unchanged' ? f.base.text : f.candidates.equivalent.text, 'supplied');
}
function previewFor(state) {
  const c = practiceCase(state), f = fixtureFor(state.selected), assessment = assessPractice(state);
  if (!c.inspected || c.disposition !== 'open') throw Error('Inspect or resume this case before previewing.');
  if (!['no-change', 'equivalent-under-annotations'].includes(assessment.status)) {
    throw Error('This wording is not eligible for confirmation. Keep the draft or request evidence review.');
  }
  return { caseId: state.selected, revision: c.revision, sourceRevision: c.sourceRevision,
    sourceText: f.base.text, before: c.confirmations.at(-1)?.text ?? f.candidates.unsafe.text,
    after: c.draft, assessment: assessment.status, confirmationCount: c.confirmations.length };
}
export function previewPractice(state) {
  const preview = previewFor(state);
  practiceCase(state).preview = structuredClone(preview);
  return preview;
}
export function practicePreviewCurrent(state) {
  try { return equalReviewValue(practiceCase(state).preview, previewFor(state)); }
  catch { return false; }
}
export function confirmPractice(state, displayedPreview) {
  const c = practiceCase(state);
  if (!displayedPreview || !practicePreviewCurrent(state)
    || !equalReviewValue(displayedPreview, c.preview)) throw Error('The preview expired. Review the current draft again.');
  c.confirmations.push({ text: c.draft, version: c.confirmations.length + 1,
    preview: structuredClone(displayedPreview), simulation: true });
  c.history.push({ action: c.preview.before === c.draft ? 'keep-wording' : 'confirm-revision',
    text: c.draft, revision: c.revision });
  c.disposition = 'confirmed'; c.preview = null;
}
export function deferPractice(state, disposition) {
  if (!['deferred', 'evidence-review', 'rejected'].includes(disposition)) throw Error('Unknown review disposition.');
  const c = practiceCase(state);
  c.history.push({ action: disposition, text: c.draft, revision: c.revision });
  c.disposition = disposition; c.preview = null;
}
export function selectPractice(state, id) { fixtureFor(id); state.selected = id; }

export function parsePractice(raw) {
  const s = JSON.parse(raw);
  const obj = v => v !== null && typeof v === 'object' && !Array.isArray(v);
  const positive = v => Number.isInteger(v) && v > 0;
  const preview = p => obj(p) && Object.hasOwn(practiceCases, p.caseId) && positive(p.revision)
    && ['sourceRevision', 'sourceText', 'before', 'after', 'assessment'].every(k => typeof p[k] === 'string')
    && Number.isInteger(p.confirmationCount) && p.confirmationCount >= 0;
  if (!obj(s) || s.schema !== 1 || s.fixtureCommit !== reviewSource.commit
    || !Object.hasOwn(practiceCases, s.selected) || !obj(s.cases)
    || Object.keys(s.cases).length !== 2 || !Object.keys(practiceCases).every(id => {
      const c = s.cases[id];
      return obj(c) && typeof c.draft === 'string' && positive(c.revision)
        && typeof c.sourceRevision === 'string' && typeof c.inspected === 'boolean'
        && ['open', 'deferred', 'evidence-review', 'rejected', 'confirmed'].includes(c.disposition)
        && (c.preview === null || preview(c.preview)) && Array.isArray(c.confirmations)
        && c.confirmations.every((r, i) => obj(r) && r.version === i + 1 && typeof r.text === 'string'
          && r.simulation === true && preview(r.preview) && r.preview.caseId === id && r.text === r.preview.after)
        && (c.disposition !== 'confirmed' || (c.confirmations.length > 0
          && c.draft === c.confirmations.at(-1).text && c.revision === c.confirmations.at(-1).preview.revision))
        && Array.isArray(c.history) && c.history.every(h => obj(h) && typeof h.action === 'string'
          && typeof h.text === 'string' && positive(h.revision));
    })) throw Error('Unknown or damaged review archive. The stored original is preserved.');
  return s;
}

export function createPracticeStore(storage) {
  let raw = null, warning = '', state = createPractice();
  try { raw = storage.getItem(REVIEW_KEY); if (raw !== null) state = parsePractice(raw); }
  catch (error) { warning = error.message; }
  const assertWritable = () => {
    if (warning) throw Error(warning);
    if (storage.getItem(REVIEW_KEY) !== raw) throw Error('Review storage changed in another tab. Export this draft and reload; nothing will be overwritten.');
  };
  return {
    get state() { return state; },
    get warning() { return warning; },
    export() { return { label: 'W0 review practice; not manuscript approval or semantic validation', state,
      storageWarning: warning || null, preservedArchive: warning ? raw : null }; },
    commit(next, requirePersistence = false) {
      parsePractice(JSON.stringify(next));
      try {
        assertWritable();
        const nextRaw = JSON.stringify(next);
        storage.setItem(REVIEW_KEY, nextRaw); raw = nextRaw; state = next;
      } catch (error) {
        warning = error.message;
        if (requirePersistence) throw Error(`Confirmation was not recorded. ${warning}`);
        state = next; // Preserve unsaved human drafts in memory for explicit export.
      }
    },
    changedExternally() { warning = 'Review storage changed in another tab. Export this draft and reload; saving is paused.'; },
  };
}
