/**
 * The renderer's typed failures.
 *
 * X3 asks for one specific behaviour and this class exists to deliver it:
 * "App-supplied views must satisfy declared usage/format/dimension requirements
 * — **validated at registration with a typed error, never discovered at draw
 * time**." So every provider validates its descriptor before it touches the
 * device, and every rejection carries a code a caller can branch on plus a
 * message that says which requirement failed and what to pass instead.
 *
 * The split from core's diagnostics channel is deliberate and mirrors the one
 * `scene.ts` draws: a structural mistake — a view of the wrong format, a
 * duplicate source id, a draw against a torn-down device — throws, because
 * continuing leaves the resource graph describing textures that are not there.
 * Recoverable, per-frame findings are not errors: those travel as
 * `demotionReason`s through core's state model, which is the honest place for
 * "this still renders, just less".
 */

export const RENDERER_ERROR_CODES = [
  /** A `GPUTextureView`'s backing texture lacks a required usage flag. */
  "texture-usage",
  /** Format outside the set the sampling path can read. */
  "texture-format",
  /** Wrong view dimension, or a depth/array layer count the pass cannot bind. */
  "texture-dimension",
  /** Zero or absurd extent, or a size that exceeds the device's limits. */
  "texture-size",
  /** A source id registered twice, or an unknown id referenced. */
  "source-identity",
  /** The provider was asked for a frame it cannot produce (closed video, detached canvas). */
  "source-unavailable",
  /** No device is attached, or the attached one is lost. */
  "device-unavailable",
  /** A frame was acquired twice without a release, or released without an acquire. */
  "frame-protocol",
  /** A pass was asked to draw something the current resources cannot express. */
  "pass-input",
] as const;

export type RendererErrorCode = (typeof RENDERER_ERROR_CODES)[number];

export class RendererError extends Error {
  readonly code: RendererErrorCode;
  /** The source, group or node the failure is about, when there is one. */
  readonly subject: string | undefined;

  constructor(code: RendererErrorCode, message: string, subject?: string) {
    super(message);
    this.name = "RendererError";
    this.code = code;
    this.subject = subject;
  }
}

export function rendererError(
  code: RendererErrorCode,
  message: string,
  subject?: string,
): RendererError {
  return new RendererError(code, message, subject);
}
