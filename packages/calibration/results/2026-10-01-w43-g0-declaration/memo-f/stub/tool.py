#!/usr/bin/env python3.12
"""memo F's stub tools, for the proof only: one file, copied under each tool's name into a
throwaway tools directory by `proof.sh`, which dispatches on the name it is called by.

Nothing here touches the machine's real state:
- `defaults` runs the REAL /usr/bin/defaults, but only against a sandbox domain named in
  `state.json`: every `-g` / NSGlobalDomain argument is rewritten to the sandbox, any other write
  or delete is refused, and the accessibility reads answer from `state.json`. So the proof
  exercises the real tool's export, read-type and plist-value semantics on the one key without
  ever writing the global domain.
- `open` launches nothing real. It emulates `open -W … VitreaReference.app --args dump-layers …`:
  it reads the sandbox slider AT LAUNCH (a fresh launch reads the current value), runs the stub
  harness binary (a copy of /bin/sleep under the stub harness's name) for the dump's length, and
  writes one dump per scene from memo D's own dumps (~/vitrea-w42/grounding/dumps/runs/, each
  checked against the grounding's committed scratch-sha256.txt). It sets
  `inputBlurFillNormalOpacity` to the slider it read, and in light the Lighten opacity and the
  face fill's alpha to W29 G0's light readings (0.675 + 0.45x capped at 0.9; 0.4x to 0.5, then
  0.2 + 0.6(x - 0.5)). Those ramps exist only so the reader has something to find; at x = 0.5
  the dump is memo D's byte for byte in content. Faults are injected by launch number.
- `displayplacer`, `read-session`, `sw_vers` and `codesign` answer from `state.json`.
"""
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
STATE = HERE / 'state.json'
MEMO_D = Path.home() / 'vitrea-w42/grounding'
MANIFEST = Path(__file__).resolve().parent / 'scratch-sha256.txt'
GLOBAL = ('-g', '-globalDomain', 'NSGlobalDomain', 'Apple Global Domain')


def state():
    return json.loads(STATE.read_text())


def save(s):
    STATE.write_text(json.dumps(s, indent=1))


def log(name, argv):
    with open(HERE / 'calls.log', 'a') as f:
        f.write(json.dumps(dict(tool=name, argv=argv, at=time.time())) + '\n')


def defaults(argv):
    s = state()
    domain = s['sandbox']
    if len(argv) >= 2 and argv[0] == 'read' and argv[1] in [d for d, _ in s['a11yKeys']]:
        value = s['a11y'].get(f'{argv[1]} {argv[2]}')
        if value is None:
            print(f'The domain/default pair of ({argv[1]}, {argv[2]}) does not exist', file=sys.stderr)
            return 1
        print(value)
        return 0
    args = [domain if a in GLOBAL else a for a in argv]
    if any(a in GLOBAL for a in args):
        print('stub defaults: refused, a global-domain argument survived the rewrite', file=sys.stderr)
        return 70
    if args[0] in ('write', 'delete', 'import', 'rename') and (len(args) < 2 or args[1] != domain):
        print(f'stub defaults: refused, {args[0]} outside the sandbox domain', file=sys.stderr)
        return 70
    fault = s.get('faults', {})
    if args[0] == 'write' and fault.get('writeFails'):
        return 1
    if (args[0] == 'delete' or (args[0] == 'write' and '<real>' in ' '.join(args))) and fault.get('restoreFails'):
        print('stub defaults: injected restore failure', file=sys.stderr)
        return 1
    return subprocess.run(['/usr/bin/defaults', *args]).returncode


def sandbox_slider(s):
    out = subprocess.run(['/usr/bin/defaults', 'export', s['sandbox'], '-'], capture_output=True)
    domain = plistlib.loads(out.stdout) if out.returncode == 0 else {}
    return domain.get('NSGlassTintAmount', 0.5)   # an absent key draws at 0.5 (W29 G0)


def verified_template(scale, scheme, pose, scene):
    rel = f'dumps/runs/{scale}x-{scheme}-{pose}/json/{scene}.json'
    want = {line.split()[1]: line.split()[0] for line in MANIFEST.read_text().splitlines() if line.strip()}
    raw = (MEMO_D / rel).read_bytes()
    import hashlib
    if want.get(rel) != hashlib.sha256(raw).hexdigest():
        raise SystemExit(f'stub open: memo D template {rel} is not the hashed scratch')
    return json.loads(raw)


