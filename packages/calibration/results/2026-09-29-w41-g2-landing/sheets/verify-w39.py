#!/usr/bin/env python3.12
"""W41 G2: do G1's 536 W39 standing sheets already show the shipped E3 pixels? (c9a §5.193)

G1 rendered one Native | Shipped | Candidate sheet per admitted W39 calibration/validation
cell (§5.192 §19), its candidate column being G1's scratch E3 capture. G2 sealed that E3 and
re-rendered the same 600 cells from the sealed documents (../identity/). This checks, per
cell, rather than re-rendering 536 sheets:

  1. G1's committed sheet inventory (render-inventory.json.gz) decompresses to the primary
     inventory's recorded SHA-256, and names 536 RENDERED W39 cells.
  2. The G2 identity capture of that cell exists, its metadata names the SEALED document
     pair (live bytes), and its PNG SHA-256 equals the candidate capture G1's sheet was
     rendered from and identity/comparison.json's entry.
  3. G1's scratch sheet HTML and PNG still have the hashes G1's inventory records.
  4. The Candidate image embedded in that HTML decodes to exactly the identity capture's
     RGBA pixels. The sheet re-encodes each image, so this is a pixel comparison, not a
     file-hash one: it is what makes "the sheet shows the shipped pixels" literal.

It also counts the cells the seal did not move (G1's baseline PNG == the identity PNG).
Only the calibration/validation identity tree is opened; the 64 blind W39 cells are not.
No native payload, browser or capture. Writes one JSON report to stdout.
"""
import base64
import gzip
import hashlib
import io
import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import sys

