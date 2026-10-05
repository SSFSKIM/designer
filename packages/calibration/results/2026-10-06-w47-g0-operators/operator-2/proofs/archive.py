#!/usr/bin/env python3.12
"""Archive completed operator2 proof runs; refuse partial evidence and overwriting.

Run after both background jobs succeed and identity.py read exits0. Repeat PNGs and op1-replay
PNGs stay in scratch: their raw hashes must equal the first recording or prior committed op1 tree.
Canonical identity PNGs are not duplicated; their full byte hashes and matrix rows are preserved.
"""
from pathlib import Path
import hashlib,json,re,shutil,subprocess
HERE=Path(__file__).resolve().parent
OP=HERE.parent
SCRATCH=Path.home()/'vitrea-w47/op2-proofs'
IDENTITY=Path.home()/'vitrea-w47/op2-identity'
CANONICAL=Path('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')

def main():
 labels=('before-1','before-2','after-1','after-2','op1-replay')
 for label in labels:
  assert (SCRATCH/label/'cases.json').is_file(),label
  log=(SCRATCH/f'{label}.log').read_text()
  assert re.search(r'\b1 passed\b',log),label
 for label in ('before-goldens','after-goldens'):
  assert re.search(r'\b34 passed\b',(SCRATCH/f'{label}.log').read_text()),label
 assert re.search(r'\b1 passed\b',(SCRATCH/'after-assertions.log').read_text())
 assert 'failures: none' in (OP/'identity.txt').read_text()
 for label in labels:
  target=HERE/label
  if target.exists():raise SystemExit(f'{target} exists; never overwrite a proof')
  target.mkdir()
  shutil.copy2(SCRATCH/label/'cases.json',target/'cases.json')
  if label in ('before-1','after-1'):shutil.copytree(SCRATCH/label/'png',target/'png')
 logs=HERE/'gpu-logs';logs.mkdir(exist_ok=False)
 for label in (*labels,'before-goldens','after-goldens','after-assertions'):
  shutil.copy2(SCRATCH/f'{label}.log',logs/f'{label}.txt')
 subprocess.run(['python3.12','-B',str(HERE/'compare.py')]
  + (['--check'] if (HERE/'comparison.json').exists() else []),check=True)
 shutil.copy2(HERE/'comparison.txt',OP/'compare.txt')
 b=json.loads((HERE/'before-1/cases.json').read_text());a=json.loads((HERE/'after-1/cases.json').read_text())
 manifest=[dict(png=f"{label.replace('/','__')}.png",before=b[label]['sha256'],after=a[label]['sha256'],
  identical=b[label]['sha256']==a[label]['sha256'],identity=b[label]['identity'],
  hashKind='SHA256 of decoded raw RGBA, not PNG container') for label in sorted(b)
  if not label.startswith('golden/')]
 with (OP/'png-sha256.json').open('x') as f:f.write(json.dumps(manifest,indent=1)+'\n')
 records=[]
 archive=HERE/'identity';archive.mkdir(exist_ok=False)
 for scale in ('1x','2x'):
  for tier in ('webgpu','css'):
   target=archive/scale/tier;target.mkdir(parents=True)
   for name in ('matrix.json','compare.log'):shutil.copy2(IDENTITY/scale/tier/name,target/name)
  for p in sorted((IDENTITY/scale/'captures').rglob('*.png')):
   rel=p.relative_to(IDENTITY/scale/'captures');ref=CANONICAL/rel
   ours=hashlib.sha256(p.read_bytes()).hexdigest();theirs=hashlib.sha256(ref.read_bytes()).hexdigest()
   assert ours==theirs,str(rel)
   records.append(dict(capture=str(rel),ours=ours,canonical=theirs))
 assert len(records)==168,len(records)
 (archive/'png-sha256.json').write_text(json.dumps(records,indent=1)+'\n')
 print(f'Archived {len(b)} GPU cases and {len(records)} identity PNG hashes; all comparison predicates pass.')
if __name__=='__main__':main()
