"""W42 G2 step 2 (identification): the pins, recorded and committed before the first archive read.

`python3.12 -B pins.py write` records `pins.json`; every reader in this folder calls `verify()` at import and
refuses to run if any pinned byte has moved. What is pinned (charter G2 step 2; the parent's brief):

- the hashed declaration (`declaration.json`, SHA-256 f04ae95b...) and every one of its 92 pinned sources,
  re-hashed from the working tree or from the commit the declaration names;
- the two pre-read addenda, each by its full SHA-256: `native-t-addendum.md` (native T between strata and
  across sparse strata; T at s = 112 is (T96 + T128) / 2) and `candidate1-black-join-addendum.md`;
- the archive of record: GitHub release `w42-archive`, its asset by SHA-256 and byte size, and the archive's
  `inventory.json` by SHA-256, as G1 committed them (`2026-09-30-w42-g1-sitting/archive/`);
- the repeat bar G1 published (`bar/bar.json.gz`'s decompressed SHA-256, and its headlines);
- the instrument and oracle files step 2 imports, by SHA-256.

Reading rule: only the roles calibration and validation, through the wave's guarded Reader
(`bed/sitting/w42_archive.py`, `bed/wave.py`); the holdout H is withheld by that Reader and never requested;
the raw sitting root `~/vitrea-w42/g1` is denied by an audit hook in every process that reads.
"""
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVID = HERE.parent
RESULTS = EVID.parent
REPO = RESULTS.parents[2]
DECL = RESULTS / '2026-09-29-w42-g0-declaration'
G1 = RESULTS / '2026-09-30-w42-g1-sitting'
PINS = HERE / 'pins.json'

DECLARATION_SHA = 'f04ae95b626c7547cc3dbae11e08cb04a89ef642680d0b4f509c6c833633381c'
ADDENDA = {
    'native-t-addendum.md': '23e400bffb923db7c2453c0ed6062a3c4b4217d1217817adb635ef7eb7085362',
    'candidate1-black-join-addendum.md': '8ad314c13047722c22869b2bd46d1691f1adfd232ccb1209b48264c5ca52a1f6',
}
ARCHIVE = dict(tag='w42-archive', repo='SSFSKIM/designer',
               asset='w42-archive-1e3d6e65fa3b9a621f1d0f80fb03cc79ee76c29d9b001174983689a7aed31014.tar.zst',
               sha256='1e3d6e65fa3b9a621f1d0f80fb03cc79ee76c29d9b001174983689a7aed31014', bytes=13611249,
               inventorySha256='5481795e0a77ef246f6743d2b6bbe2111a79d858ff9b7a2a4571255595940ed7',
               verifiedCopy=str(Path.home() / 'vitrea-w42' / 'archive-copy'))
BAR_JSON_SHA = 'a85662f2eacba16613c6470407a5f0d7469569d4a4918f1ab0047ae0c6b8ccf0'
RAW_ROOT = Path.home() / 'vitrea-w42' / 'g1'
# The files step 2 imports or reads as its oracle, beyond the declaration's own pins.
USED = [
    DECL / 'instrument' / n for n in ('forward.py', 'families.py', 'fitting.py', 'tone.py', 'regions.py',
                                      'geometry.py', 'bed.py', 'proof_common.py', 'refraction_order.py',
                                      'resolution.json', 'tolerances.json')
] + [
    DECL / 'bed' / n for n in ('bed.json', 'scenes-w42-body.json', 'wave.py', 'pins.json',
                               'sitting/w42_archive.py')
] + [
    EVID / 'implementation-design' / 'native_t.py',
    EVID / 'implementation-design' / 'candidate1_black_join.py',
    DECL / 'gate' / 'rehearsal' / 'body.py',
    DECL / 'gate' / 'rehearsal' / 'swap.py',
] + [
    RESULTS / '2026-09-27-w41-g1-identification' / 'body' / 'attempt-1' / f'{ep}-E3-fit.json'
    for ep in ('light-active', 'light-inactive', 'dark-active', 'dark-inactive')
] + [G1 / 'archive' / 'inventory.json', G1 / 'bar' / 'bar-headlines.json', G1 / 'bar' / 'report-bars.py']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rel(p):
    return str(Path(p).resolve().relative_to(REPO))


