# Materialist demos — the panel, the audit and the verdict

The pre-registered panel is astra-high, astra-medium, claude-opus, claude-sonnet. Missing or partial members keep every verdict provisional. Two counts of 25 print for every demo: the **panel-only** count (the 2.3 panel's pre-registered reading, comparable with its figures) and the **assigned** count (the panel on the 22 capture-visible rules, and r18, r19 and r23 from the audit and the source review, as the spec declared before any capture existed). The pass line uses the assigned count.

Raters: 4 (astra-high, astra-medium, claude-opus, claude-sonnet). Demos with a rule file: 6 of 6. Audits: 6 of 6. Source reviews: 6 of 6. Rules: 25, of which 8 are tagged [layer] or [material] and fatal to the verdict. Rules digest `fe05c2bd00c10c60…` (the 2.3 panel's).

| demo | raters | audit | source review |
|---|---|---|---|
| `music-player` | 4 | yes | yes |
| `transit-ops` | 4 | yes | yes |
| `photo-review` | 4 | yes | yes |
| `film-festival` | 4 | yes | yes |
| `park-trails` | 4 | yes | yes |
| `product-launch` | 4 | yes | yes |

- `astra-high` recorded the order park-trails → photo-review → transit-ops → film-festival → music-player → product-launch — the seeded shuffle for this rater.
- `astra-medium` recorded the order park-trails → transit-ops → film-festival → music-player → photo-review → product-launch — the seeded shuffle for this rater.
- `claude-opus` recorded the order photo-review → park-trails → music-player → film-festival → product-launch → transit-ops — the seeded shuffle for this rater.
- `claude-sonnet` recorded the order product-launch → transit-ops → park-trails → photo-review → music-player → film-festival — the seeded shuffle for this rater.

## The rule reading

Per rule and demo: the panel majority as `held (yes/n)`, a tie a failure, `—` unanswered; on r18, r19 and r23 the assigned reading follows after `→`, and that is the answer the assigned count uses.

| rule | tag | `music-player` | `transit-ops` | `photo-review` | `film-festival` | `park-trails` | `product-launch` |
|---|---|---|---|---|---|---|---|
| r1 | layer | 1 (3/4) | 1 (3/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) |
| r2 | layer | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) |
| r3 | layer | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) |
| r4 | material | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) |
| r5 | material | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) |
| r6 | material | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (3/4) | 1 (4/4) |
| r7 | material | 1 (3/4) | 1 (3/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) |
| r8 | geometry | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) |
| r9 | geometry | 1 (3/4) | 0 (2/4) | 1 (3/4) | 1 (4/4) | 1 (3/4) | 1 (4/4) |
| r10 | geometry | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) |
| r11 | grouping | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) |
| r12 | grouping | 1 (4/4) | 0 (0/4) | 0 (1/4) | 0 (1/4) | 1 (4/4) | 1 (4/4) |
| r13 | grouping | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) |
| r14 | grouping | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) |
| r15 | legibility | 0 (1/4) | 0 (1/4) | 0 (1/4) | 1 (3/4) | 0 (0/4) | 0 (0/4) |
| r16 | material | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (3/4) | 1 (4/4) |
| r17 | legibility | 1 (3/4) | 0 (2/4) | 0 (1/4) | 0 (2/4) | 1 (3/4) | 1 (3/4) |
| r18 | legibility | 1 (3/4) → 1 | 1 (3/4) → 1 | 1 (3/4) → 1 | 0 (2/4) → 1 | 1 (3/4) → 1 | 1 (3/4) → 1 |
| r19 | legibility | 0 (0/4) → 1 | 0 (1/4) → 1 | 0 (1/4) → 1 | 0 (1/4) → 1 | 0 (1/4) → 1 | 0 (0/4) → 1 |
| r20 | layout | 1 (3/4) | 1 (3/4) | 0 (0/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) |
| r21 | layout | 0 (2/4) | 0 (2/4) | 0 (0/4) | 0 (2/4) | 0 (2/4) | 0 (2/4) |
| r22 | layout | 0 (2/4) | 0 (1/4) | 1 (4/4) | 0 (2/4) | 1 (4/4) | 1 (4/4) |
| r23 | motion | 0 (1/4) → 1 | 0 (0/4) → 1 | 0 (1/4) → 1 | 0 (1/4) → 1 | 0 (1/4) → 1 | 0 (1/4) → 1 |
| r24 | colour | 1 (4/4) | 0 (0/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) |
| r25 | colour | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) | 1 (4/4) |

