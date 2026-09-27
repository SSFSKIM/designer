"""Bind the parent's v2.2 aggregation and declared execution budgets additively.

Run once after the body solver fix is sealed. The complete original declaration,
closure, pins and generator remain under their original declaration hash.
No native observations, fitted numbers or historical artifacts are rewritten.
"""
import hashlib
import json
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OLD='99e460d5cf83da086fb27dbd132058fe81c31767462917623ce9883c74c9c05c'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if sha(HERE/'bounds-declaration.txt')!=OLD:raise SystemExit('expected original declaration; amendment refuses another generation')
execution={name:sha(HERE/name) for name in ['body-instrument/execution-parameters.json','instrument/stroke-execution-parameters.json']}
text=(HERE/'bounds-declaration.txt').read_text().replace('charter v2.1 clauses','charter v2.3 clauses',1)
text+='''
V2 ADDENDUM — PARENT X31 AGGREGATION AND EXECUTION RECORDS
Supersedes the initial declaration's aggregation ambiguity, not its bounds,
required populations, parameters, working spaces, split or recorded numbers.
The complete original is retained under declaration-history/'''+OLD+'''.
SURVIVAL: every required population-admitted comparison must be measured within
max(1,bar) or censored-bound-satisfied. A rail violation or measured miss binds.
Population-deficient bins are UNMEASURED, excluded from the test and counted.
Bound satisfaction meets a constraint, never measured accuracy evidence.
CLOSURE: a censored held-out cell is UNMEASURED (X21), contributes neither pass
nor coverage; all measured held-out cells must pass, and the measured coverage
fraction of the held-out set is mandatory. No suppressed failures or fictitious
coverage. These rules are the parent's charter v2.2 clause5/X31 ruling.
Numerical candidates bind the archive-ADMITTED cells, never the unadmitted
phase variants left in the original scenes declaration. The archive inventory
hash and every native role boundary remain unchanged.
Rendered held-out predictions are made BLIND before exposure from the public
scene backdrop/geometry and committed generated-backdrop bundle, never native
fixture/archive pixels. They are frozen by hash. Inside the receipt recapture
and require byte/projection equality BEFORE any native held-out scoring.
This is the parent's charter v2.3 clause11 clarification; G0 still captures nothing.
The parent confirms G-curvature is the NOMINAL-radius ladder: calibration
circles have R22 and32 CSS px; rrects retain their declared nominal22 CSS px.
It is NOT a differential local-curvature law along the continuous supplied
path. That path still controls support and normals. A local kappa(p) law is
not declared in W41 and must be declared by a later charter before fitting.
The following execution records bind exact optimizer/certificate-recovery
budgets before any native fit. Uncertified is a reportable numerical outcome,
never a pass, a certified family negative or permission to widen a tolerance.
'''
for name,digest in execution.items():text+=name+' SHA-256 '+digest+'\n'
text+='''
Standing sheets in G0 may read the already-committed canonical calibration and
validation fixtures/captures. Canonical holdout pixels, every W39 sheet pixel
and any browser remain closed. Missing W39 captures are UNMEASURED until G1.
This clarification authorizes no archive fit, capture or exposure.
'''
history=HERE/'declaration-history'/OLD
history.mkdir(parents=True,exist_ok=False)
for name in ['bounds-declaration.txt','closure.json','pins.json','declare.py']:
    shutil.copyfile(HERE/name,history/name)
(HERE/'bounds-declaration.txt').write_text(text)
new=sha(HERE/'bounds-declaration.txt')
closure=json.loads((HERE/'closure.json').read_text())
closure['boundsDeclarationSha256']=new
closure['supersededDeclarationHashes']=[OLD]
closure['charterRevision']='9e0ec5af6b6167e6e5463d9f10537e99bd88e10b'
closure['executionRecords']=execution
closure['families']['G-curvature'].update(calibrationCircleRadiiCSS=[22,32],rrectNominalRadiusCSS=22,localDifferentialCurvature=False)
closure['survival'].update(aggregation='every admitted comparison measured within bound or censored-bound-satisfied; any measured miss or rail violation binds',populationDeficient='UNMEASURED, excluded and counted')
closure['closure']=dict(aggregation='every measured held-out cell passes',censoredHeldout='UNMEASURED; neither pass nor coverage',report='measured/total held-out coverage fraction; bound satisfaction separate from measured maxima')
closure['receipt']['blindRenderedPredictions']='before exposure from public backdrop/geometry and committed generated rasters, never native fixture/archive pixels; inside receipt recapture and require byte/projection equality before native scoring'
closure['receipt']['numericalMembership']='archive-admitted glass cells intersecting unchanged declared roles; unadmitted phase variants excluded by inventory metadata'
closure['sheetsG0']=dict(allowedPixels='canonical calibration/validation only',closedPixels=['canonical holdout','all W39'],browser=False)
(HERE/'closure.json').write_text(json.dumps(closure,indent=2,allow_nan=False)+'\n')
pins=json.loads((HERE/'pins.json').read_text())
pins['boundsDeclarationSha256']=new
pins['supersededDeclarationHashes']=[OLD]
pins['closureSha256']=sha(HERE/'closure.json')
pins['executionRecords']=execution
charter='docs/doperpowers/specs/2026-09-27-w41-archive-reread.md'
pins['files'][charter]=sha(ROOT/charter)
(HERE/'pins.json').write_text(json.dumps(pins,indent=2)+'\n')
print(json.dumps(dict(superseded=OLD,current=new,execution=execution),indent=2))
