# Skill Architecture: Figma Core + Grafts from frontend-design & impeccable

Decision (2026-07-22): no broad open-source survey. The skill = **Figma Make workflow as core**, with targeted grafts from exactly two sources, both already on disk:

- `frontend-design` — Anthropic official plugin (`~/.claude/plugins/cache/claude-plugins-official/frontend-design/`), single ~56-line SKILL.md. License: bundled LICENSE.txt (check before vendoring verbatim text).
- `impeccable` v3.5.0 — Matt Pocock-ecosystem skill (`~/.claude/skills/impeccable/`), SKILL.md + 28 reference files + scripts. **Apache 2.0** — vendorable with attribution (keep MIT/Apache footers per doperpowers precedent).

## The key finding: triple convergent evolution

All three systems independently evolved the *same architecture*:

| Function | Figma Make | impeccable | frontend-design |
|---|---|---|---|
| Per-project design law | `guidelines/Guidelines.md` (+ theme.css owns values) | `PRODUCT.md` + `DESIGN.md` (context.mjs loads each session) | inline "compact token plan" (per-task) |
| Anti-default entropy | `create_make_theme` sampler (3 stances / 2 traditions / 1 canvas, "pick the less-common one") | `palette.mjs` brand-seed script | calibration paragraph naming the 3 AI-default looks |
| Stance commitment | "commit to one stance" | color-strategy commitment axis (restrained/committed/full/drenched) | "spend your boldness in one place" + signature element |
| Conditional modules | skills: aesthetic-stance, icon-illustration, design-imports… | reference/: brand.md vs product.md registers + 22 command refs | — (single file) |
| QA | blind checklist (no eyes) | `detect.mjs` slop detector + `critique` scoring + `live` browser iteration + screenshots | self-critique + screenshots |

This validates the architecture for our skill: **project-law file + entropy sampler + committed stance + register-conditional references + verification loop.**

## The critical tension (and why the grafts are mandatory, not optional)

Figma's own outputs cluster into exactly the AI-default looks the other two skills ban:

- Figma R2 "Quiet editorial" = warm cream `#F5F0E8` + Newsreader serif + vermilion accent → **this is frontend-design's "AI default look #1" (cream near `#F4F1EA` + high-contrast serif + terracotta)** and sits squarely inside impeccable's banned cream band (OKLCH L 0.84–0.97, C < 0.06, hue 40–100).
- MERIDIAN (Round 4b) = near-black + hot vermilion `#FF3B1D` accent, hairline rules, mono labels → frontend-design's **default looks #2 and #3 combined**; and its `--paper: #F4F1EA` is the *literal hex* frontend-design names as the cream tell.
- Figma's uppercase tracked DM Mono eyebrows on every section → impeccable's banned "2023-era kicker" scaffold.

Conclusion: **Figma supplies the process architecture and craft engineering (structure); impeccable + frontend-design supply the 2026-era taste calibration (anti-slop priors).** Using Figma's example systems as-is would bake in the very defaults the workflow claims to break. The skill must encode Figma's *procedures* (OKLCH ramp construction, semantic tokens, stance→guidelines→code chain, blind QA) while replacing its aesthetic *priors* with the sharper slop taxonomy — and widening the entropy sampler beyond Figma's 10 stances so sampling itself pushes outside saturated lanes.

## Graft list — frontend-design (whole file is dense; near-total vendor)

1. **Studio framing**: "design lead at a studio known for identities that couldn't be mistaken for anyone else's; client already rejected templated proposals; take one real aesthetic risk you can justify."
2. **Ground it in the subject**: the subject's world — materials, instruments, artifacts, vernacular — as the source of distinctive choices. (Figma has product-category tables; this is sharper and more generative.)
3. **Hero as thesis** — open with the most characteristic thing in the subject's world; the big-number-small-label hero named as template.
4. **Calibration paragraph**: the three named AI-default looks + "the brief's own words always win, including when it asks for one of these looks."
5. **Two-pass process**: compact token plan (4–6 named hex, 2+ type roles, ASCII wireframe, **signature element**) → self-review ("would I arrive here for any similar brief?") → build exactly to plan.
6. **Signature-element discipline**: one memorable thing, everything else quiet; Chanel remove-one-accessory; "not taking a risk is a risk."
7. **Writing-in-design section**: copy as design material; user-side naming; active voice; action keeps its name through the flow; errors state what happened + next step; empty states invite action. (Complements Figma R3-P8 voice-per-stance tables.)
8. CSS specificity-cancellation warning (practical bug class).