| demo | panel-only (of 25) | assigned (of 25) | unread in the assigned count |
|---|---|---|---|
| `music-player` | 20 | 22 | — |
| `transit-ops` | 16 | 18 | — |
| `photo-review` | 18 | 20 | — |
| `film-festival` | 18 | 21 | — |
| `park-trails` | 21 | 23 | — |
| `product-launch` | 21 | 23 | — |

### `music-player`

Raters: 4 (astra-high, astra-medium, claude-opus, claude-sonnet). Panel-only: **20 of 25**. Assigned: **22 of 25**. No fatal-tag failure in available answers.

The assigned readings, with the panel's answers beside them:

| rule | assigned | panel | on |
|---|---|---|---|
| r18 | 1 | 1 (3/4) | light 20/20 on glass, min 6.36 (DOM sample 55/55); dark 20/20 on glass, min 4.74 (DOM sample 55/55) |
| r19 | 1 | 0 (0/4) | method page-switch; reduced ran=yes, reduced no page error=yes, reduced policy as asked=yes, reduced material moved=yes, increasedContrast ran=yes, increasedContrast no page error=yes, increasedContrast policy as asked=yes, reducedMotion ran=yes, reducedMotion no page error=yes, reducedMotion policy as asked=yes, forcedColors ran=yes, forcedColors no page error=yes, forcedColors policy as asked=yes, forced colours draw no glass=yes |
| r23 | 1 | 0 (1/4) | Post-fix source (reviewer-medium, 2026-09-27): (a) the playlist menu arrives through GlassMorph (Queue.tsx:120-143), no opacity transition; (b) every interactive glass host carries the runtime's press through the channel properties (Controls.tsx:39-42) and no colour-swap press remains anywhere; plai |

Capture-visible rules that failed:

| rule | tag | yes/n | a rater that said no | its evidence |
|---|---|---|---|---|
| r15 | legibility | 1/4 | astra-high | Light and dark: no scroll-edge effect is visible around the bottom transport or queue region. |
| r21 | layout | 2/4 | astra-medium | Lower controls overlay artwork without demonstrated safe-area clearing or sidebar extension in either scheme. |
| r22 | layout | 2/4 | astra-high | Light and dark: the Playing Next sheet uses a solid custom-looking background with a visible enclosing edge. |

Mechanical read: root reachable; 3 surface(s); page errors 0; diagnostics 0; ban-subset findings 0; colour scheme followed: light=True, dark=True.

Verdict, clause by clause:

| clause | met | on |
|---|---|---|
| four-rater panel complete | yes | all 25 rules answered |
| assigned readings present | yes | r18, r19, r23 read |
| at least 22 of 25 held (assigned count) | yes | 22 of 25 held |
| no [layer] or [material] rule fails | yes | none failed in available answers |
| zero diagnostics, either channel | yes | none |
| zero ban-subset findings | yes | none |
| works with transparency reduced | yes | method page-switch; policyAsAsked=True; materialMoved=True; errors=[] |

**music-player: PASSES**

### `transit-ops`

Raters: 4 (astra-high, astra-medium, claude-opus, claude-sonnet). Panel-only: **16 of 25**. Assigned: **18 of 25**. No fatal-tag failure in available answers.

The assigned readings, with the panel's answers beside them:

