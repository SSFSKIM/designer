#!/usr/bin/env python3.12
"""Produce role-separated repeat evidence and replay it without raw PNGs (§5.174).

A producer may see holdout. It returns only the declared inventory, content
hashes and admission. States, frequencies and numerical diagnostics are inside
the cell's guarded role directory; the public file count does not reveal how
many byte-states a holdout cell returned.
"""
import base64
import copy
import gzip
import hashlib
import json
from pathlib import Path
import numpy as np
import instrument as I


def encode(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()


def produce(records,wave,root):
    root=Path(root)
    if root.exists():raise ValueError('archive output already exists; do not rewrite recorded evidence')
    root.mkdir(parents=True)
    inventory=[]
    for cell in sorted({r['cell'] for r in records}):
        if cell not in wave.cells:raise ValueError('undeclared archive cell')
        role=wave.roles[cell.split('/',1)[1]]
        rows=[r for r in records if r['cell']==cell]
        admitted=[r for r in rows if r['admitted']]
        alignment=(admitted or rows)[0]['payload'].get('alignment')
        states={};mapping=[];statistics=[]
        for r in rows:
            payload=copy.deepcopy(r['payload'])
            # Registration must not remove run-to-run movement from the bar.
            # One cell's masks stay fixed; every raw alignment fit remains in
            # the run mapping as a diagnostic, never as per-run registration.
            payload['alignment']=alignment
            raw=I.pack(payload);state=sha(raw)
            states[state]=base64.b64encode(raw).decode()
            run=dict(run=r['run'],protocol=r.get('protocol','normal'),state=state,admitted=r['admitted'],inputHashes=r['inputHashes'],
                     alignmentFit=r['payload'].get('alignment'))
            mapping.append(run)
            statistics.append({**run,'statistics':I.analyse(payload)})
        bundles={'crop':gzip.compress(encode(dict(schema=1,states=states,runs=mapping)),mtime=0),
                 'statistics':encode(dict(schema=1,runs=statistics))}
        for kind,raw in bundles.items():
            path=f'{role}/{sha(cell.encode())}.{kind}'+('.json.gz' if kind=='crop' else '.json')
            dest=root/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
            inventory.append(dict(cell=cell,kind=kind,path=path,sha256=sha(raw),admitted=bool(admitted)))
    output=dict(schema=1,scenesSha256=wave.scenes_sha,splitSha256=wave.split_sha,
                sourceManifests=sorted({r['inputHashes']['manifest'] for r in records if 'manifest' in r['inputHashes']}),entries=inventory,
                disclosure='Inventory, hashes and admission only; analytical payload is role-separated.')
    (root/'inventory.json').write_bytes(encode(output))
    return output


def replay(reader,cell):
    crop=json.loads(gzip.decompress(reader.read(cell,'crop')))
    recorded=json.loads(reader.read(cell,'statistics'))
    output=[]
    for row in crop['runs']:
        raw=base64.b64decode(crop['states'][row['state']])
        if sha(raw)!=row['state']:raise ValueError('state digest mismatch')
        output.append({**row,'statistics':I.analyse(I.unpack(raw))})
    if output!=recorded['runs']:raise ValueError('raw/archive instrument outputs differ')
    return dict(cell=cell,runs=len(output),identical=True)


def repeat_bar(reader,cell,protocol=None):
    crop=json.loads(gzip.decompress(reader.read(cell,'crop')))
    rows=[r for r in crop['runs'] if r['admitted'] and (protocol is None or r['protocol']==protocol)]
    if len({r['protocol'] for r in rows})>1:
        return dict(cell=cell,status='protocols are separate strata; choose one',protocols=sorted({r['protocol'] for r in rows}))
    if len(rows)<2:return dict(cell=cell,status='insufficient admitted repeats',runs=len(rows))
    states={k:I.unpack(base64.b64decode(v)) for k,v in crop['states'].items()}
    reference=states[rows[0]['state']]
    h,w=reference['rgb'].shape[:2]
    d,nx,ny,arc=I.geometry(w,h,reference['component'],reference['scale'],
                          reference['alignment']['translationDevicePx'])
    bins=[]
    for (part,shell,angle),mask in I.strata(d,nx,ny,arc):
        images=[states[r['state']]['rgb'][mask] for r in rows]
        bins.append(dict(part=part,shell=shell,bin=angle,pixels=int(mask.sum()),
                         admissible=int(mask.sum())>=4,barRGB=I.pairwise_bar(images)))
    return dict(cell=cell,protocol=protocol,status='measured observed envelope, not population noise guarantee',
                runs=len(rows),distinctStates=len({r['state'] for r in rows}),bins=bins)
