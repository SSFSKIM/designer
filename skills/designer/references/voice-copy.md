# Voice and copy

This file teaches how to write the real content that goes into a design as it's built — believable data instead of placeholder filler, a voice resolved from the stance's energy and criticality for headlines and system messages, the microcopy rules that keep buttons, labels, tooltips, and errors legible, and the length heuristics that keep copy fitting the composition it lives in. Use it at the "build with realistic content" step, after composition (`references/composition.md`) has decided what's dominant and secondary and before the craft pass adds motion and effects — copy is written into the layout that composition already built, not after it. Lorem ipsum and generic filler hide real hierarchy, density, and spacing problems that only surface with content of realistic length and shape; everything below exists to make that real content plausible rather than obviously fake.

## Believable data

The trick isn't randomness — it's internal consistency and domain-correct distributions. Fake data reads fake when the numbers are uniform, too round, or don't relate to each other.

**Names & people:** vary ethnicity and structure (Mina Okafor, Ari Kumar, Elena Ward, Noah Reyes — not five Anglo first names). Match role plausibility: a "Director" is a full name; a commit author might be a handle. Avoid celebrity/real-company collisions.

**Companies:** invent ones that sound like the sector — SaaS gets abstract-noun names (Northwind, Lattice-ish), agencies get founder-surname or single-word marks, industrial gets compound functional names. Never real trademarks.

**What makes numbers believable — the domain-specific part:**

- **Budget / finance table:** numbers must be non-round and internally arithmetic. `$218,400` reads real; `$200,000` reads placeholder. Committed spend should be less than approved and roughly 60–75% of it. Variance is a small percentage (`+2.8%`), not `+40%`. Money aligns right, tabular-nums, consistent decimal places. A total should actually sum its rows — reviewers do add them up.
- **Fitness app:** numbers live in human physiological ranges and cadences. Resting HR 48–72, not 140. Steps 4k–14k. A run pace like `8:42/mi`. Streaks are small integers (`12 days`). Believability = "could a real body produce this?" — a 62-minute 5k is as wrong as a $200k round budget.
- **Analytics/SaaS metrics:** week-over-week deltas in single-to-low-double-digit percents; MRR that's a sum of plan tiers; churn under ~5%; DAU < MAU by a sensible ratio. A chart should have one interesting inflection, not noise or a straight line.
- **Dates:** relative to today and causally ordered — "created" before "updated" before "due." Use real recent dates (`18 Jul`), business-day-aware for work apps. No `01/01/2024` for everything.
- **Prices:** psychological endings where the domain uses them ($29, $1,299) but not in a B2B contract table where clean-ish negotiated figures ($164,800) read truer.

The meta-rule: pick a few anchor numbers, then derive the rest so relationships hold. One project's progress %, budget, and due-date should tell the same story.

## Voice by energy and criticality

Voice is derived, not picked off a list. Energy sets the enthusiasm ceiling — contractions, a wink, an exclamation mark only at lively and above. Criticality sets directness and formality: at consequential, errors are literal and actionable, humour never appears in an error, a warning, or an irreversible flow, there is always a support or recovery path, and urgency is never manufactured. The product's voice stays stable across the surface; it is tone that shifts with the moment.

The same four pieces of copy — hero headline, primary CTA, empty state (no projects yet), and error (save failed) — written four ways for a project/production management tool. What moves between them is sentence length, contraction use, first-person plural vs. none, and how the error handles blame; the information is identical, the posture isn't.

**A. quiet × consequential, dense** — terse, technical, states facts.

- _Headline:_ "Every production, tracked to the frame."
- _CTA:_ "Start a project"
- _Empty state:_ "No active productions. Create one to begin tracking budget and schedule."
- _Error:_ "Save failed. Changes weren't written. Retry."

**B. composed × transactional** — human, unhurried.

- _Headline:_ "The calm way to run a demanding slate."
- _CTA:_ "Begin your first project"
- _Empty state:_ "Nothing in motion yet. When you start a project, it'll live here — schedule, budget, and all."
- _Error:_ "We couldn't save that just now. Nothing was lost — give it another try in a moment."

**C. lively × exploratory** — casual, energetic, a wink.

- _Headline:_ "Herd your projects. Finally."
- _CTA:_ "Let's go →"
- _Empty state:_ "It's quiet in here. Spin up a project and watch this fill up."
- _Error:_ "That didn't stick. Nothing broke — hit save again?"

**D. quiet × consequential, formal** — measured, plural, a support path.

