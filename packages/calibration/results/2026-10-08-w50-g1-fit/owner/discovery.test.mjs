import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,writeFileSync,rmSync,realpathSync,mkdirSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {resolve} from 'node:path';
import {discoverSources} from './discover.mjs';
function fixture(t) {
  const root=realpathSync(mkdtempSync(resolve(tmpdir(),'w50-owner-static-')));
  t.after(()=>rmSync(root,{recursive:true,force:true}));
  writeFileSync(resolve(root,'package.json'),'{"type":"module"}');
  return {root,write:(name,text)=>writeFileSync(resolve(root,name),text)};
}
test('static discovery follows source imports without executing imported side effects',t=>{
  const f=fixture(t);
  f.write('entry.ts',"import './helper.ts'; throw Error('must not execute');");
  f.write('helper.ts','throw Error("must not execute helper");');
  f.write('ast.py','raise Exception("must not execute AST source")');
  const result=discoverSources(f.root,[resolve(f.root,'entry.ts')],[resolve(f.root,'ast.py')]);
  assert.deepEqual(result.sources.map(p=>p.path),['ast.py','entry.ts','helper.ts','package.json']);
});
test('discovery follows TypeScript import-equals without executing the required helper',t=>{
  const f=fixture(t);
  f.write('entry.ts',"import helper = require('./helper.cjs'); throw Error('entry must not execute');");
  f.write('helper.cjs',"throw Error('helper must not execute');");
  const paths=discoverSources(f.root,[resolve(f.root,'entry.ts')]).sources.map(p=>p.path);
  assert.deepEqual(paths,['entry.ts','helper.cjs','package.json']);
});
test('discovery refuses a nonliteral external import-equals expression',t=>{
  const f=fixture(t);
  f.write('entry.ts','const name="./helper.cjs"; import helper = require(name);');
  assert.throws(()=>discoverSources(f.root,[resolve(f.root,'entry.ts')]),/Dynamic import/);
});
test('discovery rejects data imported as modules rather than hashing measurements',t=>{
  const f=fixture(t);mkdirSync(resolve(f.root,'results'));
  f.write('entry.ts',"import data from './results/matrix.json';");
  f.write('results/matrix.json','{"measured":42}');
  assert.throws(()=>discoverSources(f.root,[resolve(f.root,'entry.ts')]),/source-only/);
});
test('discovery refuses unresolved dynamic import instead of allowing a guessed closure',t=>{
  const f=fixture(t);f.write('entry.ts','const path="x"; import(path);');
  assert.throws(()=>discoverSources(f.root,[resolve(f.root,'entry.ts')]),/Dynamic import/);
});
test('discovery pins nested package and type configuration boundaries',t=>{
  const f=fixture(t);mkdirSync(resolve(f.root,'nested'));
  f.write('entry.ts',"import './nested/helper.ts';");
  f.write('nested/helper.ts','export const x=1;');
  f.write('nested/package.json','{"type":"module"}');f.write('nested/tsconfig.json','{}');
  const paths=discoverSources(f.root,[resolve(f.root,'entry.ts')]).sources.map(p=>p.path);
  assert.ok(paths.includes('nested/package.json'));assert.ok(paths.includes('nested/tsconfig.json'));
});
