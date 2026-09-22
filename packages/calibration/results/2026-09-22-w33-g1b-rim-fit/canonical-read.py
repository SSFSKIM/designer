#!/usr/bin/env python3.12
"""The sealed W33 read, one artifact for holdout, X6 before every browser (§5.172).

Calibration/validation and holdout are selected by the manifest's declared sets.
The probe pass is W32's 55-scene ladder, unchanged. The accidental widening of
the initial scratch reproduction is not a canonical read-set decision.
A pass writes an exclusive start artifact before capturing and cannot be rerun.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE=Path(__file__).resolve().parent
CAL=HERE.parent.parent


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m
    spec.loader.exec_module(m)
    return m


def main():
    p=argparse.ArgumentParser()
    p.add_argument('mode',choices=('calibration,validation','ladder','holdout'))
    a=p.parse_args()
    sealed=json.loads((HERE/'sealed-manifest.json').read_text())
    for name,entry in sealed['documents'].items():
        assert hashlib.sha256((CAL/'profiles'/name).read_bytes()).hexdigest()==entry['fileSha256']
    configuration=load('w33_configuration',CAL/'results/holdout-configuration/configuration.py')
    assert configuration.document_hashes()=={n:e['fileSha256'] for n,e in sealed['documents'].items()}
    reads=configuration.load_log()
    assert reads[-1]['claims']=='c9a §5.172'
    assert reads[-1]['documents']==configuration.document_hashes()
    assert reads[-1]['sourceSha256']==configuration.source_hash()[0]
    # The seal must carry the configuration record in git, not merely on disk.
    logpath='packages/calibration/results/holdout-configuration/configuration-log.json'
    committed=subprocess.check_output(['git','show','HEAD:'+logpath],cwd=CAL)
    assert json.loads(committed)['reads'][-1]==reads[-1]
    marker=HERE/('read-'+a.mode.replace(',','-')+'-started.json')
    with marker.open('x') as f:
        json.dump(dict(mode=a.mode,at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                       configuration=reads[-1]),f,indent=2)
        f.write('\n')
    profiles=[
        'apple-macos-27.0-1x-light-standard-glass0.5',
        'apple-macos-27.0-2x-light-standard-glass0.5',
        'apple-macos-27.0-1x-dark-standard-glass0.5',
        'apple-macos-27.0-2x-dark-standard-glass0.5',
        'apple-macos-27.0-1x-light-reduced-transparency-glass0.5',
        'apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5']
    laddertext=(CAL/'results/2026-09-21-w32-g1-shadow-fit/ladder.sh').read_text()
    ladder=re.search(r'LADDER_45="([^"]+)"',laddertext)[1]+','+re.search(r'LADDER_W32="([^"]+)"',laddertext)[1]
    assert len(ladder.split(','))==55
    jobs=([(profile,'webgpu') for profile in profiles[:4]]+
          [(profiles[0],'css'),(profiles[2],'css')]) if a.mode=='ladder' else [
          (profile,renderer) for profile in profiles for renderer in ('webgpu','css')]
    x6=load('w33_capture',HERE/'render-bed.py').x6
    for profile,renderer in jobs:
        scheme='dark' if '-dark-' in profile else 'light'
        doc=Path('profiles')/f'apple-macos-27.0-1x-{scheme}-standard-glass0.5.json'
        receded=doc.with_name(doc.stem+'-receded.json')
        x6(f'canonical/{a.mode}/{profile}/{renderer}')
        cmd=['npx','tsx','cli/compare.ts','--profile',profile,'--renderer',renderer,
             '--material-profile',str(doc),'--receded-profile',str(receded),
             '--alpha','--write-partial','--set','probe' if a.mode=='ladder' else a.mode]
        if a.mode=='ladder': cmd+=['--scene',ladder]
        subprocess.run(cmd,cwd=CAL,env=dict(os.environ,VITREA_WEB_CAPTURES=str(CAL/'web-captures')),check=True)
    with (HERE/('read-'+a.mode.replace(',','-')+'-completed.txt')).open('x') as f:
        f.write(datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n')


if __name__=='__main__': main()
