#!/usr/bin/env python3.12
"""Python read-only adapter for W40's frozen bed and indexed generations.

Cells retain their original raw byte slices privately, so legacy-envelope hashes
certify recorded evidence rather than a Python reserialization of its numbers.
"""
import collections
import hashlib
import json
import os
import pathlib
import re

from snapshot import RESULTS, digest, documents, key, slices

_RAW = {}
_ENVELOPE = {}
_TOKEN = re.compile(r"^[0-9a-f]{12}$")
_FILE = re.compile(r"^[0-9a-f]{12}(?:-[0-9a-f]{12})?\.json$")
_UNQUALIFIED = object()


def _load_matrix(path):
    raw = path.read_bytes()
    envelope = json.loads(raw)
    if envelope.get("schemaVersion") != 5 or not isinstance(envelope.get("cells"), list):
        raise ValueError(f"{path}: expected schema-5 cells array")
    spans, prefix, sep, suffix = slices(raw)
    if len(spans) != len(envelope["cells"]):
        raise ValueError(f"{path}: cells and raw byte slices differ")
    rows = []
    seen = set()
    for (a, b), parsed in zip(spans, envelope["cells"]):
        row = json.loads(raw[a:b])
        if row != parsed:
            raise ValueError(f"{path}: parsed row differs from byte slice")
        identity = key(row)
        if identity in seen:
            raise ValueError(f"{path}: duplicate serialized row key {identity}")
        seen.add(identity)
        _RAW[id(row)] = raw[a:b]
        _ENVELOPE[id(row)] = (prefix, sep, suffix)
        rows.append(row)
    return rows, raw


def _index(directory, archived=False):
    path = directory / "index.json"
    index = json.loads(path.read_bytes())
    if not archived and (index.get("schemaVersion") != 1 or
                         not all(isinstance(index.get(x), dict) for x in
                                 ("files", "byDocumentSha256", "currentByProfile"))):
        raise ValueError(f"{path}: invalid generations index schema")
    if archived and not all(isinstance(index.get(x), dict) for x in
                            ("files", "byDocumentSha256")):
        raise ValueError(f"{path}: invalid superseded index")
    owners = collections.defaultdict(set)
    for filename, metadata in index["files"].items():
        if not _FILE.fullmatch(filename):
            raise ValueError(f"{path}: invalid file name {filename}")
        active = metadata.get("activeDocumentSha256")
        docs = metadata.get("documents")
        if not _TOKEN.fullmatch(active or "") or not isinstance(docs, list):
            raise ValueError(f"{path}: invalid active hash/documents in {filename}")
        hashes = [d.get("sha256") for d in docs]
        if (len(hashes) not in (1, 2) or active not in hashes or len(set(hashes)) != len(hashes)
                or any(not isinstance(d.get("path"), str) or not _TOKEN.fullmatch(h or "")
                       for d, h in zip(docs, hashes))):
            raise ValueError(f"{path}: incomplete document pair in {filename}")
        if not archived and (metadata.get("status") not in ("current", "retired") or
                             not isinstance(metadata.get("rowsByProfileKey"), dict)):
            raise ValueError(f"{path}: invalid generation entry {filename}")
        for h in hashes:
            owners[h].add(filename)
    if not archived:
        declared = index["byDocumentSha256"]
        if any(not isinstance(names, list) or len(names) != len(set(names))
               for names in declared.values()) or {
                   h: sorted(names) for h, names in declared.items()
               } != {h: sorted(names) for h, names in owners.items()}:
            raise ValueError(f"{path}: incomplete or stale aliases")
    if archived:
        archive_aliases = {h: sorted({first, *index.get("sharedReceded", {}).get(h, [])})
                           for h, first in index["byDocumentSha256"].items()}
        if archive_aliases != {h: sorted(names) for h, names in owners.items()}:
            raise ValueError(f"{path}: incomplete archive aliases")
    return index


def _file(directory, filename, metadata):
    path = directory / filename
    raw = path.read_bytes()
    if len(raw) != metadata.get("bytes") or digest(raw) != metadata.get("sha256"):
        raise ValueError(f"{path}: byte length or SHA-256 differs from index")
    rows, _ = _load_matrix(path)
    if len(rows) != metadata.get("rowCount"):
        raise ValueError(f"{path}: row count differs from index")
    expected_docs = {(d["path"], d["sha256"]) for d in metadata["documents"]}
    counts = collections.Counter()
    for row in rows:
        if row["key"]["profileKey"].startswith("apple-macos-26.5-"):
            raise ValueError(f"{path}: frozen row in indexed generation")
        clauses = documents(row)
        if {(p, h) for _, p, h in clauses} != expected_docs:
            raise ValueError(f"{path}: row document ownership differs from index")
        if next(h for kind, _, h in clauses if kind == "materialProfile") != metadata["activeDocumentSha256"]:
            raise ValueError(f"{path}: row active document differs from index")
        counts[row["key"]["profileKey"]] += 1
    if dict(counts) != metadata.get("rowsByProfileKey"):
        raise ValueError(f"{path}: profile counts differ from index")
    return rows


def _unique(rows):
    seen = set()
    for row in rows:
        identity = key(row)
        if identity in seen:
            raise ValueError(f"serialized row key occurs in two authoritative files: {identity}")
        seen.add(identity)
    return sorted(rows, key=lambda row: key(row))