| rule | assigned | panel | on |
|---|---|---|---|
| r18 | 1 | 1 (3/4) | light 31/31 on glass, min 5.4 (DOM sample 45/45); dark 31/31 on glass, min 6.86 (DOM sample 45/45) |
| r19 | 1 | 0 (1/4) | method page-switch; reduced ran=yes, reduced no page error=yes, reduced policy as asked=yes, reduced material moved=yes, increasedContrast ran=yes, increasedContrast no page error=yes, increasedContrast policy as asked=yes, reducedMotion ran=yes, reducedMotion no page error=yes, reducedMotion policy as asked=yes, forcedColors ran=yes, forcedColors no page error=yes, forcedColors policy as asked=yes, forced colours draw no glass=yes |
| r23 | 1 | 0 (0/4) | Post-fix source (reviewer-medium, 2026-09-27) plus the fix worker's browser check of the three follow-ups: (a) both transient hosts arrive through present (Chrome.tsx:364, 690), no opacity transition; (b) every interactive glass host carries the runtime's press through the channel properties, the ac |

Capture-visible rules that failed:

| rule | tag | yes/n | a rater that said no | its evidence |
|---|---|---|---|---|
| r9 | geometry | 2/4 | astra-high | Light and dark selected-vehicle views: capsule action fills flare inside a much squarer outer action bar. |
| r12 | grouping | 0/4 | astra-high | Light and dark selected-vehicle views: the icon-only close action shares glass with Call operator, Hold and Follow. |
| r15 | legibility | 1/4 | astra-high | Light and dark: the map meets floating controls without any visible scroll-edge treatment. |
| r17 | legibility | 2/4 | astra-high | Light and dark resting views: street-grid content continues directly underneath the top filter and search controls. |
| r21 | layout | 2/4 | astra-medium | Left alert sidebar forms a hard solid boundary over the map, not a visible background extension, in both schemes. |
| r22 | layout | 1/4 | astra-high | Light and dark selected-vehicle views: the large information platter has an opaque custom-looking sheet background and outline. |
| r24 | colour | 0/4 | astra-high | Light and dark: saturated route-identification dots appear inside the top control bar, not solely in map content. |

Mechanical read: root reachable; 6 surface(s); page errors 0; diagnostics 0; ban-subset findings 0; colour scheme followed: light=True, dark=True.

Verdict, clause by clause:

| clause | met | on |
|---|---|---|
| four-rater panel complete | yes | all 25 rules answered |
| assigned readings present | yes | r18, r19, r23 read |
| at least 22 of 25 held (assigned count) | no | 18 of 25 held |
| no [layer] or [material] rule fails | yes | none failed in available answers |
| zero diagnostics, either channel | yes | none |
| zero ban-subset findings | yes | none |
| works with transparency reduced | yes | method page-switch; policyAsAsked=True; materialMoved=True; errors=[] |

**transit-ops: FAILS**

### `photo-review`

Raters: 4 (astra-high, astra-medium, claude-opus, claude-sonnet). Panel-only: **18 of 25**. Assigned: **20 of 25**. No fatal-tag failure in available answers.

The assigned readings, with the panel's answers beside them:

| rule | assigned | panel | on |
|---|---|---|---|
| r18 | 1 | 1 (3/4) | light 14/14 on glass, min 11.17 (DOM sample 75/75); dark 14/14 on glass, min 8.08 (DOM sample 75/75) |
| r19 | 1 | 0 (1/4) | method page-switch; reduced ran=yes, reduced no page error=yes, reduced policy as asked=yes, reduced material moved=yes, increasedContrast ran=yes, increasedContrast no page error=yes, increasedContrast policy as asked=yes, reducedMotion ran=yes, reducedMotion no page error=yes, reducedMotion policy as asked=yes, forcedColors ran=yes, forcedColors no page error=yes, forcedColors policy as asked=yes, forced colours draw no glass=yes |
| r23 | 1 | 0 (1/4) | Post-fix source (reviewer-medium, 2026-09-27): (a) the platter arrives through GlassMorph (Controls.tsx:88-132), no opacity transition; (b) press is written through the runtime's channel properties on every interactive host AND on the open platter, whose plain controls drive --vitrea-press, --vitrea |

