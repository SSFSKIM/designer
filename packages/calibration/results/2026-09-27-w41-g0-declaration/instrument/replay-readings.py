"""Reproduce copied calibration readings from verified archive; no optimizer.

The guarded reader is the only payload accessor. All of ~/vitrea-w39 is denied.
Validation/holdout is refused even if the caller names a different fixture root.
"""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import instrument as m

sys.path.insert(0,str(m.G2))
import native
root=Path((m.E/'archive-root.txt').read_text().strip())
w,r=native.guarded(root,('calibration',))
pins=json.loads((m.E/'pins.json').read_text())
assert r.generation==pins['archive']['inventorySha256']
source=json.loads((m.E/'readings/body/readings.json').read_text())
stroke=json.loads(gzip.decompress((m.E/'readings/stroke/reading.json.gz').read_bytes()))
by_cell={}
for row in stroke['rows']:by_cell.setdefault(row['cell'],[]).append(row)
body={row['cell']:row for row in source['rows']}
grad={row['cell']:row for row in source['gradients']}
checked=0;strips=[];pixels_checked=0
for cell in sorted(by_cell):
    sid=cell.split('/',1)[1]
    assert w.roles[sid]=='calibration'
    records=[v for v in native.archive.recorded_statistics(r,cell) if v['admitted'] and v['protocol']=='normal']
    assert len(records)==7
    stats=[v['statistics'] for v in records]
    for old in by_cell[cell]:
        rows=[s['members'][old['member']] for s in stats]
        ix=next(i for i,b in enumerate(rows[0]['bins']) if (b['part'],b['side'],b['bin'],b['shell'])==(old['part'],old['side'],old['bin'],old['shell']))
        values=np.array([v['bins'][ix]['meanRGB'] for v in rows]);refs=np.array([v['noGlassBins'][ix]['meanRGB'] for v in rows])
        for name,value in [('native',np.median(values,0)),('backgroundRGB',np.median(refs,0)),('delta',np.median(values-refs,0)),('bar',.5+.5*np.ptp(values-refs,axis=0))]:
            np.testing.assert_array_equal(value,old[name])
        assert rows[0]['bins'][ix]['pixels']==old['pixels']
        checked+=1
    if cell in body or cell in grad:
        runs,states=native.archive.unbundle(r.read(cell,'crop'))
        runs=[v for v in runs if v['admitted'] and v['protocol']=='normal'];assert len(runs)==7
        payloads={v:native.archive.unpack(states[v]) for v in {run['state'] for run in runs}}
        p=payloads[runs[0]['state']];sh=m.readers.shapes_of(p['component']);geo=m.readers.geometry(p['rgb'].shape[:2],sh,p['scale'])
        if cell in body:
            vals=np.array([m.readers.deep_body(payloads[run['state']]['rgb'],geo)['medianRGB'] for run in runs])
            np.testing.assert_array_equal(vals,body[cell]['runs'])
            np.testing.assert_array_equal(np.median(vals,0),body[cell]['median'])
            pixels_checked+=1
        else:
            rgb=np.array([payloads[v['state']]['rgb'] for v in runs]);bg=np.array([payloads[v['state']]['noGlass'] for v in runs])
            strip=m.gradient_strip(rgb,bg,sh[0],p['scale'])
            old=grad[cell]
            np.testing.assert_array_equal(strip['memoRowMean'],old['median'])
            np.testing.assert_array_equal(strip['memoReferenceMean'],old['reference'])
            delta=float(np.max(abs(np.array(strip['native'])-np.array(old['median']))))
            strips.append(dict(cell=cell,scale=p['scale'],rows=len(strip['yCSS']),pixelsPerRow=strip['pixelsPerRow'],memoRowMeansIdentical=True,declaredMedianVsMemoMeanMaximumCodes=delta,referenceRange=[float(np.min(strip['reference'])),float(np.max(strip['reference']))]))
report=dict(schema='w41-readings-replay-1',archiveInventory=r.generation,roles=['calibration'],rawRootDenied=str(Path.home()/'vitrea-w39'),nativeFits=0,calibrationCells=len(by_cell),strokeBinsExactlyReproduced=checked,deepCellsFromPixelsExactlyReproduced=pixels_checked,gradientCellsExactlyReproduced=len(strips),strips=strips,
 sources={str(p.relative_to(m.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(m.__file__),m.G0/'w39_readers.py',m.G0/'wave.py']})
print(json.dumps(report,indent=2,allow_nan=False))
