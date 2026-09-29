"""Stream existing BODY-E3 evidence into exact runner inputs, never freeze or expose.

Deep/member/repeat/censor readings remain in the compact score. Large exterior,
interior and veto arrays stay in their original hash-bound reports with per-cell
JSON-pointer links. Their pass flags are checked before deriving admission.
"""
import argparse
from copy import deepcopy
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import resource
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
G1=HERE.parents[1]
EXPECTED_RUNNER='5ae591ad6ea2098613e75dfb6377875314fcc2280d7526bf80e139f206436c08'
HISTORICAL_RUNNER='02ed44215ca4f273eb698ab9f514173f2c6cbfb89d09b6a12c837ffee9b4aa96'
# The unchanged reading committed at 5d7c37ee, not a new pin of present-day evidence.
EXPECTED_TRANSITION='e232fd1f51bd1ba5132fd118fc1436077b8fcef03567c802a5046c98f527e12c'
# Existing reports peak at 8,627,814 characters (fix-value-sizing.json). Allow headroom
# without letting malformed early input buffer the 2.46 GB admission document.
MAX_VALUE_CHARS=16*1024*1024


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def stable(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def cell_sha(value):return hashlib.sha256(stable(value).encode()).hexdigest()


def unique(pairs):
    out={}
    for key,value in pairs:
        if key in out:raise ValueError('duplicate JSON key: '+key)
        out[key]=value
    return out


def forbidden(value):raise ValueError('nonfinite JSON value: '+value)


def entries(path,chunk_size=1024*1024,max_value_chars=MAX_VALUE_CHARS):
    """Bound each encoded JSON key/value in decoded Unicode characters, not bytes.

    The inclusive limit counts quotes, escapes and internal whitespace, but excludes
    whitespace before the value. One extra character permits delimiter lookahead at
    the exact limit, including a scalar split across chunks. The text buffer never
    exceeds limit + 1, even when a caller requests a larger read. Python's Unicode
    storage and the decoded object have separate memory costs; this is not an RSS cap.
    """
    if chunk_size<1 or max_value_chars<1:raise ValueError('positive stream limits required')
    decoder=json.JSONDecoder(object_pairs_hook=unique,parse_constant=forbidden)
    opener=gzip.open if Path(path).suffix=='.gz' else open
    buffer='';eof=False;seen=set()
    with opener(path,'rt',encoding='utf-8') as stream:
        def refill():
            nonlocal buffer,eof
            available=max_value_chars+1-len(buffer)
            if available<=0:raise ValueError('JSON value exceeds character limit')
            block=stream.read(min(chunk_size,available));eof=not block;buffer+=block
        def whitespace():
            nonlocal buffer
            while True:
                buffer=buffer.lstrip()
                if buffer or eof:return
                refill()
        def token(expected):
            nonlocal buffer
            whitespace()
            if not buffer.startswith(expected):raise ValueError('invalid JSON delimiter: '+expected)
            buffer=buffer[len(expected):]
        def value():
            nonlocal buffer
            whitespace()
            while True:
                try:
                    row,end=decoder.raw_decode(buffer)
                    if end>max_value_chars:raise ValueError('JSON value exceeds character limit')
                    # A scalar can be a valid prefix of a token split across chunks.
                    if end==len(buffer) and not eof:
                        refill();continue
                    if end<len(buffer) and buffer[end] not in ',}: \t\r\n':
                        if eof:raise ValueError('invalid scalar token boundary')
                        refill();continue
                    buffer=buffer[end:];return row
                except json.JSONDecodeError:
                    if eof:raise
                    refill()
        token('{');first=True
        while True:
            whitespace()
            if buffer.startswith('}'):
                token('}');whitespace()
                if buffer or not eof:raise ValueError('trailing JSON data')
                return
            if not first:token(',')
            key=value()
            if not isinstance(key,str) or key in seen:raise ValueError('duplicate or invalid cell key')
            seen.add(key);token(':');row=value();yield key,row;first=False


def flags(reading,key):
    values=reading.get(key)
    if not isinstance(values,list) or len(values)!=3 or any(type(v) is not bool for v in values):
        raise ValueError('invalid RGB flags: '+key)
    return values


def deep_status(raw,kind):
    members=raw['members'] if kind=='numerical' else raw['deep']
    scores=[]
    for member in members:
        score=member['score']
        if score.get('reason')=='deep population below four':continue
        if len(score['runs'])!=7 or len(score['pixels'])!=7:raise ValueError('all seven deep repeats required')
        readings=[score['median'],*score['runs']]
        survives=not any(any(flags(row,'failed')) for row in readings)
        measured=not any(any(flags(row,'railChannels')) for row in readings)
        if score['survives'] is not survives or score['heldoutCoverage'] is not measured:
            raise ValueError('deep rail/repeat summary disagreement')
        scores.append((survives,measured))
    if not scores:raise ValueError('no admitted deep member')
    passed=all(s for s,_ in scores);measured=all(m for _,m in scores)
    expected=dict(status='measured',passes=passed) if measured else dict(
        status='UNMEASURED',reason='censored',passes=None,constraintsPass=passed)
    for key,value in expected.items():
        if key not in raw or raw[key]!=value or type(raw[key]) is not type(value):
            raise ValueError('deep status/censor summary disagreement: '+key)
    for key,value in [('admittedMembers',len(scores)),('populationDeficientMembers',len(members)-len(scores))]:
        if key in raw and raw[key]!=value:raise ValueError('deep population count disagreement')


def compact(kind,raw):
    deep_status(raw,kind)
    if kind=='numerical':return deepcopy(raw)
    admitted=[];deficient=0
    for row in raw['veto']:
        score=row['score']
        if score['passes'] is None:
            if score.get('status')!='UNMEASURED':raise ValueError('invalid deficient veto status')
            deficient+=1;continue
        if len(score['runs'])!=7:raise ValueError('all seven veto repeats required')
        passed=not any(any(flags(r,'vetoRGB')) for r in [score['median'],*score['runs']])
        if score['passes'] is not passed:raise ValueError('veto repeat summary disagreement')
        admitted.append(passed)
    veto=bool(admitted) and all(admitted)
    if raw['vetoPass'] is not veto or not veto:raise ValueError('rendered veto failure or summary disagreement')
    if raw['populationDeficientVetoBins']!=deficient:raise ValueError('veto population count disagreement')
    return {key:deepcopy(value) for key,value in raw.items()
            if key not in ('rawRendered','interiorTransfer','veto')}


def local(root,name):
    path=root/name
    if Path(name).is_absolute() or '..' in Path(name).parts or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('artifact outside repository')
    return path


def maps(root,candidate,baseline,expected,identities):
    if set(candidate)!=set(expected) or set(baseline)!=set(expected) or not set(identities)<=set(expected):
        raise ValueError('rendered/baseline membership mismatch')
    checked={}
    for collection in (candidate,baseline):
        for cell,row in collection.items():
            if set(row)!={'png','pngSha256','projection','projectionSha256'}:
                raise ValueError('capture map record fields differ')
            for kind in ('png','projection'):
                name=row[kind]
                if name not in checked:checked[name]=sha(local(root,name))
                if checked[name]!=row[kind+'Sha256']:raise ValueError('capture payload hash mismatch: '+cell)
    for cell in identities:
        if any(candidate[cell][kind+'Sha256']!=baseline[cell][kind+'Sha256'] for kind in ('png','projection')):
            raise ValueError('endpoint identity artifact mismatch: '+cell)
    view=lambda row:{key:row[key] for key in ('png','projection')}
    return ({'cells':{c:view(candidate[c]) for c in sorted(expected)}},
            {'cells':{c:view(baseline[c]) for c in sorted(identities)}})


def check_admission(disposition,raw,original):
    if disposition=='claimed uniform body':
        result=(raw.get('status')=='measured' and raw.get('passes') is True) or (
            raw.get('status')=='UNMEASURED' and raw.get('reason')=='censored'
            and raw.get('passes') is None and raw.get('constraintsPass') is True)
        if not result:raise ValueError('claimed admission failure')
    else:result=dict(status=disposition,passes=None,score=raw)
    if result!=original:raise ValueError('original admission differs from raw reading/disposition')
    return result


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);obj=importlib.util.module_from_spec(spec)
    sys.modules[name]=obj;spec.loader.exec_module(obj);return obj



