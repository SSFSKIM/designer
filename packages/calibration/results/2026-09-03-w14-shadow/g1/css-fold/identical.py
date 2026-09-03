"""Which CSS-tier captures the fold left byte-for-byte alone.

The claim the derivation makes is that it vanishes where the lift does — below
the size law's knee, and over a backdrop with no light to copy — so the check is
on the PNG and not on a metric: same bytes, or a named difference.
"""
import sys, hashlib, os

BEFORE, AFTER = sys.argv[1], sys.argv[2]


def digest(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()[:12]


def walk(root):
    out = {}
    for base, _, files in os.walk(root):
        for name in files:
            if name.endswith('.png'):
                out[os.path.relpath(os.path.join(base, name), root)] = os.path.join(base, name)
    return out


before, after = walk(BEFORE), walk(AFTER)
same = 0
for name in sorted(after):
    if name not in before:
        print(f'{"(new)":10s} {name}')
        continue
    if digest(before[name]) == digest(after[name]):
        same += 1
    else:
        print(f'{"CHANGED":10s} {name}')
print(f'{same} of {len(after)} captures byte-identical')
