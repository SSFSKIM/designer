"""W42 G0 instrument: vitrea's own canonical web captures as cells, for proof 3 (the known-kernel control).

Reading discipline (the shared rules; the grounding's common rules): only canonical calibration, validation
and PROBE scenes are admitted, and only vitrea's WEB captures are opened here. No native pixel is opened by
proof 3. The canonical web-capture tree is gitignored and lives in the main checkout on the capture machine
(`packages/calibration/web-captures`); its cells were rendered with the SHIPPED macOS 27 documents (light
active 85ad7f7e3e0d, receded 30fbe05986ae, per each capture's `cell__webgpu.json`), whose body the code maps:
memo B's code-map (`~/vitrea-w42/grounding/kernel/code-map/kernels.json`, SHA-256 9c684eb9…) gives every
endpoint, scale and component's narrow kernel (chain L1, sigma_RMS 1.58 dev), deep kernel and share.
"""
import hashlib
import json
import os

import numpy as np
from PIL import Image

import geometry as G
import forward as F

WEB = f'{G.MAIN_REPO}/packages/calibration/web-captures'
CODE_MAP = os.path.expanduser('~/vitrea-w42/grounding/kernel/code-map')
KERNELS_SHA = '9c684eb920bee7b2da6f895a2e642d48a03f1e7abeff3a3432928d4f4c290c6e'
_S = json.load(open(G.CANON_SCENES))
ROLE = {s: k for k, v in _S['split'].items() if isinstance(v, list) and not k.startswith('$') for s in v}
ADMIT = {'calibration', 'validation', 'probe'}
POSE = {'rest': 'rest', 'inactive': 'inactive'}


def profile(scheme, scale):
    return f'apple-macos-27.0-{scale}x-{scheme}-standard-glass0.5'


def web_cell(scene, scheme, scale, tier='webgpu', rgb=False, d_in=None):
    """A forward.Cell for a canonical scene with vitrea's capture as its observed image."""
    role = ROLE.get(scene)
    assert role in ADMIT, f'refused: {scene} is {role}'
    bg, comp, state = scene.split('__')
    assert state in POSE, f'only plain rest/inactive states are read, not {state}'
    c = F.Cell(scene, bg, comp, scale, scheme, POSE[state], rgb=rgb, d_in=d_in)
    p = f'{WEB}/{profile(scheme, scale)}/{scene}/{scene}__{tier}.png'
    img = np.asarray(Image.open(p).convert('RGB'), dtype=np.float64)
    c.y = img if rgb else G.luma(img)
    c.capture = p
    c.role = role
    return c


def exists(scene, scheme, scale, tier='webgpu'):
    return os.path.exists(f'{WEB}/{profile(scheme, scale)}/{scene}/{scene}__{tier}.png')


def kernels():
    """memo B's code-map kernels, hash-checked: {(endpoint, scale, component): record}. Endpoint names are the
    code-map's ('light-active', 'light-receded', 'dark-active', 'dark-receded')."""
    p = f'{CODE_MAP}/kernels.json'
    assert hashlib.sha256(open(p, 'rb').read()).hexdigest() == KERNELS_SHA, 'kernels.json moved'
    return {(r['endpoint'], r['scale'], r['component']): r for r in json.load(open(p))['centre']}


CODE_EP = {'light-rest': 'light-active', 'light-inactive': 'light-receded', 'dark-rest': 'dark-active',
           'dark-inactive': 'dark-receded'}
CODE_COMP = {'capsule-button': 'capsule', 'rrect-sm': 'rrect-sm', 'rrect-md': 'rrect-md', 'rrect-ml': 'rrect-ml'}
