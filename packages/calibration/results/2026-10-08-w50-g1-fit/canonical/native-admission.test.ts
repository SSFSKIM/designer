import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {syncBuiltinESMExports} from 'node:module';
import {tmpdir} from 'node:os';
import {join,relative} from 'node:path';
import {createHash} from 'node:crypto';
import {admitNative} from './native-admission.ts';
import {candidateMaterialLabel} from '../../../src/material-selection.ts';
import {colourlessTintEvidence} from '../../../cli/gates.ts';

const digest=(p:string)=>createHash('sha256').update(fs.readFileSync(p)).digest('hex');
test('selected native admission never opens out-of-batch holdout and refuses lost tint',()=>{
 const root=fs.mkdtempSync(join(tmpdir(),'w50-selected-native-'));
 const original=fs.readFileSync;
 try {
  const scenes=[{id:'orange',background:'photo',component:'capsule',state:'rest',tint:'orange'},
   {id:'blue',background:'photo',component:'capsule',state:'rest',tint:'blue'},
   {id:'withheld',background:'photo',component:'capsule',state:'rest',tint:'red'}];
  const spec={scenes,split:{calibration:['orange','blue'],holdout:['withheld']}};
  for(const id of ['orange','blue'])fs.writeFileSync(join(root,id+'.png'),id);
  const manifest={profiles:[{profileKey:'p',fixtures:scenes.map(s=>({sceneId:s.id,file:s.id+'.png',fixtureSet:s.id==='withheld'?'holdout':'calibration',materialRendered:true}))}]};
  const pins=['orange','blue'].map(scene=>({scene,path:join(root,scene+'.png'),sha256:digest(join(root,scene+'.png'))}));
  const reads:string[]=[];
  fs.readFileSync=((path:any,...args:any[])=>{reads.push(String(path));if(String(path).includes('withheld'))throw Error('OUTSIDE_BATCH');return (original as any)(path,...args);}) as typeof fs.readFileSync;
  syncBuiltinESMExports();
  const request={profile:'p',scenes:['orange','blue'],sets:['calibration'],native:pins};
  assert.throws(()=>colourlessTintEvidence(spec as any,manifest as any,root),/OUTSIDE_BATCH/);
  reads.length=0;
  const admitted=admitNative(spec as any,manifest as any,root,request);
  assert.equal(admitted.status,'ADMITTED');
  assert.equal(admitted.tint.status,'NO_DUPLICATE_IN_SELECTED_PAIRS');
  const singleton=admitNative(spec as any,manifest as any,root,{...request,scenes:['orange'],native:[pins[0]!]});
  assert.equal(singleton.tint.status,'NOT_COMPARABLE');
  assert.ok(reads.length>0);assert.ok(reads.every(p=>!p.includes('withheld')));
  manifest.profiles[0]!.fixtures[0]!.materialRendered=false;
  const before=reads.length;
  assert.throws(()=>admitNative(spec as any,manifest as any,root,request),/material/);
  assert.equal(reads.length,before);
  manifest.profiles[0]!.fixtures[0]!.materialRendered=true;
  const nested=join(root,'nested');fs.mkdirSync(nested);
  const escapedManifest={...manifest,profiles:[{...manifest.profiles[0],fixtures:[
    {...manifest.profiles[0]!.fixtures[0],file:'../orange.png'}]}]};
  assert.throws(()=>admitNative(spec as any,escapedManifest as any,nested,
    {...request,scenes:['orange'],native:[pins[0]!]}),/escapes fixture root/);
  fs.writeFileSync(join(root,'blue.png'),'orange');pins[1]!.sha256=digest(join(root,'blue.png'));
  assert.throws(()=>admitNative(spec as any,manifest as any,root,request),/tint/i);
  spec.scenes.forEach(s=>s.state='inactive');
  assert.equal(admitNative(spec as any,manifest as any,root,request).status,'ADMITTED');
  pins[0]!.sha256='0'.repeat(64);
  assert.throws(()=>admitNative(spec as any,manifest as any,root,request),/pin/i);
 }finally{fs.readFileSync=original;syncBuiltinESMExports();fs.rmSync(root,{recursive:true,force:true});}
});

test('production candidate label uses the driver repository-relative declaration',()=>{
 const root=process.env.W50_TEST_REPO!;
 const path=join(root,'candidate.json');
 const shown=relative(root,path);
 console.log('PRODUCTION_LABEL='+candidateMaterialLabel({declaration:shown,sha256:'a'.repeat(12),name:'synthetic',glassTintAmount:.25}));
 assert.equal(shown,'candidate.json');
});
