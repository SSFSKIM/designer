#!/usr/bin/env python3.12
"""Run one browser suite after the same recorded X6 barrier as capture (§5.172)."""
import importlib.util
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('w33_capture',HERE/'render-bed.py')
capture=importlib.util.module_from_spec(spec); spec.loader.exec_module(capture)
mode=sys.argv[1]
commands={
    'goldens':['pnpm','--fail-if-no-match','--filter','@vitrea/renderer-webgpu','test:golden'],
    'window':['pnpm','--fail-if-no-match','--filter','@vitreajs/vitrea-web','exec','playwright',
              'test','e2e/shared/window-activation.spec.ts','--project=chromium'],
}
command=commands[mode]
capture.x6('close/'+mode)
subprocess.run(command,cwd=ROOT,check=True)
