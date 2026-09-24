"""Guarded transport to existing native-mask metrics; no path-shaped pixel API."""
import base64,hashlib,json,subprocess,sys
from pathlib import Path
from cut import HERE,edge
from w35_readers import WebReader
cell=sys.argv[1]
projection={r['cell']:r for r in json.loads((HERE/'projection.json').read_text())}
row=projection[cell]
plan=next(p for p in json.loads((HERE/'candidate-plans.json').read_text()) if p['profile']==cell.split('/')[0])
reader=WebReader.w34(Path(plan['root'])/'web-captures') if row['origin']=='w34' else WebReader.canonical(Path(plan['root'])/'web-captures')
raw=reader.read(cell)
checks={c['cell']:c for r in map(json.loads,(HERE/'browser-runs.txt').read_text().splitlines()) for c in r.get('checks',[])}
assert checks[cell]['used'] and hashlib.sha256(raw).hexdigest()==checks[cell]['pngSha256']
p=subprocess.run(['python3.12',str(edge.HERE/'export-cell.py'),row['origin'],cell],capture_output=True,text=True,check=True)
value=json.loads(p.stdout);value['candidate']=base64.b64encode(raw).decode()
print(json.dumps(value))