def load_transition(path):
    if sha(path)!=EXPECTED_TRANSITION:raise ValueError('transition reading differs from historical pin')
    return json.loads(Path(path).read_text(),object_pairs_hook=unique,parse_constant=forbidden)


def historical_inputs(root,reading,bridge_path,runner_path,capture):
    """Revalidate historical identity before using evidence or importing its helper.

    Current committed bytes alone cannot attest an earlier generation. The pinned
    transition reading binds the original reports and source-witness documents; only
    its exact old-to-new guard runner transition is permitted in those witnesses.
    Every checked path joins the assembly's committed/input-hash/end-unchanged set.
    """
    relative=lambda p:str(p.relative_to(root))
    runner_name=relative(runner_path)
    if (reading['oldRunner']['sha256']!=HISTORICAL_RUNNER
            or reading['newRunner']['sha256']!=EXPECTED_RUNNER):
        raise ValueError('transition runner allowance differs from reviewed generations')
    bridge_sources=reading['bridgeSources']
    required={relative(bridge_path),relative(bridge_path.with_name('test_bridge.py'))}
    if not required<=set(bridge_sources):raise ValueError('bridge source inventory incomplete')
    for name,expected in bridge_sources.items():
        if sha(local(root,name))!=expected:raise ValueError('bridge source changed: '+name)
    bridge=module('assembly_bridge',bridge_path)
    names=set(bridge_sources)|{runner_name}
    if sha(runner_path)!=EXPECTED_RUNNER:raise ValueError('current runner differs from reviewed generation')
    bridge.check_artifacts(root,reading['retainedArtifacts'])
    names.update(reading['retainedArtifacts'])
    for name,witness in reading['historicalSourceWitnesses'].items():
        bridge.check_artifacts(root,{name:witness['sha256']})
        document=bridge.load(local(root,name))
        result=bridge.check_witnesses(root,document['sources'],runner_name,
                                      HISTORICAL_RUNNER,EXPECTED_RUNNER)
        if result!={k:witness[k] for k in ('count','changed')}:
            raise ValueError('historical source witness inventory differs')
        names.add(name);names.update(document['sources'])
    frozen_path=capture/'frozen.json';seal_path=capture/'seal.json'
    if reading['captureFrozen']['path']!=relative(frozen_path):
        raise ValueError('capture generation path differs from transition')
    bridge.check_artifacts(root,{relative(frozen_path):reading['captureFrozen']['sha256']})
    frozen=bridge.load(frozen_path)
    bridge.check_artifacts(root,{relative(seal_path):frozen['sealSha256']})
    seal=bridge.load(seal_path)
    result=bridge.check_witnesses(root,{p:seal['inputs'][p] for p in seal['sources']},
                                  runner_name,HISTORICAL_RUNNER,EXPECTED_RUNNER)
    if result!=reading['captureSourceWitness']:raise ValueError('capture source witness inventory differs')
    bridge.check_witnesses(root,seal['inputs'],runner_name,HISTORICAL_RUNNER,EXPECTED_RUNNER)
    bridge.check_artifacts(root,frozen['files'])
    names.update((relative(frozen_path),relative(seal_path)))
    names.update(seal['inputs']);names.update(frozen['files'])
    return bridge,{local(root,name) for name in names}


