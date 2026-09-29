#!/usr/bin/env python3.12
"""Copy the declared examples (examples-declaration.json as amended by examples-amendment.json)
out of scratch sheet runs into examples/, byte for byte, and bind each copy to its run
inventory's hashes in examples/selection.json. Only declared identities are copied; an undeclared file is never
promoted and an existing example is never overwritten.
usage: select-examples.py <run inventory.json> [...]"""
import hashlib
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
EXAMPLES = HERE / 'examples'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    declaration = json.loads((HERE / 'examples-declaration.json').read_text())
    amendment_path = HERE / 'examples-amendment.json'
    amendment = json.loads(amendment_path.read_text())
    if amendment['amends']['sha256'] != sha(HERE / 'examples-declaration.json'):
        raise SystemExit('amendment does not amend this declaration')
    withdrawn = {w['ordinal'] for w in amendment['withdrawn']}
    declared = [e for e in declaration['examples'] if e['ordinal'] not in withdrawn] + amendment['added']
    found = {}
    for inventory_path in map(Path, sys.argv[1:]):
        inventory = json.loads(inventory_path.read_text())
        for record in inventory['records']:
            if record.get('status', '').startswith('RENDERED'):
                found[(record['bed'], record['profileKey'], record['sceneId'])] = (inventory_path, record)
    EXAMPLES.mkdir(exist_ok=True)
    selection_path = EXAMPLES / 'selection.json'
    selection = json.loads(selection_path.read_text()) if selection_path.exists() else {
        'declaration': 'examples-declaration.json',
        'declarationSha256': sha(HERE / 'examples-declaration.json'), 'examples': []}
    if selection['declarationSha256'] != sha(HERE / 'examples-declaration.json'):
        raise SystemExit('declaration changed after selection began')
    selection['amendment'] = 'examples-amendment.json'
    selection['amendmentSha256'] = sha(amendment_path)
    selection['withdrawnOrdinals'] = sorted(withdrawn)
    done = {e['ordinal'] for e in selection['examples']}
    for example in declared:
        key = (example['bed'], example['profileKey'], example['sceneId'])
        if example['ordinal'] in done or key not in found:
            continue
        inventory_path, record = found[key]
        stem = f"{example['ordinal']:02d}__{example['bed']}__{example['profileKey']}__{example['sceneId']}"
        files = {}
        for kind in ('html', 'png'):
            source = inventory_path.parent / record[kind]
            if sha(source) != record[f'{kind}Sha256']:
                raise SystemExit(f'{source}: differs from its inventory')
            target = EXAMPLES / f'{stem}.{kind}'
            if target.exists():
                raise SystemExit(f'{target}: exists')
            shutil.copyfile(source, target)
            files[kind] = dict(path=f'examples/{target.name}', sha256=sha(target), scratchPath=str(source))
        selection['examples'].append(dict(
            ordinal=example['ordinal'], bed=example['bed'], profileKey=example['profileKey'],
            sceneId=example['sceneId'], reason=example['reason'], runInventory=str(inventory_path),
            runInventorySha256=sha(inventory_path), preEqualsNowBytes=record['preEqualsNowBytes'],
            distances=record['distances'], files=files))
    selection['examples'].sort(key=lambda e: e['ordinal'])
    missing = [e['ordinal'] for e in declared
               if e['ordinal'] not in {x['ordinal'] for x in selection['examples']}]
    selection['pendingOrdinals'] = missing
    selection_path.write_text(json.dumps(selection, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(dict(selected=len(selection['examples']), pending=missing)))


if __name__ == '__main__':
    main()
