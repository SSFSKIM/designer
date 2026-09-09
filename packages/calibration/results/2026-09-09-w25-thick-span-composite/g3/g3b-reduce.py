"""W25 G3b — reduce a scratch matrix to ONE material's rows.

A cell's key carries the material profile document's sha256, so `compare` APPENDS beside the old
rows rather than replacing them when the document changes — which is the behaviour CLAUDE.md warns
about and offers two answers to: `rm results/matrix.json` before a full rebuild, or reduce to the
newest row per key. This is the second answer, and it exists because this child ran its dry run
twice: once at the pair the joint objective picked, (0.70, 0.15), and once at the pair that lands,
(0.85, 0.10), after the first was found to drop two calibration cells out of the bed. The captures
on disk are the second run's — they are written per profile and scene and the later run overwrote
them — but the matrix holds both, and a gate reading both sees every cell twice.

Rather than keep "the newest row", which is a claim about ordering, this keeps the rows whose
capture path names the documents that are on disk NOW. That is a claim about the material, it is
checkable from the file itself, and it cannot silently keep a row from a run whose document has
since been edited.

    g3b-reduce.py <in.json> <out.json>
"""

import hashlib
import json
import os
import re
import sys

PROFILES = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "..", "..", "..", "profiles"))
DOCUMENTS = (
    "apple-macos-26.5-1x-light-standard.json",
    "apple-macos-26.5-1x-dark-standard.json",
)


def main():
    source, target = sys.argv[1:3]
    wanted = set()
    for name in DOCUMENTS:
        with open(os.path.join(PROFILES, name), "rb") as handle:
            wanted.add(hashlib.sha256(handle.read()).hexdigest()[:12])
    matrix = json.load(open(source))
    kept, dropped = [], {}
    for cell in matrix["cells"]:
        match = re.search(r"sha256:([0-9a-f]{12})", cell["key"]["web"]["capturePath"])
        digest = match.group(1) if match else "?"
        if digest in wanted:
            kept.append(cell)
        else:
            dropped[digest] = dropped.get(digest, 0) + 1
    matrix["cells"] = kept
    json.dump(matrix, open(target, "w"))
    print(f"documents on disk: {sorted(wanted)}")
    print(f"kept {len(kept)} cells; dropped {sum(dropped.values())} from other materials {dropped}")
    keys = {(c["key"]["profileKey"], c["key"]["sceneId"], c["tier"],
             c["key"]["web"]["renderer"]) for c in kept}
    print(f"distinct cells kept: {len(keys)}"
          + ("" if len(keys) == len(kept) else "  — STILL DUPLICATED, do not gate this"))


if __name__ == "__main__":
    main()
