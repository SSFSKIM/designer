"""Additive guard-only source bridge. No native read, capture, freeze or receipt API.

Historical measurements keep their original source witnesses. This instrument
proves the changed execution boundary leaves their inputs and score functions
unchanged, and rechecks public predictions/domain metadata without reopening Apple.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import types

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
G1=HERE.parents[1]
RUNNER=str((G1/'exposure/runner.py').relative_to(ROOT))
OLD_REF='9b6d1bf7d34410927cb75556e0317569dd98c339'
OLD_SHA='02ed44215ca4f273eb698ab9f514173f2c6cbfb89d09b6a12c837ffee9b4aa96'
NEW_SHA='5ae591ad6ea2098613e75dfb6377875314fcc2280d7526bf80e139f206436c08'
CHANGED={'freeze','CaptureRequest','capture_web','_run'}
ADDED={'X6WaitBudget','observe_x6','x6_record','prebegin_x6','prelaunch_x6'}
TOP_ADDITIONS=[
    'import time',
    "X6_SOURCES = ('packages/calibration/results/2026-09-27-w41-g1-identification/x6/observe.py', 'packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/record-machine.py')",
    "x6_spec = importlib.util.spec_from_file_location('w41_exposure_x6', ROOT / X6_SOURCES[0])",
    'x6 = importlib.util.module_from_spec(x6_spec)',
    'x6_spec.loader.exec_module(x6)',
]


def digest(data): return hashlib.sha256(data).hexdigest()


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for data in iter(lambda:stream.read(1024*1024),b''):h.update(data)
    return h.hexdigest()


def local(root,name):
    path=root/name
    if Path(name).is_absolute() or '..' in Path(name).parts or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('non-repository artifact path')
    return path


def git(root,*args):return subprocess.check_output(['git','-C',str(root),*args])


def load(path):return json.loads(Path(path).read_text())


def save(path,value):
    with Path(path).open('x') as stream:
        json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')
        stream.flush();os.fsync(stream.fileno())
    fd=os.open(Path(path).parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)


def function_transition(old,new,changed,added,allowed_top):
    def parts(source):
        tree=ast.parse(source);definitions={};assignments={};top=[]
        for node in tree.body:
            value=ast.dump(node,include_attributes=False)
            if isinstance(node,(ast.FunctionDef,ast.ClassDef)):definitions[node.name]=value
            else:
                top.append(value)
                if isinstance(node,ast.Assign):
                    for target in node.targets:
                        if isinstance(target,ast.Name):assignments[target.id]=ast.dump(node.value,include_attributes=False)
        return definitions,assignments,top
    before,globals_before,top_before=parts(old);after,globals_after,top_after=parts(new)
    for name,value in globals_before.items():
        if globals_after.get(name)!=value:raise ValueError('preexisting module assignment changed: '+name)
    mutations={name for name in before if before[name]!=after.get(name)}
    additions=set(after)-set(before)
    if mutations!=set(changed) or additions!=set(added):
        raise ValueError('unapproved function/class transition: '+repr((mutations,additions)))
    if [node for node in top_after if node not in allowed_top]!=top_before:
        raise ValueError('unapproved top-level execution or imports')
    return dict(changedFunctions=sorted(mutations),addedFunctions=sorted(additions),
                unchangedFunctions=sorted(set(before)-mutations),preexistingAssignmentsUnchanged=True)


def check_witnesses(root,pins,runner_name,old_sha,new_sha):
    changed=[]
    for name,expected in pins.items():
        actual=sha(local(root,name))
        if name==runner_name:
            if expected!=old_sha:raise ValueError('historical runner witness is not the declared old generation')
            if actual!=new_sha:raise ValueError('current runner is not the reviewed new generation')
            changed.append(name)
        elif actual!=expected:raise ValueError('source changed outside guard transition: '+name)
    return dict(count=len(pins),changed=changed)


def check_artifacts(root,pins):
    for name,expected in pins.items():
        if sha(local(root,name))!=expected:raise ValueError('historical artifact changed: '+name)
    return len(pins)


def require_committed(root,names):
    """Compare Git blobs and working bytes without loading large score files in memory."""
    entries={}
    for entry in git(root,'ls-tree','-rz','HEAD').split(b'\0'):
        if not entry:continue
        header,name=entry.split(b'\t',1);mode,kind,oid=header.decode().split()
        if kind=='blob':entries[os.fsdecode(name)]=(mode,oid)
    for name in set(names):
        path=local(root,name)
        if name not in entries or entries[name][0]=='120000' or path.is_symlink():
            raise ValueError('input must be a committed regular file: '+name)
        h=hashlib.sha1(('blob '+str(path.stat().st_size)+'\0').encode())
        with path.open('rb') as stream:
            for data in iter(lambda:stream.read(1024*1024),b''):h.update(data)
        if h.hexdigest()!=entries[name][1]:raise ValueError('uncommitted input: '+name)


def module(name,path,source=None):
    if source is None:
        spec=importlib.util.spec_from_file_location(name,path);obj=importlib.util.module_from_spec(spec)
        sys.modules[name]=obj;spec.loader.exec_module(obj);return obj
    obj=types.ModuleType(name);obj.__file__=str(path);sys.modules[name]=obj
    exec(compile(source,str(path),'exec'),obj.__dict__);return obj


def verify(text_fix_ref=None):
    head=git(ROOT,'rev-parse','HEAD').decode().strip()
    old=git(ROOT,'show',OLD_REF+':'+RUNNER)
    new=local(ROOT,RUNNER).read_bytes()
    if digest(old)!=OLD_SHA or digest(new)!=NEW_SHA:raise ValueError('runner generation differs from reviewed transition')
    allowed={ast.dump(ast.parse(text).body[0],include_attributes=False) for text in TOP_ADDITIONS}
    proof=function_transition(old.decode(),new.decode(),CHANGED,ADDED,allowed)
    candidate=G1/'candidate-e3';capture=G1/'candidate-capture/attempt-1'
    relative=lambda path:str(path.relative_to(ROOT))
    witnesses={}
    required={RUNNER,relative(Path(__file__)),relative(HERE/'test_bridge.py')}
    for path in (candidate/'public-2/provenance.json',candidate/'calval-2/summary.json',
                 candidate/'rendered-calval-1/summary.json'):
        document=load(path);required.add(relative(path));required.update(document['sources'])
        witnesses[relative(path)]=dict(sha256=sha(path),**check_witnesses(
            ROOT,document['sources'],RUNNER,OLD_SHA,NEW_SHA))
    seal=load(capture/'seal.json');frozen=load(capture/'frozen.json')
    if sha(capture/'seal.json')!=frozen['sealSha256']:raise ValueError('capture seal changed')
    source_check=check_witnesses(ROOT,{p:seal['inputs'][p] for p in seal['sources']},RUNNER,OLD_SHA,NEW_SHA)
    check_witnesses(ROOT,seal['inputs'],RUNNER,OLD_SHA,NEW_SHA)
    prefix=relative(capture)+'/'
    if any(not name.startswith(prefix) for name in frozen['files']):raise ValueError('unexpected frozen capture payload scope')
    check_artifacts(ROOT,frozen['files'])
    required.update(seal['inputs']);required.update(frozen['files']);required.add(relative(capture/'frozen.json'))
    # Read retained evidence bytes, not any native archive payload they were scored from.
    evidence_paths=[candidate/'public-2/numerical.json',candidate/'public-2/parameters.json',
        candidate/'calval-2/scores.json.gz',candidate/'calval-2/numerical-admission.json.gz',
        candidate/'calval-2/admission-storage.json',candidate/'rendered-calval-1/scores.json.gz',
        candidate/'rendered-calval-1/rendered-admission.json.gz',candidate/'rendered-calval-1/admission-storage.json',
        candidate/'rendered-calval-1/veto.json',candidate/'rendered-calval-1/independent-replay.json',
        candidate/'shipped-baseline.json']
    for path in evidence_paths:required.add(relative(path))
    require_committed(ROOT,required)
    runner=module('transition_current_runner',ROOT/RUNNER)
    old_runner=module('transition_historical_runner',ROOT/RUNNER,old.decode())
    scorer=module('transition_scorer',candidate/'scorer.py')
    def no_native(*args,**kwargs):raise AssertionError('native reader forbidden in source bridge')
    scorer.native_reader=no_native
    scorer.wave.reader=no_native
    scorer.check_runtime()
    expected=load(candidate/'public-2/numerical.json')
    scorer.runner=old_runner;before=scorer.predictions()
    scorer.runner=runner;after=scorer.predictions()
    encoded=(json.dumps(after,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    if before!=after or after!=expected or digest(encoded)!=sha(candidate/'public-2/numerical.json'):
        raise ValueError('public prediction reproduction changed')
    admitted,_=runner.admitted_scope(ROOT,scorer.wave)
    if admitted!=old_runner.admitted_scope(ROOT,scorer.wave)[0]:raise ValueError('admitted membership changed')
    config=load(capture/'runtime.json')
    runner.freeze_domain(ROOT,scorer.wave,dict(id='body-e3',domainEvidence=relative(capture/'domain-evidence.json')),
                        admitted['rendered'],runner.sources(ROOT),set(),config)
    text_fix=None
    if text_fix_ref:
        path='packages/calibration/test/tier-coherence.test.ts'
        changed=git(ROOT,'diff-tree','--no-commit-id','--name-only','-r',text_fix_ref).decode().splitlines()
        if changed!=[path]:raise ValueError('text-fix commit changes unexpected paths')
        if path in runner.sources(ROOT) or path in seal['sources']:raise ValueError('text fix unexpectedly participates in runtime source frontier')
        before_text=git(ROOT,'show',text_fix_ref+'^:'+path)
        after_text=git(ROOT,'show',text_fix_ref+':'+path)
        require_committed(ROOT,[path])
        if digest(after_text)!=sha(ROOT/path):raise ValueError('text-fix file moved after named commit')
        text_fix=dict(commit=text_fix_ref,path=path,beforeSha256=digest(before_text),afterSha256=digest(after_text),
                      outsideRuntimeAndCaptureSourceInventories=True,
                      qualification='Test wording-only classification requires the separate worker review; no runtime CSS parity inferred.')
    if git(ROOT,'rev-parse','HEAD').decode().strip()!=head:raise ValueError('HEAD moved during source bridge; rerun to name one frontier')
    return dict(schema='w41-guard-source-transition-1',head=head,oldRunner=dict(commit=OLD_REF,sha256=OLD_SHA),
        newRunner=dict(sha256=NEW_SHA),functionIdentity=proof,historicalSourceWitnesses=witnesses,
        captureSourceWitness=source_check,captureFrozen=dict(path=relative(capture/'frozen.json'),sha256=sha(capture/'frozen.json'),files=len(frozen['files'])),
        retainedArtifacts={relative(p):sha(p) for p in evidence_paths},publicPredictions=dict(cells=len(after['cells']),byteIdentical=True,sha256=digest(encoded)),
        domainRecordsValidated=len(admitted['rendered']),membership={kind:dict(total=len(cells),holdout=sum(scorer.wave.roles[c.split('/',1)[1]]=='holdout' for c in cells)) for kind,cells in admitted.items()},
        textOnlyTestFix=text_fix,bridgeSources={relative(p):sha(p) for p in (Path(__file__),HERE/'test_bridge.py')},
        nativePayloadReads=0,browsersLaunched=0,manifestFreezeAttempted=False,receiptAttempted=False,
        limitation='Source transition and public/domain checks, not new native scores or closure. Old driver.verify intentionally retains old source pin; no seal rewritten. Full final-wave source inventory remains for a later authorized freeze.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--text-fix-ref');args=parser.parse_args()
    if args.out.exists():raise FileExistsError(args.out)
    save(args.out,verify(args.text_fix_ref))
    print('Source bridge verified; no native reads, recapture, freeze or receipt.')


if __name__=='__main__':main()
