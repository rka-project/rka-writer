import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { STORAGE_KEY, createState } from './state.mjs';
import { createPractice, practiceCase, assessPractice, inspectPractice, editPractice,
  usePracticeAlternative, previewPractice, practicePreviewCurrent, confirmPractice,
  deferPractice, selectPractice, parsePractice, createPracticeStore, REVIEW_KEY, reviewRules } from './review-practice.mjs';
import { renderPractice } from './review-practice-view.mjs';

const prepared = id => {
  const s = createPractice(); selectPractice(s,id); inspectPractice(s);
  usePracticeAlternative(s,'equivalent'); return s;
};
const memory = () => {
  const map = new Map([[STORAGE_KEY,'untouched paper archive']]);
  return { map, getItem:key=>map.get(key) ?? null, setItem:(key,value)=>map.set(key,value) };
};

for (const id of ['H1','H2']) {
  test(`${id}: finding, revision, exact preview and confirmation are distinct steps`, () => {
    const s = createPractice(), paper = createState(), originalPaper = structuredClone(paper);
    selectPractice(s,id);
    assert.equal(assessPractice(s).status,'meaning-change');
    assert.throws(()=>previewPractice(s),/Inspect/);
    inspectPractice(s);
    assert.throws(()=>previewPractice(s),/not eligible/);
    usePracticeAlternative(s,'equivalent');
    assert.equal(practiceCase(s).confirmations.length,0);
    const p = previewPractice(s);
    assert.equal(practiceCase(s).confirmations.length,0);
    confirmPractice(s,p);
    assert.equal(practiceCase(s).confirmations.length,1);
    assert.equal(practiceCase(s).confirmations[0].text,p.after);
    assert.deepEqual(paper,originalPaper);
    assert.throws(()=>confirmPractice(s,p),/expired/);
  });
  test(`${id}: a custom draft is retained and unassessed`, () => {
    const s = prepared(id), text = '  My own wording with a material caveat.\n';
    editPractice(s,text);
    assert.equal(practiceCase(s).draft,text);
    assert.equal(assessPractice(s).status,'unassessed');
    assert.throws(()=>previewPractice(s),/not eligible/);
    assert.equal(practiceCase(s).confirmations.length,0);
    assert.deepEqual(parsePractice(JSON.stringify(s)),s);
  });
  test(`${id}: source wording can be selected without inventing a new proposition`, () => {
    const s = prepared(id); usePracticeAlternative(s,'unchanged');
    assert.equal(assessPractice(s).status,'no-change');
    confirmPractice(s,previewPractice(s));
    inspectPractice(s);
    const p = previewPractice(s); assert.equal(p.before,p.after);
    confirmPractice(s,p);
    assert.equal(practiceCase(s).history.at(-1).action,'keep-wording');
  });
}

for (const [label,alter] of [
  ['draft bytes',s=>editPractice(s,'A new custom edit.')],
  ['edit and revert',s=>{ const c = practiceCase(s),text = c.draft; editPractice(s,'Changed'); editPractice(s,text); }],
  ['source version',s=>{ practiceCase(s).sourceRevision = 'new-source'; }],
  ['deferral',s=>deferPractice(s,'deferred')],
  ['evidence request',s=>deferPractice(s,'evidence-review')],
]) test(`${label} invalidates an earlier confirmation preview`,()=>{
  const s = prepared('H1'), p = previewPractice(s); alter(s);
  const before = structuredClone(s);
  assert.equal(practicePreviewCurrent(s),false);
  assert.throws(()=>confirmPractice(s,p));
  assert.deepEqual(s,before);
});

