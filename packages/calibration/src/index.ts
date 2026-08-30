/**
 * @vitrea/calibration — the fidelity ground truth (C7).
 *
 * X9 authority lives in the parent spec; this package owns the content. C1
 * fixed the profile-key grammar and the metric axes so C7's fixtures and C9's
 * fidelity claims cite the same thing; C7 fills in the measurements.
 *
 * ## What is here
 *
 * - `profile` — X9's native side: profile-key grammar, axes, fixture split, tiers.
 * - `image` / `color` / `silhouette` / `stats` — the substrate every metric
 *   shares: one capture representation, the sRGB↔linear boundary under X5,
 *   silhouette extraction with an exact distance transform, and the order
 *   statistics and fits the metrics report through.
 * - `component-region` — the scene matrix's declared geometry, placed and
 *   rasterised: the search region that bounds extraction and the exact contour
 *   distance the shadow axis profiles by.
 * - `metrics/shape`, `metrics/material`, `metrics/perceptual`, `metrics/motion`,
 *   `metrics/shadow` — the axes, reported separately so a win on one can never
 *   mask a loss on another.
 * - `report` — X9's result side: the per-cell key (native profile × web cell ×
 *   scene), the per-axis reports, and the result matrix.
 *
 * ## Two rules that shape all of it
 *
 * **No thresholds, anywhere.** Every metric returns numbers with declared
 * units and no verdict. What counts as close enough is per tier and per engine
 * cell, it is decided against holdout fixtures, and it is C9's. A threshold
 * living next to the metric that produced it would be tuning against the
 * calibration set, which is precisely what the three-way fixture split exists
 * to prevent.
 *
 * **Pure functions over decoded pixels.** `decodePng` is the only concession to
 * the outside world, and it takes a buffer rather than a path. Reading files,
 * driving harnesses and choosing scenes belong to the CLI above this library.
 */

export * from "./profile";

export * from "./errors";
export * from "./color";
export * from "./stats";
export * from "./image";
export * from "./silhouette";
export * from "./component-region";
export * from "./plurality";

export * from "./metrics/shape";
export * from "./metrics/material";
export * from "./metrics/shadow";
export * from "./metrics/perceptual";
export * from "./metrics/motion";

export * from "./report";
