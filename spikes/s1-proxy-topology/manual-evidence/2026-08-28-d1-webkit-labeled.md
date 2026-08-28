# D1 fully labeled — retail Safari 26 (WebKit), user manual pass, 2026-08-28

The labeled per-engine reading checklist item 2.1 asked for, WebKit half. The
user's report, verbatim:

> - D1, fully labeled. Backdrop-root-forming in this WebKit: `opacity: 0.99`,
>   `filter: blur(0px)`, `filter: grayscale(0)`, `mask-image`,
>   `clip-path: inset(0)`, `mix-blend-mode: multiply`, and
>   `will-change: opacity`. Harmless: the control, `filter: none`,
>   `contain: paint`, `isolation: isolate`, `will-change: transform`,
>   `translate3d(0,0,0)`. So the previously-unattributed asymmetry now has an
>   owner — WebKit is where `will-change: opacity` kills the proxy while
>   `will-change: transform` doesn't. Two details are genuinely informative:
>   `filter: none` is safe while `blur(0px)`/`grayscale(0)` break (an identity
>   filter still forms a backdrop root — the value's presence matters, not its
>   effect), and `isolation: isolate` does not re-root despite creating a
>   stacking context.
> - C1: the padded-box mask stands proud as a blurred rectangle — the halo is
>   real, confirming vitrea's panel-shaped mask is load-bearing in WebKit.
> - The D1 control being blurred also confirms the portaled masked proxy
>   renders at all in retail WebKit — the substance behind A1's field.

## What moved on this evidence

`packages/platform-web/src/probe/conformance-table.ts` gained a
`webkit / minVersion: 26` row: `rasterisesBackdropFilter: "yes"` (the D1
control), `backdropRootTriggers: "normative"` (the labeled set is exactly the
Filter Effects 2 normative membership — including the identity-filter and
isolation details), `edgeMode` deliberately still `"unverified"` (section C
measures mask extent, not the sampling edge mode), `transform3dHazard`
unchanged at `"perspective-preserve3d"` (bugs 252181/201987 open;
`translate3d(0,0,0)` measured harmless is consistent, not a contradiction).
WebKit below 26 keeps the presumptive unverified row; Gecko's gate is still
open — no Firefox run has been made.
