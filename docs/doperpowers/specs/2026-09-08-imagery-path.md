# The imagery path

**Status:** in progress. **Follows** `2026-09-05-settling-experiment.md`, whose 52 builds showed
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

## Surprises & Discoveries

- Observation: The Unsplash search results carry an `alt_description` and a dominant `color`
  per photo, which give the container colour and a draft alt for free; Openverse carries a
  ready attribution string. The script's common shape is mostly a rename.
  Evidence: the first live search, 1,415 results for "hardware store shelf".

## Deferred

- A role-aware locator for the settling instrument (the accent read), unrelated to this path but
  the same lesson: read the role, not the statistic.
- Pexels as a third keyed source, if Unsplash's fifty-an-hour demo limit binds on a large build.
- The vitrea route: a photograph beneath a glass surface needs the backdrop hint measured from
  the image, which `references/material.md` already describes.

## Outcomes & Retrospective

Pending — written after the acceptance builds.

## Revision Notes

- 2026-09-08: created from the user's question and the settling evidence; script, tests and the
  skill edits written; acceptance builds to follow.
