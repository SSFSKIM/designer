#!/usr/bin/env python3.12
"""W43 G3 (ii) review closure, finding 1: ``read.py``'s holdout preconditions refuse under
``python3 -O`` exactly as they do without it.

At 48d3b744 the four preconditions were ``assert`` statements, and the interpreter removes an
assert, together with every call inside it, under ``-O`` or PYTHONOPTIMIZE. Here
``read.holdout_refusals`` reads a stub ledger module and a stub committed record that are wrong
in each way the holdout rule names (W31 Decision Log 1 (b); charter clause 10 step 6), and right
once as the control. For contrast the 48d3b744 block itself, read out of git with its one git call
stubbed, runs over the same inputs. A run without ``-O`` does all of that, then re-runs this file
under ``-O`` and relays the child's record:

    python3.12 -B test_read_preconditions.py    # the record test_read_preconditions.txt keeps

No case calls ``main()``, and nothing here spawns ``compare``: ``read.launch`` is replaced by a
function that fails the run, so the guard does not lean on ``main`` skipping completed labels.
The holdout is already read and is never launched again. Exit 1 on any failed check.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import textwrap
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import read as R  # noqa: E402

PRE_FIX = "48d3b744"
OPTIMIZED = sys.flags.optimize > 0
failures: list[str] = []


def check(ok: bool, what: str) -> None:
    print(f"    {'ok  ' if ok else 'FAIL'} {what}")
    if not ok:
        failures.append(what)


def no_launch(*args, **kwargs):
    raise RuntimeError("a launch was attempted from the precondition test")


R.launch = no_launch

DOCUMENTS = {f"apple-macos-27.0-1x-{s}-standard-glass0.25{r}.json": c * 64
             for (s, r), c in zip([("light", ""), ("dark", ""), ("light", "-receded"),
                                   ("dark", "-receded")], "abcd")}
SOURCE = "e" * 64
RIGHT = dict(at="2026-10-02T11:36:20Z", documentSet="glass0.25", documents=DOCUMENTS,
             sourceSha256=SOURCE, claims="stub")


class Ledger:
    """A stub of ``configuration.py``: the reads it holds and the configuration on 'disk'."""

    def __init__(self, reads: list[dict]):
        self.reads, self.calls = reads, []

    def load_log(self) -> list[dict]:
        self.calls.append("load_log")
        return copy.deepcopy(self.reads)

    def document_hashes(self, document_set: str = "glass0.5") -> dict[str, str]:
        self.calls.append(f"document_hashes({document_set})")
        return dict(DOCUMENTS) if document_set == "glass0.25" else {"other.json": "f" * 64}

    def source_hash(self) -> tuple[str, list[str]]:
        self.calls.append("source_hash")
        return SOURCE, []


def but(**changes) -> dict:
    return {**copy.deepcopy(RIGHT), **changes}


# (name, the ledger's reads, the record committed at HEAD, the refusal kinds expected)
CASES = [
    ("right: every precondition holds", [RIGHT], RIGHT, set()),
    ("documentSet is glass0.5", [but(documentSet="glass0.5")], but(documentSet="glass0.5"),
     {"documentSet"}),
    ("one document hash differs", [but(documents={**DOCUMENTS, next(iter(DOCUMENTS)): "0" * 64})],
     but(documents={**DOCUMENTS, next(iter(DOCUMENTS)): "0" * 64}), {"documents"}),
    ("the sources moved", [but(sourceSha256="0" * 64)], but(sourceSha256="0" * 64), {"sources"}),
    ("the record is not the one committed at HEAD", [RIGHT], but(at="2026-10-01T00:00:00Z"),
     {"committed"}),
    ("all four wrong at once", [but(documentSet="glass0.5", documents={}, sourceSha256="0" * 64)],
     RIGHT, {"documentSet", "documents", "sources", "committed"}),
    ("the ledger is empty", [], None, {"empty"}),
]
KIND = {"documentSet": "documentSet", "documents": "not these documents",
        "sources": "sources moved", "committed": "not committed", "empty": "no record"}


def kinds(refusals: list[str]) -> set[str]:
    return {kind for kind, phrase in KIND.items() if any(phrase in r for r in refusals)}


def pre_fix_block() -> str:
    """The 48d3b744 holdout block of ``main``, from its ledger read to ``sets = "holdout"``."""
    source = subprocess.run(["git", "-C", str(HERE), "show", f"{PRE_FIX}:./read.py"],
                            check=True, capture_output=True, text=True).stdout.splitlines()
    start = next(i for i, l in enumerate(source) if "last = hc.load_log()[-1]" in l)
    end = next(i for i, l in enumerate(source) if l.strip() == 'sets = "holdout"')
    return textwrap.dedent("\n".join(source[start:end]))


def run_pre_fix(block: str, ledger: Ledger, committed: dict | None) -> str:
    """The 48d3b744 block over the stubs, compiled at this interpreter's optimisation level."""
    git = types.SimpleNamespace(check_output=lambda *a, **k: json.dumps(
        {"reads": [] if committed is None else [committed]}))
    scope = dict(hc=ledger, json=json, CAL=R.CAL, subprocess=git)
    try:
        exec(compile(block, f"read.py@{PRE_FIX}", "exec", optimize=-1), scope)
    except Exception as error:  # noqa: BLE001 -- any exception stops main before a launch
        return f"refused ({type(error).__name__})"
    return "LET THROUGH"


def main() -> int:
    print(f"W43 G3 (ii) review, finding 1: holdout preconditions, sys.flags.optimize = "
          f"{sys.flags.optimize} ({'python3 -O' if OPTIMIZED else 'no -O'})")
    block = pre_fix_block()
    for name, reads, committed, expected in CASES:
        print(f"  {name}")
        ledger = Ledger(reads)
        refusals = R.holdout_refusals(ledger, committed)
        for refusal in refusals:
            print(f"      refusal: {refusal}")
        check(kinds(refusals) == expected and len(refusals) == len(expected),
              f"fixed: refuses on {sorted(expected) or 'nothing'}, got {sorted(kinds(refusals))}")
        old = Ledger(reads)
        outcome = run_pre_fix(block, old, committed)
        print(f"      {PRE_FIX} block: {outcome}; calls {old.calls}")
        if expected and not OPTIMIZED:
            check(outcome.startswith("refused"), f"{PRE_FIX} without -O also refuses (control)")
    print("  launches attempted: none (read.launch raises; main() is never called)")
    if not OPTIMIZED:
        child = subprocess.run([sys.executable, "-O", "-B", __file__], capture_output=True,
                               text=True)
        print()
        print(child.stdout, end="")
        print(child.stderr, end="")
        if child.returncode != 0:
            failures.append(f"the -O run exited {child.returncode}")
    print(f"{'FAILED' if failures else 'PASSED'} ({'-O' if OPTIMIZED else 'both runs'}): "
          f"{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
