#!/usr/bin/env python3.12
"""W42 G0 — the referees' candidate-admission mode, red and green (charter clause 10; Design,
"The instrument (G0)").

    OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3.12 -B test_admission.py \
        | tee admission-test.txt

GREEN base: every script here in base mode against W41 G2's committed port run the same way
from its own folder (the current union, canonical captures; then one stage of unchanged
rows), byte for byte, chroma-cut's `generatedAt` wall clock and scratch-union's printed
output path set aside.

GREEN candidate: two scratch stages, light and dark, built from the four standard macOS 27
profiles' non-holdout WebGPU rows. The control pair names the shipped documents; the
candidate pair names candidate documents that are the shipped bytes plus one
"$comment-w42-g0-admission-test" key (the resolved material is identical and only the file
hash moves), with a scratch capture tree whose metadata names them. Every script reads the
control in base mode and the candidate with --candidate; each output must equal the
control's once the stamps are removed and the document names, hashes and the digests over
rows naming them are mapped back. Before mapping, the candidate chroma cut's
`shippedDocuments` must name the four candidates (the gate review of b151aff4, finding 11).

RED: a wrong =SHA12, the candidate's bytes changed after the rows were written (declared
with and without its hash), base mode on the candidate stages, a candidate under
profiles/, overlapping stages, a candidate without a stage and a candidate no stage
declares: every row reader refuses, names the mismatch and writes nothing.

Scratch lives under /tmp/w42-gate-admission/test. The candidate documents must be
repo-relative paths, so they are written to .admission-scratch/ beside this file and removed
on exit; that directory is never committed. No canonical holdout or recorded pixel is
opened: the capture tree copies calibration, validation and probe cells only.
"""
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
CAL = HERE.parents[3]
ROOT = CAL.parent.parent
RESULTS = CAL / 'results'
W41 = RESULTS / '2026-09-29-w41-g2-landing/referees'
CAN = Path('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures').resolve()
SCRATCH = Path('/tmp/w42-gate-admission/test').resolve()  # the scripts resolve /tmp too
CANDIDATES = HERE / '.admission-scratch'
sys.path.insert(0, str(RESULTS / '2026-09-26-w40-g0-generations'))
import matrix_store as store  # noqa: E402

PROFILES = 'packages/calibration/profiles/'
SCHEMES = {
    scheme: dict(profiles=[f'apple-macos-27.0-{s}-{scheme}-standard-glass0.5' for s in ('1x', '2x')],
                 active=f'{PROFILES}apple-macos-27.0-1x-{scheme}-standard-glass0.5.json',
                 receded=f'{PROFILES}apple-macos-27.0-1x-{scheme}-standard-glass0.5-receded.json')
    for scheme in ('light', 'dark')
}
ROW_READERS = ['chroma-cut', 'exterior-cut', 'l1-cut', 'black-cut', 'e2-regression',
               'scratch-union']
