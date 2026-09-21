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

## The digest rule (W31), and what it ended

Those two rules used to collide whenever the **renderer's default** gained a
leaf. `resolvedMaterialSha256` is taken over the fully resolved material, so a
material that gains a key moves every document's digest whatever that key holds —
including documents whose own patch did not change by one character and whose
pixels did not move at all.

**W31 Decision Log 1 (a) ended that collision by changing the fingerprint.** The
digest is now taken over the resolved material with every entry of
`MATERIAL_IDENTITY_TABLE` — an append-only constant beside
`DEFAULT_MATERIAL_PROFILE` — dropped where its gates hold their declared inert
identities. That is **rule 2**; rule 1 is the plain resolved fingerprint, and a
document sealed under the rule records `resolvedMaterialSha256Rule: 2` beside
its digest so a recorded digest names the function that produced it.

Under it:

- a leaf added at its identity moves **no** document's digest, so an operator
  wave no longer needs an exemption to land one;
- the two frozen macOS 26.5 documents' own recorded fields —
  `b2b570e4adcea8fb` and `874be66ea501621b` — are the **live** fingerprint
  again, without a byte of them being edited;
- a leaf whose default moves OFF its identity reappears in every digest the
  moment it moves, which is what keeps the rule from being a blind pin;
- a **gate-group** — a gate leaf at its identity together with the leaves it
  makes unread — is dropped as one unit and never leaf by leaf, because a gated
  leaf has no identity of its own to be at. Each such entry has to name the
  committed unit case that proves the gated leaves cannot reach the pixels.

The table is **append-only**, and the cost of that is worth stating: a post-seal
leaf's default IS its identity, forever. Moving one, or removing an entry, moves
every shipped document's digest at once.

**`digest-supersessions.json` is HISTORY**, and it is where the collision went
while it existed. One record per shipped
document, with:

- `recordedSha256` — the document's own field: the digest it was sealed at, and
  still the reading;
- `currentSha256` — what the same fingerprint resolves to over the default as it
  now stands;
- `leaves` — the dotted paths the difference consists of;
- `decisionLog` and `date`.

Since W31 G3 no pin reads it. `tuned-profiles.test.ts`,
`macos26-document-selection.test.ts` and `macos27-profile-export.test.ts` read
each document's own field under the rule, and `material-document.ts`'s two
hand-written digests went back to the frozen documents' own numbers. What keeps
the record TRUE rather than merely kept is `test/digest-supersessions.test.ts`,
which reproduces every `recordedSha256` under the rule and every
`currentSha256` under the plain fingerprint of the material **as it stood at
W30's close** — today's material with every identity-table entry added after W30
dropped. A recorded number is added beside and never deleted, and a record
nothing checks is a record that quietly becomes false.

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

**No later wave adds a record here without a new grant from the user.** A third
entry is a second exemption, and `digest-supersessions.test.ts` fails on one.
Under the digest rule no wave should need to ask: W31 G3 landed an operator leaf
and moved no frozen digest at all.

## Changing a document

Run the sealing script of the wave that is changing it — never edit
`resolvedMaterialSha256` by hand; a hand-written digest is a number nobody
checked. Land the re-seal and the canonical read that re-reads its bed in one
merge. Say in `$comment-sha-history` what moved and cite the claims section, and
record the rule the seal was taken under.

**Adding a leaf to the renderer's default is a different operation** and does not
touch a document at all. Add the entry to `MATERIAL_IDENTITY_TABLE` in the same
commit as the leaf, name the unit case that proves the identity, and ship the
default AT that identity — and then every document's digest is unmoved and there
is nothing here to change. A leaf added without a table entry is carried at
whatever it holds and moves every digest at once, which is the loud failure and
the one worth having.
