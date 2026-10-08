import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,writeFileSync,rmSync,readFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {assertPreseal,assertDataPath} from './discovery-common.mjs';

test('discovery refuses any already registered execution root before work',()=>{
  const root=mkdtempSync(join(tmpdir(),'w50-discovery-sealed-'));
  try {
    assertPreseal(root);
    mkdirSync(join(root,'execution'));
    writeFileSync(join(root,'execution/execution-root.json'),'{}');
    assert.throws(()=>assertPreseal(root),/already sealed/);
  } finally {rmSync(root,{recursive:true,force:true});}
});

test('actual discovery preload refuses a sealed execution root before importing a target',()=>{
  const root=mkdtempSync(join(tmpdir(),'w50-discovery-preload-'));
  try {
    const wave=join(root,'packages/calibration/results/wave');
    const web=join(wave,'web');mkdirSync(web,{recursive:true});mkdirSync(join(wave,'execution'));
    for(const name of ['discovery-common.mjs','discovery-hooks.mjs'])
      writeFileSync(join(web,name),readFileSync(new URL(name,import.meta.url)));
    writeFileSync(join(wave,'execution/execution-root.json'),'{}');
    const run=spawnSync(process.execPath,['--import',join(web,'discovery-hooks.mjs'),'-e',"console.log('TARGET_RAN')"],
      {encoding:'utf8',env:{...process.env,W50_DISCOVERY_SCRATCH:join(root,'scratch')}});
    assert.notEqual(run.status,0);assert.match(run.stderr,/already sealed/);
    assert.doesNotMatch(run.stdout,/TARGET_RAN/);
  } finally {rmSync(root,{recursive:true,force:true});}
});

test('discovery cannot consume real pixels or canonical statistical evidence',()=>{
  for(const path of ['/repo/apps/reference-apple/fixtures/native.png',
    '/archive/native.zip','/repo/packages/calibration/web-captures/a.json',
    '/repo/packages/calibration/results/generations/index.json','/repo/results/matrix.json']) {
    assert.throws(()=>assertDataPath(path,'/scratch/probe'),/real measurement data/);
  }
  assertDataPath('/scratch/probe/synthetic.png','/scratch/probe');
  assertDataPath('/repo/apps/reference-apple/scenes.json','/scratch/probe');
});

test('builder exercises both real Node entrypoints and both Vite scene graphs without a browser',()=>{
  const root=mkdtempSync(join(tmpdir(),'w50-discovery-test-'));
  try {
    const out=join(root,'proposal');
    const script=fileURLToPath(new URL('./discover.mjs',import.meta.url));
    const result=spawnSync(process.execPath,[script,out],{encoding:'utf8',timeout:120000});
    assert.equal(result.status,0,result.stderr+'\n'+result.stdout);
    const proposal=JSON.parse(readFileSync(join(out,'proposal.json'),'utf8'));
    assert.equal(proposal.status,'PROPOSED_SOURCE_ONLY');
    assert.equal(proposal.runtimeAuthorization,false);
    assert.deepEqual(proposal.routes.map(r=>r.route).sort(),
      ['browser-canonical','browser-w50','capture-canonical','capture-w50','compare-canonical']);
    const paths=new Set(proposal.sources.map(p=>p.path));
    for(const path of ['packages/calibration/cli/compare.ts','packages/calibration/scripts/capture-web.ts',
      'packages/calibration/web/scene.ts','packages/calibration/web/index.html',
      'packages/calibration/web/vite.config.ts','apps/reference-apple/scenes.json',
      'packages/renderer-webgpu/src/renderer.ts','packages/platform-web/src/css-tier.ts',
      'packages/calibration/cli/measure.ts',
      'packages/calibration/results/2026-10-08-w50-g0-declaration/bed/scenes-w50.json',
      'packages/calibration/package.json','package.json','pnpm-lock.yaml'])assert.ok(paths.has(path),path);
    for(const route of proposal.routes) {
      assert.equal(route.browserLaunched,false);
      assert.equal(route.realMeasurementDataRead,false);
    }
    const again=spawnSync(process.execPath,[script,out],{encoding:'utf8'});
    assert.notEqual(again.status,0);assert.match(again.stderr,/fresh scratch/);
  } finally {rmSync(root,{recursive:true,force:true});}
});
