#!/usr/bin/env python3.12
"""Proposal P2, before the hash: would W42's P1 pitch-32 checker on rrect-64 resolve the ratio in every endpoint?

    python3.12 -B proposal_p2.py      # writes proposal-p2.txt

`bp-p1-c32-rrect-64` is a W42 calibration cell captured in all four 2x passes (so it has its seven-run 0.5
counterpart, X46). rrect-64 sits in the t = 0 stratum with the capsule (memo D: nothing moves for s <= 64), so
its T is the capsule greys'; in the active pose its narrow term has zero width, and its 0 / 255 levels give the
largest excursion the bed can carry. Read exactly as rehearsal 3 reads the probe's own cells.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rehearse as RH  # noqa: E402
import wtest as W  # noqa: E402
import w42frames as O  # noqa: E402

CID = 'bp-p1-c32-rrect-64'


def main():
    probe_cache = O.SCRATCH
    extra = O.SCRATCH.parent / 'observed-0.5-p2'
    O.SCRATCH = extra
    O.extract([(s, st, CID) for s in ('light', 'dark') for st in ('rest', 'inactive')])
    lines = [f'Proposal P2: {CID} under the declared support rule and rehearsal 3\'s conditioning', '']
    for ep in W.ENDPOINTS:
        scheme, pose = ep.split('-')
        O.SCRATCH = probe_cache
        greys, _ = RH.endpoint_cells(ep)
        T50 = RH.grey_tables(ep, {cid: O.observed(scheme, pose, cid)[0] for cid in greys})
        O.SCRATCH = extra
        regs, _ = W.side_regions(ep, CID)
        g = regs['free']
        if g['pixels'] < W.MIN_PX:
            lines.append(f'{ep:15s} free {g["pixels"]} px: excluded')
            continue
        img, _ = O.observed(scheme, pose, CID)
        inv50, y, q50 = RH.region_reading('median', T50[0], img, g['idx'])
        pred = [g['level'] + 0.5 * (m - g['level']) for m in inv50['Mc']]
        p25 = W.invert(T50[0], [T50[0][ch](pred[ch]) for ch in range(3)])
        rr = W.ratio(g['level'], p25, inv50)
        lines.append(f"{ep:15s} free C {g['level']:5.1f} {g['pixels']:5d} px  y50 {y}  D {rr['D']:+6.1f}  "
                     f"predicted dr {rr['dr']:.3f}{'  SUPPORTED' if rr['dr'] <= W.DR_MAX else ''}")
    (HERE / 'proposal-p2.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
