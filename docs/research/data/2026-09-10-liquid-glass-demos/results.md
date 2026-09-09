# Liquid Glass demos — the panel's rule reading

The pre-registered panel is astra-medium, astra-high, claude-opus, claude-sonnet. Missing or partial members keep acceptance provisional; rule answers are never replaced by audit checks.

Raters: 3 (astra-medium, astra-high, claude-sonnet). Demos with a rule file: 6 of 6. Demos with an audit.json: 6 of 6. Rules: 25, of which 8 are tagged [layer] or [material] and fatal to the verdict.

The panel per demo, and the demo order each rater recorded:

| demo | raters with rules | raters with quality | audit.json |
|---|---|---|---|
| `music-player` | 3 | 3 | yes |
| `transit-ops` | 3 | 3 | yes |
| `photo-review` | 3 | 3 | yes |
| `film-festival` | 3 | 3 | yes |
| `park-trails` | 3 | 3 | yes |
| `product-launch` | 3 | 3 | yes |

- `astra-medium` recorded the order park-trails → transit-ops → film-festival → music-player → photo-review → product-launch — the seeded shuffle for this rater.
- `astra-high` recorded the order park-trails → photo-review → transit-ops → film-festival → music-player → product-launch — the seeded shuffle for this rater.
- `claude-sonnet` recorded the order product-launch → transit-ops → park-trails → photo-review → music-player → film-festival — the seeded shuffle for this rater.

## The rule reading

The panel majority per rule, as `held (yes/n)`; a tie is a failure. This table stands on 3 rater(s); a rule no rater answered on a demo reads `—`.

