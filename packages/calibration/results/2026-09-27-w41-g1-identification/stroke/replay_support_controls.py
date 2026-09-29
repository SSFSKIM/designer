"""Replay the support certificate after scratch leaves move working source bytes.

Use a fresh output directory. The immutable pre-leaf worktree supplies the
unchanged sealed material loader and all its epoch-pinned sources; only this
additive control orchestration is read from the current worktree. No native fit.
"""
import argparse
from pathlib import Path
import subprocess
import sys

PRIMARY = Path(__file__).resolve().parent
PROOF = Path('/Users/new/vitrea-w41/pre-w41-proof')
PROOF_STROKE = PROOF/'packages/calibration/results/2026-09-27-w41-g1-identification/stroke'
REVISION = 'd35b4cbf43f1fcdda55063b3b8e0fa178d720a78'
if subprocess.check_output(['git', '-C', str(PROOF), 'rev-parse', 'HEAD'], text=True).strip() != REVISION:
    raise ValueError('immutable proof revision differs')
sys.path.insert(0, str(PROOF_STROKE))
import replay as r
sys.path.remove(str(PROOF_STROKE))
import execute
import support_controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    out = Path(parser.parse_args().out).resolve()
    if PRIMARY not in out.parents:
        raise ValueError('output must be beneath primary stroke/')
    out.mkdir(exist_ok=False)
    r.verify_seal()
    observations = r.load_role(r.Preparation(), 'calibration')
    result = execute.gzip_rows(out/'bins.jsonl.gz', lambda emit: support_controls.controls(observations, emit))
    result['replayHeldSource'] = dict(root=str(PROOF), revision=REVISION, loaderUnchanged=True)
    execute.json_write(out/'summary.json', result)


if __name__ == '__main__':
    main()