- _Headline:_ "Comprehensive oversight for every production."
- _CTA:_ "Create a project"
- _Empty state:_ "You have no active projects. Create a project to begin managing schedules and budgets."
- _Error:_ "Your changes could not be saved. Please try again. If the issue continues, contact support."

A and D sit at the same energy and the same criticality and still sound different: formality and the offer of a recovery path come from the stakes and the audience, not from energy.

Playful reassures fast and moves on; institutional offers a support path; industrial states facts; editorial soothes. Read the energy and criticality lines from `DESIGN.md` §0 and hold that posture across every piece of copy on the surface — don't let one screen sound editorial and the next sound industrial.

## Microcopy rules

- **Button verbs:** always a verb, always specific to the outcome. "Create project," "Save changes," "Send invite" — never "Submit," "OK," "Click here." Destructive buttons name the consequence: "Delete project," not "Confirm."
- **Name persistence:** an action keeps the same name through the whole flow, so the button that says "Publish" produces a toast that says "Published," not "Success" or "Done." The vocabulary of an interface is the signposting for someone navigating the product — cohesion and consistency are how people learn their way around it.
- **Labels:** noun or noun-phrase, no colon, no "Please." "Email," not "Please enter your email." Match the field to its data type in phrasing.
- **Links:** a link's visible text should carry its destination or outcome on its own, with no surrounding sentence required — "View invoice history," not "Click here" or "Learn more" repeated a dozen times on one page with nothing to tell them apart.
- **Tooltips:** explain why/what happens, not restate the label. Good: "Archived projects stay searchable but leave the active slate." Bad: "Archive button." Keep to one line, no terminal period on fragments.
- **Case — the decision rule:**
  - Sentence case for basically everything: buttons, labels, menu items, headings, empty states, toasts. It's calmer, more modern, easier to read, and fails gracefully with dynamic content.
  - Title Case only when the surface is genuinely formal or institutional — high criticality with a formal audience — or the type tradition is editorial-classic, or for genuine proper nouns and product names.
  - Never ALL-CAPS as real text — only as a styled eyebrow/label via CSS `text-transform` with letter-spacing, so the underlying string stays sentence case and accessible.
  - Consistency beats correctness: pick one and hold it across the whole surface. Mixed case is the tell of copy written by committee.
- **Numbers in copy:** spell out zero–nine in prose, use numerals in UI/data. Always numerals for money, dates, metrics.
- **Error anatomy:** say what happened, whether data was lost, and what to do next — in that order, every time. Never expose stack traces or blame the user.
- **Empty states invite action:** an empty screen is a moment for direction, not mood — it names what's missing and gives the one action that fills it, it never just sits there silent or apologizes for having nothing to show.

## Length heuristics

- **Hero headline:** 3–8 words, one line at desktop hero scale. If it wraps to three lines it's a paragraph wearing a headline's font.
- **Hero subhead:** one sentence, ~12–22 words, ≤ ~2 lines. It earns the headline — adds the concrete "what/for whom," never restates it. Cut it entirely if the headline is self-sufficient.
- **Section intro:** 1–2 sentences, capped ~30 words, at a readable measure (≤65ch). Orients, doesn't explain — the section content explains.
- **Card description:** 1 sentence, 6–16 words, and uniform across sibling cards — mismatched card copy lengths wreck a grid's rhythm more than the words themselves matter. Truncate to fit the ragged-bottom, don't let one card balloon.
- **Empty state:** one line of what's missing + one line of how to fix it + the action button. Three elements, no paragraph.
- **Button:** 1–3 words.
- **Tooltip:** ≤ ~10 words, one line.
- **Error toast:** ≤ 2 sentences.

Copy length is a layout constraint as much as a writing one: write to the space the composition allows, keep sibling elements the same length for rhythm, and treat "can I cut this?" as the default — the shortest version that stays specific wins. Vague-and-short ("Powerful. Simple. Fast.") is worse than specific-and-slightly-longer; cut filler, not information.

## Writing as design material

Copy is a design decision, not something poured in after the layout is finished — weigh a word choice the same way you'd weigh a spacing value or a color token. Every string on a screen exists to make the interface easier to understand; if a word isn't doing that job, cut it.

Name things the way the person using them would, not the way the system implementing them is structured — someone manages notifications, they don't configure a webhook. When two phrasings say the same thing, prefer the plain, specific one over the clever one; clever rarely survives a second reading.

Hold each element to a single job: a label should only name the field, an example should only show a case, and neither should quietly stretch to cover for the other's absence.

---

This section is adapted from Anthropic's `frontend-design` skill ("More on writing in design").
