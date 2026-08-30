/**
 * One cell, measured: the shared core behind both `diff` (one pair, from the
 * command line) and `compare` (the whole matrix, in one process).
 *
 * It lives apart from either CLI because the full-matrix run needs to measure
 * thirty cells, and paying a `tsx` process start plus a re-parse of the metric
 * module thirty times made a full re-measure slow enough to discourage running
 * one — which is the wrong incentive for the only thing that tells you whether a
 * tuning change helped. One import, thirty calls, one matrix write.
 *
 * The two design rules `diff` was built on hold here unchanged:
 *
 * **The background is a first-class input, not an optional extra.** Every
 * material metric is a comparison against the backdrop the material sampled, and
 * the silhouette of an opaque native composite can only be found by differencing
 * against that same backdrop. Without one, this reports the shape and perceptual
 * axes and says so; it does not guess a material number.
 *
 * **The declaration bounds the search, and the shadow is its own axis** (schema
 * 5, wave Decision Log 15). Differencing against the backdrop finds the
 * component *and anything else that differs from it* — which on the active-pose
 * bed is the reference's outer shadow. So extraction is bounded to the geometry
 * `scenes.json` declares, and what happens outside that geometry is measured
 * separately rather than swallowed.
 *
 * **No thresholds and no verdict.** Nothing here decides whether a number is
 * good. What counts as close enough is per tier and per engine cell, decided
 * against holdout fixtures, and it is C9's — see docs/doperpowers/specs/
 * c9a-fidelity-claims.md.
 */

import { readFileSync } from "node:fs";

import {
  blurEdgeSpread,
  componentRegion,
  contourDistance,
  coherenceAxisReport,
  cornerCurvature,
  decodePng,
  edgeWeightedDifference,
  extractSilhouette,
  silhouetteHoleCount,
  interiorLevel,
  luminanceTransfer,
  materialAxisReport,
  oklabDeltaE,
  perceptualAxisReport,
  resultCellKey,
  rimIntensity,
  shadowAxisReport,
  shadowFalloff,
  shadowField,
  shapeAxisReport,
  silhouetteArea,
  silhouetteIoU,
  singleEdgeRegion,
  ssim,
  tintResponse,
  type CalibrationImage,
  type CanvasSize,
  type CellResult,
  type CoherenceAxisReport,
  type DeclaredComponent,
  type EdgeSpreadReport,
  type FidelityTier,
  type FixtureSet,
  type LuminanceTransferReport,
  type MaterialAxisReport,
  type PerceptualAxisReport,
  type ShadowAxisReport,
  type ShapeAxisReport,
  type WebCell,
} from "../src/index";

export interface MeasureInput {
  readonly nativePath: string;
  readonly webPath: string;
  readonly backgroundPath?: string;
  readonly profileKey: string;
  readonly sceneId: string;
  readonly webCellPath: string;
  /**
   * The **texture** tier's capture of this same profile and scene, when one is on
   * disk — the other half of the coherence pair (schema 4).
   *
   * Only meaningful on a `dom` measurement, and optional there: a scene captured
   * on one tier alone is not a coherence data point. Absent means the axis is
   * absent, never that the tiers agreed.
   */
  readonly textureTwinPath?: string;
  readonly tier: FidelityTier;
  readonly fixtureSet: FixtureSet;
  readonly blurAxis: "x" | "y";
  readonly blurRegion?: readonly [number, number, number, number];
  /**
   * Linear-light luminance delta that counts as "the component is here", used to
   * cut the silhouette out of an opaque composite. Exposed because the right
   * value depends on the background's own contrast: a glass body over a flat
   * light-solid backdrop differs from it far less than over a checkerboard.
   */
  readonly silhouetteThreshold: number;
  /**
   * The scene matrix's declaration of where the component is (schema 5).
   *
   * Not optional, and not derivable from the capture. It bounds the shape axis's
   * search — the rule that "anything differing from the background is the
   * surface" is false for a material that casts a shadow — and it is the contour
   * the shadow axis profiles outward from. See `src/component-region.ts`.
   */
  readonly component: DeclaredComponent;
  /** The canvas the component is centred in, in points. */
  readonly canvas: CanvasSize;
  /** Device pixels per point: the profile's backing scale. */
  readonly scale: number;
  /** Outward dilation of the declared region, device px. Defaults to zero. */
  readonly componentRegionMarginPx?: number;
}

