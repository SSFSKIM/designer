
## P1 — Verbatim theme output (highest priority)

I’ll call the theme generator separately for each exact brief and reproduce the returned text without editing.

### Output 1 — film-production studio dashboard

```json
[{"type":"text","text":"Here are some aesthetic ingredients to consider for this user's project.\n\nLean especially toward these directions to break out of trained defaults. Treat them as tiebreakers when the brief is silent on aesthetic, not overrides — if the brief explicitly names an aesthetic, honor it literally. If two directions feel equally plausible, pick the less-common one.\n\n**Stances to consider:**\n1. **maximalist** — Zine aesthetic, scrap-and-tape. Mixed type, overlapping elements, deliberately layered hierarchy.\n2. **warm** — Aesop, Le Labo, boutique hospitality. Cream bases, muted earth tones, serif type, tactile-feeling imagery.\n3. **editorial** — Monocle, The Gentlewoman, Kinfolk. Serif display + sans body, asymmetric column grids, generous margins, feature photography, warm neutral palettes.\n\n**Typography traditions:**\n1. Old-style serif (Garamond, Caslon, Minion, Janson)\n2. Geometric sans (Futura, Avenir, Nunito)\n\n**Canvas treatment:**\n1. gradient or mesh background\n\nYOUR TASK: Combine any preferences the user expressed with these directions to make a great theme for them. Be opinionated and specific. Commit to one stance — the most memorable outputs come from full commitment to one direction rather than hedging."}]
```

### Output 2 — teenage habit-tracking mobile web app

```json
[{"type":"text","text":"Here are some aesthetic ingredients to consider for this user's project.\n\nLean especially toward these directions to break out of trained defaults. Treat them as tiebreakers when the brief is silent on aesthetic, not overrides — if the brief explicitly names an aesthetic, honor it literally. If two directions feel equally plausible, pick the less-common one.\n\n**Stances to consider:**\n1. **minimalist** — Apple, Aesop, Teenage Engineering product pages. One hero element, tight type, lots of whitespace, single accent.\n2. **archival** — MoMA catalogs, Rijksmuseum. Numbered sections, serif/mono pairings, textured neutrals, reverent composition.\n3. **brutalist** — Bloomberg Businessweek online, brutalistwebsites.com. Raw mono type, stark black/white, hot accent, deliberately unstyled-looking but composed.\n\n**Typography traditions:**\n1. Glyphic serif (Trajan, Albertus)\n2. Monospace-as-display (JetBrains Mono, Berkeley Mono, Fira Code)\n\n**Canvas treatment:**\n1. gradient or mesh background\n\nYOUR TASK: Combine any preferences the user expressed with these directions to make a great theme for them. Be opinionated and specific. Commit to one stance — the most memorable outputs come from full commitment to one direction rather than hedging."}]
```
## P2 — Stance → concrete CSS translation table

Below are five concrete, shippable visual systems. Each is a **complete starting spec**, not a mood direction. I would still tune the content density and component usage per product, but I would not need to invent token values while implementing.

For all five, I would use semantic tokens—not ad-hoc per-component colors—and I would use the named shadow recipes only where their stated elevation is needed.

---

## 1. Precision industrial

**Best for:** operations tools, infrastructure, logistics, scientific products, technical dashboards, high-trust data applications.

```css
/* PRECISION INDUSTRIAL
   Character: exact, durable, sober, low-noise.
   Surface model: cool near-white workspace + steel-tinted panels.
   Use shadows sparingly; structure comes from grid and rules.
*/

:root {
  /* Color tokens */
  --background: #F4F6F7;
  --foreground: #162024;

  --card: #FFFFFF;
  --card-foreground: #162024;

  --primary: #123B45;
  --primary-foreground: #F7FAFA;

  --secondary: #E3E9EA;
  --secondary-foreground: #243237;

  --muted: #EDF1F1;
  --muted-foreground: #607076;

  --accent: #D46B2C;
  --accent-foreground: #241006;

  --border: #C7D0D2;
  --ring: #D46B2C;

  /* Optional semantic status colors */
  --success: #2C725E;
  --warning: #B75D16;
  --danger: #B63B3B;
  --info: #276B8A;

  /* Radius scale */
  --radius-0: 0px;
  --radius-1: 2px;
  --radius-2: 4px;
  --radius-3: 6px;
  --radius-4: 8px;
  --radius-full: 9999px;

  /* Border system */
  --border-hairline: 1px;
  --border-strong: 2px;
  --border-subtle: rgb(22 32 36 / 12%);
  --border-default: rgb(22 32 36 / 20%);
  --border-strong-color: rgb(22 32 36 / 38%);
  --border-active: #123B45;

  /* Shadows — use only for floating UI, never ordinary cards */
  --shadow-none: none;
  --shadow-float:
    0 1px 2px rgb(22 32 36 / 8%),
    0 8px 20px rgb(22 32 36 / 10%);
  --shadow-popover:
    0 2px 4px rgb(22 32 36 / 8%),
    0 18px 42px rgb(22 32 36 / 16%);
  --shadow-modal:
    0 8px 16px rgb(22 32 36 / 10%),
    0 28px 70px rgb(22 32 36 / 22%);

  /* Spacing scale */
  --space-0: 0px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
  --space-20: 80px;
  --space-24: 96px;

  /* Typography */
  --font-display: "Archivo", "Helvetica Neue", Arial, sans-serif;
  --font-ui: "Inter", "Helvetica Neue", Arial, sans-serif;
  --font-mono: "Geist Mono", "SFMono-Regular", Consolas, monospace;

  --type-display-size: 48px;
  --type-display-line: 1.04;
  --type-display-weight: 650;
  --type-display-tracking: -0.025em;

  --type-h1-size: 36px;
  --type-h1-line: 1.12;
  --type-h1-weight: 650;
  --type-h1-tracking: -0.02em;

  --type-h2-size: 28px;
  --type-h2-line: 1.18;
  --type-h2-weight: 620;
  --type-h2-tracking: -0.014em;

  --type-h3-size: 20px;
  --type-h3-line: 1.25;
  --type-h3-weight: 620;
  --type-h3-tracking: -0.008em;

  --type-body-size: 15px;
  --type-body-line: 1.55;
  --type-body-weight: 430;
  --type-body-tracking: 0em;

  --type-body-sm-size: 13px;
  --type-body-sm-line: 1.5;
  --type-body-sm-weight: 430;
  --type-body-sm-tracking: 0em;

  --type-caption-size: 12px;
  --type-caption-line: 1.4;
  --type-caption-weight: 500;
  --type-caption-tracking: 0.01em;

  --type-label-size: 11px;
  --type-label-line: 1.25;
  --type-label-weight: 650;
  --type-label-tracking: 0.08em;
  --type-label-transform: uppercase;

  --type-data-size: 12px;
  --type-data-line: 1.35;
  --type-data-weight: 500;
  --type-data-tracking: -0.01em;

  /* Motion */
  --ease-standard: cubic-bezier(0.2, 0, 0, 1);
  --ease-enter: cubic-bezier(0, 0, 0, 1);
  --ease-exit: cubic-bezier(0.3, 0, 1, 1);

  --duration-instant: 80ms;
  --duration-fast: 120ms;
  --duration-standard: 180ms;
  --duration-slow: 240ms;

  /* Use: hover/focus = 120ms; menus = 180ms; dialogs = 240ms. */
}
```

**Implementation rules:** use `--radius-2` for controls, `--radius-3` for panels, and `--radius-0` for data tables. Ordinary cards have a 1px border and **no shadow**. Use the orange accent for exceptions, high-priority actions, and keyboard focus—not decorative highlights.

---

## 2. Quiet editorial

**Best for:** studios, publications, cultural institutions, portfolios, research experiences, refined service brands.

```css
/* QUIET EDITORIAL
   Character: literary, composed, spacious, image-aware.
   Surface model: warm paper ground + ink text + restrained vermilion accent.
   Let typography and whitespace create hierarchy.
*/

:root {
  /* Color tokens */
  --background: #F5F0E8;
  --foreground: #24211E;

  --card: #FCF9F3;
  --card-foreground: #24211E;

  --primary: #2C302A;
  --primary-foreground: #FAF6EE;

  --secondary: #E8E0D4;
  --secondary-foreground: #4A443D;

  --muted: #EEE8DF;
  --muted-foreground: #756D64;

  --accent: #A9462D;
  --accent-foreground: #FFF8F0;

  --border: #D4CABE;
  --ring: #A9462D;

  /* Radius scale */
  --radius-0: 0px;
  --radius-1: 2px;
  --radius-2: 4px;
  --radius-3: 8px;
  --radius-4: 12px;
  --radius-full: 9999px;

  /* Border system */
  --border-hairline: 1px;
  --border-emphasis: 1px;
  --border-subtle: rgb(36 33 30 / 12%);
  --border-default: rgb(36 33 30 / 18%);
  --border-emphasized: rgb(36 33 30 / 32%);
  --border-image: rgb(36 33 30 / 10%);

  /* Shadows — editorial interfaces should be nearly shadowless */
  --shadow-none: none;
  --shadow-image:
    0 1px 1px rgb(36 33 30 / 6%),
    0 6px 18px rgb(36 33 30 / 8%);
  --shadow-float:
    0 2px 6px rgb(36 33 30 / 8%),
    0 16px 36px rgb(36 33 30 / 12%);
  --shadow-modal:
    0 8px 22px rgb(36 33 30 / 10%),
    0 32px 80px rgb(36 33 30 / 18%);

  /* Spacing scale */
  --space-0: 0px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 40px;
  --space-8: 48px;
  --space-10: 64px;
  --space-12: 80px;
  --space-16: 112px;
  --space-20: 144px;

  /* Typography */
  --font-display: "Newsreader", Georgia, serif;
  --font-ui: "Public Sans", "Helvetica Neue", Arial, sans-serif;
  --font-mono: "DM Mono", "SFMono-Regular", Consolas, monospace;

  --type-display-size: 64px;
  --type-display-line: 0.98;
  --type-display-weight: 480;
  --type-display-tracking: -0.032em;

  --type-h1-size: 44px;
  --type-h1-line: 1.04;
  --type-h1-weight: 500;
  --type-h1-tracking: -0.024em;

  --type-h2-size: 32px;
  --type-h2-line: 1.12;
  --type-h2-weight: 510;
  --type-h2-tracking: -0.018em;

  --type-h3-size: 23px;
  --type-h3-line: 1.22;
  --type-h3-weight: 560;
  --type-h3-tracking: -0.01em;

  --type-body-size: 16px;
  --type-body-line: 1.62;
  --type-body-weight: 400;
  --type-body-tracking: -0.003em;

  --type-body-sm-size: 14px;
  --type-body-sm-line: 1.55;
  --type-body-sm-weight: 400;
  --type-body-sm-tracking: 0em;

  --type-caption-size: 12px;
  --type-caption-line: 1.45;
  --type-caption-weight: 500;
  --type-caption-tracking: 0.01em;

  --type-label-size: 11px;
  --type-label-line: 1.3;
  --type-label-weight: 650;
  --type-label-tracking: 0.12em;
  --type-label-transform: uppercase;

  --type-data-size: 12px;
  --type-data-line: 1.45;
  --type-data-weight: 500;
  --type-data-tracking: 0em;

  /* Motion */
  --ease-standard: cubic-bezier(0.22, 1, 0.36, 1);
  --ease-enter: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-exit: cubic-bezier(0.7, 0, 0.84, 0);

  --duration-instant: 100ms;
  --duration-fast: 160ms;
  --duration-standard: 260ms;
  --duration-slow: 420ms;

  /* Use: hover/focus = 160ms; image/caption reveals = 260ms; overlays = 420ms. */
}
```

**Implementation rules:** use full-bleed or editorially cropped images, with rules and whitespace doing most of the layout work. Use `--radius-0` or `--radius-1` for cards and image frames; reserve `--radius-3` for inputs and soft utility controls. The vermilion accent should appear rarely: selected state, active link, primary action, or a small editorial rule.

---

## 3. Contemporary craft commerce

**Best for:** premium goods, food and beverage, small-batch products, hospitality, independent retail, maker brands.

```css
/* CONTEMPORARY CRAFT COMMERCE
   Character: tactile, assured, warm, materially grounded.
   Surface model: mineral neutral + deep ink + botanical green + clay signal.
   Product imagery leads; UI elements remain quietly premium.
*/

:root {
  /* Color tokens */
  --background: #EDE7DC;
  --foreground: #302A24;

  --card: #F8F4EC;
  --card-foreground: #302A24;

  --primary: #334D3D;
  --primary-foreground: #F9F6EF;

  --secondary: #DDD4C6;
  --secondary-foreground: #463D34;

  --muted: #E6DED2;
  --muted-foreground: #766C60;

  --accent: #B65A3C;
  --accent-foreground: #FFF9F3;

  --border: #CDBFAF;
  --ring: #B65A3C;

  /* Optional semantic colors */
  --success: #426B4F;
  --warning: #A36B22;
  --danger: #A63F34;

  /* Radius scale */
  --radius-0: 0px;
  --radius-1: 3px;
  --radius-2: 6px;
  --radius-3: 10px;
  --radius-4: 16px;
  --radius-5: 24px;
  --radius-full: 9999px;

  /* Border system */
  --border-hairline: 1px;
  --border-strong: 1px;
  --border-subtle: rgb(48 42 36 / 10%);
  --border-default: rgb(48 42 36 / 18%);
  --border-emphasized: rgb(48 42 36 / 30%);
  --border-inverse: rgb(249 246 239 / 32%);

  /* Shadows — soft, warm, used on product media and flyouts only */
  --shadow-none: none;
  --shadow-product:
    0 1px 2px rgb(48 42 36 / 5%),
    0 10px 24px rgb(48 42 36 / 10%);
  --shadow-float:
    0 4px 10px rgb(48 42 36 / 8%),
    0 18px 42px rgb(48 42 36 / 14%);
  --shadow-modal:
    0 12px 28px rgb(48 42 36 / 12%),
    0 36px 88px rgb(48 42 36 / 20%);

  /* Spacing scale */
  --space-0: 0px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 28px;
  --space-8: 36px;
  --space-10: 48px;
  --space-12: 60px;
  --space-16: 80px;
  --space-20: 112px;
  --space-24: 144px;

  /* Typography */
  --font-display: "Fraunces", Georgia, serif;
  --font-ui: "Albert Sans", "Helvetica Neue", Arial, sans-serif;
  --font-mono: "Azeret Mono", "SFMono-Regular", Consolas, monospace;

  --type-display-size: 60px;
  --type-display-line: 0.98;
  --type-display-weight: 560;
  --type-display-tracking: -0.035em;

  --type-h1-size: 42px;
  --type-h1-line: 1.06;
  --type-h1-weight: 560;
  --type-h1-tracking: -0.025em;

  --type-h2-size: 30px;
  --type-h2-line: 1.15;
  --type-h2-weight: 580;
  --type-h2-tracking: -0.018em;

  --type-h3-size: 21px;
  --type-h3-line: 1.25;
  --type-h3-weight: 600;
  --type-h3-tracking: -0.008em;

  --type-body-size: 15px;
  --type-body-line: 1.58;
  --type-body-weight: 430;
  --type-body-tracking: 0em;

  --type-body-sm-size: 13px;
  --type-body-sm-line: 1.5;
  --type-body-sm-weight: 450;
  --type-body-sm-tracking: 0em;

  --type-caption-size: 12px;
  --type-caption-line: 1.4;
  --type-caption-weight: 520;
  --type-caption-tracking: 0.01em;

  --type-label-size: 11px;
  --type-label-line: 1.25;
  --type-label-weight: 700;
  --type-label-tracking: 0.09em;
  --type-label-transform: uppercase;

  --type-price-size: 15px;
  --type-price-line: 1.2;
  --type-price-weight: 650;
  --type-price-tracking: -0.01em;

  /* Motion */
  --ease-standard: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-enter: cubic-bezier(0.12, 0.8, 0.2, 1);
  --ease-exit: cubic-bezier(0.6, 0, 0.8, 0.2);

  --duration-instant: 100ms;
  --duration-fast: 150ms;
  --duration-standard: 220ms;
  --duration-slow: 360ms;

  /* Use: product-image hover = 220ms; add-to-cart = 150ms; drawer = 360ms. */
}
```

**Implementation rules:** use `--radius-2` for buttons and inputs, `--radius-3` for product cards, and `--radius-4` for image-led promotional surfaces. Product imagery can use `--shadow-product`; standard text/content cards should normally remain flat with a border.

---

## 4. Institutional calm

**Best for:** healthcare, education, civic services, legal products, financial planning, nonprofit and public-interest platforms.

```css
/* INSTITUTIONAL CALM
   Character: measured, trustworthy, clear, enduring.
   Surface model: parchment-light background + navy anchor + restrained blue-green.
   Emphasize information clarity, predictability, and accessible contrast.
*/

:root {
  /* Color tokens */
  --background: #F7F7F3;
  --foreground: #1D2A36;

  --card: #FFFFFF;
  --card-foreground: #1D2A36;

  --primary: #1E4263;
  --primary-foreground: #F8FBFC;

  --secondary: #E7ECEC;
  --secondary-foreground: #31434B;

  --muted: #EFF2F1;
  --muted-foreground: #64727A;

  --accent: #2B7B78;
  --accent-foreground: #F4FFFF;

  --border: #CAD3D4;
  --ring: #2B7B78;

  /* Optional semantic colors */
  --success: #31755F;
  --warning: #9A661B;
  --danger: #A34242;
  --info: #29658C;

  /* Radius scale */
  --radius-0: 0px;
  --radius-1: 2px;
  --radius-2: 4px;
  --radius-3: 6px;
  --radius-4: 10px;
  --radius-full: 9999px;

  /* Border system */
  --border-hairline: 1px;
  --border-strong: 2px;
  --border-subtle: rgb(29 42 54 / 10%);
  --border-default: rgb(29 42 54 / 17%);
  --border-emphasized: rgb(29 42 54 / 28%);
  --border-focus: #2B7B78;

  /* Shadows — reserved for menus/dialogs, never navigation or primary content */
  --shadow-none: none;
  --shadow-dropdown:
    0 2px 4px rgb(29 42 54 / 7%),
    0 10px 24px rgb(29 42 54 / 11%);
  --shadow-popover:
    0 4px 10px rgb(29 42 54 / 9%),
    0 20px 48px rgb(29 42 54 / 14%);
  --shadow-modal:
    0 10px 24px rgb(29 42 54 / 12%),
    0 34px 76px rgb(29 42 54 / 20%);

  /* Spacing scale */
  --space-0: 0px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
  --space-20: 80px;
  --space-24: 96px;

  /* Typography */
  --font-display: "Source Serif 4", Georgia, serif;
  --font-ui: "Source Sans 3", "Helvetica Neue", Arial, sans-serif;
  --font-mono: "Roboto Mono", "SFMono-Regular", Consolas, monospace;

  --type-display-size: 46px;
  --type-display-line: 1.08;
  --type-display-weight: 600;
  --type-display-tracking: -0.02em;

  --type-h1-size: 36px;
  --type-h1-line: 1.14;
  --type-h1-weight: 650;
  --type-h1-tracking: -0.016em;

  --type-h2-size: 28px;
  --type-h2-line: 1.2;
  --type-h2-weight: 650;
  --type-h2-tracking: -0.01em;

  --type-h3-size: 21px;
  --type-h3-line: 1.28;
  --type-h3-weight: 650;
  --type-h3-tracking: -0.005em;

  --type-body-size: 16px;
  --type-body-line: 1.55;
  --type-body-weight: 400;
  --type-body-tracking: 0em;

  --type-body-sm-size: 14px;
  --type-body-sm-line: 1.5;
  --type-body-sm-weight: 400;
  --type-body-sm-tracking: 0em;

  --type-caption-size: 12px;
  --type-caption-line: 1.45;
  --type-caption-weight: 550;
  --type-caption-tracking: 0.005em;

  --type-label-size: 12px;
  --type-label-line: 1.3;
  --type-label-weight: 700;
  --type-label-tracking: 0.05em;
  --type-label-transform: none;

  --type-data-size: 13px;
  --type-data-line: 1.4;
  --type-data-weight: 500;
  --type-data-tracking: 0em;

  /* Motion */
  --ease-standard: cubic-bezier(0.2, 0, 0, 1);
  --ease-enter: cubic-bezier(0, 0, 0.2, 1);
  --ease-exit: cubic-bezier(0.4, 0, 1, 1);

  --duration-instant: 90ms;
  --duration-fast: 140ms;
  --duration-standard: 200ms;
  --duration-slow: 300ms;

  /* Use: focus/hover = 140ms; menus = 200ms; dialogs = 300ms. */
}
```

**Implementation rules:** use `--radius-2` as the default across inputs, buttons, and cards. Information architecture should do more work than visual novelty: clear labels, ordered forms, durable tables, and obvious selected states. Never rely on color alone for validation, warnings, or progress.

---

## 5. Playful consumer

**Best for:** habit tracking, youth-focused products, consumer education, social tools, wellness, friendly productivity apps.

```css
/* PLAYFUL CONSUMER
   Character: optimistic, lively, legible, emotionally direct.
   Surface model: soft lavender white + ink blue + citrus/lilac/peach signals.
   Playfulness comes from scale, rhythm, and interaction—not visual clutter.
*/

:root {
  /* Color tokens */
  --background: #F7F5FF;
  --foreground: #24203D;

  --card: #FFFFFF;
  --card-foreground: #24203D;

  --primary: #5A47D5;
  --primary-foreground: #FFFFFF;

  --secondary: #E9E4FF;
  --secondary-foreground: #342B76;

  --muted: #F0EDF8;
  --muted-foreground: #716B88;

  --accent: #FFB94D;
  --accent-foreground: #3B2500;

  --border: #DCD7EF;
  --ring: #5A47D5;

  /* Supporting expressive colors */
  --playful-mint: #82D7B2;
  --playful-mint-foreground: #123E2D;
  --playful-peach: #FFB6A2;
  --playful-peach-foreground: #542016;
  --playful-sky: #94D7FF;
  --playful-sky-foreground: #123854;
  --success: #2F9E6C;
  --warning: #C77B12;
  --danger: #D34858;

  /* Radius scale */
  --radius-0: 0px;
  --radius-1: 6px;
  --radius-2: 10px;
  --radius-3: 14px;
  --radius-4: 20px;
  --radius-5: 28px;
  --radius-full: 9999px;

  /* Border system */
  --border-hairline: 1px;
  --border-strong: 2px;
  --border-subtle: rgb(36 32 61 / 10%);
  --border-default: rgb(36 32 61 / 16%);
  --border-emphasized: rgb(36 32 61 / 26%);
  --border-primary: rgb(90 71 213 / 50%);

  /* Shadows — soft and slightly colored; one level for cards, one for active/floating */
  --shadow-none: none;
  --shadow-card:
    0 1px 2px rgb(36 32 61 / 5%),
    0 7px 16px rgb(90 71 213 / 8%);
  --shadow-active:
    0 2px 4px rgb(36 32 61 / 7%),
    0 10px 24px rgb(90 71 213 / 16%);
  --shadow-float:
    0 5px 12px rgb(36 32 61 / 10%),
    0 22px 46px rgb(90 71 213 / 20%);
  --shadow-modal:
    0 10px 24px rgb(36 32 61 / 14%),
    0 36px 82px rgb(36 32 61 / 24%);

  /* Spacing scale */
  --space-0: 0px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
  --space-20: 80px;

  /* Typography */
  --font-display: "Bricolage Grotesque", "Arial Rounded MT Bold", sans-serif;
  --font-ui: "DM Sans", "Helvetica Neue", Arial, sans-serif;
  --font-mono: "Fira Mono", "SFMono-Regular", Consolas, monospace;

  --type-display-size: 52px;
  --type-display-line: 1;
  --type-display-weight: 700;
  --type-display-tracking: -0.035em;

  --type-h1-size: 36px;
  --type-h1-line: 1.08;
  --type-h1-weight: 700;
  --type-h1-tracking: -0.025em;

  --type-h2-size: 28px;
  --type-h2-line: 1.14;
  --type-h2-weight: 700;
  --type-h2-tracking: -0.018em;

  --type-h3-size: 20px;
  --type-h3-line: 1.25;
  --type-h3-weight: 700;
  --type-h3-tracking: -0.008em;

  --type-body-size: 16px;
  --type-body-line: 1.5;
  --type-body-weight: 500;
  --type-body-tracking: 0em;

  --type-body-sm-size: 14px;
  --type-body-sm-line: 1.45;
  --type-body-sm-weight: 500;
  --type-body-sm-tracking: 0em;

  --type-caption-size: 12px;
  --type-caption-line: 1.35;
  --type-caption-weight: 600;
  --type-caption-tracking: 0.01em;

  --type-label-size: 12px;
  --type-label-line: 1.25;
  --type-label-weight: 700;
  --type-label-tracking: 0.02em;
  --type-label-transform: none;

  --type-stat-size: 30px;
  --type-stat-line: 1;
  --type-stat-weight: 750;
  --type-stat-tracking: -0.035em;

  /* Motion */
  --ease-standard: cubic-bezier(0.2, 0.8, 0.2, 1);
  --ease-spring-soft: cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-enter: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-exit: cubic-bezier(0.7, 0, 0.84, 0);

  --duration-instant: 90ms;
  --duration-fast: 140ms;
  --duration-standard: 220ms;
  --duration-emphasis: 320ms;
  --duration-slow: 420ms;

  /* Use:
     button press = 90ms standard;
     card hover = 140ms standard;
     completion/check-in feedback = 220ms soft spring;
     modal/sheet = 320ms enter;
     celebratory sequence max = 420ms.
  */
}
```

**Implementation rules:** use `--radius-3` for standard cards and controls, `--radius-4` for hero modules or bottom sheets, and `--radius-full` only for compact chips, avatars, or progress dots. Use the expressive support colors for categories or celebration moments, but maintain a single primary interaction color: violet. Motion should feel encouraging, not distracting; animations should never block recording a habit or reading progress.


## P3 — Material effects & decoration policy ★ (core for SVGF-Design)

Material effects are earned when they clarify a product’s spatial model, reinforce its brand/material world, or make interaction easier to understand. They are arbitrary when they merely add perceived sophistication to an otherwise ordinary layout.

A useful test is:

> **If I remove this effect, does the interface lose meaningful depth, hierarchy, brand expression, or interaction feedback?**  
> If the answer is only “it looks less trendy,” I remove it.

---

# Decision framework: when an effect is earned

An effect is earned when all—or nearly all—of these are true:

1. **It has a semantic role**  
    It communicates containment, layering, focus, materiality, a changing state, atmosphere, or product identity.
    
2. **It fits the visual stance**  
    A spatial operating system, music tool, fashion editor, immersive consumer app, or visualization product may support richer materials. A dense claims-processing portal usually does not.
    
3. **It supports the product type**  
    For example:
    
    - Glass: floating controls over live visual content
    - Grain: a tactile, editorial, craft-oriented brand
    - Gradient: an atmospheric consumer product or a meaningful data field
    - Glow: a signal, selected state, or live/active object
    - Organic shape: a product related to creativity, wellbeing, biology, food, or movement
    - Refraction: an immersive, visual-first product where depth is part of the interaction model
4. **It is localized**  
    Rich materials belong on a few intentional surfaces—hero media, floating controls, selected objects, a compact identity moment—not every card on every screen.
    
5. **It preserves legibility and affordance**  
    Text contrast, focus rings, form readability, and touch targets cannot be sacrificed.
    
6. **It has a fallback**  
    Effects depending on blur, filters, animation, or high-end GPU work need a solid, readable baseline for unsupported or reduced-motion contexts.
    
7. **It performs within the interface’s interaction budget**  
    Avoid expensive animated filters, large blur regions, and lots of simultaneously composited layers in a utility interface.
    

---

# 1. Backdrop blur / glass

## When glass is earned

I use glass when the UI genuinely sits **above a changing visual plane**, and the transparency helps preserve context.

Good use cases:

- Floating controls over a map, canvas, video, 3D scene, or photo-led workspace
- A media player with artwork or video as the visual ground
- A mobile bottom sheet that should retain location/context beneath it
- A spatial/immersive operating-system-like experience
- A premium consumer product where depth and layering are central to the brand expression
- A temporary overlay, command palette, inspector, or utility rail

Less suitable use cases:

- Dense financial tables
- Medical record systems
- Administrative forms
- Documentation
- Inventory systems
- Dashboards where the “background” is simply gray app chrome

Glass is not earned merely because a card can be made translucent.

## Shippable CSS: restrained frosted surface

```css
:root {
  --glass-fill: rgb(255 255 255 / 68%);
  --glass-border: rgb(255 255 255 / 62%);
  --glass-highlight: rgb(255 255 255 / 45%);
  --glass-shadow:
    0 1px 1px rgb(15 23 42 / 4%),
    0 12px 30px rgb(15 23 42 / 12%);
  --glass-blur: 18px;
}

.glass-panel {
  background:
    linear-gradient(
      135deg,
      rgb(255 255 255 / 78%) 0%,
      rgb(255 255 255 / 56%) 100%
    );
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  box-shadow: var(--glass-shadow);

  -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(135%);
  backdrop-filter: blur(var(--glass-blur)) saturate(135%);
}

.glass-panel::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  border-radius: inherit;
  box-shadow: inset 0 1px 0 var(--glass-highlight);
}

@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
  .glass-panel {
    background: rgb(255 255 255 / 94%);
  }
}

@media (prefers-contrast: more) {
  .glass-panel {
    background: #FFFFFF;
    border-color: #94A3B8;
    -webkit-backdrop-filter: none;
    backdrop-filter: none;
  }
}
```

### Practical rules

- Use `blur(12px–24px)` for most UI. Values above `32px` often add GPU cost without useful improvement.
- Use glass over **visually rich or changing ground**, not a blank solid background.
- Keep a reasonably opaque fill. Nearly transparent glass often fails contrast and feels cosmetic.
- Use it for a **small number of elevated surfaces**: one header, one command palette, one inspector, or one bottom sheet.
- Do not blur every list item or standard dashboard card.

---

# 2. Gradients

## When gradients are earned

I use gradients when they encode one of the following:

### A. Atmospheric identity

Useful for consumer, creative, music, beauty, culture, entertainment, or emerging-technology products where atmosphere is part of the brand.

### B. Spatial depth

Useful behind floating controls, visual workspaces, onboarding, or a hero where a flat field would weaken the depth model.

### C. Meaningful data

Useful for heatmaps, intensity fields, range selections, progress, time-of-day, or environmental data—provided the gradient is labeled and accessible.

### D. Material change

Useful when showing a surface transition: light across metal, a translucent pane, a color-shifting object, or a simulated environmental field.

I do not use a gradient merely to make a hero feel “premium.”

## Shippable CSS: quiet editorial atmospheric field

```css
.hero-atmosphere {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  background:
    radial-gradient(
      90% 110% at 8% 4%,
      rgb(217 186 144 / 42%) 0%,
      rgb(217 186 144 / 0%) 64%
    ),
    radial-gradient(
      78% 100% at 96% 20%,
      rgb(103 137 124 / 28%) 0%,
      rgb(103 137 124 / 0%) 62%
    ),
    linear-gradient(
      135deg,
      #F6F0E7 0%,
      #EEE5D8 48%,
      #E7E0D7 100%
    );
}

.hero-atmosphere > * {
  position: relative;
  z-index: 1;
}
```

This is appropriate for a calm editorial or craft-commerce hero because it creates atmosphere without turning the whole page into a visibly synthetic “mesh gradient” product.

## Shippable CSS: data-intensity gradient

```css
.usage-scale {
  background: linear-gradient(
    90deg,
    #D9F0EC 0%,
    #8FD0C1 30%,
    #4F9E8D 58%,
    #E9B44C 78%,
    #C95742 100%
  );
  border: 1px solid rgb(29 42 54 / 18%);
  border-radius: 9999px;
  height: 10px;
}

.usage-scale-labels {
  display: flex;
  justify-content: space-between;
  color: #4C5B64;
  font-size: 12px;
  line-height: 16px;
}
```

This is earned when the colors represent a documented numeric scale, such as consumption intensity or risk. It should not be the only way the user learns the state; labels, values, or patterns should remain available.

---

# 3. Noise / grain texture

## When grain is earned

I use grain when the visual stance has a legitimate tactile, analog, printed, photographic, or material reference.

Good fits:

- Editorial brands
- Artisan commerce
- Food, beverage, fragrance, hospitality
- Film, music, and cultural products
- Archival interfaces
- Campaign sites with intentional physicality
- Backgrounds that would otherwise look unnaturally flat or digitally sterile

Poor fits:

- Dense data products
- Forms-heavy enterprise tools
- Medical, financial, legal, or accessibility-critical core workflows
- Small, repetitive UI surfaces where texture creates visual fatigue

Grain should sit **behind content**, remain subtle, and never interfere with reading. It is surface atmosphere, not information.

## Shippable CSS: static SVG noise texture

```css
.textured-surface {
  position: relative;
  background: #F4EEE4;
  isolation: isolate;
}

.textured-surface::after {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  opacity: 0.055;
  mix-blend-mode: multiply;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.78' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.85'/%3E%3C/svg%3E");
  background-size: 180px 180px;
}

.textured-surface > * {
  position: relative;
  z-index: 1;
}

@media (prefers-contrast: more) {
  .textured-surface::after {
    display: none;
  }
}
```

### Practical values

- Opacity: `0.025–0.08` for backgrounds
- Do not animate the noise
- Use a fixed repeated tile, generally `128px–256px`
- Use only on a page or major section—not on every card
- Disable it in high-contrast contexts

---

# 4. Glow

## When glow is earned

I use glow to communicate **energy, activation, focus, liveness, or depth**, not just to make controls feel futuristic.

Good fits:

- A selected object in a visual workspace
- A live-recording indicator
- Music/audio tools
- Developer or infrastructure monitoring with a meaningful active signal
- Gaming, social, or expressive consumer tools
- A focused object in a dark, immersive interface
- A visual brand with emitted-light material logic

Poor fits:

- Every CTA
- Every dashboard metric
- Default form inputs
- Serious high-density tools with no luminous visual metaphor
- Multiple different glow colors competing for attention

## Shippable CSS: selected “live” control

