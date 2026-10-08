import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, readFileSync, symlinkSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
const guard = fileURLToPath(new URL('./node-guard.mjs', import.meta.url));
const hash = value => createHash('sha256').update(value).digest('hex');

test('Vite plugin rejects a newly introduced browser module before transformation', () => {
  const root=mkdtempSync(join(tmpdir(),'w50-vite-guard-'));
  try {
    const guardBytes=readFileSync(guard);
    const shimBytes=readFileSync(new URL('./vite-guard.mjs',import.meta.url));
    writeFileSync(join(root,'node-guard.mjs'),guardBytes);
    writeFileSync(join(root,'vite-guard.mjs'),shimBytes);
    symlinkSync(fileURLToPath(new URL('../../../node_modules',import.meta.url)),join(root,'node_modules'));
    writeFileSync(join(root,'unsealed.ts'),'export const unexpected=1;');
    const entry=`import {sourcePlugin} from './vite-guard.mjs';\nsourcePlugin().load(${JSON.stringify(join(root,'unsealed.ts'))});\n`;
    writeFileSync(join(root,'entry.mjs'),entry);
    const text=JSON.stringify({sources:[
      {path:'node-guard.mjs',sha256:hash(guardBytes)},
      {path:'vite-guard.mjs',sha256:hash(shimBytes)},
      {path:'entry.mjs',sha256:hash(entry)},
    ]});
    writeFileSync(join(root,'closure.json'),text);
    const result=spawnSync(process.execPath,['--import',join(root,'node-guard.mjs'),join(root,'entry.mjs')],{
      encoding:'utf8',env:{...process.env,W50_WEB_ROOT:root,
        W50_WEB_CLOSURE:join(root,'closure.json'),W50_WEB_CLOSURE_SHA256:hash(text)}});
    assert.notEqual(result.status,0);assert.match(result.stderr,/Unsealed or changed web source: .*unsealed.ts/);
  } finally {rmSync(root,{recursive:true,force:true});}
});

for (const defect of ['none', 'changed', 'new-import']) {
  test(`node source guard ${defect === 'none' ? 'admits pinned sources' : `refuses ${defect}`}`, () => {
    const root=mkdtempSync(join(tmpdir(),'w50-web-guard-'));
    try {
      const source="import './helper.mjs'; console.log('ADMITTED');\n";
      writeFileSync(join(root,'entry.mjs'),source);
      writeFileSync(join(root,'helper.mjs'),'export const n=1;\n');
      const closure={sources:[{path:'entry.mjs',sha256:hash(source)},
        ...defect==='new-import' ? [] : [{path:'helper.mjs',sha256:hash('export const n=1;\n')}]]};
      const text=JSON.stringify(closure);writeFileSync(join(root,'closure.json'),text);
      if(defect==='changed')writeFileSync(join(root,'helper.mjs'),'export const n=2;\n');
      const result=spawnSync(process.execPath,['--import',guard,join(root,'entry.mjs')],{
        encoding:'utf8',env:{...process.env,W50_WEB_ROOT:root,
          W50_WEB_CLOSURE:join(root,'closure.json'),W50_WEB_CLOSURE_SHA256:hash(text)}});
      if(defect==='none') {assert.equal(result.status,0,result.stderr);assert.match(result.stdout,/ADMITTED/);}
      else {assert.notEqual(result.status,0);assert.match(result.stderr,/Unsealed or changed web source/);}
    } finally {rmSync(root,{recursive:true,force:true});}
  });
}
