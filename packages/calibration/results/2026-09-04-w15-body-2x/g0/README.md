# W15 G0 — the 2x body, its instruments, and how to re-run them

The findings are `g0-2x.md`; every table it quotes is `g0-tables.md`, formatted from
`parts/*.json` by `g0_tables.py` so the document and the JSON cannot drift.

## What is here

| file | what it does |
| --- | --- |
| `w15lib.py` | the driver's vocabulary over W13 G0's instrument: widths in device px, the share bounded to [0, 1], a read-off that names the deep value and two reach statistics |
| `g0a_width.py` | (a) the base width at 2x swept 8–16 device px, solved free and bounded at every width → `parts/g0a-width.json` |
| `g0b_depth.py` | (b) the sharp share by depth at the settled widths, and the pooled width surface → `parts/g0b-depth.json` |
| `g0c_recovery.py` | (c) contract X4: vitrea's own 2x law, its widths, and a synthetic 2x ramp → `parts/g0c-recovery.json` |
| `g0d_css.py` | (d) the CSS tier's 2x ceiling, what the tier draws, and (b)'s law projected → `parts/g0d-css.json` |
| `g0_tables.py` | every part rendered as `g0-tables.md` |

(e), the 1x golden, is not analysis and lives in the product: `renderer-webgpu/e2e/fixtures/
scenes.ts` (`body-ramp-1x`), its golden PNG, and `W15_HASHES` in `e2e/golden/isolation.spec.ts`
— committed on its own as `b913c1b`.

## Running them

The analysis venv needs numpy, scipy and Pillow. Everything reads committed rasters — the 2x
probe bed (`results/2026-09-03-w12-lens/probe-2x/`), the harness's backgrounds and vitrea's
own `web-captures/` — and writes only into this directory. **No capture is taken and no
scene server is started.**

```bash
cd packages/calibration/results/2026-09-04-w15-body-2x/g0
python g0a_width.py      # ~1 min
python g0b_depth.py      # ~30 s
python g0c_recovery.py   # ~20 s
python g0d_css.py        # ~1 s; also runs `node -e` against packages/platform-web/dist,
                         # so `pnpm --filter @vitreajs/vitrea-web build` first
python g0_tables.py
```

`g0b_depth.py` must run before `g0d_css.py`: the projection column reads (b)'s own profile.
