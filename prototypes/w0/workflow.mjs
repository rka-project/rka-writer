// Bounded interaction fixtures, not language analysis or evidence entailment.
import { fixture } from './fixture.mjs';

export const warrants = {
  e1: 'Labels establish what the example interface exposes, not its physical meaning.',
  e2: 'The selected trace exhibits a required precondition absent from the label.',
  e3: 'Availability persists while the consequence changes in this replacement trace.',
  e4: 'The case boundary limits each inference; it does not add positive evidence.',
};
export const contrasts = [
  'Availability is not successful execution or safety.',
  'A precondition is required before execution; it is not an outcome.',
  'A consequence is an outcome, not a guarantee of safety or benefit.',
];
export const styleFields = ['source', 'passage', 'admired', 'term', 'prose', 'tone'];
export const styleStarter = {
  source: '', passage: '', admired: '',
  term: 'Repeat defined technical terms when the concept is unchanged.',
  prose: 'Keep each sentence focused on its intended reader function.',
  tone: 'State the observed case directly; retain qualifiers for untested scope.',
};
export const reviewExamples = [
  { id: 'qualifier', label: 'Missing scope qualifier', intent: 'si-01',
    text: 'The command remains available, but its physical consequence changes.',
    span: 'The command remains available', layer: 'Expression',
    basis: 'si-01 and e3/e4 restrict the observation to the selected replacement trace.',
    consequence: 'Without a case qualifier, the reader may interpret a case observation as a general statement.',
    repair: fixture.intents[0].candidates[0],
    semanticDelta: 'Scientific claim unchanged. Expressed proposition narrows from an unqualified statement to the selected trace. This is not meaning-neutral polish.' },
  { id: 'safety', label: 'Unsupported safety claim', intent: 'si-01',
    text: 'This representation improves safety across all devices.', span: 'improves safety across all devices',
    layer: 'Science', basis: 'c3 is parked: there is no safety evaluation. e4 also forbids all-device generalization.',
    consequence: 'The reader would infer a demonstrated safety benefit that this case does not establish.',
    repair: null, semanticDelta: 'Return to claim and evidence selection. A softer tone cannot supply missing evaluation.' },
];

export function createWorkflow() {
  return { questionDraft: '', questionProposal: '', selection: ['e1','e2','e3','e4'],
    warrants: { ...warrants }, termNote: '', termLock: null, termHistory: [],
    styleDraft: { ...styleStarter, scope: 'paragraph' }, profiles: [], reviews: [] };
}
export const requiredEvidence = state => state.plan.scope === 'relocation' ? ['e1','e2','e4'] : ['e1','e2','e3','e4'];
export const termBundle = state => ({ concepts: fixture.terms.map((t,i) => ({ ...t, contrast: contrasts[i] })), authorNote: state.workflow.termNote });
export const termToken = state => JSON.stringify(termBundle(state));
export const termsReady = state => state.workflow.termLock?.token === termToken(state);
export function lockTerms(state, preview) {
  if (!preview || preview.token !== termToken(state) || JSON.stringify(preview.bundle) !== preview.token) throw Error('Term preview expired. Review the definitions again.');
  if (!termsReady(state)) {
    if (state.workflow.termLock) state.workflow.termHistory.push(structuredClone(state.workflow.termLock));
    state.workflow.termLock = structuredClone(preview);
  }
}
export function toggleEvidence(state, id) {
  if (!Object.hasOwn(warrants,id)) throw Error('Counterevidence cannot be promoted to positive support in this fixture.');
  const selected = new Set(state.workflow.selection);
  if (selected.has(id)) selected.delete(id); else selected.add(id);
  state.workflow.selection = Object.keys(warrants).filter(key => selected.has(key));
}
export function workflowBlockers(state) {
  const w = state.workflow;
  const reasons = [];
  if (w.questionProposal) reasons.push('Your proposed question needs a new claim/evidence/intent plan. Supplied candidates cannot answer it automatically.');
  for (const id of requiredEvidence(state)) {
    if (!w.selection.includes(id)) reasons.push(`Required use ${id} is excluded. Restore it or revise the claim scope.`);
    else if (!w.warrants[id].trim()) reasons.push(`Explain the inference warrant for ${id}.`);
  }
  if (!termsReady(state)) reasons.push('Review and lock the proposed concept definitions before admitting sentences.');
  return reasons;
}
export function approveProfile(state) {
  const d = state.workflow.styleDraft;
  if (!d || !styleFields.every(k => typeof d[k] === 'string') || !['paragraph','section'].includes(d.scope)) throw Error('Unsupported advisory profile. Choose paragraph or section scope.');
  if (d.passage.trim() && (!d.source.trim() || !d.admired.trim())) throw Error('For a supplied passage, record its source/locator and what you value about it.');
  if (![d.term,d.prose,d.tone].every(s => s.trim())) throw Error('Specify term, prose, and tone preferences before approving this profile.');
  const previous = state.workflow.profiles.at(-1);
  if (previous && JSON.stringify(previous.profile) === JSON.stringify(d)) return;
  state.workflow.profiles.push({ version: state.workflow.profiles.length + 1, profile: structuredClone(d), origin: 'explicit-author-preference', advisory: true });
}
export function profileToken(state) { return JSON.stringify(state.workflow.profiles.at(-1) ?? null); }

// Persisted browser JSON is untrusted. Refuse unknown shapes, never reset them.
export function validateWorkflow(w) {
  const obj = v => v !== null && typeof v === 'object' && !Array.isArray(v);
  const str = v => typeof v === 'string';
  const profile = p => obj(p) && styleFields.every(k => str(p[k])) && ['paragraph','section'].includes(p.scope);
  const lock = t => obj(t) && str(t.token) && obj(t.bundle) && JSON.stringify(t.bundle) === t.token;
  if (!obj(w) || !str(w.questionDraft) || !str(w.questionProposal) || !str(w.termNote)
    || !Array.isArray(w.selection) || new Set(w.selection).size !== w.selection.length || !w.selection.every(id => Object.hasOwn(warrants,id))
    || !obj(w.warrants) || !Object.keys(warrants).every(id => str(w.warrants[id]))
    || (w.termLock !== null && !lock(w.termLock)) || !Array.isArray(w.termHistory) || !w.termHistory.every(lock)
    || !profile(w.styleDraft) || !Array.isArray(w.profiles) || !w.profiles.every((p,i) => obj(p) && p.version === i + 1 && profile(p.profile) && p.advisory === true)
    || !Array.isArray(w.reviews) || !w.reviews.every(r => obj(r) && ['keep','defer','apply'].includes(r.decision) && obj(r.preview)
      && fixture.intents.some(i => i.id === r.preview.id) && str(r.preview.text) && str(r.preview.token)
      && str(r.preview.profileToken) && Number.isInteger(r.preview.version) && r.preview.version > 0)) throw Error('Incompatible workflow archive. The original will not be overwritten.');
}
