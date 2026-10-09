"""Central candidate-domain, numerical-provenance and capture-receipt admission.

The existing G0 numerical referee is reused unchanged. These additional checks bind it
to this invocation's complete cohort and to original, source-pinned material endpoints.
No current-material capture is relabelled as a live-chart numerical PASS.
"""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re

CHART = {'lowEndStrength', 'lowEnd44', 'lowEnd96', 'lowEnd160'}
SLOTS = {'active.light', 'active.dark', 'receded.light', 'receded.dark'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def checked(repo, pin):
    if not isinstance(pin, dict) or not isinstance(pin.get('path'), str):
        raise ValueError('Missing admission content pin')
    path=(repo/pin['path']).resolve()
    if not path.is_relative_to(repo) or not path.is_file() or sha(path)!=pin.get('sha256'):
        raise ValueError('Changed admission content pin')
    return path


def endpoints(doc, item, current=False):
    repo=Path(doc['repo']); path=checked(repo,item); candidate=load(path)
    position=candidate.get('glassTintAmount')
    if (candidate.get('kind')!='vitrea-candidate-material-document' or candidate.get('schemaVersion')!=1 or
            position not in (.25,.5) or set(candidate.get('endpoints',{}))!=SLOTS):
        raise ValueError('Incomplete or wrong-position candidate document')
    part_path=checked(repo,doc['partTwo']); original_pins={p['path']:p for p in load(part_path)['sources']}
    profiles=part_path.parent.parent.parent/'profiles'
    patches={}
    for slot,pin in candidate['endpoints'].items():
        pose,scheme=slot.split('.'); suffix='-receded' if pose=='receded' else ''
        source=profiles/f'apple-macos-27.0-1x-{scheme}-standard-glass{position}{suffix}.json'
        relative=str(source.relative_to(repo))
        if relative not in original_pins: raise ValueError('Original endpoint absent from immutable G0 sources')
        original=load(checked(repo,original_pins[relative]))
        endpoint_path=(path.parent/pin['path']).resolve()
        endpoint=load(checked(repo,{'path':str(endpoint_path.relative_to(repo)),'sha256':pin['sha256']}))
        key=endpoint.get('profileKey','')
        match=re.fullmatch(r'apple-macos-27\.0-1x-'+scheme+r'-standard-glass([0-9]+(?:\.[0-9]+)?)'+suffix,key)
        if not match or float(match[1])!=position or match[1]==str(position):
            raise ValueError('Candidate endpoint identity differs from declared slot')
        patch=endpoint.get('patch'); before=original.get('patch')
        if not isinstance(patch,dict) or not isinstance(before,dict):
            raise ValueError('Missing complete endpoint patch')
        strip=lambda p:{k:v for k,v in p.items() if k not in CHART}
        if ((current or scheme=='light') and patch!=before) or strip(patch)!=strip(before):
            raise ValueError('Candidate changes held material leaves')
        if endpoint.get('cssTierMapping')!=original.get('cssTierMapping'):
            raise ValueError('Candidate changes held CSS mapping')
        patches[slot]=patch
    for pose in ('active','receded'):
        resolved={**patches['active.dark'],**(patches['receded.dark'] if pose=='receded' else {})}
        if current:
            if resolved.get('lowEndStrength',0)!=0: raise ValueError('Current baseline is not gate0')
        else:
            if type(resolved.get('lowEndStrength')) not in (int,float) or resolved['lowEndStrength']!=1:
                raise ValueError('Live candidate requires numeric strength1')
            for name in ('lowEnd44','lowEnd96','lowEnd160'):
                row=resolved.get(name)
                if not isinstance(row,list) or len(row)!=4 or any(
                        type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=1 for v in row) or row!=sorted(row):
                    raise ValueError('Candidate chart rows require four finite nondecreasing ordinates')
    return position


def validate_cohort(doc, cohort, current=False):
    positions=[endpoints(doc,p,current) for p in cohort]
    if len(positions)!=len(set(positions)) or (not current and sorted(positions)!=[.25,.5]):
        raise ValueError('Live cohort must contain both positions exactly once')
    return {p['sha256']:position for p,position in zip(cohort,positions)}


def validate_numerical(doc, batch):
    repo=Path(doc['repo']); wanted=sorted(p['sha256'] for p in batch['cohort'])
    proof_pins=[r.get('numericalReferee') for r in batch['runs']]
    if not proof_pins or any(p!=proof_pins[0] for p in proof_pins):
        raise ValueError('Every run must bind the same complete numerical admission')
    proof_path=checked(repo,proof_pins[0]); report=load(proof_path)
    if report.get('candidateSha256s')!=wanted or sorted(
            (p.get('path'),p.get('sha256')) for p in report.get('candidateDocuments',[]))!=sorted(
            (p['path'],p['sha256']) for p in batch['cohort']):
        raise ValueError('Numerical admission cohort differs from complete invocation cohort')
    g0=checked(repo,doc['partTwo']).parent
    path=g0/'audit/runner.py'
    expected=doc['closure']['sources']
    for name in ('runner.py','numerical_guard.py'):
        source=g0/'audit'/name
        if expected.get(str(source.relative_to(repo)))!=sha(source):
            raise ValueError('G0 numerical referee is not in the prospective source closure')
    spec=importlib.util.spec_from_file_location('w50_g1_original_numerical_runner',path)
    runner=importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(),str(path),'exec'),runner.__dict__)
    for digest in wanted: runner.validate_numerical_referee(report,digest,repo)
    return proof_pins[0]


