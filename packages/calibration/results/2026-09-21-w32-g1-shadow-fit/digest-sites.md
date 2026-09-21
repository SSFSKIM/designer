# W31 G3 — every digest site, rule 1 → rule 2

Claims §5.164 §2. The rule is `MATERIAL_IDENTITY_TABLE` in
`packages/renderer-webgpu/src/material.ts`: the fingerprint is taken over the
resolved material with every table entry dropped whose gates hold their declared
inert identities. **Rule 1** is the plain resolved fingerprint; **rule 2** is
this one, and a document sealed under it records
`resolvedMaterialSha256Rule: 2`.

## The two frozen macOS 26.5 documents — NOT edited, and the pin is their own field again

| document | recorded (unmoved) | plain fingerprint today (rule 1) | under rule 2 |
| --- | --- | --- | --- |
| `apple-macos-26.5-1x-light-standard` | `b2b570e4adcea8fb` | `e3a93c54e5ba60a2` | **`b2b570e4adcea8fb`** |
| `apple-macos-26.5-1x-dark-standard` | `874be66ea501621b` | `ade6eb6567c25d0d` | **`874be66ea501621b`** |

Nine leaves dropped on each: W30's eight plus W31's one.

**A precision claims §5.161 §7b rounds off.** §7b says the two frozen documents
"need no field, because their recorded digests equal both definitions' output".
They do not equal today's rule 1 — the middle column above. What they equal is
the plain fingerprint of the material **as it stood when they were sealed**,
which is exactly what rule 2 reconstructs by dropping the nine leaves added
since. The conclusion (no field needed) is unchanged; the reason is the sharper
one, and `tuned-profiles.test.ts` carries it beside the reader.

## The four macOS 27 documents — re-sealed under rule 2, with history

| document | was (rule 1) | now (rule 2) | dropped | file sha256 |
| --- | --- | --- | ---: | --- |
| `…-1x-light-standard-glass0.5` | `3a2513742936ceb1` | `62e684744954580b` | 6 | `66f29eb27e1fbe4032abf6daf79ba27faccf2cc2d062c1c511c5f78dacd88374` |
| `…-1x-dark-standard-glass0.5` | `f3008c3e9033ed4c` | `c61194f820d77280` | 4 | `b18ca27cdd8e24f0b1dff570314aa5a6c922333e9047b08755a029a555391d28` |
| `…-1x-light-standard-glass0.5-receded` | `d8015c2587126d08` | `183c8949f194ff43` | 6 | `3714970944ffd9e9878dc788478e2a98a8ace23eeae3e3ee882678422e4a63ef` |
| `…-1x-dark-standard-glass0.5-receded` | `8c85774d161fcbaa` | `1a64247df6786fc2` | 4 | `0e2c5a39b165017d1a9debb14d6cb2da22cc0ef2d2f1c0a6110f81bc5fbcbede` |

**These four rule-2 digests are the ones G0 PREDICTED** before a leaf existed
(claims §5.161 §7b, the table of four). They reproduce to the digit with the leaf
added, which is the proof that the leaf is digest-neutral — G0 computed them on a
material without `bodyChromaRetention` and this seal computed them on a material
with it. What moved is the DROP COUNT, from 5/3/5/3 to 6/4/6/4: the leaf is
dropped too, and dropping it changes nothing.

Neither macOS 27 document drops the σ group: both carry a fitted
`sigmaSlopePerSpan`, so that gate is not held. The light pair drop the scatter
group, `sizeScatterScaleRef` = 0.03 included.

## Every pin site

| site | was | now |
| --- | --- | --- |
| `profiles/apple-macos-27.0-*.json` × 4 | rule-1 digests, no rule field | rule-2 digests, `resolvedMaterialSha256Rule: 2`, history appended |
| `profiles/apple-macos-26.5-*.json` × 2 | untouched | **untouched** (X1) |
| `test/tuned-profiles.test.ts` | frozen pair through `supersessionFor(...).currentSha256`; 27 pair through their own fields under rule 1 | all six through their own fields under rule 2, with a case that rule 1 gives a different number |
| `test/macos26-document-selection.test.ts` | `currentSha256` | the documents' own fields |
| `test/digest-supersessions.ts` | the shared pin reader | **history**, with `test/digest-supersessions.test.ts` reproducing both halves |
| `src/material-document.ts` (macOS 26.5 endpoints) | `b340a4dee871633c` / `93ab090705c43f1f` | `b2b570e4adcea8fb` / `874be66ea501621b` |
| `src/macos27-profile.ts` (`MACOS_27_RESOLVED_MATERIAL_SHA256`) | `3a2513742936ceb1` / `f3008c3e9033ed4c` / `d8015c2587126d08` / `8c85774d161fcbaa` | `62e684744954580b` / `c61194f820d77280` / `183c8949f194ff43` / `1a64247df6786fc2` (regenerated from the documents) |
| `e2e/shared/window-activation.spec.ts` (eight full sha256) | over the whole handed material | over `materialDigestInput(...)` of it |

## The eight browser-read hashes, and the two that came home

Read back from Chromium at `e2e/shared/window-activation.spec.ts`:

```
macos27 light: active 62e684744954580b…  inactive 183c8949f194ff43…
macos27 dark:  active c61194f820d77280…  inactive 1a64247df6786fc2…
macos26 light: active b2b570e4adcea8fb…  inactive 6dcb32c422639d0d…
macos26 dark:  active 874be66ea501621b…  inactive 70391dee6d9990c2…
```

The four macOS 27 readings and the two macOS 26.5 active ones are the documents'
own digests, prefix for prefix. **The two macOS 26.5 INACTIVE readings are two of
the pre-W30 eight this file already recorded** — `6dcb32c4…` and `70391dee…`, to
the last digit. Nothing arranged that: the frozen material's receded composition
is what it was before W30's leaves existed, and dropping those leaves at their
identities hands back the same bytes. It is the rule's own sentence — "the digest
is over what draws" — read from a browser rather than from a script.
