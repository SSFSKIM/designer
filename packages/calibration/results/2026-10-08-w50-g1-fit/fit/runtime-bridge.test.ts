import assert from 'node:assert/strict';
import { test } from 'node:test';
import { assertHeldResolved } from './runtime-bridge.ts';

const baseline = {
  lowEndStrength: 0, lowEnd44: [0, 0, 0, 0], lowEnd96: [0, 0, 0, 0], lowEnd160: [0, 0, 0, 0],
  tintAlpha: .8, backdropToneAbscissa: { kind: 'silhouette', insetPx: 4 },
  sizeScatterFloor2x: 1, sizeHeavySecondShare: .25,
};
const evaluated = () => ({ ...structuredClone(baseline), lowEndStrength: 1,
  lowEnd44: [.1, .2, .3, .4], lowEnd96: [.2, .3, .4, .5], lowEnd160: [.3, .4, .5, .6] });

test('only the admitted chart may differ when reusing captured tone arguments', () => {
  assert.doesNotThrow(() => assertHeldResolved(baseline, evaluated()));
  for (const next of [
    { ...evaluated(), tintAlpha: .7 },
    { ...evaluated(), backdropToneAbscissa: { kind: 'source', insetPx: 4 } },
    { ...evaluated(), sizeScatterFloor2x: .6 },
    { ...evaluated(), sizeHeavySecondShare: .5 },
    { ...evaluated(), previouslyUnknownSamplingLeaf: 1 },
  ]) assert.throws(() => assertHeldResolved(baseline, next), /held/);
});

test('gate0 must be inert and evaluation rows must remain within the declared family', () => {
  assert.throws(() => assertHeldResolved({ ...baseline, lowEndStrength: 1 }, evaluated()), /gate0/);
  // The global norm's reference is the actual current chart, not arbitrary dormant rows.
  assert.throws(() => assertHeldResolved({ ...baseline, lowEnd44: [.1, .1, .1, .1] }, evaluated()), /gate0/);
  for (const next of [
    { ...evaluated(), lowEndStrength: 0 },
    { ...evaluated(), lowEnd44: [.2, .1, .3, .4] },
    { ...evaluated(), lowEnd96: [0, .1, NaN, .4] },
    { ...evaluated(), lowEnd160: [0, .1, .2, 1.1] },
  ]) assert.throws(() => assertHeldResolved(baseline, next), /chart/);
});
