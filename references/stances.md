# Stances

A stance is a committed visual system, not a mood. "Clean and modern" or "warm and friendly" are moods — they don't tell you a radius scale, a type ramp, or when a shadow is allowed. A stance is the thing that answers those questions consistently across every screen, so a page reads as designed rather than assembled section by section from whatever felt right at the time.

Use this file at the "commit to one stance" step of the workflow, and again at "build semantic tokens":

1. Look up the stance name that was sampled or chosen for the brief in the mapping table below.
2. If it maps to one of the five complete systems, port that system's token block into the project with **all values intact** — do not reweight a hex, retime a duration, or "improve" a shadow recipe. The values are the content; the system stops being that stance the moment its numbers drift.
3. If it maps to "derive fresh," there is no full token block here to copy. Use the derivation hints in its row, plus `references/color-engineering.md` and `references/typography.md`, to build a token set for that stance following the same shape (color roles, radius scale, border system, shadow tiers, spacing scale, type ramp, motion) as the five complete systems below. The hints name a ground temperature, a typography-tradition fit, and what the accent should do — start there, not from a blank page.
4. Either way, commit to the result in writing in the project's `DESIGN.md` before writing UI code against it.

## Five complete systems

Five concrete, shippable visual systems follow. Each is a complete starting spec, not a mood direction — implement against the token values below without inventing new ones. Use semantic tokens, not ad-hoc per-component colors, and use the named shadow recipes only where their stated elevation is actually needed.

---

### 1. Precision industrial

**Best for:** operations tools, infrastructure, logistics, scientific products, technical dashboards, high-trust data applications.

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

**Implementation rules:** use `--radius-2` for controls, `--radius-3` for panels, and `--radius-0` for data tables. Ordinary cards have a 1px border and **no shadow**. Use the orange accent for exceptions, high-priority actions, and keyboard focus — not decorative highlights.

---

### 2. Quiet editorial

**Best for:** studios, publications, cultural institutions, portfolios, research experiences, refined service brands.

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

**Implementation rules:** use full-bleed or editorially cropped images, with rules and whitespace doing most of the layout work. Use `--radius-0` or `--radius-1` for cards and image frames; reserve `--radius-3` for inputs and soft utility controls. The vermilion accent should appear rarely: selected state, active link, primary action, or a small editorial rule.

---

### 3. Contemporary craft commerce

**Best for:** premium goods, food and beverage, small-batch products, hospitality, independent retail, maker brands.

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

**Implementation rules:** use `--radius-2` for buttons and inputs, `--radius-3` for product cards, and `--radius-4` for image-led promotional surfaces. Product imagery can use `--shadow-product`; standard text/content cards should normally remain flat with a border.

---

### 4. Institutional calm

**Best for:** healthcare, education, civic services, legal products, financial planning, nonprofit and public-interest platforms.

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

**Implementation rules:** use `--radius-2` as the default across inputs, buttons, and cards. Information architecture should do more work than visual novelty: clear labels, ordered forms, durable tables, and obvious selected states. Never rely on color alone for validation, warnings, or progress.

---

### 5. Playful consumer

**Best for:** habit tracking, youth-focused products, consumer education, social tools, wellness, friendly productivity apps.

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

**Implementation rules:** use `--radius-3` for standard cards and controls, `--radius-4` for hero modules or bottom sheets, and `--radius-full` only for compact chips, avatars, or progress dots. Use the expressive support colors for categories or celebration moments, but maintain a single primary interaction color: violet. Motion should feel encouraging, not distracting; animations should never block recording a habit or reading progress.

## Component character per stance

The same component — a primary/secondary/disabled button set, an interactive card, and a data table — implemented three times, once per stance, with identical content shape so the differences in typography, density, borders, radius, color, shadow, hover behavior, and focus treatment are easy to diff. Keep the code; it is the reference. Adapt class names to whatever styling approach the project actually uses — the token values and interaction states are what must survive the port.

---

### 1. Precision industrial

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

### 2. Quiet editorial

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

### 3. Playful consumer

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

The character differences above are concentrated in:

- **Precision industrial:** tight radius, rule-based surfaces, minimal shadow, compact mono metadata, restrained transitions.
- **Quiet editorial:** mostly flat surfaces, generous vertical rhythm, serif hierarchy, underline-led secondary actions, low-noise states.
- **Playful consumer:** larger radius, brighter controlled color, soft elevated shadows, expressive display type, springier movement, rounded status/pill treatment.