def assessment_signature(row):
    wrapped='score' in row and row.get('status','').startswith('not claimed')
    score=row['score'] if wrapped else row
    keys=('status','passes','reason','constraintsPass','diagnostic','vetoPass')
    return dict(disposition=row['status'] if wrapped else 'claimed',
                score={k:score[k] for k in keys if k in score})


def reduce_kind(kind,raw_path,admission_path,expected,wave,claim,runner,disposition):
    reduced={};survival={};links={};equivalent=0
    for pair in itertools.zip_longest(entries(raw_path),entries(admission_path)):
        if pair[0] is None or pair[1] is None or pair[0][0]!=pair[1][0]:
            raise ValueError('score/admission membership or ordering differs')
        (cell,raw),(_,original)=pair
        if cell not in expected:raise ValueError('score membership contains undeclared or holdout cell')
        slim=compact(kind,raw)
        old=check_admission(disposition(cell),raw,original)
        new=check_admission(disposition(cell),slim,True if old is True else dict(
            status=old['status'],passes=None,score=slim))
        for payload in (raw,slim):
            scores={'body-e3':{'numerical':{},'rendered':{}}};scores['body-e3'][kind][cell]=payload
            coverage,assessments=runner.aggregate(wave,scores,{'body-e3':{}},{'body-e3':claim},
                [cell] if kind=='numerical' else [],[cell] if kind=='rendered' else [])
            signature=(coverage,assessment_signature(assessments['body-e3'][kind][cell]))
            if payload is raw:raw_signature=signature
            elif signature!=raw_signature:raise ValueError('aggregate or assessment semantics changed')
        reduced[cell]=slim;survival[cell]=new;equivalent+=1
        pointer='/'+cell.replace('~','~0').replace('/','~1')
        links[cell]=dict(jsonPointer=pointer,rawCellSha256=cell_sha(raw),originalAdmissionCellSha256=cell_sha(original))
    if set(reduced)!=set(expected):raise ValueError('score membership incomplete')
    return reduced,survival,links,equivalent


