import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,realpathSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {resolve} from 'node:path';
import {discoverLiveSources,exerciseRuntime} from './live-discover.mjs';
import {copyFileSync,mkdirSync,readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
function fixture(t) {
  const root=realpathSync(mkdtempSync(resolve(tmpdir(),'w50-live-source-')));
  t.after(()=>rmSync(root,{recursive:true,force:true}));
  const write=(name,text)=>writeFileSync(resolve(root,name),text);
  write('package.json','{"type":"module"}');
  return {root,write};
}
test('additive discovery retains static helper and explicit bootstrap source without execution',t=>{
  const f=fixture(t);
  f.write('entry.ts',"import './helper.ts'; throw Error('not executed');");
  f.write('helper.ts',"throw Error('not executed');");
  f.write('bootstrap.py',"raise RuntimeError('not executed')");
  const result=discoverLiveSources(f.root,[resolve(f.root,'entry.ts')],[resolve(f.root,'bootstrap.py')]);
  assert.deepEqual(result.sources.map(p=>p.path),['bootstrap.py','entry.ts','helper.ts','package.json']);
  assert.equal(result.exercise,undefined);
});
test('new entries do not silently admit unresolved dynamic imports',t=>{
  const f=fixture(t);f.write('entry.ts','const x="./unknown.ts"; import(x);');
  assert.throws(()=>discoverLiveSources(f.root,[resolve(f.root,'entry.ts')]),/Dynamic import/);
});
test('new entries refuse data imports before reading any measured document',t=>{
  const f=fixture(t);f.write('entry.ts',"import './never-created-pixels.png';");
  assert.throws(()=>discoverLiveSources(f.root,[resolve(f.root,'entry.ts')]),/source-only/);
});
test('fixed source-only probe exercises a synthetic closure before emitting runtime metadata',t=>{
  const f=fixture(t),root=resolve(f.root,'repo');mkdirSync(root);
  const home=resolve(root,'packages/calibration/results/2026-10-08-w50-g1-fit');
  for(const name of ['owner-candidate','owner','web'])mkdirSync(resolve(home,name),{recursive:true});
  const here=dirname(fileURLToPath(import.meta.url));
  writeFileSync(resolve(root,'package.json'),'{"type":"module"}');
  for(const name of ['owner/node-guard.mjs','web/node-guard.mjs','web/vite-guard.mjs'])
    copyFileSync(resolve(here,'..',name),resolve(home,name));
  copyFileSync(resolve(here,'live-probe.mjs'),resolve(home,'owner-candidate/live-probe.mjs'));
  writeFileSync(resolve(home,'owner-candidate/bridge.ts'),'export const synthetic = true;');
  writeFileSync(resolve(home,'owner-candidate/frozen-engine.ts'),
    'export function createCandidateEngine({sourcePins,declarations}) { if(Object.keys(sourcePins).length!==4||declarations.length) throw Error("not synthetic"); }');
  writeFileSync(resolve(home,'owner-candidate/union.ts'),
    'export function selectOwnerUnion(rows) { if(rows.length) throw Error("not synthetic"); }');
  const readers=['api.ts','referee.ts','intrinsic.ts','source.ts'].map(name=>{
    const path=resolve(home,'owner',name);writeFileSync(path,'// synthetic source, no data');return path;
  });
  const entries=['owner-candidate/bridge.ts','owner-candidate/frozen-engine.ts',
    'owner-candidate/union.ts','owner/node-guard.mjs'].map(name=>resolve(home,name));
  readers.push(resolve(home,'owner-candidate/live-probe.mjs'));
  const closure=discoverLiveSources(root,entries,readers);
  const sourceFile=resolve(f.root,'static.json');writeFileSync(sourceFile,JSON.stringify(closure));
  const pin=path=>({path:realpathSync(path),sha256:createHash('sha256').update(readFileSync(path)).digest('hex')});
  const toolchain={node:pin(process.execPath),tsx:pin(createRequire(import.meta.url).resolve('tsx/esm/api'))};
  const output=resolve(f.root,'runtime.json');
  const runtime=exerciseRuntime(root,pin(sourceFile),toolchain,output);
  const result=JSON.parse(readFileSync(runtime.path,'utf8'));
  assert.equal(result.schema,'w50-owner-candidate-runtime-1');
  assert.equal(result.exercise,'synthetic source-only');
  assert.deepEqual(result.toolchain,toolchain);
  assert.deepEqual(result.sources,closure.sources);
  assert.throws(()=>exerciseRuntime(root,pin(sourceFile),toolchain,output),/fresh external/);
});
