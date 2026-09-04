# Persona authoring template

A persona is a distilled human decision function: a governing layer that, when invoked, replaces the sampler run and the stance choice, and injects judgment into every workflow step. One persona = one self-contained file in `personas/`, written against the eight parts below, in this order, with these exact headings. This template is the authoring contract; it is never loaded at runtime.

Authoring rules:

- Distill from a collected primary-source corpus (`docs/research/personas/<name>/`), never from generic knowledge. Every per-step law block ends with `Sources: <corpus file(s)>`. A law that cannot be grounded in the corpus does not ship.
- Write laws agent-executable: exact values and checkable prescriptions ("one type family; exactly two weights across the ramp, derived from the family's own weight axis"), never moods ("keep it elegant").
- The home token system copies the shape of the worked derivations in `references/stances.md`: color roles, radius scale, border system, shadow tiers, spacing scale, type ramp, motion.
- Keep the whole file readable in one sitting — it is consulted mid-build as one voice.

## 1. Identity & lineage

Who the composite is; what each source in the lineage contributes. Written so the agent adopts a character, not a checklist.

## 2. The decision function

The persona's core loop, as questions asked at every choice.

## 3. Per-step laws

One block per spine step, each ending with a `Sources:` tag, under these subheadings:

### Composition & information architecture
### Color
### Typography
### Spacing & grid
### Surfaces & effects
### Motion
### Copy
### Single marks

## 4. Home token system

A complete stances.md-shaped token block (CSS custom properties) — the persona's default starting system, so a build begins without re-derivation.

## 5. Derivation rules

How to deviate in persona when the product genuinely requires it, without breaking character.

## 6. Ban list

Explicit negatives, mechanically checkable where possible. Keep the grep-checkable subset in sync with any eval assert script that enforces it.

## 7. QA lens

Added checks run after `references/qa-protocol.md`, phrased in the persona's voice — including the removal pass: name one element you tried to remove and why it had to stay.

## 8. Provenance

Corpus directory, distillation notes file, distillation date.

## Authoring note: character vs. bias

A persona is a bias on purpose — the defect class is *unauthored* preference. Two tests separate them. **Authorship:** a trait is character when it traces to the corpus; it is a defect when it comes from the model's training prior or from an artifact of the persona file itself (an anchor value repeated until it reads as law, a rule phrased so one answer always wins) while wearing the character's clothes. **Reasoning versus output:** where the source designer's own practice produced different answers for different products, distill the reasoning, never one answer — converging outputs across unrelated products is the tell that an instantiation froze into law. Corollaries: guardrails against unauthored bias (rejected-candidate records, hue audits) are per-persona laws, not template requirements — a persona whose authored character *is* a signature palette would rightly refuse them, because its answer to "why this hue?" is "because it's mine." And derivation freedom applies at birth, not afterward: a value derived once may be held permanently — commitment itself can be the authored character.
