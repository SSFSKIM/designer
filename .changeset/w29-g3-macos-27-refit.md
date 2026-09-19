---
"@vitreajs/vitrea-web": minor
---

Measure vitrea against macOS 27 and ship the refitted material as selectable
profile documents. **The material a page draws by default does not change in this
release**; the runtime selection that makes macOS 27 the default is the next one.

macOS 27 changed Apple's Liquid Glass under every app. Measured against the new
reference bed, the body's settled level over a dark backdrop, the rim's amplitude
and width and how much of a backdrop's structure survives the material all moved —
most visibly, a surface over a near-black backdrop is no longer nearly invisible.
Two documents now record the 27 material, one per colour scheme, as patches over
exactly the same renderer default the two macOS 26.5 documents patch. Both tiers
derive from them: the WebGPU tier is fitted and the CSS tier's mapping is refit in
the same change.

Which packages move, and why:

- **`@vitreajs/vitrea-web`** — a documentation and capability change rather than a
  code change, and stated that way on purpose: **no constant in this package
  moved**. What is new is that a second reference material exists and is
  selectable through the options a root already has: a document's `patch` is a
  value `createGlassRoot({ materialProfile })` accepts and its `cssTierMapping` is
  a value the sibling `cssTierMapping` option accepts, and both have to be passed
  for a page to draw the 27 material on both tiers. The README now says which macOS
  each document is measured against, and how to pass one. The CSS tier needed no
  new code to follow the refit — it already derives its blur, tint and rim from whichever
  document the root carries, and the 27 documents carry their own CSS mapping —
  which is the two-tiers-one-profile rule paying for itself. An app that upgrades
  and asks for nothing new draws exactly what it drew before.
- **`@vitreajs/vitrea` and `@vitreajs/vitrea-react`** carry no change of their
  own; they move because the three published packages are versioned as one fixed
  group, which is what keeps a cross-package material claim from being split
  across two versions.

The measurement bed, the documents, the declared bounds and the fifteen rows the
refit did not meet are in the repository rather than in the tarball:
`packages/calibration/profiles/apple-macos-27.0-*.json` and the ledger's §5.153.
