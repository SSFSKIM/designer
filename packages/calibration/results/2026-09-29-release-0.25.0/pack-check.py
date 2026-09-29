"""Assert the 0.25.0 rehearsal's tarballs and count what each one exports.

    python3 pack-check.py

W36 G2's pack-check.py at 0.25.0, plus the export count the cold installs of
0.21.0-0.24.0 recorded (core 44 / web 258 / react 38 at 0.24.0). The count is
taken off the PACKED bytes rather than the workspace: the three tarballs are
extracted into a scratch consumer's node_modules, `react` and `react-dom` are
linked from the workspace (the only peers), and node imports each entry point
under native ESM. No network, no registry, no publish. Writes pack-check.json
exclusively.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
VERSION = '0.25.0'
OUT = ROOT / '.vitrea-tmp/rel-0.25.0-pack'
CONSUMER = ROOT / '.vitrea-tmp/rel-0.25.0-consumer'
records = []
if CONSUMER.exists():
    shutil.rmtree(CONSUMER)
modules = CONSUMER / 'node_modules'
(modules / '@vitreajs').mkdir(parents=True)
(CONSUMER / 'package.json').write_text('{"type": "module", "private": true}\n')
for peer in ['react', 'react-dom']:
    os.symlink((ROOT / 'packages/react/node_modules' / peer).resolve(), modules / peer)
for package in ['vitrea', 'vitrea-web', 'vitrea-react']:
    path = OUT / f'vitreajs-{package}-{VERSION}.tgz'
    with tarfile.open(path) as archive:
        names = archive.getnames()
        for required in ['LICENSE', 'NOTICE', 'README.md']:
            assert 'package/' + required in names, (package, required)
        dist = [n for n in names if n.startswith('package/dist/')]
        assert dist, package
        document = json.load(archive.extractfile('package/package.json'))
        assert document['version'] == VERSION, document['version']
        for name, version in document.get('dependencies', {}).items():
            if name.startswith('@vitreajs/'):
                assert version == '^' + VERSION, (name, version)
            assert not name.startswith('@vitrea/'), name
        assert 'workspace:' not in json.dumps(document)
        target = modules / '@vitreajs' / package
        target.mkdir()
        for member in archive.getmembers():
            if member.isfile():
                relative = Path(member.name).relative_to('package')
                (target / relative).parent.mkdir(parents=True, exist_ok=True)
                (target / relative).write_bytes(archive.extractfile(member).read())
    records.append(dict(name=document['name'], version=document['version'],
        bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        dependencies=document.get('dependencies', {}),
        peerDependencies=document.get('peerDependencies', {}), distEntries=len(dist),
        requiredFiles=True))
for record in records:
    count = subprocess.check_output(['node', '--input-type=module', '-e',
        f"const m = await import({json.dumps(record['name'])}); console.log(Object.keys(m).length)"],
        cwd=CONSUMER, text=True).strip()
    record['exports'] = int(count)
with (HERE / 'pack-check.json').open('x') as f:
    json.dump(records, f, indent=2)
    f.write('\n')
print(json.dumps(records, indent=2))
