import test from 'node:test';
import assert from 'node:assert/strict';
import { probeExpressionReview } from './review-probe.mjs';
import { annotatedReview, semanticReviewCases, reviewSource } from './review-fixtures.mjs';

const probe = data => probeExpressionReview(data.base, data.candidate, data.assessment);

test('source is pinned; examples are two independent semantic failures', () => {
  assert.deepEqual(semanticReviewCases.map(item => item.id), ['H1', 'H2']);
  assert.match(reviewSource.commit, /^[a-f0-9]{40}$/);
  assert.match(reviewSource.skillSha256, /^[a-f0-9]{64}$/);
  assert.equal(reviewSource.version, '3.1.0');
});

test('H1: identical digits do not hide lower-bound to exact-value drift', () => {
  const data = annotatedReview('H1', 'unsafe');
  assert.deepEqual(data.base.text.match(/\d+/g), data.candidate.text.match(/\d+/g));
  const review = probe(data);
  assert.equal(review.status, 'meaning-change');
  assert.equal(review.route, 'scientific-review');
  assert.deepEqual(review.issues, [{ id: 'area', code: 'changed-proposition', kind: 'quantity',
    anchor: 'exactly 3,000 square feet', fields: ['relation'] }]);
});

test('H2: invented mechanism and complexity are separate unsupported additions', () => {
  const review = probe(annotatedReview('H2', 'unsafe'));
  assert.equal(review.status, 'meaning-change');
  assert.equal(review.route, 'scientific-review');
  assert.deepEqual(review.issues.map(issue => [issue.id, issue.code]), [
    ['new-mechanism', 'unsupported-addition'], ['new-cost', 'unsupported-addition'],
  ]);
});

for (const [variant, id] of [['mechanismOnly', 'new-mechanism'], ['complexityOnly', 'new-cost']]) {
  test(`H2: removing the other invention does not excuse ${variant}`, () => {
    const review = probe(annotatedReview('H2', variant));
    assert.equal(review.status, 'meaning-change');
    assert.deepEqual(review.issues.map(issue => issue.id), [id]);
  });
}

for (const id of ['H1', 'H2']) {
  test(`${id}: equivalent wording remains a proposal, not accepted text`, () => {
    const review = probe(annotatedReview(id, 'equivalent'));
    assert.equal(review.status, 'equivalent-under-annotations');
    assert.equal(review.route, 'researcher-review');
    assert.deepEqual(review.issues, []);
    assert.equal(review.automaticWrite, false);
    assert.equal(review.requiresResearcherApproval, true);
  });
  test(`${id}: unchanged prose may remain unchanged`, () => {
    assert.equal(probe(annotatedReview(id, 'unchanged')).status, 'no-change');
  });
  test(`${id}: all outcomes leave the supplied text and annotations intact`, () => {
    for (const variant of ['unsafe', 'equivalent', 'unchanged']) {
      const data = annotatedReview(id, variant), original = structuredClone(data);
      const review = probe(data);
      assert.deepEqual(data, original);
      assert.deepEqual(probe(data), review);
      assert.equal(review.automaticWrite, false);
      assert.equal(review.requiresResearcherApproval, true);
    }
  });
}

test('same numerical value with a changed unit is a semantic change too', () => {
  const data = annotatedReview('H1', 'equivalent');
  data.candidate.text = 'The gallery has over 3,000 square metres of floor area.';
  data.assessment.candidate = structuredClone(data.candidate);
  data.assessment.after[0].anchor = 'over 3,000 square metres';
  data.assessment.after[0].meaning.unit = 'square-metres';
  assert.deepEqual(probe(data).issues[0].fields, ['unit']);
});

test('dropping an established complexity statement is not automatically harmless', () => {
  const data = annotatedReview('H2', 'equivalent');
  data.candidate.text = 'The function replaces the previous traversal.';
  data.assessment.candidate = structuredClone(data.candidate);
  data.assessment.after = data.assessment.after.filter(atom => atom.id !== 'old-cost');
  const review = probe(data);
  assert.equal(review.status, 'meaning-change');
  assert.deepEqual(review.issues.map(issue => issue.code), ['omitted-proposition']);
});

for (const [label, alter] of [
  ['missing assessment', data => { data.assessment = null; }],
  ['unknown assessment', data => { data.assessment.status = 'unassessed'; }],
  ['absent atoms', data => { delete data.assessment.after; }],
  ['empty atoms', data => { data.assessment.after = []; }],
  ['duplicate atom', data => { data.assessment.after.push(structuredClone(data.assessment.after[0])); }],
  ['unanchored atom', data => { data.assessment.after[0].anchor = 'not in the candidate'; }],
  ['missing meaning', data => { delete data.assessment.after[0].meaning; }],
  ['empty meaning', data => { data.assessment.after[0].meaning = {}; }],
  ['invalid quantity', data => { data.assessment.after[0].meaning.value = NaN; }],
]) {
  test(`${label} cannot silently pass`, () => {
    const data = annotatedReview('H1', 'equivalent'); alter(data);
    const review = probe(data);
    assert.equal(review.status, 'unassessed');
    assert.equal(review.automaticWrite, false);
  });
}

for (const [label, alter] of [
  ['base revision', data => { data.base.revision = 'newer'; }],
  ['base text', data => { data.base.text += ' An author addition.'; }],
  ['candidate revision', data => { data.candidate.revision = 'newer'; }],
  ['candidate text', data => { data.candidate.text = 'The gallery has exactly 3,000 square feet.'; }],
]) {
  test(`changed ${label} invalidates an earlier annotation`, () => {
    const data = annotatedReview('H1', 'equivalent'); alter(data);
    assert.equal(probe(data).status, 'stale');
  });
}

test('atom ordering and object field order are not semantic differences', () => {
  const data = annotatedReview('H2', 'equivalent');
  data.assessment.after.reverse();
  data.assessment.after[0].meaning = Object.fromEntries(Object.entries(data.assessment.after[0].meaning).reverse());
  assert.equal(probe(data).status, 'equivalent-under-annotations');
});

test('explicit limit: the probe cannot discover omissions in supplied annotations', () => {
  const data = annotatedReview('H1', 'unsafe');
  // A bad reviewer can mislabel equality as a lower bound. This probe does not
  // parse text and cannot detect the lie; real reviewer evaluation is separate.
  data.assessment.after[0].meaning.relation = 'gt';
  const review = probe(data);
  assert.equal(review.status, 'equivalent-under-annotations');
  assert.equal(review.automaticWrite, false);
  assert.equal(review.requiresResearcherApproval, true);
});
