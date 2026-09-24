"""CSS counterpart price at exactly the GPU candidate bytes; no fitted CSS constant (§5.179)."""
import json,os,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
plans=json.loads((HERE/'candidate-plans.json').read_text())
for plan in plans:
    command=list(plan['command']);command[command.index('--renderer')+1]='css'
    result=subprocess.run(['python3.12',str(HERE/'run-browser.py'),'price-css-'+plan['profile'],*command],env={**os.environ,**plan['environment']})
    # A metric refusal is not a missing or nondeterministic capture. Keep it;
    # the price reader separately names the unmeasured metric and checks pixels.
    captures=Path(plan['root'])/'web-captures'/plan['profile']
    for sid in plan['scenes']:
        meta=json.loads((captures/sid/'cell__css.json').read_text())
        assert meta['deterministic'] and meta['repeatNoise']==0 and meta['renderer']=='css'
print('CSS captures present and deterministic:',sum(len(p['scenes']) for p in plans))
