# The imagery path

**Status:** landed (2.2.1). **Follows** `2026-09-05-settling-experiment.md`, whose 52 builds showed
the gap this closes, and the user's question of 2026-09-08 ("does our skill have a path that lets
it use the photos it needs?"). Sources compared: the Figma Make interview's imagery rules and
Unsplash tool (`Figma Design/Interview Round 2 Result.md` §60–62 and its image-search workflow)
and the impeccable skill's brand reference ("zero images is a bug"; verify every URL).

## Purpose

After this change, a person can hand the skill an image-led brief — a hardware store, a
children's library, a restaurant — and receive a page with photographs in it: photographs the
skill found for that product, confirmed to resolve, credited as their source requires, and
placed with alt text and a container colour, or, where no source answered, an artifact drawn as
content and a record saying which slots to revisit. A project that already owns photography gets
its own photography, found before any search.

## The measured problem

None of the 52 settling builds contains an `<img>` element; 42 draw inline SVG. The three
image-led briefs (library, hardware, rebate) shipped illustrations of storefronts, contour maps
and stamp sheets where a photograph was the natural content. The skill carried the whole
art-direction layer for photographs — roles, queries, the four selection criteria, the ten
disqualifiers, crop rules per slot — ported from the Figma Make interview, and one abstract
sourcing line ("search a stock-photo service") whose code examples pointed at files that never
exist. A Claude Code agent has no image tool; Unsplash's API answers 401 without a key; a
guessed photo id ships as a broken image. The only honest move left was the "imagery as content"
rule, and every build took it.

## Design

**One script, three rungs.** `skills/designer/scripts/find-image.mjs`:

- `inventory [dir]` — every image file already in the project, with dimensions read from the
  file header (PNG, GIF, JPEG, WebP, SVG), skipping build directories. Rung one.
- `search "<query>" [--n] [--orientation] [--source] [--width]` — Unsplash when an access key
  is present (`UNSPLASH_ACCESS_KEY`, else `~/.config/designer/unsplash-key`), Openverse
  otherwise; every candidate is HEAD-checked to answer with an image before it is reported.
  Candidates share one shape: url sized for the slot, page, width, height, colour, alt,
  creator, licence, credit line. Rungs two and three.
- `pick <id>` — the chosen photo's `<figure>` (alt, intrinsic size, container colour, credit)
  and, for Unsplash, the download-endpoint call its API guidelines require when a photo is
  placed. Links carry the `utm_source=designer&utm_medium=referral` the guidelines ask for.

**The fourth rung is the agent's.** When no rung answers, the slot is drawn as content and
`DESIGN.md` §4 records it, so a later pass with a source knows what to revisit.

**Where the skill changed** (2.2.0):

- `SKILL.md`: step 1 of the required first steps reads the project's image assets; step 6 of
  the spine sources imagery off the ladder for a world and draws it for an artifact; one
  taste-floor line — an image-led brief ships imagery, never a coloured block, an empty half, or
  a guessed URL.
- `references/composition.md`, "Imagery integration": the abstract sourcing paragraph becomes
  the ladder, the never-guess rule, and the per-image requirements (alt, intrinsic size,
  container colour, credit).
- `references/qa-protocol.md`, check 7: every image slot is filled and none is guessed.
- `references/guidelines-authoring.md`, §4: the rung per photo slot and why the rungs above
  did not answer.

## Acceptance

Rebuild the three image-led settling briefs (library, hardware, rebate) with fresh agents under
2.2.0, the Unsplash key present, into `figma-design-workspace/imagery-check/<brief>/`. A build
passes when:

- **A1.** It contains at least one photograph (`<img>` whose `src` resolves to an image) placed
  where the brief's subject is a world, and its `DESIGN.md` §4 names the rung per slot.
- **A2.** Every `<img>` has non-empty alt text, intrinsic width and height, and a container
  background colour; every sourced photograph has its credit line.
