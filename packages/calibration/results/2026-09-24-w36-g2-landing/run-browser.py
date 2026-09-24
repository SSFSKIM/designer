"""One X6-attested browser command, no retry (§5.180 clause 8, X6)."""
import datetime,importlib.util,os,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('w35_browser',HERE.parent/'2026-09-24-w35-g0-edge-cut/browser.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.HERE=HERE
label=sys.argv[1];command=sys.argv[2:]
original_log=m.log
renderer=command[command.index('--renderer')+1] if '--renderer' in command else 'suite'
def log(row):
    if 'renderer' in row:row={**row,'renderer':renderer}
    original_log(row)
m.log=log
out=HERE/(label+'.txt')
if out.exists():raise RuntimeError('Already attempted; no implicit retry: '+label)
m.preflight(label)
with out.open('x') as f:
    result=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,env=os.environ)
m.log(dict(label=label,completed=datetime.datetime.now(datetime.timezone.utc).isoformat(),exitCode=result.returncode,command=command))
print(label,'exit',result.returncode,'log',out)
raise SystemExit(result.returncode)
