"""Closing CPU verification, with every exit recorded (§5.179)."""
import json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
commands=[('close-build',['pnpm','-r','build']),('close-lint',['pnpm','-r','lint']),
 ('close-calibration',['pnpm','--filter','@vitrea/calibration','--fail-if-no-match','test']),
 ('close-renderer-unit',['pnpm','--filter','@vitrea/renderer-webgpu','--fail-if-no-match','test'])]
rows=[]
for label,cmd in commands:
    with (HERE/(label+'.txt')).open('x') as f:
        run=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    rows.append(dict(label=label,command=cmd,exitCode=run.returncode));print(label,run.returncode,flush=True)
with (HERE/'close-cpu.json').open('x') as f:json.dump(rows,f,indent=2);f.write('\n')
raise SystemExit(int(any(r['exitCode'] for r in rows)))
