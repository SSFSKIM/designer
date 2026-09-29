"""Dark-active top held-shadow control; conditional, not family-wide exclusion."""
import argparse
from pathlib import Path
import numpy as np
import sys
PRIMARY = Path(__file__).resolve().parent
PROOF = Path('/Users/new/vitrea-w41/pre-w41-proof/packages/calibration/results/2026-09-27-w41-g1-identification/stroke')
sys.path.insert(0, str(PROOF))
import execute
import replay as r
import scoring


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', required=True)
    out = Path(ap.parse_args().out).resolve()
    if PRIMARY not in out.parents:
        raise ValueError('output must be beneath stroke/')
    out.mkdir(exist_ok=False)
    native, wave, reader = r.guarded_reader(('calibration',))
    prep = r.Preparation()
    rows = []
    for (cell, kind), entry in sorted(reader.entries.items()):
        sid = cell.split('/', 1)[1]
        if kind != 'crop' or sid not in reader.allowed or not entry['admitted']:
            continue
        if '-dark-' not in cell or sid.endswith('__inactive'):
            continue
        if wave.scenes[sid]['background'] not in ('g128', 'g255') \
                or native.wave.native_only(wave.component(sid)):
            continue
        runs, states = native.archive.unbundle(reader.read(cell, 'crop'))
        runs = [a for a in runs if a['admitted'] and a['protocol'] == 'normal']
        payloads = {s: native.archive.unpack(states[s]) for s in {a['state'] for a in runs}}
        o = prep.prepare(cell, 'calibration', [payloads[a['state']] for a in runs],
                         [a['state'] for a in runs], wave.scenes[sid]['background'])
        prediction = np.concatenate([p['compact'].mean_b-p['amplitude']*p['compact'].mean_bfall
                                     for p in o['parts']])
        for row in scoring.bin_rows(o, prediction, {}, shadow_only=True):
            if row['darkTopControl']:
                row['classification'] = 'conditional held-shadow control; free gamma can paint here; '
                row['classification'] += 'not a coefficient-independent support certificate'
                rows.append(row)
    execute.gzip_rows(out/'bins.jsonl.gz', lambda emit: [emit(row) for row in rows])
    execute.json_write(out/'summary.json', dict(summary=scoring.summarize(rows),
        coefficientIndependent=False, nativeFits=0,
        strata={f'dark-active/{scale}x': scoring.summarize(row for row in rows if row['scale'] == scale)
                for scale in (1, 2)}))


if __name__ == '__main__':
    main()