from PIL import Image

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
ROOT = CAL.parents[1]
G1 = CAL / 'results/2026-09-27-w41-g1-identification/sheets'
INVENTORY_SHA256 = 'f52dbcb03a9b164fbafb916a400c14e79c8d8405d1ae4a6b83a487e62064f44e'
G1_SCRATCH = Path('/Users/new/vitrea-w41/g1-captures/sheets/run-1')
IDENTITY = Path('/Users/new/vitrea-w41/g2-captures/identity/calval')
SEALED = {
    'light': {'materialProfile': 'packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.5.json',
              'recededProfile': 'packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json'},
    'dark': {'materialProfile': 'packages/calibration/profiles/apple-macos-27.0-1x-dark-standard-glass0.5.json',
             'recededProfile': 'packages/calibration/profiles/apple-macos-27.0-1x-dark-standard-glass0.5-receded.json'},
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Images(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.images = {}

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            a = dict(attrs)
            if a['alt'] in self.images:
                raise ValueError('duplicate panel ' + a['alt'])
            self.images[a['alt']] = a['src']


def rgba(png_bytes):
    with Image.open(io.BytesIO(png_bytes)) as image:
        image.load()
        if image.mode not in ('RGB', 'RGBA'):
            raise ValueError('unexpected PNG mode ' + image.mode)
        return image.size, image.convert('RGBA').tobytes()


EXPECTED = {'light': ('85ad7f7e3e0d', '003940b4c7da'), 'dark': ('0eac5b294cc2', '5cec8c961201')}


def sealed_pair(scheme):
    pair = {}
    for (kind, path), expected in zip(SEALED[scheme].items(), EXPECTED[scheme]):
        digest = sha((ROOT / path).read_bytes())[:12]
        if digest != expected:
            raise SystemExit(f'{path} is {digest}, not the sealed {expected}')
        pair[kind] = f'{path} sha256:{digest}'
    return pair


def main():
    raw = gzip.decompress((G1 / 'render-inventory.json.gz').read_bytes())
    if sha(raw) != INVENTORY_SHA256:
        raise SystemExit('G1 sheet inventory does not decompress to its recorded primary hash')
    inventory = json.loads(raw)
    comparison = json.loads((HERE.parent / 'identity/comparison.json').read_text())['cells']
    pairs = {scheme: sealed_pair(scheme) for scheme in SEALED}
    records = [r for r in inventory['records'] if r['bed'] == 'w39']
    rendered = [r for r in records if r.get('status') == 'RENDERED']
    unmeasured = [f"{r['profileKey']}/{r['sceneId']}" for r in records if r.get('status') != 'RENDERED']
    if len(rendered) != 536:
        raise SystemExit(f'expected 536 rendered W39 sheets, found {len(rendered)}')
    failures, cells = [], {}
    unmoved = Counter()
    for r in rendered:
        cell = f"{r['profileKey']}/{r['sceneId']}"
        problems = []
        scheme = 'dark' if '-dark-' in r['profileKey'] else 'light'
        pose = 'inactive' if r['sceneId'].endswith('__inactive') else 'rest'
        directory = IDENTITY / r['profileKey'] / r['sceneId']
        png_path = directory / f"{r['sceneId']}__webgpu.png"
        identity_png = png_path.read_bytes()
        identity_sha = sha(identity_png)
        meta = json.loads((directory / 'cell__webgpu.json').read_text())
        for kind, clause in pairs[scheme].items():
            if f'{kind}={clause}' not in meta['capturePath']:
                problems.append(f'identity metadata does not name the sealed {kind}')
        if meta['sceneId'] != r['sceneId'] or meta['renderer'] != 'webgpu':
            problems.append('identity metadata names another scene or renderer')
        candidate_sha = r['candidate']['capture']['pngSha256']
        if identity_sha != candidate_sha:
            problems.append('identity PNG differs from the G1 candidate capture')
        if comparison.get(cell, {}).get('pngSha256') != identity_sha or \
                comparison[cell].get('status') != 'identical':
            problems.append('identity/comparison.json does not record this PNG as identical')
        html = (G1_SCRATCH / r['html']).read_bytes()
        if sha(html) != r['htmlSha256']:
            problems.append('G1 sheet HTML changed')
        if sha((G1_SCRATCH / r['png']).read_bytes()) != r['pngSha256']:
            problems.append('G1 sheet PNG changed')
        parser = Images()
        parser.feed(html.decode('utf-8'))
        prefix = 'data:image/png;base64,'
        embedded = parser.images.get('Candidate', '')
        if not embedded.startswith(prefix):
            problems.append('G1 sheet has no embedded Candidate image')
        elif rgba(base64.b64decode(embedded[len(prefix):], validate=True)) != rgba(identity_png):
            problems.append('embedded Candidate pixels differ from the identity capture')
        baseline_sha = r['shipped']['pngSha256']
        same_as_pre = baseline_sha == identity_sha
        if same_as_pre:
            unmoved[f"{r['profileKey']}/{pose}"] += 1
        cells[cell] = dict(identityPngSha256=identity_sha, g1CandidatePngSha256=candidate_sha,
                           g1BaselinePngSha256=baseline_sha, sealUnmoved=same_as_pre,
                           g1SheetHtmlSha256=r['htmlSha256'], g1SheetPngSha256=r['pngSha256'],
                           status='VERIFIED' if not problems else 'FAILED', problems=problems)
        if problems:
            failures.append(cell)
    moved = Counter(f"{c.split('/')[0]}/{'inactive' if c.endswith('__inactive') else 'rest'}"
                    for c, v in cells.items() if not v['sealUnmoved'])
    report = dict(
        schema='w41-g2-w39-sheet-verification-1',
        g1Inventory=dict(path='packages/calibration/results/2026-09-27-w41-g1-identification/sheets/'
                         'render-inventory.json.gz', decompressedSha256=INVENTORY_SHA256),
        identityRoot=str(IDENTITY), g1SheetRoot=str(G1_SCRATCH),
        sealedDocuments=pairs,
        summary=dict(w39Memberships=len(records), rendered=len(rendered),
                     verified=len(rendered) - len(failures), failed=failures,
                     unmeasuredMemberships=unmeasured,
                     sealUnmovedByProfilePose=dict(sorted(unmoved.items())),
                     sealMovedByProfilePose=dict(sorted(moved.items())),
                     blindCellsOpened=0, nativePayloadsOpened=0),
        meaning='VERIFIED: the identity capture names the sealed documents, its PNG is the file G1 '
                'rendered as Candidate (hash) and the pixels embedded in G1\'s sheet (decoded RGBA), and '
                'G1\'s sheet files are unchanged. G1\'s W39 sheets therefore show the shipped E3 pixels in '
                'their Candidate column; their "Shipped WebGPU" column is the pre-W41 material.',
        cells=cells)
    json.dump(report, sys.stdout, indent=1, sort_keys=False)
    sys.stdout.write('\n')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
