# Typography

This file teaches how to choose, pair, and scale typefaces for a semantic type-token system. Use it at the "build semantic tokens" step alongside `references/color-engineering.md` — that file derives the color tokens from a chosen stance, this one derives the type tokens: which faces to draw from, how a pairing is derived (with ten worked examples), which faces and pairings read as overused AI defaults, the operational scales to size and weight them at, the case-behavior rules that keep uppercase a structural signal rather than a default text style, and how many families a project actually needs.

## Selection order

Do not assume there is one universal bundled font library. Select fonts in this order:

1. **Existing project or design-system fonts** — if a kit, brand system, or imported Figma file specifies fonts, those are the source of truth.
2. **Project-provided local fonts** — if the repository includes licensed font files, use those.
3. **Google Fonts** — the normal fallback for self-contained web UI work in this environment.
4. **System fallbacks** — always defined after the preferred family.

## The curated library

For a new project without an existing font system, draw from a deliberately curated set rather than picking random Google Fonts.

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

## Ten worked pairings — method illustrations, not a menu

These ten exist to demonstrate the derivation method — match the display face's register to the committed stance, pair on a contrast axis, give each family one job — not to be picked from. Ten rows cannot cover the stance space, and treating this section as a catalog collapses the sixty-face pool above into the same handful of faces on every project: a new monoculture indistinguishable from the defaults this file exists to break.

The binding order is derive first, compare second:

1. **Derive first.** Start from your committed stance and the register tables above: pick the display face whose register carries the stance, then a UI face on a contrast axis, then a mono only if a real data role exists. Record the derivation in DESIGN.md.
2. **Compare second.** Only after deriving, check your result against these ten. Landing on a listed pairing independently is legitimate — but DESIGN.md must then carry the stance-specific reason, never "it is a known-strong pairing."
3. **When in doubt, swap one slot.** If your derivation matches a listed pairing and the brief does not demand those exact faces, replace at least one family with a same-register neighbor from the tables above. The pool is deep; a pairing this file has never printed is usually available one row away.

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

## Overused defaults

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

Do not reject a face because it is popular. Reject it when it is being used as a substitute for art direction.

## Operational scales

### Dense operational tool

This is the kind of scale to ship for a desktop-first operational tool with tables, alerts, activity logs, filters, key metrics, and compact navigation.

#### Families

```css
--font-display: "Archivo", "Helvetica Neue", Arial, sans-serif;
--font-ui: "Manrope", "Helvetica Neue", Arial, sans-serif;
--font-mono: "Geist Mono", "SFMono-Regular", Consolas, monospace;
```

#### Desktop scale

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

#### Mobile adjustments

|Role|Mobile size|
|---|---|
|Display metric|36px / 2.25rem|
|Page title|28px / 1.75rem|
|Section heading|20px / 1.25rem|
|Card heading|16px / 1rem|
|Body|14px / 0.875rem|
|Body compact|13px / 0.8125rem|
|Caption|12px / 0.75rem|

#### Operational-tool rules

- Use the display style for a key number, primary dashboard statement, or major page title—not every card.
- Use UI sans for all ordinary controls, table text, buttons, filters, navigation, and descriptions.
- Use mono only for values where fixed-width or technical structure improves scanning: dates, timestamps, IDs, duration, percentages, equipment codes, or live readings.
- Keep body text at `14px` minimum for dense desktop UI unless there is a strong reason to use `13px`.
- Avoid all-caps headings. Use uppercase only for short structural labels.
- Use tabular numerals when supported for financial values, measures, and data tables.

```css
.tabular-data {
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums slashed-zero;
}
```

### Editorial landing page

This is the kind of scale to ship for a desktop-first landing page with a strong hero, selective image use, narrative sections, and spacious pacing.

#### Families

```css
--font-display: "Newsreader", Georgia, serif;
--font-ui: "Public Sans", "Helvetica Neue", Arial, sans-serif;
--font-mono: "DM Mono", "SFMono-Regular", Consolas, monospace;
```

#### Desktop scale

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

#### Mobile adjustments

|Role|Mobile size|
|---|---|
|Hero display|48px / 3rem|
|Display / major statement|40px / 2.5rem|
|H1|34px / 2.125rem|
|H2|28px / 1.75rem|
|H3|20px / 1.25rem|
|Lead|18px / 1.125rem|
|Body|16px / 1rem|

#### Editorial-landing-page rules

- Use the largest display size for one primary moment, usually the hero.
- Do not make every section heading look like a hero headline.
- Keep display line-height compact but not mechanically tight: typically `0.96–1.08`.
- Keep body line-height generous: typically `1.55–1.65`.
- Use the mono face only for image captions, article-like metadata, dates, labels, or numbered sections.
- Avoid justified text on the web.
- Keep longer body copy to a readable measure, generally around `60–72ch`.

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

## Case behavior

Use uppercase sparingly. Uppercase is a **structural signal**, not an everyday text style.

### Use uppercase when all of the following are true

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
- Multi-word buttons such as `CREATE A NEW PROJECT`
- Form field labels with long descriptions
- Error messages
- Helper text
- Dense mobile navigation
- Large blocks of data labels
- Anything that needs quick, relaxed reading

### Exact uppercase values

#### Standard UI uppercase label

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

#### Editorial eyebrow

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

#### Tiny mono utility status

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

Use only for short values such as `LIVE`, `SYNCED`, `PAUSED`, `DRAFT`, `LOCKED`, or `OFFLINE`.

#### Mobile adjustment

Do not shrink ordinary uppercase labels below `10px`. If there is not enough space for an `11px` uppercase label with readable tracking, switch to sentence case, abbreviate intentionally, or redesign the component.

## Family-count rule

Normally, use:

- **One family** for a dense operational product, sometimes plus mono.
- **Two families** for most landing pages: display + UI sans.
- **Three families** only when there is a real metadata/data role: display + UI sans + mono.

Do not add a third family just because “three fonts feels more designed.”
