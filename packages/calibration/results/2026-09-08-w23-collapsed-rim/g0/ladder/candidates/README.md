# The ladder's candidate documents

The five material-profile documents this gate rendered, copied out of scratch as evidence. They were
never in `packages/calibration/profiles/` and nothing reads them but `ladder.sh`, `probe-ladder.sh`
and the fit run they name.

| document | over | the leaves it overrides |
| --- | --- | --- |
| `light-levelgain.json` | the shipped light document | `optics.regular.rimLevelGain` −0.30, `rimCollapsed` 0.05 |
| `light-envgain.json` | the shipped light document | `optics.regular.rimEnvGain` +0.10 |
| `dark-levelgain.json` | the shipped dark document | `optics.regular.rimLevelGain` +0.50, `rimCollapsed` 0.05 |
| `light-fit.json` | the shipped light document | `optics.regular.rimAlpha` 0.844, `rimLevelGain` −0.628, `rimCollapsed` 0.038 |
| `dark-fit.json` | the shipped dark document | `optics.regular.rimAlpha` 0.0265, `rimLevelGain` 2.334, `rimCollapsed` 0.038 |

Two things a reader will notice and should not be surprised by.

**They carry a `$comment-w22-g0` key.** They were written by W22 G0's `make-candidates.mjs`
unchanged — that script is a generic leaf-override writer with no bound form of its own, which is
exactly why it was reused rather than copied, and its provenance comment names itself. The leaves it
lists are this gate's.

**`resolvedMaterialSha256` is the SHIPPED document's and is STALE in every one of them**, on W21's
rule: a fabricated hash beside a changed patch is worse than an honest stale one that says so.
Nothing in the capture path reads it; `tuned-profiles.test.ts` reads only the committed documents.
