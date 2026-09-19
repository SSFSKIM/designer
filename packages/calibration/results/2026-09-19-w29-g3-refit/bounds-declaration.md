# W29 G3 — the bounds, declared before the refit's first read

**Gate: W29 G3, acceptance clause 4; contract X5 ("bounds declared before reads");
W29 Decision Log 4 (a), ruled by the user 2026-09-19. Claims §5.153.**

This file and the `adopted-thresholds.test.ts` block it records are committed **before any
macOS 27 fit is read**, and the commit carrying them precedes every fit commit of this child.
Nothing about vitrea's material has been changed or measured at the moment it is written.

## What is declared

Five profiles, per tier, at exactly the 26.5 tables' values:

| 27 profile | texture table | dom table |
| --- | --- | --- |
| `apple-macos-27.0-1x-light-standard-glass0.5` | `TEXTURE_TIER_LIGHT` | `DOM_TIER_LIGHT` |
| `apple-macos-27.0-2x-light-standard-glass0.5` | `TEXTURE_TIER_2X_LIGHT` | `DOM_TIER_2X_LIGHT` |
| `apple-macos-27.0-1x-dark-standard-glass0.5` | `TEXTURE_TIER_DARK` | `DOM_TIER_DARK` |
| `apple-macos-27.0-2x-dark-standard-glass0.5` | `TEXTURE_TIER_2X_DARK` | `DOM_TIER_2X_DARK` |
| `apple-macos-27.0-1x-light-reduced-transparency-glass0.5` | `TEXTURE_TIER_REDUCED_TRANSPARENCY` | `DOM_TIER_REDUCED_TRANSPARENCY` |

They are **aliases** of the 26.5 constants rather than transcriptions, so the ruling "at exactly
the 26.5 tables' values" cannot drift by a digit. Breaking one out into its own literal is what
re-pinning a 27 bound would mean, and `RULED_EQUAL_TO_26_5` fails the day that happens silently.

## The sixth profile, declared second (Decision Log 5, ruled 2026-09-19)

G1c Part B published `apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5` and read it
against the 26.5 increased-contrast bed like for like after the five tables above were committed.
On that reading the user ruled a sixth table, at the 26.5 **increased-contrast** tables' values per
tier, on the same form and the same argument as Decision Log 4 (a). It is declared in the commit
that follows this file's first version, and **that commit still precedes every fit commit touching
this profile** — no macOS 27 fit had been read at either declaration.

| 27 profile | texture table | dom table |
| --- | --- | --- |
| `apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5` | `TEXTURE_TIER_INCREASED_CONTRAST` | `DOM_TIER_INCREASED_CONTRAST` |

**The row Decision Log 5 predicts will be hard, recorded before the read and not loosened:** the
coupled profile's native-to-native **SSIM-outside complement reaches 0.237 at its worst cell against
an allowance of 0.20** — the only material row of that profile outside its allowance, where every
other row is inside it at its worst cell. A miss there at this child's read is a floor decision for
the user, exactly as a dark ΔE miss is.

## What is deliberately not declared

- **No table for the DECOUPLED increased-contrast key** `…-increased-contrast-glass0.5`. Decision
  Log 4 (a): contrast alone on 27 against contrast with transparency reduction on 26.5, so a bound
  across the pair would be a bound on the toggle (claims §5.151 §9). It is also not read against
  vitrea at all in this wave: `compare`'s web accessibility flags key on the manifest's `a11yMode`,
  which reads `increased-contrast` for both 27 contrast profiles, so the web side cannot be put in
  contrast-without-reduction — G1c Part B's tracker entry. `UNBOUNDED_27_PROFILES` names it so the
  absence reads as the ruling.
- **No regression floor on any 27 profile.** Acceptance clause 4: the 27 bed sits at the
  seven-run probe bar, not the seventeen-run freeze bar a floor needs (claims §5.150 Part B §4).
  Enforced by its own case.
- **The conditioning predicate as it stands** — two arms, both sides, against the cell's own
  declared region. Unchanged by this child.
- **Cell counts, `PREDICATE_EXCLUDES` and `MATRIX_PARTITION`**, which are the machine's output
  and are transcribed from the sealed canonical run, not chosen. Until then each 27 profile
  carries the `PENDING_UNTIL_THE_27_READ` sentinel, and the gate asserts the matrix holds no row
  for a profile still carrying it.

## What a miss means, decided in advance

On the two light standard profiles and on reduced transparency the whole native-to-native
distribution measured by G2 sits inside the allowance these tables carry (ΔE mean p90 0.047,
0.048 and 0.009 against 0.07, 0.07 and 0.04). **On both dark profiles it does not** — ΔE mean p90
0.111 and max 0.155 against 0.09, edge-weighted p90 0.072 against 0.04 (Decision Log 4 (c)). The
user ruled these tables knowing that, and ruled what follows from it: **a dark miss at this
child's read is a floor decision for the user, recorded** — not a bound loosened after the fact,
not a re-fit after the holdout read, and not a fit failure. This child drafts that decision; it
does not take it.

## The machine at the moment of declaration

Read on 2026-09-19 on the capture machine, before any browser run of this child:

```
sw_vers                                                      27.0 / 26A428
defaults read com.apple.universalaccess reduceTransparency   0
defaults read com.apple.universalaccess increaseContrast     0
defaults read -g NSGlassTintAmount                           0.5
displayplacer                                                mode 68 (2560x1440, scaling on), current
python3 results/2026-09-16-w29-freeze/freeze.py verify        26.5 freeze intact: 1818 entries
```
