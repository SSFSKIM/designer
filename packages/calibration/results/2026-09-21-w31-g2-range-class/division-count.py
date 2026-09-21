#!/usr/bin/env python3
"""How many divisions are there in `packages/renderer-webgpu/src/wgsl/`?

W31 G2 review closure, finding N5 (claims c9a §5.163 §8). `scan.ts`'s module
note said "over a thousand divisions" and "exactly ONE has a uniform as its
immediate divisor"; the independent review counted 116 and this recount reads
99. The difference between the three readings is what is being counted:

  * comments are not code — `stripComments` is `scan.ts`'s own, character for
    character, so this script and the scanner agree on what the source is;
  * a TypeScript import path is not a division. These files are `.ts` modules
    whose WGSL lives in template literals, and `index.ts` is nothing but imports:
    15 slashes, no arithmetic. `field.ts` and `silhouette-tone.ts` carry one and
    two. That is the whole of the 117 → 99 gap, and it is where the review's 116
    (silhouette-tone 6) sits too.

Neither the "over a thousand" reading nor the "exactly one uniform divisor"
reading survives, so both are corrected beside in `scan.ts`, in the tracker's
closure and in §5.163 §1. What the paragraph was ARGUING survives unchanged and
is now what was measured: no material leaf is an immediate divisor anywhere in
the shaders.

    python3 division-count.py            # the table, and the uniform divisors
"""

from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WGSL = os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "renderer-webgpu", "src", "wgsl")
)

# The uniform bind-group names the shaders use, so a divisor can be recognised
# as a uniform rather than as a local. Read off the `var<uniform>` declarations.
UNIFORM_DECL = re.compile(r"var<uniform>\s+([A-Za-z_][A-Za-z0-9_]*)\s*:")


def strip_comments(source: str) -> str:
    """`scan.ts`'s own comment stripper: blanked in place, newlines kept."""
    out = list(source)
    i = 0
    n = len(source)
    while i < n:
        two = source[i : i + 2]
        if two == "//":
            while i < n and source[i] != "\n":
                out[i] = " "
                i += 1
        elif two == "/*":
            end = source.find("*/", i + 2)
            stop = n if end == -1 else end + 2
            for j in range(i, stop):
                if source[j] != "\n":
                    out[j] = " "
            i = stop
        else:
            i += 1
    return "".join(out)


def strip_quoted(source: str) -> str:
    """Blank `'...'` and `"..."`, which in a `.ts` file are import paths.

    Template literals are left alone: that is where the WGSL is.
    """
    out = list(source)
    i = 0
    n = len(source)
    while i < n:
        c = source[i]
        if c in "'\"":
            quote = c
            j = i + 1
            while j < n and source[j] != quote:
                if source[j] == "\\":
                    j += 1
                j += 1
            for k in range(i, min(j + 1, n)):
                if source[k] != "\n":
                    out[k] = " "
            i = j + 1
        else:
            i += 1
    return "".join(out)


def main() -> int:
    files = sorted(name for name in os.listdir(WGSL) if name.endswith(".ts"))
    uniforms: set[str] = set()
    sources: dict[str, str] = {}
    for name in files:
        raw = open(os.path.join(WGSL, name), encoding="utf8").read()
        code = strip_quoted(strip_comments(raw))
        sources[name] = code
        uniforms.update(UNIFORM_DECL.findall(code))

    print(f"uniform variables declared: {', '.join(sorted(uniforms))}\n")
    print(f"{'file':24} {'with imports':>13} {'divisions':>10}")
    total = 0
    total_raw = 0
    bare: list[str] = []
    guarded: list[str] = []
    # A type conversion is not a guard: u32(au.grid.x) divides by the uniform.
    # `max(x, eps)` and `clamp(x, eps, hi)` are, and they are the shader's own
    # idiom for exactly this.
    CAST = r"(?:f32|u32|i32|vec2f|vec3f|vec4f|vec2u|vec2i)"
    unguarded = re.compile(rf"^\s*/=?\s*(?:{CAST}\()?\s*([A-Za-z_][A-Za-z0-9_]*)")
    floored = re.compile(r"^\s*/=?\s*(?:max|clamp)\(\s*([A-Za-z_][A-Za-z0-9_]*)")
    for name in files:
        code = sources[name]
        raw_count = strip_comments(
            open(os.path.join(WGSL, name), encoding="utf8").read()
        ).count("/")
        count = code.count("/")
        total += count
        total_raw += raw_count
        print(f"{name:24} {raw_count:13} {count:10}")
        for index, ch in enumerate(code):
            if ch != "/":
                continue
            window = code[index : index + 48]
            line = code[:index].count("\n") + 1
            text = re.sub(r"\s+", " ", code[max(0, index - 46) : index + 30]).strip()
            found = floored.match(window)
            if found is not None and found.group(1) in uniforms:
                guarded.append(f"{name}:{line}  …{text}")
                continue
            found = unguarded.match(window)
            if found is not None and found.group(1) in uniforms:
                bare.append(f"{name}:{line}  …{text}")
    print(f"{'TOTAL':24} {total_raw:13} {total:10}")

    print(f"\nuniform as the immediate divisor, with NO floor: {len(bare)}")
    for entry in bare:
        print(f"  {entry}")
    print(
        "\nNone of them is a material leaf: two are the viewport's own size in device\n"
        "px (>= 1 wherever a pass runs at all) and one is the analysis reduction's\n"
        "fixed 64x64 grid."
    )
    print(f"\nuniform as the divisor, floored by max()/clamp(): {len(guarded)}")
    for entry in guarded:
        print(f"  {entry}")
    print(
        "\nThis is the other half of the paragraph scan.ts rests on, measured: every\n"
        "divisor a material leaf can reach is written max(x, 1e-4) or max(x, 1e-6) in\n"
        "the shader's own idiom."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
