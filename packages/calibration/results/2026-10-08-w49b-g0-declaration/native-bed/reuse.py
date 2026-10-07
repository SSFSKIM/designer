"""Small adapters over W43's instrument; no native action happens on import."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
W43 = REPO / 'packages/calibration/results/2026-10-01-w43-g0-declaration/bed/sitting'
_CACHE = {}


def load(name, path):
    if name not in _CACHE:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        _CACHE[name] = mod
    return _CACHE[name]


def pass_spec():
    P = load('w49b_pass_spec', W43 / 'pass-spec.py')
    P.BED_DIR, P.REPO, P.SITTINGS = HERE, REPO, ('native',)
    # W43 reserved cut-safe closing passes for W42 archive sentinels. W49b instead
    # closes against committed canonical 0.25 frames, with the same stop/order law.
    P.CLOSE_ROLE = 'bridge-canonical'
    return P


def recorder():
    R = load('w49b_recorder', W43 / 'record-machine.py')
    R.SIDE = Path(json.loads((HERE / 'bundle-pin.json').read_bytes())['path'])
    if not getattr(R, '_w49b_bound', False):
        R._w49b_bound = True
        base_read = R.read

        def read(*argv):
            if argv and argv[0] == 'python3.12':
                argv = (sys.executable, *argv[1:])
            return base_read(*argv)

        R.read = read
    return R


def driver():
    S = load('w49b_sitting', W43 / 'sitting.py')
    if getattr(S, '_w49b_bound', False):
        return S
    S._w49b_bound = True
    S.HERE, S.REPO, S.BED_DIR, S.DECL_DIR = HERE, REPO, HERE, HERE
    S.DECLARATION = HERE / 'bed-declaration.json'
    S.DECLARATION_DIGEST = HERE / 'declaration.sha256'
    S.W39_PIN = HERE / 'bundle-pin.json'
    S.W39_PIN_REL = str(S.W39_PIN.relative_to(REPO))
    S.pass_spec, S.recorder_module = pass_spec, recorder
    base_pin_check = S.pinned_declaration

    def pinned_declaration(sitting, predeclaration=False):
        if predeclaration:
            raise ValueError('W49b has no predeclaration native rehearsal path')
        record = base_pin_check(sitting, False)
        doc = json.loads(S.at_head(S.DECLARATION))
        for row in doc['files']:
            raw = S.at_head(REPO / row['path'])
            if hashlib.sha256(raw).hexdigest() != row['sha256']:
                raise ValueError('declared instrument or bed changed: ' + row['path'])
        record['nativeBedSha256'] = doc['manifestSha256']
        return record

    S.pinned_declaration = pinned_declaration
    base_bridge = S.bridge_verdict

    def bridge_verdict(frame_raw, reference_raw, background, component, scale, scheme, pose,
                       bars=None, cell=''):
        # The transfer canvas is a centred 128-point extension on every side.
        # Its bridge backgrounds repeat every 64 points (or are uniform), so this
        # exact centre crop preserves input phase and supplied-path placement.
        from PIL import Image
        import io
        with Image.open(io.BytesIO(frame_raw)) as image:
            if image.size == (576 * scale, 456 * scale):
                crop = image.crop((128 * scale, 128 * scale, 448 * scale, 328 * scale))
                out = io.BytesIO()
                crop.save(out, format='PNG')
                verdict = base_bridge(out.getvalue(), reference_raw, background, component,
                                      scale, scheme, pose, bars, cell)
                verdict.update(transferFrameSha256=hashlib.sha256(frame_raw).hexdigest(),
                               cropCss=[128, 128, 320, 200])
                return verdict
        return base_bridge(frame_raw, reference_raw, background, component, scale,
                           scheme, pose, bars, cell)

    S.bridge_verdict = bridge_verdict
    return S


def timing():
    T = load('w49b_timing', W43 / 'timing.py')
    T.pass_spec = pass_spec
    return T


def require_capture_approval():
    """An external, user-authorised readiness receipt is required before any live action.

    This is an operational interlock, not a source of user consent. The parent must
    obtain the user's X5 lift and bundle/grant choice; this worker creates no receipt.
    """
    path = os.environ.get('W49B_CAPTURE_APPROVAL')
    if not path:
        raise ValueError('X5 is not lifted for this instrument: no W49B_CAPTURE_APPROVAL receipt; '
                         'no native launch, process termination or settings write is allowed')
    p = Path(path).expanduser().resolve()
    if p.is_relative_to(REPO):
        raise ValueError('the X5/bundle readiness receipt must live outside the checkout')
    receipt = json.loads(p.read_bytes())
    required = {'x5UserDecision': str, 'bundleGrantUserDecision': str,
                'screenRecordingGrantVerified': bool}
    if any(not isinstance(receipt.get(k), kind) or not receipt[k] for k, kind in required.items()):
        raise ValueError('X5 and a positively verified user-granted bundle are both required')
    for name, field in (('bundle-pin.json', 'bundlePinSha256'),
                        ('bed-declaration.json', 'declarationSha256')):
        digest = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        if receipt.get(field) != digest:
            raise ValueError('the X5 readiness receipt names another ' + name)
    chosen = os.environ.get('W49B_PYTHON')
    if not chosen or Path(chosen).resolve() != Path(sys.executable).resolve() \
            or receipt.get('pythonExecutable') != chosen:
        raise ValueError('W49B_PYTHON and the readiness receipt must bind this scientific interpreter')
    if sys.version_info[:3] != (3, 14, 6):
        raise ValueError('scientific Python differs from the declared 3.14.6')
    import numpy
    import PIL
    import scipy
    if (numpy.__version__, PIL.__version__, scipy.__version__) != ('2.5.3', '12.3.0', '1.18.1'):
        raise ValueError('scientific runtime differs from requirements.txt')
    if os.environ.get('W43_PREDECLARATION') or os.environ.get('REHEARSAL'):
        raise ValueError('W49b admits no live rehearsal or predeclaration bypass')
