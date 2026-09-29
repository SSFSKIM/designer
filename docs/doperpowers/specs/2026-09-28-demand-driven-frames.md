# Demand-driven frames

Status: landed on `perf/demand-driven-frames` (2026-09-28). Origin: an adopter's performance audit
(opencognita.org, finding F1 / its ticket #48). Governs the root's frame loop
(`packages/platform-web/src/root.ts`), the ticker (`packages/react/src/ticker.ts`) and the scheduler's
demand contract (`packages/core/src/scheduler.ts`). No material constant, law or capture moved.

## Purpose

The root's loop re-armed `requestAnimationFrame` every frame, whatever had changed. A page whose
glass had not moved for minutes still ran all five phases 60 times a second. On the GPU tier it
also re-imported its canvas backdrop and redrew every plane; on the CSS tier it re-read a live
canvas's tone every 250 ms. The adopter measured 36–49 % of a core at idle on the GPU tier and
8–12 % on the CSS tier. Freezing rAF brought that to 0.1 %, so the loop was the whole idle cost.
While media played, a full-canvas `getImageData` of a 2880×1800 board added a ~55 ms long task four
times a second at 4× CPU.

The goal: an unchanged page draws nothing. Everything that changes still reaches the screen on
the frame it did before. Motion runs every frame while it is active, then settles to no frames.

## Design

**One bit of demand.** The root holds `demand`. Anything that can change what a frame draws sets
it and, on a started root, schedules exactly one frame. The frame clears it at its top. At its end
the frame sets it again if it left work behind. The loop re-arms only while it is set. It arms
before running the frame and cancels afterwards if no demand is left, so while it runs its callback
still precedes whatever the page requests from inside the frame, as it did when it re-armed
unconditionally.
`root.framePending` reads it, and `root.requestFrame()` sets it.

**What asks.**

- *The scene.* `createGlassScene({ onChange })` reports every mutation. The root ignores those made
  in `collect` and `read`, because that frame's resolution already covers them. Every other change
  asks for a frame, including one made straight on `root.scene`.
- *Geometry.* `GeometrySync` gained `onDirty`, called from every place that marks. The observers
  and listeners were already there: resize, scroll, the viewport, fonts, the device ratio.
- *Host channels.* The channels are the hosts' inline custom properties, a documented styling
  surface. A `MutationObserver` on each host's `style` attribute asks for a frame on any write. The
  root's own writes during a frame are taken off its queue before the listeners run, so a frame
  never schedules its successor by drawing.
- *The rest of the root's own inputs:* the material (`applyMaterialProfile`, used by the profile,
  the scheme and the OS flip), window focus (`observeWindowActivation`'s invalidate), the probe's
  style observer, a new frame listener, a supplied texture, and the owner's
  `markBackdropSourceDirty`.
- *Element events.* A decoding image (`load`) and a video (`loadeddata`, `seeked`, `resize`,
  `play`, `playing`, `pause`, `ended`, `emptied`) mark their source.
- *A reading the cadence held back.* `backdropReadingDue` returns `retryAtMs`, and one timer
  schedules the frame that takes it.

**What keeps frames coming** (`FrameParticipant.pending`, aggregated by `FrameScheduler.pending()`,
plus the listeners):

- a host's presence or ink crossfade still travelling;
- geometry still marked for the next read;
- the renderer's `framesPending`: an adaptation filter not settled, a stats or silhouette readback
  queued, mapping or uncollected, a rebuilt pyramid whose stats have not been read, or a silhouette
  reduction the cadence deferred. This is the C9a lesson read the other way round: a readback
  resolves only while frames keep coming;
- a live source: a live canvas or a playing video is re-marked each frame while the bridge draws.
  The mark is a change after the frame resolved, so it asks for the next frame;
- a frame listener that did not return `false`.

**Listeners.** `GlassFrameListener` and `GlassTickListener` return `unknown`. `false` means done,
and anything else keeps frames coming, so every listener written before this keeps the per-frame
behaviour it was written for. The return type is `unknown` rather than `boolean | void` so an
expression-bodied listener still type-checks. vitrea's own bindings return `false` once settled,
or `!machine.settled`, and call `ticker.requestFrame()` where they retarget a driver. That
covers `applyFlags`, the segmented indicator, the morph's geometry, and the materialize fade.

**Wake frames.** After an idle stretch, the first frame's delta is the last measured frame interval,
not the gap. A press starting then takes the step it would have taken on a loop that never stopped.
Hand-stepped roots keep the exact deltas they are given.

**Sources.**

- `GlassBackdropTexture`'s canvas arm gained `live?: boolean`. The default `true` keeps today's
  contract: re-imported every frame, and it keeps the root drawing. `false` means the owner calls
  `markBackdropSourceDirty` after each repaint.
- A copy provider re-imports on a rebuild at a newer epoch (`markContentChanged`). Before this, a
  non-live copy was imported once.
- A paused video is not live: its pyramid still describes the frame it shows.
- The GPU tier reads a pyramid's stats once per build (`statsReadFor`), not on a 15 Hz clock forever.
  An unchanged pyramid reduces to unchanged stats.

**The CSS tier's tone readback.** It is now windowed and due-driven:

- `createBackdropSnapshotReader` reads the source pixels under every surface sampling that source
  this frame, padded by the group's sampling padding, not the whole source.
  `silhouetteSourceWindow` bounds every bilinear tap of the reduction. It is computed from the same
  lattice the reduction walks (`silhouetteLattice`), so the window cannot disagree with the taps by
  a rounding. The window is copied at 1:1 and integer offsets, so the reduction sees the same bytes.
- Per-channel sRGB decodes go through a 256-entry table built by `srgbDecode` itself. That is bit
  for bit the same number, without a `Math.pow` per tap.
- A reading is due by liveness: an image when its epoch moves; a marked source when its epoch moves,
  but no more often than the cadence; a live source on the cadence.

## Measurements

The audit's method, on the demo's film-festival gallery page (image backdrop, glass nav, platter
and ticket bar). Full Chromium through Playwright, headless, `--enable-unsafe-webgpu
--use-angle=metal`, 1440×900 at DPR 2, Apple M1 Max. Per-process CPU time over three 15 s windows
after an 8 s settle, summed over the Chromium process tree. `rAF/s` counts the page's
`requestAnimationFrame` callbacks.

| Tier | Before: total (GPU / renderer) | After: total (GPU / renderer) | rAF/s before → after |
|---|---|---|---|
| WebGPU | 56.9 % (31.9 / 24.6) | 0.7 % (0.1 / 0.3) | 121 → 0 |
| CSS | 10.1 % (1.7 / 8.0) | 0.5 % (0.1 / 0.1) | 120 → 0 |

Before is `origin/main` at `4f43d2dc`; after is this branch.

## Decision Log

1. **Demand is opt-out for listeners, not opt-in.** A listener that returns nothing keeps frames
   coming. The alternative was to make every listener opt in by returning `true`. That silently
   freezes every animation written against the old contract, including the demo gallery's
   drifting backdrops and the adopter's board painter, the moment they upgrade. Opt-out makes
   the upgrade free and the saving a one-line change per listener.
2. **`live` defaults to `true`.** Same reason: an upgraded app with a live canvas draws exactly as
   before. `live: false` is the adopter's switch.
3. **The host-style observer rather than a return-value contract for channel writes.** A listener
   that writes its final value on the tick its spring settles would otherwise have to return `true`
   for one more tick. An app driving channels itself has no tick to return from at all. Observing
   the one attribute the channels live in covers both, and taking the frame's own records keeps the
   loop from waking itself.
4. **Stop at `settled`, do not snap.** The motion contract defines `settled` as "further advancing
   would not visibly change the value", so the loop stops there. It does not jump drivers to their
   targets on a final frame.

## Surprises

- The analysis readback re-read an unchanged pyramid 15 times a second forever, and the loop
  hid it by never idling. Keyed on pyramid identity, a static backdrop reads its stats once.
- A copy provider built non-live imported its pixels exactly once, and later rebuilds re-used the
  stale upload. No non-live canvas existed before, so nothing could see it.

## Deferred

- The demo gallery's own listeners still return nothing, so pages with a painter on the ticker
  stay continuous by design (Decision Log 1). Painters that repaint only when something changes
  could return `false` and mark their canvas. The film-festival page's ink chooser does.
- The CSS tier's legacy whole-source statistic (`sampleBackdropTone`, the ≤512 px downsample for
  `backdropToneAbscissa: "source"`) is a mean of the whole source by definition, so it is not
  windowed. It now reads only when due.
- A playing video is re-marked on every rAF. `requestVideoFrameCallback` would mark per decoded
  frame instead.
- A `GlassMorph` whose content is never laid out, for example one mounted in a `display: none`
  tab panel, keeps the root drawing. Its measurement listeners return `true` until the closed
  (and, when materializing, open) end measures non-zero. That matches the old per-frame cost, so
  it is not a regression, but that page never idles. The fix: observe the content node with a
  `ResizeObserver` and request a frame when it gains a box, instead of polling every frame.
