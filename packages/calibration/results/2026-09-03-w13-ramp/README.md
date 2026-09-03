# W13 — the body's depth ramp, carrying the device-pixel widths

Findings for `docs/doperpowers/specs/2026-09-03-w13-body-depth-ramp.md`.

## g0/ — the instrument and the measurement (spike; findings, not the spec)

| file | what it is |
| --- | --- |
| `w13lib.py` | the instrument: W12 G0's line model with one heavy share per 4 CSS px depth window, the lens pinned at `main`'s landed law. Imports `w12lib`/`g3lib`/`w11lib` by path. |
| `g0_selftest.py` | the plate self-test and the estimator on a synthetic known k(u) |
| `g0_validate.py` | contract X4: the recovery of vitrea's own uniform share, `main` and the candidate |
| `g0_ramp.py` | the reference's k(u) per span and scale; H1 against H2; the heavy width per span |
| `g0_smallspan.py` | the heavy width on the small spans, `g3lib.fit_two_joint` over the pitches |
| `g0_impulse.py` | the impulse cells: the dot's peak contrast, the radial profiles, the interior levels |
| `g0_freet.py` | the addendum: the same fit with the transmission free per depth window — does t ramp, or only the mix? |
| `g0_band.py` | an independent replica of contract X6's band / interior rows, agreeing with the landed ones (`x6-baseline.md`, claims §5.60) to 0.0015 |
| `g0-instrument.md` | **the validation** — what the instrument recovers from a known law, and what it cannot |
| `g0-ramp.md` | **the readings** — the ramp, the widths, the dot, and a draft of claims §5.60 |
| `parts/*.json` | every table the two documents quote |
| `g0-ramp.png`, `g0-ramp-absolute.png`, `g0-impulse.png` | the figures |

`x6-baseline.md`, `x6-baseline.py`, `x6-baseline.sh` and `matrix-x6-baseline.json` are X6's
own landing (claims §5.60), produced beside this spike by the band-rows worker.

Run from `g0/` with the analysis venv
(`/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python g0_*.py`). Everything is analysis of
committed rasters; nothing here captures, and no constant under `packages/*/src` is changed.
