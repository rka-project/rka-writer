// All author-supplied content passes through this encoder before innerHTML.
export const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]));
// Labels/attributes are authored markup or explicitly encoded at the call site.
export const button = (label, action, attrs = '') => `<button type="button" data-action="${action}" ${attrs}>${label}</button>`;
