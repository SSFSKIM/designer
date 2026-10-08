"""One isolated child process per LIVE step.

The sealed dispatcher's import guard is permanent and refuses any later call into a repository
source outside the root's closure, which this directory is (live-execution/dispatch.py
_prepare; guard.enforce). So the operator never loads the dispatcher in its own process: each
step runs DRIVER in `python -I -B -c`, whose code is not a repository file. The child reads one
JSON request on stdin, writes one JSON result to the request's result file, and sends its own
streams to a log beside it; nothing it reads reaches the operator's terminal (DL5k).

DRIVER.handle is the whole driver. Tests run the same source in-process against a synthetic
dispatcher (run_inprocess), so the logic tested is the logic the child runs.
"""
import json
import os
from pathlib import Path
import subprocess

DRIVER = r'''
import json, sys, types
from pathlib import Path

VERDICTS = ('CAPTURED', 'PASS_EXPOSED_OWNER_PENDING', 'NEITHER', 'PASS')


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path); sys.modules[name] = module
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def handle(request, dispatcher=None, initializer=None):
    op, root = request['op'], request['root']
    if op == 'initialize':
        E = initializer or source(request['initializer'], 'w50_live_run_initializer')
        assembled = E.assemble(root)
        bound = E.bind_arguments(root, assembled['cohort'])
        return {'cohort': assembled['cohort'], 'initializer': assembled['initializer'],
                'numericalCohort': bound['cohort'], 'argumentManifest': bound['argumentManifest']}
    D = dispatcher or source(request['dispatch'], 'w50_live_run_dispatch')
    doc = D.root_doc(root)
    if op == 'verify_prefit':
        return {'preFitEvidence': D.verify_prefit(root, doc)}
    if op == 'create_phase':
        return {'contract': str(D.create_phase(root, request['batch'], request['output'], request.get('fitRecord')))}
    contract = request.get('contract')
    if op == 'advance':
        state = D.prepare_attempt(root, contract)
        if state.get('schema') == 'w50-live-phase-complete-1':
            return {'state': 'complete'}
        if state.get('schema') == 'w50-live-capture-ready-1':
            return {'state': 'analysis', 'event': D.execute_analysis(root, contract)}
        event = D.execute_attempt(root, contract, state)
        return {'state': 'attempt', 'attempt': state['ordinal'], 'members': len(state['members']), 'event': event}
    if op == 'analysis':
        return {'event': D.execute_analysis(root, contract)}
    if op == 'stop_stale':
        return {'event': D.stop_stale_attempt(root, contract, 'INSTRUMENT_FAULT')}
    if op == 'status':
        return {'status': D.public_status(root, contract)}
    if op == 'verdict':
        status = D.result_for(contract)['report']['status']
        if status not in VERDICTS: raise ValueError('Unknown phase result status')
        return {'verdict': status}
    if op == 'fit_record':
        fit = D.source(D.checked(doc['repo'], doc['instruments']['fit']['entrypoint']), 'w50_live_run_fit_record')
        return {'record': fit.fit_record(root, request['completed'])}
    raise ValueError('Unknown driver operation')
'''

MAIN = DRIVER + r'''
if __name__ == '__main__':
    request = json.loads(sys.stdin.read()); result = Path(request['result'])
    try:
        value = {'ok': True, **handle(request)}
    except BaseException as error:
        import traceback
        traceback.print_exc()
        value = {'ok': False, 'error': type(error).__name__, 'message': str(error)}
    with result.open('x') as stream: stream.write(json.dumps(value, allow_nan=False)+'\n')
'''


def _fresh(folder, op):
    folder = Path(folder); folder.mkdir(parents=True, exist_ok=True)
    n = 1
    while (folder/f'{n:06d}-{op}.result.json').exists() or (folder/f'{n:06d}-{op}.log').exists(): n += 1
    return folder/f'{n:06d}-{op}.result.json', folder/f'{n:06d}-{op}.log'


class Child:
    """Runs DRIVER in a fresh isolated interpreter; results and logs stay under `logs`."""

    def __init__(self, python, dispatch, initializer, logs, cwd):
        self.python, self.dispatch, self.initializer = str(python), str(dispatch), str(initializer)
        self.logs, self.cwd = Path(logs), Path(cwd)

    def __call__(self, op, **request):
        result, log = _fresh(self.logs, op)
        request = {'op': op, 'dispatch': self.dispatch, 'initializer': self.initializer, 'result': str(result), **request}
        with log.open('x') as stream:
            subprocess.run([self.python, '-I', '-B', '-c', MAIN], input=json.dumps(request), text=True,
                           stdout=stream, stderr=subprocess.STDOUT, cwd=self.cwd, env=_environment())
        if not result.is_file():
            return {'ok': False, 'error': 'ChildExited', 'message': 'The child wrote no result', 'log': str(log)}
        return {**json.loads(result.read_text()), 'log': str(log)}


def _environment():
    keep = ('HOME', 'TMPDIR', 'PATH', 'USER', 'LOGNAME', 'LANG', 'LC_ALL', 'SHELL')
    return {k: os.environ[k] for k in keep if k in os.environ}


def run_inprocess(dispatcher=None, initializer=None):
    """DRIVER.handle bound to an in-process dispatcher (tests); same result shape as Child."""
    space = {'__name__': 'w50_live_run_driver'}
    exec(compile(DRIVER, '<w50-live-run-driver>', 'exec'), space)
    def call(op, **request):
        try:
            return {'ok': True, **space['handle']({'op': op, **request}, dispatcher, initializer)}
        except Exception as error:
            return {'ok': False, 'error': type(error).__name__, 'message': str(error), 'log': None}
    return call