Capture-visible rules that failed:

| rule | tag | yes/n | a rater that said no | its evidence |
|---|---|---|---|---|
| r12 | grouping | 1/4 | astra-high | Light and dark crop views: Reset and Done text buttons share the platter with the sun, thermometer and crop icon buttons. |
| r15 | legibility | 1/4 | astra-high | Light and dark: no scroll-edge equivalent is visible around the floating controls or filmstrip. |
| r17 | legibility | 1/4 | astra-high | Light and dark resting views: the compare and tool controls cover parts of the actual photograph being reviewed. |
| r20 | layout | 0/4 | astra-high | Light and dark: the photograph ends at hard margins beside opaque metadata rails instead of reaching the window edges. |
| r21 | layout | 0/4 | astra-high | Light and dark: the image meets the side rails at hard rectangular edges without a background extension. |

Mechanical read: root reachable; 3 surface(s); page errors 0; diagnostics 0; ban-subset findings 0; colour scheme followed: light=True, dark=True.

Verdict, clause by clause:

| clause | met | on |
|---|---|---|
| four-rater panel complete | yes | all 25 rules answered |
| assigned readings present | yes | r18, r19, r23 read |
| at least 22 of 25 held (assigned count) | no | 20 of 25 held |
| no [layer] or [material] rule fails | yes | none failed in available answers |
| zero diagnostics, either channel | yes | none |
| zero ban-subset findings | yes | none |
| works with transparency reduced | yes | method page-switch; policyAsAsked=True; materialMoved=True; errors=[] |

**photo-review: FAILS**

### `film-festival`

Raters: 4 (astra-high, astra-medium, claude-opus, claude-sonnet). Panel-only: **18 of 25**. Assigned: **21 of 25**. No fatal-tag failure in available answers.

The assigned readings, with the panel's answers beside them:

| rule | assigned | panel | on |
|---|---|---|---|
| r18 | 1 | 0 (2/4) | light 52/52 on glass, min 6.2 (DOM sample 180/182); dark 52/52 on glass, min 4.64 (DOM sample 179/182) |
| r19 | 1 | 0 (1/4) | method page-switch; reduced ran=yes, reduced no page error=yes, reduced policy as asked=yes, reduced material moved=yes, increasedContrast ran=yes, increasedContrast no page error=yes, increasedContrast policy as asked=yes, reducedMotion ran=yes, reducedMotion no page error=yes, reducedMotion policy as asked=yes, forcedColors ran=yes, forcedColors no page error=yes, forcedColors policy as asked=yes, forced colours draw no glass=yes |
| r23 | 1 | 0 (1/4) | Post-fix source (reviewer-medium, 2026-09-27): (a) the Tickets platter arrives through GlassMorph (Bar.tsx:139-178), no opacity transition; (b) every interactive glass host carries the runtime's press through the channel properties (interaction.ts:222-230) and no colour-swap press exists; plain butt |

Capture-visible rules that failed:

| rule | tag | yes/n | a rater that said no | its evidence |
|---|---|---|---|---|
| r12 | grouping | 1/4 | astra-high | Light and dark ticket menus: the close icon shares the same glass background as the ticket-choice text buttons. |
| r17 | legibility | 2/4 | astra-medium | The opening still sits directly under top controls at rest in both schemes. |
| r21 | layout | 2/4 | astra-medium | Scrolled tiles visibly carry programme and film content into the top bar region rather than showing clear safe-area separation. |
| r22 | layout | 2/4 | astra-high | Light and dark scrolled tiles: a persistent photographic backing band is placed beneath the bars above the scrolling sheet. |

Mechanical read: root reachable; 3 surface(s); page errors 0; diagnostics 0; ban-subset findings 0; colour scheme followed: light=True, dark=True.

Verdict, clause by clause:

| clause | met | on |
|---|---|---|
| four-rater panel complete | yes | all 25 rules answered |
| assigned readings present | yes | r18, r19, r23 read |
| at least 22 of 25 held (assigned count) | no | 21 of 25 held |
| no [layer] or [material] rule fails | yes | none failed in available answers |
| zero diagnostics, either channel | yes | none |
| zero ban-subset findings | yes | none |
| works with transparency reduced | yes | method page-switch; policyAsAsked=True; materialMoved=True; errors=[] |

**film-festival: FAILS**

### `park-trails`

Raters: 4 (astra-high, astra-medium, claude-opus, claude-sonnet). Panel-only: **21 of 25**. Assigned: **23 of 25**. No fatal-tag failure in available answers.

The assigned readings, with the panel's answers beside them:

| rule | assigned | panel | on |
|---|---|---|---|
| r18 | 1 | 1 (3/4) | light 68/68 on glass, min 8.7 (DOM sample 269/274); dark 68/68 on glass, min 4.59 (DOM sample 274/274) |
| r19 | 1 | 0 (1/4) | method page-switch; reduced ran=yes, reduced no page error=yes, reduced policy as asked=yes, reduced material moved=yes, increasedContrast ran=yes, increasedContrast no page error=yes, increasedContrast policy as asked=yes, reducedMotion ran=yes, reducedMotion no page error=yes, reducedMotion policy as asked=yes, forcedColors ran=yes, forcedColors no page error=yes, forcedColors policy as asked=yes, forced colours draw no glass=yes |
| r23 | 1 | 0 (1/4) | Post-fix source (reviewer-medium, 2026-09-27): (a) the sole platter is a GlassMorph (Planner.tsx:211-218), no opacity transition; (b) every interactive glass host carries the runtime's press through the channel properties (interaction.ts:222-230) and no colour-swap press exists; plain rows inside th |

Capture-visible rules that failed:

| rule | tag | yes/n | a rater that said no | its evidence |
|---|---|---|---|---|
| r15 | legibility | 0/4 | astra-high | Light and dark full captures: no scrolled state or scroll-edge treatment beneath the top planner is visible. |
| r21 | layout | 2/4 | astra-high | Light and dark full captures stop at the introduction, leaving clearance of the scrolling trail content unshown. |

Mechanical read: root reachable; 3 surface(s); page errors 0; diagnostics 0; ban-subset findings 0; colour scheme followed: light=True, dark=True.

Verdict, clause by clause:

| clause | met | on |
|---|---|---|
| four-rater panel complete | yes | all 25 rules answered |
| assigned readings present | yes | r18, r19, r23 read |
| at least 22 of 25 held (assigned count) | yes | 23 of 25 held |
| no [layer] or [material] rule fails | yes | none failed in available answers |
| zero diagnostics, either channel | yes | none |
| zero ban-subset findings | yes | none |
| works with transparency reduced | yes | method page-switch; policyAsAsked=True; materialMoved=True; errors=[] |

**park-trails: PASSES**

### `product-launch`

Raters: 4 (astra-high, astra-medium, claude-opus, claude-sonnet). Panel-only: **21 of 25**. Assigned: **23 of 25**. No fatal-tag failure in available answers.

The assigned readings, with the panel's answers beside them:

| rule | assigned | panel | on |
|---|---|---|---|
| r18 | 1 | 1 (3/4) | light 25/25 on glass, min 11.21 (DOM sample 180/180); dark 25/25 on glass, min 6.67 (DOM sample 180/180) |
| r19 | 1 | 0 (0/4) | method page-switch; reduced ran=yes, reduced no page error=yes, reduced policy as asked=yes, reduced material moved=yes, increasedContrast ran=yes, increasedContrast no page error=yes, increasedContrast policy as asked=yes, reducedMotion ran=yes, reducedMotion no page error=yes, reducedMotion policy as asked=yes, forcedColors ran=yes, forcedColors no page error=yes, forcedColors policy as asked=yes, forced colours draw no glass=yes |
| r23 | 1 | 0 (1/4) | Post-fix source (reviewer-medium, 2026-09-27): (a) the lens platter arrives through GlassMorph (LensMenu.tsx:233-246), no opacity transition; (b) every interactive glass host carries the runtime's press through the channel properties (interaction.ts:222-230), the navigation now opted in (Chrome.tsx: |

