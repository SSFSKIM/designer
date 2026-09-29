#!/usr/bin/env python3.12
"""b9's proof: one exposure of H across checkouts, on a SYNTHETIC holdout (test_runner's toy).

1. RED: the exposure path without the claim (the pre-fix path: W39's working-tree receipt
   alone). Checkout A exposes the toy H; checkout B, a clone of A with its own scratch receipt,
   exposes it AGAIN.
2. GREEN, local: A and B share a bare local origin. A claims the exposure (marker tag pushed
   before begin) and completes; B refuses before its begin.
3. GREEN, live: the marker is a THROWAWAY tag pushed to the real GitHub origin from this
   checkout (the toy exposure itself runs in a scratch repository), and a separate fresh clone
   of GitHub refuses on it. The tag is then deleted from GitHub and locally, and its absence
   read back. The production marker name (`w42-h-exposure`) is never pushed.

Run: python3.12 -B b9-proof.py > b9-proof.txt    (from this directory; needs network)
"""
import datetime
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import runner            # noqa: E402
import test_runner as TR  # noqa: E402

ok = []


def git(root, *args, check=True):
    out = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True)
    if check and out.returncode:
        raise RuntimeError(f'git {args}: {out.stderr.strip()}')
    return out.stdout.strip()


class Toy(TR.Exposure):
    def runTest(self):
        pass


def toy():
    t = Toy()
    t.setUp()
    return t


def expose(t, root, log, output, guard=None):
    wave = runner.boundary.Wave(root / 'decl/toy-scenes.json', root / 'decl/toy-bed.json', root / 'decl/toy-pins.json')
    t.log = log               # the toy's capture callback reads the receipt it runs under
    try:
        result = runner.run_synthetic(root, wave, root / 'frozen.json', log, output, t.capture, t.project, t.score,
                                      guard=guard)
        return f'{result["status"]}, receipt events {events(log)}'
    except PermissionError as error:
        return f'REFUSED: {str(error)[:150]}; receipt events {events(log)}'


def events(log):
    return [json.loads(line)['event'] for line in log.read_text().splitlines()] if log.exists() else []


def clone(source, dest, *extra):
    subprocess.run(['git', 'clone', '-q', *extra, str(source), str(dest)], check=True, capture_output=True)
    git(dest, 'config', 'user.email', 'test@example.invalid')
    git(dest, 'config', 'user.name', 'Synthetic test')
    return dest


# 1. RED
t = toy()
base = Path(t.tmp.name).resolve()
a = expose(t, t.root, t.log, t.output)
b_root = clone(t.root, base / 'B')
b = expose(t, b_root, base / 'B-receipt.jsonl', base / 'B-capture')
red = a.startswith('complete') and b.startswith('complete')
ok.append(red)
print(f'1. RED (no claim: the pre-fix path)\n   checkout A: {a}\n   checkout B (a clone): {b}\n'
      f'   [{"H exposed twice: defect shown" if red else "NOT SHOWN"}]\n')
t.doCleanups()

# 2. GREEN, local origin
t = toy()
base = Path(t.tmp.name).resolve()
origin = base / 'origin.git'
subprocess.run(['git', 'init', '-q', '--bare', str(origin)], check=True)
git(t.root, 'remote', 'add', 'origin', str(origin))
git(t.root, 'push', '-q', 'origin', 'HEAD:refs/heads/main')
tag = 'w42-h-exposure-proof-local'
guard = dict(repo=t.root, log=t.root / 'decl/wave-identification-receipt.jsonl', tag=tag, remote='origin')
a = expose(t, t.root, t.log, t.output, guard)
b_root = clone(origin, base / 'B', '-b', 'main')
b = expose(t, b_root, base / 'B-receipt.jsonl', base / 'B-capture',
           dict(guard, repo=b_root, log=b_root / 'decl/wave-identification-receipt.jsonl'))
green = a.startswith('complete') and b.startswith('REFUSED') and events(base / 'B-receipt.jsonl') == []
ok.append(green)
print(f'2. GREEN (the claim, a bare local origin)\n   checkout A: {a}\n   checkout B (a clone of origin): {b}\n'
      f'   [{"one exposure: fixed" if green else "NOT FIXED"}]\n')
t.doCleanups()

# 3. GREEN, live against the real origin with a throwaway tag
repo = runner.ROOT
tag = 'w42-h-exposure-proof-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
assert tag != runner.MARKER_TAG
remote_url = git(repo, 'remote', 'get-url', 'origin')
head = git(repo, 'rev-parse', 'HEAD')
on_origin = git(repo, 'branch', '-r', '--contains', head)
t = toy()
base = Path(t.tmp.name).resolve()
live_log = runner.PRODUCTION_LOG      # its history is only READ: the production receipt path on every ref
try:
    a = expose(t, t.root, t.log, t.output, dict(repo=repo, log=live_log, tag=tag, remote='origin'))
    listed = git(repo, 'ls-remote', '--tags', 'origin', f'refs/tags/{tag}')
    fresh = base / 'fresh-clone'
    subprocess.run(['git', 'clone', '-q', '--no-checkout', '--filter=blob:none', '--depth=1', '--branch', 'main',
                    remote_url, str(fresh)], check=True, capture_output=True)
    b = expose(t, t.root, base / 'B-receipt.jsonl', base / 'B-capture',
               dict(repo=fresh, log=fresh / live_log.relative_to(repo), tag=tag, remote='origin'))
finally:
    deleted = subprocess.run(['git', '-C', str(repo), 'push', '-q', 'origin', f':refs/tags/{tag}'],
                             capture_output=True, text=True)
    git(repo, 'tag', '-d', tag, check=False)
    after_remote = git(repo, 'ls-remote', '--tags', 'origin', f'refs/tags/{tag}', check=False)
    after_local = git(repo, 'tag', '-l', tag, check=False)
live = (a.startswith('complete') and bool(listed) and b.startswith('REFUSED') and 'exists on origin' in b
        and deleted.returncode == 0 and not after_remote and not after_local)
ok.append(live)
print(f'3. GREEN, live (origin {remote_url}; marker at this checkout\'s HEAD {head[:8]}, on {on_origin or "no remote branch"})\n'
      f'   throwaway tag {tag}\n'
      f'   this checkout: {a}\n   the tag on origin after it: {listed.split()[0][:12] if listed else "absent"} {tag if listed else ""}\n'
      f'   a fresh clone of origin: {b}\n'
      f'   cleanup: push :refs/tags/{tag} exit {deleted.returncode}; on origin now {after_remote or "absent"}; '
      f'locally now {after_local or "absent"}\n'
      f'   [{"one exposure across checkouts against GitHub: fixed; throwaway tag deleted" if live else "NOT FIXED"}]\n')
t.doCleanups()
shutil.rmtree(base, ignore_errors=True)

print(f'{sum(ok)} of {len(ok)} as expected')
sys.exit(0 if all(ok) else 1)
