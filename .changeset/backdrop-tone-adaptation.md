---
"@vitreajs/vitrea-web": minor
---

Glass now adapts to how light or dark the content behind it is.

Apple's material continuously changes its appearance with backdrop luminance — a
light-scheme capsule over black content settles to near-black. vitrea had no such
axis at all: material profiles were discrete per colour scheme, so a surface
looked the same over a photograph and over a black field. That was this project's
largest measured fidelity gap.

**This changes how your existing surfaces look over dark or busy backdrops**, and
it is continuous rather than a two-state switch — intermediate backdrops land
between the ends, on a measured curve.

Where each tier gets its answer, because they differ and the difference is worth
knowing:

- **The WebGPU tier** reads the pixels it is already sampling to refract, so
  adaptation is local to each surface's own neighbourhood.
- **The CSS tier** has no pixels. It asks, in order: an explicit
  `backdropLuminance` you set on the surface; then the backdrop source you have
  already handed over via `GlassGroup`'s `backdrop` prop, read once and averaged;
  then nothing at all, in which case it does not adapt. It never guesses a level.

So on the CSS tier the adaptation is one reading per backdrop **source**, not per
surface — two surfaces over different corners of the same image get the same
answer. If you need better than that on that tier, set `backdropLuminance`
yourself.

Accessibility policies still win: reduce-transparency and increase-contrast
resolve after adaptation, not before.