def assemble(out):
    out=Path(out).resolve()
    if not out.is_relative_to(HERE) or out==HERE or out.exists():raise ValueError('new assembly child directory required')
    transition_path=HERE.parent/'transition/reading-1.json'
    reading=load_transition(transition_path)
    capture=G1/'candidate-capture/attempt-1';candidate=G1/'candidate-e3'
    bridge,historical_paths=historical_inputs(ROOT,reading,HERE.parent/'transition/bridge.py',
                                            HERE.parent/'runner.py',capture)
    runner=module('assembly_runner',HERE.parent/'runner.py')
    if sha(HERE.parent/'runner.py')!=EXPECTED_RUNNER:raise ValueError('runner differs from reviewed assembly contract')
    sys.path.insert(0,str(G1/'candidate-e3'))
    prepare=module('assembly_prepare',G1/'candidate-e3/prepare.py');scorer=prepare.s
    def forbidden_native(*args,**kwargs):raise AssertionError('native reads forbidden during assembly')
    scorer.native_reader=forbidden_native;scorer.wave.reader=forbidden_native
    scorer.check_runtime();wave=scorer.wave
    relative=lambda p:str(Path(p).relative_to(ROOT))
    load=runner.load
    admitted,_=runner.admitted_scope(ROOT,wave)
    before={kind:[c for c in cells if wave.roles[c.split('/',1)[1]]!='holdout'] for kind,cells in admitted.items()}
    scope_path=HERE.parent/'body-e3-claim-scope.json';claim=load(scope_path)
    selected=runner.claim_scope(ROOT,wave,dict(claimScope=relative(scope_path)))
    identities={c for c in admitted['rendered'] if runner.endpoint(wave,c) not in selected}
    frozen=load(capture/'frozen.json');sealed=load(capture/'seal.json')
    paths={Path(__file__),HERE/'test_assemble.py',HERE.parent/'runner.py',HERE.parent/'manifest.schema.json',
        HERE.parent/'transition/reading-1.json',capture/'frozen.json',capture/'seal.json',scope_path,
        candidate/'public-2/numerical.json',candidate/'public-2/parameters.json',candidate/'public-2/provenance.json',
        candidate/'final-runner-reproduction.json',candidate/'shipped-baseline.json',
        candidate/'rendered-calval-1/veto.json',candidate/'rendered-calval-1/strata.json'}
    paths.update(historical_paths)
    paths.update(ROOT/p for p in prepare.source_inputs())
    paths.update(ROOT/p for p in frozen['files']);paths.update(ROOT/p for p in sealed['inputs'])
    for directory,stem in [('calval-2','numerical'),('rendered-calval-1','rendered')]:
        paths.update(candidate/directory/name for name in ('scores.json.gz',stem+'-admission.json.gz',
                                                          'summary.json','admission-storage.json'))
    baseline=load(candidate/'shipped-baseline.json')['cells'];captures=load(capture/'rendered.json')['cells']
    for rows in (baseline,captures):
        paths.update(ROOT/row[key] for row in rows.values() for key in ('png','projection'))
    names=sorted(relative(p) for p in paths)
    bridge.require_committed(ROOT,names)
    pins={name:sha(ROOT/name) for name in names}
    head=bridge.git(ROOT,'rev-parse','HEAD').decode().strip()
    bridge.check_artifacts(ROOT,frozen['files'])
    rendered,identity=maps(ROOT,captures,baseline,admitted['rendered'],identities)
    runtime=load(capture/'runtime.json')
    runner.freeze_domain(ROOT,wave,dict(id='body-e3',domainEvidence=relative(capture/'domain-evidence.json')),
                        admitted['rendered'],runner.sources(ROOT),set(),runtime)
    for cell,row in captures.items():runner.png(ROOT/row['png'],runner.dimension(wave,cell))
    reduced={};survival={};linkmap={};equivalence={}
    for kind,directory in [('numerical','calval-2'),('rendered','rendered-calval-1')]:
        raw_path=candidate/directory/'scores.json.gz';admission_path=candidate/directory/(kind+'-admission.json.gz')
        reduced[kind],survival[kind],links,count=reduce_kind(kind,raw_path,admission_path,set(before[kind]),
            wave,claim,runner,scorer.disposition)
        linkmap[kind]=dict(rawReport=dict(path=relative(raw_path),sha256=pins[relative(raw_path)]),
            originalAdmission=dict(path=relative(admission_path),sha256=pins[relative(admission_path)]),cells=links)
        equivalence[kind]=count
    survival['veto']={c:r['vetoPass'] for c,r in reduced['rendered'].items()}
    if survival['veto']!=load(candidate/'rendered-calval-1/veto.json'):raise ValueError('saved veto flags differ')
    coverage,assessments=runner.aggregate(wave,{'body-e3':reduced},{'body-e3':{}},{'body-e3':claim},
                                         before['numerical'],before['rendered'])
    previous=load(candidate/'rendered-calval-1/strata.json')['aggregate']['coverage']
    if coverage['body-e3']!=next(iter(previous.values())):raise ValueError('retained aggregate coverage differs')
    bridge.check_artifacts(ROOT,pins)
    if bridge.git(ROOT,'rev-parse','HEAD').decode().strip()!=head:raise ValueError('HEAD moved during assembly; preserve inputs and rerun')
    out.mkdir()
    artifact=lambda name:relative(out/name)
    spec=dict(id='body-e3',parameters=relative(candidate/'public-2/parameters.json'),
        predictions=relative(candidate/'public-2/numerical.json'),rendered=artifact('rendered.json'),
        survival=artifact('survival.json'),claimScope=relative(scope_path),identityBaseline=artifact('identity-baseline.json'),
        domainEvidence=relative(capture/'domain-evidence.json'))
    instruments=sorted(set(names)|{artifact('evidence-links.json'),artifact('summary.json'),artifact('inputs.json')})
    report=dict(schema='w41-body-e3-input-assembly-1',sourceRevision=head,runnerSha256=EXPECTED_RUNNER,
        renderedCells=len(rendered['cells']),identityCells=len(identity['cells']),
        blindIdentityCells=sum(wave.roles[c.split('/',1)[1]]=='holdout' for c in identities),
        numericalAdmissionCells=len(survival['numerical']),renderedAdmissionCells=len(survival['rendered']),vetoCells=len(survival['veto']),
        rawCompactAssessmentEquivalenceCells=equivalence,aggregateCoverage=coverage,
        retainedDeepRepeatReadings=True,fullReportsRetainedAsInstruments=True,
        peakRSSBytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024),
        nativePayloadReads=0,browsersLaunched=0,manifestFreezeAttempted=False,receiptAttempted=False,
        qualification='BODY-E3 input preparation only; await all stroke verdicts and final-wave authorization before freeze/exposure.')
    outputs={'rendered.json':rendered,'identity-baseline.json':identity,'survival.json':survival,
        'evidence-links.json':linkmap,'inputs.json':pins,'instruments.json':instruments,'candidate.json':spec,'summary.json':report}
    for name,value in outputs.items():bridge.save(out/name,value)
    print(json.dumps(report,indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();assemble(args.out)


if __name__=='__main__':main()
