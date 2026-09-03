---
"@vitreajs/vitrea-web": minor
---

The shadow under glass now changes with the content behind it, and adds light as
well as removing it.

Every glass surface cast one shadow at one strength, whatever it was standing
over and however large it was. Apple's does not. Measured across its own
material, the shadow is two things composited on one falloff, and this release
carries both.

**It reads the backdrop.** Below the size law's knee the shadow's depth is keyed
on how light the content behind the surface is — full strength across the whole
ordinary range, about a third of that over a near-white backdrop, and nothing at
all over a black one. A small control on a white card was casting a shadow more
than twice as dark as Apple's; that was the single largest visible error in the
facet and it is gone.

**It grows with the surface.** Above the knee the shadow deepens with the
casting span rather than sitting at one amplitude, which is what "larger glass
casts a deeper, richer shadow" means in practice.

**It carries the backdrop's own light.** On the WebGPU tier a large surface's
shadow adds a blurred copy of the light behind it underneath the darkening,
which is why Apple's big platters do not read as a flat gray smudge. The CSS
tier carries the geometry and the backdrop-keyed depth but not this second term
— a `box-shadow` cannot reach the backdrop outside its own element — so the two
tiers differ slightly under large surfaces and agree everywhere else.

**Under Reduce Transparency the shadow goes flat**, at the one level Apple's
does: the preference removes the adaptation, so every surface over every
backdrop gets the same shadow rather than a scaled version of the adaptive one.

Nothing in your code changes. If you pass a material profile of your own, the
shadow's amplitude is now six named constants plus the second term's four rather
than a single `outerShadow.occlusion`, and a profile still naming the retired
one is refused with a message that names its replacements rather than silently
rendering the shipped shadow.

Measured against macOS 26.5 and recorded in `c9a-fidelity-claims.md` §5.62.
