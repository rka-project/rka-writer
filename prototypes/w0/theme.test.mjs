import test from 'node:test';
import assert from 'node:assert/strict';
import { THEME_KEY, normalizeTheme, resolveTheme, createThemeController } from './theme.mjs';
import { STORAGE_KEY } from './state.mjs';

function harness(initial = 'system', denied = false) {
  const values = new Map([[THEME_KEY, initial], [STORAGE_KEY, 'preserved author data']]);
  const writes = [];
  const classes = new Set();
  let mediaChange;
  let failures = 0;
  const media = { matches:false, addEventListener: (name, fn) => { assert.equal(name, 'change'); mediaChange = fn; } };
  const root = { classList: { toggle: (name, yes) => yes ? classes.add(name) : classes.delete(name) } };
  const storage = {
    getItem: key => { if (denied) throw Error('denied'); return values.get(key); },
    setItem: (key, value) => { if (denied) throw Error('denied'); writes.push(key); values.set(key, value); },
  };
  const controller = createThemeController({ root, storage, media, onStorageError: () => failures++ });
  return { controller, values, writes, classes, get failures() { return failures; },
    system: dark => { media.matches = dark; mediaChange(); } };
}

test('theme input is an allowlisted UI preference', () => {
  for (const input of [null, undefined, '', '<script>', 'DARK', {}, ['dark']]) assert.equal(normalizeTheme(input), 'system');
  assert.equal(resolveTheme('system', true), 'dark');
  assert.equal(resolveTheme('system', false), 'light');
  assert.equal(resolveTheme('light', true), 'light');
  assert.equal(resolveTheme('dark', false), 'dark');
});
test('initialization and OS theme changes do not write storage', () => {
  const h = harness();
  assert.deepEqual([...h.classes], ['light']);
  h.system(true);
  assert.deepEqual([...h.classes], ['dark']);
  assert.deepEqual(h.writes, []);
});
test('explicit theme persists separately and ignores OS changes', () => {
  const h = harness();
  h.controller.set('dark');
  h.system(false);
  assert.deepEqual([...h.classes], ['dark']);
  assert.deepEqual(h.writes, [THEME_KEY]);
  assert.equal(h.values.get(STORAGE_KEY), 'preserved author data');
  assert.equal(h.values.get(THEME_KEY), 'dark');
});
test('saved choice survives controller recreation; system mode follows OS again', () => {
  const h = harness('dark');
  assert.equal(h.controller.mode, 'dark');
  assert.deepEqual([...h.classes], ['dark']);
  h.controller.set('system');
  assert.deepEqual([...h.classes], ['light']);
  h.system(true);
  assert.deepEqual([...h.classes], ['dark']);
});
test('unavailable theme storage does not prevent rendering or theme changes', () => {
  const h = harness(undefined, true);
  assert.equal(h.controller.mode, 'system');
  h.controller.set('dark');
  assert.deepEqual([...h.classes], ['dark']);
  assert.equal(h.failures, 1);
  assert.equal(h.values.get(STORAGE_KEY), 'preserved author data');
});
