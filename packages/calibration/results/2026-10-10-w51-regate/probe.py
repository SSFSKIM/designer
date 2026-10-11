"""Source-only exercise for W51: no historical root, fixture, capture or native value read."""
from pathlib import Path
import types
import sys

HERE=Path(__file__).resolve().parent
FIT=HERE.parent/'2026-10-08-w50-g1-fit'
CURRENT=HERE.parent/'2026-10-08-w50-g1-current3'


def source(path,name):
    module=types.ModuleType(name);module.__file__=str(path);sys.modules[name]=module
    exec(compile(path.read_bytes(),str(path),'exec',dont_inherit=True),module.__dict__)
    return module


def exercise():
    for name in ('run','root','journal','guard','semantics','ports','static','capture','role_common',
                 'measurement','phase_sources','judge','judge_rules','judge_targets','repeat','repeat_sources','witness'):
        source(HERE/(name+'.py'),'w51_probe_'+name)
    # Importing an adapter does not execute its late launch dependencies. Its source probe
    # loads the same census chain as launch, but classifies synthetic rows without observing
    # the machine or launching a renderer. Both paths remain part of this one closure.
    for lane in ('canonical','web'):
        transport=source(HERE/lane/'adapter.py','w51_probe_'+lane)
        if transport.source_probe().get('status')!='SOURCE_ONLY':
            raise ValueError('Transport probe did not remain source-only')
    for path in (HERE/'lifecycle.py',FIT/'live-execution/admission.py',
                 FIT/'current-analysis/analysis.py',
                 FIT.parent/'2026-10-08-w50-g0-declaration/audit/runner.py'):
        source(path,'w51_probe_'+path.stem)
    s=source(HERE/'repeat_sources.py','w51_probe_repeat_math')
    image=s.M.np.full((64,64,3),128,dtype=s.M.np.uint8)
    s.canonical_statistics(image,s.M.np.zeros_like(image),[image]*7,image,image,
        [{'statistic':'T1-low','B':None}],provenance={'dataOrigin':'synthetic-source-probe'},
        component={'kind':'rrect','size':[48,48],'radius':0},canvas={'width':64,'height':64},scale=1,text=True)
    source(HERE/'semantics.py','w51_probe_differential').verify()
    # A controlled scalar exercises the new reduction path under the guard. It is not a
    # reference or candidate reading and creates no population, root, or output authority.
    rules=source(HERE/'judge_rules.py','w51_probe_policy_rules')
    key=['source-probe','webgpu','source-probe','T1-full-silhouette']
    member={'key':key,'statistic':key[3],'component':None,'native':.25,'current':.375,
            'epsilon':.03125,'provenance':{'source':'synthetic-source-probe'}}
    policy={'schema':'w51-dl5-policy-1','dataOrigin':'synthetic','completePopulation':{},
            'completeKeys':[key],'primaryT1GrowthMultiplier':2,'exceptions':[],
            'aggregates':[{'id':'source-probe','kind':'t1','dimensions':{},'gate':True,
                'reduction':'median-log-ratio','timing':'population-full','members':[member],
                'membershipSha256':rules._digest([member])}]}
    row=dict(zip(rules.KEY,key))
    row['readings']={key[3]:{'native':.25,'current':.375,'candidate':.375,
        **{side+'MeasurementStatus':'MEASURED' for side in ('native','current','candidate')}}}
    graded=rules.route_aggregates([row],landing_policy=policy,policy_sha256=rules._digest(policy),
        complete_keys=[key],full_union=True)
    if graded['status']!='WITHIN':raise ValueError('Source-only landing policy probe failed')
    return {'status':'SOURCE_ONLY','landingPolicy':graded['status']}

if __name__=='__main__': exercise()
