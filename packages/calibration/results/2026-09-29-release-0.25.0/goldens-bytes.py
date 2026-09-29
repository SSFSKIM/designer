"""The renderer's golden PNGs, byte for byte, after the golden suite ran.

    python3 goldens-bytes.py

`test:golden` compares renders against these files; this step shows the files
themselves did not move either — every PNG under
`packages/renderer-webgpu/e2e/goldens/` equals its bytes at `v0.24.0` (the last
published tag) and at this branch's HEAD, and git reports nothing changed or
untracked in that directory. Exit 1 on any difference.
"""
import hashlib
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DIRECTORY = 'packages/renderer-webgpu/e2e/goldens'
failures = 0
paths = sorted((ROOT / DIRECTORY).glob('*.png'))
for path in paths:
    relative = str(path.relative_to(ROOT))
    raw = path.read_bytes()
    same = all(subprocess.check_output(['git', '-C', str(ROOT), 'show', f'{ref}:{relative}']) == raw
               for ref in ('v0.24.0', 'HEAD'))
    failures += not same
    print(('ok  ' if same else 'MOVED'), relative, hashlib.sha256(raw).hexdigest())
status = subprocess.check_output(['git', '-C', str(ROOT), 'status', '--porcelain', '--', DIRECTORY],
                                 text=True)
print('git status of the golden directory:', status.strip() or 'clean')
failures += bool(status.strip())
print(f'{len(paths)} golden PNGs, {"byte-identical to v0.24.0 and HEAD" if not failures else f"{failures} failure(s)"}')
raise SystemExit(1 if failures else 0)
