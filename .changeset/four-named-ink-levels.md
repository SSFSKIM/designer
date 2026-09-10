---
"@vitreajs/vitrea-web": minor
"@vitreajs/vitrea-react": minor
---

Four named ink levels on every glass host, on both tiers.

```css
.panel__title   { color: var(--vitrea-foreground); }
.panel__caption { color: var(--vitrea-foreground-secondary); }
.panel__meta    { color: var(--vitrea-foreground-tertiary); }
.panel__rule    { border-color: var(--vitrea-foreground-quaternary); }
```

`--vitrea-foreground-secondary`, `-tertiary` and `-quaternary` join
`--vitrea-foreground`: Apple's four label levels, as reduced-alpha versions of
the ink the runtime resolved for this surface. Until now there was one token, so
an app with a caption or a disabled row either wrote it at full strength or
invented a scale against a material it cannot see.

**The alphas are not Apple's copied flat, and that is the point.** 60% is where
the platform's ink reaches WCAG's 4.5 body-text floor over the platform's white
background — and glass is never a white background. Sixty percent of vitrea's
dark ink reaches 4.49 over an encoded level of 1.0 and 3.21 over the regular
material's darkest. So **secondary is raised to whatever holds 4.5 against the
level this surface actually resolved at**, and is Apple's 60% wherever that
already clears it, which is most of the dark appearance. On a surface whose
primary ink cannot hold 4.5 either, secondary collapses onto the primary rather
than publishing a level that is not readable.

**Tertiary and quaternary carry no floor**, deliberately: they are Apple's
supporting and decorative tiers, they are not body text, and lifting them to 4.5
would collapse the scale onto one value. Quaternary is the one Apple warns about
by name — too low-contrast on a thin material — and in dev mode a page whose CSS
uses it while a surface resolves below the material's thin/thick knee now gets a
diagnostic saying so. It changes nothing: the token is published either way.

Under forced colours all four are `CanvasText`, and under increased contrast all
four are the near-monochrome ink. A preference that asked for more contrast does
not get three dimmer answers.