test('forged replacement text is refused without changing anything',()=>{
  const s = prepared('H1'), p = structuredClone(previewPractice(s)); p.after = 'Injected wording';
  const before = structuredClone(s); assert.throws(()=>confirmPractice(s,p)); assert.deepEqual(s,before);
});
test('case switching preserves drafts and cannot use the other case preview',()=>{
  const s = prepared('H1'), p = previewPractice(s), first = structuredClone(s.cases.H1);
  selectPractice(s,'H2'); assert.throws(()=>confirmPractice(s,p));
  inspectPractice(s); editPractice(s,'My H2 draft');
  selectPractice(s,'H1'); assert.deepEqual(s.cases.H1,first);
  confirmPractice(s,p); assert.equal(s.cases.H2.draft,'My H2 draft');
});
for (const disposition of ['deferred','evidence-review','rejected']) {
  test(`${disposition} keeps draft and prior confirmations`,()=>{
    const s = prepared('H2'); confirmPractice(s,previewPractice(s));
    const confirmations = structuredClone(practiceCase(s).confirmations), text = practiceCase(s).draft;
    deferPractice(s,disposition);
    assert.equal(practiceCase(s).draft,text);
    assert.deepEqual(practiceCase(s).confirmations,confirmations);
    assert.equal(practiceCase(s).preview,null);
  });
}
test('selecting a supplied repair preserves the displaced custom draft',()=>{
  const s = prepared('H1'); editPractice(s,'A custom draft to retain'); usePracticeAlternative(s,'equivalent');
  assert.equal(practiceCase(s).history.at(-1).text,'A custom draft to retain');
});
test('practice persists separately and restores history and an exact preview',()=>{
  const storage = memory(), store = createPracticeStore(storage), s = prepared('H1');
  previewPractice(s); store.commit(s);
  assert.equal(storage.map.get(STORAGE_KEY),'untouched paper archive');
  assert.deepEqual([...storage.map.keys()].sort(),[REVIEW_KEY,STORAGE_KEY].sort());
  const restored = createPracticeStore(storage);
  assert.deepEqual(restored.state,s); assert.equal(practicePreviewCurrent(restored.state),true);
});
test('another tab cannot be overwritten; unsaved drafts remain exportable',()=>{
  const storage = memory(), store = createPracticeStore(storage), s = prepared('H1');
  storage.setItem(REVIEW_KEY,'another tab archive');
  editPractice(s,'Latest local draft'); store.commit(s);
  assert.match(store.warning,/another tab/);
  assert.equal(storage.getItem(REVIEW_KEY),'another tab archive');
  assert.equal(store.export().state.cases.H1.draft,'Latest local draft');
});
test('storage failure cannot report a recorded confirmation',()=>{
  const storage = memory(), store = createPracticeStore(storage), s = prepared('H1');
  previewPractice(s); store.commit(s);
  const next = structuredClone(s); confirmPractice(next,next.cases.H1.preview);
  storage.setItem = ()=>{ throw Error('quota full'); };
  assert.throws(()=>store.commit(next,true),/not recorded/);
  assert.equal(store.state.cases.H1.confirmations.length,0);
  assert.equal(JSON.parse(storage.map.get(REVIEW_KEY)).cases.H1.confirmations.length,0);
});
test('damaged archives are preserved, not reset or overwritten',()=>{
  const storage = memory(); storage.setItem(REVIEW_KEY,'{broken');
  const store = createPracticeStore(storage); assert.ok(store.warning);
  store.commit(prepared('H1'));
  assert.equal(storage.getItem(REVIEW_KEY),'{broken');
  assert.equal(store.export().preservedArchive,'{broken');
});
for (const [name,alter] of [
  ['unknown schema',s=>{ s.schema=99; }],
  ['unknown source',s=>{ s.fixtureCommit='unknown'; }],
  ['unknown case',s=>{ s.selected='H3'; }],
  ['missing case',s=>{ delete s.cases.H2; }],
  ['malformed preview',s=>{ s.cases.H1.preview={}; }],
  ['malformed confirmation',s=>{ s.cases.H1.confirmations.push({text:'fake'}); }],
  ['confirmed status without a record',s=>{ s.cases.H1.disposition='confirmed'; }],
]) test(`archive rejects ${name}`,()=>{ const s=createPractice(); alter(s); assert.throws(()=>parsePractice(JSON.stringify(s))); });

test('confirmed archive cannot silently replace its recorded wording',()=>{
  const s=prepared('H1'); confirmPractice(s,previewPractice(s));
  s.cases.H1.draft='Unrecorded replacement';
  assert.throws(()=>parsePractice(JSON.stringify(s)));
});

test('English review rules, unknown outcomes and stale controls are visible',()=>{
  const s = prepared('H1'), p = previewPractice(s);
  assert.deepEqual(reviewRules.map(r=>r[0]),['E1','E2','E3','E4','E5','E6','E7']);
  editPractice(s,'Custom text'); const html=renderPractice(s);
  assert.match(html,/Not assessed/); assert.match(html,/Preview expired/);
  assert.match(html,/data-review-action="confirm"[^>]*disabled/);
  assert.ok(html.includes(p.after));
  assert.doesNotMatch(html,/\p{Script=Han}/u);
  assert.match(html,/do not|not word bans/i);
});
test('author text is escaped in draft, preview and history',()=>{
  const s=prepared('H1'), attack='<img src=x onerror=alert(1)>';
  editPractice(s,attack); usePracticeAlternative(s,'equivalent');
  const p=previewPractice(s); p.before=attack; p.after=attack; practiceCase(s).draft=attack;
  const html=renderPractice(s);
  assert.ok(html.includes('&lt;img')); assert.ok(!html.includes(attack));
});
test('browser probe has no Node import or model/network execution path',()=>{
  for(const name of ['review-probe.mjs','review-practice.mjs','review-practice-view.mjs']) {
    const text=readFileSync(new URL(name,import.meta.url),'utf8');
    assert.doesNotMatch(text,/from ['"]node:|\bfetch\(|XMLHttpRequest|WebSocket|\beval\(/);
    assert.doesNotMatch(text,/\p{Script=Han}/u);
  }
});
