import { silhouetteBackdropTone } from "../../../platform-web/src/backdrop-tone";
import { createWebGPURenderer } from "../../src/renderer";
import { createAppTextureProvider } from "../../src/backdrop";
import { srgbToLinearChannel } from "../../src/color";
import type { MaterialProfilePatch } from "../../src/material";
import type { SurfaceInput } from "../../src/render-model";

/** Real reduction and real optics, with a structured left host and uniform right host.
 * Altering the obsolete source reference must not alter either local solve. */
export async function silhouetteProbe(
  mode: "silhouette" | "source" | "absent", sourceReference = 0.3, split = false, hint = false,
  alpha: "opaque" | "partial" | "empty" = "opaque",
) {
  const adapter = await navigator.gpu.requestAdapter();
  if (adapter === null) throw new Error("No adapter");
  const device = await adapter.requestDevice();
  device.pushErrorScope("validation");
  const width = 128, height = 64;
  const pixels = new Uint8Array(width * height * 4);
  for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
    const encoded = x < 64 ? (x % 2) * 255 : 191;
    const a = x >= 64 || alpha === "opaque" ? 255 : alpha === "empty" ? 0 : encoded;
    pixels.set([encoded, encoded, encoded, a], (y * width + x) * 4);
  }
  const source = device.createTexture({ size: [width, height], format: "rgba8unorm",
    usage: GPUTextureUsage.COPY_DST | GPUTextureUsage.TEXTURE_BINDING });
  device.queue.writeTexture({ texture: source }, pixels,
    { bytesPerRow: width * 4 }, [width, height]);
  const profile: MaterialProfilePatch = {
    ...(mode === "absent" ? {} : { backdropToneAbscissa:
      mode === "source" ? "source" : { kind: "silhouette" } }),
    outerShadow: { thinOcclusionDark: 0, thinOcclusionMid: 0, thinOcclusionBright: 0,
      thickOcclusionAt96: 0, thickOcclusionAt128: 0, thickOcclusionAt160: 0, liftAmplitude: 0 },
    optics: { regular: { rimAlpha: 0, shadowAlpha: 0 } },
  };
  const renderer = createWebGPURenderer({ materialProfile: profile });
  renderer.attachDevice(device, "app");
  renderer.setViewport({ widthCss: width, heightCss: height, devicePixelRatio: 1 });
  renderer.registerBackdrop(createAppTextureProvider({ id: "bg", device, texture: source,
    colorSpace: "srgb", alphaMode: alpha === "opaque" ? "opaque" : "unpremultiplied", encoded: true }));
  const surfaces: SurfaceInput[] = [32, 96].map((x, i) => ({
    nodeId: `host-${i}`, family: "fixed-rounded-rect",
    reference: "figma-smoothing", shape: { center: [x, 32], size: [48, 32],
      radii: [8, 8, 8, 8], smoothing: 0, thickness: 8 },
  }));
  const css = surfaces.map((surface) => silhouetteBackdropTone(
    new Uint8ClampedArray(pixels), width, height, {
      bounds: { x: surface.shape.center[0] - 24, y: 16, width: 48, height: 32 }, radius: 8,
      viewport: { width, height, devicePixelRatio: 1 },
    },
  ));
  const groups = split ? surfaces.map((surface) => [surface]) : [surfaces];
  groups.forEach((members, i) => renderer.setGroup({
    groupId: `group-${i}`, surfaces: members, backdropSourceId: "bg",
    refraction: "none", analysisExact: false,
    backdropTone: [sourceReference, sourceReference, sourceReference],
    backdropToneLevel: srgbToLinearChannel(sourceReference),
    backdropToneHint: hint,
    backdropToneLinearLuminance: sourceReference,
    union: { neckWidth: 0, maxBulge: 0, separationThreshold: 0 },
  }));
  const target = device.createTexture({ size: [width, height], format: "rgba8unorm",
    usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.COPY_SRC });
  renderer.drawFrame({ frame: { id: 1, timeMs: 0 }, optics: target.createView() });
  await renderer.collectAdaptation();
  const readings = groups.flatMap((_, i) => renderer.backdropToneAbscissae(`group-${i}`));
  const readback = device.createBuffer({ size: width * height * 4,
    usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ });
  const encoder = device.createCommandEncoder();
  encoder.copyTextureToBuffer({ texture: target }, { buffer: readback, bytesPerRow: width * 4 },
    [width, height]);
  device.queue.submit([encoder.finish()]);
  await readback.mapAsync(GPUMapMode.READ);
  const output = Array.from(new Uint8Array(readback.getMappedRange()));
  readback.unmap();
  const error = await device.popErrorScope();
  renderer.destroy();
  source.destroy(); target.destroy(); readback.destroy(); device.destroy();
  if (error !== null) throw new Error(error.message);
  return { readings, css, output, width, height };
}
