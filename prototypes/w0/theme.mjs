// UI preference only: no access to authoring state, approvals or Core settings.
export const THEME_KEY = 'rka-writer:w0:theme';
export const normalizeTheme = value => ['light', 'dark', 'system'].includes(value) ? value : 'system';
export const resolveTheme = (mode, prefersDark) => normalizeTheme(mode) === 'system'
  ? prefersDark ? 'dark' : 'light'
  : normalizeTheme(mode);

export function createThemeController({ root, storage, media, onStorageError = () => {} }) {
  let mode = 'system';
  try { mode = normalizeTheme(storage.getItem(THEME_KEY)); } catch { /* Work without persistence. */ }
  const apply = () => {
    const resolved = resolveTheme(mode, media.matches);
    root.classList.toggle('dark', resolved === 'dark');
    root.classList.toggle('light', resolved === 'light');
  };
  media.addEventListener('change', apply);
  apply();
  return {
    get mode() { return mode; },
    set(value) {
      mode = normalizeTheme(value);
      apply();
      try { storage.setItem(THEME_KEY, mode); } catch { onStorageError(); }
    },
  };
}
