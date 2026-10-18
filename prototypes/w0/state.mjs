// Disposable W0 simulation. This is not a production Authoring Graph or SDK.
import { fixture, intentsFor } from './fixture.mjs';
import { createWorkflow, requiredEvidence, termBundle, workflowBlockers, validateWorkflow, profileToken, reviewExamples } from './workflow.mjs';

export const STORAGE_KEY = 'rka-writer:w0:paper-studio:en:v2';
export const PREVIOUS_STORAGE_KEY = 'rka-writer:w0:paper-studio:en:v1';
export const LEGACY_STORAGE_KEY = 'rka-writer:w0:paper-studio:v1';
const clone = value => structuredClone(value);
export const sourceBindings = state => fixture.evidence.map(e => ({
  ...e, version: e.id === 'e3' && state.withdrawn ? 2 : 1,
  text: e.id === 'e3' && state.withdrawn
    ? 'The command was observed to remain available, but the physical consequence attribution is unverified.' : e.text,
}));

export function createState() {
  return {
    schema: 2, fixtureId: fixture.id, revision: 0, workflow: createWorkflow(),
    view: 'argument', section: 'intro', focus: 'si-01', sidecar: true,
    plan: { scope: 'both', narrative: 'scenario', selected: true,
      purpose: 'Start from concrete cases, distinguish command availability from physical meaning, and introduce the representation problem.',
      note: '', terms: fixture.terms.map(t => t.term) },
    withdrawn: false, metadataRevision: 1,
    approvals: [], documents: {}, history: [], events: [],
    notes: [], noteDraft: '', drafts: {}, mapping: null,
    preference: { actorFirst: false, scope: 'paragraph', history: [] },
    walkthrough: {}, walkthroughDraft: '',
  };
}

export function planBundle(state) {
  const support = requiredEvidence(state).filter(id => state.workflow.selection.includes(id));
  return {
    simulation: true, fixture: fixture.id, protocol: 'w0-researcher-workflow-v2',
    proposedQuestion: state.workflow.questionProposal,
    question: state.plan.scope === 'relocation'
      ? 'How should the physical preconditions of device commands be represented in the selected relocation case?' : fixture.question,
    claim: state.plan.scope === 'relocation'
      ? 'In the selected relocation trace, the command label does not encode a physical precondition required for execution.' : fixture.claims[0].text,
    scope: state.plan.scope, selected: state.plan.selected,
    boundary: fixture.boundary,
    spine: 'Physical meaning in the cases → Scoped representation problem → Approach → Evaluation to be completed',
    section: 'Introduction', paragraph: 'p1 · Cases and the representation gap',
    neighboringRoles: ['p0 establishes context', 'p2 introduces the contribution', 'Method details belong in Representation'],
    purpose: state.plan.purpose, authorNote: state.plan.note,
    narrative: state.plan.narrative,
    evidence: sourceBindings(state).filter(e => support.includes(e.id)).map(e => ({ ...e, warrant: state.workflow.warrants[e.id] })),
    counterevidence: { ...fixture.evidence[4], selectedAsSupport: false },
    intents: intentsFor(state.plan).map(({ candidates, ...intent }) => intent),
    terms: [...state.plan.terms], terminology: termBundle(state),
    exclusions: ['Unseen future sentences', 'Prose in other paragraphs', 'Canonical PI decisions or Core write-back', 'Any model call'],
  };
}

// Equality token, not a cryptographic provenance hash or security attestation.
export const planToken = state => JSON.stringify(planBundle(state));
export function currentApproval(state) {
  return [...state.approvals].reverse().find(a => a.token === planToken(state));
}
export function blockers(state) {
  const reasons = workflowBlockers(state);
  if (!state.plan.selected) reasons.push('The target claim is parked.');
  if (!state.plan.purpose.trim()) reasons.push('First specify the purpose of the target paragraph.');
  if (state.withdrawn && state.plan.scope === 'both') reasons.push('The consequence support in e3 was withdrawn. The paragraph and all its original intents need review.');
  if (!currentApproval(state)) reasons.push('The current plan has not been explicitly approved.');
  return reasons;
}
export function previewPlan(state) {
  return { token: planToken(state), bundle: clone(planBundle(state)) };
}

