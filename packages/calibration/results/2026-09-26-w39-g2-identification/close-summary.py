"""Assemble the gate outcome from committed corrected reports; no new measurement."""
import gzip
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
body_path=HERE/'body-correction/correction-attempt-1.json.gz'
edge_path=HERE/'edge-correction/attempt-2/summary.json'
body=json.loads(gzip.decompress(body_path.read_bytes()));edge=json.loads(edge_path.read_text())
bs=[]
for family in ['H1','H2','H2prime','H3','H3prime']:
 method={'H2prime':'multistartMinimaxCandidate','H3':'globalMinimax','H3prime':'multistartMinimaxCandidate'}.get(family,'minimax')
 for r in body['summary']:
  if r['family']==family and r['method']==method and r['population']=='colour':
   assert r['status']=='failed';bs.append(r)
es=[];support=[]
for endpoint in ['light-active','light-inactive','dark-active','dark-inactive']:
 for scale in [1,2]:
  for method in ['leastSquares','minimax']:
   rows=[r for r in edge['summary'] if r['endpoint']==endpoint and r['scale']==scale and r['method']==method and r['sourceKind']=='all' and r['stateIndex']==0]
   worst=max(rows,key=lambda r:r['worstUncensored']['codes'])['worstUncensored']
   assert worst['codes']>worst['toleranceCodes']
   es.append(dict(endpoint=endpoint,scale=scale,method=method,status='failed',worst=worst,
      failingBins=sum(r['failingBins'] for r in rows),failingChannels=sum(r['failingChannels'] for r in rows)))
  rows=[r for r in edge['summary'] if r['endpoint']==endpoint and r['scale']==scale and r['method']=='support' and r['sourceKind']=='all' and r['role']=='calibration']
  assert len(rows)==8 and all(r['failingChannels']>0 for r in rows)
  support.append(dict(endpoint=endpoint,scale=scale,allSevenRunsAndMedianFail=True,
      worst=next(r for r in rows if r['stateIndex']==0)['worstUncensored']))
assert len(bs)==40 and len(es)==16 and len(support)==8
out=dict(schema='w39-g2-outcome-1',
 declarationSha256='94cebb42735a22f345b0a877ca5137d3355e84e78d09b12c9fabf67f0ba3faae',
 archiveSha256='489db938a1e234a772ba7223d24fbaf76d137ef5d9e5b2421ed84a86894426b5',
 inventorySha256='58329732f947d42cd5e1518962016191faaa79d89b7089c6dadf5724dde35f61',
 inputs={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [body_path,edge_path]},
 bodySurvival=bs,edgeSurvival=es,supportCertificate=support,H4='not applicable: no surviving body law identified',
 nonlinearQualification='H2prime/H3prime candidate failures, not certified global exclusions',
 survivingCandidates=[],freezeForExposure=None,exposureRan=False,holdout='analytically sealed; no receipt spent',
 resolution='not evaluated: no surviving predictions; not an insufficient-resolution finding',
 transferRange=None,cssReach='not entered: no survivor',decisionLog2='recommendation only; user rules')
with (HERE/'outcome.json').open('x') as f:json.dump(out,f,indent=2,allow_nan=False);f.write('\n')
print('Body strata40; selected edge strata16; support strata8; no survivors or exposure.')
