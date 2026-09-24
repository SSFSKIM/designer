"""One closing chain at the completed read, with no implicit browser retry (§5.179)."""
import json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
assert (HERE/'read-witness.json').is_file(), 'Finish and split the read before its closing chain'
calibration_log=(HERE/'read-calibration-tests.txt').read_text()
assert '678 passed (678)' in calibration_log and '47 passed (47)' in calibration_log
rows=[dict(label='final-calibration',command=['pnpm','--filter','@vitrea/calibration','--fail-if-no-match','test'],exitCode=0,
    evidenceLog='read-calibration-tests.txt',reuse='Already run after split and cut regeneration; no relevant file has changed since.') ]
commands=[('final-build',['pnpm','-r','build']),('final-lint',['pnpm','-r','lint']),
 ('final-other-units',['pnpm','--filter','!@vitrea/calibration','--fail-if-no-match','-r','test'])]
for label,cmd in commands:
    with (HERE/(label+'.txt')).open('x') as f:run=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    rows.append(dict(label=label,command=cmd,exitCode=run.returncode));print(label,run.returncode,flush=True)
# One worker for every suite: no browser suite contends with a capture pass or
# with another suite. Existing project exclusions and hardware requirements stay.
browsers=[('final-goldens',['pnpm','--dir',str(ROOT),'--filter','@vitrea/renderer-webgpu','--fail-if-no-match','run','test:golden']),
 ('final-gpu',['pnpm','--dir',str(ROOT),'--filter','@vitrea/renderer-webgpu','--fail-if-no-match','run','test:gpu']),
 ('final-platform-e2e',['pnpm','--dir',str(ROOT),'--filter','@vitreajs/vitrea-web','--fail-if-no-match','exec','playwright','test','--workers=1','--retries=0']),
 ('final-react-e2e',['pnpm','--dir',str(ROOT),'--filter','@vitreajs/vitrea-react','--fail-if-no-match','exec','playwright','test','--workers=1','--retries=0'])]
for label,cmd in browsers:
    run=subprocess.run(['python3.12',str(HERE/'run-browser.py'),label,*cmd],cwd=ROOT)
    rows.append(dict(label=label,command=cmd,exitCode=run.returncode));print(label,run.returncode,flush=True)
for label,cmd in [('final-freeze',['python3',str(ROOT/'packages/calibration/results/2026-09-16-w29-freeze/freeze.py'),'verify']),
 ('final-capture-tree',['pnpm','--filter','@vitrea/calibration','--fail-if-no-match','run','check-capture-tree'])]:
    with (HERE/(label+'.txt')).open('x') as f:run=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    rows.append(dict(label=label,command=cmd,exitCode=run.returncode));print(label,run.returncode,flush=True)
with (HERE/'final-verification.json').open('x') as f:json.dump(rows,f,indent=2);f.write('\n')
raise SystemExit(int(any(r['exitCode'] for r in rows)))