def _current(results_dir):
    frozen_path = results_dir / "matrix.json"
    frozen, _ = _load_matrix(frozen_path)
    index_path = results_dir / "generations/index.json"
    if not index_path.exists():
        return _unique(frozen), None
    for row in frozen:
        if not row["key"]["profileKey"].startswith("apple-macos-26.5-"):
            raise ValueError(f"{frozen_path}: indexed layout must contain frozen profiles only")
        documents(row)
    directory = index_path.parent
    index = _index(directory)
    members = {}
    for name, entry in index["files"].items():
        if entry["status"] == "current":
            members[name] = _file(directory, name, entry)
    for profile, name in index["currentByProfile"].items():
        if name not in members or index["files"][name]["status"] != "current" or not any(
            row["key"]["profileKey"] == profile for row in members[name]
        ):
            raise ValueError(f"{index_path}: missing current profile {profile} in {name}")
    for name, entry in index["files"].items():
        for profile in entry["rowsByProfileKey"]:
            if entry["status"] == "current" and index["currentByProfile"].get(profile) != name:
                raise ValueError(f"{index_path}: current file {name} not selected for {profile}")
            if entry["status"] == "retired" and index["currentByProfile"].get(profile) == name:
                raise ValueError(f"{index_path}: retired file selected for {profile}")
    current = frozen + [row for name in sorted(set(index["currentByProfile"].values())) for row in members[name]]
    return _unique(current), (index, members)


def load_current_rows(matrix_path=None, results_dir=None):
    """Key-ordered current union; explicit paths and VITREA_MATRIX_PATH are scratch files."""
    override = matrix_path or os.environ.get("VITREA_MATRIX_PATH")
    directory = pathlib.Path(results_dir) if results_dir else RESULTS
    if override and pathlib.Path(override).resolve() != (directory / "matrix.json").resolve():
        return _unique(_load_matrix(pathlib.Path(override))[0])
    return _current(directory)[0]


def load_current_profile(profile_key, results_dir=None):
    rows = load_current_rows(results_dir=results_dir)
    selected = [row for row in rows if row["key"]["profileKey"] == profile_key]
    return selected


def owners_for_document(sha256, results_dir=None):
    """Enumerate EVERY indexed current, retired and archive owner of a document."""
    directory = pathlib.Path(results_dir) if results_dir else RESULTS
    owners = []
    for subdir, archived in (("generations", False), ("superseded", True)):
        path = directory / subdir
        if not (path / "index.json").exists():
            continue
        index = _index(path, archived)
        if archived:
            names = {index["byDocumentSha256"][sha256],
                     *index.get("sharedReceded", {}).get(sha256, [])} if sha256 in index["byDocumentSha256"] else set()
        else:
            names = set(index["byDocumentSha256"].get(sha256, []))
        owners.extend((subdir, name) for name in sorted(names))
    return owners


def load_generation(active, receded=_UNQUALIFIED, results_dir=None):
    """Resolve the document pair; explicit None selects the no-receded generation."""
    if not _TOKEN.fullmatch(active) or (receded is not _UNQUALIFIED and receded is not None
                                        and not _TOKEN.fullmatch(receded)):
        raise ValueError("generation documents require twelve-hex SHA-256 tokens")
    directory = pathlib.Path(results_dir) if results_dir else RESULTS
    choices = []
    for subdir, name in owners_for_document(active, directory):
        index = _index(directory / subdir, subdir == "superseded")
        entry = index["files"][name]
        if receded is not _UNQUALIFIED and entry["activeDocumentSha256"] != active:
            continue
        secondary = next((d["sha256"] for d in entry["documents"]
                          if d["sha256"] != entry["activeDocumentSha256"]), None)
        if receded is _UNQUALIFIED or receded == secondary:
            choices.append((subdir, name, entry))
    if len(choices) > 1:
        qualifier = "unspecified" if receded is _UNQUALIFIED else "none" if receded is None else receded
        raise ValueError(f"generation ({active}, {qualifier}) has "
                         f"{len(choices)} owners; supply an unambiguous active/receded pair")
    if choices:
        subdir, name, entry = choices[0]
        return sorted(_file(directory / subdir, name, entry), key=key)
    # Frozen macOS 26.5 generations predate the indexed layout.
    frozen, _ = _load_matrix(directory / "matrix.json")
    matching = [row for row in frozen if any(
        kind == "materialProfile" and h == active for kind, _, h in documents(row)
    ) and (receded is _UNQUALIFIED or (
        next((h for kind, _, h in documents(row) if kind == "recededProfile"), None) == receded
    ))]
    secondaries = {next((h for kind, _, h in documents(row) if kind == "recededProfile"), None)
                   for row in matching}
    if len(secondaries) > 1:
        raise ValueError(f"ambiguous frozen generation {active}; supply receded qualifier")
    if not matching:
        raise ValueError(f"no generation owns document {active}")
    return sorted(matching, key=key)


def iterate_recorded_rows(results_dir=None):
    """Opt-in iterator across current, retired and historical evidence."""
    directory = pathlib.Path(results_dir) if results_dir else RESULTS
    yield from load_current_rows(results_dir=directory)
    for subdir, archived in (("generations", False), ("superseded", True)):
        path = directory / subdir
        if not (path / "index.json").exists():
            continue
        index = _index(path, archived)
        for name, entry in index["files"].items():
            if archived or entry["status"] == "retired":
                yield from _file(path, name, entry)


def legacy_envelope_digest(rows):
    """Streaming digest over the ORIGINAL row bytes and schema-5 envelope."""
    ordered = _unique(rows)
    if not ordered:
        return digest(b'{\n  "schemaVersion": 5,\n  "cells": []\n}\n')
    sha = hashlib.sha256()
    sha.update(b'{\n  "schemaVersion": 5,\n  "cells": [\n    ')
    for i, row in enumerate(ordered):
        if i:
            sha.update(b",\n    ")
        if id(row) not in _RAW:
            raise ValueError("legacy envelope requires rows loaded with their raw bytes")
        sha.update(_RAW[id(row)])
    sha.update(b"\n  ]\n}\n")
    return sha.hexdigest()