## Mapping sampled stances to systems

`scripts/sample-ingredients.mjs` returns stance names from this table. Look up the sampled or brief-committed name, then either port the named system's full token block (Step 2 above) or derive fresh using the hints given — ground temperature (warm/cool/neutral, light/dark), which typography tradition (see `references/typography.md`) fits the character, and what job the accent color does.

| Stance | Origin | Maps to | Notes / derivation hints |
|---|---|---|---|
| `swiss` | figma | **Precision industrial** (use as-is) | Direct match: strict grid, mostly-neutral palette plus one accent, function-first restraint. Vignelli/Helvetica sensibility is exactly what the system's cool near-white + steel-tint surface model encodes. |
| `warm` | figma | **Contemporary craft commerce** (use as-is) | Direct match: cream/mineral neutrals, botanical green primary, clay accent, tactile shadow use on product media only. Aesop/Le Labo boutique register is this system's stated character. |
| `editorial` | figma | **Quiet editorial** (use as-is) | Direct match: serif display + sans body, asymmetric grids, warm paper ground, vermilion accent used rarely. Monocle/Kinfolk register is this system's stated character. |
| `archival` | figma | **Quiet editorial** (variant) | Keep the paper ground, ink foreground, and restrained accent, but push toward the museum-catalog register: pair the serif display with the mono UI face for numbered sections and object labels, tighten radius toward `--radius-0`/`--radius-1` everywhere (even utility controls), and let texture (not color) carry the "archival" feel. |
| `data-dense` | figma | **Precision industrial** (variant) | Keep the cool near-white ground, steel-tinted panels, and restrained accent, but compress the spacing scale (favor `--space-1`–`--space-4` over the larger steps) and lean harder on the semantic status colors for functional color-coding across dense tabular rows — Precision industrial's minimal-shadow, mono-data-column discipline is the right skeleton; density is the delta. |
| `memphis` | figma | **Playful consumer** (variant) | Keep the "one primary interaction color, expressive support colors for accents" rule and the soft-spring motion curve, but shift the ground toward a pastel rather than lavender-white, and let the support colors (mint/peach/sky) run more saturated and more geometric — Sottsass primary-shape energy over Playful consumer's rounded-pill softness. |
| `minimalist` | figma | derive fresh | Ground: neutral white or near-white, warmer and less steel-toned than Precision industrial. Typography: geometric sans or neo-grotesque for both display and UI, one weight doing most of the work. Accent: a single, rarely-used color reserved strictly for the one interactive or hero element per screen — the whole system should hold Precision industrial's "shadow almost never, structure from rules" discipline while reading as premium-consumer rather than industrial. |
| `brutalist` | figma | derive fresh | Ground: true black-and-white, no warmth in either surface — the starkest of any system here. Typography: monospace-as-display or condensed/expressive display, deliberately raw. Accent: one hot, fully saturated color (not muted like any of the five systems) used sparingly against the black/white field so it reads as an interruption, not decoration. |
| `kinetic` | figma | derive fresh | Ground: dark, near-black or deep charcoal — none of the five systems are dark-mode; this stance needs an inverted color-token direction (background/foreground swapped in role, not just value). Typography: neo-grotesque sans, tight and understated, since motion carries the expression, not the letterforms. Accent: one bright, high-contrast highlight color used specifically to mark motion state changes; see `references/motion.md` before building this stance, since motion is the primary character here rather than a craft-pass addition. |
| `maximalist` | figma | derive fresh | Ground: warm, textured, paper- or scrap-like — closer to Quiet editorial's or Contemporary craft commerce's warmth than to any cool system. Typography: deliberately mix two display traditions (e.g., condensed/expressive display against a serif or slab) rather than the single-display-face discipline every other stance here holds — this is the one stance where controlled layering of type is the point. Accent: multiple saturated accents are allowed, but they still need a hierarchy (one dominant, others supporting) or the "commit to one stance" floor breaks down into visual noise. |
| `risograph` | extension | derive fresh | Ground: uncoated warm paper, similar temperature to Quiet editorial's paper ground but grainier — texture should read at the surface level, not just as color. Typography: geometric sans or condensed/expressive display, printed rather than screen-native in feel. Accent: one or two flat, fully saturated spot-ink colors (fluorescent pink, orange, teal) used for overprint-style layering rather than gradients — no gloss, no blur. |
| `terminal` | extension | derive fresh | Ground: near-black, colder than kinetic's charcoal — a true console black. Typography: monospace-as-display for every role, not just data — headings, labels, and body all set in the same mono face, with box-drawing characters or hairline rules standing in for conventional borders where it reads naturally. Accent: exactly one phosphor color (green or amber) doing all signal work; treat it the way Precision industrial treats its orange accent, but starker and on a dark ground. |
| `bauhaus` | extension | derive fresh | Ground: neutral white or cream, flatter and more literal than any of the five systems — zero shadow anywhere, not even the sparing use Precision industrial allows. Typography: geometric sans exclusively. Accent: primary-color blocking (red, blue, yellow) used structurally to divide regions of the layout, not as a single "accent" role — this stance is the one place where more than one saturated color is expected to carry equal structural weight. |
| `y2k-web` | extension | derive fresh | Ground: cool white or pale sky-blue. Typography: rounded geometric sans. Accent: aqua/blue with a gradient sheen reserved for hero chrome elements only. This stance is a deliberate exception to the taste floor's usual flat/no-gloss default — flag the gloss and gradient use explicitly in `DESIGN.md` so it reads as a considered period reference rather than an accidental violation of `references/effects-policy.md`. |
| `luxury-fashion` | extension | derive fresh | Ground: pure white or pure black, no warmth — push further than Quiet editorial's restraint toward near-total monochrome. Typography: Didone/high-contrast serif for display, paired with a neutral sans for UI text; this is the one stance in the whole library that should reach for a Didone display face. Accent: none, functionally — replace the "one accent color" role with a monochrome-only interaction language (weight, spacing, and hairline borders instead of color) for selection and focus states, while still holding the accessibility floor's focus-visibility requirement through a visible (not colored) outline treatment. |
| `deco` | extension | derive fresh | Ground: warm cream or deep ink, with strong black-on-cream or cream-on-black contrast. Typography: glyphic serif or geometric sans, set with deliberate vertical emphasis in the type scale (taller, narrower display sizes than any of the five systems). Accent: a single metallic gold or brass tone, used for stepped-geometry rules, dividers, and symmetry markers rather than for interactive state — treat it as an ornamental accent role layered on top of, not replacing, a functional interaction accent. |
| `vernacular` | extension | derive fresh | Ground: warm cream or paper, close in temperature to Quiet editorial or Contemporary craft commerce but rougher — less refined, more hand-made. Typography: condensed/expressive display mixed boldly across more than one weight or size within the same heading role. Accent: this stance intentionally breaks the "one accent color" taste-floor rule — multiple saturated accents are expected — so record that exception explicitly in `DESIGN.md` alongside which specific colors are in play, rather than letting it read as an unreviewed violation. |
| `topographic` | extension | derive fresh | Ground: cool, terrain-toned neutrals (sand, khaki, glacier blue) rather than pure white or black. Typography: monospace-as-display for coordinates, annotations, and labels, paired with a neutral sans for body text. Accent: muted terrain-palette colors (contour green, elevation orange) used the way Precision industrial uses its orange — for markers, call-outs, and current-position indicators, not decoration. Structure the surface itself around a literal grid or contour-line motif rather than treating grid as implicit layout scaffolding. |

**Institutional calm** has no `ingredients.json` stance name mapped to it above — none of the 18 sampled stances name its "measured, trustworthy, civic" register directly. Reach for it directly, independent of the sampler, whenever the brief's product category is healthcare, education, civic services, legal, financial planning, or nonprofit/public-interest — a sampled stance name is a tiebreaker, and product-category trust needs override a sampled suggestion that doesn't fit the domain (see SKILL.md's precedence chain).

## Closing rule

Never blend two systems in one interface — a Precision industrial data table next to a Playful consumer hero reads as two projects stapled together, not one considered design. Pick one system (ported intact) or one derived-fresh stance, commit to it in writing, and record which system it is, or the full derivation (ground temperature, typography tradition, accent role) if derived fresh, in the project's `DESIGN.md` before writing UI code against it. A later revision that wants a different stance replaces the record in `DESIGN.md`; it does not layer a second stance on top of the first.
