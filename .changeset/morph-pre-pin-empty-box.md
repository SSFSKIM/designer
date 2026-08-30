---
"@vitreajs/vitrea-react": patch
---

`GlassMorph` no longer claims the top-left of the viewport for a frame before it
opens.

A morph measures its closed end on a frame and only then places itself, and until
now the platter spent that frame in normal flow. Flow inside a plane's host layer
is not the app's layout — a host layer is `position: absolute; inset: 0` over the
viewport, so a block box there is the full width of the page at the page's origin.
That box was registered like any other glass surface, which meant a freshly
mounted morph briefly overlapped every surface on its plane and stretched its
sampling group's backdrop proxy across the whole viewport. On a page with dev-mode
diagnostics on, it showed up as `same-plane-overlap` and `group-proxy-overlap`
findings for a layout that never had either.

The platter is now out of flow from its first commit and explicitly empty until it
has been placed, so there is no meaningful box to register until there is a real
one. Nothing about the closed footprint changes: that has always been the morph's
anchor spacer, which still sits in the app's own layout and still holds the space.

For apps this removes a placement constraint rather than adding one — glass may
sit in the viewport's top-left corner next to a morph, and a morph no longer needs
a sampling group of its own purely to keep that transient out of a neighbour's
proxy. A morph that shares a group with other surfaces is still worth avoiding for
the frame before it places itself.
