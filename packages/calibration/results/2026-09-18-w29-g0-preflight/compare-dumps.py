#!/usr/bin/env python3
"""Compare the declared material across bundles that differ only in linked SDK.

    compare-dumps.py <label>=<root> <label>=<root> [...]

Each root is a `dump-arms.sh` output: `light/`, `dark/` and `inactive/` trees of
per-scene `dump-layers` JSON. For every cell present in all roots this prints, and
returns as JSON on stdout under `--json`, three readings:

  * whether the whole dump is byte-identical across the arms;
  * whether the set of layer/effect classes is identical;
  * every filter input whose value differs, with the value each arm declared.

The first arm named is the reference. Fields that record the run rather than the
material — the pose booleans, the settle, the os string — are excluded from the
byte comparison by being listed in VOLATILE, because two runs of the same bundle
differ in them and a comparison that calls that a difference cannot see a real one.
"""
import hashlib
import json
import os
import sys

# Fields that record the run or the process rather than the material. The first
# group is the pose and the environment, which two arms of a comparison are
# supposed to hold equal and which a real difference would show up in anyway. The
# second is process-local: `description` carries every layer's heap address, and
# `sourceContextId` / `sourceLayerRenderId` are per-process render identities.
# Measured 2026-09-18: those three account for all 21 leaves by which two dumps of
# the same cell from two bundles differ when every filter input agrees, so a digest
# that kept them could never report identity and would say nothing at all.
VOLATILE = {"isKeyWindow", "appIsActive", "activationPolicy", "settleSeconds",
            "backingScaleFactor", "os", "a11y",
            "description", "sourceContextId", "sourceLayerRenderId"}


def filters(node, out=None):
    if out is None:
        out = []
    if isinstance(node, dict):
        if "type" in node and "inputs" in node:
            out.append(node)
        for v in node.values():
            filters(v, out)
    elif isinstance(node, list):
        for v in node:
            filters(v, out)
    return out


def classes(node, out=None):
    if out is None:
        out = {}
    if isinstance(node, dict):
        for key in ("class", "type"):
            if isinstance(node.get(key), str):
                out[node[key]] = out.get(node[key], 0) + 1
        for v in node.values():
            classes(v, out)
    elif isinstance(node, list):
        for v in node:
            classes(v, out)
    return out


def inputs_of(doc):
    flat = {}
    for f in filters(doc):
        for k, v in (f.get("inputs") or {}).items():
            flat[f"{f.get('type', '?')}.{k}"] = json.dumps(v, sort_keys=True)
    return flat


def stable(doc):
    """The dump with the run-recording fields dropped, canonically serialised."""
    if isinstance(doc, dict):
        return {k: stable(v) for k, v in sorted(doc.items()) if k not in VOLATILE}
    if isinstance(doc, list):
        return [stable(v) for v in doc]
    return doc


def cells(root):
    found = {}
    for pose in ("light", "dark", "inactive"):
        d = os.path.join(root, pose)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name.endswith(".json"):
                found[f"{pose}/{name[:-5]}"] = os.path.join(d, name)
    return found


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    arms = [(a.split("=", 1)[0], a.split("=", 1)[1]) for a in args]
    maps = {label: cells(root) for label, root in arms}
    shared = set.intersection(*(set(m) for m in maps.values()))
    ref = arms[0][0]

    report = {"arms": {label: root for label, root in arms}, "cells": {}}
    for cell in sorted(shared):
        docs = {label: json.load(open(maps[label][cell])) for label, _ in arms}
        digests = {label: hashlib.sha256(
            json.dumps(stable(doc), sort_keys=True).encode()).hexdigest()
            for label, doc in docs.items()}
        klasses = {label: classes(doc) for label, doc in docs.items()}
        ins = {label: inputs_of(doc) for label, doc in docs.items()}
        keys = sorted(set().union(*(set(v) for v in ins.values())))
        differing = {}
        for k in keys:
            vals = {label: ins[label].get(k, "<absent>") for label, _ in arms}
            if len(set(vals.values())) > 1:
                differing[k] = vals
        entry = {
            "stableDigestIdentical": len(set(digests.values())) == 1,
            "stableDigest": digests,
            "classesIdentical": all(klasses[label] == klasses[ref] for label, _ in arms),
            "inputCount": len(keys),
            "differingInputs": differing,
        }
        report["cells"][cell] = entry
        print(f"{cell}: digest-identical={entry['stableDigestIdentical']} "
              f"classes-identical={entry['classesIdentical']} "
              f"inputs={len(keys)} differing={len(differing)}")
        for k, vals in differing.items():
            print(f"    {k}: " + "  ".join(f"{label}={vals[label]}" for label, _ in arms))

    total = len(report["cells"])
    same = sum(1 for e in report["cells"].values() if e["stableDigestIdentical"])
    report["summary"] = {"cells": total, "digestIdentical": same,
                         "cellsWithDifferingInputs": sum(
                             1 for e in report["cells"].values() if e["differingInputs"])}
    print(f"\n{same} of {total} cells declare a byte-identical material across "
          f"{', '.join(label for label, _ in arms)}")
    if as_json:
        out = os.environ.get("COMPARE_DUMPS_OUT")
        if out:
            json.dump(report, open(out, "w"), indent=2, sort_keys=True)
            print(f"→ {out}")


if __name__ == "__main__":
    main()
