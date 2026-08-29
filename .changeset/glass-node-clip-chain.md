---
"@vitreajs/vitrea": minor
"@vitreajs/vitrea-web": minor
---

Glass inside an `overflow: scroll` ancestor is now cropped by it.

`GlassNodeRecord.clip` was declared, documented and populated by nobody: the
read phase never passed it and nothing ever read it, so the pipeline believed
the border box — which `getBoundingClientRect` reports wherever a surface has
scrolled to, including entirely outside the scroller (Decision Log #41(k)).

Three things follow, and all three were wrong before:

- **The proxy is cropped.** A group's backdrop proxy lives in the plane layer,
  not inside the app's scroller, so nothing crops it on the browser's behalf: a
  surface straddling a scroller's edge had its glass painted in full, hanging
  outside the container. The proxy's painted region and its sampling box are now
  the visible extent, and a corner the crop cut is drawn square rather than
  round.
- **`same-plane-overlap` stops firing between surfaces that cannot touch.** It is
  a hard error, and a surface scrolled out of view was raising it against every
  surface whose box it passed over.
- **`group-proxy-overlap`'s predicate is true again.** It rests on "a proxy
  paints only inside its own clip union", and a union built from unclipped boxes
  made that sentence false under any scroller.

The cost is one extra rect read per clipping ancestor per measurement. The
computed-style walk that finds which ancestors clip runs once per host and is
cached, so a scroll costs rects and not styles, and the zero-reads-at-steady-state
guarantee is unchanged.

`GlassScene.setNodeBounds(id, bounds, clip?)` has carried the third argument
since v1; `clipRect(rect, clip)` is exported for a consumer that holds both.
Rounded clipping ancestors are folded as their bounding boxes — stated in
`clipRect`'s own documentation, and always erring towards reporting more surface
rather than less.
