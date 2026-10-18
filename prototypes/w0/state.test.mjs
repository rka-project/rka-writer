import test from 'node:test';
import assert from 'node:assert/strict';
import { fixture, intentsFor } from './fixture.mjs';
import { lockTerms, termToken, termBundle } from './workflow.mjs';
import { createState, planToken, currentApproval, blockers, previewPlan,
  approvePlan, changePlan, acceptCandidate, withdrawEvidence, impact,
  changeMetadata, setPreference, stageEdit, saveEdit, previewMapping, reconcile,
  documentStatus, addNote, serialize, deserialize } from './state.mjs';

const termReview = s => lockTerms(s,{ token:termToken(s), bundle:termBundle(s) });
const approved = () => { const s = createState(); termReview(s); approvePlan(s,previewPlan(s)); return s; };
const accepted = () => { const s = approved(); acceptCandidate(s,'si-01',0,planToken(s)); return s; };

test('new fixture is synthetic, unapproved and contains no accepted prose', () => {
  const s = createState();
  assert.match(s.fixtureId,/synthetic/);
  assert.equal(s.approvals.length,0);
  assert.deepEqual(s.documents,{});
  assert.ok(blockers(s).length);
});
test('plan approval has exact context, evidence, intents and exclusions, not prose', () => {
  const s = approved();
  const b = s.approvals[0].bundle;
  assert.equal(b.intents.length,5);
  assert.deepEqual(b.evidence.map(e => e.id),['e1','e2','e3','e4']);
  assert.equal(b.counterevidence.selectedAsSupport,false);
  assert.ok(b.spine && b.section && b.neighboringRoles.length);
  assert.ok(b.intents.every(i => !Object.hasOwn(i,'candidates')));
  assert.deepEqual(s.documents,{});
});
test('stale preview cannot approve changed purpose or unshown constraints', () => {
  const s = createState(); const p = previewPlan(s);
  changePlan(s,{ note:'New author constraint.' });
  assert.throws(() => approvePlan(s,p),/Preview it again/);
  assert.equal(s.approvals.length,0);
});
test('approval delivery is idempotent for the same plan', () => {
  const s = approved(); const revision = s.revision;
  approvePlan(s,previewPlan(s)); assert.equal(s.approvals.length,1); assert.equal(s.revision,revision);
});
test('unshown additions to a preview bundle are refused', () => {
  const s = createState(); const p = previewPlan(s);
  p.bundle.intents.push({ id:'hidden-intent', meaning:'Unseen addition.' });
  assert.throws(() => approvePlan(s,p),/Preview it again/);
  assert.equal(s.approvals.length,0);
});
test('invalid plan mutations leave the existing plan unchanged', () => {
  const s = approved(); const before = serialize(s);
  assert.throws(() => changePlan(s,{ scope:'unknown' })); assert.equal(serialize(s),before);
});
test('author discussion never grants approval', () => {
  const s = createState(); s.noteDraft = 'I want a narrower claim.'; addNote(s);
  assert.equal(s.notes.length,1); assert.equal(s.approvals.length,0);
  assert.equal(s.plan.note,'');
});
test('one candidate action accepts exactly one sentence, with no style learning', () => {
  const s = accepted(); assert.deepEqual(Object.keys(s.documents),['si-01']);
  assert.equal(s.preference.actorFirst,false);
  assert.equal(s.documents['si-01'].text,fixture.intents[0].candidates[0]);
});
test('unapproved, unknown and stale-target candidates fail closed', () => {
  const s = createState(); assert.throws(() => acceptCandidate(s,'si-01',0,planToken(s)));
  termReview(s);
  approvePlan(s,previewPlan(s));
  assert.throws(() => acceptCandidate(s,'si-05r',0,planToken(s)));
  assert.throws(() => acceptCandidate(s,'si-01',99,planToken(s)));
  const token = planToken(s); changePlan(s,{ narrative:'representation' });
  assert.throws(() => acceptCandidate(s,'si-01',0,token),/basis/);
});
test('parking a claim blocks admission without erasing history', () => {
  const s = accepted(); const before = serialize(s.documents);
  changePlan(s,{ selected:false });
  assert.throws(() => approvePlan(s,previewPlan(s)),/parked/);
  assert.equal(serialize(s.documents),before);
});
test('e3 withdrawal preserves bytes and approvals and blocks all original intents', () => {
  const s = approved();
  for (const i of intentsFor(s.plan)) acceptCandidate(s,i.id,0,planToken(s));
  const bytes = serialize(s.documents); const history = serialize(s.approvals);
  withdrawEvidence(s);
  assert.equal(serialize(s.documents),bytes); assert.equal(serialize(s.approvals),history);
  assert.equal(currentApproval(s),undefined);
  for (const i of intentsFor(s.plan)) {
    assert.throws(() => acceptCandidate(s,i.id,1,planToken(s)),/e3/);
    assert.equal(documentStatus(s,i.id),'Historical text · Needs review');
  }
  assert.ok(impact(s).some(i => i.label.includes('si-01')));
  assert.ok(impact(s).some(i => i.label.includes('si-02') && i.status === 'Needs review'));
});
test('reapproving cannot restore missing evidence', () => {
  const s = accepted(); withdrawEvidence(s);
  assert.throws(() => approvePlan(s,previewPlan(s)),/e3/);
  assert.equal(s.approvals.length,1);
});
test('narrowing creates a new approvable plan, retaining original text lineage', () => {
  const s = accepted(); const prior = serialize(s.documents['si-01']);
  withdrawEvidence(s); changePlan(s,{ scope:'relocation' });
  approvePlan(s,previewPlan(s));
  assert.equal(s.approvals.length,2); assert.equal(serialize(s.documents['si-01']),prior);
  assert.equal(documentStatus(s,'si-01'),'Previous-plan text · Preserved');
  assert.deepEqual(intentsFor(s.plan).map(i => i.id),['si-02','si-03','si-05r']);
  acceptCandidate(s,'si-02',0,planToken(s));
  assert.equal(documentStatus(s,'si-02'),'Accepted in simulation');
});
test('verified display-only change has no scientific invalidation or rewrite', () => {
  const s = accepted(); const token = planToken(s); const before = serialize(s.documents);
  changeMetadata(s); assert.equal(planToken(s),token); assert.equal(serialize(s.documents),before);
  assert.equal(blockers(s).length,0);
});
test('advisory preference and explicit scope override do not alter scientific state', () => {
  const s = accepted(); const token = planToken(s); const before = serialize(s.documents);
  setPreference(s,true,'paragraph'); setPreference(s,true,'section');
  assert.equal(s.preference.history.at(-1).scope,'paragraph');
  assert.equal(planToken(s),token); assert.equal(serialize(s.documents),before);
});
test('manual writing before admission is allowed, never implicitly accepted', () => {
  const s = createState(); stageEdit(s,'si-01','  Human text.\n'); saveEdit(s,'si-01');
  assert.equal(s.documents['si-01'].text,'  Human text.\n');
  assert.equal(s.documents['si-01'].unreconciled,true);
  assert.equal(s.approvals.length,0);
  previewMapping(s,'si-01'); assert.throws(() => reconcile(s));
});
test('candidate acceptance never overwrites pending draft or unreconciled human text', () => {
  const s = accepted(); stageEdit(s,'si-01','My version.');
  assert.throws(() => acceptCandidate(s,'si-01',1,planToken(s)),/manual edit/);
  saveEdit(s,'si-01'); assert.throws(() => acceptCandidate(s,'si-01',1,planToken(s)),/mapping/);
  assert.equal(s.documents['si-01'].text,'My version.');
});
test('interrupted mapping rejects a second edit and preserves both versions', () => {
  const s = accepted(); stageEdit(s,'si-01','First human edit.'); saveEdit(s,'si-01'); previewMapping(s,'si-01');
  stageEdit(s,'si-01','Second human edit.'); saveEdit(s,'si-01');
  assert.throws(() => reconcile(s),/expired/);
  assert.equal(s.documents['si-01'].text,'Second human edit.');
  assert.ok(s.history.some(h => h.document.text === 'First human edit.'));
});
test('unsaved newer draft also invalidates mapping acceptance', () => {
  const s = accepted(); previewMapping(s,'si-01'); stageEdit(s,'si-01','Unsaved edit.');
  assert.throws(() => reconcile(s),/expired/); assert.equal(s.drafts['si-01'].text,'Unsaved edit.');
});
test('explicit current mapping records approval without changing text', () => {
  const s = accepted(); stageEdit(s,'si-01','Author expression.'); saveEdit(s,'si-01');
  previewMapping(s,'si-01'); reconcile(s);
  assert.equal(s.documents['si-01'].text,'Author expression.');
  assert.equal(documentStatus(s,'si-01'),'Accepted in simulation'); assert.equal(s.mapping,null);
});
test('refresh reconstruction retains notes, draft whitespace, impacts and old mapping', () => {
  const s = accepted(); s.noteDraft = 'Unsubmitted note'; previewMapping(s,'si-01');
  stageEdit(s,'si-01','  Exact unsaved text.\n'); withdrawEvidence(s);
  s.walkthroughDraft = 'Optional participant comment';
  const restored = deserialize(serialize(s)); assert.deepEqual(restored,s);
  assert.throws(() => reconcile(restored),/expired/);
});
test('malformed or incompatible local states are refused, not silently reset', () => {
  assert.throws(() => deserialize('{bad'));
  const s = createState(); s.schema = 9; assert.throws(() => deserialize(serialize(s)));
  const t = createState(); t.plan = null; assert.throws(() => deserialize(serialize(t)));
  const u = accepted(); u.documents['si-01'].text = { malformed:true }; assert.throws(() => deserialize(serialize(u)));
  const v = createState(); v.focus = 'unknown'; assert.throws(() => deserialize(serialize(v)));
});