def patch(tree, x, scheme):
    def walk(n):
        if isinstance(n, dict):
            if n.get('class') == 'CABackdropLayer':
                for f in n.get('filters') or []:
                    inputs = f.get('inputs') or {}
                    if 'inputBlurFillNormalOpacity' in inputs:
                        inputs['inputBlurFillNormalOpacity'] = x
                        if scheme == 'light':
                            inputs['inputBlurFillLightenOpacity'] = min(0.9, 0.675 + 0.45 * x)
                            alpha = 0.4 * x if x <= 0.5 else 0.2 + 0.6 * (x - 0.5)
                            inputs['inputFaceColorMatrixFillColor']['cgColorComponents'][3] = alpha
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)
    walk(tree)


def depart(tree):
    """An injected departure from memo D that is not the slider: the narrow blur's radius 5 -> 6."""
    def walk(n):
        if isinstance(n, dict):
            for f in n.get('filters') or []:
                if 'inputBlurRadius' in (f.get('inputs') or {}):
                    f['inputs']['inputBlurRadius'] = 6
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)
    walk(tree)


def open_(argv):
    s = state()
    s['launches'] = s.get('launches', 0) + 1
    n = s['launches']
    save(s)
    fault = {k: v for k, v in s.get('faults', {}).items() if v == n}
    env, i = {}, 0
    while argv[i] != str(HERE / 'VitreaReference.app'):
        if argv[i] == '--env':
            k, v = argv[i + 1].split('=', 1)
            env[k] = v
            i += 2
        elif argv[i] in ('--stdout', '--stderr'):
            env[argv[i]] = argv[i + 1]
            i += 2
        else:
            i += 1
    rest = argv[i + 2:]
    opt = {rest[j]: rest[j + 1] for j in range(1, len(rest) - 1) if rest[j].startswith('--') and
           not rest[j + 1].startswith('--')}
    scale, scheme = int(env['VITREA_SCALE']), opt['--scheme']
    pose = 'inactive' if '--inactive' in rest else 'active'
    x = sandbox_slider(s)
    if 'stale' in fault:
        x = s.get('lastSlider', x)
    s = state()
    s['lastSlider'] = x
    save(s)
    binary = HERE / 'VitreaReference.app/Contents/MacOS' / (HERE / 'harness-name').read_text().strip()
    if 'orphan' in fault:
        subprocess.Popen([str(binary), '30'], start_new_session=True)
    harness = subprocess.Popen([str(binary), '8' if 'slow' in fault else '0.2'])
    out = Path(opt['--out'])
    out.mkdir(parents=True, exist_ok=True)
    scenes = opt['--scenes'].split(',')
    if 'missing' in fault:
        scenes = scenes[:-1]
    for scene in scenes:
        tree = verified_template(scale, scheme, pose, scene)
        patch(tree, x, scheme)
        if 'depart' in fault:
            depart(tree)
        if 'unkey' in fault and pose == 'active':
            tree['isKeyWindow'] = tree['appIsActive'] = False
        (out / f'{scene}.json').write_text(json.dumps(tree))
    Path(env['--stdout']).write_text(f'stub dump-layers: {len(scenes)} scenes at slider {x!r}\n')
    Path(env['--stderr']).write_text('')
    harness.wait()
    return 1 if 'fail' in fault else 0


def displayplacer(argv):
    s = state()
    if argv and argv[0] == 'list':
        for mode in (68, 69):
            print(f'  mode {mode}: res:2560x1440 hz:60 color_depth:4 scaling:{"on" if mode == 68 else "off"}'
                  + (' <-- current mode' if s['mode'] == mode else ''))
        return 0
    mode = int(argv[0].rsplit('mode:', 1)[1])
    if s.get('faults', {}).get('modeSticks'):
        return 0
    s['mode'] = mode
    save(s)
    return 0


def read_session(_argv):
    s = state()
    print(json.dumps(s['session']))
    return 0


def sw_vers(argv):
    s = state()
    print(s['build'] if argv == ['-buildVersion'] else s['product'])
    return 0


def codesign(_argv):
    s = state()
    print(f"Identifier={s['identifier']}\nCDHash={s['cdhash']}", file=sys.stderr)
    return 0


TOOLS = {'defaults': defaults, 'open': open_, 'displayplacer': displayplacer, 'read-session': read_session,
         'sw_vers': sw_vers, 'codesign': codesign}

if __name__ == '__main__':
    name = Path(sys.argv[0]).name
    log(name, sys.argv[1:])
    sys.exit(TOOLS[name](sys.argv[1:]))