```css
.live-control {
  color: #F8FAFC;
  background: #263A82;
  border: 1px solid rgb(161 180 255 / 72%);
  border-radius: 10px;
  box-shadow:
    inset 0 1px 0 rgb(255 255 255 / 14%),
    0 0 0 1px rgb(92 111 255 / 18%),
    0 0 18px rgb(92 111 255 / 26%),
    0 0 42px rgb(92 111 255 / 14%);
  transition:
    background-color 160ms cubic-bezier(0.2, 0, 0, 1),
    border-color 160ms cubic-bezier(0.2, 0, 0, 1),
    box-shadow 160ms cubic-bezier(0.2, 0, 0, 1);
}

.live-control:focus-visible {
  outline: 3px solid #F4C95D;
  outline-offset: 3px;
}
```

Glow remains an enhancement; the selected state is also clear through fill, label, border, and focus behavior.

---

# 5. Organic blob shapes

## When organic forms are earned

I use organic shapes when they relate to the product’s subject matter or stance:

- Wellness, movement, creativity, youth, food, biology, gardening, ecology
- A brand with soft, human, handmade, playful, or fluid identity
- An onboarding or campaign experience that needs a compositional counterweight
- A visual system derived from natural forms, collage, or physical materials

I avoid them in:

- Precision systems
- Serious operator dashboards
- Products where geometry communicates reliability and exactness
- Interfaces where organic forms would compete with dense content

The important distinction is between a **designed organic form** and a random CSS blob added to an empty hero.

## Shippable CSS: deliberate organic backdrop

```css
.organic-field {
  position: absolute;
  width: 420px;
  aspect-ratio: 1;
  right: -110px;
  top: 48px;
  pointer-events: none;
  opacity: 0.9;
  background:
    radial-gradient(circle at 28% 30%, #FFE5A7 0 14%, transparent 14.5%),
    radial-gradient(circle at 68% 72%, #BCE8D7 0 20%, transparent 20.5%),
    #CFC3FF;
  border-radius: 58% 42% 51% 49% / 42% 55% 45% 58%;
  transform: rotate(-12deg);
}

@media (max-width: 700px) {
  .organic-field {
    width: 260px;
    right: -104px;
    top: 76px;
    opacity: 0.58;
  }
}
```

This is appropriate behind a single onboarding message in a playful habit app because it provides a stable visual identity and frames the content. It would be inappropriate behind every dashboard panel.

## Shippable SVG: controlled organic path

For a brand illustration or a hero composition, I prefer an explicit SVG path over unpredictable random generation:

```svg
<svg
  viewBox="0 0 560 500"
  fill="none"
  xmlns="http://www.w3.org/2000/svg"
  aria-hidden="true"
>
  <path
    d="M116 82C192 5 337 25 422 96C506 166 504 292 426 378C350 462 200 481 112 404C21 324 40 159 116 82Z"
    fill="#CFC3FF"
  />
  <path
    d="M204 102C247 75 316 86 353 127C390 167 379 229 337 267C295 305 224 314 181 276C137 238 161 129 204 102Z"
    fill="#FFE5A7"
  />
</svg>
```

The shape is chosen and reviewable. It is not random decoration generated by code at runtime.

---

# 6. Displacement and refraction

## When displacement/refraction is earned

This is the most specialized category. I use it only when the product’s visual model is explicitly immersive or material:

- A spatial or visual creative tool
- A media experience
- A high-end campaign or editorial site
- A weather, water, optics, glass, or scientific visualization context
- A product whose brand identity explicitly uses liquid, lens, prism, or refractive materials
- A highly controlled hero/transition—not core transactional UI

I would not use it for ordinary cards, forms, tables, or navigation. It can be expensive, visually distracting, and difficult to make accessible.

## Shippable SVG: subtle static liquid-glass refraction

```svg
<svg
  width="0"
  height="0"
  aria-hidden="true"
  focusable="false"
  xmlns="http://www.w3.org/2000/svg"
>
  <filter id="liquid-glass" x="-20%" y="-20%" width="140%" height="140%">
    <feTurbulence
      type="fractalNoise"
      baseFrequency="0.012 0.018"
      numOctaves="2"
      seed="18"
      result="noise"
    />
    <feDisplacementMap
      in="SourceGraphic"
      in2="noise"
      scale="7"
      xChannelSelector="R"
      yChannelSelector="G"
    />
  </filter>
</svg>
```

```css
.liquid-glass-art {
  border-radius: 28px;
  overflow: hidden;
  filter: url("#liquid-glass");
  transform: translateZ(0);
}
```

I would use this on a **non-essential hero artwork or visual ornament**, not on text or an interactive control. Distorting text harms legibility and distorting controls can make hit targets feel disconnected from their visual boundaries.

## More practical alternative: CSS glass, not true refraction

For most product UI, a conventional translucent surface with backdrop blur is preferable:

```css
.prismatic-sheet {
  background:
    linear-gradient(
      140deg,
      rgb(255 255 255 / 74%) 0%,
      rgb(190 219 255 / 36%) 42%,
      rgb(238 205 255 / 32%) 100%
    );
  border: 1px solid rgb(255 255 255 / 66%);
  box-shadow:
    inset 0 1px 0 rgb(255 255 255 / 58%),
    0 18px 44px rgb(37 38 74 / 16%);
  -webkit-backdrop-filter: blur(20px) saturate(145%);
  backdrop-filter: blur(20px) saturate(145%);
}
```

This produces a legible, stable glass-like surface without distorting the content behind it.

---

# Do I use SVG filter primitives in UI work?

Yes, but selectively.

SVG filters are legitimate tools. The important question is not whether they are “allowed”; it is whether they are serving the interaction and visual system without harming performance, accessibility, or maintainability.

## `feTurbulence`

**Yes, usually static only.**  
Useful for subtle grain, paper texture, cloud-like visual fields, or a background material.

```svg
<filter id="paper-grain">
  <feTurbulence
    type="fractalNoise"
    baseFrequency="0.72"
    numOctaves="3"
    stitchTiles="stitch"
    seed="24"
  />
  <feColorMatrix
    type="matrix"
    values="
      0 0 0 0 0.18
      0 0 0 0 0.15
      0 0 0 0 0.12
      0 0 0 0.13 0
    "
  />
</filter>
```

Use it as a background-only texture at low opacity. I do not animate it continuously in standard UI.

---

## `feDisplacementMap`

**Rarely, and only for non-essential artwork.**  
Useful for a static refractive hero illustration, water-like distortion, or a highly specific campaign effect.

```svg
<filter id="soft-displace" x="-10%" y="-10%" width="120%" height="120%">
  <feTurbulence
    type="turbulence"
    baseFrequency="0.01"
    numOctaves="2"
    seed="11"
    result="texture"
  />
  <feDisplacementMap
    in="SourceGraphic"
    in2="texture"
    scale="5"
    xChannelSelector="R"
    yChannelSelector="B"
  />
</filter>
```

I do **not** put displacement filters on body text, navigation, primary buttons, tables, or anything whose visual boundary must remain exact.

---

## `feGaussianBlur` + `feColorMatrix` for “goo”

**Very rarely.**  
This can work in a playful, expressive consumer experience—such as a single animated completion illustration, a nonessential loading motif, or a campaign graphic. It is usually too loud and too computationally expensive for product UI.

```svg
<svg
  viewBox="0 0 320 140"
  xmlns="http://www.w3.org/2000/svg"
  aria-hidden="true"
>
  <defs>
    <filter id="goo" color-interpolation-filters="sRGB">
      <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
      <feColorMatrix
        in="blur"
        mode="matrix"
        values="
          1 0 0 0 0
          0 1 0 0 0
          0 0 1 0 0
          0 0 0 22 -9
        "
        result="goo"
      />
      <feComposite in="SourceGraphic" in2="goo" operator="atop" />
    </filter>
  </defs>

  <g filter="url(#goo)">
    <circle cx="96" cy="70" r="36" fill="#7E6BEA" />
    <circle cx="156" cy="70" r="36" fill="#FFB94D" />
    <circle cx="216" cy="70" r="36" fill="#82D7B2" />
  </g>
</svg>
```

This would be an illustration, not a structural component style.

---

## `feSpecularLighting`

**Almost never for interface components.**

It can create a convincing embossed, wet, or lit material, but it is difficult to control across displays, can make text harder to read, and often looks like a novelty effect when applied to UI chrome.

I might use it for:

- A one-off 3D-ish badge or seal
- A decorative product visualization
- A game or music visualizer
- A non-interactive hero material study

I would not use it for buttons, cards, inputs, or navigation.

```svg
<filter id="soft-specular" x="-20%" y="-20%" width="140%" height="140%">
  <feGaussianBlur in="SourceAlpha" stdDeviation="2" result="blur" />
  <feSpecularLighting
    in="blur"
    surfaceScale="3"
    specularConstant="0.45"
    specularExponent="18"
    lighting-color="#FFFFFF"
    result="specular"
  >
    <feDistantLight azimuth="225" elevation="50" />
  </feSpecularLighting>
  <feComposite
    in="specular"
    in2="SourceAlpha"
    operator="in"
    result="specularClip"
  />
  <feComposite
    in="SourceGraphic"
    in2="specularClip"
    operator="arithmetic"
    k1="0"
    k2="1"
    k3="0.34"
    k4="0"
  />
</filter>
```

---

## `feDropShadow`

**Yes, commonly—but gently.**  
For SVG icons, marks, floating objects, and illustrations, it can be better than trying to fake a shadow with duplicate paths.

```svg
<filter id="icon-shadow" x="-30%" y="-30%" width="160%" height="160%">
  <feDropShadow
    dx="0"
    dy="5"
    stdDeviation="5"
    flood-color="#172033"
    flood-opacity="0.18"
  />
</filter>
```

I use one coherent shadow, not stacks of several unrelated effects.

---

# Before/after: an effect that improved a design

## Scenario: mobile video-editing workspace

The app’s main surface is a live video preview. The timeline, inspector, and transport controls need to overlay it without severing the user’s connection to the visual content.

## Before: opaque utility slab

```css
.transport-controls {
  position: absolute;
  right: 16px;
  bottom: 16px;
  width: min(360px, calc(100vw - 32px));
  padding: 12px;
  color: #F8FAFC;
  background: #15202B;
  border: 1px solid #314152;
  border-radius: 16px;
}
```

### Why it was weaker

- The controls feel detached from the video canvas.
- The solid panel creates a heavy black slab.
- It hides too much of the preview.
- The composition reads as “a dashboard placed over a video,” not one spatial workspace.

## After: glass transport surface

```css
.transport-controls {
  position: absolute;
  right: 16px;
  bottom: 16px;
  width: min(360px, calc(100vw - 32px));
  padding: 12px;
  color: #F8FAFC;

  background:
    linear-gradient(
      135deg,
      rgb(17 27 40 / 76%) 0%,
      rgb(17 27 40 / 58%) 100%
    );
  border: 1px solid rgb(226 232 240 / 24%);
  border-radius: 16px;
  box-shadow:
    inset 0 1px 0 rgb(255 255 255 / 10%),
    0 14px 32px rgb(0 0 0 / 24%);

  -webkit-backdrop-filter: blur(18px) saturate(125%);
  backdrop-filter: blur(18px) saturate(125%);
}

.transport-controls:focus-within {
  border-color: rgb(148 201 255 / 72%);
}
```

### Why the glass is earned here

- There is meaningful, changing visual content beneath it.
- The blur preserves the spatial relationship with the preview.
- The surface remains opaque enough for controls and labels to be legible.
- The panel is a localized, floating utility object—not a default treatment applied to every UI region.
- A solid fallback still works.

---

# Before/after: an effect I would remove

## Scenario: B2B delivery-performance dashboard

The interface includes order metrics, late-delivery exceptions, and a dense operations table.

## Before: decorative animated gradient behind the dashboard

```css
.dashboard-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at 20% 10%, #B2A4FF 0%, transparent 35%),
    radial-gradient(circle at 80% 20%, #7BE7D0 0%, transparent 38%),
    linear-gradient(135deg, #F5F3FF, #E7F9F5);
  background-size: 160% 160%;
  animation: drift 12s ease-in-out infinite alternate;
}

@keyframes drift {
  from { background-position: 0% 0%; }
  to { background-position: 100% 100%; }
}
```

### Why it is arbitrary

- The product is operational and data-dense; the gradient adds no semantic information.
- It lowers the perceived seriousness and clarity of alerts and metrics.
- It creates subtle contrast variation behind white cards.
- Animation consumes attention without communicating a state change.
- It makes the same dashboard feel closer to a marketing page than a working tool.

## After: stable precision surface

```css
.dashboard-shell {
  min-height: 100vh;
  background: #F4F6F7;
}

.dashboard-grid {
  background-image:
    linear-gradient(rgb(22 32 36 / 4%) 1px, transparent 1px),
    linear-gradient(90deg, rgb(22 32 36 / 4%) 1px, transparent 1px);
  background-size: 32px 32px;
  background-position: -1px -1px;
}

.dashboard-panel {
  background: #FFFFFF;
  border: 1px solid #C7D0D2;
  border-radius: 6px;
  box-shadow: none;
}
```

### Why removing the effect improved the design

- The page becomes calmer and easier to scan.
- Metrics and alerts regain visual priority.
- The subtle grid supports the “operational system” stance without competing with content.
- The product feels more trustworthy and less decorative.
- The visual treatment now has a role: it reinforces measurement, structure, and precision.

---

# Practical rule of thumb

I use rich material effects when the design has a real answer to all three questions:

1. **What does this effect mean in this product?**
2. **Why is it placed on this surface rather than everywhere?**
3. **What remains if the effect is unsupported, reduced, or removed?**

If the answers are strong, glass, grain, gradients, glow, organic forms, and even carefully controlled SVG filters can produce an excellent, sophisticated interface.

If the answers are weak, the same effects become generic visual noise.

## P4 — Typography operative detail

## 1. Font sources and the actual type library I select from

I do **not** assume there is one universal bundled font library. The selection order is:

1. **Existing project or design-system fonts** — if a kit, brand system, or imported Figma file specifies fonts, those are the source of truth.
2. **Project-provided local fonts** — if the repository includes licensed font files, use those.
3. **Google Fonts** — the normal fallback for self-contained web UI work in this environment.
4. **System fallbacks** — always defined after the preferred family.

For a new project without an existing font system, I draw from a deliberately curated set rather than picking random Google Fonts.

### Display serif / editorial serif

|Typeface|What I use it for|Register|
|---|---|---|
|**Newsreader**|Editorial products, culture, research, hospitality, quiet premium brands|Literary, warm, contemporary editorial|
|**Fraunces**|Craft commerce, food, beauty, expressive premium consumer work|Tactile, playful, materially rich|
|**Source Serif 4**|Institutional, educational, civic, publishing-adjacent products|Scholarly, trustworthy, durable|
|**DM Serif Display**|Bold campaign moments, selective large headlines|Assertive, compact, poster-like|
|**Literata**|Reading-heavy experiences and long-form publishing|Bookish, measured, serious|
|**Libre Baskerville**|Formal, classical, restrained identity moments|Traditional, dignified|
|**Cormorant Garamond**|Only when a genuinely high-fashion or historical brief calls for it|Romantic, dramatic; otherwise avoided|
|**Bodoni Moda**|Fashion/editorial campaigns with sufficient scale and contrast|Sharp, high-contrast, image-led|

### Humanist and readable UI sans

|Typeface|What I use it for|Register|
|---|---|---|
|**Source Sans 3**|Institutional systems, forms, content-heavy UI, civic products|Clear, calm, durable|
|**Public Sans**|Governmental, public-interest, operational, trustworthy products|Neutral, civic, highly functional|
|**Atkinson Hyperlegible Next**|Accessibility-conscious products, reading-heavy utility interfaces|Open, highly legible, human|
|**Nunito Sans**|Friendly but structured consumer products|Warm, approachable|
|**Manrope**|Contemporary product interfaces with geometric restraint|Clean, confident, modern|
|**Albert Sans**|Retail, craft, editorial-commerce hybrids|Neutral but polished|
|**DM Sans**|Consumer products and approachable utility UI|Friendly, balanced, compact|
|**Work Sans**|Editorial/product hybrids and small-screen UI|Practical, slightly humanist|

### Grotesk / neo-grotesk / rational sans

|Typeface|What I use it for|Register|
|---|---|---|
|**Archivo**|Operational tools, data products, technical and industrial systems|Condensed energy, functional precision|
|**Archivo Narrow**|Metrics, data headers, compact utility labeling|Industrial, compact|
|**IBM Plex Sans**|Only for products where its technical/enterprise character is genuinely correct|Technical, established, engineered|
|**Barlow**|Transport, engineering, industrial interfaces|Mechanical, practical|
|**Barlow Condensed**|Timelines, dense dashboards, utility display labels|Technical, high-density|
|**Roboto Flex**|Systems that benefit from variable-width and variable-weight control|Functional, adaptable|
|**Commissioner**|Modern enterprise with more character than a default sans|Formal, composed|
|**Instrument Sans**|Contemporary culture, design, fashion, product work|Crisp, current, not overly neutral|

### Geometric sans

|Typeface|What I use it for|Register|
|---|---|---|
|**Outfit**|Youth-oriented consumer products and direct mobile UI|Crisp, optimistic|
|**Plus Jakarta Sans**|Contemporary consumer/product systems|Clean, rounded without becoming childish|
|**Sora**|Modern digital products, selective tech positioning|Geometric, distinct|
|**Figtree**|Friendly applications and general consumer UI|Open, easy, compact|
|**Lexend**|Readability-oriented, consumer education, accessible interfaces|Spacious, clear|
|**Urbanist**|Lifestyle, consumer, retail, mobile-first products|Smooth, contemporary|
|**Cabin**|Warm, functional, less-polished digital products|Human, practical|

### Expressive display sans

|Typeface|What I use it for|Register|
|---|---|---|
|**Bricolage Grotesque**|Playful consumer, creative tools, energetic campaigns|Expressive, contemporary|
|**Unbounded**|Selective futuristic, music, gaming, experimental work|Technical, graphic, bold|
|**Climate Crisis**|Large-scale climate/civic campaign moments only|Compressed, activist, emphatic|
|**Familjen Grotesk**|Cultural, editorial, and branded product pages|Slightly idiosyncratic, composed|
|**Red Hat Display**|Friendly premium-tech or creative products|Warm, broad, modern|
|**Anybody**|Youth, movement, playful modular visual identities|Variable, elastic, expressive|

### Slab serif / utility serif

|Typeface|What I use it for|Register|
|---|---|---|
|**Roboto Slab**|Education, documentation, trustworthy systems|Practical, stable|
|**Bitter**|Publishing, reading, editorial information density|Bookish, robust on screen|
|**Zilla Slab**|News, media, civic, structured editorial systems|Direct, readable|
|**Arvo**|Selective utility, vintage-tech, or printed-material references|Strong, compact|
|**Space Mono**|Only when an explicitly retro/technical stance requires it|Technical, conspicuous; not a default|

### Mono

|Typeface|What I use it for|Register|
|---|---|---|
|**Geist Mono**|Modern data labels, IDs, timestamps, developer-adjacent tools|Clean, restrained|
|**DM Mono**|Editorial metadata, archive references, measured technical labels|Soft, intellectual|
|**Azeret Mono**|Craft-commerce metadata, experimental editorial work|Distinctive, characterful|
|**IBM Plex Mono**|Existing enterprise systems or IBM/Plex-aligned work|Technical, structured|
|**Roboto Mono**|Institutional data and accessibility-oriented utility UI|Neutral, familiar|
|**Fira Mono**|Playful consumer data, small code-like labels|Friendly, technical|
|**JetBrains Mono**|Code-heavy and developer products|Highly legible, developer-native|
|**Fragment Mono**|Graphic/experimental metadata treatment|Distinctive, editorial|

### Practical selection rule

I normally use:

- **One family** for a dense operational product, sometimes plus mono.
- **Two families** for most landing pages: display + UI sans.
- **Three families** only when there is a real metadata/data role: display + UI sans + mono.

I do not add a third family just because “three fonts feels more designed.”

---

## 2. Ten pairings I consider strong

### 1. Newsreader + Public Sans + DM Mono

|Field|Value|
|---|---|
|**Stance**|Quiet editorial, cultural institution, research platform, considered hospitality|
|**Families**|Newsreader / Public Sans / DM Mono|
|**Why it works**|Newsreader gives literary warmth without looking like a generic fashion-serif choice. Public Sans keeps controls and body copy extremely clear. DM Mono gives metadata, dates, archive IDs, or issue numbers a deliberate structural role.|
|**Use**|Large headlines in Newsreader; all UI in Public Sans; only metadata/data in DM Mono.|

### 2. Fraunces + Albert Sans + Azeret Mono

|Field|Value|
|---|---|
|**Stance**|Contemporary craft commerce, food, fragrance, hospitality, small-batch retail|
|**Families**|Fraunces / Albert Sans / Azeret Mono|
|**Why it works**|Fraunces brings material richness and controlled personality. Albert Sans keeps commerce UI elegant and readable. Azeret Mono gives SKU, quantity, origin, batch, or product-spec metadata an unusual but restrained voice.|
|**Use**|Fraunces for hero/product storytelling; Albert Sans for shopping UI; Azeret Mono for product facts only.|

### 3. Archivo + Manrope + Geist Mono

|Field|Value|
|---|---|
|**Stance**|Precision industrial, logistics, analytics, operational dashboard|
|**Families**|Archivo / Manrope / Geist Mono|
|**Why it works**|Archivo has compact, durable display energy; Manrope keeps dense controls comfortable; Geist Mono makes values, dates, IDs, and measurements scan cleanly.|
|**Use**|Archivo for section headers and key metrics; Manrope for UI and body; Geist Mono for data.|

### 4. Source Serif 4 + Source Sans 3 + Roboto Mono

|Field|Value|
|---|---|
|**Stance**|Institutional calm, education, healthcare, civic service, legal or public-interest products|
|**Families**|Source Serif 4 / Source Sans 3 / Roboto Mono|
|**Why it works**|The families have compatible proportions and an established, trustworthy tone. The serif supports longer reading and formal headings; the sans delivers durable interface clarity.|
|**Use**|Serif for key headings and reading moments; sans for nearly all interface elements; mono only for reference numbers, dates, and structured data.|

### 5. Bricolage Grotesque + DM Sans

|Field|Value|
|---|---|
|**Stance**|Playful consumer, habit tracking, youth products, social or wellness tools|
|**Families**|Bricolage Grotesque / DM Sans|
|**Why it works**|Bricolage creates a lively, recognisable display voice without needing stickers, blobs, or excessive color. DM Sans is friendly and functional at small mobile sizes.|
|**Use**|Bricolage for key prompts, completion moments, statistics, and onboarding; DM Sans for navigation, forms, and all sustained reading.|

### 6. Instrument Sans + Newsreader

|Field|Value|
|---|---|
|**Stance**|Contemporary gallery, fashion, design studio, portfolio, culture-led product|
|**Families**|Instrument Sans / Newsreader|
|**Why it works**|Instrument Sans is crisp and current; Newsreader adds a quieter literary counterpoint. The contrast feels more deliberate than a standard “serif headline + Inter body” combination.|
|**Use**|Instrument Sans for UI and compact headers; Newsreader for large editorial statements, case-study titles, or selected pull quotes.|

### 7. Barlow + Barlow Condensed + IBM Plex Mono

|Field|Value|
|---|---|
|**Stance**|Transit, industrial operations, sports data, transport, manufacturing|
|**Families**|Barlow / Barlow Condensed / IBM Plex Mono|
|**Why it works**|This is a tightly related utility system. Barlow provides an accessible working UI, Barlow Condensed increases density in metrics and timetable-like areas, and Plex Mono makes technical identifiers distinct.|
|**Use**|Barlow for standard UI; Barlow Condensed for big metric values and compact headers; mono for serials, schedule data, and IDs.|

### 8. Literata + Work Sans + DM Mono

|Field|Value|
|---|---|
|**Stance**|Journal, long-form reading product, archival catalogue, knowledge platform|
|**Families**|Literata / Work Sans / DM Mono|
|**Why it works**|Literata is optimized for reading and works well for intellectual content. Work Sans remains stable at small UI sizes. DM Mono turns references and metadata into a calm system rather than visual clutter.|
|**Use**|Literata for articles and primary titles; Work Sans for interface/navigation; mono for citations, issue references, and timestamps.|

### 9. Outfit + Figtree

|Field|Value|
|---|---|
|**Stance**|Friendly digital consumer, mobile-first utility, lifestyle product, simple onboarding|
|**Families**|Outfit / Figtree|
|**Why it works**|Both are open and contemporary, but Outfit is more display-forward while Figtree handles interface text naturally. It is clean and optimistic without feeling like a default productivity app.|
|**Use**|Outfit for hero prompts and numeric summaries; Figtree for all standard UI and body copy.|

### 10. DM Serif Display + Commissioner + Geist Mono

|Field|Value|
|---|---|
|**Stance**|Premium financial planning, private client portal, boutique consultancy, refined B2B|
|**Families**|DM Serif Display / Commissioner / Geist Mono|
|**Why it works**|DM Serif Display provides selective gravitas; Commissioner is formal without being sterile; Geist Mono gives financial values and dates a precise utility layer.|
|**Use**|Use the serif sparingly and at large sizes. Commissioner must carry the actual application. Mono is for amounts, dates, document IDs, and structured values.|

---

## 3. Faces and pairings I treat as overused AI defaults

These are not banned. They become a problem when used without a reason.

### Overused default faces

|Typeface|Why I avoid using it automatically|
|---|---|
|**Inter**|Excellent UI font, but it is now the default visual texture of a huge amount of product UI. Use it when an existing system uses it or when maximum neutrality is truly right—not because nothing else was considered.|
|**Space Grotesk**|Frequently used to signal “modern AI/startup.” It has become highly recognizable as a generated-design shortcut.|
|**Space Mono**|Often added as decorative “technical flavor” even when there is no real data, code, or metadata role.|
|**IBM Plex Mono**|Strong font, but easy to overuse as a generic “serious technology” signal.|
|**Syne**|Commonly used as a fast route to “creative agency” or “experimental brand” styling.|
|**Cormorant Garamond**|Repeatedly used to imply luxury, fashion, or editorial refinement, often without a typographic rationale.|
|**Bebas Neue**|A common shortcut for impact and loudness; it can flatten hierarchy and become poster-template-like.|
|**Playfair Display**|Often used for “premium feminine” styling without enough specificity. It is valid when the editorial/fashion register is actually appropriate.|
|**Poppins**|Can create a generic friendly-app look when used indiscriminately.|
|**Montserrat**|Widely used, often associated with generic marketing-site typography.|
|**Raleway**|Still usable in selective display roles, but often reads as template-era startup or agency typography.|
|**Lato**|Readable, but can make a design feel like an undifferentiated early SaaS product.|
|**Roboto**|Extremely functional, but visually neutral to the point of sameness when no Google/Android/system context motivates it.|

### Overused pairings

|Pairing|Why I avoid it by default|
|---|---|
|**Inter + Space Grotesk**|The common “AI SaaS” pairing.|
|**Playfair Display + Inter**|A frequent “editorial luxury landing page” shortcut.|
|**Cormorant Garamond + Inter**|Often produces generic warm-premium styling.|
|**Poppins + Poppins**|Gives an overly uniform, generic app-template rhythm.|
|**Space Grotesk + Space Mono**|A common startup/developer-product visual shorthand.|
|**DM Sans + DM Mono**|Strong pairing, but easy to make generic unless the product and composition give it personality.|
|**Bebas Neue + Montserrat**|Common poster/fitness/campaign formula.|
|**Syne + Manrope**|Often used as a ready-made “creative tech” identity without deeper structural choices.|

### The actual rule

I do not reject a face because it is popular. I reject it when it is being used as a substitute for art direction.

---

## 4. Actual type scale: dense operational tool

This is the kind of scale I would ship for a desktop-first operational tool with tables, alerts, activity logs, filters, key metrics, and compact navigation.

### Families

```css
--font-display: "Archivo", "Helvetica Neue", Arial, sans-serif;
--font-ui: "Manrope", "Helvetica Neue", Arial, sans-serif;
--font-mono: "Geist Mono", "SFMono-Regular", Consolas, monospace;
```

### Desktop scale

|Role|Family|Size|Weight|Line-height|Tracking|Case|
|---|---|---|---|---|---|---|
|Display metric|Archivo|48px / 3rem|650|1.00|-0.030em|Sentence case / numeral|
|Page title|Archivo|32px / 2rem|650|1.12|-0.022em|Sentence case|
|Section heading|Archivo|22px / 1.375rem|630|1.20|-0.012em|Sentence case|
|Card heading|Manrope|16px / 1rem|700|1.30|-0.006em|Sentence case|
|Body|Manrope|14px / 0.875rem|450|1.50|0em|Sentence case|
|Body compact|Manrope|13px / 0.8125rem|450|1.46|0em|Sentence case|
|Table value|Manrope|13px / 0.8125rem|520|1.35|0em|Sentence case|
|Table metadata|Geist Mono|12px / 0.75rem|500|1.35|-0.010em|Sentence case|
|Caption|Manrope|12px / 0.75rem|520|1.40|0.005em|Sentence case|
|Utility label|Manrope|11px / 0.6875rem|700|1.25|0.075em|Uppercase|
|Tiny status|Geist Mono|10px / 0.625rem|550|1.20|0.030em|Uppercase only if very short|

### Mobile adjustments

|Role|Mobile size|
|---|---|
|Display metric|36px / 2.25rem|
|Page title|28px / 1.75rem|
|Section heading|20px / 1.25rem|
|Card heading|16px / 1rem|
|Body|14px / 0.875rem|
|Body compact|13px / 0.8125rem|
|Caption|12px / 0.75rem|

### Operational-tool rules

- Use the display style for a key number, primary dashboard statement, or major page title—not every card.
- Use UI sans for all ordinary controls, table text, buttons, filters, navigation, and descriptions.
- Use mono only for values where fixed-width or technical structure improves scanning: dates, timestamps, IDs, duration, percentages, equipment codes, or live readings.
- Keep body text at `14px` minimum for dense desktop UI unless there is a strong reason to use `13px`.
- Avoid all-caps headings. Use uppercase only for short structural labels.
- Use tabular numerals when supported for financial values, measures, and data tables.

```css
.tabular-data {
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums slashed-zero;
}
```

---

## 5. Actual type scale: editorial landing page

This is the kind of scale I would ship for a desktop-first landing page with a strong hero, selective image use, narrative sections, and spacious pacing.

### Families

```css
--font-display: "Newsreader", Georgia, serif;
--font-ui: "Public Sans", "Helvetica Neue", Arial, sans-serif;
--font-mono: "DM Mono", "SFMono-Regular", Consolas, monospace;
```

### Desktop scale

|Role|Family|Size|Weight|Line-height|Tracking|Case|
|---|---|---|---|---|---|---|
|Hero display|Newsreader|72px / 4.5rem|500|0.96|-0.038em|Sentence case|
|Display / major statement|Newsreader|56px / 3.5rem|500|1.00|-0.032em|Sentence case|
|H1|Newsreader|44px / 2.75rem|520|1.05|-0.024em|Sentence case|
|H2|Newsreader|32px / 2rem|540|1.13|-0.018em|Sentence case|
|H3|Public Sans|21px / 1.3125rem|650|1.28|-0.008em|Sentence case|
|Lead|Public Sans|20px / 1.25rem|420|1.48|-0.006em|Sentence case|
|Body|Public Sans|16px / 1rem|400|1.62|-0.002em|Sentence case|
|Body small|Public Sans|14px / 0.875rem|420|1.55|0em|Sentence case|
|Caption|Public Sans|12px / 0.75rem|550|1.45|0.008em|Sentence case|
|Eyebrow / section label|Public Sans|11px / 0.6875rem|700|1.25|0.120em|Uppercase|
|Image metadata|DM Mono|11px / 0.6875rem|500|1.40|0.010em|Sentence case|
|Button label|Public Sans|13px / 0.8125rem|650|1.00|0em|Sentence case|

### Mobile adjustments

|Role|Mobile size|
|---|---|
|Hero display|48px / 3rem|
|Display / major statement|40px / 2.5rem|
|H1|34px / 2.125rem|
|H2|28px / 1.75rem|
|H3|20px / 1.25rem|
|Lead|18px / 1.125rem|
|Body|16px / 1rem|

### Editorial-landing-page rules

- Use the largest display size for one primary moment, usually the hero.
- Do not make every section heading look like a hero headline.
- Keep display line-height compact but not mechanically tight: typically `0.96–1.08`.
- Keep body line-height generous: typically `1.55–1.65`.
- Use the mono face only for image captions, article-like metadata, dates, labels, or numbered sections.
- Avoid justified text on the web.
- Keep longer body copy to a readable measure, generally around `60–72ch`.

```css
.editorial-copy {
  max-width: 68ch;
  font-family: var(--font-ui);
  font-size: 16px;
  font-weight: 400;
  line-height: 1.62;
  letter-spacing: -0.002em;
}
```

---

## 6. Case behavior: exactly when I use uppercase labels

I use uppercase sparingly. Uppercase is a **structural signal**, not an everyday text style.

## Use uppercase when all of the following are true

1. The text is short.
2. It functions as metadata, taxonomy, a section kicker, or a compact utility label.
3. It is not a sentence, paragraph, or long navigation item.
4. Its role benefits from visual separation rather than conversational readability.
5. The selected font remains legible in uppercase at that size.

### Good uppercase uses

- `PROJECT STATUS`
- `Q3 PERFORMANCE`
- `SHOT 04 · DAY 12`
- `UPDATED 14 MIN AGO`
- `SAVED VIEWS`
- `MEMBER BENEFITS`
- `FEATURED WORK`
- `OPEN ISSUES`
- `SELECTED RANGE`
- `LIVE`

### Avoid uppercase for

- Primary navigation with long labels
- Main page titles
- Body copy
- Multi-word buttons such as `CREATE A NEW PROJECT`
- Form field labels with long descriptions
- Error messages
- Helper text
- Dense mobile navigation
- Large blocks of data labels
- Anything that needs quick, relaxed reading

## Exact uppercase values

### Standard UI uppercase label

```css
.label-uppercase {
  font-family: "Manrope", "Helvetica Neue", Arial, sans-serif;
  font-size: 11px;
  font-weight: 700;
  line-height: 1.25;
  letter-spacing: 0.075em;
  text-transform: uppercase;
}
```

