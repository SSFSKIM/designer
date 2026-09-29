/** UNAPPLIED interface proposal: code below is not imported by the runtime. */
export type BodyE3Gains = readonly [number, number, number];
export type BodyE3Neutral = readonly [number, number, number, number, number, number, number];

export interface BodyE3Fields {
  /** Identity gate in [0,1]; all shipped endpoints retain 0. */
  readonly bodyE3Strength: number;
  /** Encoded-luma gain ordinates at 63,93,118, held outside; each in [0,3]. */
  readonly bodyE3Gains: BodyE3Gains;
  /** Encoded neutral ordinates at 40,56,72,88,104,128,150; each in [0,255]. */
  readonly bodyE3Neutral: BodyE3Neutral;
}

// Add these three fields to MaterialProfile and optional counterparts to
// MaterialProfilePatch; merge tuples atomically through withMaterialOverrides.
export const PROPOSED_DEFAULTS: BodyE3Fields = {
  bodyE3Strength: 0,
  bodyE3Gains: [1, 1, 1],
  bodyE3Neutral: [40, 56, 72, 88, 104, 128, 150],
};

// Append ONE identity entry; do not modify earlier entries or digest rule 2.
export const PROPOSED_IDENTITY_GROUP = {
  wave: "W41",
  gate: { bodyE3Strength: 0 },
  gated: ["bodyE3Gains", "bodyE3Neutral"],
  law: "When enabled, replace the sampled untinted body with encoded E3 before author tint.",
  inertLawCase: "Proposed w41-body-e3 tests: gate zero never evaluates the replacement; " +
    "sweeping both tuples leaves CPU/drawn pixels and materialDigestInput unchanged.",
  whyGated: "At strength 0 neither tuple can reach the replacement branch's pixels.",
  claims: "c9a §5.192; W41 clause 11, parent partial-endpoint ruling",
};

// SAME field shapes on OpticsPassArgs. Append, never pack into old padding.
export const PROPOSED_UNIFORM_LAYOUT = {
  previousFloatCount: 140,
  floatCount: 152,
  bodyE3: [140, 141, 142, 143], // strength, three gains
  bodyE3Neutral0: [144, 145, 146, 147],
  bodyE3Neutral1: [148, 149, 150, 151], // seventh ordinate, then zero padding
};

// Scratch light-receded ONLY, once explicitly authorized; this is not a
// selected runtime document and must not be imported by a root or capture page.
export const PROPOSED_LIGHT_RECEDED: BodyE3Fields = {
  bodyE3Strength: 1,
  bodyE3Gains: [0.929205829365914, 0.9597570955316058, 0.9383102545096953],
  bodyE3Neutral: [150, 157, 164, 171, 178, 188, 197],
};
