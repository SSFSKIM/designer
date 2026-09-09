"""Acceptance regressions exercised through the report CLI with isolated evidence."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('glass-rules-analyze.py')
BASELINE = SCRIPT.parent.parent / 'data/2026-09-10-liquid-glass-demos/audit/music-player.json'
PANEL = ('astra-medium', 'astra-high', 'claude-opus', 'claude-sonnet')


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.audit = json.loads(BASELINE.read_text())

    def run_report(self, raters=PANEL, failed=(), audit=True, missing_rule=None):
        for rater in raters:
            path = self.root / 'rules' / rater / 'music-player.json'
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({'slug': 'music-player', 'rules': {
                f'r{i}': int(f'r{i}' not in failed) for i in range(1, 26)
                if (rater, f'r{i}') != missing_rule},
                'quality': {k: 6 for k in ('a1', 'a2', 'a3', 'a4', 'd1', 'e1')}}))
        if audit:
            path = self.root / 'audit/music-player.json'
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(self.audit))
        # The mutable demo copy deliberately disagrees with the frozen audit.
        mutable = self.root / 'demos/music-player/audit.json'
        mutable.parent.mkdir(parents=True, exist_ok=True)
        mutable.write_text(json.dumps(json.loads(BASELINE.read_text())))
        out = self.root / 'custom/report.md'
        result = subprocess.run([sys.executable, str(SCRIPT), '--out', str(out)],
            env={**os.environ, 'GLASS_DATA': str(self.root),
                 'GLASS_DEMOS': str(self.root / 'demos')}, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(out.read_text(), result.stdout)
        self.assertFalse((self.root / 'results.md').exists())
        return result.stdout

    def test_complete_panel_can_pass_at_22_but_not_21(self):
        self.assertIn('**music-player: PASSES**', self.run_report(failed=('r18', 'r19', 'r23')))
        report = self.run_report(failed=('r18', 'r19', 'r23', 'r24'))
        self.assertNotIn('**music-player: PASSES**', report)
        self.assertIn('21 of 25', report)

    def test_two_raters_cannot_be_final_panel(self):
        report = self.run_report(raters=PANEL[:2])
        self.assertNotIn('**music-player: PASSES**', report)
        self.assertIn('claude-opus', report)
        self.assertIn('provisional', report.lower())

    def test_partial_fourth_rater_cannot_pass(self):
        report = self.run_report(missing_rule=('claude-opus', 'r25'))
        self.assertNotIn('**music-player: PASSES**', report)

    def test_unknown_rater_cannot_substitute(self):
        report = self.run_report(raters=(*PANEL[:3], 'replacement'))
        self.assertNotIn('**music-player: PASSES**', report)

    def test_fatal_rule_blocks_even_24_held(self):
        self.assertNotIn('**music-player: PASSES**', self.run_report(failed=('r1',)))

    def test_page_without_menu_can_pass(self):
        self.audit['menu'] = 'not-offered'
        self.audit['menuDiagnostics'] = None
        self.assertIn('**music-player: PASSES**', self.run_report())

    def test_no_audit_fields_cannot_pass(self):
        self.audit = {}
        self.assertNotIn('**music-player: PASSES**', self.run_report())

    def test_absent_frozen_audit_does_not_use_mutable_copy(self):
        self.assertNotIn('**music-player: PASSES**', self.run_report(audit=False))

    def test_menu_diagnostic_blocks_pass(self):
        self.audit['menuDiagnostics'] = [{'code': 'same-plane-overlap'}]
        report = self.run_report()
        self.assertNotIn('**music-player: PASSES**', report)
        self.assertIn('same-plane-overlap', report)

    def test_reduced_ok_alone_is_insufficient(self):
        self.audit['reduced'] = {'ok': True}
        self.assertNotIn('**music-player: PASSES**', self.run_report())

    def test_reduced_failures_are_not_hidden(self):
        for key, value in [('overrideHonoured', False), ('materialMoved', False),
                           ('errors', ['reduced page error'])]:
            with self.subTest(key=key):
                self.audit = json.loads(BASELINE.read_text())
                self.audit['reduced'][key] = value
                self.assertNotIn('**music-player: PASSES**', self.run_report())

    def test_missing_diagnostics_are_unknown(self):
        del self.audit['diagnostics']
        self.assertNotIn('**music-player: PASSES**', self.run_report())

    def test_accessibility_is_not_promoted_to_rules(self):
        report = self.run_report(failed=('r18', 'r19', 'r23', 'r24'))
        self.assertIn('21 of 25', report)
        self.assertIn('both schemes', report)
        self.assertIn('increased contrast', report)
        self.assertIn('materialMoved', report)


if __name__ == '__main__':
    unittest.main()
