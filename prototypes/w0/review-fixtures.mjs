// Independently worded, synthetic adaptations of Humanizer 3.1.0 examples.
// Gold annotations are authored test data, not model output or source facts.
export const reviewSource = {
  repository: 'https://github.com/blader/humanizer',
  commit: '8c307f367c91bd974002f10f2be2965d642c13df',
  version: '3.1.0',
  skillSha256: '0612f1dfb1672b0ea9b97e139bf1f06cabe98d8b27424fe8ff01e1fb4cc99cad',
};

const area = (relation, anchor) => ({ id: 'area', kind: 'quantity', anchor,
  meaning: { subject: 'gallery', metric: 'floor-area', relation, value: 3000, unit: 'square-feet' } });
const replacement = anchor => ({ id: 'replacement', kind: 'relation', anchor,
  meaning: { subject: 'current-function', relation: 'replaces', object: 'previous-traversal' } });
const oldCost = anchor => ({ id: 'old-cost', kind: 'complexity', anchor,
  meaning: { subject: 'previous-traversal', operation: 'traversal', bound: 'O(n²)' } });
const newMechanism = { id: 'new-mechanism', kind: 'mechanism', anchor: 'hash map',
  meaning: { subject: 'current-function', implementation: 'hash-map' } };
const newCost = { id: 'new-cost', kind: 'complexity', anchor: 'O(1) lookups',
  meaning: { subject: 'current-function', operation: 'lookup', bound: 'O(1)' } };

export const semanticReviewCases = [
  {
    id: 'H1', sourceSection: '18. Avoiding is, are, and has',
    base: { revision: 'H1-base-v1', text: 'The gallery occupies more than 3,000 square feet.' },
    before: [area('gt', 'more than 3,000 square feet')],
    candidates: {
      unsafe: { text: 'The gallery occupies exactly 3,000 square feet.',
        atoms: [area('eq', 'exactly 3,000 square feet')] },
      equivalent: { text: 'The gallery has over 3,000 square feet of floor area.',
        atoms: [area('gt', 'over 3,000 square feet')] },
    },
  },
  {
    id: 'H2', sourceSection: '25. Writing about the document instead of its subject (first example)',
    base: { revision: 'H2-base-v1', text: 'The function was introduced to replace a previous O(n²) traversal.' },
    before: [replacement('replace a previous O(n²) traversal'), oldCost('previous O(n²) traversal')],
    candidates: {
      unsafe: { text: 'The function replaces a previous O(n²) traversal with a hash map providing O(1) lookups.',
        atoms: [replacement('replaces a previous O(n²) traversal'), oldCost('previous O(n²) traversal'), newMechanism, newCost] },
      equivalent: { text: 'The function replaces the previous traversal, which had O(n²) cost.',
        atoms: [replacement('replaces the previous traversal'), oldCost('previous traversal, which had O(n²) cost')] },
      mechanismOnly: { text: 'The function replaces a previous O(n²) traversal with a hash map.',
        atoms: [replacement('replaces a previous O(n²) traversal'), oldCost('previous O(n²) traversal'), newMechanism] },
      complexityOnly: { text: 'The function replaces a previous O(n²) traversal and provides O(1) lookups.',
        atoms: [replacement('replaces a previous O(n²) traversal'), oldCost('previous O(n²) traversal'), newCost] },
    },
  },
];

export function annotatedReview(id, variant) {
  const item = semanticReviewCases.find(entry => entry.id === id);
  if (!item) throw Error(`Unknown semantic review fixture: ${id}`);
  const selected = variant === 'unchanged' ? { text: item.base.text, atoms: item.before } : item.candidates[variant];
  if (!selected) throw Error(`Unknown review variant: ${variant}`);
  const base = structuredClone(item.base);
  const candidate = { revision: `${id}-${variant}-v1`, text: selected.text };
  return { base, candidate, assessment: {
    status: 'reviewed', base: structuredClone(base), candidate: structuredClone(candidate),
    before: structuredClone(item.before), after: structuredClone(selected.atoms),
  } };
}
