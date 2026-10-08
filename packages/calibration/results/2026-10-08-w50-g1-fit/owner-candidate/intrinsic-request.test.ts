import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync,rmSync,readFileSync } from 'node:fs';
import { dirname,join,resolve,relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { DEFAULT_MATERIAL_PROFILE } from '@vitrea/renderer-webgpu';
import { candidateFixture,put,hash } from './identity.test.ts';
import { checkIntrinsicRecords } from './bridge.ts';
const home=dirname(fileURLToPath(import.meta.url));
const repo=resolve(home,'../../../../..');
const prefix='packages/calibration/results/2026-10-08-w50-g1-fit/owner/';
const P25='apple-macos-27.0-1x-dark-standard-glass0.25';

/** A gate batch whose intrinsic records the frozen engine reads before any marker: two synthetic
 * candidate declarations, one frozen current row at 0.25 and its before document pair. */
function world(dir:string,change:(parts:any)=>void=()=>{}) {
  const a=candidateFixture(dir,.25,'quarter'),b=candidateFixture(dir,.5,'half');
  const parts:any={cohort:[a.pin,b.pin].map(pin=>({...pin,path:relative(repo,pin.path)})),
    beforeActive:{profileKey:P25,patch:{sizeSpanMin:DEFAULT_MATERIAL_PROFILE.sizeSpanMin},entries:{}},
    beforeReceded:{profileKey:P25+'-receded',kind:'receded-endpoint',patch:{},entries:{}},
    active:{endpointSha256:a.endpoints['active.dark'].sha256,retainedMeasuredEntries:{},fittedEntries:{}},
    methods:{endpointSha256:a.endpoints['receded.dark'].sha256,methods:{}}};
  change(parts);
  const beforeActive=put(dir,'before-active.json',parts.beforeActive),beforeReceded=put(dir,'before-receded.json',parts.beforeReceded);
  const stamp=(parts.currentPair??[beforeActive.sha256,beforeReceded.sha256]) as string[];
  const row={key:{profileKey:P25,sceneId:'dark-solid__box__rest',web:{renderer:'webgpu',samplingBackend:'css-backdrop',
    capturePath:`viewport=4x4, deviceScaleFactor=1, materialProfile=a sha256:${stamp[0]!.slice(0,12)} recededProfile=r sha256:${stamp[1]!.slice(0,12)}`}},
    tier:'texture',fixtureSet:'calibration',state:'rest',material:{interiorMeanWeb:{value:.2}}};
  const current={matrix:put(dir,'current.json',{schemaVersion:5,cells:[row]}),documents:{a:stamp[0],r:stamp[1]}};
  const closurePath=resolve(repo,prefix+'r2/source-closure.json'),closure=JSON.parse(readFileSync(closurePath,'utf8'));
  const sourcePins=Object.fromEntries(closure.sources.filter((p:any)=>
    ['api.ts','referee.ts','intrinsic.ts','source.ts'].some(n=>p.path===prefix+n))
    .map((p:any)=>[p.path,{path:resolve(repo,p.path),sha256:p.sha256}]));
  const config=put(dir,'config.json',{schema:'w50-owner-candidate-config-1',ownerInputs:put(dir,'inputs.json',{current:[current]}),
    frozenSourceClosure:{path:closurePath,sha256:hash(readFileSync(closurePath))},sourcePins});
  const records={beforeActive,beforeReceded,methods:put(dir,'methods.json',parts.methods),activeEntries:put(dir,'active.json',parts.active)};
  const intrinsic=put(dir,'intrinsic.json',{candidateDeclarations:parts.declarations??parts.cohort,recededRecords:{'0.25':records}});
  const root=put(dir,'root.json',{repo,inputs:parts.unregistered?[]:[config]});
  const batch=put(dir,'gate-batch.json',{phase:'gate',cohort:parts.cohort,ownerIntrinsicRecords:intrinsic});
  return {config,root,batch,a,b};
}

function admitted(dir:string,change?:(parts:any)=>void,env:Record<string,string>={}) {
  const saved={...process.env};
  try {
    const w=world(dir,change);
    Object.assign(process.env,{W50_OWNER_LIVE_CONFIG:w.config.path,W50_OWNER_LIVE_CONFIG_SHA256:w.config.sha256,
      W50_OWNER_LIVE_ROOT_SHA256:w.root.sha256,W50_OWNER_LIVE_BATCH_SHA256:w.batch.sha256},env);
    return checkIntrinsicRecords({config:w.config,root:w.root,batch:w.batch});
  } finally {
    for(const key of Object.keys(process.env)) if(!(key in saved)) delete process.env[key];
    Object.assign(process.env,saved);
  }
}

test('the frozen engine admits intrinsic records it can read and answers admission only',()=>{
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {assert.deepEqual(admitted(dir),{intrinsic:'ADMITTED'});}
  finally {rmSync(dir,{recursive:true});}
});

test('every content refusal the frozen engine throws after the marker throws before it',()=>{
  const cases:[string,(parts:any)=>void,RegExp][]=[
    ['before active identity',p=>{p.beforeActive.profileKey=P25+'-receded';},/identity/],
    ['before receded identity',p=>{p.beforeReceded.kind='active';},/identity/],
    ['current document pair',p=>{p.currentPair=['1'.repeat(64),'2'.repeat(64)];},/Document pair/],
    ['active record endpoint',p=>{p.active.endpointSha256='3'.repeat(64);},/endpoint hash/],
    ['receded record endpoint',p=>{p.methods.endpointSha256='4'.repeat(64);},/endpoint hash/],
    ['incomplete envelope',p=>{delete p.active.fittedEntries;},/envelope/],
    ['retained record changed',p=>{p.active.retainedMeasuredEntries={sizeSpanMin:{status:'measured',value:1}};},/Retained/],
    ['declarations',p=>{p.declarations=[p.cohort[0]];},/declarations/],
    ['unregistered config',p=>{p.unregistered=true;},/registered/],
  ];
  for(const [name,change,message] of cases) {
    const dir=mkdtempSync(join(home,'.synthetic-'));
    try {assert.throws(()=>admitted(dir,change),message,name);}
    finally {rmSync(dir,{recursive:true});}
  }
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {assert.throws(()=>admitted(dir,undefined,{W50_OWNER_LIVE_BATCH_SHA256:'0'.repeat(64)}),/admission/);}
  finally {rmSync(dir,{recursive:true});}
});