def declaration_sources():
    d = json.loads((DECL / 'declaration.json').read_bytes())
    bad = []
    for key, want in d['sources'].items():
        if '@' in key:
            path, commit = key.rsplit('@', 1)
            data = subprocess.run(['git', '-C', str(REPO), 'show', f'{commit}:{path}'], check=True,
                                  capture_output=True).stdout
        else:
            data = (REPO / key).read_bytes()
        if sha(data) != want:
            bad.append(key)
    return len(d['sources']), bad


def current():
    decl = sha((DECL / 'declaration.json').read_bytes())
    n, bad = declaration_sources()
    bar_raw = gzip.decompress((G1 / 'bar' / 'bar.json.gz').read_bytes())
    return dict(
        schema='w42-g2-step2-pins-1',
        what='W42 G2 step 2 (identification): pins recorded before the first archive read',
        declaration=dict(path=rel(DECL / 'declaration.json'), sha256=decl,
                         recorded=(DECL / 'declaration.sha256').read_text().split()[0],
                         sourcesPinned=n, sourcesMismatched=bad),
        addenda={name: dict(path=rel(EVID / name), sha256=sha((EVID / name).read_bytes())) for name in ADDENDA},
        archive=ARCHIVE,
        archiveInventoryCommitted=dict(path=rel(G1 / 'archive' / 'inventory.json'),
                                       sha256=sha((G1 / 'archive' / 'inventory.json').read_bytes())),
        bar=dict(path=rel(G1 / 'bar' / 'bar.json.gz'), decompressedSha256=sha(bar_raw),
                 rule='0.5 + half the largest pairwise separation of the seven run medians; 0.5 on all 27,777'),
        used={rel(p): sha(p.read_bytes()) for p in USED},
        readingRule=dict(roles=['calibration', 'validation'], holdout='never requested; withheld by the Reader',
                         rawRootDenied=str(RAW_ROOT)),
        python=sys.version.split()[0],
    )


def check(value):
    errors = []
    if value['declaration']['sha256'] != DECLARATION_SHA or value['declaration']['recorded'] != DECLARATION_SHA:
        errors.append('declaration hash')
    if value['declaration']['sourcesMismatched']:
        errors.append('declaration sources: ' + ', '.join(value['declaration']['sourcesMismatched']))
    for name, want in ADDENDA.items():
        if value['addenda'][name]['sha256'] != want:
            errors.append('addendum ' + name)
    if value['archiveInventoryCommitted']['sha256'] != ARCHIVE['inventorySha256']:
        errors.append('committed archive inventory')
    if value['bar']['decompressedSha256'] != BAR_JSON_SHA:
        errors.append('bar')
    return errors


def verify():
    """Refuse unless every pin recorded in pins.json still holds."""
    want = json.loads(PINS.read_text())
    now = current()
    errors = check(now)
    for k in ('declaration', 'addenda', 'archive', 'archiveInventoryCommitted', 'bar', 'used'):
        if now[k] != want[k]:
            errors.append(f'{k} differs from pins.json')
    if errors:
        raise SystemExit('PIN CHECK FAILED: ' + '; '.join(errors))
    return want


if __name__ == '__main__':
    if sys.argv[1:] == ['write']:
        value = current()
        errors = check(value)
        if errors:
            raise SystemExit('refusing to write pins: ' + '; '.join(errors))
        PINS.write_text(json.dumps(value, indent=1, sort_keys=True) + '\n')
        print('pins.json written;', len(value['used']), 'used files;',
              value['declaration']['sourcesPinned'], 'declaration sources verified')
    else:
        verify()
        print('pins hold')
