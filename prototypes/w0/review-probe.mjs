// Disposable W0 contract probe. Not a semantic extractor or acceptance authority.
// The caller supplies independently reviewed atoms bound to exact text snapshots.
// A model's self-declared "reviewed" value is NOT sufficient in a real integration.
import { isDeepStrictEqual } from 'node:util';

const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const nonempty = value => typeof value === 'string' && value.trim().length > 0;
const snapshot = value => object(value) && nonempty(value.revision) && nonempty(value.text);
const kinds = new Set(['quantity', 'relation', 'mechanism', 'complexity']);
const scalar = value => nonempty(value) || (typeof value === 'number' && Number.isFinite(value)) || typeof value === 'boolean';

function validAtoms(atoms, text) {
  return Array.isArray(atoms) && atoms.length > 0
    && new Set(atoms.map(atom => atom?.id)).size === atoms.length
    && atoms.every(atom => object(atom) && nonempty(atom.id) && kinds.has(atom.kind)
      && nonempty(atom.anchor) && text.includes(atom.anchor)
      && object(atom.meaning) && Object.keys(atom.meaning).length > 0
      && Object.values(atom.meaning).every(scalar));
}

function result(status, route, reason, issues = []) {
  return { status, route, reason, issues, automaticWrite: false, requiresResearcherApproval: true };
}

export function probeExpressionReview(base, candidate, assessment) {
  if (!snapshot(base) || !snapshot(candidate) || !object(assessment)
    || assessment.status !== 'reviewed'
    || !snapshot(assessment.base) || !snapshot(assessment.candidate)) {
    return result('unassessed', 'review', 'A complete, independently reviewed annotation is required.');
  }
  if (!isDeepStrictEqual(base, assessment.base) || !isDeepStrictEqual(candidate, assessment.candidate)) {
    return result('stale', 'review', 'Text or revision changed after annotation; obtain a fresh review.');
  }
  if (!validAtoms(assessment.before, base.text) || !validAtoms(assessment.after, candidate.text)) {
    return result('unassessed', 'review', 'Missing, invalid, duplicate or unanchored semantic atoms.');
  }

  const before = new Map(assessment.before.map(atom => [atom.id, atom]));
  const after = new Map(assessment.after.map(atom => [atom.id, atom]));
  const issues = [];
  for (const [id, previous] of before) {
    const next = after.get(id);
    if (!next) {
      issues.push({ id, code: 'omitted-proposition', kind: previous.kind, anchor: previous.anchor });
    } else if (previous.kind !== next.kind || !isDeepStrictEqual(previous.meaning, next.meaning)) {
      const fields = [...new Set([...Object.keys(previous.meaning), ...Object.keys(next.meaning)])]
        .filter(key => !isDeepStrictEqual(previous.meaning[key], next.meaning[key]));
      if (previous.kind !== next.kind) fields.push('kind');
      issues.push({ id, code: 'changed-proposition', kind: next.kind, anchor: next.anchor, fields });
    }
  }
  for (const [id, atom] of after) {
    if (!before.has(id)) issues.push({ id, code: 'unsupported-addition', kind: atom.kind, anchor: atom.anchor });
  }
  if (issues.length) {
    return result('meaning-change', 'scientific-review', 'This is not a same-meaning expression edit.', issues);
  }
  if (base.text === candidate.text) {
    return result('no-change', 'researcher-review', 'No text or annotated proposition changed; keeping it is valid.');
  }
  return result('equivalent-under-annotations', 'researcher-review',
    'Supplied atoms agree; this does not prove that the annotations capture all meaning.');
}