## Graft list — impeccable (selective; it's huge)

**Craft rules with numbers** (SKILL.md "General rules" — merge with Figma's R2 values):
- Contrast verification incl. placeholder text; gray-on-color fix (darker shade of bg's own hue).
- Body measure 65–75ch; scale-step ratio ≥1.25; ≤3 families; pair on a contrast axis, never two similar sans; display tracking floor ≥ −0.04em; hero clamp ceiling ≤6rem; `text-wrap: balance`/`pretty`.
- Semantic z-index scale; `repeat(auto-fit, minmax(280px, 1fr))`; dropdown clipping escape (dialog/popover/fixed/portal).
- Motion: ease-out expo family, no bounce/elastic; reduced-motion mandatory; reveal must enhance an already-visible default (headless-render blank-section bug); blur/backdrop/clip-path/mask as legitimate premium motion material.

**Anti-slop taxonomy** (the 2026 state of the art; adopt wholesale):
- Absolute bans: side-stripe borders; gradient text; glassmorphism-as-default; hero-metric template; identical card grids; eyebrow-on-every-section; numbered markers as reflex scaffold; heading overflow.
- The cream-band ban with its OKLCH specification and token-name tells (`--paper`, `--cream`, `--sand`…).
- **Second-order category-reflex check**: if category + anti-reference still predicts the aesthetic family ("fintech that's not navy-gold → terminal-dark"), it's the trap one tier deeper. This is the strongest generalization device in any of the three systems.
- Physical-scene sentence to force dark-vs-light (never a default).
- Color-strategy commitment axis: restrained / committed / full palette / drenched.
- Copy bans: no em dashes, no aphoristic cadence, no buzzword family; verb+object buttons; standalone-meaning links.

**Architecture to imitate (not copy verbatim)**:
- Register split: `brand.md` (design IS the product) vs `product.md` (design SERVES the product) — cleaner than Figma's single path; our skill should route the same way.
- `detect.mjs`-style slop detection and `critique`-with-scoring as the verification loop; `live` browser iteration concept pairs with our playwright-cli verification.
- PRODUCT.md/DESIGN.md persistence — merges naturally with Figma's Guidelines.md into one "project design law" artifact.

**Mine later during build** (not yet read): `reference/brand.md` (reflex-reject aesthetic lanes list), `reference/product.md`, `reference/craft.md`, `reference/critique.md`, `reference/animate.md`, `reference/overdrive.md` (ambitious effects — likely adjacent to our SVG-filter layer), `reference/delight.md`.

## What NO source covers (our SVG-filter layer remains unique)

- impeccable *bans* glassmorphism-as-default and only names blur/backdrop/clip-path as motion materials; frontend-design doesn't touch materials; Figma's effects policy (R2-P3) is the most developed but deliberately conservative ("displacement: rarely, non-essential artwork only").
- Nobody teaches SVG filter primitives as a designed material system (liquid glass, engineered displacement maps, goo, grain, specular lighting) with an earned-effects framework. That's the second skill's territory — and Figma's R2-P3 "effect is earned when…" framework becomes its gating layer.

## Synthesis shape for the Figma-replica skill (input to the approaches step)

- **SKILL.md** ≈ aesthetic-stance skeleton + frontend-design's framing/two-pass + impeccable's absolute bans and slop test (the always-loaded taste floor).
- **Entropy sampler** as a skill asset: Figma's 10 stances × widened with impeccable's reflex-reject lanes and frontend-design's calibration, sampling instruction "pick the less-common one; brief always wins."
- **references/**: stance→system procedures (Figma R2/R3 craft values, OKLCH engineering, motion system, composition patterns), register split (brand/product), effects policy, voice/copy, QA protocol (blind checks + screenshot verification when available).
- **Project law**: the skill authors a per-project `DESIGN.md`/Guidelines.md (FRAME + MERIDIAN as the canonical contrast pair showing one brief → two committed systems).
