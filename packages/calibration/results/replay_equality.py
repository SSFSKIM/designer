"""Compare immutable evidence on the recording platform and a different BLAS.

The W37 forward bins differ on Linux by at most 8.67e-13 in absolute value
(x86 OpenBLAS versus macOS Accelerate); cancellation in tiny transfers makes
pure relative comparison inappropriate. Keep numbers exact on the recording
platform and require every key, bin, integer population and verdict to agree
exactly everywhere. This does not change a recorded artifact or fitted bound.
"""
import math
import sys


def same_evidence(actual, recorded):
    if type(actual) is not type(recorded):
        return False
    if isinstance(actual, dict):
        return actual.keys() == recorded.keys() and all(
            same_evidence(actual[key], recorded[key]) for key in actual)
    if isinstance(actual, list):
        return len(actual) == len(recorded) and all(
            same_evidence(a, b) for a, b in zip(actual, recorded))
    if isinstance(actual, float) and sys.platform != 'darwin':
        return math.isclose(actual, recorded, rel_tol=1e-12, abs_tol=1e-12)
    return actual == recorded