Capture-visible rules that failed:

| rule | tag | yes/n | a rater that said no | its evidence |
|---|---|---|---|---|
| r15 | legibility | 0/4 | astra-high | Light and dark full captures show only the hero, with no visible scroll-edge treatment at either floating bar. |
| r21 | layout | 2/4 | astra-high | Light and dark full captures contain no sensor, lens or price sections, so scrolling content clearance of the bottom bar is not shown. |

Mechanical read: root reachable; 5 surface(s); page errors 0; diagnostics 0; ban-subset findings 0; colour scheme followed: light=True, dark=True.

Verdict, clause by clause:

| clause | met | on |
|---|---|---|
| four-rater panel complete | yes | all 25 rules answered |
| assigned readings present | yes | r18, r19, r23 read |
| at least 22 of 25 held (assigned count) | yes | 23 of 25 held |
| no [layer] or [material] rule fails | yes | none failed in available answers |
| zero diagnostics, either channel | yes | none |
| zero ban-subset findings | yes | none |
| works with transparency reduced | yes | method page-switch; policyAsAsked=True; materialMoved=True; errors=[] |

**product-launch: PASSES**

## Agreement per rule (Krippendorff's α, nominal)

The units are the demos and the observations are the panel's 0/1 answers, so each α below stands on at most 6 unit(s) — far fewer than a reliability claim wants, and the column saying how many is part of the reading. A rule the panel answered the same way on every demo has no variation for chance to explain: its α is 1.0 by construction and is marked constant.

| rule | tag | α | demos with ≥ 2 raters | values used | note |
|---|---|---|---|---|---|
| r1 | layer | -0.05 | 6 | 0, 1 |  |
| r2 | layer | 1.00 | 6 | 1 | constant at 1 |
| r3 | layer | 1.00 | 6 | 1 | constant at 1 |
| r4 | material | 1.00 | 6 | 1 | constant at 1 |
| r5 | material | 1.00 | 6 | 1 | constant at 1 |
| r6 | material | 0.00 | 6 | 0, 1 |  |
| r7 | material | -0.05 | 6 | 0, 1 |  |
| r8 | geometry | 1.00 | 6 | 1 | constant at 1 |
| r9 | geometry | -0.05 | 6 | 0, 1 |  |
| r10 | geometry | 1.00 | 6 | 1 | constant at 1 |
| r11 | grouping | 1.00 | 6 | 1 | constant at 1 |
| r12 | grouping | 0.67 | 6 | 0, 1 |  |
| r13 | grouping | 1.00 | 6 | 1 | constant at 1 |
| r14 | grouping | 1.00 | 6 | 1 | constant at 1 |
| r15 | legibility | 0.15 | 6 | 0, 1 |  |
| r16 | material | 0.00 | 6 | 0, 1 |  |
| r17 | legibility | -0.10 | 6 | 0, 1 |  |
| r18 | legibility | -0.22 | 6 | 0, 1 |  |
| r19 | legibility | -0.15 | 6 | 0, 1 |  |
| r20 | layout | 0.57 | 6 | 0, 1 |  |
| r21 | layout | -0.10 | 6 | 0, 1 |  |
| r22 | layout | 0.29 | 6 | 0, 1 |  |
| r23 | motion | -0.21 | 6 | 0, 1 |  |
| r24 | colour | 1.00 | 6 | 0, 1 |  |
| r25 | colour | 1.00 | 6 | 1 | constant at 1 |

## The line

**3 of 6 demos pass** (`music-player`, `park-trails`, `product-launch`). The initiative meets its purpose when all six pass. The stop condition (three or more demos failing a [layer] or [material] rule) is not met on the evidence so far (0). The user's eye (reading 4) is not in this report.
