"""The 26.5 adopted tables, read from the test file instead of transcribed (2026-09-19).

`test/adopted-thresholds.test.ts` is the source of truth for every allowance this wave
reasons against. G2's first review closure copied the texture tier into a dictionary by
hand and got four of forty-eight rows wrong, and those four reached the charter's Decision
Log 4 (c), claims §5.151 §12 and §5.152 §B §11 before an independent read caught them. So
the numbers are parsed here, once, and both review closures import this module rather than
keeping a copy each: `results/2026-09-19-w29-g2-native-delta/review-closure.py` and
`results/2026-09-19-w29-g1c-coupled/review-closure.py`.

It lives beside G2's closure because that is the child whose transcription failed, and it
is a module rather than a function in that script so that importing it cannot re-run a
report. It reads; it writes nothing.
"""
import pathlib
import re

CALIBRATION = pathlib.Path(__file__).resolve().parents[2]
ADOPTED_THRESHOLDS = CALIBRATION / "test" / "adopted-thresholds.test.ts"

# The adopted row's name → the native-delta metric that measures the same thing, and whether
# the adopted row is a `≥` (so the delta metric is its complement and the allowance is 1 − it).
ADOPTED_TO_DELTA = {
    "silhouetteIoU": ("silhouetteIoUComplement", True),
    "contourDistanceMean": ("contourDistanceMeanPx", False),
    "contourDistanceP95": ("contourDistanceP95Px", False),
    "ssimMean": ("ssimComplement", True),
    "oklabDeltaEMean": ("oklabDeltaEMean", False),
    "oklabDeltaEP95": ("oklabDeltaEP95", False),
    "edgeWeightedMean": ("edgeWeightedMean", False),
    "ssimOutside": ("ssimOutsideComplement", True),
}

GATE_ROW = re.compile(r'\[\s*"\w+"[^"]*"(\w+)"[^"]*"(≥|≤)"\s*,\s*([0-9.]+)\s*\]')


def read_allowances():
    """Return `({profile: {tier: {delta metric: allowance}}}, {profile: {tier: constant name}})`.

    The profile is the key with `apple-macos-26.5-` stripped, which is how both closures
    name their columns; the tier is `texture` or `dom`; the metric is the native delta's
    own name, so a row always reads *lower is closer*. The table constant's name travels
    with the numbers so an output can say where its column came from.
    """
    source = ADOPTED_THRESHOLDS.read_text(encoding="utf-8")
    tables = {}
    for block in re.finditer(r"const (\w+): readonly GateRow\[\] = \[(.*?)\n\];", source, re.S):
        rows = {}
        for line in block.group(2).splitlines():
            found = GATE_ROW.search(line)
            if found is None:
                continue
            delta_name, complemented = ADOPTED_TO_DELTA[found.group(1)]
            value = float(found.group(3))
            rows[delta_name] = 1 - value if complemented else value
        tables[block.group(1)] = rows
    start = source.index("const GATED_PROFILES")
    gated = source[start:source.index("\n];", start)]
    parsed, sources = {}, {}
    for entry in re.split(r"\n  \},?", gated):
        key = re.search(r'profileKey:\s*"([^"]+)"', entry)
        texture = re.search(r"\btexture:\s*(TEXTURE_\w+)", entry)
        dom = re.search(r"\bdom:\s*(DOM_\w+)", entry)
        if key is None or texture is None or dom is None:
            continue
        name = key.group(1).replace("apple-macos-26.5-", "")
        parsed[name] = {"texture": tables[texture.group(1)], "dom": tables[dom.group(1)]}
        sources[name] = {"texture": texture.group(1), "dom": dom.group(1)}
    if not parsed:
        raise SystemExit("adopted_allowances: parsed no profile out of adopted-thresholds.test.ts")
    return parsed, sources
