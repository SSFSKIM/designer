"""Synthetic compiler override regression: execute installed tsx, never an owner data route."""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
NODE = shutil.which('node')
spec = importlib.util.spec_from_file_location('owner_environment', HERE/'run.py')
RUN = importlib.util.module_from_spec(spec)
spec.loader.exec_module(RUN)


class EnvironmentTests(unittest.TestCase):
    def test_inherited_compiler_override_cannot_execute_but_installed_tsx_can(self):
        with tempfile.TemporaryDirectory(prefix='w50-owner-compiler-') as tmp:
            root = Path(tmp).resolve()
            marker = root/'unregistered-compiler-ran'
            compiler = root/'unregistered-compiler'
            compiler.write_text(f'#!/bin/sh\nprintf injected > "{marker}"\nexit 1\n')
            compiler.chmod(0o700)
            entry = root/'synthetic.ts'
            entry.write_text('const value: number = 7; console.log(value);\n')
            with patch.dict(os.environ, {'ESBUILD_BINARY_PATH': str(compiler),
                                         'TSX_DISABLE_CACHE': '1'}):
                env = RUN.child_environment(root/'unused-root.json', '0'*64,
                    {'path': str(root/'unused-closure.json'), 'sha256': '0'*64})
            # Resolve tsx from the real installed dependency, then transform only temporary text.
            script = 'import {pathToFileURL} from "node:url"; await import(pathToFileURL(process.argv[1]).href);'
            result = subprocess.run([NODE, '--import', 'tsx', '--input-type=module', '-e', script,
                                     str(entry)], cwd=CAL, env=env, capture_output=True, text=True)
            self.assertFalse(marker.exists(), 'Inherited ESBUILD_BINARY_PATH executed an unregistered compiler')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, '7\n')

    def test_ambient_tool_and_loader_variables_do_not_cross_child_boundary(self):
        with patch.dict(os.environ, {'ESBUILD_BINARY_PATH': '/unregistered',
                'NODE_OPTIONS': '--import=/unregistered', 'TSX_TSCONFIG_PATH': '/unregistered',
                'LD_PRELOAD': '/unregistered', 'DYLD_INSERT_LIBRARIES': '/unregistered',
                'PYTHONPATH': '/unregistered', 'FUTURE_COMPILER_OVERRIDE': '/unregistered',
                'PATH': '/unregistered'}):
            env = RUN.child_environment('/synthetic/root.json', '0'*64,
                {'path': '/synthetic/closure.json', 'sha256': '0'*64})
        self.assertFalse(any('unregistered' in value for value in env.values()))
        self.assertEqual(env['W50_OWNER_INSTRUMENT'], '/synthetic/root.json')


if __name__ == '__main__':
    unittest.main()
