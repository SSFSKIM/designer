#!/usr/bin/env python3.12
"""W40 G0 pre-migration witness; offsets and hashes identify original byte slices.

The brace walk and envelope are derived from W30's split-generation.py:elements/read.
Run before migration. A rerun refuses a different source, rather than overwriting evidence.
"""
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[4]
RESULTS = ROOT / "packages/calibration/results"
HERE = pathlib.Path(__file__).resolve().parent
DOCUMENT = re.compile(r"(materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})(?![0-9a-f])")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def elements(raw):
    """Top-level cells-array object spans, honoring escaped strings (W30 slicer)."""
    start = raw.index(b"[", raw.index(b'"cells"'))
    i, depth, begin, quoted, escaped = start + 1, 0, None, False, False
    spans = []
    while i < len(raw):
        c = raw[i]
        if quoted:
            if escaped:
                escaped = False
            elif c == 92:
                escaped = True
            elif c == 34:
                quoted = False
        elif c == 34:
            quoted = True
        elif c in (123, 91):
            if depth == 0:
                begin = i
            depth += 1
        elif c in (125, 93):
            if depth == 0:
                return start, spans, i
            depth -= 1
            if depth == 0:
                spans.append((begin, i + 1))
        i += 1
    raise ValueError("cells array never closes")


def slices(raw):
    start, spans, end = elements(raw)
    prefix = raw[:spans[0][0]] if spans else raw[:start + 1]
    suffix = raw[spans[-1][1]:] if spans else raw[start + 1:]
    separators = {raw[spans[i][1]:spans[i + 1][0]] for i in range(len(spans) - 1)}
    if len(separators) > 1:
        raise ValueError("mixed cell separators")
    separator = separators.pop() if separators else b",\n    "
    if prefix + separator.join(raw[a:b] for a, b in spans) + suffix != raw:
        raise ValueError("matrix envelope does not reconstruct source bytes")
    return spans, prefix, separator, suffix


def key(row):
    k, w = row["key"], row["key"]["web"]
    fields = (k["profileKey"], k["sceneId"], w["engine"], w["engineVersion"],
              w["renderer"], w["samplingBackend"], w["gpuAdapter"], w["colorSpace"],
              w["capturePath"])
    return "|".join(str(field).replace("%", "%25").replace("|", "%7C") for field in fields)


def documents(row):
    path = row["key"]["web"]["capturePath"]
    clauses = DOCUMENT.findall(path)
    if not clauses or path.count("sha256:") != len(clauses):
        raise ValueError(f"unrecognized/incomplete document clauses: {path}")
    if sum(kind == "materialProfile" for kind, _, _ in clauses) != 1 or sum(
        kind == "recededProfile" for kind, _, _ in clauses) > 1:
        raise ValueError(f"invalid document pair: {path}")
    return clauses


def evidence(raw):
    spans, prefix, sep, suffix = slices(raw)
    rows, groups = [], {}
    for a, b in spans:
        cell = json.loads(raw[a:b]); identity = key(cell)
        clauses = documents(cell)
        group = groups.setdefault(cell["key"]["profileKey"], {})
        pair = tuple((kind, path, h) for kind, path, h in clauses)
        group[json.dumps(pair, separators=(",", ":"))] = group.get(json.dumps(pair, separators=(",", ":")), 0) + 1
        rows.append({"start": a, "end": b, "key": identity, "sha256": digest(raw[a:b])})
    keys = [r["key"] for r in rows]
    if len(set(keys)) != len(keys) or keys != sorted(keys):
        raise ValueError("original matrix keys are not unique and ordered")
    demo = json.loads((HERE / "demo-before.json").read_bytes())
    assert demo["matrixCellCount"] == len(rows)
    return {"schemaVersion": 1, "source": "packages/calibration/results/matrix.json",
            "matrixSha256": digest(raw), "matrixBytes": len(raw), "rowCount": len(rows),
            "prefixHex": prefix.hex(), "separatorHex": sep.hex(), "suffixHex": suffix.hex(),
            "keyOrderSha256": digest(json.dumps(keys, ensure_ascii=False, separators=(",", ":")).encode()),
            "rows": rows,
            "profiles": {p: [{"documents": json.loads(d), "rowCount": n}
                              for d, n in sorted(entries.items())]
                         for p, entries in sorted(groups.items())},
            "demoReduction": demo}


def main():
    path = HERE / "snapshot.json"
    raw = (RESULTS / "matrix.json").read_bytes()
    if path.exists():
        previous = json.loads(path.read_bytes())
        if digest(raw) != previous["matrixSha256"]:
            raise ValueError("snapshot already exists for different source bytes; refusing overwrite")
    recorded = evidence(raw)
    blob = (json.dumps(recorded, indent=2, ensure_ascii=False) + "\n").encode()
    if path.exists():
        if path.read_bytes() != blob:
            raise ValueError("snapshot exists but differs; refusing overwrite")
        print("identical pre-migration snapshot; unchanged")
    else:
        path.write_bytes(blob)
        print(f"snapshot {len(recorded['rows'])} rows, {recorded['matrixBytes']} bytes, {recorded['matrixSha256']}")


if __name__ == "__main__":
    main()
