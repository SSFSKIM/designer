#!/usr/bin/env python3
"""Exercise build refusals without compiling or touching a granted bundle (§5.174)."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]


class BuildGuard(unittest.TestCase):
    def test_protected_aliases_and_failed_signing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            harness = root / 'apps/reference-apple'
            harness.mkdir(parents=True)
            script = harness / 'build.sh'
            shutil.copyfile(ROOT / 'apps/reference-apple/build.sh', script)
            dev = root / 'dev'
            tool = dev / 'Toolchains/XcodeDefault.xctoolchain/usr/bin'
            tool.mkdir(parents=True)
            (dev / 'Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk').mkdir(parents=True)
            fake = '#!/bin/bash\necho called >> "$MARKER"\nexit 0\n'
            (tool / 'swiftc').write_text(fake)
            (tool / 'swiftc').chmod(0o755)
            tools = root / 'bin'; tools.mkdir()
            (tools / 'codesign').write_text('#!/bin/bash\nexit "${SIGN_EXIT:-0}"\n')
            (tools / 'codesign').chmod(0o755)
            env = {**os.environ, 'DEVELOPER_DIR': str(dev), 'PATH': str(tools)+':'+os.environ['PATH'],
                   'MARKER':str(root/'compiler-called')}
            env.pop('VITREA_ALLOW_PROTECTED_REBUILD', None)
            for name in ['build', 'build-probe']:
                protected = harness / name
                protected.mkdir(exist_ok=True)
                alias = root / (name+'-alias'); alias.symlink_to(protected)
                for out in [protected, protected/'nested', alias]:
                    p = subprocess.run(['bash', str(script)], env={**env,'VITREA_BUILD_OUT':str(out)},
                                       capture_output=True,text=True)
                    self.assertNotEqual(p.returncode, 0, str(out))
                    self.assertFalse((root/'compiler-called').exists(), str(out))
            out = root / 'side'
            p = subprocess.run(['bash', str(script)], env={**env,'VITREA_BUILD_OUT':str(out),
                               'VITREA_BUNDLE_ID':'dev.vitrea.reference-apple.w34','SIGN_EXIT':'1'},
                               capture_output=True,text=True)
            self.assertNotEqual(p.returncode,0,'failed signing must fail the build')
            self.assertFalse((out/'harness').exists(),'failed build must not advertise a launcher')
            self.assertIn('dev.vitrea.reference-apple.w34',(out/'VitreaReference.app/Contents/Info.plist').read_text())


if __name__ == '__main__': unittest.main()
