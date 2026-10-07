"""Land the dark capture generation, preserving the retired tree under its active document name.

W49a is a receded-only reseal: the new matrix filename includes both hashes, whereas
CLAUDE.md's capture archive names the retired tree by its active hash. The retiring
b2d074/29da6a generation has no existing b2d074 archive. Refuse a collision rather than
reuse an alias; matrix-store.loadGeneration requires the pair once the active is shared.
This script's only main-checkout writes are the authorised capture moves and copies.
"""
from pathlib import Path
import hashlib
import json
import shutil

HERE = Path(__file__).resolve().parent
MAIN = Path('/Users/new/Developer/GitHub/designer/packages/calibration')
CANONICAL = MAIN / 'web-captures'
RETIRED = MAIN / 'web-captures-superseded/b2d074d2df24'
STAGE = Path.home() / 'vitrea-w49/w49a-stage-dark/web-captures'
PROFILES = [f'apple-macos-27.0-{scale}x-dark-standard-glass0.25' for scale in (1, 2)]


def inventory(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file()}


def validate(root, receded):
    cells = sorted(root.glob('*/cell__*.json'))
    if len(cells) != 234:
        raise RuntimeError(f'{root}: expected 234 captures, found {len(cells)}')
    for p in cells:
        path = json.loads(p.read_text())['capturePath']
        if 'sha256:b2d074d2df24' not in path or f'sha256:{receded}' not in path:
            raise RuntimeError(f'{p}: wrong document pair')
    return [str(p.relative_to(root)) for p in cells]


def main():
    if RETIRED.exists():
        raise RuntimeError(f'{RETIRED} exists; inspect, never overwrite a retired generation')
    plans = []
    for profile in PROFILES:
        old, new = CANONICAL/profile, STAGE/profile
        if validate(old,'29da6a888a23') != validate(new,'940384c06f73'):
            raise RuntimeError(f'{profile}: capture membership differs')
        plans.append((profile, inventory(old), inventory(new)))
    RETIRED.mkdir()
    records = []
    for profile, old, new in plans:
        shutil.move(str(CANONICAL/profile), str(RETIRED/profile))
        shutil.copytree(STAGE/profile, CANONICAL/profile)
        if inventory(RETIRED/profile) != old or inventory(CANONICAL/profile) != new:
            raise RuntimeError(f'{profile}: copied/moved bytes differ')
        records.append(dict(profile=profile, movedFrom=str(CANONICAL/profile),
            movedTo=str(RETIRED/profile), copiedFrom=str(STAGE/profile),
            copiedTo=str(CANONICAL/profile), oldFiles=old, newFiles=new))
    out = HERE/'tree'
    out.mkdir(exist_ok=True)
    (out/'copy-manifest.json').write_text(json.dumps(dict(
        generation='b2d074d2df24-940384c06f73.json',
        retiredPair=['b2d074d2df24','29da6a888a23'], records=records),indent=2)+'\n')
    print(json.dumps([dict(profile=p, movedFiles=len(o),copiedFiles=len(n)) for p,o,n in plans],indent=2))

if __name__ == '__main__':
    main()
