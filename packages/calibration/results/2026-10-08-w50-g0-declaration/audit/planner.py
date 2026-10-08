"""Pure batch validation: all capture arguments originate in the sealed batch."""
import re


def validate_run(run, phase):
    if phase not in ('gate', 'exposure'):
        raise ValueError('Unknown capture phase')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', run['id']):
        raise ValueError('Unsafe run id')
    if not re.fullmatch(r'apple-macos-27\.0-[12]x-dark-standard-glass0\.(25|5)', run['profile']):
        raise ValueError('Profile outside W50 dark scope')
    if run['renderer'] not in ('webgpu', 'css'):
        raise ValueError('Unknown renderer')
    scenes, sets = run['scenes'], run['sets']
    if not scenes or len(set(scenes)) != len(scenes) or any(',' in s or not s for s in scenes):
        raise ValueError('Empty or duplicate scene membership')
    allowed = {'calibration', 'validation', 'recorded', 'probe'}
    if phase == 'exposure':
        allowed.add('holdout')
    if not sets or len(set(sets)) != len(sets) or not set(sets).issubset(allowed):
        raise ValueError('Withheld or unknown set outside exposure')
    pin = run['candidate']
    if not pin.get('path') or not re.fullmatch(r'[0-9a-f]{64}', pin.get('sha256', '')):
        raise ValueError('Candidate document is not content-pinned')
    return run


def plan(batch):
    if batch.get('schema') != 'w50-render-batch-1' or not batch.get('runs'):
        raise ValueError('Missing registered capture batch')
    runs = [validate_run(run, batch['phase']) for run in batch['runs']]
    if len({r['id'] for r in runs}) != len(runs):
        raise ValueError('Duplicate run identity')
    return {'phase': batch['phase'], 'runs': runs,
            'cells': sum(len(run['scenes']) for run in runs), 'status': 'BOUND_PLAN'}
