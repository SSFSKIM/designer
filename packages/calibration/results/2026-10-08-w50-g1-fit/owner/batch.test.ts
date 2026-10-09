import test from 'node:test';
import assert from 'node:assert/strict';
import { ownerRows, projectCurrentBatch, projectPreparedInventory, ownerContracts } from './witness.ts';
import { prepareCurrent } from './api.ts';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { executeRequest } from './bridge.ts';
const inventory=()=>({schema:'w50-reference-inventory-1',cells:Array.from({length:640},(_,i)=>({
  profile:'apple-macos-27.0-1x-dark-standard-glass0.5',renderer:i%2?'css':'webgpu',
  scene:`synthetic-${i}`,statistic:'owner-contracts',role:'gate',B:null,
}))});
test('batch derives every one of 640 identities from inventory, not caller selection',()=>{
  const manifest=inventory();
  manifest.cells.push({...manifest.cells[0],statistic:'T1'});
  const rows=ownerRows(manifest);
  assert.equal(rows.length,640);
  assert.equal(new Set(rows.map(r=>JSON.stringify(r))).size,640);
  assert.ok(rows.every(r=>r.statistic==='owner-contracts'));
  const missing=inventory();missing.cells.pop();
  assert.throws(()=>ownerRows(missing),/640/);
  const duplicate=inventory();duplicate.cells[1]=duplicate.cells[0];
  assert.throws(()=>ownerRows(duplicate),/duplicate/i);
});
test('production batch refuses another inventory pin before opening inputs',()=>{
  const pin={path:'/not-opened',sha256:'0'.repeat(64)};
  assert.throws(()=>projectCurrentBatch(pin,pin,pin,pin),/original.*inventory/i);
  assert.throws(()=>executeRequest({mode:'project-current-batch',inputsPin:pin,
    completedReferencesPin:pin,contractsPin:pin,inventoryPin:pin,rows:[]}),/Unexpected field/);
});
test('640 projections reuse one prepared context and retain unselected aggregate context',()=>{
  const dir=mkdtempSync(join(dirname(fileURLToPath(import.meta.url)),'.synthetic-'));
  try {
    const put=(name:string,value:unknown)=>{
      const raw=Buffer.from(JSON.stringify(value)),path=join(dir,name);writeFileSync(path,raw);
      return {path,sha256:createHash('sha256').update(raw).digest('hex')};
    };
    const manifest=inventory();manifest.cells.forEach(r=>r.renderer='css');
    const identities=[...manifest.cells,{...manifest.cells[0],scene:'context-only'}];
    const rows=identities.map(r=>({key:{profileKey:r.profile,sceneId:r.scene,
      web:{renderer:'css',samplingBackend:'css-backdrop',capturePath:
        'materialProfile=a sha256:aaaaaaaaaaaa recededProfile=r sha256:bbbbbbbbbbbb'}},
      tier:'dom',fixtureSet:'validation',state:'rest'}));
    const inputs={declaration:put('scenes.json',{canvas:{width:1,height:1},
      components:{box:{kind:'rrect',size:[1,1]}},
      scenes:identities.map(r=>({id:r.scene,state:'rest',component:'box',background:'light-solid'})),
      split:{validation:identities.map(r=>r.scene)}}),
      current:[{matrix:put('matrix.json',{schemaVersion:5,cells:rows}),documents:{a:'a'.repeat(64),r:'b'.repeat(64)}}],
      references:[],captures:{},referenceCaptures:{},python:'/Users/new/vitrea-w49/py/bin/python'};
    const context=prepareCurrent(inputs),contracts=ownerContracts(inputs.python);
    const pins={inputsPin:put('inputs.json',inputs),reportPin:put('report.json',context.current),
      contractsPin:put('contracts.json',contracts)};
    // Deleting the inputs after preparation proves projection cannot reopen or re-prepare them.
    rmSync(inputs.current[0].matrix.path);rmSync(inputs.declaration.path);
    const result=projectPreparedInventory(context,contracts,manifest,pins);
    assert.equal(result.length,640);
    assert.equal(new Set(result.map(r=>r.cellId)).size,640);
    assert.ok(result.every(r=>r.row.scene!=='context-only'));
    assert.ok(result.every(r=>r.axes.coherence.evidence.state==='UNMEASURED'
      &&r.axes.coherence.evidence.diagnosticOnly===true));
    assert.equal(context.currentRows.length,641);
  } finally {rmSync(dir,{recursive:true});}
});
