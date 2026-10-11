"""Internal W51 completeness/provenance witness, never a historical gate comparison."""
import copy
import json
from pathlib import Path

KEY=('profile','renderer','scene','statistic')


def coverage(expected,captures,measured,reported):
    keys=[tuple(r[k] for k in KEY) for r in expected]
    if len(keys)!=len(set(keys)):raise ValueError('Declared statistic population is ambiguous')
    for rows in (measured,reported):
        actual=[tuple(r[k] for k in KEY) for r in rows]
        if len(actual)!=len(set(actual)) or set(actual)!=set(keys):raise ValueError('Measurement/report coverage differs')
    physical=[tuple(r[k] for k in KEY[:3]) for r in captures]
    if (len(physical)!=len(set(physical)) or set(physical)!={k[:3] for k in keys} or
            any(r['lane']!='candidate' for r in captures)):
        raise ValueError('Capture membership or lane differs')


def clause_c(engine, context, measured, report):
    """Recompute only sealed scalar reductions, not images or new scientific operands."""
    R = engine.R
    static = R.source(Path(__file__).resolve().parent/'static.py', 'w51_witness_policy')
    policy = static.bound_landing_policy(engine.doc, engine.science, context['inputs'])
    pin = engine.science['landingPolicy']
    if report.get('landingPolicy') != pin:
        raise ValueError('Report aggregate policy differs from its sealed dataset')
    complete = R.checked(engine.doc['repo'], policy['completePopulation'])
    keys = engine.J.load(complete)['statisticKeys']
    full = context['populationPin'] == policy['completePopulation']
    selected = [tuple(row[k] for k in KEY) for row in context['expectedCells']]
    if (len(selected) != len(set(selected)) or not set(selected) <= {tuple(k) for k in keys} or
            (full and set(selected) != {tuple(k) for k in keys})):
        raise ValueError('Report aggregate completeness differs from declared population')
    rules = R.source(Path(__file__).resolve().parent/'judge_rules.py', 'w51_witness_rules')
    expected = rules.route_aggregates(measured['rows'], landing_policy=policy,
        policy_sha256=pin['sha256'], complete_keys=keys, full_union=full)
    if report.get('clauseC') != expected:
        raise ValueError('Report aggregate values, membership or completeness differ')
    return expected


def verify(engine,context,union,captures,receipt,measured,report):
    engine.require_context(context);R,J=engine.R,engine.J
    R.verify_web_sources(engine.doc,engine.batch)
    for relative,expected in engine.doc['closure']['sources'].items():
        R.checked(R.REPO,{'path':relative,'sha256':expected})
    for item in engine.science['inputs']:R.checked(R.REPO,item)
    coverage(context['expectedCells'],captures['captures'],measured['rows'],report['cells'])
    if engine.store.complete_union()!=union:raise ValueError('Complete capture union changed')
    if captures['captures']!=[J.load(J.checked(r['payload'])) for r in union['members']]:
        raise ValueError('Capture record differs from checkpoint')
    if receipt!=engine.A.validate_captures(engine.batch,captures,engine.output):
        raise ValueError('Capture receipt changed')
    snapshots={tuple(row[k] for k in KEY):row for row in measured['rows']}
    producer,text=[],[]
    for row in measured['rows']:
        value=J.load(J.checked(row['evidence']))
        if value['row']!=json.loads(R.encoded({k:v for k,v in row.items() if k!='evidence'})):
            raise ValueError('Keyed measurement was mutated after its write')
        identity=[row[k] for k in KEY]
        if row['statistic']=='T1-full-silhouette' and row['family']=='impulse' and row['position']==.25:
            reading=row['readings']['T1-full-silhouette']
            proof=reading['evidence']['candidate'].get('productionStatistic')
            if proof is None or proof['estimator']!='PRODUCTION_TS_INTERIOR_LEVEL':
                raise ValueError('Impulse producer companion lost productionStatistic')
            producer.append({'key':identity,'evidence':row['evidence'],'producer':proof['estimator']})
        if row['statistic']=='T1-low':
            if not {'T1-low','T1-fine'}<=set(row['readings']):raise ValueError('Text band companion missing')
            proof=row['readings']['T1-low']['evidence']['candidate'].get('productionStatistic')
            if row['position']==.25 and (proof is None or proof['estimator']!='CANONICAL_NUMPY_GAUSSIAN_LOW'):
                raise ValueError('Frozen low-band producer provenance missing')
            text.append({'key':identity,'evidence':row['evidence'],'bands':['T1-low','T1-fine'],
                         'producer':None if proof is None else proof['estimator']})
    wanted=lambda row: 'PENDING_OWNER_UNION' if row['statistic']=='owner-contracts' else (
        {'REPORTED','UNMEASURED_REPORTED','UNMEASURED_EMPTY_SUPPORT'} if
        [row[k] for k in KEY] in engine.science['reportedKeys'] else 'PASS')
    passed=True
    for row in report['cells']:
        if row['evidence']!=snapshots[tuple(row[k] for k in KEY)]['evidence']:
            raise ValueError('Report cell names another measurement')
        desired=wanted(row)
        passed &= row['status'] in desired if isinstance(desired,set) else row['status']==desired
    aggregates=clause_c(engine,context,measured,report)
    passed &= aggregates['status'] in ('WITHIN','PENDING_FULL_UNION')
    if report['status']!=('PASS_EXPOSED_OWNER_PENDING' if passed else 'NEITHER'):
        raise ValueError('Report status differs from complete cell verdicts')
    if (report['ownerChecks']!='PENDING_FULL_UNION' or report['targetChecks']!='PENDING_FULL_UNION' or
            report['pendingOwnerKeys']!=context['phaseDependencies']['pendingOwnerKeys']):
        raise ValueError('Partial population claimed full-union owners/targets')
    if engine.science['dataOrigin']=='synthetic' and (not producer or not text or
            not any(r['producer']=='CANONICAL_NUMPY_GAUSSIAN_LOW' for r in text)):
        raise ValueError('Synthetic rehearsal omitted required producer/frozen-low/text branch witnesses')
    differential=R.source(Path(__file__).resolve().parent/'semantics.py','w51_final_differential').verify()
    return {'schema':'w51-completeness-witness-1','status':'COMPLETE','dataOrigin':engine.science['dataOrigin'],
        'population':context['populationPin'],'dataset':context['datasetPin'],
        'executionRoot':J.pin(context['executionRoot']),'analysisClaim':copy.deepcopy(context['executionClaim']),
        'captureUnion':J.pin(engine.store.home/'captures.complete.json'),'physicalCount':len(captures['captures']),
        'statisticCount':len(measured['rows']),'candidate':engine.batch['cohort'],
        'importedFit':engine.doc['importedFit'],'referenceInventory':engine.science['references'],
        'measurement':measured['snapshot'],'sourceClosureSha256':R.digest(engine.doc['closure']),
        'sourceDifferential':differential,'branches':{'producerCarry':producer,'textBands':text},
        'judgeCompleted':True,'reportStatus':report['status'],
        'landingPolicy':engine.science['landingPolicy'],'clauseC':aggregates}
