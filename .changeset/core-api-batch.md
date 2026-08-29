---
"@vitreajs/vitrea": minor
"@vitreajs/vitrea-web": minor
"@vitreajs/vitrea-react": minor
---

The scene model grows the three fields another package was already carrying.

All three were recorded together in Decision Log #23(c) as the same shape — "core
grows a field another package already carries" — and deferred as a batch rather
than drip-fed as core churn.

- **The corner reference is a scene-model field.** `GlassNodeDescriptor.reference`
  and `GlassHostOptions.reference` carry which of the two corner fits a shape is
  authored against; `GlassSurface` sends it from its `profile` prop. **This
  changes what the WebGPU tier draws for a surface with a non-`"continuous"`
  profile.** The renderer has always had the field and nothing ever set it, so
  every surface was resolved against the Apple-direct fit — including one
  authored on the Figma smoothing axis, which is a separate fit rather than
  another point on the same axis (#22(a)). `profile="circular"` and
  `profile={0.6}` are now drawn on the axis those values live on. The CSS tier is
  unaffected: it renders corners with `border-radius`.
- **The concentric parent link is a scene-model field.**
  `GlassNodeDescriptor.concentricOf` / `GlassHostOptions.concentricOf` declare a
  surface as a level set of another surface's field (X8 rider 2). An unknown
  parent, a parent in another group, a self-reference and a cycle are all refused
  at registration, where the call that caused them is still on the stack, instead
  of throwing once per frame from the renderer's draw path; and a parent with a
  child still attached refuses removal, like a group with members.
- **The platform probe can be set per group.** `setPlatformProbe(probe, groupId?)`
  mirrors `setGovernorPressure`. S1's backdrop-root audit is per group, so a
  group whose proxy chain is re-rooted has to demote alone — which a scene-wide
  probe could not express, so the browser layer bypassed `resolve()` and folded
  the verdict into a private call to core's pure resolver. It no longer does, and
  `scene.resolve()` and `root.capabilities(groupId)` now give one answer instead
  of two. `effectiveGroupState` is deprecated in favour of the scene path.