def validate_captures(batch, captures, output):
    """A claimed hash in a summary is insufficient: every declared draw needs pinned artifacts."""
    if not isinstance(captures,dict) or captures.get('status')!='CAPTURED' or captures.get('candidateSha256s')!=sorted(
            p['sha256'] for p in batch['cohort']):
        raise ValueError('Capture report does not name the complete selected cohort')
    expected=set()
    for run in batch['runs']:
        lane='current' if batch['phase']=='current' else 'candidate'
        for scene in run['scenes']:
            expected.add((run['profile'],run['renderer'],scene,run['candidate']['path'],run['candidate']['sha256'],lane))
            if batch['phase']=='exposure' and run.get('baselineCandidate'):
                p=run['baselineCandidate']; expected.add((run['profile'],run['renderer'],scene,p['path'],p['sha256'],'current'))
    rows=captures.get('captures',[]); actual=[]; bound=[]
    for row in rows:
        p=row.get('candidate',{})
        identity=(row.get('profile'),row.get('renderer'),row.get('scene'),p.get('path'),p.get('sha256'),row.get('lane'))
        if identity not in expected: raise ValueError('Falsely reported or out-of-batch capture member')
        actual.append(identity)
        for name in ('cell','report','png'):
            item=row.get('artifacts',{}).get(name)
            if not isinstance(item,dict): raise ValueError('Capture lacks pinned cell/report/PNG artifacts')
            path=Path(item.get('path','')).resolve()
            if not path.is_relative_to(Path(output).resolve()) or not path.is_file() or sha(path)!=item.get('sha256'):
                raise ValueError('Capture artifact missing, changed or outside invocation output')
            bound.append({'path':str(path),'sha256':item['sha256']})
        report=load(row['artifacts']['report']['path'])
        metadata=load(row['artifacts']['cell']['path'])
        page=report.get('page',{}); scale=re.search(r'-([12])x-',row['profile'])
        if (not scale or page.get('sceneId')!=row['scene'] or page.get('requestedRenderer')!=row['renderer'] or
                page.get('devicePixelRatio')!=int(scale[1])):
            raise ValueError('Captured artifact scene/tier/scale differs from reported member')
        if page.get('candidateDocument',{}).get('declarationSha256')!=p['sha256'][:12] or \
                f'declarationSha256={p["sha256"][:12]}' not in metadata.get('capturePath',''):
            raise ValueError('Captured artifact material differs from reported cohort member')
    if len(actual)!=len(expected) or set(actual)!=expected:
        raise ValueError('Capture population does not cover the full declared cohort and membership')
    return {'members':[list(k) for k in sorted(expected)],'artifacts':bound}
