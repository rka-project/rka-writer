import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fixture } from './fixture.mjs';
import { STORAGE_KEY, LEGACY_STORAGE_KEY, createState, planBundle, currentApproval,
  deserialize, serialize, approvePlan, previewPlan, reconcile, acceptCandidate } from './state.mjs';
import { migrateLegacy, LEGACY_FIXTURE_ID } from './legacy-session.mjs';
import { lockTerms, termToken, termBundle } from './workflow.mjs';

// Captured from the previous implementation using only synthetic authored data.
const raw = readFileSync(new URL('./test-fixtures/legacy-session.json', import.meta.url), 'utf8');
const old = JSON.parse(raw);

test('new UI and supplied content are English; source quotations remain supplied text', () => {
  for (const file of ['studio.mjs', 'state.mjs', 'fixture.mjs', 'workflow.mjs', 'workflow-view.mjs', 'index.html']) {
    assert.doesNotMatch(readFileSync(new URL(file, import.meta.url), 'utf8'), /\p{Script=Han}/u, file);
  }
  assert.match(readFileSync(new URL('./index.html', import.meta.url), 'utf8'), /lang="en"/);
  assert.doesNotMatch(JSON.stringify(planBundle(createState())), /\p{Script=Han}/u);
  assert.notEqual(STORAGE_KEY, LEGACY_STORAGE_KEY);
  assert.notEqual(fixture.id, LEGACY_FIXTURE_ID);
  for (const e of old.approvals[0].bundle.evidence) {
    assert.equal(fixture.evidence.find(current => current.id === e.id).text, e.text);
  }
  assert.deepEqual(fixture.terms.map(term => term.term), old.plan.terms);
});

test('legacy upgrade retains original author text, approvals and pending work', () => {
  const s = migrateLegacy(raw);
  for (const field of ['approvals', 'documents', 'history', 'events', 'notes', 'noteDraft', 'drafts', 'mapping', 'preference', 'walkthrough', 'walkthroughDraft']) {
    assert.deepEqual(s[field], old[field], field);
  }
  assert.equal(s.languageUpgrade.originalPresetPurpose, old.plan.purpose);
  assert.equal(s.plan.purpose, createState().plan.purpose);
  assert.equal(JSON.parse(raw).fixtureId, LEGACY_FIXTURE_ID);
  assert.equal(s.fixtureId, fixture.id);
  assert.deepEqual(deserialize(serialize(s)), s);
});

test('old approval and mapping tokens cannot authorize translated demo content', () => {
  const s = migrateLegacy(raw);
  assert.equal(currentApproval(s), undefined);
  assert.throws(() => approvePlan(s, { token:old.approvals[0].token, bundle:old.approvals[0].bundle }));
  assert.throws(() => acceptCandidate(s, 'si-01', 0, old.approvals[0].token));
  assert.throws(() => reconcile(s));
  lockTerms(s,{ token:termToken(s), bundle:termBundle(s) });
  approvePlan(s, previewPlan(s));
  assert.equal(s.approvals.length, old.approvals.length + 1);
  assert.deepEqual(s.approvals[0], old.approvals[0]);
  assert.deepEqual(s.documents, old.documents);
  assert.deepEqual(s.drafts, old.drafts);
});

test('custom purpose and other authored text are never translated', () => {
  const legacy = structuredClone(old);
  legacy.plan.purpose = '  我自己的段落职责。\n';
  legacy.plan.note = '<b>原始约束</b>';
  const s = migrateLegacy(JSON.stringify(legacy));
  assert.equal(s.plan.purpose, legacy.plan.purpose);
  assert.equal(s.plan.note, legacy.plan.note);
  assert.equal(s.languageUpgrade.originalPresetPurpose, null);
});

test('corrupt or unknown legacy snapshots are rejected without a reset', () => {
  assert.throws(() => migrateLegacy('{bad'));
  assert.throws(() => migrateLegacy(JSON.stringify({ ...old, fixtureId:'unknown' })));
  assert.throws(() => migrateLegacy(JSON.stringify({ ...old, plan:null })));
  assert.throws(() => deserialize(raw));
});
