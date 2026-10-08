"""DL5g exposure-only evidence completeness, called by the not-yet-sealed live judge.

This does not award a numerical PASS or alter the sealed dispatcher. The caller must run
it before its final verdict. Every original blind statistic retains its identity and is
bound to three admitted native runs plus real same-invocation baseline/candidate captures.
"""
import importlib.util
from pathlib import Path
import re
import sys

KEY=('profile','renderer','scene','statistic')


def validate_blind_exposure(context,rows):
    dispatcher=sys.modules.get('w50_g1_dispatch')
    if dispatcher is None:raise ValueError('Blind evidence validation requires live exposure authority')
    dispatcher.require_context(context)
    if context.get('phase')!='exposure' or context.get('batch',{}).get('phase')!='exposure':
        raise ValueError('Blind evidence validation is exposure-only')
    root=dispatcher.sealed(context['executionRoot'])
    path=Path(__file__).with_name('native_evidence.py')
    spec=importlib.util.spec_from_file_location('w50_blind_native_evidence',path)
    native_module=importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(),str(path),'exec'),native_module.__dict__)
    evidence=native_module.NativeEvidence(context['repo'],root['manifest'])
    original=evidence.read(root['references'])
    expected={tuple(r[k] for k in KEY):r for r in original['cells'] if r['role']=='blind'}
    if not isinstance(rows,list) or not expected:
        raise ValueError('Blind exposure needs the full original reference population')
    actual=[]
    for row in rows:
        if not isinstance(row,dict) or any(k not in row for k in KEY):raise ValueError('Missing blind reference identity')
        actual.append(tuple(row[k] for k in KEY))
    if len(actual)!=len(set(actual)) or set(actual)!=set(expected):
        raise ValueError('Blind exposure evidence must cover every original blind key exactly once')
    cohort=context['batch']['cohort'];output=Path(context['output']).resolve()
    for row in rows:
        before=expected[tuple(row[k] for k in KEY)]
        for key in ('role','support','nativeIdentity','referenceIdentity','currentGeneration','currentDocumentPair'):
            if row.get(key)!=before.get(key):raise ValueError('Blind exposure changed original provenance')
        runs=[r for r in context['batch']['runs'] if r['profile']==row['profile'] and
              r['renderer']==row['renderer'] and row['scene'] in r['scenes']]
        if len(runs)!=1:raise ValueError('Blind row is outside its exact exposure run')
        run=runs[0]
        if run['candidate'] not in cohort or run.get('baselineCandidate') not in root.get('baselineDocuments',[]):
            raise ValueError('Blind row needs same-cohort candidate and registered frozen-current baseline')
        dispatcher.require_render_admission(context,run)
        dispatcher.require_render_admission(context,dispatcher.baseline_run(run),current=True)
        evidence.validate(row,row.get('nativeEvidence'),exposure=context)
        scale=re.search(r'-([12])x-',row['profile'])
        if not scale:raise ValueError('Blind profile lacks its declared scale')
        dimensions=[512*int(scale[1]),384*int(scale[1])]
        for field,lane,candidate in (('currentCapture','current',run['baselineCandidate']),
                                     ('candidateCapture','candidate',run['candidate'])):
            capture=row.get(field)
            if not isinstance(capture,dict) or capture.get('lane')!=lane or capture.get('candidate')!=candidate or any(
                    capture.get(k)!=row[k] for k in KEY[:3]):
                raise ValueError('Blind capture is missing or names another scene/material/lane')
            evidence.check(candidate)
            artifacts=capture.get('artifacts',{})
            for key in ('png','cell','report'):
                target=evidence.check(artifacts.get(key))
                if not target.is_relative_to(output):raise ValueError('Blind capture is outside the single exposure output')
            evidence.png(artifacts['png'],dimensions)
            metadata=evidence.read(artifacts['cell']);page=evidence.read(artifacts['report']).get('page',{})
            if (metadata.get('sceneId')!=row['scene'] or metadata.get('renderer')!=row['renderer'] or
                    metadata.get('pixelSize')!=dimensions or page.get('sceneId')!=row['scene'] or
                    page.get('requestedRenderer')!=row['renderer'] or page.get('devicePixelRatio')!=int(scale[1]) or
                    page.get('materialMode')!='candidate' or page.get('candidateDocument',{}).get('mode')!='candidate' or
                    page.get('candidateDocument',{}).get('declarationSha256')!=candidate['sha256'][:12] or
                    f'declarationSha256={candidate["sha256"][:12]}' not in metadata.get('capturePath','')):
                raise ValueError('Blind capture metadata/report does not attest the same actual draw')
    evidence.finish();dispatcher.require_context(context)
    return {'schema':'w50-bound-blind-exposure-evidence-1','status':'BOUND_BLIND_EVIDENCE',
            'cells':len(rows),'candidateSha256s':sorted(p['sha256'] for p in cohort)}
