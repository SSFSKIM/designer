"""W50's narrow adapters over W43's protected sitting, with no implicit native launch."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import signal
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
W43 = ROOT/'packages/calibration/results/2026-10-01-w43-g0-declaration/bed/sitting'
APP = Path('/Users/new/vitrea-w39/side/VitreaReference.app')
CLIENT = 'dev.vitrea.reference-apple.w39'
PIN = ROOT/'packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/bundle-pin.json'
MODULES = {}


def load(name, path):
    if name not in MODULES:
        spec = importlib.util.spec_from_file_location(name, path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        MODULES[name] = m
    return MODULES[name]


def driver():
    return load('w50_protected_driver', W43/'sitting.py')


def recorder():
    r = load('w50_process_recorder', W43/'record-machine.py')
    # W43 predates the Chrome-for-Testing name without the Google prefix. Retain its
    # executable/entry-script rule while admitting every supported Chrome variant to census.
    r.FOREIGN_EXECUTABLES = re.compile(
        r'^(Chromium|Google Chrome|Chrome for Testing)\b|Chrome Helper|headless[-_ ]shell|^VitreaReference$')
    r.FOREIGN_BUNDLES = re.compile(r'^(Chromium|Google Chrome[^/]*|Chrome for Testing)\.app$')
    return r


def grant_row(rows):
    matching = [r for r in rows if r.get('service') == 'kTCCServiceScreenCapture'
                and r.get('client') == CLIENT and r.get('client_type') == 0]
    positive = len(matching) == 1 and matching[0].get('auth_value') == 2 and bool(matching[0].get('csreq'))
    return dict(positive=positive, rows=matching,
                reason='positive auth=2 row; identity still to check' if positive else 'no unique positive grant')


def grant_check():
    """Read TCC only. Never invokes the app or a request API; unreadable is not permission."""
    query = ("select service,client,client_type,auth_value,hex(csreq) as csreq,last_modified from access "
             "where service='kTCCServiceScreenCapture' and client='dev.vitrea.reference-apple.w39';")
    result = subprocess.run(['sqlite3', '-readonly', '-json',
                             '/Library/Application Support/com.apple.TCC/TCC.db', query],
                            capture_output=True, text=True)
    if result.returncode:
        return dict(positive=False, reason='TCC read unavailable', error=result.stderr.strip())
    verdict = grant_row(json.loads(result.stdout or '[]'))
    pin = json.loads(PIN.read_bytes())
    binary = APP/'Contents/MacOS/VitreaReference'
    digest = hashlib.sha256(binary.read_bytes()).hexdigest() if binary.is_file() else None
    signature = subprocess.run(['codesign', '-dvvv', str(APP)], capture_output=True, text=True)
    cd = re.search(r'^CDHash=(.+)$', signature.stderr, re.M)
    identity = digest == pin['binarySha256'] and cd is not None and cd[1] == pin['cdhash']
    verdict.update(binarySha256=digest, cdhash=cd[1] if cd else None, unchangedBundle=identity)
    if verdict['positive'] and identity:
        # Validate the grant's own compiled requirement against these exact bundle bytes.
        with tempfile.TemporaryDirectory(prefix='w50-grant-') as td:
            req = Path(td)/'requirement.bin'
            req.write_bytes(bytes.fromhex(verdict['rows'][0]['csreq']))
            check = subprocess.run(['codesign', '-v', '-R', str(req), str(APP)],
                                   capture_output=True, text=True)
            verdict['requirementMatches'] = check.returncode == 0
            verdict['positive'] = verdict['requirementMatches']
            if not verdict['positive']:
                verdict.update(reason='TCC auth=2 exists, but signed-bundle requirement validation failed',
                               error=check.stderr.strip() or check.stdout.strip(),
                               requirementExitCode=check.returncode)
    elif not identity:
        verdict.update(positive=False, reason='Pinned bundle identity check failed; no launch attempted',
                       error=signature.stderr.strip() if signature.returncode else 'Binary or CDHash differs from pin')
    else:
        verdict.update(positive=False, reason='No unique positive TCC grant; no launch attempted')
    if verdict['positive']:
        verdict['reason'] = 'grant and unchanged signed bundle match'
    return verdict


def chrome_family(executable):
    """The outer browser bundle owns its nested helpers, independent of channel or app spelling."""
    path = Path(executable)
    for parent in reversed(path.parents):
        if recorder().FOREIGN_BUNDLES.fullmatch(parent.name):
            return str(parent)
    if re.match(r'^(Google Chrome|Chrome for Testing|Chromium)\b', path.name):
        return str(path.parent)
    return None


def classify(rows):
    """Executable/entry-script census, preserving W43's launcher identity exclusions upstream."""
    r = recorder()
    candidates = [(row, r.foreign_reason(row), chrome_family(row['executable'])) for row in rows]
    automation = re.compile(r'--enable-automation|--remote-debugging-(pipe|port)|--headless|ms-playwright')
    automated = {family for row, _, family in candidates if family and
                 (automation.search(' '.join(row['argv'])) or re.search(r'Chromium|Testing', family))}
    capture_browser = bool(automated) or any(re.search(r'Chromium|headless[-_ ]shell|chrome-headless',
                                                row['executable']) for row, _, _ in candidates)
    refused, annotated = [], []
    for row, why, family in candidates:
        if why is None:
            continue
        name = Path(row['executable']).name
        if family and family not in automated:
            annotated.append(dict(row, classification='user Chrome'))
        elif r.INTERPRETERS.match(name) and 'playwright' in str(r.entry_point(row['argv'])).lower() \
                and not capture_browser:
            annotated.append(dict(row, classification='browserless relay'))
        else:
            refused.append(dict(row, classification='capture process'))
    return dict(refuse=refused, annotate=annotated)


def machine(phase):
    r = recorder()
    rows = r.process_table()
    foreign, excluded = r.census(rows=rows)
    allowed = {(q['pid'], q['start']) for q in foreign}
    result = classify([q for q in rows if (q['pid'], q['start']) in allowed])
    original = r.census
    try:
        # Classify the SAME process-table snapshot whose launcher identities were excluded.
        r.census = lambda: (result['refuse'], excluded)
        observation = r.machine(phase)
    finally:
        r.census = original
    observation.update(annotatedProcesses=result['annotate'], gate='W50 classifying census (DL3)')
    return observation


def restore(slider, display):
    """A failure restoring one resource cannot prevent restoring the other; repeated signals wait."""
    signals = (signal.SIGHUP, signal.SIGINT, signal.SIGTERM)
    previous = {s: signal.signal(s, signal.SIG_IGN) for s in signals}
    results = {}
    try:
        for name, action in (('slider', slider), ('display', display)):
            try:
                results[name] = action()
            except BaseException as error:
                results[name] = dict(restored=False, error=f'{type(error).__name__}: {error}')
        return dict(restored=all(v.get('restored') is True for v in results.values()), **results)
    finally:
        for s, handler in previous.items():
            signal.signal(s, handler)


if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['grant-check']:
        answer = grant_check()
        print(json.dumps(answer, indent=2))
        raise SystemExit(0 if answer['positive'] else 1)
    if len(sys.argv) != 2:
        raise SystemExit('usage: safety.py grant-check | <machine-read phase>')
    print(json.dumps(machine(sys.argv[1]), indent=2))
