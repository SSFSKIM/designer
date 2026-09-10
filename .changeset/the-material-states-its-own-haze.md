---
"@vitreajs/vitrea-web": minor
---

The frosted haze inside a large surface is now the width Apple's is, instead of whatever level the
backdrop pyramid happened to stop at.

vitrea's body has always been two components — a sharp one and a heavy one, mixed by depth — and
until now the heavy one had no width of its own: it was a sample of the blurred-backdrop pyramid,
and at ordinary display scale that sample was pinned to the chain's last level, 13.4 device pixels
wide, whatever the material asked for. Apple's is **8.6–9.5 device pixels at both scales**, measured
by fitting the composite vitrea actually computes to every thick backdrop of one surface at once,
with the fit held against vitrea's own known kernel as a control — the first reading of this
material that had one. So the heavy component was half again too wide, which is also why two earlier
attempts to raise its share made things worse: more of a too-wide component is more of the wrong
thing. The material now states the width directly (`sizeHeavyTapSigma`, `sizeHeavyTapSigma2x`, both
**9**) and the renderer builds it as a real Gaussian rather than a chain level. Against Apple's own
captures the width's error over six independently read surfaces falls by three quarters, and a thick
surface over a coarse pattern now washes it flat by about as much as macOS does rather than
noticeably more.

**This is a WebGPU-tier change, and the CSS fallback tier deliberately does not follow it yet.** Its
own frosted layer is unchanged — byte for byte, on 640 of 644 captures of the calibration bed — so a
page that falls back to `backdrop-filter` looks exactly as it did. Giving that tier the same width
was tried and measured, and it cost structure on every large surface over a patterned backdrop,
badly enough to show as a checkerboard through the inner pane of nested glass. The two tiers'
frosted widths therefore differ for now, which is a known gap with its own measurements recorded
rather than a difference nobody noticed.
