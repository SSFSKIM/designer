# apps/demo

Two pages, one Vite app.

| Route | What it is |
| --- | --- |
| `/` | **vitrea's public demo site.** Designed under [`DESIGN.md`](./DESIGN.md); asserted by [`e2e/site.spec.ts`](./e2e/site.spec.ts). |
| `/playground/` | **The internal acceptance harness.** What `vitrea-react`'s Playwright suite drives. Its structure, control names and layout are pinned by those tests, and it is deliberately outside the design law. |

```sh
pnpm --filter demo dev        # both routes, on http://localhost:5173
pnpm --filter demo build      # a static site in apps/demo/dist
pnpm --filter demo preview    # serve that build
pnpm --filter demo lint       # eslint + tsc for src and for e2e
pnpm --filter demo test:e2e   # the site suite: layout law, the pair, a11y, contrast
```

Both routes accept `?renderer=css` and `?renderer=webgpu`. The default is `webgpu`,
and asking is not getting: where there is no adapter, no device or no renderer
chunk, every group resolves to the CSS tier and the page's readouts name the
reason. That is the thing the site exists to show, which is why the default is safe
to ship.

## The static build

`pnpm --filter demo build` writes a self-contained directory. Serving it needs a
static file server and nothing else: no rewrites, no redirects, no runtime, no
network access from the page (there are no webfonts and no third-party requests at
all).

```
dist/
  index.html                  the site
  playground/index.html       the harness
  assets/                     hashed JS and CSS, including the lazily imported
                              WebGPU renderer chunk
  fixtures/
    backgrounds/              the six shared raster backgrounds
    apple-macos-26.5-1x-light-standard/
                              the native Liquid Glass captures the reference
                              pair compares against
```

**Asset paths are relative** (`base: "./"` in `vite.config.ts`), so the same
`dist/` works at `/`, at `/vitrea/`, or at any other prefix. That is what makes it
GitHub Pages compatible without a build-time base flag: a project site published at
`https://<user>.github.io/<repo>/` and a user site published at the domain root
both resolve `./assets/...` and `./fixtures/...` correctly, and the nested
`/playground/` entry resolves `../assets/...`. Verified by serving `dist/` under a
`/vitrea/` prefix and loading both routes plus a fixture.

### Where the fixtures come from

`fixtures/` is copied at build time from `apps/reference-apple/fixtures/`, which is
committed machine-specific ground truth belonging to the capture harness. It is not
a `public/` directory and it is not duplicated into this app's source tree, because
the whole value of those PNGs is being the ones ScreenCaptureKit produced on the
capture machine, and a second copy is a second thing to drift. `vite.config.ts`
holds both halves of that: a dev-server middleware that maps `/fixtures/*` onto the
harness directory, and a `closeBundle` hook that copies the two directories the
site references. Add a directory to that list when the site starts showing a new
profile.

### Publishing to GitHub Pages

There is no workflow committed yet (release automation is a later task). The manual
shape is:

```sh
pnpm -r build                                  # the packages the app aliases to source
pnpm --filter demo build
# then publish apps/demo/dist as the Pages artifact
```

In an Actions workflow that is `actions/upload-pages-artifact` with
`path: apps/demo/dist`, followed by `actions/deploy-pages`. Nothing else is needed:
no `.nojekyll` is required for these paths, and no base path has to be configured.

## Why the site does not scroll its glass

X1 puts every glass surface in a viewport-fixed plane and documents arbitrary
interleaving with foreign stacking contexts out of contract for v1. So the site is
an asymmetric split: the narrative column scrolls and the instrument window on the
right is `position: fixed`, with all glass inside it. A page that scrolled its own
glass out from under itself would be the library lying on its own home page. The
stage follows the section the reader is on, which is what keeps the demonstration
attached to the prose without pretending the plane model offers something it does
not.

## Fidelity figures

Every number on the page is read from
`packages/calibration/results/matrix.json` at build time and rendered with its
cell: native profile, engine and version, renderer, sampling backend, GPU adapter
class, tier and fixture set. A scene with no measured cell renders a labelled empty
slot instead of borrowing a figure from a different cell. Fidelity tuning runs
separately and writes into the same file, so more cells means more filled slots and
no page change.

One check is worth naming because it is unusual: `e2e/contrast.spec.ts` measures
text contrast over the live glass on the rendered pixels, across several phases of
the backdrop's drift. axe reports "incomplete" for text whose background is a canvas,
which is every label on this page's glass, so the floor for those would otherwise be
unchecked.

The geometry in the reference pair comes from `apps/reference-apple/scenes.json`,
the same file the SwiftUI harness reads. `e2e/site.spec.ts` asserts the live
surface lands on exactly the integers that file implies, so the pair is a
comparison rather than an illustration.
