"""Archive-only W39 body observations. Admission precedes every payload open."""
import gzip
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
G0=HERE.parent/'2026-09-26-w39-g0-colour-edge-bed'
sys.path.insert(0,str(G0))
import wave
import w39_archive as archive
import w39_readers as readers


def guarded(root,roles):
    w=wave.default_wave()
    spec=importlib.util.spec_from_file_location('w39_replay_guard',G0/'replay-archive.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    guard.deny(Path.home()/'vitrea-w39')
    return w,w.reader(root,roles=roles)

def cell(reader,cell):
    sid=cell.split('/',1)[1]
    runs,states=archive.unbundle(reader.read(cell,'crop'))
    runs=[r for r in runs if r['admitted'] and r['protocol']=='normal']
    if len(runs)!=7:raise ValueError('expected all seven normal repeats')
    saved=json.loads(gzip.decompress(reader.read(cell,'statistics')))['statistics']
    extracted={}
    for sha in sorted({r['state'] for r in runs}):
        p=archive.unpack(states[sha]);shapes=readers.shapes_of(p['component'])
        geo=readers.geometry(p['rgb'].shape[:2],shapes,p['scale'])
        deep=[readers.deep_body(p['rgb'],geo,i) for i in range(len(shapes))]
        assert deep==[m['deep'] for m in saved[sha]['members']]
        extracted[sha]=dict(deep=deep,scale=p['scale'],scheme=p['scheme'],pose=p['pose'])
    example=next(iter(extracted.values()));members=[]
    for i in range(len(example['deep'])):
        ds=[extracted[r['state']]['deep'][i] for r in runs]
        if any(d['status']!='measured' for d in ds):raise ValueError('UNMEASURED deep: '+cell)
        values=np.array([d['medianRGB'] for d in ds]);median=np.median(values,axis=0)
        members.append(dict(medianRGB=median.tolist(),barRGB=(.5+.5*np.ptp(values,axis=0)).tolist(),
            runMediansRGB=values.tolist(),pixels=[d['pixels'] for d in ds],
            minimumRGB=np.min([d['minimumRGB'] for d in ds],axis=0).tolist(),
            maximumRGB=np.max([d['maximumRGB'] for d in ds],axis=0).tolist(),
            censoredChannels=np.flatnonzero((median<=5)|(median>=250)).tolist()))
    return dict(cell=cell,role=reader.wave.roles[sid],scale=example['scale'],scheme=example['scheme'],
        pose=example['pose'],stateMembership=[r['state'] for r in runs],members=members)
