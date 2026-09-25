"""Reproduce G0 without rewriting its recorded absolute worktree provenance."""
import gzip,json,subprocess,sys
from common import G0,HERE,edge
ns={'__file__':str(G0/'replay.py')}
exec(compile((G0/'replay.py').read_text().split("if '--verify' in sys.argv:")[0],str(G0/'replay.py'),'exec'),ns)
prior=json.loads(gzip.decompress((G0/'native-replay.json.gz').read_bytes()));actual=ns['output']
paths={k:{'recorded':prior[k],'current':actual[k]} for k in ['source','guard']}
assert {k:v for k,v in actual.items() if k not in paths}=={k:v for k,v in prior.items() if k not in paths}
if '--verify-native' in sys.argv:
    print('Native numeric reproduction exact; absolute provenance paths retained separately.')
    raise SystemExit(0)
edge.save(HERE/'g0-replay-reproduction.json',dict(cells=actual['cells'],numericDifference=0,
    exactExceptAbsoluteWorktreePaths=paths,reason='G0 replay --verify compares absolute worktree paths; numeric evidence is identical. No G0 file changed.'))
for script in ['verify-scores.py','derived.py']:
    command=['python3.12',str(G0/script)]+(['--verify'] if script=='derived.py' else [])
    result=subprocess.run(command,capture_output=True,text=True)
    (HERE/('g0-'+script+'.txt')).write_text(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError(script+' failed; retained its output')
