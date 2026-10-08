import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync, mkdirSync, writeFileSync, readFileSync, realpathSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {resolve, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
const HERE=dirname(fileURLToPath(import.meta.url));
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');

function fixture(t) {
  const root=realpathSync(mkdtempSync(resolve(tmpdir(),'w50-owner-guard-')));
  t.after(()=>rmSync(root,{recursive:true,force:true}));
  for(const dir of ['owner','web','nested'])mkdirSync(resolve(root,dir));
  for(const [to,from] of [['owner/node-guard.mjs','node-guard.mjs'],
    ['web/node-guard.mjs','../web/node-guard.mjs'],['web/vite-guard.mjs','../web/vite-guard.mjs']]) {
    writeFileSync(resolve(root,to),readFileSync(resolve(HERE,from)));
  }
  writeFileSync(resolve(root,'package.json'),'{"type":"module"}');
  writeFileSync(resolve(root,'entry.mjs'),'console.log("synthetic")');
  writeFileSync(resolve(root,'ast.ts'),'export const value=1;');
  writeFileSync(resolve(root,'nested/helper.mjs'),'console.log("SIDE EFFECT")');
  const names=['owner/node-guard.mjs','web/node-guard.mjs','web/vite-guard.mjs',
    'package.json','entry.mjs','ast.ts','nested/helper.mjs'];
  function seal() {
    const closure=JSON.stringify({sources:names.map(path=>({path,sha256:hash(readFileSync(resolve(root,path)))}))});
    writeFileSync(resolve(root,'closure.json'),closure);
    return hash(closure);
  }
  function run(digest=seal(),extra=[]) {
    return spawnSync(process.execPath,['--import',resolve(root,'owner/node-guard.mjs'),...extra,resolve(root,'entry.mjs')],
      {encoding:'utf8',env:{...process.env,W50_WEB_ROOT:root,W50_WEB_CLOSURE:resolve(root,'closure.json'),
        W50_WEB_CLOSURE_SHA256:digest}});
  }
  return {root,run,seal,write:(file,bytes)=>writeFileSync(resolve(root,file),bytes)};
}

test('guard admits the fixed synthetic imported and AST-read sources',t=>{
  const f=fixture(t);
  f.write('entry.mjs',"import {readFileSync} from 'node:fs'; console.log(readFileSync(new URL('./ast.ts',import.meta.url),'utf8'));");
  const r=f.run();assert.equal(r.status,0,r.stderr);assert.match(r.stdout,/value=1/);
});
test('guard admits synthetic TypeScript through the installed pinned compiler route',t=>{
  const f=fixture(t);
  f.write('entry.mjs',"import {value} from './ast.ts'; console.log(value);");
  f.write('ast.ts','export const value:number=7;');
  const tsx=createRequire(import.meta.url).resolve('tsx');
  const r=f.run(undefined,['--import',tsx]);
  assert.equal(r.status,0,r.stderr);assert.equal(r.stdout,'7\n');
});
test('new import is refused before its module body side effect',t=>{
  const f=fixture(t);f.write('entry.mjs',"await import('./new.mjs');");
  f.write('new.mjs','console.log("SIDE EFFECT")');
  const r=f.run();assert.notEqual(r.status,0);assert.doesNotMatch(r.stdout,/SIDE EFFECT/);
  assert.match(r.stderr,/Unsealed|unsealed/);
});
test('new dynamic source reader file is refused before content is evaluated',t=>{
  const f=fixture(t);f.write('entry.mjs',"import {readFileSync} from 'node:fs'; eval(readFileSync(new URL('./new.ts',import.meta.url),'utf8'));");
  f.write('new.ts','console.log("SIDE EFFECT")');
  const r=f.run();assert.notEqual(r.status,0);assert.doesNotMatch(r.stdout,/SIDE EFFECT/);
  assert.match(r.stderr,/Unsealed|unsealed/);
});
test('source or closure mutation is refused before entrypoint',t=>{
  for(const name of ['ast.ts','closure.json']) {
    const f=fixture(t),digest=f.seal();f.write(name,'console.log("SIDE EFFECT")');
    const r=f.run(digest);assert.notEqual(r.status,0);assert.equal(r.stdout,'');
  }
});
test('a newly introduced module or type boundary is refused',t=>{
  for(const name of ['package.json','tsconfig.json']) {
    const f=fixture(t);f.write('entry.mjs',"await import('./nested/helper.mjs');");
    const digest=f.seal();f.write(`nested/${name}`,'{}');
    const r=f.run(digest);assert.notEqual(r.status,0);assert.doesNotMatch(r.stdout,/SIDE EFFECT/);
  }
});