export interface MeasureOutcome {
  readonly cell: CellResult;
  /** Everything the run legitimately could not measure, and why. Never empty by accident. */
  readonly notes: readonly string[];
}

export const DEFAULT_SILHOUETTE_THRESHOLD = 0.02;

function loadImage(path: string): CalibrationImage {
  return decodePng(readFileSync(path));
}

/**
 * Read the web cell descriptor the capture script wrote.
 *
 * Required, with no default, and that is the point. `WebCell.renderer` is a
 * closed `"webgpu" | "css"` — there is no honest "unknown" for which tier drew,
 * because the whole purpose of the web axis is that a fidelity claim names the
 * cell it was measured in. A cell defaulted to the common case would make every
 * row in the matrix a guess. So the capture script, which is the only thing that
 * actually knows, has to say.
 */
export function loadWebCell(path: string): WebCell {
  const raw: unknown = JSON.parse(readFileSync(path, "utf8"));
  if (typeof raw !== "object" || raw === null) {
    throw new Error(`--web-cell '${path}' is not a JSON object`);
  }
  const cell = raw as Partial<WebCell>;
  const missing = (
    ["engine", "engineVersion", "renderer", "samplingBackend", "gpuAdapter", "colorSpace", "capturePath"] as const
  ).filter((field) => cell[field] === undefined);
  if (missing.length > 0) {
    throw new Error(`--web-cell '${path}' is missing: ${missing.join(", ")}`);
  }
  if (cell.renderer !== "webgpu" && cell.renderer !== "css") {
    throw new Error(`--web-cell renderer must be 'webgpu' or 'css', got '${String(cell.renderer)}'`);
  }
  if (cell.colorSpace !== "srgb") {
    throw new Error(`--web-cell colorSpace must be 'srgb' (X5 locks v1), got '${String(cell.colorSpace)}'`);
  }
  return cell as WebCell;
}

