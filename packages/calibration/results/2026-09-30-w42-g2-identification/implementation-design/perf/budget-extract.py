import json, sys, re
tag = sys.argv[1]
out = []
rows = {}
for i in (1, 2, 3):
    d = json.load(open(f'/tmp/w42-perf/budget-{tag}-{i}.json'))
    def walk(s):
        for spec in s.get('specs', []):
            for t in spec['tests']:
                for r in t['results']:
                    yield r, t
        for sub in s.get('suites', []):
            yield from walk(sub)
    for suite in d['suites']:
        for r, t in walk(suite):
            status = r['status']
            anns = list(dict.fromkeys(a['description'] for a in t.get('annotations', []) + r.get('annotations', []) if a['type'] == 'bench'))
            out.append(f'## run {i} ({status})')
            out.extend(sorted(anns))
            for a in anns:
                m = re.match(r'([^:]+): gpu\(median\)=([\d.]+|n/a)ms? .*wall\(median\)=([\d.]+)ms.*?\| (.*)', a)
                if m:
                    passes = dict(p.split('=') for p in m.group(4).split())
                    rows.setdefault(m.group(1), []).append((float(m.group(3)), float(passes.get('body-law', 0))))
print('\n'.join(out))
print()
for label, v in sorted(rows.items()):
    print(f'{label:40s} wall ' + ' / '.join(f'{w:.1f}' for w, _ in v) + '   body-law ' + ' / '.join(f'{b:.2f}' for _, b in v))