Use for dense operational tools, compact cards, filter-group labels, small dashboard section labels, and status headings.

### Editorial eyebrow

```css
.editorial-eyebrow {
  font-family: "Public Sans", "Helvetica Neue", Arial, sans-serif;
  font-size: 11px;
  font-weight: 700;
  line-height: 1.25;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
```

Use for article categories, story context, section kickers, campaign labels, and image-series identification.

### Tiny mono utility status

```css
.mono-status {
  font-family: "Geist Mono", "SFMono-Regular", Consolas, monospace;
  font-size: 10px;
  font-weight: 550;
  line-height: 1.2;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}
```

Use only for short values such as `LIVE`, `SYNCED`, `PAUSED`, `DRAFT`, `LOCKED`, or `OFFLINE`.

### Mobile adjustment

Do not shrink ordinary uppercase labels below `10px`. If there is not enough space for an `11px` uppercase label with readable tracking, switch to sentence case, abbreviate intentionally, or redesign the component.

---

## Final practical rule

I select typography in this order:

```text
Existing system or brand font
    → product register and user task
        → readability at target density
            → hierarchy roles
                → pairing contrast
                    → detailed scale, spacing, and case rules
```

A font is never chosen solely because it looks sophisticated in a hero screenshot. It must support the content, the interaction density, the stance, and the smallest screen where the product has to work.


## P5 — Color engineering

## 1. Font sources and the actual type library I select from

I do **not** assume there is one universal bundled font library. The selection order is:

1. **Existing project or design-system fonts** — if a kit, brand system, or imported Figma file specifies fonts, those are the source of truth.
2. **Project-provided local fonts** — if the repository includes licensed font files, use those.
3. **Google Fonts** — the normal fallback for self-contained web UI work in this environment.
4. **System fallbacks** — always defined after the preferred family.

For a new project without an existing font system, I draw from a deliberately curated set rather than picking random Google Fonts.

### Display serif / editorial serif

|Typeface|What I use it for|Register|
|---|---|---|
|**Newsreader**|Editorial products, culture, research, hospitality, quiet premium brands|Literary, warm, contemporary editorial|
|**Fraunces**|Craft commerce, food, beauty, expressive premium consumer work|Tactile, playful, materially rich|
|**Source Serif 4**|Institutional, educational, civic, publishing-adjacent products|Scholarly, trustworthy, durable|
|**DM Serif Display**|Bold campaign moments, selective large headlines|Assertive, compact, poster-like|
|**Literata**|Reading-heavy experiences and long-form publishing|Bookish, measured, serious|
|**Libre Baskerville**|Formal, classical, restrained identity moments|Traditional, dignified|
|**Cormorant Garamond**|Only when a genuinely high-fashion or historical brief calls for it|Romantic, dramatic; otherwise avoided|
|**Bodoni Moda**|Fashion/editorial campaigns with sufficient scale and contrast|Sharp, high-contrast, image-led|

### Humanist and readable UI sans

|Typeface|What I use it for|Register|
|---|---|---|
|**Source Sans 3**|Institutional systems, forms, content-heavy UI, civic products|Clear, calm, durable|
|**Public Sans**|Governmental, public-interest, operational, trustworthy products|Neutral, civic, highly functional|
|**Atkinson Hyperlegible Next**|Accessibility-conscious products, reading-heavy utility interfaces|Open, highly legible, human|
|**Nunito Sans**|Friendly but structured consumer products|Warm, approachable|
|**Manrope**|Contemporary product interfaces with geometric restraint|Clean, confident, modern|
|**Albert Sans**|Retail, craft, editorial-commerce hybrids|Neutral but polished|
|**DM Sans**|Consumer products and approachable utility UI|Friendly, balanced, compact|
|**Work Sans**|Editorial/product hybrids and small-screen UI|Practical, slightly humanist|

### Grotesk / neo-grotesk / rational sans

|Typeface|What I use it for|Register|
|---|---|---|
|**Archivo**|Operational tools, data products, technical and industrial systems|Condensed energy, functional precision|
|**Archivo Narrow**|Metrics, data headers, compact utility labeling|Industrial, compact|
|**IBM Plex Sans**|Only for products where its technical/enterprise character is genuinely correct|Technical, established, engineered|
|**Barlow**|Transport, engineering, industrial interfaces|Mechanical, practical|
|**Barlow Condensed**|Timelines, dense dashboards, utility display labels|Technical, high-density|
|**Roboto Flex**|Systems that benefit from variable-width and variable-weight control|Functional, adaptable|
|**Commissioner**|Modern enterprise with more character than a default sans|Formal, composed|
|**Instrument Sans**|Contemporary culture, design, fashion, product work|Crisp, current, not overly neutral|

### Geometric sans

|Typeface|What I use it for|Register|
|---|---|---|
|**Outfit**|Youth-oriented consumer products and direct mobile UI|Crisp, optimistic|
|**Plus Jakarta Sans**|Contemporary consumer/product systems|Clean, rounded without becoming childish|
|**Sora**|Modern digital products, selective tech positioning|Geometric, distinct|
|**Figtree**|Friendly applications and general consumer UI|Open, easy, compact|
|**Lexend**|Readability-oriented, consumer education, accessible interfaces|Spacious, clear|
|**Urbanist**|Lifestyle, consumer, retail, mobile-first products|Smooth, contemporary|
|**Cabin**|Warm, functional, less-polished digital products|Human, practical|

### Expressive display sans

|Typeface|What I use it for|Register|
|---|---|---|
|**Bricolage Grotesque**|Playful consumer, creative tools, energetic campaigns|Expressive, contemporary|
|**Unbounded**|Selective futuristic, music, gaming, experimental work|Technical, graphic, bold|
|**Climate Crisis**|Large-scale climate/civic campaign moments only|Compressed, activist, emphatic|
|**Familjen Grotesk**|Cultural, editorial, and branded product pages|Slightly idiosyncratic, composed|
|**Red Hat Display**|Friendly premium-tech or creative products|Warm, broad, modern|
|**Anybody**|Youth, movement, playful modular visual identities|Variable, elastic, expressive|

### Slab serif / utility serif

|Typeface|What I use it for|Register|
|---|---|---|
|**Roboto Slab**|Education, documentation, trustworthy systems|Practical, stable|
|**Bitter**|Publishing, reading, editorial information density|Bookish, robust on screen|
|**Zilla Slab**|News, media, civic, structured editorial systems|Direct, readable|
|**Arvo**|Selective utility, vintage-tech, or printed-material references|Strong, compact|
|**Space Mono**|Only when an explicitly retro/technical stance requires it|Technical, conspicuous; not a default|

### Mono

|Typeface|What I use it for|Register|
|---|---|---|
|**Geist Mono**|Modern data labels, IDs, timestamps, developer-adjacent tools|Clean, restrained|
|**DM Mono**|Editorial metadata, archive references, measured technical labels|Soft, intellectual|
|**Azeret Mono**|Craft-commerce metadata, experimental editorial work|Distinctive, characterful|
|**IBM Plex Mono**|Existing enterprise systems or IBM/Plex-aligned work|Technical, structured|
|**Roboto Mono**|Institutional data and accessibility-oriented utility UI|Neutral, familiar|
|**Fira Mono**|Playful consumer data, small code-like labels|Friendly, technical|
|**JetBrains Mono**|Code-heavy and developer products|Highly legible, developer-native|
|**Fragment Mono**|Graphic/experimental metadata treatment|Distinctive, editorial|

### Practical selection rule

I normally use:

- **One family** for a dense operational product, sometimes plus mono.
- **Two families** for most landing pages: display + UI sans.
- **Three families** only when there is a real metadata/data role: display + UI sans + mono.

I do not add a third family just because “three fonts feels more designed.”

---

## 2. Ten pairings I consider strong

### 1. Newsreader + Public Sans + DM Mono

|Field|Value|
|---|---|
|**Stance**|Quiet editorial, cultural institution, research platform, considered hospitality|
|**Families**|Newsreader / Public Sans / DM Mono|
|**Why it works**|Newsreader gives literary warmth without looking like a generic fashion-serif choice. Public Sans keeps controls and body copy extremely clear. DM Mono gives metadata, dates, archive IDs, or issue numbers a deliberate structural role.|
|**Use**|Large headlines in Newsreader; all UI in Public Sans; only metadata/data in DM Mono.|

### 2. Fraunces + Albert Sans + Azeret Mono

|Field|Value|
|---|---|
|**Stance**|Contemporary craft commerce, food, fragrance, hospitality, small-batch retail|
|**Families**|Fraunces / Albert Sans / Azeret Mono|
|**Why it works**|Fraunces brings material richness and controlled personality. Albert Sans keeps commerce UI elegant and readable. Azeret Mono gives SKU, quantity, origin, batch, or product-spec metadata an unusual but restrained voice.|
|**Use**|Fraunces for hero/product storytelling; Albert Sans for shopping UI; Azeret Mono for product facts only.|

### 3. Archivo + Manrope + Geist Mono

|Field|Value|
|---|---|
|**Stance**|Precision industrial, logistics, analytics, operational dashboard|
|**Families**|Archivo / Manrope / Geist Mono|
|**Why it works**|Archivo has compact, durable display energy; Manrope keeps dense controls comfortable; Geist Mono makes values, dates, IDs, and measurements scan cleanly.|
|**Use**|Archivo for section headers and key metrics; Manrope for UI and body; Geist Mono for data.|

### 4. Source Serif 4 + Source Sans 3 + Roboto Mono

|Field|Value|
|---|---|
|**Stance**|Institutional calm, education, healthcare, civic service, legal or public-interest products|
|**Families**|Source Serif 4 / Source Sans 3 / Roboto Mono|
|**Why it works**|The families have compatible proportions and an established, trustworthy tone. The serif supports longer reading and formal headings; the sans delivers durable interface clarity.|
|**Use**|Serif for key headings and reading moments; sans for nearly all interface elements; mono only for reference numbers, dates, and structured data.|

### 5. Bricolage Grotesque + DM Sans

|Field|Value|
|---|---|
|**Stance**|Playful consumer, habit tracking, youth products, social or wellness tools|
|**Families**|Bricolage Grotesque / DM Sans|
|**Why it works**|Bricolage creates a lively, recognisable display voice without needing stickers, blobs, or excessive color. DM Sans is friendly and functional at small mobile sizes.|
|**Use**|Bricolage for key prompts, completion moments, statistics, and onboarding; DM Sans for navigation, forms, and all sustained reading.|

### 6. Instrument Sans + Newsreader

|Field|Value|
|---|---|
|**Stance**|Contemporary gallery, fashion, design studio, portfolio, culture-led product|
|**Families**|Instrument Sans / Newsreader|
|**Why it works**|Instrument Sans is crisp and current; Newsreader adds a quieter literary counterpoint. The contrast feels more deliberate than a standard “serif headline + Inter body” combination.|
|**Use**|Instrument Sans for UI and compact headers; Newsreader for large editorial statements, case-study titles, or selected pull quotes.|

### 7. Barlow + Barlow Condensed + IBM Plex Mono

|Field|Value|
|---|---|
|**Stance**|Transit, industrial operations, sports data, transport, manufacturing|
|**Families**|Barlow / Barlow Condensed / IBM Plex Mono|
|**Why it works**|This is a tightly related utility system. Barlow provides an accessible working UI, Barlow Condensed increases density in metrics and timetable-like areas, and Plex Mono makes technical identifiers distinct.|
|**Use**|Barlow for standard UI; Barlow Condensed for big metric values and compact headers; mono for serials, schedule data, and IDs.|

### 8. Literata + Work Sans + DM Mono

|Field|Value|
|---|---|
|**Stance**|Journal, long-form reading product, archival catalogue, knowledge platform|
|**Families**|Literata / Work Sans / DM Mono|
|**Why it works**|Literata is optimized for reading and works well for intellectual content. Work Sans remains stable at small UI sizes. DM Mono turns references and metadata into a calm system rather than visual clutter.|
|**Use**|Literata for articles and primary titles; Work Sans for interface/navigation; mono for citations, issue references, and timestamps.|

### 9. Outfit + Figtree

|Field|Value|
|---|---|
|**Stance**|Friendly digital consumer, mobile-first utility, lifestyle product, simple onboarding|
|**Families**|Outfit / Figtree|
|**Why it works**|Both are open and contemporary, but Outfit is more display-forward while Figtree handles interface text naturally. It is clean and optimistic without feeling like a default productivity app.|
|**Use**|Outfit for hero prompts and numeric summaries; Figtree for all standard UI and body copy.|

### 10. DM Serif Display + Commissioner + Geist Mono

|Field|Value|
|---|---|
|**Stance**|Premium financial planning, private client portal, boutique consultancy, refined B2B|
|**Families**|DM Serif Display / Commissioner / Geist Mono|
|**Why it works**|DM Serif Display provides selective gravitas; Commissioner is formal without being sterile; Geist Mono gives financial values and dates a precise utility layer.|
|**Use**|Use the serif sparingly and at large sizes. Commissioner must carry the actual application. Mono is for amounts, dates, document IDs, and structured values.|

---

## 3. Faces and pairings I treat as overused AI defaults

These are not banned. They become a problem when used without a reason.

### Overused default faces

|Typeface|Why I avoid using it automatically|
|---|---|
|**Inter**|Excellent UI font, but it is now the default visual texture of a huge amount of product UI. Use it when an existing system uses it or when maximum neutrality is truly right—not because nothing else was considered.|
|**Space Grotesk**|Frequently used to signal “modern AI/startup.” It has become highly recognizable as a generated-design shortcut.|
|**Space Mono**|Often added as decorative “technical flavor” even when there is no real data, code, or metadata role.|
|**IBM Plex Mono**|Strong font, but easy to overuse as a generic “serious technology” signal.|
|**Syne**|Commonly used as a fast route to “creative agency” or “experimental brand” styling.|
|**Cormorant Garamond**|Repeatedly used to imply luxury, fashion, or editorial refinement, often without a typographic rationale.|
|**Bebas Neue**|A common shortcut for impact and loudness; it can flatten hierarchy and become poster-template-like.|
|**Playfair Display**|Often used for “premium feminine” styling without enough specificity. It is valid when the editorial/fashion register is actually appropriate.|
|**Poppins**|Can create a generic friendly-app look when used indiscriminately.|
|**Montserrat**|Widely used, often associated with generic marketing-site typography.|
|**Raleway**|Still usable in selective display roles, but often reads as template-era startup or agency typography.|
|**Lato**|Readable, but can make a design feel like an undifferentiated early SaaS product.|
|**Roboto**|Extremely functional, but visually neutral to the point of sameness when no Google/Android/system context motivates it.|

### Overused pairings

|Pairing|Why I avoid it by default|
|---|---|
|**Inter + Space Grotesk**|The common “AI SaaS” pairing.|
|**Playfair Display + Inter**|A frequent “editorial luxury landing page” shortcut.|
|**Cormorant Garamond + Inter**|Often produces generic warm-premium styling.|
|**Poppins + Poppins**|Gives an overly uniform, generic app-template rhythm.|
|**Space Grotesk + Space Mono**|A common startup/developer-product visual shorthand.|
|**DM Sans + DM Mono**|Strong pairing, but easy to make generic unless the product and composition give it personality.|
|**Bebas Neue + Montserrat**|Common poster/fitness/campaign formula.|
|**Syne + Manrope**|Often used as a ready-made “creative tech” identity without deeper structural choices.|

### The actual rule

I do not reject a face because it is popular. I reject it when it is being used as a substitute for art direction.

---

## 4. Actual type scale: dense operational tool

This is the kind of scale I would ship for a desktop-first operational tool with tables, alerts, activity logs, filters, key metrics, and compact navigation.

### Families

```css
--font-display: "Archivo", "Helvetica Neue", Arial, sans-serif;
--font-ui: "Manrope", "Helvetica Neue", Arial, sans-serif;
--font-mono: "Geist Mono", "SFMono-Regular", Consolas, monospace;
```

### Desktop scale

|Role|Family|Size|Weight|Line-height|Tracking|Case|
|---|---|---|---|---|---|---|
|Display metric|Archivo|48px / 3rem|650|1.00|-0.030em|Sentence case / numeral|
|Page title|Archivo|32px / 2rem|650|1.12|-0.022em|Sentence case|
|Section heading|Archivo|22px / 1.375rem|630|1.20|-0.012em|Sentence case|
|Card heading|Manrope|16px / 1rem|700|1.30|-0.006em|Sentence case|
|Body|Manrope|14px / 0.875rem|450|1.50|0em|Sentence case|
|Body compact|Manrope|13px / 0.8125rem|450|1.46|0em|Sentence case|
|Table value|Manrope|13px / 0.8125rem|520|1.35|0em|Sentence case|
|Table metadata|Geist Mono|12px / 0.75rem|500|1.35|-0.010em|Sentence case|
|Caption|Manrope|12px / 0.75rem|520|1.40|0.005em|Sentence case|
|Utility label|Manrope|11px / 0.6875rem|700|1.25|0.075em|Uppercase|
|Tiny status|Geist Mono|10px / 0.625rem|550|1.20|0.030em|Uppercase only if very short|

### Mobile adjustments

|Role|Mobile size|
|---|---|
|Display metric|36px / 2.25rem|
|Page title|28px / 1.75rem|
|Section heading|20px / 1.25rem|
|Card heading|16px / 1rem|
|Body|14px / 0.875rem|
|Body compact|13px / 0.8125rem|
|Caption|12px / 0.75rem|

### Operational-tool rules

- Use the display style for a key number, primary dashboard statement, or major page title—not every card.
- Use UI sans for all ordinary controls, table text, buttons, filters, navigation, and descriptions.
- Use mono only for values where fixed-width or technical structure improves scanning: dates, timestamps, IDs, duration, percentages, equipment codes, or live readings.
- Keep body text at `14px` minimum for dense desktop UI unless there is a strong reason to use `13px`.
- Avoid all-caps headings. Use uppercase only for short structural labels.
- Use tabular numerals when supported for financial values, measures, and data tables.

```css
.tabular-data {
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums slashed-zero;
}
```

---

## 5. Actual type scale: editorial landing page

This is the kind of scale I would ship for a desktop-first landing page with a strong hero, selective image use, narrative sections, and spacious pacing.

### Families

```css
--font-display: "Newsreader", Georgia, serif;
--font-ui: "Public Sans", "Helvetica Neue", Arial, sans-serif;
--font-mono: "DM Mono", "SFMono-Regular", Consolas, monospace;
```

### Desktop scale

|Role|Family|Size|Weight|Line-height|Tracking|Case|
|---|---|---|---|---|---|---|
|Hero display|Newsreader|72px / 4.5rem|500|0.96|-0.038em|Sentence case|
|Display / major statement|Newsreader|56px / 3.5rem|500|1.00|-0.032em|Sentence case|
|H1|Newsreader|44px / 2.75rem|520|1.05|-0.024em|Sentence case|
|H2|Newsreader|32px / 2rem|540|1.13|-0.018em|Sentence case|
|H3|Public Sans|21px / 1.3125rem|650|1.28|-0.008em|Sentence case|
|Lead|Public Sans|20px / 1.25rem|420|1.48|-0.006em|Sentence case|
|Body|Public Sans|16px / 1rem|400|1.62|-0.002em|Sentence case|
|Body small|Public Sans|14px / 0.875rem|420|1.55|0em|Sentence case|
|Caption|Public Sans|12px / 0.75rem|550|1.45|0.008em|Sentence case|
|Eyebrow / section label|Public Sans|11px / 0.6875rem|700|1.25|0.120em|Uppercase|
|Image metadata|DM Mono|11px / 0.6875rem|500|1.40|0.010em|Sentence case|
|Button label|Public Sans|13px / 0.8125rem|650|1.00|0em|Sentence case|

### Mobile adjustments

|Role|Mobile size|
|---|---|
|Hero display|48px / 3rem|
|Display / major statement|40px / 2.5rem|
|H1|34px / 2.125rem|
|H2|28px / 1.75rem|
|H3|20px / 1.25rem|
|Lead|18px / 1.125rem|
|Body|16px / 1rem|

### Editorial-landing-page rules

- Use the largest display size for one primary moment, usually the hero.
- Do not make every section heading look like a hero headline.
- Keep display line-height compact but not mechanically tight: typically `0.96–1.08`.
- Keep body line-height generous: typically `1.55–1.65`.
- Use the mono face only for image captions, article-like metadata, dates, labels, or numbered sections.
- Avoid justified text on the web.
- Keep longer body copy to a readable measure, generally around `60–72ch`.

```css
.editorial-copy {
  max-width: 68ch;
  font-family: var(--font-ui);
  font-size: 16px;
  font-weight: 400;
  line-height: 1.62;
  letter-spacing: -0.002em;
}
```

---

## 6. Case behavior: exactly when I use uppercase labels

I use uppercase sparingly. Uppercase is a **structural signal**, not an everyday text style.

## Use uppercase when all of the following are true

1. The text is short.
2. It functions as metadata, taxonomy, a section kicker, or a compact utility label.
3. It is not a sentence, paragraph, or long navigation item.
4. Its role benefits from visual separation rather than conversational readability.
5. The selected font remains legible in uppercase at that size.

### Good uppercase uses

- `PROJECT STATUS`
- `Q3 PERFORMANCE`
- `SHOT 04 · DAY 12`
- `UPDATED 14 MIN AGO`
- `SAVED VIEWS`
- `MEMBER BENEFITS`
- `FEATURED WORK`
- `OPEN ISSUES`
- `SELECTED RANGE`
- `LIVE`

### Avoid uppercase for

- Primary navigation with long labels
- Main page titles
- Body copy
- Multi-word buttons such as `CREATE A NEW PROJECT`
- Form field labels with long descriptions
- Error messages
- Helper text
- Dense mobile navigation
- Large blocks of data labels
- Anything that needs quick, relaxed reading

## Exact uppercase values

### Standard UI uppercase label

```css
.label-uppercase {
  font-family: "Manrope", "Helvetica Neue", Arial, sans-serif;
  font-size: 11px;
  font-weight: 700;
  line-height: 1.25;
  letter-spacing: 0.075em;
  text-transform: uppercase;
}
```

Use for dense operational tools, compact cards, filter-group labels, small dashboard section labels, and status headings.

### Editorial eyebrow

```css
.editorial-eyebrow {
  font-family: "Public Sans", "Helvetica Neue", Arial, sans-serif;
  font-size: 11px;
  font-weight: 700;
  line-height: 1.25;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
```

Use for article categories, story context, section kickers, campaign labels, and image-series identification.

### Tiny mono utility status

```css
.mono-status {
  font-family: "Geist Mono", "SFMono-Regular", Consolas, monospace;
  font-size: 10px;
  font-weight: 550;
  line-height: 1.2;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}
```

Use only for short values such as `LIVE`, `SYNCED`, `PAUSED`, `DRAFT`, `LOCKED`, or `OFFLINE`.

### Mobile adjustment

Do not shrink ordinary uppercase labels below `10px`. If there is not enough space for an `11px` uppercase label with readable tracking, switch to sentence case, abbreviate intentionally, or redesign the component.

---

## Final practical rule

I select typography in this order:

```text
Existing system or brand font
    → product register and user task
        → readability at target density
            → hierarchy roles
                → pairing contrast
                    → detailed scale, spacing, and case rules
```

A font is never chosen solely because it looks sophisticated in a hero screenshot. It must support the content, the interaction density, the stance, and the smallest screen where the product has to work.

> Walk me through how you construct an actual palette, not the semantic-token philosophy. (1) What color space do you think in (OKLCH, HSL)? (2) How do you derive the neutrals — temperature, number of steps, actual values for a warm-paper vs cool-technical ground? (3) How do you pick the accent hue and validate it (contrast math, saturation limits per stance)? (4) Dark mode: exact derivation rules from a light theme — what changes beyond inverting (surface lightness ramps, desaturation, border opacity, shadow strategy)? (5) Chart/data-viz series: how do you generate 6–8 series colors that stay on-theme, with real values? (6) Show all of this end-to-end for one concrete product.

I think in **OKLCH first**, then validate in the actual rendering environment. I use hex only when a codebase, library, browser fallback, or asset pipeline needs it.

OKLCH is more useful for palette construction because its three axes map more closely to how designers reason about color:

```text
oklch(L C H)

L = perceived lightness, from 0 to 1
C = chroma / colorfulness
H = hue angle, from 0 to 360 degrees
```

That lets me say things like:

- “Make this surface lighter without changing its temperature.”
- “Keep the hue but reduce saturation for dark mode.”
- “Make the accent more forceful without making it visually lighter.”
- “Keep chart series at comparable perceived weight.”

HSL is convenient for quick experiments, but equal numeric changes in HSL do not create reliably equal visual changes. A palette with six HSL colors at the same saturation/lightness can still have one series that looks dramatically louder than the rest.

---

# 1. The palette-construction sequence

I build palettes in this order:

```text
1. Choose the ground temperature
2. Build a neutral ramp
3. Choose the anchor/ink color
4. Choose an accent hue by product meaning
5. Build semantic states
6. Verify contrast in actual roles
7. Build dark mode as a new surface system
8. Build chart colors separately from UI semantic colors
9. Test the palette on real components and real data
```

I do **not** start with a random purple/blue brand color and derive everything else from it.

---

# 2. Ground temperature and neutral ramps

The first palette decision is usually the relationship between the page ground and the “ink” color.

## Warm-paper ground

I use warm-paper neutrals when the product should feel:

- editorial,
- crafted,
- filmic,
- archival,
- cultural,
- hospitality-oriented,
- human,
- tactile,
- narrative-led.

The warm hue is usually a low-chroma yellow-orange range, around `H 65–95`.

The chroma should remain very low. The goal is not beige UI; it is a neutral with a perceptible material temperature.

### Warm-paper neutral ramp

```css
:root {
  /* Warm-paper neutral ramp: H ≈ 78, low chroma */
  --paper-0: oklch(0.985 0.006 78); /* near-white highlight */
  --paper-1: oklch(0.965 0.009 78); /* elevated surface */
  --paper-2: oklch(0.942 0.012 78); /* main page ground */
  --paper-3: oklch(0.912 0.015 78); /* muted panel / hover */
  --paper-4: oklch(0.864 0.018 78); /* stronger secondary surface */
  --paper-5: oklch(0.784 0.020 78); /* subtle divider / disabled fill */
  --paper-6: oklch(0.677 0.022 78); /* muted text region */
  --paper-7: oklch(0.540 0.020 78); /* secondary text */
  --paper-8: oklch(0.365 0.018 78); /* soft ink */
  --paper-9: oklch(0.235 0.016 78); /* primary ink */
}
```

### What that means in implementation

```css
--background: var(--paper-2);
--card: var(--paper-1);
--secondary: var(--paper-3);
--muted: var(--paper-3);
--border: color-mix(in oklch, var(--paper-9) 16%, transparent);
--foreground: var(--paper-9);
--muted-foreground: var(--paper-7);
```

The lightness steps are intentionally not uniform. The top end of a palette needs smaller jumps because people are more sensitive to small surface shifts in very light UI.

---

## Cool-technical ground

I use cool-technical neutrals when the product should feel:

- operational,
- infrastructural,
- analytical,
- precise,
- scientific,
- data-dense,
- contemporary industrial,
- high-trust.

The hue generally sits in a very low-chroma blue/cyan range, around `H 220–250`.

### Cool-technical neutral ramp

```css
:root {
  /* Cool-technical neutral ramp: H ≈ 235, low chroma */
  --slate-0: oklch(0.985 0.004 235); /* near-white highlight */
  --slate-1: oklch(0.964 0.007 235); /* elevated panel */
  --slate-2: oklch(0.944 0.010 235); /* workspace ground */
  --slate-3: oklch(0.912 0.013 235); /* muted surface */
  --slate-4: oklch(0.855 0.016 235); /* subdued fill */
  --slate-5: oklch(0.760 0.018 235); /* disabled / subtle control */
  --slate-6: oklch(0.650 0.019 235); /* muted content */
  --slate-7: oklch(0.515 0.020 235); /* secondary text */
  --slate-8: oklch(0.340 0.021 235); /* ink-adjacent */
  --slate-9: oklch(0.215 0.022 235); /* primary ink */
}
```

### Why I do not make “cool technical” blue-gray

A technical palette does not need blue backgrounds everywhere. It needs controlled temperature, stable contrast, and enough low-chroma structure that charts, alerts, and selected states can do their jobs.

A very chromatic blue-gray canvas becomes visually loud and competes with data. The background should support information—not become the strongest color on screen.

---

# 3. Picking an accent hue

I choose the accent hue from the product’s meaning, not from a generic “brand color” reflex.

## Product-to-accent heuristics

|Product meaning / stance|Accent families I consider|Why|
|---|---|---|
|Infrastructure, energy, industrial|deep teal, oxide orange, controlled amber|Signals monitoring, physical systems, energy, caution|
|Editorial, craft, food, film|vermilion, clay, moss, ink blue|Feels material and culturally grounded|
|Institutional, healthcare, civic|restrained teal, navy, dark blue-green|Trustworthy, stable, accessible|
|Youthful consumer, wellness|violet, coral, citrus, mint|Expressive and emotionally legible|
|Finance, legal, private-client|deep navy, forest, burgundy in moderation|Serious, durable, low-noise|
|Nature, ecology, climate|moss, lichen, water blue, soil/clay|Semantically connected without obvious “greenwashing”|
|Music, media, creative tools|electric-but-controlled violet, indigo, vermilion|Supports energy and signal without making all surfaces neon|

## Accent-chroma limits by stance

These are starting limits for UI—not rules for illustrations or campaign art.

|Stance|Accent chroma range|Typical accent lightness|
|---|---|---|
|Precision industrial|`C 0.10–0.15`|`L 0.50–0.66`|
|Institutional calm|`C 0.08–0.13`|`L 0.45–0.60`|
|Quiet editorial|`C 0.10–0.16`|`L 0.45–0.62`|
|Contemporary craft commerce|`C 0.10–0.17`|`L 0.48–0.65`|
|Playful consumer|`C 0.14–0.22`|`L 0.55–0.72`|
|Dark immersive/media|`C 0.15–0.25`|`L 0.62–0.78`|

The accent can be more chromatic in a playful consumer product because the product’s emotional register supports it. In an operational dashboard, the same chroma can make the interface feel alarmed or toy-like.

---

# 4. Accent validation: the actual checks

I validate a color in its **real semantic role**, not simply by checking whether the raw swatch looks attractive.

## A. Text contrast

For normal text, I target at least:

```text
WCAG AA normal text: 4.5:1
WCAG AA large text: 3:1
```

For UI controls, I target:

```text
UI boundary / meaningful visual state: at least 3:1
```

I check:

- foreground text on background,
- card text on card,
- primary button text on primary fill,
- secondary-action text on secondary fill,
- muted text on background,
- disabled text only where it remains meaningfully readable,
- focus ring against background and the component it surrounds,
- alert/status text and icon against alert background.

## B. Role contrast

I also check whether the accent has enough distinction from nearby system colors.

A primary accent may pass contrast against white but still fail as an active state if it is too close to:

- an information blue,
- a chart series,
- a success green,
- a selected table row fill,
- a dark navigation state.

## C. Color-blind resilience

For functional status or data:

- Do not encode meaning with hue alone.
- Pair color with a label, icon, pattern, marker, line style, value, or position.
- Avoid red/green-only comparisons.
- Ensure adjacent chart colors differ in lightness and/or chroma as well as hue.

## D. Saturation check in context

I view the accent at actual component size:

- 12px label,
- 14px button text,
- selected tab,
- 40px primary button,
- full-width alert,
- chart line,
- focused input.

A color that looks refined as a 200px swatch can become abrasive when repeated in fifty controls.

---

# 5. Dark mode: derive, do not invert

Dark mode is not:

```css
background: black;
foreground: white;
```

and it is not simply the light palette inverted.

A good dark system is a new surface hierarchy with related temperature and reduced visual glare.

## Exact derivation rules

### Rule 1: retain the hue family, reduce chroma in large surfaces

Light backgrounds can carry slight warmth or coolness because they are high-lightness, low-demand surfaces.

Dark backgrounds should usually be **less chromatic** than their light equivalents. A strongly chromatic dark background can feel neon, muddy, or tiring.

```text
Light workspace: L 0.94, C 0.01
Dark workspace:  L 0.19–0.23, C 0.01–0.02
```

### Rule 2: do not use pure black by default

Pure black makes bright text and colored accents feel harsh. I generally begin dark workspaces around:

```text
L 0.16–0.22
```

rather than `#000000`.

### Rule 3: surfaces step upward in lightness, not downward

In light mode:

```text
background → card is lighter
```

In dark mode:

```text
background → card is lighter too
```

The direction remains the same. Cards and overlays rise toward the foreground, but with restrained contrast.

### Rule 4: use borders more than shadows

In light mode, subtle shadows can help separate white panels from a light background.

In dark mode, shadows often disappear into the background or create muddy halos. I use:

- slightly lighter surface steps,
- low-opacity light borders,
- subtle inset highlights,
- very restrained black shadows only for dialogs and popovers.

### Rule 5: reduce text brightness below pure white

Main text is usually around `L 0.92–0.96`, not pure white. Pure white is reserved for exceptional emphasis or small high-contrast details.

### Rule 6: re-tune accents independently

A light-mode primary accent is not automatically suitable for dark mode.

Dark mode often requires:

- higher lightness,
- slightly reduced chroma if it vibrates,
- separate foreground text color,
- more muted secondary/accent fills,
- distinct border/focus values.

### Rule 7: re-check charts separately

Series that are distinct on a light canvas may collapse or bloom on a dark canvas. Dark-mode chart colors usually need higher lightness and more controlled chroma.

---

# 6. Chart and data-viz series: how I create 6–8 colors

I do not use the same colors for:

- primary button,
- destructive action,
- success status,
- and chart series.

Chart colors are a separate palette with different requirements.

## A. First decide the chart purpose

### Sequential data

Use one hue with a lightness/chroma ramp.

Examples:

- heatmaps,
- risk intensity,
- volume,
- probability,
- time accumulation.

### Diverging data

Use two semantic poles with a neutral midpoint.

Examples:

- below/above target,
- loss/profit,
- temperature deviation,
- negative/positive variance.

### Categorical data

Use 6–8 distinguishable hues with controlled equal visual weight.

Examples:

- projects,
- departments,
- crew groups,
- channels,
- locations,
- product categories.

## B. Rules for categorical series

