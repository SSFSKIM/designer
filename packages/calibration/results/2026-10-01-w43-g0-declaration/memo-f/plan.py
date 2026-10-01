#!/usr/bin/env python3.12
"""W43 G0 (c): memo F's declared plan, written before the window (charter clause 2; Design "Memo F").

    python3.12 -B plan.py            # writes plan.json beside this file and prints the estimate

Memo F reads Apple's declared glass configuration through the W39 side bundle's `dump-layers`
at nine slider positions, the way W42's memo D read it at one. It captures no pixel and needs no
grant. This file fixes, before any launch, everything the driver (`memo-f.sh`) does:

- **The positions, in priority order.** A window that is cut short keeps the blocks that matter
  most. 0.5 first: it must reproduce memo D field for field (`dump-reference.json`), which is
  the control that the machine, the bundle and the fresh-launch rule still read what memo D
  read. Then 0.25 (the generation's position and the w-test's prediction), the ladder's ends 1
  and 0, its third position 0.75, the four eighths, and last the 1x arm at 0.25, the only block
  that needs the display at mode 69.
- **The scenes.** Six shapes on dark-solid spanning memo D's span strata, s = 44, 64, 80, 96,
  128 and 160 (t = 0, 0, 1/6, 1/3, 2/3, 1; rrect-lg is also the 0.25 backdrop-scale step),
  which are also every shape the w-test reads (capsule, rrect-64, rrect-80, rrect-md). They are
  canonical `__rest` ids posed by `--require-key` or `--inactive`, as memo D posed them, so the
  0.5 block is memo D's own scene set. At 0.25, 0 and 1 the block adds rrect-md on photo and on
  the checkerboard: memo D found no declared input that depends on the backdrop at 0.5, and these
  two rows say whether that still holds at the generation's position and the ladder's ends.
- **The four endpoints per block,** light active, light receded, dark active, dark receded: one
  fresh launch each, after the block's one slider write.
- **The scenes file** is canonical `scenes.json` version 7 at the commit named here, pinned by
  SHA-256 (memo D's canonical `2f457782…`), copied into the run root so nothing in a checkout
  is read by the harness and nothing changes under a run.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCENES_COMMIT = '6cb112d50ecc929cfdc7f59953c14bfec02c1c16'
SCENES_SHA256 = '2f45778283443a45d562befa634fc7681de9ea6e2568bca0d08d659a27393d6f'
SHAPES = ('capsule-button', 'rrect-64', 'rrect-80', 'rrect-md', 'rrect-ml', 'rrect-lg')
SPANS = {'capsule-button': 44, 'rrect-64': 64, 'rrect-80': 80, 'rrect-md': 96, 'rrect-ml': 128, 'rrect-lg': 160}
BACKDROP_CONTROLS = ('photo__rrect-md__rest', 'checkerboard__rrect-md__rest')
ENDPOINTS = (('light', 'active'), ('light', 'inactive'), ('dark', 'active'), ('dark', 'inactive'))
ORDER = ((0.5, 2), (0.25, 2), (1.0, 2), (0.0, 2), (0.75, 2), (0.125, 2), (0.375, 2), (0.625, 2), (0.875, 2),
         (0.25, 1))
WITH_BACKDROP_CONTROLS = {(0.25, 2), (1.0, 2), (0.0, 2)}
SETTLE = 8
# W42 G0's model, from memo D's real runs (bed/sitting/timing.txt): 8.131 s per scene at settle 8
# plus 6.23 s per launch. The per-launch gates (two attestations, the bundle pin, the census, the
# check) are priced at 4 s, the slider write and read-back at 1 s a block, and each display
# switch at displayplacer's 6 s settle plus a read.
PER_SCENE, PER_LAUNCH, GATES, WRITE, SWITCH = 8.131, 6.23, 4.0, 1.0, 8.0


def label(x, scale):
    return f'x{x:g}-{scale}x'


def main():
    base = [f'dark-solid__{s}__rest' for s in SHAPES]
    blocks = []
    for x, scale in ORDER:
        scenes = base + (list(BACKDROP_CONTROLS) if (x, scale) in WITH_BACKDROP_CONTROLS else [])
        blocks.append(dict(label=label(x, scale), x=x, scale=scale, mode=68 if scale == 2 else 69,
                           launches=[dict(label=f'{label(x, scale)}-{sc}-{pose}', scheme=sc, pose=pose)
                                     for sc, pose in ENDPOINTS],
                           scenes=scenes))
    launches = sum(len(b['launches']) for b in blocks)
    dumps = sum(len(b['launches']) * len(b['scenes']) for b in blocks)
    switches = 2 * sum(1 for b in blocks if b['mode'] == 69)
    seconds = dumps * PER_SCENE + launches * (PER_LAUNCH + GATES) + len(blocks) * WRITE + switches * SWITCH
    plan = dict(schema='w43-memo-f-plan-1', charter='docs/doperpowers/specs/2026-10-01-w43-glass-0-25-generation.md',
                key=dict(domain='NSGlobalDomain', name='NSGlassTintAmount', type='float'),
                scenesFile=dict(path='apps/reference-apple/scenes.json', commit=SCENES_COMMIT, sha256=SCENES_SHA256),
                settle=SETTLE, spans=SPANS, blocks=blocks,
                totals=dict(blocks=len(blocks), launches=launches, sceneDumps=dumps, displaySwitches=switches),
                estimate=dict(seconds=round(seconds, 1), minutes=round(seconds / 60, 1),
                              model=f'{PER_SCENE} s/scene + {PER_LAUNCH} s/launch (memo D, W42 G0 timing.txt) '
                                    f'+ {GATES} s gates/launch + {WRITE} s/slider write + {SWITCH} s/display switch; '
                                    'idle waits excluded'))
    (HERE / 'plan.json').write_text(json.dumps(plan, indent=1) + '\n')
    print(f"memo F plan: {len(blocks)} blocks, {launches} launches, {dumps} scene dumps, {switches} display switches; "
          f"about {seconds / 60:.1f} min of idle Mac (idle waits excluded)")
    for b in blocks:
        print(f"  {b['label']:10s} mode {b['mode']}  {len(b['scenes'])} scenes x 4 endpoints")


if __name__ == '__main__':
    main()
