# The material profile documents

A profile document records one measured material. It carries a `patch` — exactly
the `MaterialProfilePatch` `createGlassRoot({ materialProfile })` takes and the
renderer's `withMaterialOverrides` applies — its provenance, the fitted status of
every constant it names, and `resolvedMaterialSha256`, a digest over the material
the patch **resolves to** rather than over the patch itself.

Six documents ship. The two `apple-macos-26.5-*` are frozen evidence; the four
`apple-macos-27.0-*-glass0.5{,-receded}` are the material a page draws by default
from 0.19.0, with a receded document per scheme carrying the unfocused-window
difference over its own scheme's active document. `apple-macos-26.5.seed.json` is
not a patch document and carries no digest.

## Two rules, and one file that exists because of them

**A document's bytes are an input to every bound stated over its bed.**
`test/adopted-thresholds.test.ts` builds `SHIPPED_DOCUMENT_HASHES` by hashing
every file in this directory, and `atAShippedDocument` keeps only matrix rows
whose `capturePath` names a current hash. So an edit to a document — a
re-recorded digest, a history comment, a reflowed line — drops every row read at
the old bytes out of every bound, floor, partition count and conditioning
exclusion, **silently and passing**. That is deliberate: it is the guard that a
document edited without a re-read cannot quietly gate a promise against a bed
nobody captured. It also means a re-seal and its canonical read have to land in
the same merge (W30 Decision Log 4 (b)).

**A recorded number is never rewritten.** When a fit moves a document's material,
the new digest goes in `resolvedMaterialSha256` and the old one goes into
`$comment-sha-history` beside it, with what moved and which claims section
records the move.

Those two rules collide exactly once: when the **renderer's default** gains a
leaf. `resolvedMaterialSha256` is taken over the fully resolved material, so a
material that gains a key moves every document's digest whatever that key holds —
including documents whose own patch did not change by one character and whose
pixels did not move at all.

**`digest-supersessions.json` is where that goes.** One record per shipped
document, with:

- `recordedSha256` — the document's own field: the digest it was sealed at, and
  still the reading;
- `currentSha256` — what the same fingerprint resolves to over the default as it
  now stands;
- `leaves` — the dotted paths the difference consists of;
- `decisionLog` and `date`.

The pins assert **both**: `tuned-profiles.test.ts` and
`macos26-document-selection.test.ts` require the document's field to be
`recordedSha256` and the material it resolves to today to fingerprint to
`currentSha256`, and `macos27-profile-export.test.ts` requires the runtime's own
readout to name `currentSha256`, because `root.material` names what actually
drew. `test/digest-supersessions.ts` is the shared reader.

The record exists under a **one-time exemption** the user granted (W29 Decision
Log 7 (a); shaped by W30 Decision Log 1 (a) and extended to all six documents by
4 (a)). It was spent by W30 G2, which added eight leaves to the renderer's
default at values that are algebraic identities — the span-graded shadow σ and
the scale-selective scatter's spanning set, inert until claims §5.159 fits them.
`packages/calibration/results/2026-09-20-w30-g2-leaves/` carries the proofs that
no pixel moved: the freeze intact at 1,818, the 34 renderer goldens byte-
identical, the CSS tier's declarations character-identical against bytes recorded
before the leaves existed, and the material itself deep-equal to a pre-wave copy
outside the eight named leaves.

**No later wave adds a record here without a new grant from the user.** A seventh
entry is a second exemption, and `tuned-profiles.test.ts` fails on one.

## Changing a document

Run the sealing script of the wave that is changing it — never edit
`resolvedMaterialSha256` by hand; a hand-written digest is a number nobody
checked. Land the re-seal and the canonical read that re-reads its bed in one
merge. Say in `$comment-sha-history` what moved and cite the claims section.