export function measureCell(input: MeasureInput): MeasureOutcome {
  const native = loadImage(input.nativePath);
  const web = loadImage(input.webPath);
  const background = input.backgroundPath === undefined ? undefined : loadImage(input.backgroundPath);

  /*
   * The declared search region (schema 5).
   *
   * Built from the scene matrix and the profile's backing scale, never from the
   * pixels: an image-derived bound would be the same circularity in a longer
   * form, since the shadow that broke the old rule is in the very pixels the
   * bound would be fitted to. Building it here also checks the capture against
   * the declaration — a capture that is not `canvas × scale` was framed
   * differently from the scene whose geometry this is.
   */
  const region = componentRegion(input.component, {
    canvas: input.canvas,
    scale: input.scale,
    width: native.width,
    height: native.height,
    ...(input.componentRegionMarginPx === undefined
      ? {}
      : { marginPx: input.componentRegionMarginPx }),
  });

  // Silhouettes. With a background we can difference against it, which is the
  // only way to find the component in an opaque native composite; without one we
  // fall back to alpha, which only works for a capture taken over transparency.
  // Either way the search is bounded to the declared region.
  const extractor = background
    ? ({
        kind: "luminance-delta",
        background,
        threshold: input.silhouetteThreshold,
        region: region.silhouette,
      } as const)
    : ({ kind: "alpha", threshold: 0.5, region: region.silhouette } as const);

  const nativeSil = extractSilhouette(native, extractor);
  const webSil = extractSilhouette(web, extractor);
  const nativeArea = silhouetteArea(nativeSil);
  const webArea = silhouetteArea(webSil);

  // An empty silhouette is a real, informative outcome, not an error: it means
  // that side's capture contains nothing distinguishable from its background.
  // The axis is reported as ABSENT with the reason, rather than crashing the run
  // or — worse — inventing an IoU of 0 that would read like a measured mismatch.
  // The other axes still measure what they legitimately can.
  const notes: string[] = [];
  let shape: ShapeAxisReport | undefined;
  if (nativeArea === 0 || webArea === 0) {
    const empty = [nativeArea === 0 ? "native" : undefined, webArea === 0 ? "web" : undefined]
      .filter((s): s is string => s !== undefined)
      .join(" and ");
    notes.push(
      `shape axis NOT MEASURED: the ${empty} silhouette is empty at threshold ` +
        `${String(input.silhouetteThreshold)} inside the declared component region — that capture is ` +
        `indistinguishable from its background there, so there is no contour to compare.`,
    );
  } else {
    shape = shapeAxisReport({
      silhouetteAreaNative: nativeArea,
      silhouetteAreaWeb: webArea,
      componentRegionArea: region.areaPx,
      componentRegionMarginPx: region.marginPx,
      silhouetteHolesNative: silhouetteHoleCount(nativeSil, region.silhouette),
      silhouetteHolesWeb: silhouetteHoleCount(webSil, region.silhouette),
      silhouetteIoU: silhouetteIoU(nativeSil, webSil),
      contourDistance: contourDistance(nativeSil, webSil),
      cornerCurvature: cornerCurvature(nativeSil, webSil),
    });
  }

  const perceptual: PerceptualAxisReport = perceptualAxisReport({
    edgeWeighted: edgeWeightedDifference(native, web),
    ssim: ssim(native, web),
    oklabDeltaE: oklabDeltaE(native, web),
  });

  let material: MaterialAxisReport | undefined;
  if (background !== undefined && nativeArea > 0 && webArea > 0) {
    /*
     * One mask for both sides, and it is the NATIVE silhouette.
     *
     * This is the difference between a target and a moving target. Every
     * material sub-metric is a statistic over a masked region, so the mask is
     * part of the measurement — and a web-derived mask shifts as the web side is
     * tuned, which moves the native figure it is being compared against. Tuning
     * against a target that moves when you tune is not tuning. The reference's
     * own footprint is also the honest frame: the question is what vitrea does
     * where Apple's material is, not where vitrea's happens to be.
     *
     * The shape axis above deliberately still compares the two silhouettes
     * against each other — that is its whole job, and it is the axis that would
     * be made vacuous by sharing a mask.
     *
     * From schema 5 that native silhouette is bounded to the declared region,
     * which is what makes these statistics interior statistics again. Under the
     * whole-canvas rule the mask contained the reference's shadow as well as its
     * component, so `interiorMean*`, `interiorStdDev*` and the rim — the whole
     * of this package's declared tuning objective — were averaged over a region
     * roughly half shadowed backdrop (claims §5.11).
     */
    const interior = nativeSil;

    // Derived from the BACKDROP's own step structure, so both sides are measured
    // over the identical window and neither can be handed an easier one.
    const region =
      input.blurRegion === undefined
        ? singleEdgeRegion(background, interior, input.blurAxis)
        : {
            x: input.blurRegion[0],
            y: input.blurRegion[1],
            width: input.blurRegion[2],
            height: input.blurRegion[3],
          };
    if (region === undefined) {
      notes.push(
        `blur NOT MEASURED: the backdrop has no single resolvable step edge inside the ` +
          `silhouette on the ${input.blurAxis} axis, so no edge-spread width is identifiable. ` +
          `Absent, not zero — read interiorStdDev{Native,Web} for the frosting comparison.`,
      );
    }
    const edgeSpread = (image: CalibrationImage, side: string): EdgeSpreadReport | undefined => {
      if (region === undefined) return undefined;
      try {
        return blurEdgeSpread(image, { axis: input.blurAxis, region });
      } catch (error) {
        // A refused fit is information, not a crash: it says this backdrop cannot
        // identify a blur width here, which is a fact about the fixture set.
        notes.push(
          `blur NOT MEASURED on the ${side} side: ` +
            `${error instanceof Error ? error.message : String(error)}`,
        );
        return undefined;
      }
    };

    // Absent on a solid-colour backdrop: no slope exists to fit, and reporting
    // one would be arithmetic on no information (see stats.tryLinearFit).
    let luminance: LuminanceTransferReport | undefined;
    try {
      luminance = luminanceTransfer(native, web, background, { interior });
    } catch (error) {
      notes.push(
        `luminance transfer NOT MEASURED: ${error instanceof Error ? error.message : String(error)}`,
      );
    }

    const nativeBlur = edgeSpread(native, "native");
    const webBlur = edgeSpread(web, "web");
    material = materialAxisReport({
      native: {
        ...(nativeBlur === undefined ? {} : { blur: nativeBlur }),
        interior: interiorLevel(native, { interior }),
        tint: tintResponse(native, background, { interior }),
        rim: rimIntensity(native, interior),
        shadow: shadowFalloff(native, interior, background),
      },
      web: {
        ...(webBlur === undefined ? {} : { blur: webBlur }),
        interior: interiorLevel(web, { interior }),
        tint: tintResponse(web, background, { interior }),
        rim: rimIntensity(web, interior),
        shadow: shadowFalloff(web, interior, background),
      },
      backdropInterior: interiorLevel(background, { interior }),
      ...(luminance === undefined ? {} : { luminance }),
    });
  } else {
    notes.push(
      background === undefined
        ? "material axis NOT MEASURED: no background given (absent, not zero)."
        : `material axis NOT MEASURED: the ${nativeArea === 0 ? "native" : "web"} silhouette is empty at ` +
          `threshold ${String(input.silhouetteThreshold)}, so there is no shared interior to sample. ` +
          `A material within that threshold of its own backdrop is a real outcome — over a solid ` +
          `backdrop of its own tone the reference is very nearly invisible — not a capture fault.`,
    );
  }

  /*
   * The shadow axis (schema 5): what each side does to the backdrop it does not
   * cover, measured OUTSIDE the declared region.
   *
   * Needs a backdrop and nothing else — in particular it does not need either
   * silhouette, which is the point. It is measured on cells whose shape and
   * material axes are absent (a material invisible against its own backdrop
   * still casts a shadow), and its own absences are its own: over `dark-solid`
   * and `impulse` there is no light behind the component to remove, so the
   * normalised figures are absent with the support recorded, never zeroed.
   */
  let shadow: ShadowAxisReport | undefined;
  if (background !== undefined) {
    const nativeShadow = shadowField(native, background, region);
    const webShadow = shadowField(web, background, region);
    shadow = shadowAxisReport({ native: nativeShadow, web: webShadow });
    if (nativeShadow.unmeasurableReason !== undefined) {
      notes.push(
        `shadow axis NOT NORMALISED: ${nativeShadow.unmeasurableReason} The absolute departure ` +
          `(meanDeparture{Native,Web}) is still reported; every ratio-valued field is absent, not zero.`,
      );
    }
  } else {
    notes.push("shadow axis NOT MEASURED: no background given (absent, not zero).");
  }

  /*
   * The coherence axis: this capture against its texture twin, web against web,
   * with no fixture in the comparison at all (schema 4, `CoherenceAxisReport`).
   *
   * Computed here rather than in a second pass over the written matrix, because
   * both quantities need pixels — and the pixels, the native silhouette that
   * masks the interiors, and the very cell this belongs to are all already in
   * hand at this point. A pass that re-derived them from a matrix would be
   * re-decoding four PNGs to recover a mask this function just built.
   *
   * Dom-tier only. The pair has one number, so it is stored on one side of it,
   * and the CSS tier is the side that moves.
   */
  let coherence: CoherenceAxisReport | undefined;
  if (input.tier === "dom" && input.textureTwinPath !== undefined) {
    const twin = loadImage(input.textureTwinPath);
    coherence = coherenceAxisReport({
      // Whole-canvas, exactly as `cli/tier-delta.ts` reports it: the dom tier's
      // shadow is part of what a viewer sees on a demotion, so it is not masked
      // out of the comparison the demotion is judged by.
      crossTierOklabDeltaEMean: oklabDeltaE(twin, web).mean,
      // Absent — not zero, and not one — where no interior exists to sample.
      // `material` is present on exactly the cells that have a shared mask, so
      // its presence is the condition rather than a second empty-silhouette test.
      ...(material === undefined
        ? {}
        : {
            interiorLevelRatioGpuOverCss:
              interiorLevel(twin, { interior: nativeSil }).mean / material.interiorMeanWeb.value,
          }),
    });
  }

  const cell: CellResult = {
    key: resultCellKey(input.profileKey, loadWebCell(input.webCellPath), input.sceneId),
    fixtureSet: input.fixtureSet,
    tier: input.tier,
    capturedAt: new Date().toISOString(),
    perceptual,
    // Absent axes mean "not measured", which is what the schema's optional axes
    // are for — never "measured as zero". No motion axis: this is a still pair.
    ...(shape === undefined ? {} : { shape }),
    ...(material === undefined ? {} : { material }),
    ...(shadow === undefined ? {} : { shadow }),
    ...(coherence === undefined ? {} : { coherence }),
  };

  return { cell, notes };
}
