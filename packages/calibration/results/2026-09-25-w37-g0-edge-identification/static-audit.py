"""Historical artifact reductions beside the fresh guarded pixel replay; not new captures."""
import collections,gzip,hashlib,json,re
from law import HERE,edge
old=HERE.parent/'2026-09-24-w35-g0-edge-cut';g=HERE.parent/'2026-09-24-w36-g1-black-branch'
metrics=json.loads((old/'canonical-metrics.json').read_text())['rows']
widths=[dict(cell=r['cell'],nativeRim=r['nativeRim']) for r in metrics if r['cell'].endswith('/dark-solid__rrect-md__rest')]
fits=[{k:v for k,v in r.items() if k!='rows'} for r in json.loads((old/'native-grey-law-fits.json').read_text())]
wave=edge.W.default_wave();profiles=json.loads(gzip.decompress((old/'profiles.json.gz').read_bytes()))
roles=collections.Counter(r['role'] for r in profiles)
material=json.loads((g/'resolved-materials.json').read_text())
leaves={scheme:material[f'apple-macos-27.0-1x-{scheme}-standard-glass0.5']['optics']['regular'] for scheme in ['light','dark']}
log=(g/'final-goldens.txt').read_text();golden=int(re.search(r'\n\s+(\d+) passed \(',log).group(1))
probe=wave.reader(edge.G1/'probe');inventory=collections.Counter(wave.roles[r['cell'].split('/')[1]] for r in probe.report_inventory() if r['kind']=='png' and wave.roles[r['cell'].split('/')[1]]!='holdout')
value=dict(widthArtifact='W35 actual rimIntensity output, reduced without re-running estimator; not physical CSS line width',widths=widths,historicalGreyFits=fits,materialLeaves=leaves,glassCells=dict(roles),admittedProbePngs=dict(inventory),historicalGoldenPasses=golden,goldenRerun=False)
edge.save(HERE/'static-audit.json',value)
print(json.dumps({k:v for k,v in value.items() if k not in ['historicalGreyFits','materialLeaves','widths']},indent=2))
