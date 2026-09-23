#!/usr/bin/env python3.12
"""One frozen W34 identification exposure, called only by G0 wave.py (§5.176)."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import identification as M
import forward as F
import browser
import fast


def dependencies(document):
    for name,sha in document['inventories'].items():
        path=M.W.ROOT/name
        if M.W.committed(path)!=sha or hashlib.sha256(path.read_bytes()).hexdigest()!=sha:
            raise RuntimeError('Frozen inventory moved: '+name)
    for name,sha in document['dependencies'].items():
        path=HERE/name
        if hashlib.sha256(path.read_bytes()).hexdigest()!=sha:
            raise RuntimeError('Frozen dependency moved: '+name)
        if M.W.committed(path)!=sha:
            raise RuntimeError('Uncommitted analysis dependency: '+name)


def capture(wave,token):
    ids=wave.launch_scenes(['holdout'],token)
    env={**os.environ,'VITREA_SCENES':str(wave.scenes_path),'VITREA_FIXTURES':str(M.G1/'probe')}
    for profile in wave.spec['profiles']:
        key=profile['key'];scheme='dark' if '-dark-' in key else 'light';scale='1' if '-1x-' in key else '2'
        command=['pnpm','--dir',str(M.W.ROOT),'--filter','@vitrea/calibration','exec','tsx',
                 'scripts/capture-web.ts',*ids,'--renderer','webgpu','--color-scheme',scheme,
                 '--scale',scale,'--out',str(HERE/'web-captures'/key)]
        log=HERE/('holdout-browser-'+key+'.txt')
        if log.exists():raise RuntimeError('Holdout browser output already exists')
        browser.preflight('receipt holdout '+key)
        with log.open('w') as f:
            result=subprocess.run(command,env=env,stdout=f,stderr=subprocess.STDOUT)
        with (HERE/'browser-runs.txt').open('a') as f:
            f.write(json.dumps(dict(holdout=True,profile=key,exitCode=result.returncode,
                                   scenes=len(ids),command=command))+'\n')
        if result.returncode:raise RuntimeError('Holdout browser capture failed; receipt remains spent')


def main(wave,token):
    document=token.configuration['candidate']['document'];dependencies(document)
    fast.activate()
    records,controls=M.extract(wave,['holdout'],token)
    M.instrument_tables(records,controls,'holdout-native')
    capture(wave,token)
    spec=importlib.util.spec_from_file_location('webgap',HERE/'web-gap.py')
    webgap=importlib.util.module_from_spec(spec);spec.loader.exec_module(webgap)
    webgap.run(records,'holdout-web')
    for r in records:
        if r['cov'] is not None and r['backgroundKind'] in ['solid','linear-gradient']:
            r['exactBaselines']={space:F.baseline(r,space,r['alignment']['translationDevicePx'],cov=r['cov'])[0]
                                 for space in ['encoded','linear']}
    tables=[];headlines=[];physical=[];physical_indices={}
    for index,entry in enumerate(document['candidates']):
        fit=entry['fit']
        rs=[r for r in records if (r['profile'],r['pose'])==(fit['profile'],fit['pose'])]
        if fit['spec']['stage']!='W33-first':rs=[r for r in rs if r['cov'] is not None]
        if fit['spec'].get('exactBody'):
            rs=[r for r in rs if r['backgroundKind'] in ['solid','linear-gradient']]
            physical_indices[len(physical)]=index
            physical.append(fit)
        per={}
        for source in rs:
            r=source.copy()
            if entry['comparator']=='web':
                profile,sid=r['cell'].split('/',1)
                web=np.asarray(Image.open(HERE/'web-captures'/profile/sid/(sid+'__webgpu.png')).convert('RGB'),float)
                r['D']=web[r['xy'][:,1],r['xy'][:,0]]
            pred=M.predict(r,fit['spec'],fit['coefficients'])
            uncertainty=np.zeros_like(pred)
            if fit['spec'].get('exactBody'):
                uncertainty=r['cov']['body'][:,None]*np.array(r['body']['uncertaintyRGB'])+.5
            for key,mask in r['masks']:
                row=dict(candidate=index,selection=entry['selection'],cell=r['cell'],part=key[0],shell=key[1],bin=key[2],
                         **M.bin_residual(r['n'][mask],pred[mask],uncertainty[mask],r['bar'][key]['barRGB']))
                tables.append(row);per.setdefault(key[0],[]).append(row)
        for part,rows in per.items():
            admitted=[r for r in rows if r['admissible']]
            headlines.append(dict(candidate=index,selection=entry['selection'],profile=fit['profile'],pose=fit['pose'],
                part=part,cells=len(rs),bins=len(admitted),pixels=sum(r['pixels'] for r in admitted),
                underpopulated=len(rows)-len(admitted),worstMAE=max(max(r['maeRGB']) for r in admitted),
                maxBar=max(max(r['barRGB']) for r in admitted),
                maxTolerance=max(max(r['tauRGB']) for r in admitted),
                pointClosure=all(r['status']=='point compatible' for r in admitted),
                failedBins=sum(r['status']=='point fails' for r in admitted)))
    M.save(HERE/'holdout-residuals.json.gz',tables)
    M.save(HERE/'holdout-result.json',dict(candidateSha256=token.configuration['candidate']['sha256'],
        cells=len(records),headlines=headlines,refit=False,
        note='One receipt exposure; only frozen validation nominees, no coefficient adjustment.'))
    M.save(HERE/'holdout-qualified-candidate-map.json',physical_indices)
    F.verify(records,physical,'holdout-qualified')


if __name__=='__main__':
    if 'W34_WAVE' not in globals() or 'W34_AUTHORIZATION' not in globals():
        raise RuntimeError('Run only through G0 wave.py expose; no standalone holdout reader')
    main(W34_WAVE,W34_AUTHORIZATION)