1. Keep most series within a comparable lightness band.
2. Vary hue first, then use lightness/chroma to resolve conflicts.
3. Do not make every series equally saturated if one is intended as the focus.
4. Reserve the brand primary for the selected/focused series where possible.
5. Use direct labels, markers, patterns, tooltips, or line styles so color is not the only cue.
6. Do not use eight random rainbow colors.
7. Test the series on the intended chart background, with actual line widths and point sizes.

---

# 7. End-to-end example: a film-production studio dashboard

## Product brief

> A desktop-first project dashboard for a small film-production studio tracking shoots, budgets, crew, and delivery deadlines. Calm, editorial, operational; not generic enterprise SaaS.

The product needs to balance:

- high-density operational data,
- a creative and cinematic subject matter,
- a calm studio identity,
- clear exceptions,
- readable budgets and dates,
- staff-facing daily use.

I would choose a stance of:

```text
Quiet editorial operations
```

That means:

- warm paper ground,
- deep ink-like text,
- cinematic green-black primary,
- clay/orange accent for urgency and selected emphasis,
- hairline warm-gray structure,
- low-noise surfaces,
- no bright blue SaaS defaults,
- no shadows on ordinary panels,
- charts with measured, film-production-relevant color families.

---

## 7.1 Construct the neutral ramp

The studio needs warmth, but it is still a working dashboard. So the background remains restrained.

```css
:root {
  /* Foundation: warm paper, H ≈ 78 */
  --film-paper-0: oklch(0.985 0.006 78);
  --film-paper-1: oklch(0.968 0.008 78);
  --film-paper-2: oklch(0.946 0.011 78);
  --film-paper-3: oklch(0.918 0.014 78);
  --film-paper-4: oklch(0.862 0.017 78);
  --film-paper-5: oklch(0.762 0.019 78);
  --film-paper-6: oklch(0.642 0.020 78);
  --film-paper-7: oklch(0.510 0.019 78);
  --film-paper-8: oklch(0.330 0.018 78);
  --film-paper-9: oklch(0.220 0.016 78);
}
```

### Visual roles

```text
paper-2 → page workspace
paper-1 → cards and elevated panels
paper-3 → muted fills, selected-table-row background, hover surface
paper-4 → disabled field or more visible secondary surface
paper-7 → muted labels and secondary information
paper-9 → primary text/ink
```

---

## 7.2 Choose the primary and accent hues

### Primary: studio green-black

The main primary should feel like dark equipment, grading bays, studio walls, and production craft—not like consumer green.

```css
--film-primary: oklch(0.305 0.046 164);
--film-primary-hover: oklch(0.270 0.046 164);
--film-primary-active: oklch(0.235 0.042 164);
--film-primary-foreground: oklch(0.975 0.006 78);
```

This is a low-chroma, very dark green-teal. It works for:

- primary buttons,
- active navigation,
- selected tabs,
- key budget bars,
- focused project context.

### Accent: oxide/clay orange

The studio needs a visible signal for deadlines, selected work, and production exceptions without becoming alarm-red.

```css
--film-accent: oklch(0.610 0.145 42);
--film-accent-hover: oklch(0.565 0.145 42);
--film-accent-soft: oklch(0.925 0.035 42);
--film-accent-foreground: oklch(0.245 0.045 42);
```

This hue works because it suggests:

- marking tape,
- call sheets,
- production notes,
- warm practical lights,
- physical workflow,
- urgency without destructive danger.

It should not be used everywhere. Its strongest roles are:

- deadline at risk,
- selected item,
- primary emphasis in a warm context,
- highlighted shoot day,
- key action in a neutral view.

---

## 7.3 Define semantic status colors

```css
:root {
  /* Positive: on track / delivered */
  --film-success: oklch(0.510 0.105 154);
  --film-success-soft: oklch(0.925 0.028 154);
  --film-success-foreground: oklch(0.265 0.060 154);

  /* Warning: needs review / budget pressure */
  --film-warning: oklch(0.690 0.135 76);
  --film-warning-soft: oklch(0.940 0.040 76);
  --film-warning-foreground: oklch(0.350 0.070 76);

  /* Danger: overdue / blocked */
  --film-danger: oklch(0.545 0.155 28);
  --film-danger-soft: oklch(0.930 0.035 28);
  --film-danger-foreground: oklch(0.320 0.075 28);

  /* Informational: scheduled / in review */
  --film-info: oklch(0.535 0.090 240);
  --film-info-soft: oklch(0.925 0.025 240);
  --film-info-foreground: oklch(0.300 0.055 240);
}
```

These colors should appear with text and an icon or explicit label:

```text
● On track
▲ Needs review
! Overdue
○ Scheduled
```

Not color alone.

---

## 7.4 Light-mode token assignment

```css
:root {
  --background: oklch(0.946 0.011 78);
  --foreground: oklch(0.220 0.016 78);

  --card: oklch(0.968 0.008 78);
  --card-foreground: oklch(0.220 0.016 78);

  --primary: oklch(0.305 0.046 164);
  --primary-foreground: oklch(0.975 0.006 78);

  --secondary: oklch(0.918 0.014 78);
  --secondary-foreground: oklch(0.315 0.018 78);

  --muted: oklch(0.918 0.014 78);
  --muted-foreground: oklch(0.510 0.019 78);

  --accent: oklch(0.610 0.145 42);
  --accent-foreground: oklch(0.245 0.045 42);

  --border: oklch(0.762 0.019 78);
  --ring: oklch(0.610 0.145 42);

  --radius: 8px;
}
```

### Border rules

```css
--border-subtle: rgb(42 35 29 / 10%);
--border-default: rgb(42 35 29 / 16%);
--border-emphasized: rgb(42 35 29 / 28%);
```

I would use `1px` rules. Most cards remain flat:

```css
.project-panel {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  box-shadow: none;
}
```

Floating menus and dialogs may receive a restrained shadow:

```css
--shadow-floating:
  0 2px 4px rgb(42 35 29 / 6%),
  0 16px 38px rgb(42 35 29 / 13%);
```

---

## 7.5 Dark-mode derivation

The dark mode should resemble a quiet studio screening room or editing workspace—not a black terminal.

### Surface ramp

```css
.dark {
  /* Same warm-paper family, much lower lightness and lower chroma */
  --film-night-0: oklch(0.170 0.012 78); /* app ground */
  --film-night-1: oklch(0.205 0.013 78); /* standard panel */
  --film-night-2: oklch(0.245 0.015 78); /* raised panel */
  --film-night-3: oklch(0.290 0.016 78); /* hover/selected quiet fill */
  --film-night-4: oklch(0.390 0.018 78); /* divider / muted control */
  --film-night-5: oklch(0.620 0.015 78); /* muted text */
  --film-night-6: oklch(0.880 0.010 78); /* main text */
  --film-night-7: oklch(0.950 0.006 78); /* rare high emphasis */

  --background: var(--film-night-0);
  --foreground: var(--film-night-6);

  --card: var(--film-night-1);
  --card-foreground: var(--film-night-6);

  /* Primary must become lighter to work on a dark base */
  --primary: oklch(0.720 0.100 164);
  --primary-foreground: oklch(0.185 0.016 78);

  --secondary: var(--film-night-2);
  --secondary-foreground: var(--film-night-6);

  --muted: var(--film-night-2);
  --muted-foreground: var(--film-night-5);

  /* Accent is slightly lighter but less chromatic than the light-mode version */
  --accent: oklch(0.735 0.115 42);
  --accent-foreground: oklch(0.225 0.020 78);

  --border: rgb(244 237 226 / 15%);
  --ring: oklch(0.790 0.105 42);
}
```

### Dark-mode elevation rules

```css
.dark {
  --shadow-floating:
    0 1px 1px rgb(0 0 0 / 25%),
    0 18px 48px rgb(0 0 0 / 38%);
}

.dark .project-panel {
  background: var(--card);
  border: 1px solid rgb(244 237 226 / 12%);
  box-shadow: inset 0 1px 0 rgb(255 255 255 / 3%);
}
```

In dark mode, I do not use a visible drop shadow on every panel. The system is separated primarily by:

- lightness steps,
- low-opacity light borders,
- one subtle inset highlight,
- spacing,
- and localized dialog/popover shadows.

---

## 7.6 Build the chart series palette

The dashboard may show:

- per-project budget burn,
- crew allocation,
- shoot-day progress,
- post-production workload,
- delivery schedules,
- department spend.

These require categorical colors. I would use eight series that feel related to the film-studio palette but are still distinguishable.

### Light-mode chart series

```css
:root {
  --chart-1: oklch(0.480 0.105 164); /* studio green */
  --chart-2: oklch(0.610 0.145 42);  /* oxide orange */
  --chart-3: oklch(0.560 0.105 244); /* slate blue */
  --chart-4: oklch(0.650 0.125 84);  /* warm amber */
  --chart-5: oklch(0.545 0.115 318); /* muted magenta */
  --chart-6: oklch(0.590 0.105 198); /* blue-teal */
  --chart-7: oklch(0.475 0.085 132); /* olive green */
  --chart-8: oklch(0.570 0.105 15);  /* brick red */
}
```

### Dark-mode chart series

On dark surfaces, I lift series lightness and slightly control chroma:

```css
.dark {
  --chart-1: oklch(0.720 0.100 164);
  --chart-2: oklch(0.735 0.115 42);
  --chart-3: oklch(0.700 0.100 244);
  --chart-4: oklch(0.790 0.115 84);
  --chart-5: oklch(0.720 0.105 318);
  --chart-6: oklch(0.730 0.095 198);
  --chart-7: oklch(0.690 0.080 132);
  --chart-8: oklch(0.710 0.105 15);
}
```

### Series behavior rules

```text
Selected project        → chart-1 or the product primary
Secondary projects      → chart-2 through chart-8
Hovered line            → stroke width +1px and direct label
Deselected series       → 35–45% opacity, not removed completely
Budget target           → neutral dashed line
Over-budget region      → soft danger fill at 10–14% opacity
```

### Chart accessibility rules

- Pair every series color with a direct label or accessible tooltip.
- For line charts with more than four series, use dash patterns or markers for secondary lines.
- Do not rely on red versus green as the only distinction.
- Use `tabular-nums` for labels and values.
- Keep gridlines neutral and subtle.

```css
.chart-gridline {
  stroke: rgb(42 35 29 / 12%);
  stroke-width: 1;
}

.chart-target-line {
  stroke: oklch(0.510 0.019 78);
  stroke-width: 1.5;
  stroke-dasharray: 5 5;
}
```

---

# 8. The final validation pass

Before I ship a palette, I test it in real contexts:

```text
1. Page ground with body copy
2. Card surface with card title and metadata
3. Primary button in resting, hover, disabled, and focus states
4. Secondary button and selected tab
5. Input field, error field, warning field, and success state
6. Dense table with selected row and hover row
7. Chart with all 6–8 series visible
8. Image placed beside or behind the palette
9. Light mode and dark mode
10. Mobile display at actual text and control sizes
11. High-contrast/reduced-effects fallback
```

The palette is complete only when it works as an interface, not when its swatches look good in isolation.

## P6 — Component character in code

Each example below is a **separate component file**. They intentionally share the same content structure so the differences in typography, density, borders, radius, color, shadow, hover behavior, and focus treatment are easy to diff.

---

## 1. Precision industrial

```tsx
// PrecisionIndustrialExamples.tsx
const rows = [
  { project: "North Terminal", owner: "M. Ibarra", status: "At risk", date: "18 Jul", budget: "$42,680" },
  { project: "Signal Relay", owner: "A. Chen", status: "On track", date: "22 Jul", budget: "$18,420" },
  { project: "Foundry Survey", owner: "R. Patel", status: "Review", date: "29 Jul", budget: "$31,050" },
];

const statusClass = {
  "At risk": "bg-[#B63B3B] text-white",
  "On track": "bg-[#2C725E] text-white",
  Review: "bg-[#B75D16] text-white",
};

export default function PrecisionIndustrialExamples() {
  return (
    <main className="min-h-screen bg-[#F4F6F7] px-6 py-10 font-['Manrope'] text-[#162024] sm:px-10">
      <div className="mx-auto max-w-5xl space-y-10">
        <header className="border-b border-[#C7D0D2] pb-6">
          <p className="text-[11px] font-bold uppercase tracking-[0.09em] text-[#607076]">
            Component specimen / 01
          </p>
          <h1 className="mt-2 font-['Archivo'] text-[32px] font-semibold leading-[1.12] tracking-[-0.022em]">
            Precision industrial
          </h1>
        </header>

        {/* Buttons */}
        <section aria-labelledby="industrial-buttons">
          <h2
            id="industrial-buttons"
            className="mb-4 text-[11px] font-bold uppercase tracking-[0.08em] text-[#607076]"
          >
            Buttons
          </h2>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              className="inline-flex h-10 items-center justify-center rounded-[4px] border border-[#123B45] bg-[#123B45] px-4 text-[13px] font-bold tracking-[-0.005em] text-[#F7FAFA] transition-[background-color,border-color,box-shadow,transform] duration-150 ease-out hover:bg-[#0C3038] hover:border-[#0C3038] active:translate-y-px active:bg-[#08252B] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D46B2C] focus-visible:ring-offset-2 focus-visible:ring-offset-[#F4F6F7] disabled:cursor-not-allowed disabled:border-[#AEBBBC] disabled:bg-[#AEBBBC] disabled:text-[#E9EEEE]"
            >
              Create work order
            </button>

            <button
              type="button"
              className="inline-flex h-10 items-center justify-center rounded-[4px] border border-[#8FA0A4] bg-transparent px-4 text-[13px] font-bold tracking-[-0.005em] text-[#243237] transition-[background-color,border-color,color,box-shadow,transform] duration-150 ease-out hover:border-[#123B45] hover:bg-[#E3E9EA] active:translate-y-px active:bg-[#D5DFE0] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D46B2C] focus-visible:ring-offset-2 focus-visible:ring-offset-[#F4F6F7] disabled:cursor-not-allowed disabled:border-[#C7D0D2] disabled:text-[#93A0A3]"
            >
              Export report
            </button>

            <button
              type="button"
              disabled
              className="inline-flex h-10 items-center justify-center rounded-[4px] border border-[#123B45] bg-[#123B45] px-4 text-[13px] font-bold tracking-[-0.005em] text-[#F7FAFA] transition-[background-color,border-color,box-shadow,transform] duration-150 ease-out hover:bg-[#0C3038] active:translate-y-px focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D46B2C] focus-visible:ring-offset-2 focus-visible:ring-offset-[#F4F6F7] disabled:cursor-not-allowed disabled:border-[#AEBBBC] disabled:bg-[#AEBBBC] disabled:text-[#E9EEEE]"
            >
              Awaiting approval
            </button>
          </div>
        </section>

        {/* Interactive card */}
        <section aria-labelledby="industrial-card">
          <h2
            id="industrial-card"
            className="mb-4 text-[11px] font-bold uppercase tracking-[0.08em] text-[#607076]"
          >
            Card
          </h2>

          <a
            href="#north-terminal"
            className="group block max-w-xl rounded-[6px] border border-[#C7D0D2] bg-white p-5 transition-[border-color,background-color,box-shadow,transform] duration-150 ease-out hover:border-[#7E9297] hover:bg-[#FCFDFD] hover:shadow-[0_1px_2px_rgb(22_32_36_/_8%),0_8px_20px_rgb(22_32_36_/_10%)] active:translate-y-px focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D46B2C] focus-visible:ring-offset-2 focus-visible:ring-offset-[#F4F6F7]"
          >
            <div className="flex items-start justify-between gap-6">
              <div>
                <p className="font-['Geist_Mono'] text-[11px] font-medium tracking-[-0.01em] text-[#607076]">
                  JOB-0418 · EAST SECTOR
                </p>
                <h3 className="mt-2 font-['Archivo'] text-[20px] font-semibold leading-[1.25] tracking-[-0.008em] text-[#162024]">
                  North Terminal inspection
                </h3>
                <p className="mt-2 max-w-md text-[14px] leading-[1.5] text-[#607076]">
                  Three unresolved equipment flags require assignment before the next field
                  window.
                </p>
              </div>

              <span className="shrink-0 border border-[#D7AA8B] bg-[#F9E6D9] px-2 py-1 font-['Geist_Mono'] text-[10px] font-semibold uppercase tracking-[0.04em] text-[#8C3C17]">
                3 flags
              </span>
            </div>

            <div className="mt-5 flex items-center justify-between border-t border-[#DCE3E4] pt-3">
              <span className="font-['Geist_Mono'] text-[12px] font-medium tracking-[-0.01em] text-[#607076]">
                Due 18 Jul · 14:00
              </span>
              <span className="text-[13px] font-bold text-[#123B45] transition-transform duration-150 group-hover:translate-x-0.5">
                View job →
              </span>
            </div>
          </a>
        </section>

        {/* Data table */}
        <section aria-labelledby="industrial-table">
          <div className="mb-4 flex items-end justify-between">
            <div>
              <h2
                id="industrial-table"
                className="text-[11px] font-bold uppercase tracking-[0.08em] text-[#607076]"
              >
                Data table
              </h2>
              <p className="mt-1 text-[13px] text-[#607076]">Active work orders</p>
            </div>
            <button
              type="button"
              className="text-[12px] font-bold text-[#123B45] underline decoration-[#8FA0A4] underline-offset-4 transition-colors hover:text-[#D46B2C] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D46B2C] focus-visible:ring-offset-2 focus-visible:ring-offset-[#F4F6F7]"
            >
              View all
            </button>
          </div>

          <div className="overflow-x-auto rounded-[6px] border border-[#C7D0D2] bg-white">
            <table className="w-full min-w-[720px] border-collapse text-left">
              <thead className="bg-[#EDF1F1]">
                <tr className="border-b border-[#C7D0D2]">
                  {["Project", "Owner", "Status", "Due date", "Approved budget", ""].map((heading) => (
                    <th
                      key={heading || "action"}
                      scope="col"
                      className="px-4 py-3 text-[11px] font-bold uppercase tracking-[0.08em] text-[#607076]"
                    >
                      {heading}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr
                    key={row.project}
                    className="group border-b border-[#DCE3E4] last:border-b-0 hover:bg-[#F6F8F8] focus-within:bg-[#F1F5F5]"
                  >
                    <td className="px-4 py-3.5 text-[13px] font-bold text-[#162024]">
                      {row.project}
                    </td>
                    <td className="px-4 py-3.5 text-[13px] text-[#607076]">{row.owner}</td>
                    <td className="px-4 py-3.5">
                      <span
                        className={`inline-flex rounded-[2px] px-2 py-1 font-['Geist_Mono'] text-[10px] font-semibold uppercase tracking-[0.035em] ${statusClass[row.status as keyof typeof statusClass]}`}
                      >
                        {row.status}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 font-['Geist_Mono'] text-[12px] font-medium tracking-[-0.01em] text-[#243237]">
                      {row.date}
                    </td>
                    <td className="px-4 py-3.5 font-['Geist_Mono'] text-[12px] font-medium tabular-nums tracking-[-0.01em] text-[#243237]">
                      {row.budget}
                    </td>
                    <td className="px-4 py-3.5 text-right">
                      <button
                        type="button"
                        aria-label={`Open ${row.project}`}
                        className="text-[12px] font-bold text-[#123B45] opacity-0 transition-[color,opacity] duration-150 hover:text-[#D46B2C] focus-visible:opacity-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D46B2C] focus-visible:ring-offset-2 group-hover:opacity-100"
                      >
                        Open →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  );
}
```

---

## 2. Quiet editorial

```tsx
// QuietEditorialExamples.tsx
const rows = [
  { project: "Autumn House", owner: "L. Okafor", status: "In edit", date: "18 Jul", budget: "$42,680" },
  { project: "The Estuary", owner: "N. Reyes", status: "On schedule", date: "22 Jul", budget: "$18,420" },
  { project: "After the Rain", owner: "S. Wilson", status: "Review", date: "29 Jul", budget: "$31,050" },
];

const statusClass = {
  "In edit": "border-[#B97965] bg-[#F8E4DD] text-[#7D3423]",
  "On schedule": "border-[#89A495] bg-[#E5EEE7] text-[#355C43]",
  Review: "border-[#C7A86A] bg-[#F7EFD9] text-[#73561B]",
};

export default function QuietEditorialExamples() {
  return (
    <main className="min-h-screen bg-[#F5F0E8] px-6 py-12 font-['Public_Sans'] text-[#24211E] sm:px-10 md:py-16">
      <div className="mx-auto max-w-5xl space-y-16">
        <header className="border-b border-[#D4CABE] pb-8">
          <p className="text-[11px] font-bold uppercase tracking-[0.12em] text-[#756D64]">
            Studio ledger · July 2026
          </p>
          <h1 className="mt-3 font-['Newsreader'] text-[44px] font-medium leading-[1.04] tracking-[-0.024em] sm:text-[56px]">
            Quiet editorial
          </h1>
        </header>

        {/* Buttons */}
        <section aria-labelledby="editorial-buttons">
          <h2
            id="editorial-buttons"
            className="mb-5 text-[11px] font-bold uppercase tracking-[0.12em] text-[#756D64]"
          >
            Buttons
          </h2>

          <div className="flex flex-wrap items-center gap-x-6 gap-y-4">
            <button
              type="button"
              className="inline-flex min-h-11 items-center justify-center rounded-[4px] border border-[#2C302A] bg-[#2C302A] px-5 text-[13px] font-semibold text-[#FAF6EE] transition-[background-color,border-color,box-shadow,transform] duration-[160ms] [transition-timing-function:cubic-bezier(0.22,1,0.36,1)] hover:bg-[#464B42] hover:border-[#464B42] active:translate-y-px active:bg-[#1E211D] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A9462D] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F5F0E8] disabled:cursor-not-allowed disabled:border-[#A9A39B] disabled:bg-[#A9A39B] disabled:text-[#EAE5DD]"
            >
              Prepare call sheet
            </button>

            <button
              type="button"
              className="inline-flex min-h-11 items-center justify-center border-b border-[#756D64] px-1 text-[13px] font-semibold text-[#24211E] transition-[border-color,color,transform] duration-[160ms] [transition-timing-function:cubic-bezier(0.22,1,0.36,1)] hover:border-[#A9462D] hover:text-[#A9462D] active:translate-y-px focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A9462D] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F5F0E8] disabled:cursor-not-allowed disabled:border-[#C8C0B6] disabled:text-[#9A9187]"
            >
              Download treatment
            </button>

            <button
              type="button"
              disabled
              className="inline-flex min-h-11 items-center justify-center rounded-[4px] border border-[#2C302A] bg-[#2C302A] px-5 text-[13px] font-semibold text-[#FAF6EE] transition-[background-color,border-color,box-shadow,transform] duration-[160ms] [transition-timing-function:cubic-bezier(0.22,1,0.36,1)] hover:bg-[#464B42] active:translate-y-px focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A9462D] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F5F0E8] disabled:cursor-not-allowed disabled:border-[#A9A39B] disabled:bg-[#A9A39B] disabled:text-[#EAE5DD]"
            >
              Awaiting cut
            </button>
          </div>
        </section>

        {/* Interactive card */}
        <section aria-labelledby="editorial-card">
          <h2
            id="editorial-card"
            className="mb-5 text-[11px] font-bold uppercase tracking-[0.12em] text-[#756D64]"
          >
            Card
          </h2>

          <a
            href="#autumn-house"
            className="group block max-w-2xl border-y border-[#D4CABE] py-7 transition-colors duration-[260ms] [transition-timing-function:cubic-bezier(0.22,1,0.36,1)] hover:border-[#9A8D80] hover:bg-[#F8F3EB] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A9462D] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F5F0E8]"
          >
            <div className="grid gap-6 sm:grid-cols-[minmax(0,1fr)_auto]">
              <div>
                <p className="font-['DM_Mono'] text-[11px] font-medium tracking-[0.01em] text-[#756D64]">
                  FEATURE · POST-PRODUCTION · 04
                </p>
                <h3 className="mt-3 font-['Newsreader'] text-[32px] font-medium leading-[1.12] tracking-[-0.018em] text-[#24211E]">
                  Autumn House
                </h3>
                <p className="mt-3 max-w-xl text-[16px] leading-[1.62] tracking-[-0.002em] text-[#5F5850]">
                  The editor’s assembly is ready for review, with one music cue and two
                  archival clearances still unresolved.
                </p>
              </div>

              <span className="h-fit border border-[#B97965] bg-[#F8E4DD] px-2.5 py-1.5 font-['DM_Mono'] text-[10px] font-semibold uppercase tracking-[0.05em] text-[#7D3423]">
                In edit
              </span>
            </div>

            <div className="mt-7 flex items-center justify-between">
              <span className="font-['DM_Mono'] text-[11px] tracking-[0.01em] text-[#756D64]">
                Delivery · 18 July
              </span>
              <span className="text-[13px] font-semibold text-[#24211E] transition-[color,transform] duration-[160ms] group-hover:translate-x-1 group-hover:text-[#A9462D]">
                Open project →
              </span>
            </div>
          </a>
        </section>

        {/* Data table */}
        <section aria-labelledby="editorial-table">
          <div className="mb-5">
            <p className="text-[11px] font-bold uppercase tracking-[0.12em] text-[#756D64]">
              Current slate
            </p>
            <h2
              id="editorial-table"
              className="mt-2 font-['Newsreader'] text-[32px] font-medium leading-[1.12] tracking-[-0.018em]"
            >
              Productions in motion
            </h2>
          </div>

          <div className="overflow-x-auto border-y border-[#D4CABE]">
            <table className="w-full min-w-[720px] border-collapse text-left">
              <thead>
                <tr className="border-b border-[#D4CABE]">
                  {["Project", "Producer", "Stage", "Delivery", "Budget", ""].map((heading) => (
                    <th
                      key={heading || "action"}
                      scope="col"
                      className="px-3 py-3 text-[11px] font-bold uppercase tracking-[0.1em] text-[#756D64] first:pl-0 last:pr-0"
                    >
                      {heading}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr
                    key={row.project}
                    className="group border-b border-[#E0D8CE] last:border-b-0 transition-colors duration-[160ms] hover:bg-[#F8F3EB] focus-within:bg-[#F8F3EB]"
                  >
                    <td className="px-3 py-5 font-['Newsreader'] text-[21px] font-medium leading-[1.2] tracking-[-0.01em] first:pl-0">
                      {row.project}
                    </td>
                    <td className="px-3 py-5 text-[14px] text-[#5F5850]">{row.owner}</td>
                    <td className="px-3 py-5">
                      <span
                        className={`inline-flex border px-2 py-1 font-['DM_Mono'] text-[10px] font-medium uppercase tracking-[0.04em] ${statusClass[row.status as keyof typeof statusClass]}`}
                      >
                        {row.status}
                      </span>
                    </td>
                    <td className="px-3 py-5 font-['DM_Mono'] text-[11px] tracking-[0.01em] text-[#5F5850]">
                      {row.date}
                    </td>
                    <td className="px-3 py-5 font-['DM_Mono'] text-[11px] tabular-nums tracking-[0.01em] text-[#5F5850]">
                      {row.budget}
                    </td>
                    <td className="px-0 py-5 text-right">
                      <button
                        type="button"
                        aria-label={`Open ${row.project}`}
                        className="text-[13px] font-semibold text-[#24211E] underline decoration-transparent underline-offset-4 transition-[color,text-decoration-color] duration-[160ms] hover:text-[#A9462D] hover:decoration-[#A9462D] focus-visible:decoration-[#A9462D] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A9462D] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F5F0E8]"
                      >
                        Open
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  );
}
```

---

## 3. Playful consumer

```tsx
// PlayfulConsumerExamples.tsx
const rows = [
  { habit: "Morning stretch", streak: "12 days", status: "On fire", next: "Today", score: "+36" },
  { habit: "Sketch for fun", streak: "6 days", status: "Growing", next: "Today", score: "+18" },
  { habit: "Read 15 minutes", streak: "3 days", status: "New", next: "Tomorrow", score: "+9" },
];

const statusClass = {
  "On fire": "border-[#D17A15] bg-[#FFF0C8] text-[#703B00]",
  Growing: "border-[#4CB184] bg-[#DCF7E9] text-[#124C35]",
  New: "border-[#7768E4] bg-[#E9E4FF] text-[#3D317E]",
};

export default function PlayfulConsumerExamples() {
  return (
    <main className="min-h-screen bg-[#F7F5FF] px-5 py-8 font-['DM_Sans'] text-[#24203D] sm:px-8 sm:py-12">
      <div className="mx-auto max-w-5xl space-y-10">
        <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-[12px] font-bold tracking-[0.02em] text-[#716B88]">Your component kit</p>
            <h1 className="mt-1 font-['Bricolage_Grotesque'] text-[36px] font-bold leading-[1.08] tracking-[-0.025em] sm:text-[52px]">
              Playful consumer
            </h1>
          </div>
          <span className="w-fit rounded-full bg-[#E9E4FF] px-3 py-1.5 text-[12px] font-bold text-[#4A3AB2]">
            Small wins, daily
          </span>
        </header>

        {/* Buttons */}
        <section aria-labelledby="playful-buttons">
          <h2
            id="playful-buttons"
            className="mb-4 font-['Bricolage_Grotesque'] text-[20px] font-bold tracking-[-0.008em]"
          >
            Buttons
          </h2>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              className="inline-flex min-h-11 items-center justify-center rounded-[14px] border border-[#5A47D5] bg-[#5A47D5] px-5 text-[14px] font-bold text-white shadow-[0_2px_4px_rgb(36_32_61_/_7%),0_10px_24px_rgb(90_71_213_/_16%)] transition-[background-color,border-color,box-shadow,transform] duration-[140ms] [transition-timing-function:cubic-bezier(0.2,0.8,0.2,1)] hover:-translate-y-0.5 hover:bg-[#4938C5] hover:shadow-[0_4px_10px_rgb(36_32_61_/_9%),0_14px_28px_rgb(90_71_213_/_22%)] active:translate-y-px active:scale-[0.98] active:bg-[#3E2FA8] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5A47D5] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F7F5FF] disabled:cursor-not-allowed disabled:border-[#B6AEE2] disabled:bg-[#B6AEE2] disabled:text-[#F5F2FF] disabled:shadow-none"
            >
              Log today’s win
            </button>

            <button
              type="button"
              className="inline-flex min-h-11 items-center justify-center rounded-[14px] border border-[#DCD7EF] bg-white px-5 text-[14px] font-bold text-[#342B76] shadow-[0_1px_2px_rgb(36_32_61_/_5%),0_7px_16px_rgb(90_71_213_/_8%)] transition-[background-color,border-color,box-shadow,transform] duration-[140ms] [transition-timing-function:cubic-bezier(0.2,0.8,0.2,1)] hover:-translate-y-0.5 hover:border-[#AFA5EC] hover:bg-[#F5F2FF] hover:shadow-[0_2px_5px_rgb(36_32_61_/_7%),0_10px_20px_rgb(90_71_213_/_12%)] active:translate-y-px active:scale-[0.98] active:bg-[#E9E4FF] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5A47D5] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F7F5FF] disabled:cursor-not-allowed disabled:border-[#E6E1F4] disabled:bg-[#F4F2F9] disabled:text-[#AAA3BD] disabled:shadow-none"
            >
              Edit habits
            </button>

            <button
              type="button"
              disabled
              className="inline-flex min-h-11 items-center justify-center rounded-[14px] border border-[#5A47D5] bg-[#5A47D5] px-5 text-[14px] font-bold text-white shadow-[0_2px_4px_rgb(36_32_61_/_7%),0_10px_24px_rgb(90_71_213_/_16%)] transition-[background-color,border-color,box-shadow,transform] duration-[140ms] [transition-timing-function:cubic-bezier(0.2,0.8,0.2,1)] hover:-translate-y-0.5 hover:bg-[#4938C5] active:translate-y-px active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5A47D5] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F7F5FF] disabled:cursor-not-allowed disabled:border-[#B6AEE2] disabled:bg-[#B6AEE2] disabled:text-[#F5F2FF] disabled:shadow-none"
            >
              Come back tomorrow
            </button>
          </div>
        </section>

        {/* Interactive card */}
        <section aria-labelledby="playful-card">
          <h2
            id="playful-card"
            className="mb-4 font-['Bricolage_Grotesque'] text-[20px] font-bold tracking-[-0.008em]"
          >
            Card
          </h2>

          <a
            href="#morning-stretch"
            className="group relative block max-w-xl overflow-hidden rounded-[20px] border border-[#DCD7EF] bg-white p-6 shadow-[0_1px_2px_rgb(36_32_61_/_5%),0_7px_16px_rgb(90_71_213_/_8%)] transition-[border-color,box-shadow,transform] duration-[220ms] [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] hover:-translate-y-1 hover:border-[#B2A8EF] hover:shadow-[0_5px_12px_rgb(36_32_61_/_10%),0_22px_42px_rgb(90_71_213_/_17%)] active:translate-y-0 active:scale-[0.99] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5A47D5] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F7F5FF]"
          >
            <div className="absolute -right-10 -top-12 h-40 w-40 rounded-[58%_42%_51%_49%_/_42%_55%_45%_58%] bg-[#E9E4FF] transition-transform duration-[320ms] [transition-timing-function:cubic-bezier(0.34,1.56,0.64,1)] group-hover:rotate-12 group-hover:scale-110" />
            <div className="absolute right-10 top-8 h-8 w-8 rounded-full bg-[#FFB94D] transition-transform duration-[320ms] [transition-timing-function:cubic-bezier(0.34,1.56,0.64,1)] group-hover:-translate-y-1 group-hover:translate-x-1" />

            <div className="relative">
              <div className="flex items-start justify-between gap-5">
                <div>
                  <p className="text-[12px] font-bold tracking-[0.02em] text-[#716B88]">
                    Your next tiny win
                  </p>
                  <h3 className="mt-2 font-['Bricolage_Grotesque'] text-[28px] font-bold leading-[1.14] tracking-[-0.018em] text-[#24203D]">
                    Morning stretch
                  </h3>
                </div>

                <span className="rounded-full border border-[#D17A15] bg-[#FFF0C8] px-3 py-1.5 text-[12px] font-bold text-[#703B00]">
                  12-day streak
                </span>
              </div>

              <p className="mt-3 max-w-sm text-[16px] font-medium leading-[1.5] text-[#5E5874]">
                Two minutes counts. Give your shoulders a little “thank you.”
              </p>

              <div className="mt-6 flex items-center justify-between">
                <span className="rounded-full bg-[#DCF7E9] px-3 py-1.5 text-[12px] font-bold text-[#124C35]">
                  +3 energy points
                </span>
                <span className="text-[14px] font-bold text-[#5A47D5] transition-transform duration-[140ms] group-hover:translate-x-1">
                  Check in →
                </span>
              </div>
            </div>
          </a>
        </section>

        {/* Data table */}
        <section aria-labelledby="playful-table">
          <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
            <div>
              <p className="text-[12px] font-bold tracking-[0.02em] text-[#716B88]">This week</p>
              <h2
                id="playful-table"
                className="mt-1 font-['Bricolage_Grotesque'] text-[28px] font-bold leading-[1.14] tracking-[-0.018em]"
              >
                Habit scoreboard
              </h2>
            </div>
            <button
              type="button"
              className="rounded-full border border-[#DCD7EF] bg-white px-3 py-2 text-[12px] font-bold text-[#4A3AB2] transition-[background-color,border-color,transform] duration-[140ms] hover:-translate-y-0.5 hover:border-[#AFA5EC] hover:bg-[#F5F2FF] active:translate-y-px focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5A47D5] focus-visible:ring-offset-3 focus-visible:ring-offset-[#F7F5FF]"
            >
              See all habits
            </button>
          </div>

          <div className="overflow-x-auto rounded-[20px] border border-[#DCD7EF] bg-white shadow-[0_1px_2px_rgb(36_32_61_/_5%),0_7px_16px_rgb(90_71_213_/_8%)]">
            <table className="w-full min-w-[700px] border-collapse text-left">
              <thead className="bg-[#F0EDF8]">
                <tr className="border-b border-[#DCD7EF]">
                  {["Habit", "Streak", "Mood", "Next up", "Points", ""].map((heading) => (
                    <th
                      key={heading || "action"}
                      scope="col"
                      className="px-5 py-3 text-[12px] font-bold tracking-[0.02em] text-[#716B88]"
                    >
                      {heading}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr
                    key={row.habit}
                    className="group border-b border-[#E9E5F4] last:border-b-0 transition-colors duration-[140ms] hover:bg-[#FAF9FF] focus-within:bg-[#F5F2FF]"
                  >
                    <td className="px-5 py-4 text-[14px] font-bold text-[#24203D]">{row.habit}</td>
                    <td className="px-5 py-4">
                      <span className="rounded-full bg-[#E9E4FF] px-2.5 py-1 text-[12px] font-bold text-[#4A3AB2]">
                        {row.streak}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <span
                        className={`inline-flex rounded-full border px-2.5 py-1 text-[12px] font-bold ${statusClass[row.status as keyof typeof statusClass]}`}
                      >
                        {row.status}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-[14px] font-medium text-[#5E5874]">{row.next}</td>
                    <td className="px-5 py-4 font-['Bricolage_Grotesque'] text-[20px] font-bold leading-none tracking-[-0.02em] text-[#5A47D5]">
                      {row.score}
                    </td>
                    <td className="px-5 py-4 text-right">
                      <button
                        type="button"
                        aria-label={`Check in to ${row.habit}`}
                        className="rounded-full bg-[#5A47D5] px-3 py-1.5 text-[12px] font-bold text-white opacity-0 shadow-[0_2px_4px_rgb(36_32_61_/_7%),0_10px_20px_rgb(90_71_213_/_16%)] transition-[background-color,box-shadow,opacity,transform] duration-[140ms] hover:-translate-y-0.5 hover:bg-[#4938C5] active:translate-y-px active:scale-[0.97] focus-visible:opacity-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5A47D5] focus-visible:ring-offset-3 group-hover:opacity-100"
                      >
                        Done!
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  );
}
```

