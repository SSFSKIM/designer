"""Assert the rehearsal's contents and rewritten ranges (§5.180 clause 8)."""
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / '.vitrea-tmp/w36-g2-pack'
records = []
for package in ['vitrea', 'vitrea-web', 'vitrea-react']:
    path = OUT / f'vitreajs-{package}-0.24.0.tgz'
    with tarfile.open(path) as archive:
        names = archive.getnames()
        for required in ['LICENSE', 'NOTICE', 'README.md']:
            assert 'package/' + required in names
        dist = [n for n in names if n.startswith('package/dist/')]
        assert dist
        document = json.load(archive.extractfile('package/package.json'))
        assert document['version'] == '0.24.0'
        for name, version in document.get('dependencies', {}).items():
            if name.startswith('@vitreajs/'):
                assert version == '^0.24.0'
        assert 'workspace:' not in json.dumps(document)
        records.append(dict(name=document['name'], version=document['version'],
            bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            dependencies=document.get('dependencies', {}),
            peerDependencies=document.get('peerDependencies', {}), distEntries=len(dist),
            requiredFiles=True))
with (HERE / 'pack-check.json').open('x') as f:
    json.dump(records, f, indent=2)
    f.write('\n')
print(json.dumps(records, indent=2))
