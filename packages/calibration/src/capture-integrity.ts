/**
 * What stands between a page that finished rendering and a capture that may be
 * measured (W27c G1's correction).
 *
 * `web/scene.ts` already checks the conditions whose failure silently
 * invalidates a material reading rather than breaking the run: the viewport must
 * be the declared canvas exactly, because the renderer cover-fits the backdrop
 * texture to the viewport and a differently-framed raster refracts pixels that
 * are not the ones the page composites; the device pixel ratio must be the scale
 * that was asked for, because the capture is diffed against a native fixture at
 * that scale. The page reports each as a `problem`, and a driver that waits for
 * `data-scene-ready` and screenshots has read none of them — a wrongly framed
 * capture looks exactly like a good one and fits exactly like a bad one.
 *
 * So a driver that produces fitting evidence asks this before it believes a
 * report. It is a predicate returning the refusal rather than a throw, for the
 * same reason `probeCanonicalOutputRefusal` is: the caller decides how loud to
 * be, and every disagreement is named at once instead of one failed run at a
 * time.
 */

/** The part of a `SceneReport` a capture's integrity is decided on. */
export interface CaptureIntegrityReport {
  readonly canvas: { readonly width: number; readonly height: number };
  readonly requestedScale: number;
  readonly devicePixelRatio: number;
  readonly problems: readonly string[];
}

/** What the cell being captured declares, from the scene matrix and its own scale. */
export interface DeclaredCapture {
  readonly canvas: { readonly width: number; readonly height: number };
  readonly scale: number;
}

/**
 * The reason this capture may not be measured, or `undefined` when it may.
 *
 * An absent report is refused rather than treated as clean: a ready page whose
 * report never landed is precisely the case where nothing was checked at all.
 */
export function captureIntegrityRefusal(
  report: CaptureIntegrityReport | undefined,
  declared: DeclaredCapture,
): string | undefined {
  if (report === undefined) {
    return "This capture may not be measured: the page reported nothing, so neither its framing " +
      "nor its scale was ever checked.";
  }

  const refusals: string[] = [];
  if (report.canvas.width !== declared.canvas.width ||
      report.canvas.height !== declared.canvas.height) {
    refusals.push(
      `the page's scene canvas is ${report.canvas.width}x${report.canvas.height} where the matrix ` +
        `declares ${declared.canvas.width}x${declared.canvas.height}`,
    );
  }
  if (report.requestedScale !== declared.scale) {
    refusals.push(
      `the page was asked for scale ${report.requestedScale} where the cell is ${declared.scale}`,
    );
  }
  if (report.devicePixelRatio !== declared.scale) {
    refusals.push(
      `the browser's devicePixelRatio is ${report.devicePixelRatio} where the cell is ` +
        `${declared.scale}, so the capture's pixel size is not the native fixture's`,
    );
  }
  if (report.problems.length > 0) {
    refusals.push(
      `the page reported ${report.problems.length} problem(s) — ${report.problems.join(" ")}`,
    );
  }

  if (refusals.length === 0) return undefined;
  return `This capture may not be measured: ${refusals.join("; ")}.`;
}