The main character differences are concentrated in:

- **Precision industrial:** tight radius, rule-based surfaces, minimal shadow, compact mono metadata, restrained transitions.
- **Quiet editorial:** mostly flat surfaces, generous vertical rhythm, serif hierarchy, underline-led secondary actions, low-noise states.
- **Playful consumer:** larger radius, brighter controlled color, soft elevated shadows, expressive display type, springier movement, rounded status/pill treatment.

## P7 — Motion system

I ship a **small, role-based motion system**, not a set of arbitrary animation durations.

The system has three goals:

1. **Preserve orientation** — show where something came from, where it went, or what changed.
2. **Confirm interaction** — make hover, press, selection, loading, and completion states feel responsive.
3. **Protect reading and task flow** — motion should not delay access, compete with data, or make dense UI feel unstable.

My default implementation is **CSS transitions and keyframes**. I use `motion/react` only when a transition needs mount/unmount coordination, layout-aware animation, drag behavior, sequencing, or stateful gesture behavior that CSS cannot express cleanly.

I do **not** use `framer-motion` imports in this environment; when needed, the available compatible library is `motion/react`.

---

# 1. Duration tiers

```css
:root {
  --motion-instant: 80ms;
  --motion-fast: 120ms;
  --motion-standard: 180ms;
  --motion-slow: 240ms;
  --motion-overlay: 320ms;
  --motion-emphasis: 420ms;
}
```

|Tier|Duration|Use it for|
|---|---|---|
|Instant|`80ms`|Press feedback, checkbox/radio state, very small icon feedback|
|Fast|`120ms`|Hover, focus, border-color, background-color, button-state changes, small tooltips|
|Standard|`180ms`|Tabs, selected-state changes, compact popovers, row expansion, small panel shifts|
|Slow|`240ms`|Small drawers, accordion content, context panels, larger reveal transitions|
|Overlay|`320ms`|Dialogs, mobile sheets, full-size menus, contextual side panels|
|Emphasis|`420ms`|One-time onboarding, celebration, hero reveal, nonessential brand motion|

## Actual application rules

```text
80ms   → press/tap compression, checkbox tick, icon nudge
120ms  → hover/focus states, color transitions, small control states
180ms  → tab content, popover/tooltip, selected content state
240ms  → accordion, inspector panel, non-blocking contextual expansion
320ms  → modal, sheet, command palette, mobile navigation
420ms  → one-off completion celebration or initial hero composition only
```

I do not make common actions slower than `180ms` unless the animation provides a meaningful spatial transition.

For example:

- A button changing color at `320ms` feels laggy.
- A dialog appearing in `80ms` can feel abrupt.
- A data-table row should not drift into place over `400ms`.
- A toast should enter quickly enough to be noticed without pulling attention from the active task.

---

# 2. Exact easing curves

```css
:root {
  /* General utility motion */
  --ease-standard: cubic-bezier(0.2, 0, 0, 1);
  --ease-enter: cubic-bezier(0, 0, 0, 1);
  --ease-exit: cubic-bezier(0.3, 0, 1, 1);

  /* Softer editorial motion */
  --ease-editorial: cubic-bezier(0.22, 1, 0.36, 1);
  --ease-editorial-enter: cubic-bezier(0.16, 1, 0.3, 1);

  /* Expressive but controlled consumer motion */
  --ease-playful: cubic-bezier(0.2, 0.8, 0.2, 1);
  --ease-spring-soft: cubic-bezier(0.34, 1.56, 0.64, 1);

  /* Decisive operational motion */
  --ease-operational: cubic-bezier(0.2, 0, 0, 1);
  --ease-operational-exit: cubic-bezier(0.4, 0, 1, 1);
}
```

## When I use each curve

|Curve|Use|
|---|---|
|`cubic-bezier(0.2, 0, 0, 1)`|Default UI motion: buttons, focus, tabs, menus, compact state changes|
|`cubic-bezier(0, 0, 0, 1)`|Entering elements that should arrive directly and clearly|
|`cubic-bezier(0.3, 0, 1, 1)`|Exits that should get out of the way quickly|
|`cubic-bezier(0.22, 1, 0.36, 1)`|Editorial image/caption reveals, polished card motion, soft page transitions|
|`cubic-bezier(0.16, 1, 0.3, 1)`|Larger calm enters: drawers, menus, image overlays, restrained sheets|
|`cubic-bezier(0.2, 0.8, 0.2, 1)`|Consumer interaction feedback and approachable card hover|
|`cubic-bezier(0.34, 1.56, 0.64, 1)`|Small, celebratory overshoot only: a completion check, reward token, tiny icon—not entire panels or core navigation|

## Rules for spring-like easing

I use `--ease-spring-soft` only for **small, positive feedback moments**:

- a completed habit check,
- a reaction button,
- a tiny badge settling into place,
- a progress reward,
- an icon in a playful onboarding screen.

I do not use spring overshoot for:

- modals,
- tables,
- forms,
- navigation,
- charts,
- enterprise controls,
- destructive actions,
- warnings or errors.

---

# 3. Properties I animate and properties I avoid

## Properties I regularly animate

|Property|Typical use|Why|
|---|---|---|
|`opacity`|Enter/exit, selected content, skeletons, overlays|Low-cost and visually clear|
|`transform`|Hover lift, press scale, panel enter/exit, icon nudge|Usually compositor-friendly and does not reflow layout|
|`background-color`|Buttons, tabs, selected rows, status state|Confirms state without moving layout|
|`color`|Links, labels, icon state|Communicates state cleanly|
|`border-color`|Focus, hover, selected input, panel emphasis|Supports structure without visual drama|
|`outline-color` / `box-shadow`|Focus ring and limited elevation change|Useful when localized and short|
|`text-decoration-color`|Editorial link underline reveal|Good for text-led interactions|
|`clip-path`|Rarely, for isolated image/art direction|Only for nonessential rich media, not standard controls|
|`grid-template-rows`|Accordion expansion|Controlled exception for semantic content reveal|

## Properties I do not animate by default

|Property|Why|
|---|---|
|`width` / `height`|Causes layout work; usually creates unstable content movement|
|`top` / `right` / `bottom` / `left`|Prefer `transform`; positional animation often causes layout/repaint work|
|`margin` / `padding`|Reflows siblings and makes dense layouts jump|
|`font-size`|Causes layout shift and makes text feel unstable|
|`line-height`|Causes reflow and can disrupt reading|
|`letter-spacing`|Can cause jitter, reflow, and text readability issues|
|`border-width`|Moves content and changes component dimensions|
|`filter: blur()`|Expensive at large areas; can look mushy and harm contrast|
|`backdrop-filter`|Expensive and visually inconsistent during animation|
|`background-position` across a whole page|Commonly creates meaningless “drifting” visual noise|
|continuously changing gradient coordinates|Distracting unless the product is explicitly visual/media-led|
|continuous turbulence/displacement filters|GPU-heavy and usually decorative rather than informative|

## Exceptions

### `height` or layout-like expansion

For accordions, disclosures, and content reveals, I may animate a controlled layout property—not because it is free, but because the change is semantically meaningful.

I prefer `grid-template-rows: 0fr → 1fr` over a hard-coded `height`, because it can accommodate unknown content length.

### `box-shadow`

I animate shadows only on isolated objects:

- a hoverable card,
- a floating menu,
- a primary consumer button,
- a dialog.

I do not animate shadows across every table row or list item in a dense dashboard.

---

# 4. Stance-to-motion system

|Dimension|Quiet editorial site|Operations dashboard|Playful consumer app|
|---|---|---|---|
|Core tone|Calm, composed, reading-friendly|Immediate, precise, non-distracting|Encouraging, expressive, responsive|
|Default duration|`160–260ms`|`80–180ms`|`120–220ms`|
|Overlay duration|`320ms`|`180–240ms`|`240–320ms`|
|Main easing|`cubic-bezier(0.22, 1, 0.36, 1)`|`cubic-bezier(0.2, 0, 0, 1)`|`cubic-bezier(0.2, 0.8, 0.2, 1)`|
|Hover|Subtle underline, image zoom ≤ `1.02`, slight color shift|Border/background shift, no theatrical lift|Small lift, color response, optional scale ≤ `1.02`|
|Press|Usually `translateY(1px)` only|`translateY(1px)`; fast confirmation|`scale(0.98)` plus `translateY(1px)`|
|Cards|Often no motion, or 1–2px lift max|Generally no lift; state through border/surface|2–4px lift possible for tappable cards|
|Navigation|Soft reveal, no bounce|Fast state change, no spatial flourish|Direct selection response with small active marker movement|
|Toast|Soft fade/slide, `240ms`|Fast fade/slide, `180ms`|Friendly slide/scale, `220ms`|
|Completion state|Minimal, maybe text change or quiet check|Immediate status change, no celebration|Optional small check/badge spring, `220–320ms`|
|Skeleton|Low-contrast shimmer or pulse only if loading is expected|Subtle opacity pulse, often static preferred|Soft shimmer can be acceptable, still low contrast|
|Forbidden feeling|Overly productized SaaS animation|Playful bounce, delayed panels, floating cards|Cold abruptness, entirely static reward moments|

---

# 5. Micro-interaction recipes

## A. Hover lift

Use for a clearly interactive card or tile. Do not use it on every card in a dashboard.

```css
.interactive-card {
  border: 1px solid #DCD7EF;
  border-radius: 20px;
  background: #FFFFFF;
  box-shadow:
    0 1px 2px rgb(36 32 61 / 5%),
    0 7px 16px rgb(90 71 213 / 8%);
  transition:
    transform 140ms cubic-bezier(0.2, 0.8, 0.2, 1),
    border-color 140ms cubic-bezier(0.2, 0.8, 0.2, 1),
    box-shadow 140ms cubic-bezier(0.2, 0.8, 0.2, 1);
}

@media (hover: hover) and (pointer: fine) {
  .interactive-card:hover {
    transform: translateY(-3px);
    border-color: #B2A8EF;
    box-shadow:
      0 5px 12px rgb(36 32 61 / 10%),
      0 22px 42px rgb(90 71 213 / 17%);
  }
}

.interactive-card:active {
  transform: translateY(0) scale(0.99);
}

.interactive-card:focus-visible {
  outline: 3px solid #5A47D5;
  outline-offset: 4px;
}
```

### Industrial variation

```css
.industrial-card {
  transition:
    border-color 120ms cubic-bezier(0.2, 0, 0, 1),
    background-color 120ms cubic-bezier(0.2, 0, 0, 1);
}

@media (hover: hover) and (pointer: fine) {
  .industrial-card:hover {
    border-color: #7E9297;
    background: #FCFDFD;
  }
}
```

No lift. The card becomes more available, not more playful.

---

## B. Press feedback

```css
.primary-button {
  transition:
    transform 80ms cubic-bezier(0.2, 0, 0, 1),
    background-color 120ms cubic-bezier(0.2, 0, 0, 1),
    border-color 120ms cubic-bezier(0.2, 0, 0, 1),
    box-shadow 120ms cubic-bezier(0.2, 0, 0, 1);
}

.primary-button:active:not(:disabled) {
  transform: translateY(1px);
}

.primary-button:disabled {
  cursor: not-allowed;
}
```

### Playful consumer variation

```css
.playful-primary-button {
  transition:
    transform 90ms cubic-bezier(0.2, 0.8, 0.2, 1),
    background-color 140ms cubic-bezier(0.2, 0.8, 0.2, 1),
    box-shadow 140ms cubic-bezier(0.2, 0.8, 0.2, 1);
}

.playful-primary-button:active:not(:disabled) {
  transform: translateY(1px) scale(0.98);
}
```

The scale is deliberately small. Do not use `scale(0.9)` or an exaggerated elastic bounce for ordinary button press feedback.

---

## C. Tab switch

For a standard tab interface, I use immediate state change plus a small content transition. The tab itself should not “fly”; the active state should move or appear clearly.

```tsx
import { useState } from "react";

const tabs = ["Overview", "Schedule", "Budget"] as const;
type Tab = (typeof tabs)[number];

export function TabsExample() {
  const [activeTab, setActiveTab] = useState<Tab>("Overview");

  return (
    <section>
      <div
        role="tablist"
        aria-label="Project views"
        className="inline-flex rounded-[8px] border border-[#C7D0D2] bg-[#EDF1F1] p-1"
      >
        {tabs.map((tab) => (
          <button
            key={tab}
            type="button"
            role="tab"
            aria-selected={activeTab === tab}
            onClick={() => setActiveTab(tab)}
            className={[
              "rounded-[4px] px-3 py-2 text-[13px] font-bold transition-[background-color,color,box-shadow] duration-[120ms] [transition-timing-function:cubic-bezier(0.2,0,0,1)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D46B2C] focus-visible:ring-offset-2 focus-visible:ring-offset-[#F4F6F7]",
              activeTab === tab
                ? "bg-white text-[#162024] shadow-[0_1px_2px_rgb(22_32_36_/_8%)]"
                : "text-[#607076] hover:text-[#243237]",
            ].join(" ")}
          >
            {tab}
          </button>
        ))}
      </div>

      <div
        key={activeTab}
        role="tabpanel"
        className="mt-4 animate-[tab-enter_180ms_cubic-bezier(0,0,0,1)_both]"
      >
        {activeTab === "Overview" && <p>Overview content</p>}
        {activeTab === "Schedule" && <p>Schedule content</p>}
        {activeTab === "Budget" && <p>Budget content</p>}
      </div>
    </section>
  );
}
```

```css
@keyframes tab-enter {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

Use `translateY(4px)` or less. The user is switching content, not traveling through space.

---

## D. Accordion expand/collapse

Use a semantic button with `aria-expanded`, not a visually clickable non-button element.

```tsx
import { useState } from "react";

export function AccordionExample() {
  const [open, setOpen] = useState(false);

  return (
    <section className="max-w-xl border-y border-[#D4CABE]">
      <h2>
        <button
          type="button"
          aria-expanded={open}
          aria-controls="delivery-notes"
          onClick={() => setOpen((value) => !value)}
          className="flex w-full items-center justify-between gap-4 py-5 text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A9462D] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F5F0E8]"
        >
          <span className="font-['Newsreader'] text-[23px] font-medium leading-[1.22] tracking-[-0.01em]">
            Delivery notes
          </span>
          <span
            aria-hidden="true"
            className={[
              "text-[20px] transition-transform duration-[180ms] [transition-timing-function:cubic-bezier(0.22,1,0.36,1)]",
              open ? "rotate-45" : "rotate-0",
            ].join(" ")}
          >
            +
          </span>
        </button>
      </h2>

      <div
        id="delivery-notes"
        className={[
          "grid transition-[grid-template-rows,opacity] duration-[240ms] [transition-timing-function:cubic-bezier(0.22,1,0.36,1)]",
          open ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0",
        ].join(" ")}
      >
        <div className="overflow-hidden">
          <div className="pb-6 text-[16px] leading-[1.62] text-[#5F5850]">
            Final delivery includes the ProRes master, caption files, social cutdowns,
            and an archived project package.
          </div>
        </div>
      </div>
    </section>
  );
}
```

The only layout-affecting transition is intentional: it reveals content whose space must actually open in the document.

---

## E. Toast enter and exit

For mount/unmount animation, I use `motion/react` when the toast must remain mounted through exit.

```tsx
import { AnimatePresence, motion } from "motion/react";

type ToastProps = {
  open: boolean;
  onDismiss: () => void;
};

