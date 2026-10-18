import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fixture } from './fixture.mjs';
import { createState, approvePlan, previewPlan, planBundle, planToken, currentApproval, blockers,
  acceptCandidate, stageEdit, saveEdit, previewReview, resolveReview, changePlan, withdrawEvidence,
  serialize, deserialize, migratePrevious, STORAGE_KEY, PREVIOUS_STORAGE_KEY, LEGACY_STORAGE_KEY } from './state.mjs';
import { lockTerms, termToken, termBundle, termsReady, toggleEvidence, approveProfile, reviewExamples } from './workflow.mjs';
import { questionControls, evidenceControls, terminologyPanel, styleContent, reviewContent } from './workflow-view.mjs';

const lock = s => lockTerms(s,{ token:termToken(s), bundle:termBundle(s) });
const ready = () => { const s = createState(); lock(s); approvePlan(s,previewPlan(s)); return s; };
const exercise = (example = reviewExamples[0]) => {
  const s = ready(); stageEdit(s,example.intent,example.text); saveEdit(s,example.intent); return s;
};

test('definitions require separate explicit review; a plan approval cannot bypass it', () => {
  const s = createState(); assert.equal(termsReady(s),false);
  assert.throws(() => approvePlan(s,previewPlan(s)),/definitions/);
  lock(s); assert.equal(s.approvals.length,0); assert.deepEqual(s.documents,{});
  approvePlan(s,previewPlan(s)); assert.equal(blockers(s).length,0);
});
test('term preview and lock are invalidated by rationale changes, preserving the old lock', () => {
  const s = ready(); const old = structuredClone(s.workflow.termLock);
  const p = { token:termToken(s), bundle:termBundle(s) };
  s.workflow.termNote = 'Protect the distinction between a condition and an outcome.';
  assert.equal(termsReady(s),false); assert.equal(currentApproval(s),undefined);
  assert.throws(() => lockTerms(s,p),/expired/);
  lock(s); assert.deepEqual(s.workflow.termHistory,[old]);
  assert.throws(() => acceptCandidate(s,'si-01',0,planToken(s)),/approved/);
});
test('hidden term definitions cannot ride along with a visible preview', () => {
  const s = createState(); const p = { token:termToken(s), bundle:termBundle(s) };
  p.bundle.concepts[0].meaning = 'Unexpected change';
  assert.throws(() => lockTerms(s,p)); assert.equal(s.workflow.termLock,null);
});
test('required evidence exclusion blocks reapproval and preserves text', () => {
  const s = ready(); acceptCandidate(s,'si-01',0,planToken(s)); const before = serialize(s.documents);
  toggleEvidence(s,'e2'); assert.ok(!planBundle(s).evidence.some(e => e.id === 'e2'));
  assert.throws(() => approvePlan(s,previewPlan(s)),/e2/); assert.equal(serialize(s.documents),before);
});
test('counterevidence cannot be selected as support', () => {
  const s = ready(), before = serialize(s); assert.throws(() => toggleEvidence(s,'e5'),/Counterevidence/);
  assert.throws(() => toggleEvidence(s,'__proto__')); assert.equal(serialize(s),before);
});
test('a narrowed branch does not consume e3, while e4 cannot be dropped', () => {
  const s = ready(); toggleEvidence(s,'e3'); changePlan(s,{ scope:'relocation' });
  approvePlan(s,previewPlan(s)); assert.equal(blockers(s).length,0);
  toggleEvidence(s,'e4'); assert.throws(() => approvePlan(s,previewPlan(s)),/e4/);
});
test('warrant edits are exact approval inputs; blank warrants block admission', () => {
  const s = ready(), p = previewPlan(s); s.workflow.warrants.e2 = 'My revised warrant.';
  assert.throws(() => approvePlan(s,p),/Preview/);
  assert.equal(planBundle(s).evidence.find(e => e.id === 'e2').warrant,'My revised warrant.');
  s.workflow.warrants.e2 = '  '; assert.throws(() => approvePlan(s,previewPlan(s)),/warrant/);
});
test('different proposed question routes upstream, without inferring new prose', () => {
  const s = ready(); s.workflow.questionProposal = 'What about safety?';
  assert.throws(() => acceptCandidate(s,'si-01',0,planToken(s)),/new claim/);
  assert.deepEqual(s.documents,{}); assert.equal(currentApproval(s),undefined);
});
test('style draft is not a profile; adoption is explicit and scoped, not a rewrite', () => {
  const s = ready(), token = planToken(s); s.workflow.styleDraft.tone = 'My own tone.';
  assert.equal(s.workflow.profiles.length,0); approveProfile(s);
  assert.equal(s.workflow.profiles[0].profile.tone,'My own tone.');
  assert.equal(s.workflow.profiles[0].profile.scope,'paragraph');
  assert.equal(planToken(s),token); assert.deepEqual(s.documents,{});
  approveProfile(s); assert.equal(s.workflow.profiles.length,1);
  s.workflow.styleDraft.scope = 'section'; approveProfile(s);
  assert.equal(s.workflow.profiles[0].profile.scope,'paragraph'); assert.equal(s.workflow.profiles.length,2);
});
test('sample-based input requires source and author interpretation, without extraction', () => {
  const s = ready(); s.workflow.styleDraft.passage = '  An explicitly supplied sample.\n';
  assert.throws(() => approveProfile(s),/source/);
  s.workflow.styleDraft.source = 'Author-provided sample, p. 2';
  s.workflow.styleDraft.admired = 'Keep the qualifiers, not the scientific conclusion.'; approveProfile(s);
  assert.equal(s.workflow.profiles[0].profile.passage,s.workflow.styleDraft.passage);
  assert.equal(s.workflow.profiles[0].origin,'explicit-author-preference');
});
test('invalid profile adoption cannot create an unreadable saved archive', () => {
  const s = ready(); s.workflow.styleDraft.scope = 'global';
  assert.throws(() => approveProfile(s),/scope/); assert.equal(s.workflow.profiles.length,0);
});
test('supplied valid expression allows a no-change record with zero document changes', () => {
  const s = ready(); acceptCandidate(s,'si-01',0,planToken(s)); const before = serialize(s.documents);
  const p = previewReview(s,'si-01'); assert.equal(p.status,'no-change');
  resolveReview(s,p,'keep'); assert.equal(serialize(s.documents),before); assert.equal(s.history.length,0);
});
test('unknown author prose is unassessed, never silently passed or repaired', () => {
  const s = ready(); stageEdit(s,'si-01','My custom text.'); saveEdit(s,'si-01');
  const p = previewReview(s,'si-01'); assert.equal(p.status,'unassessed');
  assert.throws(() => resolveReview(s,p,'keep')); assert.throws(() => resolveReview(s,p,'apply'));
  resolveReview(s,p,'defer'); assert.equal(s.documents['si-01'].text,'My custom text.');
});
test('qualifier repair displays the expressed-proposition delta and changes one sentence only', () => {
  const s = exercise(); const before = structuredClone(s.documents['si-01']);
  acceptCandidate(s,'si-02',0,planToken(s)); const neighbor = serialize(s.documents['si-02']);
  const p = previewReview(s,'si-01'); assert.match(p.issue.semanticDelta,/not meaning-neutral/);
  assert.ok(p.text.includes(p.issue.span)); assert.ok(p.issue.basis && p.issue.consequence);
  resolveReview(s,p,'apply'); assert.equal(s.documents['si-01'].text,p.issue.repair);
  assert.equal(s.documents['si-01'].version,before.version+1); assert.equal(s.documents['si-01'].unreconciled,true);
  assert.deepEqual(s.history.at(-1).document,before); assert.equal(serialize(s.documents['si-02']),neighbor);
  assert.throws(() => resolveReview(s,p,'apply'),/expired/);
});
test('unsupported safety claim has an upstream route, never a polish repair', () => {
  const s = exercise(reviewExamples[1]), before = serialize(s.documents);
  const p = previewReview(s,'si-01'); assert.equal(p.issue.layer,'Science'); assert.equal(p.issue.repair,null);
  assert.throws(() => resolveReview(s,p,'apply'),/upstream/); assert.equal(serialize(s.documents),before);
});
for (const [name, mutate] of [
  ['new saved text',s => { stageEdit(s,'si-01','Newer manual text.'); saveEdit(s,'si-01'); }],
  ['unsaved draft',s => stageEdit(s,'si-01','Still typing')],
  ['new plan',s => changePlan(s,{ note:'A new constraint' })],
  ['evidence withdrawal',s => withdrawEvidence(s)],
  ['adopted profile',s => approveProfile(s)],
]) test(`review refuses stale preview after ${name}`, () => {
  const s = exercise(), p = previewReview(s,'si-01'); mutate(s);
  const before = serialize(s); assert.throws(() => resolveReview(s,p,'apply')); assert.equal(serialize(s),before);
});
test('unapproved style draft does not silently affect an open review', () => {
  const s = exercise(), p = previewReview(s,'si-01'); s.workflow.styleDraft.tone = 'Draft advice';
  resolveReview(s,p,'apply'); assert.equal(s.workflow.profiles.length,0);
});
test('forged repair or preview cannot replace author text', () => {
  const s = exercise(), p = previewReview(s,'si-01'); p.issue.repair = 'A hidden replacement';
  const before = serialize(s); assert.throws(() => resolveReview(s,p,'apply'),/expired/); assert.equal(serialize(s),before);
});
test('new workflow survives serialization including source text, profiles and review decisions', () => {
  const s = exercise(); approveProfile(s); resolveReview(s,previewReview(s,'si-01'),'defer');
  s.workflow.questionDraft = '  Draft question\n'; assert.deepEqual(deserialize(serialize(s)),s);
});
test('English-v1 migration preserves authored fields and old approvals without carrying authority', () => {
  const old = JSON.parse(readFileSync(new URL('./test-fixtures/legacy-session.json',import.meta.url),'utf8'));
  old.fixtureId = fixture.id; old.plan.purpose = '  My English purpose.\n';
  const raw = JSON.stringify(old), s = migratePrevious(raw);
  for (const key of ['documents','drafts','history','events','notes','approvals','mapping','preference','plan']) assert.deepEqual(s[key],old[key],key);
  assert.equal(s.schema,2); assert.equal(termsReady(s),false); assert.equal(currentApproval(s),undefined);
  assert.equal(JSON.stringify(old),raw); assert.throws(() => deserialize(raw));
  assert.equal(new Set([STORAGE_KEY,PREVIOUS_STORAGE_KEY,LEGACY_STORAGE_KEY]).size,3);
});
for (const [name, corrupt] of [
  ['missing workflow',s => { delete s.workflow; }],
  ['unknown evidence',s => s.workflow.selection.push('e5')],
  ['duplicate evidence',s => s.workflow.selection.push('e1')],
  ['non-string warrant',s => { s.workflow.warrants.e1 = {}; }],
  ['broken lock',s => { s.workflow.termLock.token = 'unexpected'; }],
  ['invalid profile scope',s => { s.workflow.styleDraft.scope = 'global'; }],
  ['malformed review',s => s.workflow.reviews.push({ decision:'apply', preview:{} })],
]) test(`archive validation fails closed for ${name}`, () => {
  const s = ready(); corrupt(s); assert.throws(() => deserialize(serialize(s)));
});
test('author input is encoded in all new HTML surfaces', () => {
  const s = ready(), payload = '<img src=x onerror="alert(1)"><script>bad()</script>';
  s.workflow.questionDraft = payload; s.workflow.questionProposal = payload; s.workflow.termNote = payload;
  s.workflow.warrants.e1 = payload; s.workflow.styleDraft.passage = payload;
  const surfaces = [questionControls(s),evidenceControls(s,fixture.evidence[0]),terminologyPanel(s),styleContent(s),reviewContent({ id:'si-01',version:1,text:payload,status:'unassessed',basis:payload },false)];
  for (const html of surfaces) { assert.ok(html.includes('&lt;img')); assert.ok(!html.includes(payload)); assert.ok(!html.includes('<script>')); }
});
