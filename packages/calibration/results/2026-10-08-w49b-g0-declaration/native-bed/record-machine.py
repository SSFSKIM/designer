#!/usr/bin/env python3.12
"""Reuse the W43 executable census and machine reader, with the chosen bundle pin."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import reuse

if __name__ == '__main__':
    reuse.recorder().main()
