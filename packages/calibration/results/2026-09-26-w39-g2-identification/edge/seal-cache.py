"""Seal the disposable archive projection before an optimizer consumes it."""
import hashlib
import json
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
files=[*sorted(root.glob('*.npz')),root/'manifest.json']
rows=[dict(file=f.name,bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in files]
raw=(json.dumps(dict(schema='w39-edge-cache-seal-1',files=rows),indent=2)+'\n').encode()
with (root/'seal.json').open('xb') as f:f.write(raw)
print(json.dumps(dict(cache=str(root),files=len(rows),sha256=hashlib.sha256(raw).hexdigest()),indent=2))