function event(state, type, detail) {
  state.revision += 1;
  state.events.push({ sequence: state.revision, type, detail, simulation: true });
}
export function changePlan(state, patch) {
  const next = clone(state.plan);
  for (const key of ['purpose', 'note', 'scope', 'narrative', 'selected']) {
    if (Object.hasOwn(patch, key)) next[key] = patch[key];
  }
  if (!['both', 'relocation'].includes(next.scope) || !['scenario', 'representation'].includes(next.narrative)
    || typeof next.purpose !== 'string' || typeof next.note !== 'string' || typeof next.selected !== 'boolean') throw Error('Unsupported demo plan.');
  state.plan = next;
  event(state, 'plan-proposed', clone(patch));
}
export function approvePlan(state, preview) {
  if (!preview || preview.token !== planToken(state) || JSON.stringify(preview.bundle) !== preview.token) throw Error('The plan changed after preview. Preview it again; the old approval will not be applied.');
  const problem = blockers(state).filter(r => r !== 'The current plan has not been explicitly approved.');
  if (problem.length) throw Error(problem.join(' '));
  if (!currentApproval(state)) {
    const approval = { id: `mock-approval-${state.approvals.length + 1}`, token: preview.token, bundle: clone(preview.bundle) };
    state.approvals.push(approval);
    event(state, 'mock-plan-approved', approval.id);
  }
}
export function acceptCandidate(state, id, index, token) {
  if (token !== planToken(state)) throw Error('The candidate plan basis has changed. Review it again.');
  if (blockers(state).length) throw Error(blockers(state).join(' '));
  const intent = intentsFor(state.plan).find(i => i.id === id);
  if (!intent || !Number.isInteger(index) || !intent.candidates[index]) throw Error('This candidate does not belong to an intent in the approved plan.');
  if (state.drafts[id]) throw Error('This sentence has unsaved manual edits. Save or explicitly discard the draft first.');
  const prior = state.documents[id];
  if (prior?.unreconciled) throw Error('The manual edit still needs mapping review. Review it before replacing the sentence.');
  if (prior) state.history.push({ id, document: clone(prior), reason: 'explicit-candidate-replacement' });
  state.documents[id] = { text: intent.candidates[index], version: (prior?.version ?? 0) + 1,
    origin: 'supplied-candidate', approvalId: currentApproval(state).id, token,
    unreconciled: false };
  event(state, 'mock-sentence-accepted', { id, index });
}
export function withdrawEvidence(state) {
  if (!state.withdrawn) {
    state.withdrawn = true;
    event(state, 'evidence-withdrawn', { id: 'e3', oldVersion: 1, newVersion: 2 });
  }
}
export function impact(state) {
  if (!state.withdrawn) return [];
  return [
    { label: 'e3 consequence use', status: 'Invalid', reason: 'The new version no longer supports attribution of the physical consequence.' },
    { label: 'Original c1 / spine / p1', status: 'Needs review', reason: 'The original plan used the consequence support in e3.' },
    { label: 'si-01 · si-04', status: 'Needs review', reason: 'Uses e3 directly and depends on the original paragraph contract.' },
    { label: 'si-02 · si-03 · si-05', status: 'Needs review', reason: 'Direct evidence is unchanged, but these intents still depend on the original paragraph contract.' },
    { label: 'Independent parked branches / style preferences', status: 'Unaffected', reason: 'No dependency on this change; text and historical approvals are preserved.' },
  ];
}
export function changeMetadata(state) {
  state.metadataRevision += 1;
  event(state, 'metadata-only', { id: 'e1', displayRevision: state.metadataRevision,
    basis: 'Only the display title changes. Consumed text, locator and source version stay identical.' });
}
export function setPreference(state, enabled, scope = 'paragraph') {
  if (!['paragraph', 'section'].includes(scope)) throw Error('Choose paragraph or section scope.');
  const prior = clone(state.preference);
  state.preference = { actorFirst: enabled, scope, history: [...prior.history,
    { actorFirst: prior.actorFirst, scope: prior.scope }] };
  event(state, 'explicit-advisory-preference', { enabled, scope });
}
export function stageEdit(state, id, text) {
  if (!fixture.intents.some(i => i.id === id)) throw Error('Unknown sentence.');
  state.drafts[id] = { text, baseVersion: state.drafts[id]?.baseVersion ?? state.documents[id]?.version ?? 0 };
}
export function saveEdit(state, id) {
  const draft = state.drafts[id];
  const prior = state.documents[id];
  if (!draft) throw Error('There is no pending edit to save.');
  if (draft.baseVersion !== (prior?.version ?? 0)) throw Error('The document changed. Your draft is preserved; compare versions before replacing newer text.');
  if (prior) state.history.push({ id, document: clone(prior), reason: 'human-edit' });
  state.documents[id] = { text: draft.text, version: (prior?.version ?? 0) + 1,
    origin: 'human', token: prior?.token ?? null, approvalId: prior?.approvalId ?? null,
    unreconciled: true };
  delete state.drafts[id];
  event(state, 'human-edit-preserved', id);
}
export function previewMapping(state, id) {
  if (state.drafts[id]) throw Error('Save the manual draft before previewing its mapping.');
  const doc = state.documents[id];
  if (!doc) throw Error('There is no saved sentence to map yet.');
  state.mapping = { id, version: doc.version, text: doc.text, token: planToken(state) };
  return state.mapping;
}
export function reconcile(state) {
  const m = state.mapping;
  const doc = m && state.documents[m.id];
  if (!doc || state.drafts[m.id] || doc.version !== m.version || doc.text !== m.text || m.token !== planToken(state)) {
    throw Error('The old mapping preview has expired. New edits are preserved; preview again.');
  }
  if (blockers(state).length || !intentsFor(state.plan).some(i => i.id === m.id)) throw Error('The current intent is not ready. Keep your edit and review upstream state first.');
  state.history.push({ id: m.id, document: clone(doc), reason: 'explicit-mapping-review' });
  doc.unreconciled = false;
  doc.approvalId = currentApproval(state).id;
  doc.token = m.token;
  state.mapping = null;
  event(state, 'mock-human-mapping-reviewed', m.id);
}
export function documentStatus(state, id) {
  const doc = state.documents[id];
  if (!doc) return 'No text yet';
  if (doc.unreconciled) return 'Manual edit · Mapping pending';
  if (!intentsFor(state.plan).some(i => i.id === id)) return 'Previous-plan text · Preserved';
  if (doc.token !== planToken(state) || blockers(state).length) return 'Historical text · Needs review';
  return 'Accepted in simulation';
}
export function addNote(state) {
  if (!state.noteDraft.trim()) throw Error('Write your thoughts first.');
  state.notes.push({ text: state.noteDraft, view: state.view, section: state.section, intent: state.focus });
  state.noteDraft = '';
  event(state, 'author-note-saved', { index: state.notes.length - 1 });
}
export function previewReview(state, id) {
  const doc = state.documents[id];
  if (!doc || state.drafts[id]) throw Error('Save your manual draft before reviewing the current sentence.');
  const example = reviewExamples.find(e => e.intent === id && e.text === doc.text);
  const intent = fixture.intents.find(i => i.id === id);
  const supplied = intent?.candidates.includes(doc.text);
  return { id, version: doc.version, text: doc.text, token: planToken(state), profileToken: profileToken(state),
    status: example ? 'issue' : supplied ? 'no-change' : 'unassessed',
    issue: example ? clone(example) : null,
    basis: supplied ? 'This supplied example retains its defined term, case boundary, and intended function. Keep necessary repetition and qualifiers; no repair is proposed.' : 'No supplied assessment matches this exact wording. Researcher review is needed; absence of a fixture match is not a pass.' };
}
export function resolveReview(state, preview, decision) {
  if (!preview || JSON.stringify(previewReview(state,preview.id)) !== JSON.stringify(preview)) throw Error('Review preview expired. Text, plan, or advisory profile changed; inspect the current version.');
  if (!['keep','defer','apply'].includes(decision)) throw Error('Unknown review decision.');
  if (decision === 'keep' && preview.status !== 'no-change') throw Error('Only the supplied no-change case has a keep outcome.');
  if (decision === 'apply') {
    if (!preview.issue?.repair) throw Error('This issue has no wording-only repair. Return upstream.');
    if (blockers(state).length || !intentsFor(state.plan).some(i => i.id === preview.id)) throw Error('Review the upstream plan before applying this repair.');
    stageEdit(state,preview.id,preview.issue.repair);
    saveEdit(state,preview.id); // New manual version, never an automatic semantic approval.
  }
  state.workflow.reviews.push({ decision, preview: clone(preview) });
  event(state, 'researcher-review-decision', { id: preview.id, decision });
}
export function serialize(state) { return JSON.stringify(state); }
export function deserialize(raw) { return parseState(raw, fixture.id); }
export function migratePrevious(raw) { return parseState(raw, fixture.id, 1); }
function parseState(raw, expectedFixture, expectedSchema = 2) {
  const s = JSON.parse(raw);
  const isObject = v => v !== null && typeof v === 'object' && !Array.isArray(v);
  if (!isObject(s) || s.schema !== expectedSchema || s.fixtureId !== expectedFixture || !Array.isArray(s.approvals)
    || !Array.isArray(s.history) || !Array.isArray(s.events) || !Array.isArray(s.notes)
    || !isObject(s.documents) || !isObject(s.drafts) || !isObject(s.plan) || !isObject(s.preference) || !isObject(s.walkthrough)
    || !['argument', 'structure', 'writing'].includes(s.view)
    || !['both', 'relocation'].includes(s.plan.scope)
    || !['scenario', 'representation'].includes(s.plan.narrative)
    || typeof s.plan.purpose !== 'string' || typeof s.plan.note !== 'string'
    || !Array.isArray(s.plan.terms) || typeof s.noteDraft !== 'string'
    || typeof s.walkthroughDraft !== 'string'
    || !Number.isInteger(s.revision)) throw Error('Incompatible demo archive. The original archive will not be overwritten.');
  const knownIntent = id => fixture.intents.some(i => i.id === id);
  const validDoc = d => isObject(d) && typeof d.text === 'string' && Number.isInteger(d.version)
    && d.version > 0 && typeof d.unreconciled === 'boolean' && (d.token === null || typeof d.token === 'string');
  if (!knownIntent(s.focus) || !fixture.sections.some(section => section.id === s.section)
    || typeof s.sidecar !== 'boolean' || typeof s.withdrawn !== 'boolean'
    || typeof s.plan.selected !== 'boolean' || !s.plan.terms.every(t => typeof t === 'string')
    || !Number.isInteger(s.metadataRevision) || s.metadataRevision < 1
    || !Object.entries(s.documents).every(([id,d]) => knownIntent(id) && validDoc(d))
    || !Object.entries(s.drafts).every(([id,d]) => knownIntent(id) && isObject(d) && typeof d.text === 'string' && Number.isInteger(d.baseVersion))
    || !s.notes.every(n => isObject(n) && typeof n.text === 'string' && typeof n.view === 'string' && typeof n.section === 'string')
    || !s.approvals.every(a => isObject(a) && typeof a.id === 'string' && typeof a.token === 'string' && isObject(a.bundle))
    || !s.history.every(h => isObject(h) && knownIntent(h.id) && validDoc(h.document))
    || typeof s.preference.actorFirst !== 'boolean' || !['paragraph','section'].includes(s.preference.scope)
    || !Array.isArray(s.preference.history)
    || (s.mapping !== null && (!isObject(s.mapping) || !knownIntent(s.mapping.id) || typeof s.mapping.text !== 'string'
      || typeof s.mapping.token !== 'string' || !Number.isInteger(s.mapping.version)))) {
    throw Error('The demo archive is damaged or incompatible. The original archive will not be overwritten.');
  }
  if (expectedSchema === 1) {
    s.schema = 2; s.workflow = createWorkflow(); s.workflowUpgrade = { fromSchema: 1 };
  }
  validateWorkflow(s.workflow);
  planBundle(s);
  return s;
}
