#!/usr/bin/env python3.12
"""Bind W43's admitted capture protocol; default to refusing every live action."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import reuse

if __name__ == '__main__':
    try:
        action = sys.argv[1] if len(sys.argv) > 1 else ''
        if action not in ('plan', 'pin-check', '-h', '--help'):
            reuse.require_capture_approval()
        reuse.driver().main()
    except ValueError as error:
        print('W49b: ' + str(error), file=sys.stderr)
        raise SystemExit(2)
