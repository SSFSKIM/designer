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
  silhouetteBodyCount,
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
  ssimDepthWindows,
  ssimFromMap,
  ssimMap,
  SSIM_BAND_SPLIT_CSS_PX,
  tintResponse,
  type CalibrationImage,
  type CanvasSize,
  type CellResult,
  type CoherenceAxisReport,
  type DeclaredConformanceInput,
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
   * OKLab a/b distance that counts as "the component is here" where the
   * luminance delta does not (W11b) — the arm that finds an opaque tint
   * sitting at its backdrop's own level. See `LuminanceDeltaExtractor`.
   */
  readonly silhouetteChromaThreshold: number;
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
  /**
   * The declaration-conformance capture of this same cell, when one is on disk
   * (`capture-web --alpha`, W20 G0): the web side rendered over a transparent
   * page with the backdrop raster hidden, so the tier's coverage is its own
   * alpha.
   *
   * Absent means the reading is absent, never that the tier conformed. See
   * `DRAWN_ALPHA_THRESHOLD` for the one condition under which it is read.
   */
  readonly drawnAlphaPath?: string;
}

export interface MeasureOutcome {
  readonly cell: CellResult;
  /** Everything the run legitimately could not measure, and why. Never empty by accident. */
  readonly notes: readonly string[];
}

export const DEFAULT_SILHOUETTE_THRESHOLD = 0.02;
/**
 * The alpha a pixel of the declaration-conformance capture must carry to count
 * as covered, and the interior level a tier must reach for the rule to apply at
 * all (W20 G0, claims §5.83).
 *
 * Half is the same rule `silhouette.ts`'s alpha extractor already states, and on
 * a tier that composites an opaque layer it is the middle of a step: measured on
 * `apple-macos-26.5-1x-light-standard`, the GPU tier's interior alpha is exactly
 * 1.0000 over the whole body, its outer shadow reaches 0.106 at four device
 * pixels outside the contour and 0.53 nowhere but the antialiased boundary band
 * itself, and the extracted area comes back at 5104 px against the 5104 the
 * clamped contour encloses analytically. The rule recovers the drawn shape to
 * the pixel.
 *
 * `MIN_INTERIOR_ALPHA` is the conditioning half, and it exists because the CSS
 * tier fails it. That tier composites its material as one `rgba()` layer, which
 * over a transparent page is a flat interior alpha of 0.267 — below the
 * threshold — while its rim border reads 0.526 and its outer shadow reaches
 * 0.126 three pixels out. No fixed threshold separates coverage from shadow
 * there: half the tier's own interior level admits 364 px of shadow and rim on
 * `photo__capsule-button__rest`, which would read as a surface 1.25 px larger
 * than declared on a tier whose shape is the DOM's and is right by
 * construction. So the reading is REFUSED with the measured interior level
 * rather than reported as a conformance failure that is the instrument's.
 */
export const DRAWN_ALPHA_THRESHOLD = 0.5;
export const MIN_INTERIOR_ALPHA = 0.9;
/** How deep inside the declared contour the interior level is read, in CSS px. */
export const INTERIOR_ALPHA_DEPTH_CSS_PX = 4;
/**
 * The chroma arm's threshold on OKLab a/b distance (W11b, claims §5.40).
 * Declared at 0.03 before the bed-wide run: the hole pixels it exists for sit
 * at ≥ 0.12, the masks' own first percentile at 0.11, and every cell measured
 * gives the same mask at 0.02, 0.03 and 0.05.
 */
