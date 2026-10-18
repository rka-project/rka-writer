// Explicit, bounded upgrade of the supplied demo. Never translate author data.
import { fixture } from './fixture.mjs';
import { createState, migratePrevious } from './state.mjs';

export const LEGACY_FIXTURE_ID = 'synthetic-device-meaning-w0-v1';
const presetPurposes = new Map([
  ['从具体场景出发，让读者区分指令可用性与动作的物理含义，再引出表示问题。',
    createState().plan.purpose],
  ['用选定迁移案例说明标签未编码的物理前提，再引出前提的表示问题。',
    'Use the selected relocation case to explain a physical precondition absent from the label, then motivate its representation.'],
]);

export function migrateLegacy(raw) {
  const legacy = JSON.parse(raw);
  if (legacy?.fixtureId !== LEGACY_FIXTURE_ID) throw Error('Unknown previous demo version. Its archive is preserved.');
  // Validate every field using the current compatible shape, on a new object.
  const next = migratePrevious(JSON.stringify({ ...legacy, fixtureId: fixture.id }));
  next.languageUpgrade = { fromFixture: LEGACY_FIXTURE_ID, originalPresetPurpose: null };
  if (presetPurposes.has(next.plan.purpose)) {
    next.languageUpgrade.originalPresetPurpose = next.plan.purpose;
    next.plan.purpose = presetPurposes.get(next.plan.purpose);
  }
  // Existing approval bundles/tokens, documents, drafts, notes, custom purpose,
  // events, and mapping previews stay byte-for-byte unchanged. Old tokens cannot
  // approve this translated fixture; the author must review the new plan.
  return next;
}
