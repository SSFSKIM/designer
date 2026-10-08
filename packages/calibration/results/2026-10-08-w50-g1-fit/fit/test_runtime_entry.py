"""Real Python closure discovery + separately guarded Node input, all synthetic data."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[4]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


class RuntimeGuardTests(unittest.TestCase):
    def execute(self, *, extra_import=None, changed=False):
        with tempfile.TemporaryDirectory() as name:
            base=Path(name).resolve();repo=base/'repo';repo.mkdir()
            for folder in ('fit','owner','web','fit/common'):(repo/folder).mkdir(parents=True,exist_ok=True)
            names=[]
            for target,source in [('fit/runtime-entry.mjs',HERE/'runtime-entry.mjs'),
                ('owner/node-guard.mjs',HERE.parent/'owner/node-guard.mjs'),
                ('web/node-guard.mjs',HERE.parent/'web/node-guard.mjs'),
                ('web/vite-guard.mjs',HERE.parent/'web/vite-guard.mjs')]:
                shutil.copyfile(source,repo/target);names.append(target)
            (repo/'package.json').write_text('{"type":"module"}');names.append('package.json')
            bridge=repo/'fit/runtime-bridge.ts';prefix=''
            if extra_import=='inside':
                (repo/'fit/unsealed.ts').write_text('console.log("UNSEALED SIDE EFFECT");export const value = 1;')
                prefix="import './unsealed.ts';\n"
            if extra_import=='outside':
                outside=base/'outside.ts';outside.write_text('export const value = 1;')
                prefix=f'import {json.dumps(outside.as_uri())};\n'
            if extra_import=='commonjs':
                (repo/'fit/common/package.json').write_text('{"type":"commonjs"}')
                (repo/'fit/common/helper.cjs').write_text('require("./new.cjs");')
                (repo/'fit/common/new.cjs').write_text('console.log("UNSEALED SIDE EFFECT");')
                names+=['fit/common/package.json','fit/common/helper.cjs']
                prefix="import './common/helper.cjs';\n"
            bridge.write_text(prefix+'export async function fixedGate0Joins(p) { return {synthetic: true, capturedCandidate:p}; }\n')
            names.append('fit/runtime-bridge.ts')
            runtime=repo/'runtime.json'
            runtime.write_text(json.dumps({'schema':'w50-fit-runtime-closure-1','sources':[
                {'path':p,'sha256':sha(repo/p)} for p in names]}))
            runtime_pin={'path':'runtime.json','sha256':sha(runtime)}
            # Exercise the ACTUAL current3 guard: its exact observed==expected inventory is PYTHON ONLY.
            guard=repo/'guard.py';shutil.copyfile(HERE.parents[1]/'2026-10-08-w50-g1-current3/execution/guard.py',guard)
            probe=repo/'probe.py';probe.write_text('value = 1\n')
            spec=importlib.util.spec_from_file_location('synthetic_current3_guard',guard)
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            closure=module.discover(repo,probe,{'guard.py':sha(guard),'probe.py':sha(probe)})
            self.assertEqual(set(closure['sources']),{'guard.py','probe.py'})
            candidate=repo/'gate0.json';candidate.write_text('{}')
            pin={'path':'gate0.json','sha256':sha(candidate)}
            root=repo/'execution-root.json'
            root.write_text(json.dumps({'schema':'w50-g1-execution-root-1','repo':str(repo),
                'baselineDocuments':[pin],'inputs':[runtime_pin],'closure':closure}))
            Path(str(root)+'.sha256').write_text(f'{sha(root)}  {root.name}\n')
            if changed:bridge.write_text(bridge.read_text()+'// changed after root\n')
            env={key:os.environ[key] for key in ('HOME','TMPDIR','TMP','TEMP') if key in os.environ}
            env.update(PATH='/usr/bin:/bin:/usr/sbin:/sbin',TSX_DISABLE_CACHE='1',LC_ALL='C',
                W50_WEB_ROOT=str(repo),W50_WEB_CLOSURE=str(runtime),W50_WEB_CLOSURE_SHA256=runtime_pin['sha256'])
            node=shutil.which('node')
            return subprocess.run([node,'--import',str(repo/'owner/node-guard.mjs'),'--import','tsx',
                str(repo/'fit/runtime-entry.mjs')],cwd=REPO/'packages/calibration',env=env,
                input=json.dumps({'executionRoot':str(root),'runtimeClosure':runtime_pin,
                                  'operation':'joins','baseline':pin}),capture_output=True,text=True)

    def test_python_only_sealable_root_admits_its_separate_runtime_input(self):
        result=self.execute()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(json.loads(result.stdout)['synthetic'])

    def test_new_repository_external_or_commonjs_source_cannot_bypass_guard(self):
        for where in ('inside','outside','commonjs'):
            with self.subTest(where=where):
                result=self.execute(extra_import=where)
                self.assertNotEqual(result.returncode,0)
                self.assertRegex(result.stderr,'Unsealed|unsealed')
                self.assertNotIn('UNSEALED SIDE EFFECT',result.stdout)

    def test_changed_prospective_source_refuses_before_import(self):
        result=self.execute(changed=True)
        self.assertNotEqual(result.returncode,0)
        self.assertRegex(result.stderr,'changed|Changed')


if __name__=='__main__':unittest.main()
