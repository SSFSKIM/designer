import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, symlinkSync, rmSync } from 'node:fs';
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

// Run the real node -> npx -> tsx boundary. A type:module parent must not conceal a
// CommonJS child, and an admitted entry must not confer admission on its dependencies.
for (const route of ['npx-child','direct-import']) {
for (const boundary of ['mixed','implicit-commonjs']) {
for (const extension of ['ts','cts','cjs']) {
  for (const defect of ['none','new-import','changed-after-preload','unsealed-format']) {
    if (boundary==='implicit-commonjs' && defect==='unsealed-format') continue;
    test(`tsx ${route} ${boundary} ${extension}: ${defect}`, () => {
      const root=mkdtempSync(join(tmpdir(),'w50-cjs-guard-'));
      try {
        mkdirSync(join(root,'nested'));
        const files={
          ...(boundary==='mixed' ? {'package.json':'{"type":"module"}',
            'nested/package.json':'{"type":"commonjs"}'} : {}),
          'parent.mjs':"import {spawnSync} from 'node:child_process'; const p=spawnSync('npx',['--no-install','tsx',process.argv[2]],{stdio:'inherit'}); process.exit(p.status ?? 1);\n",
          'child.ts':"import './nested/pinned.ts';\n",
          'nested/pinned.ts':(defect==='changed-after-preload'
            ? `require('node:fs').writeFileSync(${JSON.stringify(join(root,`nested/target.${extension}`))},\"console.log('UNADMITTED_BODY');\\n\");\n` : '')+
            `require('./target.${extension}');\n`,
          [`nested/target.${extension}`]:"console.log('ADMITTED_BODY');\n",
        };
        for(const [path,bytes] of Object.entries(files))writeFileSync(join(root,path),bytes);
        const text=JSON.stringify({sources:Object.entries(files)
          .filter(([path])=>(defect!=='new-import' || !path.startsWith('nested/target.')) &&
            (defect!=='unsealed-format' || path!=='nested/package.json'))
          .map(([path,bytes])=>({path,sha256:hash(bytes)}))});
        writeFileSync(join(root,'closure.json'),text);
        const argv=route==='npx-child' ? [join(root,'parent.mjs'),join(root,'child.ts')]
          : ['--import','tsx','--import',guard,join(root,'child.ts')];
        const result=spawnSync(process.execPath,argv,{
          cwd:fileURLToPath(new URL('../../../',import.meta.url)),encoding:'utf8',
          env:{...process.env,NODE_OPTIONS:route==='npx-child'
            ? `--import=${new URL('./node-guard.mjs',import.meta.url).href}` : '',
            W50_WEB_ROOT:root,W50_WEB_CLOSURE:join(root,'closure.json'),W50_WEB_CLOSURE_SHA256:hash(text)}});
        if(defect==='none') {assert.equal(result.status,0,result.stderr);assert.match(result.stdout,/ADMITTED_BODY/);}
        else {
          assert.notEqual(result.status,0,'unadmitted CommonJS body executed');
          assert.match(result.stderr,/Unsealed or changed web source/);
          assert.doesNotMatch(result.stdout,/ADMITTED_BODY/);
        }
      } finally {rmSync(root,{recursive:true,force:true});}
    });
  }
}

}

}

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