| rule | tag | `music-player` | `transit-ops` | `photo-review` | `film-festival` | `park-trails` | `product-launch` |
|---|---|---|---|---|---|---|---|
| r1 | layer | 0 (1/3) | 0 (0/3) | 1 (3/3) | 1 (3/3) | 1 (2/3) | 1 (3/3) |
| r2 | layer | 0 (1/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) |
| r3 | layer | 1 (3/3) | 1 (2/3) | 1 (3/3) | 1 (2/3) | 1 (3/3) | 1 (2/3) |
| r4 | material | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) |
| r5 | material | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) |
| r6 | material | 1 (2/3) | 1 (2/3) | 1 (3/3) | 1 (3/3) | 0 (1/3) | 1 (2/3) |
| r7 | material | 1 (3/3) | 1 (3/3) | 1 (2/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) |
| r8 | geometry | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) |
| r9 | geometry | 0 (1/3) | 1 (2/3) | 1 (3/3) | 1 (3/3) | 0 (1/3) | 1 (2/3) |
| r10 | geometry | 1 (3/3) | 1 (2/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (2/3) |
| r11 | grouping | 1 (3/3) | 1 (3/3) | 1 (3/3) | 0 (0/3) | 1 (3/3) | 1 (3/3) |
| r12 | grouping | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) |
| r13 | grouping | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) |
| r14 | grouping | 0 (1/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) |
| r15 | legibility | 0 (1/3) | 0 (0/3) | 0 (1/3) | 1 (2/3) | 1 (2/3) | 0 (0/3) |
| r16 | material | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (2/3) | 1 (2/3) | 0 (0/3) |
| r17 | legibility | 1 (2/3) | 0 (1/3) | 0 (1/3) | 1 (2/3) | 1 (2/3) | 0 (1/3) |
| r18 | legibility | 0 (1/3) | 0 (1/3) | 0 (1/3) | 0 (1/3) | 0 (1/3) | 0 (1/3) |
| r19 | legibility | 0 (1/3) | 0 (1/3) | 0 (1/3) | 0 (1/3) | 0 (1/3) | 0 (1/3) |
| r20 | layout | 1 (3/3) | 1 (3/3) | 0 (0/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) |
| r21 | layout | 1 (2/3) | 0 (1/3) | 0 (0/3) | 1 (3/3) | 1 (3/3) | 0 (1/3) |
| r22 | layout | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (2/3) | 1 (2/3) | 1 (3/3) |
| r23 | motion | 0 (0/3) | 0 (0/3) | 0 (0/3) | 0 (0/3) | 0 (0/3) | 0 (0/3) |
| r24 | colour | 0 (1/3) | 0 (1/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (2/3) |
| r25 | colour | 1 (2/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) | 1 (3/3) |

### `music-player`

Raters: 3 (astra-medium, astra-high, claude-sonnet). Held: **16 of 25** by panel majority (provisional; panel incomplete). Fatal-tag failures: **r1, r2**.

Rules that failed:

| rule | tag | yes/n | a rater that said no | its evidence |
|---|---|---|---|---|
| r1 | layer | 1/3 | astra-medium | The Up next track list and its artwork sit on a large glass content panel. |
| r2 | layer | 1/3 | astra-medium | The playlist menu is a glass popover drawn directly over the glass queue panel. |
| r9 | geometry | 1/3 | astra-medium | The nearly edge-to-edge selected playlist row has corners that do not follow the outer menu arcs. |
| r14 | grouping | 1/3 | astra-medium | The nearby queue and playlist menu read as two superimposed glass materials rather than one container. |
| r15 | legibility | 1/3 | astra-high | No scroll-edge treatment is visible for the queue or album region beneath floating controls. |
| r18 | legibility | 1/3 | astra-medium | The light transport text is legible, but no dark-state capture verifies the required contrast in both modes. |
| r19 | legibility | 1/3 | astra-medium | The reduced-transparency transport and queue remain usable, but increased contrast and reduced motion are not shown. |
| r23 | motion | 0/3 | astra-medium | The playlist-menu still cannot establish opening morphs or pointer-local press feedback. |
| r24 | colour | 1/3 | astra-medium | The transport scrubber carries a saturated red progress line in the control layer. |

Frozen mechanical facts (null means unrecorded):

```json
{
  "error": null,
  "errors": [],
  "consoleErrors": [],
  "failedRequests": 0,
  "overflowCapture": false,
  "gateMechanical": true,
  "rootFound": true,
  "surfaces": 4,
  "groups": [
    {
      "id": "transport",
      "members": 2,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "analysis": "exact",
      "refraction": "true",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    },
    {
      "id": "queue",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "analysis": "exact",
      "refraction": "true",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    },
    {
      "id": "menu",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "analysis": "exact",
      "refraction": "true",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    }
  ],
  "diagnostics": [],
  "menu": "captured",
  "menuGroups": [
    {
      "id": "transport",
      "members": 2,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "health": "ok"
    },
    {
      "id": "queue",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "health": "ok"
    },
    {
      "id": "menu",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "health": "ok"
    }
  ],
  "menuDiagnostics": [],
  "colorScheme": "light",
  "contrast": {
    "checked": 68,
    "pass": 68,
    "unknown": 0,
    "rate": 1,
    "onGlass": 37,
    "onGlassPass": 37,
    "fails": []
  },
  "reduced": {
    "rootFound": true,
    "errors": [],
    "reducedMotionEmulated": true,
    "overrideHonoured": true,
    "materialMoved": true,
    "material": {
      "glass": "material",
      "colorSource": "material",
      "frost": "increased",
      "refraction": "reduced",
      "occlusion": "increased",
      "border": "nominal",
      "ambientTint": "nominal",
      "foreground": "adaptive"
    },
    "motion": {
      "overshoot": "none",
      "deformation": "none",
      "shimmer": "none",
      "morph": "non-elastic",
      "crossfade": "large-plane-shifts",
      "positionalContinuity": true
    },
    "groups": [
      {
        "id": "transport",
        "renderer": "webgpu",
        "refraction": "true",
        "cssBody": null
      },
      {
        "id": "queue",
        "renderer": "webgpu",
        "refraction": "true",
        "cssBody": null
      },
      {
        "id": "menu",
        "renderer": "webgpu",
        "refraction": "true",
        "cssBody": null
      }
    ],
    "reducedTransparencyUndetectable": false,
    "ok": true
  }
}
```

Evidence limits: r18 requires contrast in both schemes; the audit samples only the recorded scheme. r19 requires all three accessibility modes; reduced motion emulation and a reduced-transparency runtime smoke check do not establish full accessibility, and increased contrast is not tested. r23 requires motion evidence absent from static captures. These gaps do not replace panel zeros with passes or remove rules from 25.

Verdict, clause by clause:

| clause | met | on |
|---|---|---|
| four-rater panel complete | not yet readable | missing/partial: claude-opus |
| at least 22 of 25 held | not yet readable | 16 of 25 held (provisional) |
| no [layer] or [material] rule fails | not yet readable | r1, r2 |
| no group diagnostic | yes | rest=[]; menu=[] |
| works with transparency reduced | yes | reduced ok=True; overrideHonoured=True; materialMoved=True; errors=[]; runtime smoke check only, not full accessibility |

**music-player: no final verdict — incomplete evidence; provisional reading above**

### `transit-ops`

Raters: 3 (astra-medium, astra-high, claude-sonnet). Held: **17 of 25** by panel majority (provisional; panel incomplete). Fatal-tag failures: **r1**.

Rules that failed:

| rule | tag | yes/n | a rater that said no | its evidence |
|---|---|---|---|---|
| r1 | layer | 0/3 | astra-medium | The entire Active alerts content list sits on a frosted glass sidebar. |
| r15 | legibility | 0/3 | astra-medium | Alert cards clip beneath the Active alerts header and at the sidebar bottom without a visible scroll-edge treatment. |
| r17 | legibility | 1/3 | astra-medium | Vehicles and route lines run beneath the resting alert sidebar and the selected-vehicle platter. |
| r18 | legibility | 1/3 | astra-medium | The pale map controls are readable, but no dark capture establishes both-mode contrast ratios. |
| r19 | legibility | 1/3 | astra-medium | The reduced-transparency sidebar is usable, but increased-contrast and reduced-motion states are not demonstrated. |
| r21 | layout | 1/3 | astra-medium | Route lines and vehicle markers disappear beneath the sidebar without a visible safe-area or background-extension equivalent. |
| r23 | motion | 0/3 | astra-medium | The selected-vehicle still shows placement but no morph or pointer-local press animation. |
| r24 | colour | 1/3 | astra-medium | The floating status filter contains blue, amber and red marks instead of monochrome control content. |

Frozen mechanical facts (null means unrecorded):

```json
{
  "error": null,
  "errors": [],
  "consoleErrors": [],
  "failedRequests": 0,
  "overflowCapture": false,
  "gateMechanical": true,
  "rootFound": true,
  "surfaces": 6,
  "groups": [
    {
      "id": "routes",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "analysis": "exact",
      "refraction": "true",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    },
    {
      "id": "state",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "analysis": "exact",
      "refraction": "true",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    },
    {
      "id": "find",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "analysis": "exact",
      "refraction": "true",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    },
    {
      "id": "view",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "analysis": "exact",
      "refraction": "true",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    },
    {
      "id": "alerts",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "analysis": "exact",
      "refraction": "true",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    },
    {
      "id": "platter",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "analysis": "exact",
      "refraction": "true",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    }
  ],
  "diagnostics": [],
  "menu": "captured",
  "menuGroups": [
    {
      "id": "routes",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "health": "ok"
    },
    {
      "id": "state",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "health": "ok"
    },
    {
      "id": "find",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "health": "ok"
    },
    {
      "id": "view",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "health": "ok"
    },
    {
      "id": "alerts",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "health": "ok"
    },
    {
      "id": "platter",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "health": "ok"
    }
  ],
  "menuDiagnostics": [],
  "colorScheme": "light",
  "contrast": {
    "checked": 107,
    "pass": 107,
    "unknown": 0,
    "rate": 1,
    "onGlass": 62,
    "onGlassPass": 62,
    "fails": []
  },
  "reduced": {
    "rootFound": true,
    "errors": [],
    "reducedMotionEmulated": true,
    "overrideHonoured": true,
    "materialMoved": true,
    "material": {
      "glass": "material",
      "colorSource": "material",
      "frost": "increased",
      "refraction": "reduced",
      "occlusion": "increased",
      "border": "nominal",
      "ambientTint": "nominal",
      "foreground": "adaptive"
    },
    "motion": {
      "overshoot": "none",
      "deformation": "none",
      "shimmer": "none",
      "morph": "non-elastic",
      "crossfade": "large-plane-shifts",
      "positionalContinuity": true
    },
    "groups": [
      {
        "id": "routes",
        "renderer": "webgpu",
        "refraction": "true",
        "cssBody": null
      },
      {
        "id": "state",
        "renderer": "webgpu",
        "refraction": "true",
        "cssBody": null
      },
      {
        "id": "find",
        "renderer": "webgpu",
        "refraction": "true",
        "cssBody": null
      },
      {
        "id": "view",
        "renderer": "webgpu",
        "refraction": "true",
        "cssBody": null
      },
      {
        "id": "alerts",
        "renderer": "webgpu",
        "refraction": "true",
        "cssBody": null
      },
      {
        "id": "platter",
        "renderer": "webgpu",
        "refraction": "true",
        "cssBody": null
      }
    ],
    "reducedTransparencyUndetectable": false,
    "ok": true
  }
}
```

Evidence limits: r18 requires contrast in both schemes; the audit samples only the recorded scheme. r19 requires all three accessibility modes; reduced motion emulation and a reduced-transparency runtime smoke check do not establish full accessibility, and increased contrast is not tested. r23 requires motion evidence absent from static captures. These gaps do not replace panel zeros with passes or remove rules from 25.

Verdict, clause by clause:

| clause | met | on |
|---|---|---|
| four-rater panel complete | not yet readable | missing/partial: claude-opus |
| at least 22 of 25 held | not yet readable | 17 of 25 held (provisional) |
| no [layer] or [material] rule fails | not yet readable | r1 |
| no group diagnostic | yes | rest=[]; menu=[] |
| works with transparency reduced | yes | reduced ok=True; overrideHonoured=True; materialMoved=True; errors=[]; runtime smoke check only, not full accessibility |

**transit-ops: no final verdict — incomplete evidence; provisional reading above**

### `photo-review`

Raters: 3 (astra-medium, astra-high, claude-sonnet). Held: **18 of 25** by panel majority (provisional; panel incomplete). No fatal-tag failure in available answers.

Rules that failed:

| rule | tag | yes/n | a rater that said no | its evidence |
|---|---|---|---|---|
| r15 | legibility | 1/3 | astra-high | No scroll-edge treatment is visible at the photo-stage controls or filmstrip boundary. |
| r17 | legibility | 1/3 | astra-medium | The expanded exposure palette covers the photographed tool and glowing workpiece in the resting menu capture. |
| r18 | legibility | 1/3 | astra-medium | The dark palette text is legible, but there is no light-mode capture establishing both-mode contrast ratios. |
| r19 | legibility | 1/3 | astra-medium | The reduced-transparency controls remain visible, but increased-contrast and reduced-motion behavior is not captured. |
| r20 | layout | 0/3 | astra-medium | The selected photograph is inset in a dark stage beside a hard-edged metadata sidebar rather than reaching the window edges. |
| r21 | layout | 0/3 | astra-medium | The photograph stops at a rectangular stage edge before the sidebar, with no visible background extension behind it. |
| r23 | motion | 0/3 | astra-medium | The exposure still suggests an expanded control but does not demonstrate morph timing or pointer-local press feedback. |

Frozen mechanical facts (null means unrecorded):

```json
{
  "error": null,
  "errors": [],
  "consoleErrors": [],
  "failedRequests": 0,
  "overflowCapture": false,
  "gateMechanical": true,
  "rootFound": true,
  "surfaces": 3,
  "groups": [
    {
      "id": "view",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "analysis": "exact",
      "refraction": "true",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    },
    {
      "id": "tools",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "analysis": "exact",
      "refraction": "true",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    },
    {
      "id": "verdict",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "analysis": "exact",
      "refraction": "true",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    }
  ],
  "diagnostics": [],
  "menu": "captured",
  "menuGroups": [
    {
      "id": "view",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "health": "ok"
    },
    {
      "id": "tools",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "health": "ok"
    },
    {
      "id": "verdict",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "health": "ok"
    }
  ],
  "menuDiagnostics": [],
  "colorScheme": "dark",
  "contrast": {
    "checked": 106,
    "pass": 106,
    "unknown": 0,
    "rate": 1,
    "onGlass": 5,
    "onGlassPass": 5,
    "fails": []
  },
  "reduced": {
    "rootFound": true,
    "errors": [],
    "reducedMotionEmulated": true,
    "overrideHonoured": true,
    "materialMoved": true,
    "material": {
      "glass": "material",
      "colorSource": "material",
      "frost": "increased",
      "refraction": "reduced",
      "occlusion": "increased",
      "border": "nominal",
      "ambientTint": "nominal",
      "foreground": "adaptive"
    },
    "motion": {
      "overshoot": "none",
      "deformation": "none",
      "shimmer": "none",
      "morph": "non-elastic",
      "crossfade": "large-plane-shifts",
      "positionalContinuity": true
    },
    "groups": [
      {
        "id": "view",
        "renderer": "webgpu",
        "refraction": "true",
        "cssBody": null
      },
      {
        "id": "tools",
        "renderer": "webgpu",
        "refraction": "true",
        "cssBody": null
      },
      {
        "id": "verdict",
        "renderer": "webgpu",
        "refraction": "true",
        "cssBody": null
      }
    ],
    "reducedTransparencyUndetectable": false,
    "ok": true
  }
}
```

Evidence limits: r18 requires contrast in both schemes; the audit samples only the recorded scheme. r19 requires all three accessibility modes; reduced motion emulation and a reduced-transparency runtime smoke check do not establish full accessibility, and increased contrast is not tested. r23 requires motion evidence absent from static captures. These gaps do not replace panel zeros with passes or remove rules from 25.

Verdict, clause by clause:

| clause | met | on |
|---|---|---|
| four-rater panel complete | not yet readable | missing/partial: claude-opus |
| at least 22 of 25 held | not yet readable | 18 of 25 held (provisional) |
| no [layer] or [material] rule fails | not yet readable | none failed in available answers |
| no group diagnostic | yes | rest=[]; menu=[] |
| works with transparency reduced | yes | reduced ok=True; overrideHonoured=True; materialMoved=True; errors=[]; runtime smoke check only, not full accessibility |

**photo-review: no final verdict — incomplete evidence; provisional reading above**

### `film-festival`

Raters: 3 (astra-medium, astra-high, claude-sonnet). Held: **21 of 25** by panel majority (provisional; panel incomplete). No fatal-tag failure in available answers.

Rules that failed:

| rule | tag | yes/n | a rater that said no | its evidence |
|---|---|---|---|---|
| r11 | grouping | 0/3 | astra-medium | Navigation, dates, venues and booking form four separate glass groups across the top bar. |
| r18 | legibility | 1/3 | astra-medium | The light navigation is readable, but the captures do not establish numerical contrast in a dark mode. |
| r19 | legibility | 1/3 | astra-medium | The reduced-transparency top controls remain readable, but increased contrast and reduced motion are not shown. |
| r23 | motion | 0/3 | astra-medium | The venue-menu still does not reveal whether opening morphs or whether presses glow and flex. |

Frozen mechanical facts (null means unrecorded):

```json
{
  "error": null,
  "errors": [],
  "consoleErrors": [],
  "failedRequests": 0,
  "overflowCapture": false,
  "gateMechanical": true,
  "rootFound": true,
  "surfaces": 4,
  "groups": [
    {
      "id": "masthead",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "analysis": "exact",
      "refraction": "true",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    },
    {
      "id": "filters",
      "members": 2,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "analysis": "exact",
      "refraction": "true",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    },
    {
      "id": "book",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "analysis": "exact",
      "refraction": "true",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    },
    {
      "id": "venuemenu",
      "members": 0,
      "renderer": "webgpu",
      "sampling": "css-backdrop",
      "analysis": "hint",
      "refraction": "approximate",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    }
  ],
  "diagnostics": [],
  "menu": "captured",
  "menuGroups": [
    {
      "id": "masthead",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "health": "ok"
    },
    {
      "id": "filters",
      "members": 2,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "health": "ok"
    },
    {
      "id": "book",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "health": "ok"
    },
    {
      "id": "venuemenu",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "css-backdrop",
      "health": "ok"
    }
  ],
  "menuDiagnostics": [],
  "colorScheme": "light",
  "contrast": {
    "checked": 335,
    "pass": 335,
    "unknown": 0,
    "rate": 1,
    "onGlass": 11,
    "onGlassPass": 11,
    "fails": []
  },
  "reduced": {
    "rootFound": true,
    "errors": [],
    "reducedMotionEmulated": true,
    "overrideHonoured": true,
    "materialMoved": true,
    "material": {
      "glass": "material",
      "colorSource": "material",
      "frost": "increased",
      "refraction": "reduced",
      "occlusion": "increased",
      "border": "nominal",
      "ambientTint": "nominal",
      "foreground": "adaptive"
    },
    "motion": {
      "overshoot": "none",
      "deformation": "none",
      "shimmer": "none",
      "morph": "non-elastic",
      "crossfade": "large-plane-shifts",
      "positionalContinuity": true
    },
    "groups": [
      {
        "id": "masthead",
        "renderer": "webgpu",
        "refraction": "true",
        "cssBody": null
      },
      {
        "id": "filters",
        "renderer": "webgpu",
        "refraction": "true",
        "cssBody": null
      },
      {
        "id": "book",
        "renderer": "webgpu",
        "refraction": "true",
        "cssBody": null
      }
    ],
    "reducedTransparencyUndetectable": false,
    "ok": true
  }
}
```

Evidence limits: r18 requires contrast in both schemes; the audit samples only the recorded scheme. r19 requires all three accessibility modes; reduced motion emulation and a reduced-transparency runtime smoke check do not establish full accessibility, and increased contrast is not tested. r23 requires motion evidence absent from static captures. These gaps do not replace panel zeros with passes or remove rules from 25.

Verdict, clause by clause:

| clause | met | on |
|---|---|---|
| four-rater panel complete | not yet readable | missing/partial: claude-opus |
| at least 22 of 25 held | not yet readable | 21 of 25 held (provisional) |
| no [layer] or [material] rule fails | not yet readable | none failed in available answers |
| no group diagnostic | yes | rest=[]; menu=[] |
| works with transparency reduced | yes | reduced ok=True; overrideHonoured=True; materialMoved=True; errors=[]; runtime smoke check only, not full accessibility |

**film-festival: no final verdict — incomplete evidence; provisional reading above**

### `park-trails`

Raters: 3 (astra-medium, astra-high, claude-sonnet). Held: **20 of 25** by panel majority (provisional; panel incomplete). Fatal-tag failures: **r6**.

Rules that failed:

| rule | tag | yes/n | a rater that said no | its evidence |
|---|---|---|---|---|
| r6 | material | 1/3 | astra-medium | The open permit view retains the pink Check permit background alongside the red Reserve background. |
| r9 | geometry | 1/3 | astra-medium | The permit platter has pill-like interior information rows whose corner arcs do not follow the outer panel. |
| r18 | legibility | 1/3 | astra-medium | The planner is readable in the light capture, but no dark-state capture establishes the required contrast in both modes. |
| r19 | legibility | 1/3 | astra-medium | The reduced-transparency planner remains readable, but increased-contrast and reduced-motion operation are not shown. |
| r23 | motion | 0/3 | astra-medium | The open permit still does not show emergence, morphing or pointer-local press feedback. |

Frozen mechanical facts (null means unrecorded):

```json
{
  "error": null,
  "errors": [],
  "consoleErrors": [],
  "failedRequests": 0,
  "overflowCapture": false,
  "gateMechanical": true,
  "rootFound": true,
  "surfaces": 2,
  "groups": [
    {
      "id": "bar",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "css-backdrop",
      "analysis": "hint",
      "refraction": "approximate",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    },
    {
      "id": "action",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "css-backdrop",
      "analysis": "hint",
      "refraction": "approximate",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    },
    {
      "id": "permit",
      "members": 0,
      "renderer": "webgpu",
      "sampling": "css-backdrop",
      "analysis": "hint",
      "refraction": "approximate",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    }
  ],
  "diagnostics": [],
  "menu": "captured",
  "menuGroups": [
    {
      "id": "bar",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "css-backdrop",
      "health": "ok"
    },
    {
      "id": "action",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "css-backdrop",
      "health": "ok"
    },
    {
      "id": "permit",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "css-backdrop",
      "health": "ok"
    }
  ],
  "menuDiagnostics": [],
  "colorScheme": "light",
  "contrast": {
    "checked": 28,
    "pass": 28,
    "unknown": 222,
    "rate": 1,
    "onGlass": 12,
    "onGlassPass": 12,
    "fails": []
  },
  "reduced": {
    "rootFound": true,
    "errors": [],
    "reducedMotionEmulated": true,
    "overrideHonoured": true,
    "materialMoved": true,
    "material": {
      "glass": "material",
      "colorSource": "material",
      "frost": "increased",
      "refraction": "reduced",
      "occlusion": "increased",
      "border": "nominal",
      "ambientTint": "nominal",
      "foreground": "adaptive"
    },
    "motion": {
      "overshoot": "none",
      "deformation": "none",
      "shimmer": "none",
      "morph": "non-elastic",
      "crossfade": "large-plane-shifts",
      "positionalContinuity": true
    },
    "groups": [
      {
        "id": "bar",
        "renderer": "webgpu",
        "refraction": "approximate",
        "cssBody": null
      },
      {
        "id": "action",
        "renderer": "webgpu",
        "refraction": "approximate",
        "cssBody": null
      }
    ],
    "reducedTransparencyUndetectable": false,
    "ok": true
  }
}
```

Evidence limits: r18 requires contrast in both schemes; the audit samples only the recorded scheme. r19 requires all three accessibility modes; reduced motion emulation and a reduced-transparency runtime smoke check do not establish full accessibility, and increased contrast is not tested. r23 requires motion evidence absent from static captures. These gaps do not replace panel zeros with passes or remove rules from 25.

Verdict, clause by clause:

| clause | met | on |
|---|---|---|
| four-rater panel complete | not yet readable | missing/partial: claude-opus |
| at least 22 of 25 held | not yet readable | 20 of 25 held (provisional) |
| no [layer] or [material] rule fails | not yet readable | r6 |
| no group diagnostic | yes | rest=[]; menu=[] |
| works with transparency reduced | yes | reduced ok=True; overrideHonoured=True; materialMoved=True; errors=[]; runtime smoke check only, not full accessibility |

**park-trails: no final verdict — incomplete evidence; provisional reading above**

### `product-launch`

Raters: 3 (astra-medium, astra-high, claude-sonnet). Held: **18 of 25** by panel majority (provisional; panel incomplete). Fatal-tag failures: **r16**.

Rules that failed:

| rule | tag | yes/n | a rater that said no | its evidence |
|---|---|---|---|---|
| r15 | legibility | 0/3 | astra-medium | The scrolled sensor and body text passes under the bottom configurator without any visible scroll-edge fade or boundary. |
| r16 | material | 0/3 | astra-medium | In the scrolled captures the configurator lies across the uniform opaque specification cards. |
| r17 | legibility | 1/3 | astra-medium | The sensor heading overlaps the top navigation region and body copy sits behind the bottom configurator in the scrolled views. |
| r18 | legibility | 1/3 | astra-medium | The dark bars have subdued labels and no light-state capture establishes the required contrast in both modes. |
| r19 | legibility | 1/3 | astra-medium | The reduced-transparency controls remain available, but increased-contrast and reduced-motion states are not demonstrated. |
| r21 | layout | 1/3 | astra-medium | The sensor heading and lower specification copy fail to clear the floating bars in the scrolled captures. |
| r23 | motion | 0/3 | astra-medium | The lens-menu still does not reveal whether it morphs from the trigger or how presses respond. |

Frozen mechanical facts (null means unrecorded):

```json
{
  "error": null,
  "errors": [],
  "consoleErrors": [],
  "failedRequests": 0,
  "overflowCapture": false,
  "gateMechanical": true,
  "rootFound": true,
  "surfaces": 4,
  "groups": [
    {
      "id": "nav",
      "members": 2,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "analysis": "exact",
      "refraction": "true",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    },
    {
      "id": "commit",
      "members": 2,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "analysis": "exact",
      "refraction": "true",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    },
    {
      "id": "platter",
      "members": 0,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "analysis": "exact",
      "refraction": "true",
      "health": "ok",
      "demotionReason": null,
      "cssBody": null,
      "cssTint": null,
      "cssShadow": null,
      "diagnostics": []
    }
  ],
  "diagnostics": [],
  "menu": "captured",
  "menuGroups": [
    {
      "id": "nav",
      "members": 2,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "health": "ok"
    },
    {
      "id": "commit",
      "members": 2,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "health": "ok"
    },
    {
      "id": "platter",
      "members": 1,
      "renderer": "webgpu",
      "sampling": "gpu-texture",
      "health": "ok"
    }
  ],
  "menuDiagnostics": [],
  "colorScheme": "dark",
  "contrast": {
    "checked": 154,
    "pass": 154,
    "unknown": 0,
    "rate": 1,
    "onGlass": 14,
    "onGlassPass": 14,
    "fails": []
  },
  "reduced": {
    "rootFound": true,
    "errors": [],
    "reducedMotionEmulated": true,
    "overrideHonoured": true,
    "materialMoved": true,
    "material": {
      "glass": "material",
      "colorSource": "material",
      "frost": "increased",
      "refraction": "reduced",
      "occlusion": "increased",
      "border": "nominal",
      "ambientTint": "nominal",
      "foreground": "adaptive"
    },
    "motion": {
      "overshoot": "none",
      "deformation": "none",
      "shimmer": "none",
      "morph": "non-elastic",
      "crossfade": "large-plane-shifts",
      "positionalContinuity": true
    },
    "groups": [
      {
        "id": "nav",
        "renderer": "webgpu",
        "refraction": "true",
        "cssBody": null
      },
      {
        "id": "commit",
        "renderer": "webgpu",
        "refraction": "true",
        "cssBody": null
      }
    ],
    "reducedTransparencyUndetectable": false,
    "ok": true
  }
}
```

Evidence limits: r18 requires contrast in both schemes; the audit samples only the recorded scheme. r19 requires all three accessibility modes; reduced motion emulation and a reduced-transparency runtime smoke check do not establish full accessibility, and increased contrast is not tested. r23 requires motion evidence absent from static captures. These gaps do not replace panel zeros with passes or remove rules from 25.

Verdict, clause by clause:

| clause | met | on |
|---|---|---|
| four-rater panel complete | not yet readable | missing/partial: claude-opus |
| at least 22 of 25 held | not yet readable | 18 of 25 held (provisional) |
| no [layer] or [material] rule fails | not yet readable | r16 |
| no group diagnostic | yes | rest=[]; menu=[] |
| works with transparency reduced | yes | reduced ok=True; overrideHonoured=True; materialMoved=True; errors=[]; runtime smoke check only, not full accessibility |

**product-launch: no final verdict — incomplete evidence; provisional reading above**

## Agreement per rule (Krippendorff's α, nominal)

The units are the demos and the observations are the panel's 0/1 answers, so each α below stands on at most 6 unit(s) — far fewer than a reliability claim wants, and the column saying how many is part of the reading. A rule the panel answered the same way on every demo has no variation for chance to explain: its α is 1.0 by construction and is marked constant.

| rule | tag | α | demos with ≥ 2 raters | values used | note |
|---|---|---|---|---|---|
| r1 | layer | 0.53 | 6 | 0, 1 |  |
| r2 | layer | 0.47 | 6 | 0, 1 |  |
| r3 | layer | -0.13 | 6 | 0, 1 |  |
| r4 | material | 1.00 | 6 | 1 | constant at 1 |
| r5 | material | 1.00 | 6 | 1 | constant at 1 |
| r6 | material | -0.05 | 6 | 0, 1 |  |
| r7 | material | 0.00 | 6 | 0, 1 |  |
| r8 | geometry | 1.00 | 6 | 1 | constant at 1 |
| r9 | geometry | 0.06 | 6 | 0, 1 |  |
| r10 | geometry | -0.06 | 6 | 0, 1 |  |
| r11 | grouping | 1.00 | 6 | 0, 1 |  |
| r12 | grouping | 1.00 | 6 | 1 | constant at 1 |
| r13 | grouping | 1.00 | 6 | 1 | constant at 1 |
| r14 | grouping | 0.47 | 6 | 0, 1 |  |
| r15 | legibility | 0.06 | 6 | 0, 1 |  |
| r16 | material | 0.48 | 6 | 0, 1 |  |
| r17 | legibility | -0.26 | 6 | 0, 1 |  |
| r18 | legibility | -0.42 | 6 | 0, 1 |  |
| r19 | legibility | -0.42 | 6 | 0, 1 |  |
| r20 | layout | 1.00 | 6 | 0, 1 |  |
| r21 | layout | 0.36 | 6 | 0, 1 |  |
| r22 | layout | -0.06 | 6 | 0, 1 |  |
| r23 | motion | 1.00 | 6 | 0 | constant at 0 |
| r24 | colour | 0.22 | 6 | 0, 1 |  |
| r25 | colour | 0.00 | 6 | 0, 1 |  |

## The quality reading

The instrument's own items (`settling/rubric.py`), panel means over the raters that rated each demo. This table stands on 6 demo(s) and 3 rater(s).

| demo | raters | a1 | a2 | a3 | a4 | a1–a4 | d1 | e1 |
|---|---|---|---|---|---|---|---|---|
| `music-player` | 3 | 5.33 | 4.67 | 5.67 | 5.00 | 5.17 | 4.33 | 3.67 |
| `transit-ops` | 3 | 6.00 | 4.67 | 5.33 | 6.00 | 5.50 | 5.00 | 5.00 |
| `photo-review` | 3 | 6.33 | 4.67 | 6.00 | 6.33 | 5.83 | 5.33 | 6.00 |
| `film-festival` | 3 | 5.67 | 6.00 | 5.67 | 6.00 | 5.83 | 5.33 | 4.33 |
| `park-trails` | 3 | 6.00 | 5.67 | 6.00 | 6.00 | 5.92 | 5.67 | 4.00 |
| `product-launch` | 3 | 4.67 | 3.00 | 4.33 | 4.33 | 4.08 | 3.67 | 6.00 |

d1 mean over 6 of 6 demos: **4.89** against the initiative's floor of 5.0 — provisional only; the four-rater d1 panel over all six is incomplete

## The line

**0 of 6 demos pass**; no verdict yet on 6 for want of data. The initiative also asks the panel's d1 mean over the six and the user's eye on five of six; the user's comparison is not in this report.