export function Toast({ open, onDismiss }: ToastProps) {
  return (
    <AnimatePresence>
      {open ? (
        <motion.div
          role="status"
          aria-live="polite"
          initial={{ opacity: 0, y: 12, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 6, scale: 0.98 }}
          transition={{
            duration: 0.18,
            ease: [0.2, 0, 0, 1],
          }}
          className="fixed bottom-5 right-5 flex max-w-sm items-center gap-3 rounded-[10px] border border-[#B9CCCA] bg-[#F7FCFA] px-4 py-3 text-[#1D3B34] shadow-[0_2px_4px_rgb(22_32_36_/_8%),0_18px_42px_rgb(22_32_36_/_16%)]"
        >
          <span className="h-2 w-2 shrink-0 rounded-full bg-[#2C725E]" />
          <p className="text-[14px] font-medium">Shot list saved.</p>
          <button
            type="button"
            onClick={onDismiss}
            className="ml-auto text-[13px] font-bold text-[#1D3B34] underline underline-offset-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D46B2C] focus-visible:ring-offset-2"
          >
            Dismiss
          </button>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
```

### Toast rules

- Enter: `180ms`
- Exit: `120–180ms`
- Translate distance: `6–12px`
- Scale: no lower than `0.98`
- Never animate a toast from off-screen by hundreds of pixels.
- Do not use a bouncy entrance for warnings, failures, destructive events, or operational alerts.
- Use `role="status"` or `role="alert"` correctly based on urgency.

---

## F. Skeleton loading

A skeleton should communicate that content is expected soon. It should not look like an animated advertisement.

```css
.skeleton {
  position: relative;
  overflow: hidden;
  border-radius: 6px;
  background: #E8EDEB;
}

.skeleton::after {
  content: "";
  position: absolute;
  inset: 0;
  transform: translateX(-100%);
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgb(255 255 255 / 42%) 48%,
    transparent 100%
  );
  animation: skeleton-shimmer 1400ms cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

@keyframes skeleton-shimmer {
  to {
    transform: translateX(100%);
  }
}
```

```tsx
export function ProjectCardSkeleton() {
  return (
    <div
      aria-busy="true"
      aria-label="Loading project summary"
      className="rounded-[6px] border border-[#C7D0D2] bg-white p-5"
    >
      <div className="skeleton h-3 w-28" />
      <div className="skeleton mt-3 h-6 w-3/4" />
      <div className="skeleton mt-3 h-4 w-full" />
      <div className="skeleton mt-2 h-4 w-5/6" />
      <div className="mt-5 flex justify-between border-t border-[#DCE3E4] pt-3">
        <div className="skeleton h-3 w-24" />
        <div className="skeleton h-3 w-16" />
      </div>
    </div>
  );
}
```

### Skeleton rules

- Use shimmer only when the loading duration is uncertain or expected to exceed roughly `300–500ms`.
- Use a static placeholder for very short loading states to avoid flicker.
- Keep shimmer contrast low.
- Do not animate skeletons at multiple different speeds in the same screen.
- Preserve the final layout dimensions as closely as possible to avoid layout shift.

---

# 6. CSS versus `motion/react`

## CSS is my default for

- Hover and focus states
- Button press feedback
- Color, border, opacity, and simple transform transitions
- Accordion reveal
- Small static keyframe effects
- Skeleton shimmer
- Simple tab-content entry
- Tooltip/menu transitions when mount state is already retained

## `motion/react` is appropriate for

- Enter/exit transitions where elements unmount
- Dialog, toast, drawer, and sheet presence animation
- Coordinated sequences
- Layout-aware list reordering
- Drag interactions
- Gesture-driven interactions
- Shared-layout transitions when the spatial continuity is genuinely valuable

## I do not use a motion library just because animation exists

A typical dashboard should not import an animation framework for button hover states. CSS is smaller, more inspectable, and usually more robust for those interactions.

---

# 7. Reduced-motion policy

Reduced motion is not “disable all feedback.” It is:

- remove nonessential movement,
- keep state changes immediate,
- retain contrast, focus, and selection feedback,
- preserve usability without spatial motion.

## Global CSS baseline

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 1ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
    transition-duration: 1ms !important;
  }
}
```

For project code, I also prefer explicit reduced-motion overrides for richer effects:

```css
@media (prefers-reduced-motion: reduce) {
  .interactive-card,
  .playful-primary-button,
  .glass-panel,
  .skeleton::after {
    transition: none;
    animation: none;
  }

  .interactive-card:hover,
  .playful-primary-button:active {
    transform: none;
  }
}
```

## `motion/react` policy

```tsx
import { MotionConfig, motion } from "motion/react";

export function AppMotionBoundary({ children }: { children: React.ReactNode }) {
  return (
    <MotionConfig reducedMotion="user">
      {children}
    </MotionConfig>
  );
}
```

Then keep the fallback state legible even if all transform and opacity motion is removed.

## What remains with reduced motion

- Active tab changes immediately
- Focus ring appears immediately
- Toast still appears and can be dismissed
- Accordion still opens
- Selected controls still change fill/border/text
- Progress values still update
- Modal still becomes visible
- Loading states remain visible

The user loses decorative movement, not product feedback or navigation capability.

## P8 — The actual rulebook (Guidelines)

1. For any multi-section page, website, dashboard, product page, landing page, admin tool, or composed UI, read and apply the `aesthetic-stance` workflow before designing.
    
2. For a full-page or multi-section build, generate a project theme with `create_make_theme` before writing implementation code.
    
3. Summarize the full-page brief for `create_make_theme` in one or two sentences, including product type, audience, key task, and explicit aesthetic constraints.
    
4. Treat explicit user aesthetic direction as higher priority than generated theme suggestions.
    
5. Treat generated theme suggestions as a starting point and tiebreaker, not an override of the user’s requirements, existing brand, installed design system, or imported Figma design.
    
6. Choose one coherent visual stance for a composed interface and apply it consistently across layout, typography, surfaces, components, images, motion, and interaction states.
    
7. Do not mix unrelated aesthetic stances in one interface unless the contrast is explicitly motivated by the product or brief.
    
8. Do not default automatically to generic SaaS styling: light gray canvas, rounded white cards, blue primary button, soft gradient hero, equal-card grids, and familiar dashboard chrome.
    
9. Do not default automatically to warm editorial styling—off-white background plus serif display typography—unless the product and chosen stance support it.
    
10. Use product context, audience, content type, primary task, and trust level to determine the visual system.
    
11. Make the primary user task and most important information visually dominant.
    
12. Use realistic, contextually appropriate names, metrics, dates, labels, products, and copy.
    
13. Never use lorem ipsum or generic filler text in a designed interface.
    
14. Use CSS Grid for page-level composition, major columns, dashboard layouts, and responsive structural changes.
    
15. Use Flexbox for component internals, control groups, navigation clusters, icon-and-label alignment, and row-level layout.
    
16. Prefer intentional asymmetry or non-uniform proportions when they improve hierarchy; do not use equal-width columns or repeated card grids by default.
    
17. Use a deliberate page ground: light, dark, tinted, image-led, split, textured, or saturated only when appropriate to the stance.
    
18. Use accent color sparingly for primary action, selection, focus, status, or meaningful emphasis.
    
19. Do not apply accent color indiscriminately to headings, icons, dividers, cards, and backgrounds.
    
20. Use semantic color tokens rather than hard-coding unrelated colors in individual components.
    
21. Preserve the existing Tailwind token contract in `src/styles/theme.css`.
    
22. Preserve required token names including `--background`, `--foreground`, `--card`, `--card-foreground`, `--primary`, `--primary-foreground`, `--secondary`, `--secondary-foreground`, `--muted`, `--muted-foreground`, `--accent`, `--accent-foreground`, `--border`, `--ring`, and `--radius`.
    
23. Preserve the matching `.dark` token block when updating `src/styles/theme.css`.
    
24. Preserve the existing `@theme inline` mapping used by the project’s Tailwind setup.
    
25. Use token-backed Tailwind classes such as `bg-background`, `text-foreground`, `bg-card`, `text-card-foreground`, `bg-primary`, `text-primary-foreground`, and `border-border` rather than bypassing the system unnecessarily.
    
26. Do not rewrite the theme file from scratch when updating tokens; update its values while preserving the existing structure and contract.
    
27. Write the main UI component to `src/app/App.tsx`.
    
28. Export the main React component as the default export.
    
29. Add Google Font imports to `src/styles/fonts.css`.
    
30. Do not add an unlayered CSS reset such as `* { margin: 0; padding: 0; }`; Tailwind already provides a reset and an additional global reset can override utility behavior.
    
31. Use Tailwind CSS for styling by default.
    
32. Avoid inline styles unless a value must be dynamic or cannot reasonably be expressed through Tailwind or existing CSS.
    
33. Keep JSX valid: close all tags, balance all braces, and avoid malformed attribute syntax.
    
34. Use double-quoted strings when a string contains an apostrophe, or escape the apostrophe correctly in a single-quoted string.
    
35. Do not add packages unless required and installed; prefer the available dependency set.
    
36. Use `lucide-react` for standard interface icons when an icon is needed.
    
37. Import only the Lucide icons actually used.
    
38. Do not invent custom SVG icons when a suitable Lucide icon exists, unless the brief specifically requires a custom graphic or the icon itself is the deliverable.
    
39. Use `motion/react` for motion when needed; do not import from `framer-motion`.
    
40. Prefer CSS transitions for ordinary hover, focus, selection, and layout-state feedback when they are sufficient.
    
41. Avoid gratuitous animation; motion must communicate state change, spatial continuity, hierarchy, feedback, or brand character.
    
42. Respect `prefers-reduced-motion` for nonessential animation and avoid motion that blocks access to content.
    
43. Implement interactions implied by the brief with working React state and event handlers.
    
44. Implement working tabs, toggles, menus, filters, accordions, selection states, navigation, and other named controls rather than rendering them as static decoration.
    
45. Use `recharts` when the brief explicitly requests charts, rather than simulating charts with arbitrary divs or decorative SVG when appropriate.
    
46. For complex navigation, multiple pages, or URL-based state, use the project’s routing guidance before adding routing behavior.
    
47. Do not add routing to a single-view interface without a product reason.
    
48. Use Radix primitives where they meaningfully improve accessible dialogs, menus, tabs, popovers, accordions, or similar controls.
    
49. Do not assume a shadcn/ui design system is installed or mandated.
    
50. If an existing Make Kit, design system, or scoped component library is present, read its guidance before creating or modifying UI, CSS, icons, tokens, or components.
    
51. When a kit is present, use its component patterns, token system, icon rules, and accessibility conventions before applying personal defaults.
    
52. Do not replace an existing product design system with a new visual system unless the user specifically asks for a redesign.
    
53. When the user provides or references an imported Figma design, read the relevant design-import guidance before using imported code or reproducing the design.
    
54. Treat an imported Figma design as the primary visual reference unless the user asks for interpretation or a new direction.
    
55. Preserve the imported design’s visual language when reproducing it, while improving implementation quality, responsiveness, and intended interaction where appropriate.
    
56. When Figma motion metadata is supplied, follow the motion-context guidance rather than inventing unrelated animations.
    
57. When the user supplies an image, screenshot, photo, logo, mockup, or embedded SVG, read the image-attachment guidance before working with it.
    
58. When reproducing an uploaded screenshot or visual reference, prioritize the reference’s aesthetics and geometry over generic design preferences.
    
59. Use context-appropriate photography when imagery is needed.
    
60. Use Unsplash search when the task needs sourced photos or visual inspiration and no better project-specific image asset exists.
    
61. Give every meaningful image descriptive `alt` text.
    
62. Give image containers a suitable background color so layout and composition remain stable while images load.
    
63. Integrate images through intentional crop, aspect ratio, framing, overlay, or tonal treatment; do not insert unrelated stock images merely to fill space.
    
64. Use a display typeface only when it has a clear role in hierarchy or brand expression.
    
65. Use a readable UI/body typeface for general interface content.
    
66. Use a mono typeface only where it adds structure—such as metrics, dates, IDs, code, timestamps, logs, or technical labels.
    
67. Do not use mono typography as generic visual decoration.
    
68. Set letter spacing intentionally by text role.
    
69. Do not apply `tracking-tight` or `tracking-tighter` to display headings by default.
    
70. Use positive letter spacing primarily for small uppercase labels or deliberate metadata treatments.
    
71. Do not use the same typography treatment for display headings, body text, captions, labels, and data.
    
72. Avoid overused font defaults unless they are clearly correct for the chosen stance; examples to avoid as unexamined defaults include IBM Plex Mono, Space Grotesk, Syne, Cormorant Garamond, and Bebas Neue.
    
73. Use a consistent spacing scale across the interface.
    
74. Use smaller gaps within controls, medium gaps within components, larger gaps between content groups, and the largest gaps between page sections.
    
75. Use whitespace to establish hierarchy and reduce cognitive load; do not fill empty space with decorative components merely to make a page appear fuller.
    
76. Use thin, low-opacity borders and dividers to organize content.
    
77. Do not use heavy borders, excessive outlines, and stacked shadow cards as the default organization system.
    
78. Use shadows only when they communicate elevation, temporary overlay, floating context, or product materiality.
    
79. Standard cards should often be flat or border-separated; do not give every panel a large soft shadow.
    
80. Use decorative blur, glass, grain, gradient, glow, organic forms, refraction, or displacement only when they have a clear product, spatial, material, or brand role.
    
81. Do not use glass merely because a translucent card looks sophisticated.
    
82. Use backdrop blur primarily for localized floating controls, overlays, command palettes, inspectors, bottom sheets, or surfaces above meaningful visual content such as maps, video, a canvas, or artwork.
    
83. Provide a legible solid-color fallback for backdrop-filter effects.
    
84. Disable or simplify material effects in high-contrast contexts when they reduce clarity.
    
85. Do not use animated background gradients in operational, data-dense, or high-trust utility interfaces unless the animation itself communicates meaningful data or state.
    
86. Use grain/noise only as a subtle, static, nonessential background material; do not texture text, controls, dense panels, or every card.
    
87. Use glow only to communicate selected, active, live, energetic, or emitted-light states; do not make every CTA or metric glow.
    
88. Use organic shapes only when they fit the product subject or visual stance—such as wellness, creativity, food, biology, movement, youth, ecology, or handmade/collage identity.
    
89. Do not use random blobs solely to fill composition gaps.
    
90. Use SVG displacement, goo, specular lighting, or similar filters only for nonessential artwork or a clearly motivated immersive material effect.
    
91. Do not apply SVG distortion filters to body text, primary controls, navigation, tables, or any visual boundary that must remain exact and legible.
    
92. Avoid continuously animated turbulence, displacement, blur, or filter effects in normal product UI.
    
93. Treat accessibility as a baseline requirement, not a finishing pass.
    
94. Ensure normal body text meets at least WCAG AA contrast of 4.5:1.
    
95. Large text may use a minimum contrast of 3:1 where applicable.
    
96. Ensure interactive controls have at least 3:1 visible contrast against adjacent surfaces.
    
97. Never communicate a status, validation result, selection, or warning through color alone.
    
98. Provide visible keyboard focus states.
    
99. Ensure focus states remain visible on light, dark, image-led, glass, and selected surfaces.
    
100. Use semantic HTML controls where possible: buttons for actions, links for navigation, labels for inputs, headings for hierarchy, lists for list-like content, and tables for tabular data.
    
101. Do not make a clickable `div` when a semantic button, link, input, or native control is appropriate.
    
102. Maintain usable interaction targets, especially on mobile.
    
103. Include at least one meaningful responsive breakpoint around the desktop/tablet transition—roughly 1000px when appropriate.
    
104. Do not simply compress desktop layouts on mobile; intentionally reconsider hierarchy, ordering, columns, navigation, data density, spacing, and type size.
    
105. Ensure grids collapse intentionally at narrow widths.
    
106. Ensure dense data components remain usable on narrow screens through stacking, prioritization, horizontal containment, summaries, filters, or alternative views as appropriate.
    
107. Hide scrollbars by default and reveal them while scrolling only when that behavior is appropriate and does not impair discoverability or accessibility.
    
108. For isolated icons, logos, brand marks, crests, badges, monograms, and standalone vector illustrations, use the icon-illustration workflow rather than page-level aesthetic-stances.
    
109. Read a single-mark brief through subject, treatment, aesthetic register, use context, and constraints.
    
110. For a subject-specific mark, identify the generic first idea before drawing it.
    
111. Identify at least three shape-level features that distinguish the requested subject from the generic category version.
    
112. Apply an inversion test to each distinguishing feature: if it also describes a generic version of the subject, it is not specific enough.
    
113. If subject-specific distinctions cannot be identified confidently, select a named reference—such as a particular era, regional tradition, designer, or canonical example—rather than pretending generic category traits are specific.
    
114. Design marks in perceptual order: silhouette first, major positive and negative shapes second, interior detail last.
    
115. Do not spend most of a mark’s design budget on interior detail that will disappear at the intended size.
    
116. Design every mark against its smallest intended display size.
    
117. Assume a favicon may need to work at 16px, a desktop icon around 32–48px, a small logo around 48px, and an app icon around 60px unless the brief specifies otherwise.
    
118. Remove detail that does not survive the mark’s scale floor.
    
119. Match the visible-element count in a mark to the explicit nouns in the brief.
    
120. Do not add unrequested wordmarks, taglines, stars, sparkles, ambient dots, glows, highlights, banners, or mockup cards around a mark unless the brief explicitly calls for them.
    
121. Treat negative space as a designed shape.
    
122. Prefer overlap, notch, interlock, occlusion, or shared boundaries when multiple elements can be integrated meaningfully.
    
123. Do not assume mathematical centering produces optical centering.
    
124. Adjust marks by eye for visual weight, round-form overshoot, point extension, and asymmetrical balance.
    
125. Use one coherent drawing vocabulary per mark—such as geometric fill, monoweight outline, stipple, woodcut, halftone, or isometric construction.
    
126. Do not mix unrelated drawing treatments in a mark unless the contrast itself is purposeful and structurally clear.
    
127. Start a mark in monochrome plus a neutral unless the brief or use context requires additional color.
    
128. Do not use multi-stop gradients in a mark unless the use context or brand system explicitly calls for depth or gradient materiality.
    
129. Render a standalone vector mark as one self-contained SVG with a declared `viewBox` matching the intended canvas.
    
130. If a mark uses a tile, badge, pin, circle, or rounded-square background, render that shape inside the SVG as the first relevant shape rather than using an outer layout wrapper as the graphic itself.
    
131. Do not nest SVG elements inside unnecessary absolutely positioned wrapper stacks.
    
132. Match the surrounding page background to the mark background where needed so no visible canvas seam appears.
    
133. Before shipping a mark, verify small-scale legibility, element discipline, intentional negative space, and deviation from the generic default.
    
134. Do not add a backend, authentication, or database merely to make a UI prototype appear complete.
    
135. When a brief explicitly needs persistence, authentication, uploads, or external API access, use the relevant backend guidance and required secret-management workflow.
    
136. Do not expose secrets in client code, source files, or visible UI.
    
137. Use the provided Supabase connection and secret workflows when Supabase is explicitly needed.
    
138. Do not call backend services with API keys from the browser unless the architecture explicitly supports safe client-side use.
    
139. Do not create auxiliary planning files, sidecar artifacts, or unnecessary temporary deliverables when implementing a UI task.
    
140. Keep implementation focused on the requested output and required project files.
    
141. Do not ask a plain-text clarifying question when an approved user-question tool is available and a question is genuinely required.
    
142. Ask for clarification only when it materially affects the result; otherwise make the strongest reasonable design decision and proceed.
    
143. When a user is dissatisfied or says something is wrong, move directly into a concrete correction workflow rather than defensiveness or vague apology.
    
144. If repeated attempts do not resolve a design problem, propose specific alternative directions and ask the user to choose one.
    
145. Do not claim a tool generated a token set, implementation, image, or design output unless the tool was actually called and produced it.
    
146. When reproducing raw tool output, preserve it exactly rather than paraphrasing it as though it were verbatim.
    
147. Treat every new user brief as potentially adding task-specific constraints that override general defaults.
    
148. Prefer fewer, stronger, justified design decisions over a larger number of fashionable visual treatments.

## P9 — Iteration protocol (vague feedback → system changes)

Vague feedback is useful, but it is not an implementation instruction. I treat it as a signal that the person is reacting to an underlying mismatch in **hierarchy, identity, density, contrast, materiality, or product fit**.

I do not translate:

> “Make it pop” → “Add a gradient, brighter color, larger shadows, more animation.”

I translate it into a diagnosis process.

---

# 1. “Make it pop”

## What I diagnose first

In order:

1. **Is the primary message or action visually clear?**
2. **Is everything the same visual weight?**
3. **Is the section too symmetrical, too evenly spaced, or too card-like?**
4. **Is the color system too low-contrast for the intended priority?**
5. **Is there a missing focal object: a key metric, exception, product visual, chart, or CTA?**
6. **Does “pop” actually mean the user wants more brand personality rather than more hierarchy?**

“Make it pop” usually means one of these:

- “I cannot tell what matters.”
- “The page has no focal point.”
- “It feels too safe or generic.”
- “The brand personality is absent.”
- “The important action does not feel important.”
- “The visual pacing is flat.”

## System levers I consider, in order

1. **Hierarchy**
    
    - Change relative scale.
    - Change section proportion.
    - Make a key object larger or more immediate.
    - Demote supporting information.
2. **Composition**
    
    - Break an equal-card layout.
    - Create an asymmetric primary/secondary relationship.
    - Introduce a clear visual anchor.
3. **Contrast**
    
    - Strengthen foreground/background contrast on the primary element.
    - Introduce a controlled accent only in the primary area.
    - Improve surface separation.
4. **Typography**
    
    - Use a stronger display or metric treatment.
    - Increase scale selectively.
    - Improve label/value contrast.
    - Reduce generic all-same-size body text.
5. **Semantic visual material**
    
    - Add a chart, progress state, meaningful icon, project thumbnail, or image only if it clarifies the task.
6. **Micro-interaction**
    
    - Add a restrained hover or active state only after the static hierarchy works.

## What I change

- The main metric, primary action, or current exception.
- The section’s proportions.
- The contrast relationship between important and secondary content.
- The typographic hierarchy.
- The selected/active state.
- The data visualization if a visual trend is more informative than another card.

## What I refuse to change

- I do not add gradients, glows, blobs, animations, or decorative imagery without a role.
- I do not make every card colorful; that destroys the ability to prioritize.
- I do not increase every type size.
- I do not replace a coherent palette with neon accents just to create intensity.
- I do not add shadows to every surface.
- I do not turn an operational interface into a marketing page if the task is scanning and action.

---

# 2. “Feels bland”

## What I diagnose first

In order:

1. **Does the interface have a recognisable stance?**
2. **Does the visual system feel specific to the product or generic to software?**
3. **Are the typography, color, spacing, and component shapes all neutral in the same way?**
4. **Is there any visual rhythm or pacing across the page?**
5. **Is the content itself too generic or placeholder-like?**
6. **Does the page lack a distinctive material, editorial, cultural, or operational point of view?**

“Bland” is usually not solved with more decoration. It often means there is no committed decision in the system.

## System levers I consider, in order

1. **Stance**
    
    - Clarify whether the product should feel editorial, technical, civic, tactile, playful, archival, industrial, or premium.
    - Remove decisions that belong to a different stance.
2. **Typography**
    
    - Strengthen the type pairing.
    - Give display type a real role.
    - Improve the use of labels, captions, numerals, and metadata.
    - Replace generic font defaults if they are not serving the product.
3. **Ground and surface**
    
    - Revisit page temperature: warm paper, cool technical, dark workspace, mineral surface, split canvas.
    - Reduce generic gray-card repetition.
4. **Composition**
    
    - Establish stronger proportion and pacing.
    - Make some sections expansive and others compact.
    - Use whitespace more deliberately.
5. **Content specificity**
    
    - Replace generic labels and filler with product-specific language, metrics, images, charts, or data.
6. **Selective signature detail**
    
    - A distinctive data treatment, image crop, border rhythm, icon treatment, or material accent.

## What I change

- The typography pairing and hierarchy.
- The surface temperature.
- The layout rhythm.
- The content realism.
- One or two repeatable signature details.
- Generic component shapes if they are contradicting the stance.

## What I refuse to change

- I do not add random visual clutter to compensate for weak art direction.
- I do not use five fonts, several gradients, or multiple illustration styles.
- I do not introduce decoration that cannot repeat coherently across the product.
- I do not sacrifice clarity for “personality.”
- I do not abandon an existing design system unless the feedback is explicitly about redesigning that system.

---

# 3. “More premium”

## What I diagnose first

In order:

1. **Does “premium” mean more exclusive, more crafted, more calm, more expensive, or more trustworthy?**
2. **Is the current design visually noisy, crowded, or overly promotional?**
3. **Are typography, imagery, spacing, and surfaces sufficiently controlled?**
4. **Are there too many colors, badges, shadows, rounded shapes, or competing calls to action?**
5. **Is the content quality undermining the desired perception?**
6. **Does the target audience actually benefit from premium restraint, or do they need operational directness?**

“Premium” rarely means “add gold, blur, glass, and a serif font.” It usually means **better judgment, more restraint, better materials, better proportion, and clearer hierarchy**.

## System levers I consider, in order

1. **Reduction**
    
    - Remove redundant controls.
    - Reduce visual states competing for attention.
    - Simplify card structures.
    - Limit accents.
2. **Typography**
    
    - Improve display/body contrast.
    - Increase whitespace around important type.
    - Use fewer weights.
    - Refine letter spacing and line-height.
3. **Surface and material**
    
    - Use better neutral temperature.
    - Reduce shadows.
    - Introduce quiet texture, image treatment, or glass only if it matches the product.
    - Use finer borders and controlled elevation.
4. **Image direction**
    
    - Improve crop, tonal treatment, framing, and art direction.
    - Use fewer, better images.
5. **Interaction**
    
    - Make hover, focus, and selected states smoother and quieter.
    - Remove exaggerated motion.
6. **Content**
    
    - Replace generic sales language with concrete proof, provenance, detail, or expertise.

## What I change

- Spacing and layout proportions.
- Type hierarchy and font usage.
- Border/shadow system.
- Image selection and crop.
- Surface temperature.
- CTA count and prominence.
- Content density and specificity.

## What I refuse to change

- I do not use gold as shorthand for luxury.
- I do not add gradients merely to signal expense.
- I do not make all corners pill-shaped.
- I do not hide usable information to make a dashboard appear sparse.
- I do not use overly delicate low-contrast type that harms accessibility.
- I do not use “premium” styling to mask weak product content or a confusing flow.

---

# 4. “Too corporate”

## What I diagnose first

In order:

1. **Which parts feel corporate: type, copy, layout, color, density, imagery, language, or interaction?**
2. **Is the product actually institutional or high-trust, and does “less corporate” mean less generic rather than less reliable?**
3. **Are generic enterprise patterns dominating: blue CTA, gray dashboard shell, dense navigation, badge overload, equal cards, jargon-heavy copy?**
4. **Does the current design lack warmth, specificity, cultural context, or human language?**
5. **Is the user asking for more editorial, more playful, more tactile, or more direct?**

## System levers I consider, in order

1. **Content voice**
    
    - Replace abstract business language with direct, product-specific language.
    - Reduce jargon.
    - Use human-readable labels and actions.
2. **Typography**
    
    - Move away from default enterprise type if appropriate.
    - Introduce a more characteristic display role or a warmer UI face.
    - Reduce excessive uppercase label density.
3. **Composition**
    
    - Break rigid equal-grid structures.
    - Use more narrative rhythm or content-led hierarchy.
    - Reduce over-boxing.
4. **Color and material**
    
    - Move from anonymous blue-gray to a context-specific palette.
    - Add warmth or editorial texture only when it fits.
    - Use accent colors with semantic restraint.
5. **Imagery and context**
    
    - Add real people, projects, places, products, or work—not generic office-stock photography.
6. **Interaction language**
    
    - Make controls direct and understandable.
    - Replace “Manage workspace configuration” with “Edit project settings,” if that is what it does.

## What I change

- Default blue/gray color behavior.
- Generic language and labels.
- Repeated card grids.
- Overly formal type and all-caps structures.
- Anonymous iconography and stock visuals.
- Generic enterprise navigation density where the product does not need it.

## What I refuse to change

- I do not remove clarity, accessibility, or predictable navigation simply to feel less corporate.
- I do not turn a serious medical, financial, legal, or operational product into a whimsical brand campaign.
- I do not replace useful tables with decorative cards.
- I do not add personality in every component; it should have a controlled role.
- I do not remove status semantics, auditing context, or error clarity from high-stakes products.

---

# 5. “I don’t like it”

## What I diagnose first

This is the broadest feedback. I first need to locate the objection.

I identify whether the dislike is primarily about:

1. **Visual taste**
    
    - “The colors, fonts, shapes, or imagery feel wrong.”
2. **Product fit**
    
    - “This does not feel like our audience, category, or brand.”
3. **Hierarchy**
    
    - “I do not know what matters or where to look.”
4. **Usability**
    
    - “This is too dense, too empty, confusing, or hard to act on.”
5. **Reference mismatch**
    
    - “I had an unspoken reference in mind and this is far from it.”
6. **Scope mismatch**
    
    - “You designed a marketing experience, but I needed an operational tool,” or the reverse.

## System levers I consider, in order

1. **Request concrete comparison points**
    
    - Identify one thing that feels wrong and one thing that feels right.
    - Ask whether the issue is visual direction, density, navigation, content, or functionality.
    - Ask for a reference only if it will materially improve the next attempt.
2. **Re-state the chosen stance**
    
    - Verify whether the current design direction is incorrect.
    - If it is, change the stance before polishing components.
3. **Audit the largest visual decisions**
    
    - Ground color.
    - Type pairing.
    - Layout composition.
    - Primary hierarchy.
    - Image/material strategy.
4. **Change the system, not isolated symptoms**
    
    - If the core issue is “too corporate,” changing one button radius will not fix it.
    - If the issue is hierarchy, changing the font alone will not fix it.
5. **Protect what is objectively working**
    
    - Preserve accessibility, real interaction, semantic structure, responsive behavior, and useful information architecture unless those are part of the problem.

## What I change

- The main stance if it is wrong.
- The type system if it is creating the wrong register.
- The ground and color temperature if the product feels emotionally wrong.
- The composition if the eye path is wrong.
- The data density or page structure if the user task is obscured.

## What I refuse to change

- I do not make random cosmetic changes just to create activity.
- I do not destroy a working information architecture because the color palette needs revision.
- I do not remove accessibility or responsive behavior to match a static reference.
- I do not keep polishing a stance that the user fundamentally dislikes.
- I do not claim to understand vague dislike without identifying which design dimension is failing.

---

# Worked example: “Make it pop”

## Scenario

A facilities dashboard has a section for delivery risks. The user says:

> “Make this pop.”

The section is meant to help an operations manager identify the one deadline requiring attention today.

## Before: technically clean, but visually flat

The issue is not that the section lacks color. The issue is that the critical risk, supporting metrics, and general totals all receive the same card treatment.

```tsx
// Before.tsx
export function DeliveryRiskBefore() {
  return (
    <section className="rounded-xl bg-slate-100 p-6">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-500">Delivery overview</p>
          <h2 className="text-xl font-semibold text-slate-900">This week</h2>
        </div>
        <button className="rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white">
          View schedule
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <article className="rounded-lg bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Due today</p>
          <p className="mt-2 text-3xl font-semibold text-slate-900">4</p>
          <p className="mt-2 text-sm text-slate-500">Items need attention.</p>
        </article>

        <article className="rounded-lg bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">At risk</p>
          <p className="mt-2 text-3xl font-semibold text-slate-900">1</p>
          <p className="mt-2 text-sm text-slate-500">North Terminal report.</p>
        </article>

        <article className="rounded-lg bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">On schedule</p>
          <p className="mt-2 text-3xl font-semibold text-slate-900">12</p>
          <p className="mt-2 text-sm text-slate-500">All other deliveries.</p>
        </article>
      </div>
    </section>
  );
}
```

## Diagnosis

The user’s “make it pop” translates to:

```text
The deadline at risk is the actual decision point.
The section makes all three values equal.
The generic blue CTA has no relationship to the risk content.
The background, cards, typography, and shadows are generic SaaS defaults.
There is no visual path from “overview” to “exception” to “action.”
```

## Changes I will make

1. Make the at-risk delivery the **primary visual object**.
2. Use an asymmetric layout: one large actionable risk plus two quiet supporting metrics.
3. Use an oxide accent only for the at-risk item and its action.
4. Make the deadline physically specific: project, time remaining, owner, dependency.
5. Use borders and surface temperature instead of stacked shadow cards.
6. Keep the section operational. No gradient, glass, glow, decorative blob, or animation is required.

## Changes I will not make

- I will not color every metric card.
- I will not make all numbers larger.
- I will not add a dashboard-wide gradient.
- I will not add a floating illustration or irrelevant alert icon.
- I will not make the CTA oversized; it is supporting an already-clear exception.
- I will not remove the supporting delivery totals, because they provide useful context.

## After: hierarchy and specificity create the “pop”

```tsx
import { AlertTriangle, ArrowUpRight, Clock3, PackageCheck } from "lucide-react";

export function DeliveryRiskAfter() {
  return (
    <section
      aria-labelledby="delivery-risk-heading"
      className="border-y border-[#C7D0D2] bg-[#F4F6F7] py-6"
    >
      <div className="flex flex-col gap-4 px-1 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-[11px] font-bold uppercase tracking-[0.08em] text-[#607076]">
            Delivery control
          </p>
          <h2
            id="delivery-risk-heading"
            className="mt-1 font-['Archivo'] text-[28px] font-semibold leading-[1.18] tracking-[-0.014em] text-[#162024]"
          >
            Today’s delivery picture
          </h2>
        </div>

        <button
          type="button"
          className="inline-flex w-fit items-center gap-2 text-[13px] font-bold text-[#123B45] underline decoration-[#8FA0A4] underline-offset-4 transition-[color,text-decoration-color] duration-[120ms] [transition-timing-function:cubic-bezier(0.2,0,0,1)] hover:text-[#D46B2C] hover:decoration-[#D46B2C] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D46B2C] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F4F6F7]"
        >
          Open full schedule
          <ArrowUpRight size={15} strokeWidth={2} aria-hidden="true" />
        </button>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-[minmax(0,1.65fr)_minmax(260px,0.75fr)]">
        {/* Primary exception */}
        <article className="relative overflow-hidden rounded-[6px] border border-[#D9A888] bg-[#FFF9F5] p-5 sm:p-6">
          <div className="absolute inset-y-0 left-0 w-1 bg-[#D46B2C]" />

          <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
            <div className="pl-2">
              <div className="flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center gap-1.5 rounded-[2px] bg-[#F9E6D9] px-2 py-1 font-['Geist_Mono'] text-[10px] font-semibold uppercase tracking-[0.04em] text-[#8C3C17]">
                  <AlertTriangle size={12} strokeWidth={2.2} aria-hidden="true" />
                  At risk
                </span>
                <span className="font-['Geist_Mono'] text-[11px] font-medium tracking-[-0.01em] text-[#6F5B50]">
                  DEL-0184
                </span>
              </div>

              <h3 className="mt-4 font-['Archivo'] text-[24px] font-semibold leading-[1.16] tracking-[-0.014em] text-[#162024]">
                North Terminal inspection report
              </h3>

              <p className="mt-2 max-w-2xl text-[14px] leading-[1.55] text-[#5E5149]">
                Final client review is still pending. The delivery package must be released
                before the 16:00 dispatch window.
              </p>
            </div>

            <div className="shrink-0 border-l border-[#E6BDA4] pl-4 sm:min-w-32">
              <p className="text-[11px] font-bold uppercase tracking-[0.08em] text-[#8C5C44]">
                Time left
              </p>
              <p className="mt-1 font-['Archivo'] text-[30px] font-semibold leading-none tracking-[-0.03em] text-[#8C3C17]">
                02:18
              </p>
              <p className="mt-1 font-['Geist_Mono'] text-[11px] tracking-[-0.01em] text-[#6F5B50]">
                hours
              </p>
            </div>
          </div>

          <div className="mt-6 flex flex-col gap-4 border-t border-[#EBCDBD] pt-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-[12px] text-[#5E5149]">
              <span className="inline-flex items-center gap-1.5">
                <Clock3 size={14} strokeWidth={1.8} aria-hidden="true" />
                Client review pending
              </span>
              <span className="font-['Geist_Mono'] tracking-[-0.01em]">
                Owner · M. Ibarra
              </span>
            </div>

            <button
              type="button"
              className="inline-flex h-10 items-center justify-center rounded-[4px] border border-[#123B45] bg-[#123B45] px-4 text-[13px] font-bold text-[#F7FAFA] transition-[background-color,border-color,box-shadow,transform] duration-[120ms] [transition-timing-function:cubic-bezier(0.2,0,0,1)] hover:bg-[#0C3038] hover:border-[#0C3038] active:translate-y-px focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D46B2C] focus-visible:ring-offset-2 focus-visible:ring-offset-[#FFF9F5]"
            >
              Resolve delivery
            </button>
          </div>
        </article>

        {/* Supporting context */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
          <article className="rounded-[6px] border border-[#C7D0D2] bg-white p-5">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-[11px] font-bold uppercase tracking-[0.08em] text-[#607076]">
                  Due today
                </p>
                <p className="mt-3 font-['Archivo'] text-[34px] font-semibold leading-none tracking-[-0.03em] text-[#162024]">
                  04
                </p>
              </div>
              <span className="rounded-[2px] bg-[#EDF1F1] p-2 text-[#123B45]">
                <Clock3 size={17} strokeWidth={1.8} aria-hidden="true" />
              </span>
            </div>
            <p className="mt-4 text-[13px] leading-[1.5] text-[#607076]">
              Three packages are ready; one needs review.
            </p>
          </article>

          <article className="rounded-[6px] border border-[#C7D0D2] bg-white p-5">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-[11px] font-bold uppercase tracking-[0.08em] text-[#607076]">
                  On schedule
                </p>
                <p className="mt-3 font-['Archivo'] text-[34px] font-semibold leading-none tracking-[-0.03em] text-[#162024]">
                  12
                </p>
              </div>
              <span className="rounded-[2px] bg-[#E4F0EB] p-2 text-[#2C725E]">
                <PackageCheck size={17} strokeWidth={1.8} aria-hidden="true" />
              </span>
            </div>
            <p className="mt-4 text-[13px] leading-[1.5] text-[#607076]">
              No further deadline conflicts detected.
            </p>
          </article>
        </div>
      </div>
    </section>
  );
}
```

## Why the revised version “pops”

It does not pop because it is louder everywhere. It pops because:

- The **actual exception** is now dominant.
- The main panel is **larger and asymmetrical**.
- The oxide accent appears only where urgency matters.
- The primary panel includes a concrete action.
- Supporting metrics are quieter and contextually useful.
- The page feels more specific to operations work because it uses job IDs, time remaining, owner, dispatch timing, and review state.
- The interaction and visual weight are concentrated where a user needs to make a decision.

That is the default translation I aim for: turn vague feedback into a targeted system adjustment while protecting the interface’s overall coherence.

## P10 — App-scale coherence & states

I’m using the `react-router` guidance because this question is specifically about maintaining coherence across multiple routes and app states.

A multi-screen app stays coherent when the system is split into two layers:

```text
Global decisions: immutable or highly reusable rules
Route decisions: information hierarchy, content, task flow, and composition
```

The mistake that causes screen-four drift is allowing every route to solve both layers again from scratch.

---

# 1. What carries the system across routes

## What belongs in global/theme files

These are the rules that should be stable across almost every route.

|Global layer|What belongs there|
|---|---|
|`src/styles/fonts.css`|Font imports and font-family availability|
|`src/styles/theme.css`|Semantic color tokens, dark tokens, radius, focus-ring values, core surface relationships|
|`src/styles/index.css`|Existing Tailwind/theme mapping, base typography defaults, reduced-motion fallback, scrollbar policy, shared utility/keyframe rules|
|Root app shell|Persistent navigation, page frame, background, global spacing, route outlet, notifications, dialogs, keyboard-focus behavior|
|Shared components|Buttons, input patterns, tabs, cards, status badges, empty/error/loading patterns, tables, page headers|
|Route configuration|Stable path model, nesting, route-level loading/error boundaries, URL-backed filters or selected views|
|Shared data rules|Date formats, currency formats, status labels, chart color mapping, permission behavior|

For a multi-route React app, I would use the React Router data-router pattern, with `RouterProvider` at the application entry point and route configuration separated from individual route components.

```tsx
// src/app/App.tsx
import { RouterProvider } from "react-router";
import { router } from "./routes";

export default function App() {
  return <RouterProvider router={router} />;
}
```

```tsx
// src/app/routes.ts
import { createBrowserRouter } from "react-router";
import { AppShell } from "./AppShell";
import { OverviewRoute } from "./routes/OverviewRoute";
import { ProjectsRoute } from "./routes/ProjectsRoute";
import { BudgetRoute } from "./routes/BudgetRoute";
import { DeliveriesRoute } from "./routes/DeliveriesRoute";
import { SettingsRoute } from "./routes/SettingsRoute";
import { NotFoundRoute } from "./routes/NotFoundRoute";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: AppShell,
    children: [
      { index: true, Component: OverviewRoute },
      { path: "projects", Component: ProjectsRoute },
      { path: "budget", Component: BudgetRoute },
      { path: "deliveries", Component: DeliveriesRoute },
      { path: "settings", Component: SettingsRoute },
      { path: "*", Component: NotFoundRoute },
    ],
  },
]);
```

## What goes in `theme.css`

The theme file contains values that should not vary merely because the user navigated from `/projects` to `/budget`.

```css
:root {
  /* Foundation */
  --background: #F4F6F7;
  --foreground: #162024;

  --card: #FFFFFF;
  --card-foreground: #162024;

  --primary: #123B45;
  --primary-foreground: #F7FAFA;

  --secondary: #E3E9EA;
  --secondary-foreground: #243237;

  --muted: #EDF1F1;
  --muted-foreground: #607076;

  --accent: #D46B2C;
  --accent-foreground: #241006;

  --border: #C7D0D2;
  --ring: #D46B2C;

  /* Shared geometry */
  --radius: 6px;
  --radius-control: 4px;
  --radius-panel: 6px;

  /* Shared elevation */
  --shadow-float:
    0 1px 2px rgb(22 32 36 / 8%),
    0 8px 20px rgb(22 32 36 / 10%);

  --shadow-overlay:
    0 2px 4px rgb(22 32 36 / 8%),
    0 18px 42px rgb(22 32 36 / 16%);

  /* Shared motion */
  --motion-fast: 120ms;
  --motion-standard: 180ms;
  --ease-standard: cubic-bezier(0.2, 0, 0, 1);
}

.dark {
  --background: #1E2527;
  --foreground: #E9EEEE;

  --card: #252D2F;
  --card-foreground: #E9EEEE;

  --primary: #9FD1C1;
  --primary-foreground: #11201C;

  --secondary: #303A3C;
  --secondary-foreground: #D7DFE0;

  --muted: #303A3C;
  --muted-foreground: #AAB8BB;

  --accent: #F0A273;
  --accent-foreground: #29150A;

  --border: rgb(233 238 238 / 16%);
  --ring: #F0A273;
}
```

## What belongs in the app shell

The shell gives every route the same spatial and navigational identity.

```tsx
// src/app/AppShell.tsx
import { NavLink, Outlet } from "react-router";

const navItems = [
  { to: "/", label: "Overview", end: true },
  { to: "/projects", label: "Projects" },
  { to: "/budget", label: "Budget" },
  { to: "/deliveries", label: "Deliveries" },
  { to: "/settings", label: "Settings" },
];

export function AppShell() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b border-border bg-background">
        <div className="mx-auto flex min-h-16 max-w-[1440px] items-center justify-between px-5 lg:px-8">
          <NavLink
            to="/"
            className="font-['Archivo'] text-[18px] font-semibold tracking-[-0.015em] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-4"
          >
            FRAME / Studio
          </NavLink>

          <nav aria-label="Primary">
            <ul className="flex items-center gap-1">
              {navItems.map((item) => (
                <li key={item.to}>
                  <NavLink
                    to={item.to}
                    end={item.end}
                    className={({ isActive }) =>
                      [
                        "rounded-[4px] px-3 py-2 text-[13px] font-bold transition-colors duration-[120ms] [transition-timing-function:var(--ease-standard)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
                        isActive
                          ? "bg-secondary text-foreground"
                          : "text-muted-foreground hover:bg-muted hover:text-foreground",
                      ].join(" ")
                    }
                  >
                    {item.label}
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-[1440px] px-5 py-7 lg:px-8 lg:py-9">
        <Outlet />
      </main>
    </div>
  );
}
```

The shell owns:

- overall page background,
- maximum width,
- side padding,
- global header,
- active-route treatment,
- persistent navigation,
- keyboard focus behavior,
- global overlays and toasts.

A route should not quietly introduce a second unrelated page background, a new navigation style, or its own competing max-width.

---

## What belongs to individual routes

Routes are allowed to decide:

- page title and route-specific subtitle,
- task hierarchy,
- information density,
- whether the page is list-led, detail-led, dashboard-led, form-led, or editorial,
- relevant page-level actions,
- route-specific filters,
- charts and data views,
- appropriate empty, loading, error, and permission states,
- local composition.

Routes should **not** independently decide:

- new button shapes,
- new focus-ring colors,
- a different card radius,
- a new gray background,
- a different primary color,
- a different table typography system,
- an unrelated shadow model,
- a new status-language palette,
- a new motion system.

A route can be visually distinct in composition without becoming a different product.

---

# 2. Unglamorous states: concrete patterns

The operational states are where a product’s system is tested. A coherent happy path with inconsistent empty, loading, error, or permission states is not a coherent app.

Below, all examples use the same precision-industrial system.

---

## A. Empty state

An empty state should answer:

1. What is absent?
2. Why might it be absent?
3. What can the user do next?
4. Is this a normal blank state, a filtered state, or a failure to load?

```tsx
import { ClipboardPlus, SlidersHorizontal } from "lucide-react";

type EmptyProjectsProps = {
  hasFilters?: boolean;
  onCreateProject: () => void;
  onClearFilters: () => void;
};

export function EmptyProjects({
  hasFilters = false,
  onCreateProject,
  onClearFilters,
}: EmptyProjectsProps) {
  return (
    <section
      aria-labelledby="empty-projects-title"
      className="border border-border bg-card px-6 py-12 text-center sm:px-10"
    >
      <div className="mx-auto max-w-md">
        <div className="mx-auto flex size-11 items-center justify-center rounded-[6px] bg-secondary text-primary">
          {hasFilters ? (
            <SlidersHorizontal size={20} strokeWidth={1.8} aria-hidden="true" />
          ) : (
            <ClipboardPlus size={20} strokeWidth={1.8} aria-hidden="true" />
          )}
        </div>

        <p className="mt-5 text-[11px] font-bold uppercase tracking-[0.08em] text-muted-foreground">
          {hasFilters ? "Filtered results" : "Project register"}
        </p>

        <h2
          id="empty-projects-title"
          className="mt-2 font-['Archivo'] text-[24px] font-semibold leading-[1.2] tracking-[-0.012em]"
        >
          {hasFilters ? "No projects match this view" : "No projects have been created yet"}
        </h2>

        <p className="mt-3 text-[14px] leading-[1.55] text-muted-foreground">
          {hasFilters
            ? "Try widening the delivery window, clearing a status filter, or switching to all projects."
            : "Create the first project to track shoots, budgets, crew assignments, and delivery milestones."}
        </p>

        <div className="mt-6 flex flex-wrap justify-center gap-3">
          {hasFilters ? (
            <button
              type="button"
              onClick={onClearFilters}
              className="inline-flex h-10 items-center justify-center rounded-[4px] border border-border bg-card px-4 text-[13px] font-bold text-foreground transition-colors duration-[120ms] hover:bg-secondary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-card"
            >
              Clear filters
            </button>
          ) : (
            <button
              type="button"
              onClick={onCreateProject}
              className="inline-flex h-10 items-center justify-center rounded-[4px] border border-primary bg-primary px-4 text-[13px] font-bold text-primary-foreground transition-colors duration-[120ms] hover:brightness-95 active:translate-y-px focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-card"
            >
              Create project
            </button>
          )}
        </div>
      </div>
    </section>
  );
}
```

### Empty-state rules

- Do not use a large decorative illustration unless the product is consumer-facing or image-led.
- Do not imply an error when there is simply no content.
- Distinguish “no data yet” from “no results match filters.”
- Keep the state in the normal page container rather than inventing a separate visual language.
- Give the user one clear next action, not five possible CTA buttons.

---

## B. Loading / skeleton state

A skeleton should preserve the final layout’s dimensions and information hierarchy.

```tsx
function SkeletonLine({ className }: { className: string }) {
  return <div aria-hidden="true" className={`skeleton ${className}`} />;
}

export function ProjectsTableSkeleton() {
  return (
    <section aria-busy="true" aria-label="Loading projects" className="overflow-hidden border border-border bg-card">
      <div className="flex items-center justify-between border-b border-border px-5 py-4">
        <div>
          <SkeletonLine className="h-3 w-24" />
          <SkeletonLine className="mt-3 h-7 w-48" />
        </div>
        <SkeletonLine className="h-10 w-32" />
      </div>

      <div className="overflow-x-auto">
        <div className="min-w-[760px]">
          <div className="grid grid-cols-[1.5fr_1fr_0.8fr_0.8fr_0.8fr] gap-4 border-b border-border bg-muted px-5 py-3">
            {Array.from({ length: 5 }).map((_, index) => (
              <SkeletonLine key={index} className="h-3 w-20" />
            ))}
          </div>

          {Array.from({ length: 5 }).map((_, rowIndex) => (
            <div
              key={rowIndex}
              className="grid grid-cols-[1.5fr_1fr_0.8fr_0.8fr_0.8fr] gap-4 border-b border-border px-5 py-4 last:border-b-0"
            >
              <SkeletonLine className="h-4 w-4/5" />
              <SkeletonLine className="h-4 w-2/3" />
              <SkeletonLine className="h-5 w-20" />
              <SkeletonLine className="h-4 w-16" />
              <SkeletonLine className="h-4 w-24" />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
```

```css
.skeleton {
  position: relative;
  overflow: hidden;
  border-radius: 2px;
  background: #E3E9EA;
}

.skeleton::after {
  content: "";
  position: absolute;
  inset: 0;
  transform: translateX(-100%);
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgb(255 255 255 / 48%) 48%,
    transparent 100%
  );
  animation: skeleton-shimmer 1400ms cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

@keyframes skeleton-shimmer {
  to {
    transform: translateX(100%);
  }
}

@media (prefers-reduced-motion: reduce) {
  .skeleton::after {
    animation: none;
  }
}
```

### Loading-state rules

- Keep the skeleton shape close to the final content shape.
- Do not use spinners in the center of a data table when the table structure is predictable.
- Avoid a skeleton for loads shorter than roughly `300–500ms`; it can flash unnecessarily.
- Avoid high-contrast shimmer or multiple animations at different speeds.
- Use `aria-busy="true"` and an accessible label.

---

## C. Error state

Errors should preserve context, explain impact, and give a recovery action.

```tsx
import { AlertTriangle, RotateCw } from "lucide-react";

type SectionErrorProps = {
  title?: string;
  message: string;
  onRetry: () => void;
};

export function SectionError({
  title = "This section could not load",
  message,
  onRetry,
}: SectionErrorProps) {
  return (
    <section
      role="alert"
      aria-labelledby="section-error-title"
      className="border border-[#D6A5A5] bg-[#FFF8F8] p-5"
    >
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex gap-3">
          <span className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-[4px] bg-[#FBE4E4] text-[#B63B3B]">
            <AlertTriangle size={17} strokeWidth={2} aria-hidden="true" />
          </span>

          <div>
            <p className="text-[11px] font-bold uppercase tracking-[0.08em] text-[#8E4444]">
              Data unavailable
            </p>
            <h2
              id="section-error-title"
              className="mt-1 font-['Archivo'] text-[20px] font-semibold leading-[1.25] tracking-[-0.008em] text-[#6F2525]"
            >
              {title}
            </h2>
            <p className="mt-2 max-w-2xl text-[14px] leading-[1.55] text-[#7C4A4A]">
              {message}
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={onRetry}
          className="inline-flex h-10 shrink-0 items-center justify-center gap-2 rounded-[4px] border border-[#9F4545] bg-white px-4 text-[13px] font-bold text-[#812F2F] transition-colors duration-[120ms] hover:bg-[#FBE4E4] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-[#FFF8F8]"
        >
          <RotateCw size={15} strokeWidth={1.9} aria-hidden="true" />
          Try again
        </button>
      </div>
    </section>
  );
}
```

### Error-state rules

- Keep the failed section’s position; do not replace the entire page if only one chart or table failed.
- Give the user a retry action if retry is possible.
- Do not expose technical stack traces in ordinary product UI.
- Do not use error red as a full-page background.
- For destructive or blocking errors, use `role="alert"`; for passive errors, use a less interruptive status pattern.

---

## D. Zero-data chart

A zero-data chart is not an error, and it should not render a misleading flat line that implies a measured value of zero.

```tsx
import { BarChart3, Plus } from "lucide-react";

type ZeroDataChartProps = {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
};

export function ZeroDataChart({
  title,
  description,
  actionLabel,
  onAction,
}: ZeroDataChartProps) {
  return (
    <section className="border border-border bg-card">
      <div className="border-b border-border px-5 py-4">
        <p className="text-[11px] font-bold uppercase tracking-[0.08em] text-muted-foreground">
          Budget intelligence
        </p>
        <h2 className="mt-1 font-['Archivo'] text-[20px] font-semibold leading-[1.25] tracking-[-0.008em]">
          {title}
        </h2>
      </div>

      <div className="relative flex min-h-72 items-center justify-center overflow-hidden px-5 py-10">
        <div
          aria-hidden="true"
          className="absolute inset-x-5 bottom-8 top-8 bg-[linear-gradient(to_right,rgb(22_32_36_/_6%)_1px,transparent_1px),linear-gradient(to_bottom,rgb(22_32_36_/_6%)_1px,transparent_1px)] bg-[size:56px_40px]"
        />

        <div className="relative z-10 max-w-sm text-center">
          <div className="mx-auto flex size-11 items-center justify-center rounded-[6px] bg-secondary text-primary">
            <BarChart3 size={21} strokeWidth={1.8} aria-hidden="true" />
          </div>

          <h3 className="mt-4 font-['Archivo'] text-[20px] font-semibold tracking-[-0.008em]">
            No budget activity to chart yet
          </h3>

          <p className="mt-2 text-[14px] leading-[1.55] text-muted-foreground">
            {description}
          </p>

          {actionLabel && onAction ? (
            <button
              type="button"
              onClick={onAction}
              className="mt-5 inline-flex h-10 items-center justify-center gap-2 rounded-[4px] border border-primary bg-primary px-4 text-[13px] font-bold text-primary-foreground transition-colors duration-[120ms] hover:brightness-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-card"
            >
              <Plus size={15} strokeWidth={2} aria-hidden="true" />
              {actionLabel}
            </button>
          ) : null}
        </div>
      </div>
    </section>
  );
}
```

### Zero-data-chart rules

- Preserve the chart container and heading so the page does not jump when data later exists.
- Explain the condition: no invoices yet, no date range selected, no linked source, no reporting permission.
- Do not present a zero baseline as if it were observed data.
- Use a quiet graph grid only if it reinforces that this is a chart region, not as decorative texture.
- Offer an action only if the user can reasonably create or connect the missing data.

---

## E. Long-content overflow

Overflow needs a route-level strategy. Hiding content with arbitrary truncation is not a strategy.

### Responsive data-table container

```tsx
type CrewMember = {
  name: string;
  role: string;
  availability: string;
  contact: string;
  notes: string;
};

const crew: CrewMember[] = [
  {
    name: "Mina Okafor",
    role: "Director of Photography",
    availability: "Available · 18–29 Jul",
    contact: "mina.okafor@studio.example",
    notes: "Owns camera package and final lens list.",
  },
  {
    name: "Jules Pereira",
    role: "Production Designer",
    availability: "Hold · 22–24 Jul",
    contact: "jules.pereira@studio.example",
    notes: "Set materials pending approval from art director.",
  },
];

export function CrewTable() {
  return (
    <div className="overflow-x-auto border border-border bg-card">
      <table className="w-full min-w-[920px] border-collapse text-left">
        <caption className="sr-only">Assigned crew members</caption>

        <thead className="bg-muted">
          <tr className="border-b border-border">
            {["Crew member", "Role", "Availability", "Contact", "Notes"].map((heading) => (
              <th
                key={heading}
                scope="col"
                className="px-4 py-3 text-[11px] font-bold uppercase tracking-[0.08em] text-muted-foreground"
              >
                {heading}
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {crew.map((member) => (
            <tr
              key={member.contact}
              className="border-b border-border last:border-b-0 hover:bg-muted/60 focus-within:bg-muted"
            >
              <td className="px-4 py-4 text-[13px] font-bold text-foreground">{member.name}</td>
              <td className="px-4 py-4 text-[13px] text-muted-foreground">{member.role}</td>
              <td className="px-4 py-4 font-['Geist_Mono'] text-[12px] text-foreground">
                {member.availability}
              </td>
              <td className="max-w-56 truncate px-4 py-4 text-[13px] text-muted-foreground">
                <a
                  href={`mailto:${member.contact}`}
                  className="hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  {member.contact}
                </a>
              </td>
              <td className="max-w-80 px-4 py-4 text-[13px] leading-[1.5] text-muted-foreground">
                <p className="line-clamp-2">{member.notes}</p>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

### Long-content rules

- Preserve horizontal scrolling for genuinely tabular desktop data rather than forcing five columns into a narrow mobile stack.
- Use a visible responsive strategy: horizontal scroll, column prioritization, a detail drawer, or a mobile-specific list view.
- Use truncation only when the full content is available through a detail view, tooltip, dialog, expandable row, or accessible title.
- Do not truncate critical error messages, permissions information, legal copy, or primary task labels.
- For long prose, constrain reading measure rather than allowing extremely wide text:

```css
.long-form-copy {
  max-width: 68ch;
}
```

---

## F. Permission denied

A permission state should make three things clear:

1. What is unavailable.
2. Why it is unavailable, if the product can safely explain that.
3. What the user can do next.

```tsx
import { LockKeyhole, Mail } from "lucide-react";

type PermissionDeniedProps = {
  resourceName: string;
  canRequestAccess?: boolean;
  onRequestAccess?: () => void;
};

export function PermissionDenied({
  resourceName,
  canRequestAccess = true,
  onRequestAccess,
}: PermissionDeniedProps) {
  return (
    <section
      aria-labelledby="permission-title"
      className="border border-border bg-card px-6 py-12 text-center sm:px-10"
    >
      <div className="mx-auto max-w-md">
        <div className="mx-auto flex size-11 items-center justify-center rounded-[6px] bg-secondary text-primary">
          <LockKeyhole size={20} strokeWidth={1.8} aria-hidden="true" />
        </div>

        <p className="mt-5 text-[11px] font-bold uppercase tracking-[0.08em] text-muted-foreground">
          Restricted workspace
        </p>

        <h2
          id="permission-title"
          className="mt-2 font-['Archivo'] text-[24px] font-semibold leading-[1.2] tracking-[-0.012em]"
        >
          You do not have access to {resourceName}
        </h2>

        <p className="mt-3 text-[14px] leading-[1.55] text-muted-foreground">
          Your current role allows project coordination, but does not include budget
          reporting or invoice-level detail.
        </p>

        {canRequestAccess && onRequestAccess ? (
          <button
            type="button"
            onClick={onRequestAccess}
            className="mt-6 inline-flex h-10 items-center justify-center gap-2 rounded-[4px] border border-primary bg-primary px-4 text-[13px] font-bold text-primary-foreground transition-colors duration-[120ms] hover:brightness-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-card"
          >
            <Mail size={15} strokeWidth={1.9} aria-hidden="true" />
            Request access
          </button>
        ) : (
          <p className="mt-6 text-[13px] font-medium text-muted-foreground">
            Contact your workspace administrator to request access.
          </p>
        )}
      </div>
    </section>
  );
}
```

### Permission-state rules

- Do not make permission denial look like a broken page.
- Do not expose information the user is not authorized to see in the denied-state copy.
- Do not show a request-access button if the product cannot actually fulfill that request.
- Keep the global navigation visible unless the entire product is inaccessible.
- Preserve the route title or breadcrumb where useful so the user knows what they attempted to reach.

---

# 3. What usually drifts on screen 4+

The first few screens typically receive the most attention. By screen four or five, these failures often appear:

|Drift category|Typical failure|
|---|---|
|Typography|A new page uses a default sans for headings, different font weights, or too much uppercase|
|Surface system|One route introduces rounded shadow cards while earlier routes use flat ruled panels|
|Spacing|Page padding, section gaps, table density, or header spacing changes without reason|
|Color semantics|Orange means “selected” on one route and “warning” on another|
|Status treatment|Badges become pills, then dots, then colored text, with no shared logic|
|Primary action|One page uses a filled button; another uses a link; another uses a floating CTA for equal-priority actions|
|Table behavior|One route has compact rows, another oversized rows, another hides essential columns|
|Empty/loading/error states|Each route invents its own icon size, copy tone, background color, and CTA shape|
|Navigation|New local tabs, segmented controls, breadcrumbs, or sidebars appear without a hierarchy model|
|Dark mode|One page uses token colors; another hard-codes light hex values and breaks in dark mode|
|Responsive behavior|The first screens collapse intentionally; later screens simply overflow or become tiny|
|Motion|One route adds bouncy card lifts or slow fades unrelated to the established motion system|
|Content voice|Earlier routes say “Create project”; later routes say “Initiate project object”|

---

# 4. Drift-detection checklist

I review each new route against a fixed checklist before treating it as complete.

## Foundation

1. Does the route use `bg-background`, `text-foreground`, `bg-card`, `border-border`, and other semantic tokens rather than hard-coded one-off colors?
2. Does it work in both light and dark mode?
3. Does it use the shared radius values?
4. Does it use the shared border and shadow rules?
5. Has it introduced a new surface level that does not exist elsewhere?

## Typography

6. Does the route use the correct display, UI, and mono roles?
7. Is the page title at the established scale?
8. Are labels the established uppercase/sentence-case style?
9. Are captions and metadata visually quieter than primary text?
10. Is any new font being introduced without a system-level reason?

## Layout

11. Does the route use the same page max-width and shell padding?
12. Is its spacing rhythm consistent with adjacent routes?
13. Is the density appropriate to the task without becoming a new, unrelated density system?
14. Are cards used because grouping is needed, not because every section needs a container?
15. Does the route have a clear primary action and primary information object?

## Components and states

16. Do buttons use shared shape, type, focus, hover, active, and disabled behavior?
17. Are tabs, filters, inputs, tables, badges, and dialogs using established patterns?
18. Are statuses using the same semantic color meaning?
19. Do empty, loading, error, zero-data, and permission states follow shared structures?
20. Are all meaningful controls keyboard reachable and visibly focused?

## Responsiveness and interaction

21. Does the route have an intentional narrow-screen composition?
22. Do tables and dense views use the established overflow strategy?
23. Are long labels, names, dates, and values tested with realistic content?
24. Are route-specific filters represented in the URL when the state should be shareable?
25. Does motion match the product’s established duration and easing system?

## Product coherence

26. Does the route use the same voice and terminology as the rest of the app?
27. Does this screen feel like it belongs to the same product after the navigation is hidden?
28. Does it solve its task with the system, rather than inventing a new visual identity?
29. If the route is intentionally different, is the difference explained by task or content?
30. Can any route-specific styling be removed and replaced with an existing system primitive?

---

# 5. Worked drift-detection example

Consider a film-production studio application with these routes:

```text
/                 Overview
/projects         Project register
/budget           Budget tracking
/deliveries       Delivery control
/settings         Workspace settings
```

The first three routes use:

- warm technical paper background,
- dark studio-green primary,
- oxide accent for at-risk work,
- 6px panels,
- flat surfaces and hairline borders,
- Archivo for hierarchy,
- Manrope for UI,
- Geist Mono for dates, IDs, and money,
- compact 13–14px dense-data typography.

Then the `/deliveries` route is added.

## The drifting implementation

```tsx
// Problematic DeliveriesRoute.tsx
export function DeliveriesRoute() {
  return (
    <div className="min-h-screen bg-slate-50 p-10">
      <h1 className="text-4xl font-bold text-slate-900">Delivery Center</h1>

      <div className="mt-8 grid gap-6 md:grid-cols-3">
        <div className="rounded-2xl bg-white p-6 shadow-xl">
          <p className="text-xs font-semibold uppercase tracking-widest text-blue-500">
            Pending
          </p>
          <p className="mt-3 text-5xl font-bold text-slate-900">04</p>
        </div>

        <div className="rounded-2xl bg-white p-6 shadow-xl">
          <p className="text-xs font-semibold uppercase tracking-widest text-green-500">
            Delivered
          </p>
          <p className="mt-3 text-5xl font-bold text-slate-900">12</p>
        </div>

        <div className="rounded-2xl bg-white p-6 shadow-xl">
          <p className="text-xs font-semibold uppercase tracking-widest text-red-500">
            Delayed
          </p>
          <p className="mt-3 text-5xl font-bold text-slate-900">01</p>
        </div>
      </div>
    </div>
  );
}
```

## Checklist findings

|Check|Finding|
|---|---|
|Page ground|Fails: introduces `bg-slate-50` instead of the token-backed warm technical ground|
|Typography|Fails: generic Tailwind `text-4xl font-bold`; no Archivo hierarchy or mono data style|
|Radius|Fails: `rounded-2xl` contradicts the 6px system|
|Shadows|Fails: `shadow-xl` contradicts flat bordered panels|
|Color semantics|Fails: blue means pending; prior routes reserve orange for risk/exception emphasis|
|Composition|Fails: equal-card grid gives the delayed delivery equal importance to normal delivery totals|
|Data density|Fails: 5xl metrics are too large for operational scanning|
|Accessibility|Risk: green/red are the primary distinction between delivered and delayed|
|Cross-route recognition|Fails: it could belong to any generic SaaS app|

The problem is not that the screen is unattractive. The problem is that it behaves like a new product.

## Corrected route

```tsx
import { AlertTriangle, CheckCircle2, Clock3 } from "lucide-react";

const deliveryMetrics = [
  {
    label: "Due today",
    value: "04",
    detail: "Three packages ready for release",
    icon: Clock3,
    iconClass: "bg-secondary text-primary",
  },
  {
    label: "Delivered this week",
    value: "12",
    detail: "All receipts and masters confirmed",
    icon: CheckCircle2,
    iconClass: "bg-[#E4F0EB] text-[#2C725E]",
  },
];

export function DeliveriesRoute() {
  return (
    <section aria-labelledby="deliveries-heading">
      <header className="flex flex-col gap-4 border-b border-border pb-6 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-[11px] font-bold uppercase tracking-[0.08em] text-muted-foreground">
            Production control
          </p>
          <h1
            id="deliveries-heading"
            className="mt-1 font-['Archivo'] text-[32px] font-semibold leading-[1.12] tracking-[-0.022em]"
          >
            Deliveries
          </h1>
          <p className="mt-2 text-[14px] leading-[1.55] text-muted-foreground">
            Review time-sensitive packages, client approvals, and release readiness.
          </p>
        </div>

        <button
          type="button"
          className="inline-flex h-10 w-fit items-center justify-center rounded-[4px] border border-primary bg-primary px-4 text-[13px] font-bold text-primary-foreground transition-colors duration-[120ms] hover:brightness-95 active:translate-y-px focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
        >
          Export delivery log
        </button>
      </header>

      <div className="mt-6 grid gap-4 lg:grid-cols-[minmax(0,1.6fr)_minmax(260px,0.72fr)]">
        <article className="relative overflow-hidden border border-[#D9A888] bg-[#FFF9F5] p-6">
          <div className="absolute inset-y-0 left-0 w-1 bg-accent" />

          <div className="flex flex-col justify-between gap-6 sm:flex-row sm:items-start">
            <div className="pl-2">
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1.5 rounded-[2px] bg-[#F9E6D9] px-2 py-1 font-['Geist_Mono'] text-[10px] font-semibold uppercase tracking-[0.04em] text-[#8C3C17]">
                  <AlertTriangle size={12} strokeWidth={2.2} aria-hidden="true" />
                  Delayed
                </span>
                <span className="font-['Geist_Mono'] text-[11px] text-[#6F5B50]">
                  DEL-0184
                </span>
              </div>

              <h2 className="mt-4 font-['Archivo'] text-[24px] font-semibold leading-[1.16] tracking-[-0.014em]">
                North Terminal inspection report
              </h2>

              <p className="mt-2 max-w-xl text-[14px] leading-[1.55] text-[#5E5149]">
                Client review is outstanding. Release is required before the 16:00
                dispatch window.
              </p>
            </div>

            <div className="border-l border-[#E6BDA4] pl-4">
              <p className="text-[11px] font-bold uppercase tracking-[0.08em] text-[#8C5C44]">
                Time left
              </p>
              <p className="mt-1 font-['Archivo'] text-[30px] font-semibold leading-none tracking-[-0.03em] text-[#8C3C17]">
                02:18
              </p>
              <p className="mt-1 font-['Geist_Mono'] text-[11px] text-[#6F5B50]">
                hours
              </p>
            </div>
          </div>

          <div className="mt-6 flex items-center justify-between border-t border-[#EBCDBD] pt-4">
            <span className="font-['Geist_Mono'] text-[12px] text-[#6F5B50]">
              Owner · M. Ibarra
            </span>
            <button
              type="button"
              className="inline-flex h-10 items-center justify-center rounded-[4px] border border-primary bg-primary px-4 text-[13px] font-bold text-primary-foreground transition-colors duration-[120ms] hover:brightness-95 active:translate-y-px focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-[#FFF9F5]"
            >
              Resolve delivery
            </button>
          </div>
        </article>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
          {deliveryMetrics.map((metric) => {
            const Icon = metric.icon;

            return (
              <article key={metric.label} className="border border-border bg-card p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-[11px] font-bold uppercase tracking-[0.08em] text-muted-foreground">
                      {metric.label}
                    </p>
                    <p className="mt-3 font-['Archivo'] text-[34px] font-semibold leading-none tracking-[-0.03em]">
                      {metric.value}
                    </p>
                  </div>

                  <span className={`rounded-[2px] p-2 ${metric.iconClass}`}>
                    <Icon size={17} strokeWidth={1.8} aria-hidden="true" />
                  </span>
                </div>

                <p className="mt-4 text-[13px] leading-[1.5] text-muted-foreground">
                  {metric.detail}
                </p>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
```

## Why the corrected route stays coherent

It uses the system’s:

- semantic page ground through the app shell,
- established title scale,
- Archivo/Manrope/Geist Mono role assignment,
- 6px or 4px geometry,
- border-led panel model,
- oxide accent for at-risk work,
- existing primary button behavior,
- compact operational density,
- asymmetric “exception first, totals second” composition.

It is not visually identical to `/projects` or `/budget`; delivery control has a different task. But it still reads as the same product before a user even notices the navigation.

## P11 — Imagery & generated graphics workflow

# 1. Image-search workflow

I do not search for “beautiful images.” I search for **visual evidence that belongs to the product, its audience, and the specific layout slot**.

The workflow is:

```text
Brief
  → identify the visual role
  → formulate several narrow queries
  → search broadly enough to compare
  → reject weak candidates quickly
  → select for crop, palette, composition, and narrative fit
  → treat image into the UI system
  → test at the actual slot size
```

I use an Unsplash search workflow when the product needs photography or reference imagery. If the project already contains brand photography, user-uploaded assets, or a Figma design with images, those take priority.

---

## 1.1 Define the image’s job before searching

Before writing a query, I classify the slot.

|Image role|What it must do|Search emphasis|
|---|---|---|
|Hero narrative image|Establish world, mood, product subject|Composition, negative space, atmosphere|
|Product evidence|Prove the product or service is real|Specificity, detail, authenticity|
|Contextual support|Make an abstract story concrete|Relevant people/place/process|
|Editorial section image|Create pacing between text blocks|Crop flexibility, tonal fit|
|Card thumbnail|Identify content quickly|Legible subject at small size|
|Background texture|Establish material without competing with content|Low-detail, tonal stability|
|Team/avatar image|Humanize ownership and collaboration|Consistent framing, genuine expression|
|Data/diagram substitute|Explain process or system|Usually SVG/diagram, not photo|

A photo is only useful when it has a clear job.

---

## 1.2 Query formulation

I normally begin with **three to six focused search queries**, not one vague noun phrase.

### Weak query

```text
film production
```

Likely result: generic clapperboards, cinema cameras, red-carpet imagery, staged actors, irrelevant movie-theater shots.

### Better query set for a film-production studio dashboard

```text
film editor dark studio workstation
film production crew candid location
cinematographer camera rig daylight
post production color grading monitor
film set equipment natural light
production notebook call sheet desk
```

Each query explores a different potential visual role:

|Query|Likely role|
|---|---|
|`film editor dark studio workstation`|Hero or workspace context|
|`film production crew candid location`|Team/process storytelling|
|`cinematographer camera rig daylight`|Product/process evidence|
|`post production color grading monitor`|Editorial visual for post-production|
|`film set equipment natural light`|Atmospheric background or section image|
|`production notebook call sheet desk`|Detail image for operational/craft tone|

### Query structure I use

```text
[subject] + [activity or environment] + [lighting / visual quality]
```

Examples:

```text
ceramicist hands studio warm daylight
architectural model workshop overhead
field technician industrial equipment overcast
student reading library window light
coastal restaurant kitchen candid
researcher microscope laboratory side light
```

The third clause matters. It prevents results that are technically relevant but tonally wrong.

---

## 1.3 Selection criteria

After results arrive, I select for these criteria in order.

### A. Subject authenticity

Does the image show the actual world of the product?

- A logistics product: real loading bays, routes, packages, equipment, people at work.
- A food product: ingredients, process, place, product detail.
- A film studio: sets, crew, post-production, equipment, production documents.
- A healthcare product: be careful—generic smiling clinicians may be less credible than a calm, specific environment or process.

### B. Compositional usability

Can the image survive the required crop?

I look for:

- clear subject placement,
- usable negative space,
- no critical face/object at likely crop edges,
- readable silhouette at small size,
- foreground/background depth,
- an image that can tolerate `object-fit: cover`.

### C. Tonal compatibility

Does it fit the UI’s material world?

For a warm editorial product, I prefer:

- natural light,
- warm but not orange-heavy images,
- visible material texture,
- controlled contrast,
- muted or earth-adjacent color.

For a cool technical product, I prefer:

- structured environment,
- cooler or neutral light,
- clean shapes,
- deliberate geometry,
- not necessarily “blue technology” imagery.

### D. Narrative specificity

Does it tell something that copy cannot?

A good image might show:

- a real production moment,
- craft in progress,
- a distinct environment,
- a process,
- a physical artifact,
- a person’s role.

A weak image is often merely “nice-looking.”

### E. Crop resilience

I test mentally or in implementation at the actual intended ratio:

```text
wide hero: 16:9, 3:2, 21:9
editorial image: 4:3, 3:4
product thumbnail: 1:1, 4:5
avatar: 1:1
background strip: 3:1 or wider
```

If the image only works at its original ratio, it is not a flexible UI asset.

---

## 1.4 What disqualifies an image

I reject an image when it has any of these problems.

1. **Generic stock symbolism**  
    Handshake, generic laptop, smiling office meeting, staged call-center headset, random city skyline.
    
2. **The wrong cultural or product context**  
    A generic cinema image for a production workflow product, a Silicon Valley office for a local cultural institution, a laboratory photo for a logistics product.
    
3. **No crop safety**  
    The only important subject sits at an edge or will be cut by the intended slot.
    
4. **Competing visual noise**  
    Busy background, too many faces, cluttered props, high-frequency detail behind text.
    
5. **Wrong color temperature**  
    A heavily cyan-and-magenta club image inside a calm paper-based editorial system, unless that contrast is intentional.
    
6. **Overly literal cliché**  
    A leaf for sustainability, a lightbulb for ideas, a lock for security, a coffee cup for coffee, unless it is genuinely a product image rather than symbolic filler.
    
7. **Overprocessed style**  
    Aggressive HDR, artificial blur, heavy color grading, or a trend look that will fight the UI.
    
8. **Weak subject readability at thumbnail scale**  
    A beautiful wide landscape may be useless as a 72px content thumbnail.
    
9. **Text embedded in the image**  
    Unless the image is a documented poster, cover, or artifact where the text itself is required.
    
10. **Mismatched production quality**  
    If one image looks like high-end editorial photography and another looks like casual phone photography, the difference must be intentional.
    

---

# 2. Crop, aspect, and composition rules by layout slot

## Hero: split-layout image

**Typical ratio:** `3:2`, `4:3`, or `16:10`  
**Use:** product context, craft, place, feature storytelling.

```tsx
<div className="relative aspect-[3/2] overflow-hidden bg-[#D9D2C7]">
  <img
    src="https://images.unsplash.com/photo-0000000000000?w=1400&h=940&fit=crop&auto=format"
    alt="Film editor reviewing footage in a color-grading suite"
    className="size-full object-cover object-[62%_center]"
  />
</div>
```

### Crop rule

- Put the key subject on the visual side opposite the primary text.
- Use `object-position` intentionally; do not accept browser-default center crop if it cuts the visual story.
- Maintain one calm region for text or surrounding whitespace.
- Do not overlay copy on the image unless the image was selected for text legibility.

---

## Hero: full-bleed background image

**Typical ratio:** `16:9`, `21:9`, or full viewport  
**Use:** immersive consumer, travel, culture, media, hospitality, visual product launch.

```tsx
<section className="relative min-h-[680px] overflow-hidden bg-[#1A2423]">
  <img
    src="https://images.unsplash.com/photo-0000000000000?w=1800&h=1012&fit=crop&auto=format"
    alt=""
    className="absolute inset-0 size-full object-cover object-center"
  />
  <div className="hero-scrim absolute inset-0" />

  <div className="relative mx-auto flex min-h-[680px] max-w-7xl items-end px-6 py-12 lg:px-10 lg:py-16">
    {/* Content */}
  </div>
</section>
```

### Crop rule

- Use only when the image has enough visual depth and negative space.
- Place the heading in an intentionally quieter area, not on the busiest part of the image.
- Keep the live text’s contrast valid over the **worst part** of the responsive crop, not only the desktop mockup.
- Avoid using full-bleed images for a dense operational dashboard.

---

## Editorial image beside copy

**Typical ratio:** `4:5`, `3:4`, or `4:3`  
**Use:** story pacing, case study, cultural content, hospitality, portfolio.

```tsx
<figure className="max-w-[580px]">
  <div className="aspect-[4/5] overflow-hidden bg-[#E5DDD1]">
    <img
      src="https://images.unsplash.com/photo-0000000000000?w=1000&h=1250&fit=crop&auto=format"
      alt="A producer marking a call sheet beside a camera cart"
      className="size-full object-cover object-center"
    />
  </div>
  <figcaption className="mt-3 font-['DM_Mono'] text-[11px] leading-[1.4] text-[#756D64]">
    Location scout, North Yorkshire · June 2026
  </figcaption>
</figure>
```

### Crop rule

- The image should have one clear vertical gesture or subject.
- Avoid an image that only works wide.
- Give the caption the same metadata system used elsewhere in the interface.
- Do not make every image the same ratio; variation is useful in editorial pacing when deliberate.

---

## Product or project card image

**Typical ratio:** `4:3`, `3:2`, or `1:1`  
**Use:** project identification, product gallery, destination card, story preview.

```tsx
<a
  href="#project"
  className="group block overflow-hidden border border-[#D4CABE] bg-[#FCF9F3]"
>
  <div className="aspect-[4/3] overflow-hidden bg-[#EAE2D7]">
    <img
      src="https://images.unsplash.com/photo-0000000000000?w=760&h=570&fit=crop&auto=format"
      alt="Lighting setup on a coastal film location"
      className="size-full object-cover transition-transform duration-[260ms] [transition-timing-function:cubic-bezier(0.22,1,0.36,1)] group-hover:scale-[1.025]"
    />
  </div>
  <div className="p-5">
    {/* Card copy */}
  </div>
</a>
```

### Crop rule

- The subject must remain legible at 200px wide.
- Do not crop a person’s head at an awkward line.
- Use a fixed aspect ratio across a repeated card set unless there is a strong editorial reason not to.
- Keep image hover zoom at `1.015–1.03`, never dramatic.

---

## Avatar or contributor portrait

**Typical ratio:** `1:1`  
**Use:** ownership, collaboration, identity, comments, crew/team context.

```tsx
<img
  src="https://images.unsplash.com/photo-0000000000000?w=160&h=160&fit=crop&auto=format"
  alt="Mina Okafor, director of photography"
  className="size-9 rounded-full object-cover object-[50%_35%] ring-1 ring-[#FFFFFF]"
/>
```

### Crop rule

- Eyes should be near the upper third, not centered vertically by default.
- Use a consistent portrait style across a team list.
- Do not mix tiny high-fashion portrait crops with casual distant group shots.

---

## Dashboard contextual banner

**Typical ratio:** `3:1`, `4:1`, or `16:5`  
**Use:** a single context-setting visual on a project detail page, not decorative wallpaper.

```tsx
<div className="relative aspect-[16/5] overflow-hidden bg-[#243130]">
  <img
    src="https://images.unsplash.com/photo-0000000000000?w=1600&h=500&fit=crop&auto=format"
    alt="Film crew preparing a night shoot on location"
    className="size-full object-cover object-[50%_45%]"
  />
  <div className="absolute inset-0 bg-[linear-gradient(90deg,rgb(20_30_31_/_60%)_0%,rgb(20_30_31_/_18%)_58%,rgb(20_30_31_/_0%)_100%)]" />
</div>
```

### Crop rule

- Use a banner only when it adds project identity or context.
- A project dashboard should not need a new banner on every route.
- Keep enough low-detail space for a possible overlaid project title.
- Do not hide critical project data inside image treatment.

---

# 3. Overlay and treatment recipes

The treatment should integrate the image into the palette and solve a specific issue: legibility, tonal fit, material consistency, or subject emphasis.

---

## 3.1 Dark text-protection scrim

Use when white or pale text sits over an image.

```css
.hero-scrim {
  background:
    linear-gradient(
      90deg,
      rgb(17 26 26 / 76%) 0%,
      rgb(17 26 26 / 54%) 34%,
      rgb(17 26 26 / 16%) 66%,
      rgb(17 26 26 / 0%) 100%
    ),
    linear-gradient(
      0deg,
      rgb(17 26 26 / 22%) 0%,
      rgb(17 26 26 / 0%) 46%
    );
}
```

### Use when

- The text is placed on the left of a full-bleed image.
- The image has uneven brightness.
- The stance supports a cinematic, immersive, or media-led hero.

### Do not use when

- The product is operational and the image is not necessary.
- The overlay becomes so dark that the image no longer has a role.
- The image was selected purely because a heavy overlay can hide its flaws.

---

## 3.2 Light editorial wash

Use to keep a photograph visible while bringing it into a warm paper system.

```css
.editorial-image {
  position: relative;
  overflow: hidden;
  background: #E9E0D4;
}

.editorial-image::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(
      135deg,
      rgb(245 240 232 / 22%) 0%,
      rgb(245 240 232 / 5%) 52%,
      rgb(169 70 45 / 10%) 100%
    );
  mix-blend-mode: multiply;
}

.editorial-image img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(0.88) contrast(0.96) sepia(0.04);
}
```

### Exact effect

- Saturation reduced to `88%`
- Contrast reduced to `96%`
- Very light sepia shift: `0.04`
- Warm multiply wash with `22% → 5% → 10%` opacity

This is enough to make mismatched photography sit beside warm neutral UI without turning every image brown.

---

## 3.3 Cool technical tone matching

Use for technical products where photography needs to sit in a cool, controlled environment.

```css
.technical-image {
  position: relative;
  overflow: hidden;
  background: #D8E0E1;
}

.technical-image::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(
      135deg,
      rgb(18 59 69 / 18%) 0%,
      rgb(39 107 138 / 10%) 55%,
      rgb(244 246 247 / 8%) 100%
    );
  mix-blend-mode: color;
}

.technical-image img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(0.78) contrast(1.04);
}
```

### Exact effect

- Saturation reduced to `78%`
- Contrast increased to `104%`
- A cool color blend overlay using the product’s deep teal and information blue
- No extreme blue tint

This works for equipment, locations, industrial environments, maps, and workspace photography. It is not a generic “tech photo” filter.

---

## 3.4 Duotone treatment

Use a true duotone only when the product’s visual system has a strong graphic or campaign-quality image language.

Good fits:

- cultural event,
- music platform,
- activist/civic campaign,
- youth-oriented consumer experience,
- editorial storytelling section,
- brand campaign.

Poor fits:

- account settings,
- financial tables,
- generic product dashboards,
- small card thumbnails where color fidelity matters.

```css
.duotone-image {
  position: relative;
  overflow: hidden;
  background: #1F244A;
}

.duotone-image img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(1) contrast(1.12);
  mix-blend-mode: luminosity;
}

.duotone-image::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(
      135deg,
      #24203D 0%,
      #5A47D5 48%,
      #FFB94D 100%
    );
  mix-blend-mode: color;
}
```

The result preserves tonal information from the image while applying the app’s violet/amber palette.

---

## 3.5 Subtle image depth without an overlay

Sometimes the correct treatment is only crop plus restrained tonal adjustment.

```css
.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(0.94) contrast(1.02);
  transition: transform 220ms cubic-bezier(0.16, 1, 0.3, 1);
}

@media (hover: hover) and (pointer: fine) {
  .product-card:hover .product-image img {
    transform: scale(1.025);
  }
}
```

Use this when image fidelity matters—food, products, art, place, photography portfolios, or anything where the source image itself is part of the value.

---

# 4. When I use SVG graphics instead of photos

I use SVG when the visual needs to be:

- explanatory rather than atmospheric,
- consistent across many sizes,
- tied directly to data or interaction,
- brand-specific,
- visually simple at small scale,
- impossible or misleading to represent through stock photography.

## Good SVG use cases inside UI

|Need|Better choice|
|---|---|
|Workflow explanation|Diagram or process graphic|
|Data relationship|Chart, map, timeline, node graph|
|Product architecture|SVG diagram|
|Empty state|Small purposeful illustration or icon|
|Status / category|Icon system|
|Branded pattern or motif|SVG shape/pattern|
|A physical or abstract concept that must remain controllable|Custom illustration|
|A small visual identity moment|Monogram, badge, mark|

## Use a photo instead when

- The user needs proof of a real place, person, product, or process.
- The subject benefits from authenticity and material detail.
- The product is selling an experience, place, or physical object.
- The image needs emotional specificity that a generic illustration cannot provide.

A photo of a real production location is better than an SVG clapperboard if the story is “this is the work we make.”

---

## SVG drawing conventions inside UI

The SVG is subordinate to the UI. It should not introduce a new unrelated illustration language on every route.

### For precision / operations products

- Geometric fills or simple monoweight strokes
- `stroke-width="1.5"` or `2` at a `24 × 24` icon scale
- Square or modest corner joins
- Low color count
- One semantic accent maximum
- Structured grid alignment
- Minimal texture
- No decorative sparkles or random circles

```tsx
export function DeliveryFlowGraphic() {
  return (
    <svg
      viewBox="0 0 320 144"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="Delivery path from edit to client approval"
      role="img"
      className="h-auto w-full"
    >
      <path d="M44 72H138M182 72H276" stroke="#8FA0A4" strokeWidth="1.5" />
      <path d="M133 67L138 72L133 77" stroke="#8FA0A4" strokeWidth="1.5" />
      <path d="M271 67L276 72L271 77" stroke="#8FA0A4" strokeWidth="1.5" />

      <rect x="16" y="44" width="56" height="56" rx="6" fill="#FFFFFF" stroke="#C7D0D2" />
      <rect x="132" y="44" width="56" height="56" rx="6" fill="#FFFFFF" stroke="#C7D0D2" />
      <rect x="248" y="44" width="56" height="56" rx="6" fill="#FFF9F5" stroke="#D9A888" />

      <path d="M31 61H57V83H31V61Z" stroke="#123B45" strokeWidth="1.8" />
      <path d="M147 61H173V83H147V61Z" stroke="#123B45" strokeWidth="1.8" />
      <path d="M263 62L276 84L289 62H263Z" fill="#D46B2C" />

      <text x="44" y="122" textAnchor="middle" fill="#607076" fontSize="11" fontFamily="Geist Mono">
        EDIT
      </text>
      <text x="160" y="122" textAnchor="middle" fill="#607076" fontSize="11" fontFamily="Geist Mono">
        REVIEW
      </text>
      <text x="276" y="122" textAnchor="middle" fill="#8C3C17" fontSize="11" fontFamily="Geist Mono">
        RELEASE
      </text>
    </svg>
  );
}
```

### For editorial or craft products

- Fewer, larger forms
- Material references through line rhythm or shape—not fake photorealistic effects
- Low contrast unless the illustration is the main feature
- One drawing vocabulary across every illustration
- Carefully controlled asymmetry
- Hand-drawn quality only if it belongs to the product, not as generic charm

### For playful consumer products

- Larger, friendlier silhouettes
- Strong shape rhythm
- Limited bright palette
- Smooth corners or intentional irregular geometry
- Minimal interior detail
- Motion only for feedback, not constant ambient decoration

## General SVG rules

1. Start with the silhouette and major shapes.
2. Use negative space deliberately.
3. Keep the element count tied to the brief.
4. Use one drawing vocabulary per illustration.
5. Do not mix outline, glossy 3D, stipple, and gradient fill without a reason.
6. Design for the smallest intended rendering size.
7. Do not use illustrations as filler for an otherwise weak empty state or hero.

---

# 5. Hero sections: distinguished versus generic

A distinguished hero is not defined by visual complexity. It is defined by a **clear relationship between proposition, composition, visual evidence, and action**.

## A generic gradient-blob hero

Typical characteristics:

- Vague headline: “The future of productivity starts here.”
- Generic subheading: “Manage your work in one powerful platform.”
- Two default CTA buttons.
- Large purple-blue gradient.
- Abstract blob shapes.
- Dashboard mockup with no specific data or task.
- Equal-weight typography and image.
- No reason the hero belongs to this product instead of any other SaaS product.

```tsx
// Generic: visually polished but product-generic.
export function GenericHero() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-violet-600 via-indigo-500 to-cyan-400 px-6 py-24 text-white">
      <div className="absolute -left-20 top-8 size-72 rounded-full bg-fuchsia-300/40 blur-3xl" />
      <div className="absolute bottom-0 right-0 size-96 rounded-full bg-cyan-200/30 blur-3xl" />

      <div className="relative mx-auto max-w-6xl text-center">
        <p className="text-sm font-semibold uppercase tracking-wider">All-in-one workspace</p>
        <h1 className="mt-5 text-6xl font-bold">The future of productivity starts here.</h1>
        <p className="mx-auto mt-5 max-w-2xl text-lg text-white/80">
          Manage your work, collaborate with your team, and get more done.
        </p>

        <div className="mt-8 flex justify-center gap-3">
          <button className="rounded-xl bg-white px-5 py-3 font-semibold text-violet-700">
            Get started
          </button>
          <button className="rounded-xl border border-white/40 px-5 py-3 font-semibold">
            Learn more
          </button>
        </div>

        <div className="mx-auto mt-12 h-80 max-w-4xl rounded-2xl border border-white/20 bg-white/10 backdrop-blur" />
      </div>
    </section>
  );
}
```

The problem is not that gradients, blur, or glass are inherently bad. The problem is that none of these elements are tied to a specific product, user, or task.

---

## A distinguished hero: film-production operations platform

The hero should communicate:

- who the product is for,
- what it helps them coordinate,
- what operational tension it resolves,
- what the studio world feels like,
- and what action follows.

### Design choices

```text
Stance:
Quiet editorial operations

Primary visual:
Real production workspace / practical editing image

Composition:
Text and dashboard proof have different jobs.
The copy block is not centered because this is not a generic campaign.
The visual provides actual evidence: shoot, crew, budget, and delivery status.

Palette:
Warm paper ground, deep studio green, oxide urgency accent.

Action:
One primary action, one low-emphasis proof link.

Material:
No gradient blob.
No decorative glass.
A restrained image treatment and border-led composition.
```

```tsx
export function DistinguishedFilmStudioHero() {
  return (
    <section className="border-b border-[#D4CABE] bg-[#F5F0E8]">
      <div className="mx-auto grid max-w-[1440px] gap-10 px-6 py-10 lg:grid-cols-[minmax(0,0.94fr)_minmax(0,1.06fr)] lg:px-10 lg:py-14">
        <div className="flex flex-col justify-between py-2 lg:py-5">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-[0.12em] text-[#756D64]">
              Production coordination, without the spreadsheet sprawl
            </p>

            <h1 className="mt-5 max-w-2xl font-['Newsreader'] text-[48px] font-medium leading-[0.98] tracking-[-0.032em] text-[#24211E] sm:text-[64px]">
              Keep the shoot moving. Keep the finish in view.
            </h1>

            <p className="mt-6 max-w-xl text-[17px] leading-[1.6] text-[#5F5850]">
              FRAME brings call sheets, budgets, crew availability, review notes, and
              delivery deadlines into one working production record.
            </p>
          </div>

          <div className="mt-9 flex flex-wrap items-center gap-x-6 gap-y-4">
            <button
              type="button"
              className="inline-flex h-11 items-center justify-center rounded-[4px] border border-[#2C302A] bg-[#2C302A] px-5 text-[13px] font-semibold text-[#FAF6EE] transition-colors duration-[160ms] [transition-timing-function:cubic-bezier(0.22,1,0.36,1)] hover:bg-[#464B42] active:translate-y-px focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A9462D] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F5F0E8]"
            >
              See a live project
            </button>

            <a
              href="#workflow"
              className="text-[13px] font-semibold text-[#24211E] underline decoration-[#AFA59A] underline-offset-4 transition-colors duration-[160ms] hover:text-[#A9462D] hover:decoration-[#A9462D] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A9462D] focus-visible:ring-offset-4"
            >
              Explore the workflow
            </a>
          </div>
        </div>

        <div className="relative min-h-[420px] overflow-hidden border border-[#C9BEB0] bg-[#E7DED2]">
          <img
            src="https://images.unsplash.com/photo-1485846234645-a62644f84728?w=1400&h=1000&fit=crop&auto=format"
            alt="A film crew preparing a camera setup in a daylight studio"
            className="absolute inset-0 size-full object-cover object-[56%_center] saturate-[0.86] contrast-[0.97]"
          />

          <div className="absolute inset-0 bg-[linear-gradient(90deg,rgb(37_33_30_/_58%)_0%,rgb(37_33_30_/_18%)_55%,rgb(37_33_30_/_0%)_100%)]" />

          <div className="absolute inset-x-5 bottom-5 border border-white/25 bg-[rgb(37_33_30_/_74%)] p-4 text-[#F8F3EB] backdrop-blur-[10px] sm:inset-x-7 sm:bottom-7 sm:p-5">
            <div className="flex items-start justify-between gap-5">
              <div>
                <p className="font-['DM_Mono'] text-[10px] font-medium uppercase tracking-[0.07em] text-[#D7CFC3]">
                  Current production
                </p>
                <h2 className="mt-2 font-['Newsreader'] text-[25px] font-medium leading-[1.1] tracking-[-0.015em]">
                  Autumn House
                </h2>
              </div>

              <span className="shrink-0 border border-[#D89A7B] bg-[#6E3020] px-2 py-1 font-['DM_Mono'] text-[10px] font-semibold uppercase tracking-[0.04em] text-[#FFECE2]">
                1 delivery at risk
              </span>
            </div>

            <div className="mt-5 grid grid-cols-3 gap-4 border-t border-white/20 pt-4">
              <div>
                <p className="font-['DM_Mono'] text-[10px] uppercase tracking-[0.06em] text-[#D7CFC3]">
                  Shoot days
                </p>
                <p className="mt-1 text-[15px] font-semibold">14 / 18</p>
              </div>
              <div>
                <p className="font-['DM_Mono'] text-[10px] uppercase tracking-[0.06em] text-[#D7CFC3]">
                  Budget used
                </p>
                <p className="mt-1 text-[15px] font-semibold">72%</p>
              </div>
              <div>
                <p className="font-['DM_Mono'] text-[10px] uppercase tracking-[0.06em] text-[#D7CFC3]">
                  Next delivery
                </p>
                <p className="mt-1 text-[15px] font-semibold">18 Jul</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
```

## Why this hero is more distinguished

It is not “distinct” because it has a serif, an image, or a glass panel. It is distinct because:

- The copy names a real production problem.
- The image belongs to the product’s actual world.
- The content proof is specific: shoot days, budget use, delivery risk.
- The composition is asymmetric for a reason: proposition on one side, operational evidence on the other.
- The warm paper, dark ink, and oxide alert map to the production/craft stance.
- The glass-like overlay is localized and earned: it sits over changing visual content and preserves context.
- The CTA is direct and singular.
- There is no generic “one platform for everything” language.
- There are no decorative blobs trying to substitute for a product point of view.

## P12 — icon-illustration execution mechanics

# 1. SVG construction: grid, primitives, paths, and curves

For an icon or mark, I do not begin by writing arbitrary path data. I choose a coordinate system, establish a construction grid, decide the visual vocabulary, then encode the final geometry.

The working order is:

```text
Use context and smallest size
  → viewBox and grid
  → silhouette
  → major positive/negative shapes
  → treatment choice: fill versus stroke
  → optical corrections
  → small-scale render test
  → final SVG cleanup
```

---

## 1.1 ViewBox and grid choices

I use different coordinate grids depending on the output type.

|Use|Typical viewBox|Why|
|---|---|---|
|Utility icon / UI icon|`0 0 24 24`|Aligns naturally with 16–24px icon use|
|Small app/logo mark|`0 0 48 48` or `0 0 64 64`|Enough coordinate precision without excessive path noise|
|App icon tile|`0 0 64 64`, `0 0 96 96`, or `0 0 128 128`|Supports shape nuance and rounded tile geometry|
|Crest / badge|`0 0 100 100` or `0 0 120 120`|Easier proportional construction for shields, rings, and ornaments|
|Large standalone illustration|`0 0 256 256` or a composition-specific canvas|Allows richer structure and scene-level layout|

For a mark that must work at **16px**, I generally use:

```svg
viewBox="0 0 64 64"
```

That gives a four-to-one coordinate relationship:

```text
64 SVG units = 16 rendered pixels
4 SVG units  = 1 rendered pixel
```

This is enough precision to make optical adjustments while still forcing simplicity.

## Grid discipline

A 64-unit viewBox does **not** mean every point must snap to a 4-unit grid. I use two layers:

```text
Structural grid: 8-unit or 4-unit increments
Optical adjustment: 0.5–2-unit deviations where the eye requires it
```

For example:

```text
Major geometry: x = 8, 16, 24, 32, 40, 48, 56
Optical adjustment: x = 31.5, 47.8, 54.1
```

The structural grid keeps the mark coherent. The optical adjustments prevent it from becoming stiff.

---

## 1.2 Primitives versus paths

I prefer primitives when the primitive is genuinely the correct form.

|Shape|Preferred SVG element|
|---|---|
|Circle|`<circle>`|
|Ellipse|`<ellipse>`|
|Rectangle / tile|`<rect>`|
|Straight line|`<path>` or `<line>`|
|Rounded capsule|`<rect rx>`|
|Regular polygon|`<polygon>` only if its vertices are meaningful|
|Custom silhouette|`<path>`|
|Organic interlocking form|`<path>`|
|Complex negative-space cutout|`<path>` with a mask, clipPath, or even-odd fill rule|

### Use primitives when they remain visually true

```svg
<circle cx="32" cy="32" r="18" />
<rect x="8" y="8" width="48" height="48" rx="12" />
```

### Use paths when the silhouette is the identity

```svg
<path d="M31.5 7C44 6.5 53.2 17.1 54.1 28.7..." />
```

A custom mark is usually a path because its outer contour is part of what makes it distinct.

I do not convert circles and rectangles to paths just to make the SVG look more “designed.” That only makes the source harder to maintain.

---

## 1.3 How I compute path coordinates

There are three levels of path construction.

### A. Geometric construction

For circles, arcs, polygonal marks, and modular geometry, I derive points from simple geometry.

For a point on a circle:

```text
x = cx + r × cos(θ)
y = cy + r × sin(θ)
```

For example, on a circle centered at `(32, 32)` with radius `20`:

```text
At 0°:   (52, 32)
At 90°:  (32, 52)
At 180°: (12, 32)
At 270°: (32, 12)
```

For a regular hexagon, I place six points at 60-degree intervals. For a monogram, I align stems, bowls, counters, and joins to a shared baseline/cap-height system.

### B. Proportional construction

For organic-but-controlled shapes, I define anchor relationships first.

For a 64 × 64 mark:

```text
Silhouette top:      y = 7–10
Silhouette bottom:   y = 54–58
Optical center:      y = 29–31
Left safe edge:      x = 8–10
Right safe edge:     x = 54–56
Primary mass center: x = 30–34
```

Then I derive actual path points from those anchors.

### C. Optical revision

The final coordinates are not always mathematical.

Examples:

```text
A circular body may need 1–2 units of overshoot.
A pointed top may need to pull back 1–2 units.
A heavy lower-right shape may need to shift 1 unit up-left.
A seam may need to move 1.5 units off-center to stop feeling static.
```

The code reflects the finished optical geometry, not the original construction diagram.

---

## 1.4 Bézier curves: how I handle control points

For most custom SVG curves, I use cubic Bézier commands:

```svg
C x1 y1, x2 y2, x y
```

Where:

```text
P0 = current point
P1 = first control point
P2 = second control point
P3 = destination point
```

The curve begins in the direction from `P0 → P1` and arrives in the direction from `P2 → P3`.

## Practical rules

### Rule 1: establish endpoints before controls

First decide where the curve begins and ends.

```text
Start: (31.5, 7)
End:   (54.1, 28.7)
```

Only then choose controls.

### Rule 2: set the desired tangent at each end

If the contour should leave the top almost horizontally, the first control point should remain near the same `y` value:

```text
P0 = (31.5, 7)
P1 = (44, 6.5)
```

If it should arrive at the right side vertically, the second control should sit above the destination:

```text
P2 = (53.2, 17.1)
P3 = (54.1, 28.7)
```

### Rule 3: use smooth tangent continuity

When two Bézier segments join, the final handle of the first segment and the first handle of the next should generally point along the same visual tangent.

Bad join:

```text
Curve A arrives diagonally.
Curve B leaves sharply sideways.
```

Result: an accidental kink.

Good join:

```text
Curve A ends at (54.1, 28.7) with an almost downward tangent.
Curve B begins with an almost downward tangent.
```

### Rule 4: use the quarter-circle constant only for true circular arcs

For a quarter-circle approximation, use:

```text
k = 0.55228475
```

For radius `r`, the handle distance from the quarter-circle endpoints is:

```text
k × r
```

Example: quarter circle from `(32, 12)` to `(52, 32)` with `r = 20`:

```svg
<path d="M32 12 C43.05 12 52 20.95 52 32" />
```

Because:

```text
0.55228475 × 20 = 11.045695
```

I use this only when I actually want a circular arc. I do not use it for a hand-tuned organic silhouette.

### Rule 5: use fewer curves

A mark that needs ten tiny Bézier segments to describe one simple contour is usually overworked.

For a small icon, I prefer:

```text
4–8 decisive outer-curve segments
1–3 important internal shapes
```

not dozens of tiny adjustments.

---

# 2. Stroke versus fill decisions

The choice is made based on the mark’s scale floor and its conceptual role.

## Use filled geometry when

- The mark must work at `16px`.
- The silhouette is more important than interior structure.
- The shape needs to remain visible at favicon scale.
- The design is compact, emblematic, or app-icon-like.
- The graphic must hold up on low-resolution displays.
- The subject can be communicated through positive and negative mass.

## Use stroked geometry when

- The mark needs to feel diagrammatic, technical, or calligraphic.
- The stroke itself is part of the identity.
- The smallest target is at least `24–32px`.
- The icon belongs to a monoweight UI icon system.
- There is enough empty space for stroke gaps to remain open.

## Use fill plus stroke when

- The stroke has a specific structural role: a keyline around a badge, a border defining a tile, or a material separation.
- The fill defines mass while the stroke defines a meaningful boundary.

I do not use fill plus stroke merely to make the mark look more complicated.

---

## Exact stroke widths by scale floor

The actual formula is:

```text
stroke width in SVG units
= desired rendered stroke width in pixels
× viewBox size
÷ rendered icon size in pixels
```

For a `64 × 64` viewBox:

|Rendered size|Preferred rendered stroke|SVG stroke width|
|---|---|---|
|16px|1.5–2px|`6–8`|
|20px|1.5–2px|`4.8–6.4`|
|24px|1.5–2px|`4–5.33`|
|32px|1.75–2px|`3.5–4`|
|40px|2–2.25px|`3.2–3.6`|
|48px|2–2.5px|`2.67–3.33`|
|64px|2.5–3px|`2.5–3`|

## Practical defaults

|Mark type|16px floor|24px floor|32–48px floor|
|---|---|---|---|
|Filled icon|No outline; use negative-space cuts|No outline or optional 1.5px structural stroke|Fill + optional 1.5–2px outline|
|Monoweight UI icon|`stroke-width="6"` on 64-grid|`stroke-width="4.5"` on 64-grid|`stroke-width="3–4"` on 64-grid|
|Badge / crest keyline|Use a strong filled boundary|`stroke-width="4–5"`|`stroke-width="2.5–4"`|
|Illustration|Simplify heavily|Can use a limited stroke system|More detail possible if context supports it|

For a mark that must work at `16px`, I normally choose fills and negative space over thin outlines.

---

# 3. Optical-balance verification in code

Code can help reveal problems, but it cannot fully determine optical balance. A mathematically centered mark may still look too low, too heavy, too wide, or too static.

I verify balance through multiple rendered checks.

## 3.1 Structural guide overlay

During development, I temporarily include centerlines, thirds, and safe bounds.

```svg
<g
  class="debug-guides"
  pointer-events="none"
  opacity="0.35"
  stroke="#D46B2C"
  stroke-width="0.5"
  stroke-dasharray="2 2"
>
  <path d="M32 0V64" />
  <path d="M0 32H64" />

  <path d="M21.33 0V64" />
  <path d="M42.67 0V64" />

  <rect x="8" y="8" width="48" height="48" fill="none" />
</g>
```

I remove this group from the shipped SVG.

## 3.2 Render at real scale, not only large scale

I render the same mark at the actual scale floor and adjacent use sizes.

```tsx
export function MarkScaleCheck() {
  return (
    <div className="flex items-end gap-6 bg-[#F5F0E8] p-8 text-[#1E4B43]">
      <CoastalRoasteryMark className="size-4" aria-label="Coastal coffee roastery mark at 16 pixels" />
      <CoastalRoasteryMark className="size-6" aria-label="Coastal coffee roastery mark at 24 pixels" />
      <CoastalRoasteryMark className="size-8" aria-label="Coastal coffee roastery mark at 32 pixels" />
      <CoastalRoasteryMark className="size-12" aria-label="Coastal coffee roastery mark at 48 pixels" />
      <CoastalRoasteryMark className="size-16" aria-label="Coastal coffee roastery mark at 64 pixels" />
    </div>
  );
}
```

At `16px`, I ask:

- Does the silhouette remain a distinct shape?
- Is the coffee-bean read still plausible?
- Is the internal cut clearly visible?
- Does the mark look centered?
- Does it collapse into an unrecognizable blob?
- Does its negative space stay open?

## 3.3 Inversion test

I render the mark in both polarities:

```tsx
<div className="flex gap-4">
  <div className="bg-[#F5F0E8] p-4 text-[#1E4B43]">
    <CoastalRoasteryMark className="size-8" />
  </div>

  <div className="bg-[#1E4B43] p-4 text-[#F5F0E8]">
    <CoastalRoasteryMark className="size-8" />
  </div>
</div>
```

If the negative space becomes shapeless or the seam disappears in one polarity, I revise it.

## 3.4 Bounding-box and visual-center check

I do not blindly center the viewBox geometry. I compare:

```text
Geometric center: (32, 32)
Mass center: where the filled form appears to sit
Negative-space center: where the cutout pulls the eye
```

A heavy lower-right mass may need the entire shape shifted about `1–2 SVG units` upward or leftward.

I commonly make adjustments like:

```text
Move entire silhouette up: 1 unit
Move seam right: 1.5 units
Extend top shoulder: 1.5 units
Reduce lower bulge: 2 units
```

Those small changes are meaningful at icon scale.

---

# 4. Complete example: coastal coffee roastery mark, 16px floor

## Brief

> “Create a mark for a coastal coffee roastery. It must work at 16px.”

## Brief axes

|Axis|Decision|
|---|---|
|Subject|Coffee + coast|
|Treatment|Geometric filled mark with one negative-space cut|
|Register|Grounded, salt-air, crafted, restrained—not nautical kitsch|
|Use context|Favicon, small logo, package stamp, app icon|
|Constraints|Must work at 16px; no wordmark requested; no unnecessary decorative elements|

---

## 4.1 Default-breaking pass

### The generic first idea

The instinctive generic interpretation would be:

```text
Coffee cup
+ steam lines
+ wave underneath
+ small sun or seagull
```

This is disqualified because:

- It is a familiar category-level coffee logo.
- It has too many separate nouns and decorative elements.
- At 16px, the cup, steam, wave, and sun would merge into noise.
- It says “coffee near the ocean,” not “a distinctive coastal roastery.”

---

## 4.2 Three differentiators

### Differentiator 1: coffee bean as the main silhouette

Instead of a cup, use a single bean-shaped silhouette.

```text
Specific shape language:
Tall, tapered seed form; heavier upper-left shoulder; lower-right taper.
```

Why it survives the inversion test:

- A coffee bean is more specific to roasting than a coffee cup.
- The outer silhouette carries identity at 16px.
- It avoids the generic café-symbol system.

### Differentiator 2: seam becomes a shoreline/tide cut

The bean’s internal seam is not a centered, perfectly symmetrical coffee crease.

```text
Specific shape language:
The seam begins narrow and high, then sweeps low and broad like a shoreline
before rising toward the lower-right edge.
```

Why it survives the inversion test:

- A generic bean seam is usually centered, vertical, and symmetric.
- This seam’s asymmetric long sweep gives a coastal reference without adding a separate wave symbol.

### Differentiator 3: weathered asymmetry, not nautical decoration

The bean’s outer contour is not a mirrored oval.

```text
Specific shape language:
The left side is more compressed; the upper-right shoulder is fuller;
the lower-right edge resolves into a narrower, wind-shaped taper.
```

Why it survives the inversion test:

- A generic coffee-bean icon is usually symmetrical and vertically centered.
- This asymmetry creates a more specific, weathered, coastal feeling through the silhouette itself.
- It avoids adding a literal sun, ship, anchor, bird, or wave.

---

## 4.3 Construction plan

```text
Canvas: 64 × 64
Scale floor: 16px
Primary form: filled custom bean silhouette
Secondary form: one negative-space tide seam
Palette: one ink color, transparent negative space
No stroke on the main silhouette
No gradients
No shadows
No text
No decorative particles
```

### Safe bounds

```text
Left edge:  9
Right edge: 55
Top edge:   7
Bottom edge: 58
```

### Optical center

The shape is intentionally placed slightly high:

```text
Geometric center: y = 32
Perceived center of heavy form: approximately y = 30.5
```

This prevents the lower body of the bean from making the mark feel visually low.

---

## 4.4 Final SVG source code

```tsx
type CoastalRoasteryMarkProps = {
  className?: string;
  title?: string;
};

export function CoastalRoasteryMark({
  className,
  title = "Coastal coffee roastery mark",
}: CoastalRoasteryMarkProps) {
  const titleId = "coastal-roastery-mark-title";

  return (
    <svg
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-labelledby={titleId}
      className={className}
    >
      <title id={titleId}>{title}</title>

      <defs>
        <mask id="coastal-bean-mask">
          {/* Black hides; white reveals. */}
          <rect width="64" height="64" fill="black" />

          {/* Main coffee-bean silhouette. */}
          <path
            d="
              M31.5 7
              C44 6.5 53.2 17.1 54.1 28.7
              C55.2 41.4 46.9 55.1 34.4 57.3
              C22.5 59.4 10.3 50.6 9.4 38.2
              C8.5 25.7 17.3 8.5 31.5 7
              Z
            "
            fill="white"
          />

          {/* Negative-space seam: coffee crease + shoreline sweep. */}
          <path
            d="
              M30.5 12.3
              C22.6 20.4 17.8 30.3 19.6 39.4
              C21.7 49.9 31.8 53.7 40.3 48.7
              C43.3 46.9 46.2 43.6 47.8 40.2
            "
            fill="none"
            stroke="black"
            strokeWidth="6.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </mask>
      </defs>

      {/* currentColor lets the mark work in ink, white, or brand color. */}
      <rect
        width="64"
        height="64"
        fill="currentColor"
        mask="url(#coastal-bean-mask)"
      />
    </svg>
  );
}
```

---

## 4.5 Key coordinate commentary

### Outer silhouette: top anchor

```svg
M31.5 7
```

The top of the bean is at `y = 7`, not `y = 8` or `y = 10`.

Reason:

- The form needs a little upward overshoot to avoid looking too low.
- The heavier lower body pulls visual mass downward.
- The `x = 31.5` placement avoids a mechanically centered feeling.

### Upper-right shoulder

```svg
C44 6.5 53.2 17.1 54.1 28.7
```

This is the fullest part of the silhouette.

Reason:

- The upper-right shoulder gives the bean a subtle wind-shaped asymmetry.
- The near-horizontal start from `(31.5, 7)` to control point `(44, 6.5)` creates a calm, shallow shoulder rather than a pointed peak.
- The endpoint `(54.1, 28.7)` keeps the right edge broad enough to survive at 16px.

### Lower-right taper

```svg
C55.2 41.4 46.9 55.1 34.4 57.3
```

The silhouette does not mirror the upper-right curve.

Reason:

- It becomes narrower and pulls inward, creating a less generic seed shape.
- The lower-right taper gives the interior seam somewhere to resolve without becoming a symmetrical coffee-bean slit.
- The bottom lands at `y = 57.3`, leaving a 6.7-unit margin in the 64-unit canvas.

### Left compression

```svg
C22.5 59.4 10.3 50.6 9.4 38.2
C8.5 25.7 17.3 8.5 31.5 7
```

The left side is slightly more compressed than the right.

Reason:

- Perfect symmetry would make the mark generic.
- The compressed side counterbalances the fuller upper-right shoulder.
- The bean remains readable because the asymmetry is restrained, not irregular.

### The seam / tide line

```svg
M30.5 12.3
C22.6 20.4 17.8 30.3 19.6 39.4
C21.7 49.9 31.8 53.7 40.3 48.7
C43.3 46.9 46.2 43.6 47.8 40.2
```

This seam is the mark’s central conceptual move.

- It begins near the upper third at `(30.5, 12.3)`.
- It drifts left and down as though entering a coastal inlet.
- It broadens around the lower half.
- It returns upward toward the right without closing into a centered coffee-bean split.

At 16px, the `strokeWidth="6.5"` mask becomes:

```text
6.5 / 64 × 16 = 1.625px
```

That is thick enough to remain legible as a negative-space cut.

### Why a mask instead of a background-colored stroke

This mark uses a mask so the seam becomes transparent rather than painted in a specific paper color.

That means it can render correctly as:

```tsx
<div className="bg-[#F5F0E8] p-4 text-[#1E4B43]">
  <CoastalRoasteryMark className="size-4" />
</div>

<div className="bg-[#1E4B43] p-4 text-[#F5F0E8]">
  <CoastalRoasteryMark className="size-4" />
</div>
```

The cutout always reveals the background beneath the mark.

---

## 4.6 Scale-floor test usage

```tsx
export function CoastalRoasteryMarkTest() {
  return (
    <div className="grid gap-6 bg-[#F5F0E8] p-8 text-[#1E4B43]">
      <div className="flex items-end gap-5">
        <div className="grid justify-items-center gap-2">
          <CoastalRoasteryMark className="size-4" />
          <span className="font-mono text-[10px] text-[#6B625A]">16px</span>
        </div>

        <div className="grid justify-items-center gap-2">
          <CoastalRoasteryMark className="size-6" />
          <span className="font-mono text-[10px] text-[#6B625A]">24px</span>
        </div>

        <div className="grid justify-items-center gap-2">
          <CoastalRoasteryMark className="size-8" />
          <span className="font-mono text-[10px] text-[#6B625A]">32px</span>
        </div>

        <div className="grid justify-items-center gap-2">
          <CoastalRoasteryMark className="size-12" />
          <span className="font-mono text-[10px] text-[#6B625A]">48px</span>
        </div>
      </div>

      <div className="flex items-center gap-5">
        <div className="bg-[#F5F0E8] p-4 text-[#1E4B43]">
          <CoastalRoasteryMark className="size-8" />
        </div>

        <div className="bg-[#1E4B43] p-4 text-[#F5F0E8]">
          <CoastalRoasteryMark className="size-8" />
        </div>
      </div>
    </div>
  );
}
```

At 16px, the expected read is:

```text
Primary read: a distinctive coffee bean
Secondary read: a flowing internal split / shoreline
Tertiary read: a coastal, weathered asymmetry
```

If the mark reads only as “an oval with a line,” I would not add a sun, wave, or coffee cup. I would revise the silhouette or the seam until the essential forms become clearer.

