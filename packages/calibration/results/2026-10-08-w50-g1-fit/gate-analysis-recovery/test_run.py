"""Restart and capability checks against synthetic authority/output trees only."""
import copy
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
module = types.ModuleType('analysis2_run_tests'); module.__file__ = str(HERE/'run.py')
sys.modules[module.__name__] = module
exec(compile((HERE/'run.py').read_bytes(), str(HERE/'run.py'), 'exec'), module.__dict__)
R = module


class RunTests(unittest.TestCase):
    def test_marker_crash_and_output_claim_each_bar_second_and_third_invocation(self):
        for tombstone in ('marker', 'output', 'logical'):
            with self.subTest(tombstone=tombstone), tempfile.TemporaryDirectory() as tmp:
                home = Path(tmp)
                with patch.object(R.A, 'NEW_MARKER', home/'marker'), \
                     patch.object(R.A, 'OUTPUT', home/'output'), \
                     patch.object(R, 'LOGICAL', home/'logical'), \
                     patch.object(R, 'TERMINAL', home/'terminal'), \
                     patch.object(R.A, 'verify_seal', side_effect=AssertionError('No replay')):
                    path = home/tombstone
                    path.mkdir() if tombstone == 'output' else path.write_bytes(b'partial')
                    for _ in range(3):
                        self.assertEqual(R.run(), {'status': 'NEITHER', 'measurementStatus': 'UNMEASURED', 'analysis': 2})

    def test_facade_keeps_actual_live_context_and_lease_guards(self):
        live, core = R.modules()
        context = {'stage': 'analysis'}
        member = {'id': 'm', 'scene': 's', 'lane': 'candidate',
                  'run': {'profile': 'p', 'renderer': 'webgpu', 'candidate': {'sha256': 'a'*64}}}
        record = {**member['run'], 'scene': 's', 'lane': 'candidate'}
        live._ACTIVE = {'context': context, 'snapshot': copy.deepcopy(context), 'hashes': [],
                        'members': [member], 'records': {'m': record}, 'payloads': []}
        facade = R.ReadOnlyDispatcher(live, None, context)
        with patch.object(core['C'].D, 'lease_owned', return_value=True):
            facade.require_context(context)
            self.assertEqual(facade.resolve_capture_run(context, record), member['run'])
            with self.assertRaises(ValueError): facade.require_context(dict(context))
            with self.assertRaises(ValueError): facade.resolve_capture_run(context, {**record, 'scene': 'other'})
            context['phase'] = 'exposure'
            with self.assertRaises(ValueError): facade.require_context(context)
            context.pop('phase')
        with patch.object(core['C'].D, 'lease_owned', return_value=False):
            with self.assertRaises(ValueError): facade.require_context(context)
        for method in ('execute_analysis', 'create_phase', 'require_render_admission',
                       'require_native_admission', 'require_owner_admission', 'qualification_native'):
            self.assertFalse(hasattr(facade, method))


if __name__ == '__main__': unittest.main()
