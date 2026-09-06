---
"@vitreajs/vitrea-web": minor
"@vitreajs/vitrea-react": minor
---

A page in dark mode can ask for the dark material.

**What you get.** `createGlassRoot({ colorScheme })` and `<GlassRoot colorScheme>`
take `"light" | "dark" | "auto"`. `"dark"` draws the material vitrea measured
against Apple's own renderer in dark mode rather than the light one over a dark
page; `"auto"` follows `prefers-color-scheme` and re-derives both tiers when the
system flips, without rebuilding the root, so a theme toggle costs no
registrations. `root.colorScheme` reports which of the two is actually drawing and
`root.setColorScheme(...)` changes it on a live root. The default is `"light"`,
which is the material the runtime's own constants already are, so nothing moves
for an app that upgrades.

Until now the dark numbers existed only as a calibration document inside this
repository: a host in dark mode got the light material, and the only way out was
to copy constants nobody exported. `@vitreajs/vitrea-web` now exports them as
`darkMaterialProfile`, generated from that document with a test pinning the two
together, so an app that resolves its own scheme somewhere vitrea cannot see can
pass the patch directly — and an app that wants the dark material with a tuning of
its own can pass both, because the scheme selects the base and `materialProfile`
merges over it leaf by leaf.

One distinction worth keeping: a group's backdrop `hint` states the tone of what
is behind the surface, and `colorScheme` states which material the surface is made
of. They are different questions, and a dark page can honestly hand a light hint
to a surface over a white card. Your page's own background stays yours either way
— the runtime does not write your tokens, so an app offering "follow the system"
reads the query for its own colours as well as passing `"auto"` here.
