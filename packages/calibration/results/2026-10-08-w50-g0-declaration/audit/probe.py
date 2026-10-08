"""Dry-exercise the registered canonical planner/measurement launcher; no captures."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


renderer = module(HERE / 'render.py', 'w50_render_probe')
planner = module(HERE / 'planner.py', 'w50_planner_probe')
runner = module(HERE / 'runner.py', 'w50_runner_probe')
declaration = module(HERE.parent / 'declare.py', 'w50_declaration_probe')
references = module(HERE.parent / 'references.py', 'w50_references_probe')
root = HERE.parents[4]
census = module(root / 'packages/calibration/results/2026-10-02-w43-g3-refit/stage/census.py',
                'w50_census_probe')
run = {'id': 'synthetic', 'profile': 'apple-macos-27.0-1x-dark-standard-glass0.5',
       'renderer': 'webgpu', 'scenes': ['synthetic'], 'sets': ['calibration'],
       'candidate': {'path': 'not-read.json', 'sha256': 'a' * 64}}
plan = planner.plan({'schema': 'w50-render-batch-1', 'phase': 'gate', 'runs': [run]})
runner.validate_membership(plan, {'cells': [
    {'profile': run['profile'], 'renderer': 'webgpu', 'scene': 'synthetic', 'role': 'gate'}]})
try:
    runner.validate_membership(plan, {'cells': []})
except ValueError:
    pass
else:
    raise AssertionError('Out-of-domain request was admitted')
# This probe intentionally does not pretend to exercise the not-yet-built custom-bed
# measurement/band adapter. A pre-fit executionClosure report must include that adapter.