export const DEFAULT_SILHOUETTE_CHROMA_THRESHOLD = 0.03;

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
        chromaThreshold: input.silhouetteChromaThreshold,
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

  /*
   * The declaration-conformance reading (W20 G0, claims §5.83).
   *
   * Computed before the shape axis is assembled because it is one of its rows,
   * and it is the only row that is NOT a comparison between the two sides: it
   * asks whether the web tier covered the geometry the scene declares, using
   * that tier's own alpha over a transparent page and no bound at all. Without
   * it the axis is blind in one direction by construction — a surface drawn
   * larger than its declaration fills the declared region and reads perfect —
   * and that is the direction the GPU tier's clamped capsule took.
   */
  let conformance: DeclaredConformanceInput | undefined;
  if (input.drawnAlphaPath !== undefined) {
    const drawnCapture = loadImage(input.drawnAlphaPath);
    if (drawnCapture.width !== native.width || drawnCapture.height !== native.height) {
      notes.push(
        `declaration conformance NOT MEASURED: the conformance capture is ${drawnCapture.width}x` +
          `${drawnCapture.height} where the fixture is ${native.width}x${native.height}, so the ` +
          "declared geometry cannot be placed on it.",
      );
    } else {
      // The tier's own interior alpha, read where the material is unambiguously
      // the material: inside the declared contour by the same depth the shoulder
      // measurement calls the body. Analytic distance, from the declaration.
      const depthPx = INTERIOR_ALPHA_DEPTH_CSS_PX * input.scale;
      const deep: number[] = [];
      const pixels = drawnCapture.width * drawnCapture.height;
      for (let index = 0; index < pixels; index += 1) {
        if ((region.signedDistancePx[index] as number) <= -depthPx) {
          deep.push((drawnCapture.data[index * 4 + 3] as number) / 255);
        }
      }
      deep.sort((a, b) => a - b);
      const interiorAlpha = deep.length === 0 ? 0 : (deep[Math.floor(deep.length / 2)] as number);
      if (interiorAlpha < MIN_INTERIOR_ALPHA) {
        notes.push(
          `declaration conformance NOT MEASURED: this tier's interior alpha over a transparent ` +
            `page is ${interiorAlpha.toFixed(4)}, under the ${String(MIN_INTERIOR_ALPHA)} an alpha ` +
            `coverage rule needs. A tier that composites its material below the threshold cannot ` +
            `be separated from its own outer shadow by any fixed alpha, so the reading is refused ` +
            `rather than reported. Absent, not a conformance failure.`,
        );
      } else {
        // No region: the whole point is to see a surface OUTSIDE the declaration.
        const drawn = extractSilhouette(drawnCapture, {
          kind: "alpha",
          threshold: DRAWN_ALPHA_THRESHOLD,
        });
        const drawnArea = silhouetteArea(drawn);
        if (drawnArea === 0) {
          notes.push(
            `declaration conformance NOT MEASURED: nothing in the conformance capture reaches ` +
              `alpha ${String(DRAWN_ALPHA_THRESHOLD)}, so this tier drew no coverage to compare.`,
          );
        } else {
          const against = contourDistance(drawn, region.silhouette);
          conformance = {
            drawnAreaWeb: drawnArea,
            declaredIoUWeb: silhouetteIoU(drawn, region.silhouette),
            declaredContourP95Px: against.p95Px,
            declaredContourMaxPx: against.maxPx,
          };
        }
      }
    }
  }

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
    if (conformance !== undefined) {
      notes.push(
        `declaration conformance measured but NOT REPORTED: it is a row of the shape axis and the ` +
          `axis is absent for this cell. The tier drew ${String(conformance.drawnAreaWeb)} px ` +
          `against a declared ${String(region.areaPx)} px, IoU ` +
          `${conformance.declaredIoUWeb.toFixed(4)}, contour max ` +
          `${conformance.declaredContourMaxPx.toFixed(2)} px.`,
      );
    }
  } else {
    shape = shapeAxisReport({
      silhouetteAreaNative: nativeArea,
      silhouetteAreaWeb: webArea,
      componentRegionArea: region.areaPx,
      componentRegionMarginPx: region.marginPx,
      silhouetteHolesNative: silhouetteHoleCount(nativeSil, region.silhouette),
      silhouetteHolesWeb: silhouetteHoleCount(webSil, region.silhouette),
      silhouetteBodiesNative: silhouetteBodyCount(nativeSil),
      silhouetteBodiesWeb: silhouetteBodyCount(webSil),
      componentRegionBodies: silhouetteBodyCount(region.silhouette),
      silhouetteIoU: silhouetteIoU(nativeSil, webSil),
      contourDistance: contourDistance(nativeSil, webSil),
      cornerCurvature: cornerCurvature(nativeSil, webSil),
      ...(conformance === undefined ? {} : { conformance }),
    });
  }

  /*
   * The perceptual axis, and the band split on it (W13 X6).
   *
   * One SSIM map, averaged four ways: the whole crop as `ssimMean` has always
   * been, then the reference silhouette's band, its deep interior, and the
   * exterior half of the same band. The split is a fixed 24 CSS px of depth
   * converted here — and only here — into device px by the profile's backing
   * scale, because the depth is a property of the material as the eye sees it
   * and the raster is a property of the fixture.
   *
   * The window is the native silhouette, so the rows are absent on a cell whose
   * reference is indistinguishable from its backdrop inside the declared region
   * — there is no contour there to measure depth from, and averaging the whole
   * crop under the name `ssimBand` would be a different quantity wearing this
   * one's label.
   */
  const ssimField = ssimMap(native, web);
  const depthWindows =
    nativeArea === 0
      ? undefined
      : ssimDepthWindows(ssimField, nativeSil, { splitPx: SSIM_BAND_SPLIT_CSS_PX * input.scale });
  if (depthWindows === undefined) {
    notes.push(
      `band-windowed SSIM rows NOT MEASURED: the native silhouette is empty inside the declared ` +
        `component region, so there is no reference contour to split the crop at ` +
        `${String(SSIM_BAND_SPLIT_CSS_PX)} CSS px of depth. Absent, not zero.`,
    );
  } else if (depthWindows.interior === undefined) {
    notes.push(
      `ssimInterior ABSENT: no pixel of the reference silhouette is deeper than ` +
        `${String(SSIM_BAND_SPLIT_CSS_PX)} CSS px from its contour, so this surface is all band.`,
    );
  }
  const perceptual: PerceptualAxisReport = perceptualAxisReport({
    edgeWeighted: edgeWeightedDifference(native, web),
    ssim: ssimFromMap(ssimField),
    ...(depthWindows === undefined ? {} : { depthWindows }),
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
    // The scale reaches the axis for the affine bands alone (W14 X7): their
    // edges are declared in CSS px so the 1x and 2x rows describe the same
    // physical distances from the contour.
    const nativeShadow = shadowField(native, background, region, { scale: input.scale });
    const webShadow = shadowField(web, background, region, { scale: input.scale });
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
