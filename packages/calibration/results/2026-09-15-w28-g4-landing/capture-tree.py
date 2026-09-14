"""Hash the canonical capture tree, so that "no active capture moved" is a reading.

The canonical `web-captures/` is machine-local and gitignored, which means nothing in
the repository would record it being overwritten. The inactive run writes into it — a
new directory per inactive scene — and X11 says the active material does not move, so
the tree is hashed before the run and again after, and the two files are compared.

    python3 capture-tree.py <web-captures> capture-tree-before.json
    python3 capture-tree.py <web-captures> capture-tree-after.json
    python3 capture-tree.py --compare capture-tree-before.json capture-tree-after.json
"""
import hashlib
import json
import pathlib
import sys

if sys.argv[1] == "--compare":
    before = json.loads(pathlib.Path(sys.argv[2]).read_text())["files"]
    after = json.loads(pathlib.Path(sys.argv[3]).read_text())["files"]
    changed = sorted(k for k in before if k in after and before[k] != after[k])
    removed = sorted(k for k in before if k not in after)
    added = sorted(k for k in after if k not in before)
    print(f"before {len(before)}  after {len(after)}  added {len(added)}  "
          f"changed {len(changed)}  removed {len(removed)}")
    for path in changed[:20]:
        print(f"  CHANGED {path}")
    for path in removed[:20]:
        print(f"  REMOVED {path}")
    raise SystemExit(1 if changed or removed else 0)

root = pathlib.Path(sys.argv[1]).resolve()
files = {}
for path in sorted(root.rglob("*")):
    if path.is_file():
        files[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
out = pathlib.Path(__file__).with_name(sys.argv[2])
out.write_text(json.dumps({"root": str(root), "files": files}, indent=1, sort_keys=True) + "\n")
print(f"{len(files)} files under {root}")
