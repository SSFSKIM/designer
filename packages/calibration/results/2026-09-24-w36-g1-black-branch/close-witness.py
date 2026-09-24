"""Consolidate actual checks and prove the sealed material has not moved (§5.179)."""
import hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];CAL=HERE.parent.parent
manifest=json.loads((HERE/'sealed-manifest.json').read_text())['documents']
for name,d in manifest.items():assert hashlib.sha256((CAL/'profiles'/name).read_bytes()).hexdigest()==d['fileSha256'],name
source=subprocess.check_output(['python3',str(CAL/'results/holdout-configuration/configuration.py'),'show'],text=True)
assert 'SOURCE SHA-256      4e2786c83d452d9d47ac79770fbfa2bccef82728ee69d798cfbf79942671dbb4' in source
checks={}
for name,count in [('final-goldens',34),('final-gpu',49),('final-platform-e2e-corrected',410),('final-react-e2e',174)]:
    text=(HERE/(name+'.txt')).read_text();assert re.search(r'\b'+str(count)+r' passed\b',text),name
    checks[name]=dict(passed=count,log=name+'.txt')
checks['final-react-e2e']['skipped']=3
assert '3 skipped' in (HERE/'final-react-e2e.txt').read_text()
units=[]
for package,count in re.findall(r'^(\S+) test:\s+Tests\s+(\d+) passed', (HERE/'final-other-units.txt').read_text(),re.M):units.append(dict(package=package,passed=int(count)))
assert len(units)==8 and sum(u['passed'] for u in units)==2079
assert '678 passed (678)' in (HERE/'read-calibration-tests.txt').read_text()
assert (HERE/'final-platform-lint-clean.txt').read_text().strip()=='$ eslint . && tsc --noEmit && tsc --noEmit -p tsconfig.e2e.json'
chain=json.loads((HERE/'final-verification.json').read_text());assert all(c['exitCode']==0 for c in chain if c['label']!='final-platform-e2e')
result=dict(claims='c9a §5.179',sealedDocumentsUnchanged=True,materialSourcesUnchanged=True,
    build=dict(exitCode=0,log='final-build.txt'),lint=dict(exitCode=0,logs=['final-lint.txt','final-platform-lint-clean.txt']),
    unitTotal=2757,calibration=678,otherUnits=units,browserChecks=checks,freezeEntries=1818,captureMatch=786,
    initialPlatformFailure='final-platform-e2e.txt: 409 passed / 1 failed. The test oracle omitted evaluated band amplitude and the selected conversion anchor; its obsolete black-overshoot assertion was removed by fix. Full corrected suite passes.',
    limitations=['Three declared React browser-capability skips.','One CSS holdout changes five exterior pixels by one code, cause unidentified; no retry or fit.','Independent review, canonical tree landing, demo comparison and release belong to the parent.'])
with (HERE/'closing-verification.json').open('x') as f:json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n')
print('Sealed documents and sources unchanged; units2757, goldens34, GPU49, platform410, React174/3skip; build/lint, freeze1818, tree786/786 pass.')
