---
"@vitreajs/vitrea-react": minor
"@vitreajs/vitrea-web": minor
---

A toolbar can split its shared glass background, the way every system bar does.

**What is new.** `GlassToolbar`'s children are now partitioned into sampling
groups at each `<GlassToolbarSpacer />` and at each item that declares
`sharedBackground="hidden"` — Apple's `ToolbarSpacer` and
`sharedBackgroundVisibility(.hidden)`, which turn out to be one rule. The result
is one `role="toolbar"` with N groups, never N toolbars: the row keeps its single
tab stop and its arrow-key order across the split, and the flex layout is
untouched, because a group renders no DOM. What changes is what shares a proxy,
a blur and a union.

```tsx
<GlassToolbar aria-label="Document actions">
  <GlassButton onClick={share}>Share</GlassButton>
  <GlassButton onClick={duplicate}>Duplicate</GlassButton>
  <GlassToolbarSpacer kind="flexible" />
  <GlassButton onClick={publish} sharedBackground="hidden" tint="#ff9500">
    Publish
  </GlassButton>
</GlassToolbar>
```

This is also how two tints coexist in one toolbar. A group carries one seed, so a
tinted primary action beside a tinted bar is two groups by construction — and the
item that steps out can carry `groupProps` of its own for anything else that
group needs.

**The gap is derived, not chosen.** Two adjacent groups each sample a padded
region around their own shapes, and where one group's padded box covers the
other's shapes the backdrop filter applies twice over the overlap. A spacer
therefore opens the sampling padding the material actually requires under the
resolved accessibility policy, and never less than the advisory the scene model
checks a layout against: turn *Reduce Transparency* on, the frost thickens, and
the material's own requirement rises past that advisory on a normal-height bar.
Your own `gap`, margin or width adds to it, and an explicit `style` of your own
still wins. The material's half of that number is now exported from
`@vitreajs/vitrea-web` as `samplingPaddingFor({ members, material })`, which is
what a host-level app splitting a toolbar over the framework-agnostic entry
reaches for — groups are already the primitive there, so nothing else was needed.

**Nothing about the material moves.** The frame loop resolves each group's blur
through the same composition it always did, now named `proxySamplingSigma` and
shared with the derivation above rather than written out twice.