ENV = {k: v for k, v in os.environ.items() if k != 'VITREA_MATRIX_PATH'}
ENV.update(OPENBLAS_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
failures = []


def say(line=''):
    print(line, flush=True)


def check(ok, line):
    say(('  ok    ' if ok else '  FAIL  ') + line)
    if not ok:
        failures.append(line)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


# ---------------------------------------------------------------------------------------------
# Scratch: stages, candidate documents, capture tree
# ---------------------------------------------------------------------------------------------

def envelope(raws):
    return (b'{\n  "schemaVersion": 5,\n  "cells": [\n    ' + b',\n    '.join(raws) +
            b'\n  ]\n}\n')


def clause(kind, path, digest):
    return f'{kind}={path} sha256:{digest}'


def build():
    roles = json.loads((ROOT / 'apps/reference-apple/scenes.json').read_text())['split']
    role = {sid: r for r, sids in roles.items() for sid in sids}
    current = store.load_current_rows(matrix_path=str(RESULTS / 'matrix.json'))
    built = {}
    for scheme, spec in SCHEMES.items():
        shipped = {kind: (spec[kind], sha((ROOT / spec[kind]).read_bytes()))
                   for kind in ('active', 'receded')}
        candidate = {}
        for kind, (path, _) in shipped.items():
            raw = (ROOT / path).read_bytes()
            assert raw.startswith(b'{\n')
            doc = CANDIDATES / scheme / Path(path).name
            doc.parent.mkdir(parents=True, exist_ok=True)
            doc.write_bytes(b'{\n  "$comment-w42-g0-admission-test": "the shipped document plus '
                            b'this key: the resolved material is identical, the hash moves",\n'
                            + raw[2:])
            parsed = json.loads(doc.read_bytes())
            parsed.pop('$comment-w42-g0-admission-test')
            assert parsed == json.loads(raw)
            candidate[kind] = (str(doc.relative_to(ROOT)), sha(doc.read_bytes()))
        pairs = {(p, 'webgpu') for p in spec['profiles']}
        held = [r for r in current if (r['key']['profileKey'], r['key']['web']['renderer']) in pairs]
        # Every declared cell of the pairs, holdout included by KEY only; the stage holds no
        # holdout row, as a G2 stage will not (holdout is read once, after the freeze).
        cells = sorted({(r['key']['profileKey'], 'webgpu', r['fixtureSet'], r['key']['sceneId'])
                        for r in held})
        rows = [r for r in held if r['fixtureSet'] != 'holdout']
        swaps = [(clause(k, shipped[s][0], shipped[s][1][:12]),
                  clause(k, candidate[s][0], candidate[s][1][:12]))
                 for k, s in (('materialProfile', 'active'), ('recededProfile', 'receded'))]
        control_raw, candidate_raw = [], []
        for row in rows:
            raw = store._RAW[id(row)]
            control_raw.append(raw)
            for old, new in swaps:
                assert raw.count(old.encode()) == 1, (row['key']['sceneId'], old)
                raw = raw.replace(old.encode(), new.encode())
            candidate_raw.append(raw)
        stages = {}
        for name, raws, documents in (('control', control_raw, shipped),
                                      ('candidate', candidate_raw, candidate)):
            stage = SCRATCH / 'stages' / f'{name}-{scheme}'
            stage.mkdir(parents=True)
            (stage / 'matrix.json').write_bytes(envelope(raws))
            (stage / 'membership.json').write_text(json.dumps(dict(
                schemaVersion=1, profiles=spec['profiles'], tiers=['webgpu'],
                sets=sorted({c[2] for c in cells}),
                active=dict(path=documents['active'][0], sha256=documents['active'][1][:12]),
                receded=dict(path=documents['receded'][0], sha256=documents['receded'][1][:12]),
                cells=[dict(profileKey=p, renderer=t, fixtureSet=f, sceneId=s)
                       for p, t, f, s in cells]), indent=2) + '\n')
            stages[name] = stage
        # The candidate's capture tree: the canonical PNG bytes under metadata naming the
        # candidate documents. Calibration, validation and probe cells only; copies, since the
        # readers refuse a payload that resolves outside the declared root.
        copied = 0
        for row in rows:
            profile, sid = row['key']['profileKey'], row['key']['sceneId']
            if role.get(sid) not in ('calibration', 'validation', 'probe'):
                continue
            source = CAN / profile / sid
            if not (source / 'cell__webgpu.json').exists():
                continue
            meta = json.loads((source / 'cell__webgpu.json').read_text())
            assert meta['capturePath'] == row['key']['web']['capturePath'], (profile, sid)
            path = meta['capturePath']
            for old, new in swaps:
                assert path.count(old) == 1
                path = path.replace(old, new)
            meta['capturePath'] = path
            target = SCRATCH / 'captures' / profile / sid
            target.mkdir(parents=True)
            shutil.copyfile(source / f'{sid}__webgpu.png', target / f'{sid}__webgpu.png')
            (target / 'cell__webgpu.json').write_text(json.dumps(meta, indent=2) + '\n')
            copied += 1
        built[scheme] = dict(shipped=shipped, candidate=candidate, stages=stages,
                             rows=len(rows), cells=len(cells), copied=copied)
    return built


# ---------------------------------------------------------------------------------------------
# Running the scripts
# ---------------------------------------------------------------------------------------------

def run(folder, script, args):
    done = subprocess.run([sys.executable, '-B', str(folder / f'{script}.py'), *map(str, args)],
                          cwd=folder, env=ENV, capture_output=True, text=True)
    return done.returncode, done.stdout, done.stderr


def cuts(folder, out, source, captures, union=False):
    """Every script into `out`: {script: [(file name, bytes)]}; each must exit 0."""
    out.mkdir(parents=True)
    steps = [
        ('chroma-cut', [*source, '--out', out / 'chroma-cut.json'], ['chroma-cut.json']),
        ('m2-rebaseline', ['--cut', out / 'chroma-cut.json', '--out', out / 'm2-rebaseline.json'],
         ['m2-rebaseline.json']),
        ('exterior-cut', [*source, '--out', out], ['exterior-cut.json']),
        ('l1-cut', [*source, '--out', out / 'l1-cut.json'], ['l1-cut.json']),
        ('black-cut', [*source, *captures, '--out', out / 'black-cut.json'], ['black-cut.json']),
        ('e2-regression', [*source, *captures, '--out', out / 'e2-regression.json',
                           '--bins', out / 'e2-regression-bins.json.gz'],
         ['e2-regression.json', 'e2-regression-bins.json.gz']),
    ]
    if union:
        steps.append(('scratch-union', [*source, '--out', out / 'union.json'], ['union.json']))
    produced = {}
    for script, args, files in steps:
        code, stdout, stderr = run(folder, script, args)
        if code != 0:
            raise SystemExit(f'{folder.name}/{script} exited {code}:\n{stderr[-2000:]}')
        (out / f'{script}.stdout').write_text(stdout)
        produced[script] = [(name, (out / name).read_bytes()) for name in files]
        produced[script].append((f'{script}.stdout', stdout.encode()))
    return produced


def readable(name, raw):
    return gzip.decompress(raw) if name.endswith('.gz') else raw


GENERATED_AT = re.compile(rb'"generatedAt": "[^"]*"')
DOCUMENT_LINE = re.compile(r'^ {4,}(\d+)  (\S+ sha256:[0-9a-f]{12})$')
MOVED = re.compile(rb'"capturePathsMoved": \d+')


def documents_by_name(text):
    """exterior-cut's section 0 lists each document the rows name with its row count. In a
    candidate read the WebGPU rows name the candidate and the CSS rows still name the shipped
    document, so once mapped one name can appear twice: sum the counts per name."""
    lines, out, i = text.decode().split('\n'), [], 0
    while i < len(lines):
        if not DOCUMENT_LINE.match(lines[i]):
            out.append(lines[i])
            i += 1
            continue
        counts = {}
        while i < len(lines) and DOCUMENT_LINE.match(lines[i]):
            count, name = DOCUMENT_LINE.match(lines[i]).groups()
            counts[name] = counts.get(name, 0) + int(count)
            i += 1
        out += [f'    {n:>4}  {name}' for name, n in sorted(counts.items())]
    return '\n'.join(out).encode()


def base_identity(title, w41, w42, out41, out42):
    say(title)
    for script in w42:
        notes = []
        for (name, a), (_, b) in zip(w41[script], w42[script]):
            a, b = readable(name, a), readable(name, b)
            if a == b:
                notes.append(f'{name} byte-identical')
                continue
            if name == 'chroma-cut.json' and GENERATED_AT.sub(b'', a) == GENERATED_AT.sub(b'', b):
                notes.append(f'{name} byte-identical except generatedAt')
                continue
            # scratch-union prints the path it wrote, which is each run's own scratch directory.
            if name == 'scratch-union.stdout' and \
                    a.replace(str(out41).encode(), b'OUT') == b.replace(str(out42).encode(), b'OUT'):
                notes.append(f'{name} byte-identical except the output path it prints')
                continue
            notes.append(f'{name} DIFFERS')
        check(all('DIFFERS' not in n for n in notes), f'{script:<14} ' + '; '.join(notes))


def json_paths(a, b, at='$'):
    """The JSON paths at which a and b differ, list indices collapsed to []."""
    if type(a) is not type(b):
        return {at}
    if isinstance(a, dict):
        out = set()
        for k in sorted(a.keys() | b.keys()):
            out |= {f'{at}.{k}'} if k not in a or k not in b else json_paths(a[k], b[k], f'{at}.{k}')
        return out
    if isinstance(a, list):
        if len(a) != len(b):
            return {at}
        return set().union(*(json_paths(x, y, at + '[]') for x, y in zip(a, b))) if a else set()
    return set() if a == b else {at}


def summarise(paths, limit=6):
    paths = sorted(paths)
    return ', '.join(paths[:limit]) + (f' (+{len(paths) - limit} more)' if len(paths) > limit else '')


def candidate_equality(control, candidate, mapping, captures_expected, named_candidates):
    say('GREEN candidate: candidate-light + candidate-dark with --candidate (x4), against '
        'control-light + control-dark in base mode')
    for script in candidate:
        notes, ok = [], True
        for (name, a), (_, b) in zip(control[script], candidate[script]):
            a, b = readable(name, a), readable(name, b)
            text = not name.endswith(('.json', '.gz'))
            if text:
                lines = b.decode().split('\n')
                stamped = lines[0].startswith('# CANDIDATE')
                ok &= stamped
                b = '\n'.join(lines[1:]).encode() if stamped else b
                before = sum(x != y for x, y in zip(a.split(b'\n'), b.split(b'\n')))
            mapped = b
            for old, new in mapping:
                mapped = mapped.replace(old.encode(), new.encode())
            if text:
                aside = ''
                if name == 'exterior-cut.stdout':
                    a, mapped = documents_by_name(a), documents_by_name(mapped)
                    aside = ' (section 0\'s per-document counts summed per mapped name)'
                if name == 'e2-regression.stdout':
                    moved = MOVED.search(a).group()
                    mapped = MOVED.sub(moved, mapped)
                    aside = f' (capturePathsMoved set to the control\'s, {moved.decode()})'
                equal = mapped == a
                ok &= equal
                notes.append(f'{name}: first line "# CANDIDATE" {"yes" if stamped else "NO"}, '
                             f'{before} line(s) differ before mapping, '
                             f'{"equal" if equal else "NOT EQUAL"} after{aside}')
                continue
            if name == 'union.json':
                equal = mapped == a
                ok &= equal
                notes.append(f'{name}: {"byte-equal" if equal else "NOT EQUAL"} after mapping')
                continue
            ja, jb, jm = json.loads(a), json.loads(b), json.loads(mapped)
            differs = json_paths(ja, jb)
            if name == 'chroma-cut.json':
                # The gate review of b151aff4, finding 11: a candidate cut's shippedDocuments
                # names the documents its bed was measured at, the candidates, before mapping.
                named = {k: jb['shippedDocuments'].get(k) for k in named_candidates}
                ok &= named == named_candidates
                notes.append(f'{name}: shippedDocuments names the {len(named_candidates)} '
                             f'candidates before mapping: '
                             f'{"yes" if named == named_candidates else "NO"} (finding 11)')
            stamp = isinstance(jm, dict) and jm.get('admission', {}).get('mode') == 'candidate'
            if isinstance(jm, dict) and not name.endswith('.gz'):
                ok &= stamp
                jm.pop('admission', None)
                if 'atDocuments' in jm:
                    ok &= jm['atDocuments'] == 'candidate' and ja['atDocuments'] == 'shipped'
                    jm['atDocuments'] = 'shipped'
                for side in (ja, jm):
                    side.pop('generatedAt', None)
                if 'captures' in jm:  # e2's captures roots: path-only
                    ok &= jm.pop('captures') == captures_expected and ja.pop('captures') == [str(CAN)]
                if 'capturePathsMoved' in jm:
                    # e2 counts rows whose capturePath differs from the frozen pre-W38
                    # baseline's; every candidate row names another document by construction.
                    ok &= jm['capturePathsMoved'] == jm['cells']
                    notes.append(f'{name}: capturePathsMoved {jm["capturePathsMoved"]} = every '
                                 f'cell (control {ja["capturePathsMoved"]}), set aside')
                    jm['capturePathsMoved'] = ja['capturePathsMoved']
                if name == 'exterior-cut.json':
                    # One name per document the rows name; mapped, the candidate's and the
                    # shipped CSS rows' documents coincide.
                    ok &= sorted(set(jm['documents'])) == ja['documents']
                    notes.append(f'{name}: documents {len(jm["documents"])} names, '
                                 f'{len(set(jm["documents"]))} once mapped (control '
                                 f'{len(ja["documents"])}), set aside')
                    jm['documents'] = ja['documents']
            equal = ja == jm
            ok &= equal
            notes.append(f'{name}: differs before mapping at {summarise(differs) or "nothing"}; '
                         f'{"stamped, " if stamp else ""}{"equal" if equal else "NOT EQUAL"} after')
        check(ok, f'{script}')
        for note in notes:
            say(f'          {note}')


def stage_against_union(union, stages):
    say('GREEN base, two stages: control-light + control-dark against the current union (the '
        'same rows, less the holdout rows no stage holds); JSON may differ in provenance only')
    for script in union:
        for (name, a), (_, b) in zip(union[script], stages[script]):
            a, b = readable(name, a), readable(name, b)
            if name.endswith(('.json', '.gz')):
                ja, jb = json.loads(a), json.loads(b)
                differs = json_paths(ja, jb)
                allowed = {'$.source', '$.matrixSha256', '$.generatedAt'}
                check(differs <= allowed, f'{script:<14} {name}: '
                      f'{summarise(differs) or "identical"} (allowed: provenance only)')
            else:
                lines = sum(x != y for x, y in zip(a.split(b'\n'), b.split(b'\n'))) + \
                    abs(a.count(b'\n') - b.count(b'\n'))
                say(f'  info  {script:<14} {name}: {lines} line(s) differ (provenance printed to '
                    'stdout; exterior-cut also lists the holdout rows it does not read)')


# ---------------------------------------------------------------------------------------------
# Refusals
# ---------------------------------------------------------------------------------------------

def refuse(case, args_for, expect):
    """Every row reader refuses: non-zero exit, the expected phrase, nothing written."""
    say(f'RED {case}')
    messages = set()
    for script in ROW_READERS:
        out = SCRATCH / 'red' / re.sub(r'\W+', '-', case)[:40] / script
        out.mkdir(parents=True)
        tail = {'exterior-cut': ['--out', out], 'scratch-union': ['--out', out / 'union.json'],
                'e2-regression': ['--out', out / 'e2.json', '--bins', out / 'bins.json.gz']}.get(
                    script, ['--out', out / f'{script}.json'])
        code, stdout, stderr = run(HERE, script, [*args_for(script), *tail])
        message = stderr.strip().split('\n')[-1]
        messages.add(message)
        written = sorted(p.name for p in out.iterdir())
        phrase = expect.get(script, expect[None]) if isinstance(expect, dict) else expect
        check(code != 0 and phrase in message and not written,
              f'{script:<14} exit {code}; message names the mismatch: '
              f'{"yes" if phrase in message else "NO"}; outputs written: {written or "none"}')
    for message in sorted(messages):
        say(f'          "{message.replace(str(SCRATCH), "$SCRATCH").replace(str(ROOT) + "/", "")}"')


def main():
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True)
    head = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=HERE, capture_output=True,
                          text=True).stdout.strip()
    say('W42 G0 referees: candidate-admission test (charter clause 10)')
    say(f'worktree HEAD {head}; W41 port {W41.relative_to(ROOT)}; canonical captures {CAN}')
    say(f'scratch {SCRATCH}; candidate documents {CANDIDATES.relative_to(ROOT)} (removed on exit)')
    say()
    built = build()
    for scheme, b in built.items():
        say(f'stage {scheme}: {b["rows"]} non-holdout WebGPU rows of {b["cells"]} declared cells, '
            f'{b["copied"]} captures copied')
        for kind in ('active', 'receded'):
            (sp, ss), (cp, cs) = b['shipped'][kind], b['candidate'][kind]
            say(f'  {kind:<8} shipped {Path(sp).name} sha256:{ss[:12]} -> candidate '
                f'sha256:{cs[:12]}')
    say()

    # GREEN base -------------------------------------------------------------------------------
    w41 = cuts(W41, SCRATCH / 'base-union-w41', [], [])
    w42 = cuts(HERE, SCRATCH / 'base-union-w42', [], [])
    base_identity('GREEN base: current union, canonical captures (W42 port against W41 port)',
                  w41, w42, SCRATCH / 'base-union-w41', SCRATCH / 'base-union-w42')
    say()
    light = ['--stage', built['light']['stages']['control']]
    w41s = cuts(W41, SCRATCH / 'base-stage-w41', light, [], union=True)
    w42s = cuts(HERE, SCRATCH / 'base-stage-w42', light, [], union=True)
    base_identity('GREEN base: one stage, control-light at the shipped documents (W42 port '
                  'against W41 port)', w41s, w42s, SCRATCH / 'base-stage-w41',
                  SCRATCH / 'base-stage-w42')
    say()

    # GREEN candidate --------------------------------------------------------------------------
    controls = ['--stage', built['light']['stages']['control'],
                '--stage', built['dark']['stages']['control']]
    control = cuts(HERE, SCRATCH / 'control', controls, ['--captures', CAN], union=True)
    stage_against_union(w42, control)
    say()
    lc, dc = built['light']['candidate'], built['dark']['candidate']
    declared = [
        '--candidate', lc['active'][0],                                  # repo-relative
        '--candidate', f'{lc["receded"][0]}={lc["receded"][1][:12]}',    # with its hash
        '--candidate', ROOT / dc['active'][0],                           # absolute
        '--candidate', f'{ROOT / dc["receded"][0]}={dc["receded"][1][:12]}',
    ]
    stages = ['--stage', built['light']['stages']['candidate'],
              '--stage', built['dark']['stages']['candidate']]
    captures = ['--captures', CAN, '--captures', SCRATCH / 'captures']
    candidate = cuts(HERE, SCRATCH / 'candidate', [*stages, *declared], captures, union=True)
    mapping = []
    for scheme in SCHEMES:
        b = built[scheme]
        for kind in ('active', 'receded'):
            (sp, ss), (cp, cs) = b['shipped'][kind], b['candidate'][kind]
            mapping += [(cp, sp), (cs[:12], ss[:12])]
        for name in ('matrix.json',):
            cand, ctrl = b['stages']['candidate'], b['stages']['control']
            mapping += [(sha((cand / name).read_bytes()), sha((ctrl / name).read_bytes())),
                        (str(cand), str(ctrl))]
    digest = lambda produced: json.loads(dict(produced['l1-cut'])['l1-cut.json'])['matrixSha256']
    mapping.append((digest(candidate), digest(control)))
    mapping.append((str(SCRATCH / 'candidate'), str(SCRATCH / 'control')))
    say('mapped back before comparing: the four candidate paths and hashes to the shipped ones; '
        'the two candidate stage paths and stage-matrix digests to the control ones; the union\'s '
        'legacy-envelope digest (a hash over rows that name the documents); the output directory '
        'scratch-union prints; e2\'s captures roots are set aside (path-only)')
    named_candidates = {Path(built[scheme]['candidate'][kind][0]).name:
                        built[scheme]['candidate'][kind][1][:12]
                        for scheme in SCHEMES for kind in ('active', 'receded')}
    candidate_equality(control, candidate, mapping, [str(CAN), str(SCRATCH / 'captures')],
                       named_candidates)
    say()

    # RED ------------------------------------------------------------------------------------
    light_active = CANDIDATES / 'light' / Path(SCHEMES['light']['active']).name
    original = light_active.read_bytes()
    all_stages = lambda script: stages
    refuse('R1 a wrong =SHA12 on a declared candidate',
           lambda s: [*stages, '--candidate', f'{lc["active"][0]}=000000000000', *declared[2:],
                      '--candidate', lc['receded'][0]],
           'not the declared 000000000000')
    light_active.write_bytes(original + b' ')
    try:
        refuse('R2 the candidate\'s bytes changed after the rows were written, declared by path',
               lambda s: [*stages, *declared], 'not the declared candidate\'s bytes')
        refuse('R3 the candidate\'s bytes changed after the rows were written, declared with its '
               'original =SHA12',
               lambda s: [*stages, '--candidate', f'{lc["active"][0]}={lc["active"][1][:12]}',
                          *declared[2:]], f'not the declared {lc["active"][1][:12]}')
    finally:
        light_active.write_bytes(original)
    refuse('R4 base mode (no --candidate) on the candidate stages', all_stages,
           'neither a shipped document')
    refuse('R5 a --candidate under packages/calibration/profiles/',
           lambda s: [*stages, *declared, '--candidate', SCHEMES['light']['active']],
           'is the shipped file, not a candidate')
    refuse('R6 two stages replacing the same (profile, tier) pairs',
           lambda s: ['--stage', built['light']['stages']['control'], *stages, *declared],
           'replaces too')
    refuse('R7 a --candidate with no --stage', lambda s: declared,
           {None: 'needs --stage', 'scratch-union': '--stage is required'})
    refuse('R8 a declared candidate that no stage declares',
           lambda s: [*controls, *declared], 'is declared by no --stage')
    say()
    say(f'{len(failures)} failure(s)' if failures else 'all checks pass')
    return 1 if failures else 0


if __name__ == '__main__':
    try:
        code = main()
    finally:
        shutil.rmtree(CANDIDATES, ignore_errors=True)
    raise SystemExit(code)
