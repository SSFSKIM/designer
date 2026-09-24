"""Referee the read after the split, reconstructing both immutable inputs (§5.179)."""
import hashlib,importlib.util,json,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];CAL=HERE.parent.parent

def load(name,file):
    spec=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
split=load('split_append',HERE.parent/'2026-09-22-w33-g1b-rim-fit/append-check.py');read=load('read_append',HERE/'read-append-check.py')
manifest=json.loads((HERE/'before-manifest.json').read_text());rows=manifest['rows'];placed=[None]*len(rows)
shape=None
for dest in sorted({r['destination'] for r in rows}):
    raw,blobs,prefix,sep,suffix=split.slices_of(CAL/dest)
    if dest=='results/matrix.json':shape=(prefix,sep,suffix)
    selected=[r for r in rows if r['destination']==dest];assert len(selected)==len(blobs)
    for r,blob in zip(selected,blobs):placed[r['index']]=blob
reconstructed=shape[0]+shape[1].join(placed)+shape[2]
assert hashlib.sha256(reconstructed).hexdigest()==manifest['matrixSha256']
before=subprocess.check_output(['git','-C',str(ROOT),'show','2f49d390:packages/calibration/results/matrix.json'])
assert hashlib.sha256(before).hexdigest()==json.loads((HERE/'before-read.json').read_text())['matrixSha256']
with tempfile.TemporaryDirectory(prefix='w36-append-',dir=Path.home()/'vitrea-w36/scratch') as d:
    d=Path(d);(d/'before.json').write_bytes(before);(d/'read.json').write_bytes(reconstructed)
    read.snapshot(d/'before.json');read.MATRIX=d/'read.json';raise SystemExit(read.verify(HERE/'read-append-check.json'))
