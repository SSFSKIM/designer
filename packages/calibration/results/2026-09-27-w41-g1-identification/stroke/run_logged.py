"""Observe completed optimizer calls without changing their arguments or results.

This wrapper executes execute.py normally. Immutable JSONL checkpoints preserve
raw solver success, budgets used and sealed report rows even if a long-running
process later fails. Python's profile hook is observational: its return value
cannot steer the solver, and no callback is supplied to scipy.
"""
import json
import inspect
from pathlib import Path
import runpy
import sys
import time
import replay


def main():
    if '--out' not in sys.argv:
        raise ValueError('explicit additive output directory required')
    output = Path(sys.argv[sys.argv.index('--out')+1]).resolve()
    if replay.HERE not in output.parents or output.exists():
        raise ValueError('fresh output must be beneath stroke/')
    watched = {(inspect.unwrap(replay.f.least_squares).__code__.co_filename, 'least_squares'),
               (replay.f.minimize.__code__.co_filename, 'minimize'),
               (replay.f.__file__, 'report')}
    started = time.perf_counter()
    stream = None
    count = 0

    def observe(frame, event, result):
        nonlocal stream, count
        if event != 'return' or (frame.f_code.co_filename, frame.f_code.co_name) not in watched:
            return
        if result is None:
            return
        if stream is None:
            stream = (output/'optimizer-checkpoints.jsonl').open('x')
        count += 1
        kind = frame.f_code.co_name
        if kind == 'report':
            row = result
        else:
            row = dict(success=bool(result.success), message=str(result.message),
                       nfev=int(result.nfev), nit=int(getattr(result, 'nit', 0)),
                       coefficients=result.x.tolist())
        record = dict(sequence=count, seconds=time.perf_counter()-started, kind=kind,
                      caller=frame.f_back.f_code.co_name, result=row)
        stream.write(json.dumps(record, allow_nan=False)+'\n')
        stream.flush()
        print(json.dumps({k: v for k, v in record.items() if k != 'result'}), flush=True)

    if sys.getprofile() is not None:
        raise ValueError('do not displace an existing profiler')
    sys.setprofile(observe)
    try:
        runpy.run_path(str(replay.HERE/'execute.py'), run_name='__main__')
    finally:
        sys.setprofile(None)
        if stream is not None:
            stream.close()


if __name__ == '__main__':
    main()
