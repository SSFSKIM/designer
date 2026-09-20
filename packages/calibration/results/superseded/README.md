# Superseded generations of the canonical matrix

`results/matrix.json` holds **one generation per profile**: the rows whose every material
profile document is on disk at the bytes the row records. Every other row lives here,
byte for byte, in the file the document it was read at names.

A cell's key carries its `capturePath`, and the `capturePath` names the material profile
document and that document's twelve-hex content hash. A refit moves the document's bytes,
so the next canonical run does not overwrite the rows read at the old bytes — it appends a
second generation beside them, because a recorded number is never rewritten. That rule is
what made the file grow: 72,102,187 bytes over 2,017 rows at 0.19.0, two macOS 27
generations of 455 rows each, past GitHub's recommended 50 MB and one recapture from its
100 MB refusal. Splitting by generation keeps every row and answers "which generation
ships" **by name** rather than by reading a timestamp: the working file is the shipped
generation, and a superseded row is one open of a file here away (or one `git show`, as
before).

## The naming rule

**A file is named by the ACTIVE document's twelve-hex SHA-256** — the document
`--material-profile` selected, which is also the runtime material the patch is a
difference from.

A generation is a *set* of documents, not one: a canonical run that poses its inactive
scenes names a second, `--receded-profile`, and a scheme pair is two more. A set has no
single hash, so the rule picks the one document the others are differences over. A
receded document **never names a file**; it travels with the active document of its own
scheme, because a difference document cannot be read apart from the document it differs
from. A light generation and a dark generation therefore land in two files — they are two
materials, refitted together but read apart, and the light file is the one somebody
looking for "the light bed before the refit" wants.

Finding a superseded row is a **lookup, never a pattern match on a file name**.
`index.json`'s `byDocumentSha256` maps every document hash a superseded row names —
active and receded alike — to the file that holds it. `files` carries each file's
documents, claims section, capture window, row count, bytes and whole-file digest.

**One shape the plain rule cannot name, and what it is named instead** (added
2026-09-20, W30 G1 review closure, c9a §5.157 §3). A refit can seal a new receded
document over an active document that still ships — the unfocused endpoint refitted
alone — and the rows it supersedes then name a *current* active document. Naming that
file after the active hash would describe it as a generation that is in fact the
shipped one, so the file takes the **compound** name `<active>-<receded>.json` and
`index.json` maps both hashes to it. Nothing about reading changes, because reading was
already a lookup and the name is never parsed. The split script produces the compound
name where it used to refuse the shape, and refuses instead where a hash would have to
name two different files here.

## The files

| file | profiles | document read at | claims | captured | superseded | rows | bytes |
| --- | --- | --- | --- | --- | --- | ---: | ---: |
| `fa872c683f3e.json` | `apple-macos-27.0-1x-light-standard-glass0.5` (138), `-2x-light-standard-glass0.5` (138), `-1x-light-increased-contrast-coupled-glass0.5` (35), `-1x-light-reduced-transparency-glass0.5` (32) | `profiles/apple-macos-27.0-1x-light-standard-glass0.5.json` `sha256:fa872c683f3e` | c9a §5.153 (W29 G3) | 2026-09-19 | 2026-09-20 (W30 G1, c9a §5.157) | 343 | 12,421,699 |
| `96b36eedf1c4.json` | `apple-macos-27.0-1x-dark-standard-glass0.5` (56), `-2x-dark-standard-glass0.5` (56) | `profiles/apple-macos-27.0-1x-dark-standard-glass0.5.json` `sha256:96b36eedf1c4` | c9a §5.153 (W29 G3) | 2026-09-19 | 2026-09-20 (W30 G1, c9a §5.157) | 112 | 3,911,642 |

Both files are W29 G3's refit read, superseded by W29 G3b's shadow re-seal (c9a §5.154)
and published at §5.155. Neither names a receded document: G3's read predates the receded
documents, which G3b sealed. The shipped generation — the 455 rows the working file keeps
— was read at `f42ddec1cf5a` / `272d1b0c3e10` with `59d4b20a4596` / `5c81bc72edad`.

## One cell that only exists here

`apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5`,
`hc-text__capsule-button__inactive`, dom tier, holdout. At G3b's read the CSS tier's
extracted contour there is 0.00 px and `contourCurvature` refuses rather than reporting, so
that read produced **no row** for the cell and G3's row stayed the newest (c9a §5.154,
§5.155 §3). Moving the superseded generation therefore takes this cell out of the working
file rather than leaving a stale twin behind. Nothing is lost and nothing should be
re-read: the row is in `fa872c683f3e.json`, it is holdout and inactive, and both the
inactive-pose drop and the generation drop in `test/adopted-thresholds.test.ts` already
excluded it from every bound, floor and count.

## Writing and checking a file here

`results/2026-09-20-w30-g1-split/split-generation.py` performs the split and
`append-check.py` beside it proves it. The split takes the hashes that are **current**
(by default every file in `packages/calibration/profiles/`, which is exactly what
`adopted-thresholds.test.ts`'s `SHIPPED_DOCUMENT_HASHES` derives) and moves everything
else. Rows move as raw text slices, never through a JSON round trip. The append-check
reconstructs the pre-split file from the parts and compares its SHA-256 to the digest
recorded before a byte moved, which is a proof that no row was lost, changed or
reordered; four of its six clauses read the rows off the files rather than out of the
plan.

`apply` names its own evidence directory and its own claims section — there are no
defaults, because a second run that inherited the first's would overwrite the
before-manifest the append-check reconstructs from. The next application of contract X7,
in full:

```bash
python3 packages/calibration/results/2026-09-20-w30-g1-split/split-generation.py apply \
    --evidence packages/calibration/results/2026-09-20-w30-g4-landing/ \
    --claims "c9a §5.160"
```

Everything it refuses is decided over the whole plan before a byte is written, so a
refusal leaves this directory as it was: a row of a frozen macOS 26.5 profile selected to
move (contract X1, which the tool holds rather than the operator), a `capturePath`
carrying a document hash its clause pattern does not parse, a destination or a
before-manifest that already exists, and an index entry that would be repointed.
`classifier-selftest.py` exercises the classifier on a synthetic matrix carrying the
generation shapes the bed does not have; its output is committed beside it.
