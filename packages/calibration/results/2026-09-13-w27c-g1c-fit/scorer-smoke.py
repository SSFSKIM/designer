#!/usr/bin/env python3
"""Prove the G1c scorer's new refusal without rewriting the committed verdict.

The unmodified G2 matrix has no machineAccessibility reading and must be
refused. A scratch copy with the measured 0/0 reading injected must reproduce
claims §5.139's committed perProfile block exactly. `score-bound.py` writes next
to itself, so this smoke test restores `verdict.json` byte-for-byte even when an
assertion fails.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
G2 = HERE.parent / "2026-09-13-w27c-g2-read"
VERDICT = HERE / "verdict.json"


def run_scorer(matrix: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HERE / "score-bound.py"), str(matrix)],
        capture_output=True,
        text=True,
    )


def main() -> None:
    unmodified = G2 / "checking-matrix.json"
    held = VERDICT.read_bytes()
    try:
        refusal = run_scorer(unmodified)
        print("=== refusal without the accessibility reading ===")
        print((refusal.stdout + refusal.stderr).strip()[:600])
        assert refusal.returncode != 0, "expected the scorer to refuse"
        assert "does not record both" in refusal.stdout + refusal.stderr

        with tempfile.TemporaryDirectory(prefix="g1c-scorer-smoke-") as temporary:
            scratch = Path(temporary) / "checking-matrix-with-accessibility.json"
            document = json.loads(unmodified.read_text())
            document["machineAccessibility"] = {
                "reduceTransparency": 0,
                "increaseContrast": 0,
                "readAt": "injected-into-a-copy-for-scorer-smoke",
            }
            scratch.write_text(json.dumps(document))

            scored = run_scorer(scratch)
            print("\n=== scored with the reading injected into a copy ===")
            print((scored.stdout + scored.stderr).strip()[-1400:])
            assert scored.returncode == 0, "expected the scorer to score"
            actual = json.loads(VERDICT.read_text())["perProfile"]
            expected = json.loads((G2 / "verdict.json").read_text())["perProfile"]
            assert actual == expected, "perProfile differs from claims §5.139"
    finally:
        VERDICT.write_bytes(held)

    print("\nperProfile is identical to the committed claims §5.139 verdict")
    print("committed G1c verdict restored byte-for-byte")


if __name__ == "__main__":
    main()