- **A3.** No `src` was guessed: every remote URL appears in the script's output for that build
  (the builder's search results are saved beside the page).
- **A4.** The rest of the law holds — the build passes the settling measurer's mechanical gate
  (no error, no overflow, no placeholder, contrast).
- **A5.** By eye: the photographs belong to the product (selection criterion A), survive their
  crop (B), sit in the page's tonal world (C), and the page is not a stock-photo collage — one
  or two photographs with a job each, not a photo per section.

## Cost, declared

Three builds at roughly 0.4 M tokens each, one measurement pass, one look.

## Decision Log

- Decision: Unsplash behind a key, Openverse without one, both through one script; picsum and
  similar "random photo" services are not a rung.
  Rationale: Unsplash is the source both references default to and the quality band the
  selection criteria assume; its search API needs an access key, which the user supplied (kept
  outside the repository, never committed). Openverse is key-free and Creative Commons, a real
  search of real subjects at a lower editorial band. A random-photo service returns a
  photograph of nothing in particular, which fails selection criterion A by construction.
  Date/Author: 2026-09-08, Claude.

- Decision: Every search candidate is verified with a HEAD request before it is reported, and
  `pick` registers an Unsplash use through the download endpoint.
  Rationale: the impeccable reference's own finding is that guessed ids 404 and ship as broken
  images; verifying at search time makes the never-guess rule mechanical. The download-endpoint
  call and the UTM-tagged links are what Unsplash's API guidelines ask of an application that
  places photos.
  Date/Author: 2026-09-08, Claude.

- Decision: The key is read from the environment first and a dotfile second
  (`~/.config/designer/unsplash-key`, mode 600).
  Rationale: a subagent's shell may not carry the parent session's environment; a documented
  file location works for every process on the machine without putting the key in the
  repository or in a prompt.
  Date/Author: 2026-09-08, Claude.

- Decision: Project assets are rung one, and reading them joins the required first step.
  Rationale: the skill already said supplied and project photography outranks a search, but
  nothing told the agent to look; an inventory the agent runs makes the precedence real.
  Date/Author: 2026-09-08, Claude.

- Decision: Results are cached for a day under `~/.cache/designer/find-image` (and every
  candidate by id for a week), a spent Unsplash quota falls through to Openverse in `auto`
  mode with the fall-through named in the output, the output carries Unsplash's remaining
  quota, and a host that refuses HEAD is retried with a one-byte GET before a candidate is
  dropped.
  Rationale: the first acceptance run spent Unsplash's fifty-an-hour demo quota inside one
  build (sixteen searches, ten picks at two requests each) and the next build found both
  Unsplash and Openverse's anonymous tier closed; the library builder handled the 403 by hand.
  A pick now costs one request, a repeated query none, and the ladder descends on its own. A
  Flickr host answered the browser but refused HEAD, which would have dropped a good candidate.
  Date/Author: 2026-09-08, Claude.

- Decision: A credit may sit in the figure's caption or in one credits line per page, but it
  names every photographer with a link; "photographs via Unsplash" is not a credit. The audit
  checks the picked photographers' names against the page text.
  Rationale: the hardware build put ten product photographs in a grid where a caption per tile
  is noise, and credited them as "by their authors on Unsplash" — a placement problem the
  reference had not addressed, answered by a consolidated line that still meets the source's
  terms.
  Date/Author: 2026-09-08, Claude.

- Decision: One more disqualifier — a stranger presented as the product's own: an identifiable
  person from a stock source cast as this product's reader, patient or staff, and a child from
  a stock source in any role. Stock photographs carry the world; faces that belong to the
  product come from the project's assets.
  Rationale: the library build's hero is a Creative Commons snapshot of an identifiable child
  holding library books, cast as the programme's reader. Licence permits it; judgment should
  not. Neither reference names this; the memos' warning about staged people is the nearest.
  Date/Author: 2026-09-08, Claude.

## Surprises & Discoveries

- Observation: Every one of the three builds shipped photographs — rebate two, hardware ten,
  library two — and every photograph resolves, appears in the builder's saved search output, and
  carries alt, intrinsic size and a container colour; every record names the rung per slot. In
  the settling run the same three briefs shipped none. The rebate pair (a wall of battery
  cabinets; an installer at a service panel) and the hardware set (drill, hammer, chisels,
  fittings, a rack of old tools on whitewashed boards) are the product's world on sight.
  Evidence: `docs/research/scripts/imagery-check.mjs` over the three builds; the captures.

- Observation: Quota is the binding constraint, not the search. The hardware build alone spent
  thirty-six Unsplash requests; the library build, starting a few minutes later, found Unsplash
  at zero remaining and Openverse's anonymous tier closed after five searches, fell to Openverse
  for its two photographs, and recorded the fall in its §4. The ladder worked as designed and
  the cost showed: the Openverse hero is a casual Flickr snapshot of a child, a quality band
  and a subject the page around it does not deserve.
  Evidence: `library/images/search-1.json` (Unsplash, verified 2, no child-and-library
  subject), `search-6.json` (403 from Openverse), the library capture.

- Observation: The one clause that failed in the first run is placement, not sourcing: the
  hardware build named no photographer. The audit's first credit regex accepted any "Photo by …
  on Unsplash" line and would have passed a single token credit; it now checks every picked
  photographer's name against the page.
  Evidence: the hardware page's footer line; `imagery-check.mjs` before and after.

- Observation: A rate-limited search returns 403, not 429, from both services, so the
  fall-through keys on either.
  Evidence: the library build's saved error files.

- Observation: The Unsplash search results carry an `alt_description` and a dominant `color`
  per photo, which give the container colour and a draft alt for free; Openverse carries a
  ready attribution string. The script's common shape is mostly a rename.
  Evidence: the first live search, 1,415 results for "hardware store shelf".

## Deferred

- A role-aware locator for the settling instrument (the accent read), unrelated to this path but
  the same lesson: read the role, not the statistic.
- Unsplash production access (five thousand requests an hour) — the user's application; the
  demo tier bound inside one build.
- Pexels as a third keyed source, if production access is not granted.
- A library rebuild under 2.2.1, to see disqualifier 11 hold on the brief that produced it.
- The vitrea route: a photograph beneath a glass surface needs the backdrop hint measured from
  the image, which `references/material.md` already describes.

## Outcomes & Retrospective

Four builds — the three image-led briefs under 2.2.0 with the key present, then hardware again
under 2.2.1 — audited by `docs/research/scripts/imagery-check.mjs`; the audit and each build's
saved search and pick output are under `docs/research/data/2026-09-08-imagery-check/`.

- **A1 — met, four of four.** Every build ships photographs that resolve (rebate 2, hardware 10,
  library 2, hardware-2 2) and every record names the rung per slot. The same three briefs
  shipped none of the 52 settling builds' zero photographs.
- **A2 — met on three, not on the first hardware build.** Every image in every build carries
  alt text, intrinsic size and a container colour. The first hardware build credited ten
  photographs as "by their authors on Unsplash" with no names — a placement the reference had
  not addressed, now the credit rule and the audit's name check; the rebuild names both
  photographers in one footer line.
- **A3 — met, four of four.** No `src` was guessed: every remote URL appears in the builder's
  saved script output.
- **A4 — met, four of four.** No page error, no overflow, no placeholder.
- **A5 — met on three, partly on library.** Rebate: a wall of battery cabinets and an installer
  at a service panel, captioned. Hardware: a drill, hammer, chisels, brass fittings, a rack of
  old tools on whitewashed boards — the product's world, one photograph per featured item, which
  the brief's "featured tools" earns. Hardware-2: a stocked aisle as hero and rain running off a
  K-style gutter under the seasonal guide, the tools drawn as line plates. Library: the
  picture-book baskets pass; the hero is a casual Flickr snapshot of an identifiable child cast
  as the programme's reader, taken from the Openverse rung after Unsplash's quota was spent —
  permitted by licence, wrong by the judgment the reference now states (disqualifier 11).

**What the run settled.** The skill had the whole art direction for photographs and no way to
obtain one; with a way, fresh agents use it well on the first try — narrow queries, one pick
rejected on sight as the wrong country, credits and captions, and drawn artifacts where the
subject is an object. The costs are operational, not aesthetic: hourly quotas bind inside a
single build, and the free rung's editorial band is low enough that a stock child can land in
a hero. Both are now handled in the script and the reference, and the second is the one to
watch, because it is a judgment the licence does not make for you.

**Retrospective.** Reading the sources before designing paid twice: Unsplash's own guidelines
(download endpoint, UTM links, credit) shaped `pick`, and impeccable's "guessed ids 404" shaped
the verify step that made the never-guess rule mechanical. The audit's first credit check
would have passed a token line; checking each photographer's name against the page is the
right test and it found the miss. Cost: four builds at roughly 0.35 M tokens each, under the
declared budget with the rebuild.

## Revision Notes

- 2026-09-08: created from the user's question and the settling evidence; script, tests and the
  skill edits written; acceptance builds to follow.
- 2026-09-08 (second revision): three acceptance builds run; cache, quota fall-through, ranged
  GET, the credit placement rule and the people-from-stock disqualifier added (2.2.1); hardware
  rebuilt under 2.2.1 for the credit clause.
