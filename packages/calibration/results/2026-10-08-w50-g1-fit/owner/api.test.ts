import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtempSync, writeFileSync, rmSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { PNG } from 'pngjs';
import { loadContracts, pairedCoherence, recountBlack, validateCapture, identity, type Capture } from './referee.ts';
import { c1Evidence, chromaAggregate } from './api.ts';
const C = loadContracts();
const home = dirname(fileURLToPath(import.meta.url));
const hash = (b: Uint8Array) => createHash('sha256').update(b).digest('hex');
const profile = 'apple-macos-27.0-1x-dark-standard-glass0.5';
const descriptor = 'materialProfile=a.json sha256:aaaaaaaaaaaa recededProfile=r.json sha256:bbbbbbbbbbbb';
const declaration = {canvas:{width:24,height:24},components:{box:{kind:'rrect',size:[8,8]}},
  scenes:[{id:'checkerboard__box__rest',component:'box',background:'checkerboard',state:'rest'}],
  split:{calibration:['checkerboard__box__rest']}};
const row = (renderer='webgpu') => ({key:{profileKey:profile,sceneId:'checkerboard__box__rest',
  web:{renderer,capturePath:descriptor,samplingBackend:renderer==='css'?'css-backdrop':'gpu-texture'}},tier:renderer==='css'?'dom':'texture',state:'rest',
  fixtureSet:'calibration',material:{interiorMeanWeb:{value:.2}}});
function pixels(level: number) {
  const data = new Uint8Array(24*24*4);
  for(let i=0;i<data.length;i+=4) {data[i]=data[i+1]=data[i+2]=level;data[i+3]=255;}
  return PNG.sync.write({width:24,height:24,data:Buffer.from(data)} as PNG);
}
function fixture(dir:string, web:number, renderer='webgpu'):Capture {
  const put = (name:string,bytes:Uint8Array) => {
    const path=join(dir,name);writeFileSync(path,bytes);return {path,sha256:hash(bytes)};
  };
  return {web:put(`web${web}.png`,pixels(web)),native:put('native.png',pixels(0)),
    backdrop:put('backdrop.png',pixels(0)),metadata:put(`meta-${renderer}-${web}.json`,Buffer.from(JSON.stringify({engine:'chromium',engineVersion:'synthetic',
      renderer,samplingBackend:renderer==='css'?'css-backdrop':'gpu-texture',gpuAdapter:'synthetic',
      colorSpace:'srgb',sceneId:row().key.sceneId,pixelSize:[24,24],capturePath:descriptor,
      deterministic:true,repeatNoise:0}))),
    documents:{'a.json':'a'.repeat(64),'r.json':'b'.repeat(64)}};
}
test('coherence refuses absent twin and measures actual full-canvas disagreement', () => {
  assert.equal(pairedCoherence(C,row('css'),undefined).state,'UNMEASURED');
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {
    const css=fixture(dir,0,'css'), gpu=fixture(dir,255);
    const result=pairedCoherence(C,row('css'),row(),css,gpu);
    assert.equal(result.ratio,1);
    assert.equal(result.verdict,'reported');
    assert.equal(result.numericWindowAdopted,false);
    assert.equal((result.counterfactual as any).verdict,'failure');
    assert.ok((result.deltaE as number)>.9);
    gpu.documents['r.json']='c'.repeat(64);
    assert.throws(()=>pairedCoherence(C,row('css'),row(),css,gpu),/same candidate/);
  } finally {rmSync(dir,{recursive:true});}
});
test('X1 recount catches one-code light even when metadata and all row metrics pass', () => {
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {
    const result=recountBlack(C,row(),fixture(dir,1),declaration);
    assert.equal(result.state,'MEASURED');
    assert.equal(result.verdict,'failure');
    assert.ok((result.readings as any).analytic.aboveZero>0);
    assert.equal((result.readings as any).analytic.aboveOne,0);
  } finally {rmSync(dir,{recursive:true});}
});
test('C1 and M1 aggregates refuse incomplete required populations', () => {
  assert.equal(c1Evidence(C,[],declaration,[`${profile}/webgpu/missing`]).state,'UNMEASURED');
  assert.equal(chromaAggregate(C,[],4).state,'UNMEASURED');
});

test('prepare/evaluate preserves original numeric reference and fixed-current evidence', async()=>{
  const {prepareCurrent,evaluate}=await import('./api.ts');
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {
    const put=(name:string,value:any)=>{
      const bytes=Buffer.from(JSON.stringify(value)),path=join(dir,name);
      writeFileSync(path,bytes);return {path,sha256:hash(bytes)};
    };
    const scene='dark-solid__box__rest';
    const decl={...declaration,scenes:[{id:scene,component:'box',background:'dark-solid',state:'rest'}],
      split:{validation:[scene]}};
    const matrix=(name:string,active:string,receded:string,mean:number)=>{
      const a=active.padEnd(64,'0'),b=receded.padEnd(64,'0');
      const r={...row(),fixtureSet:'validation',key:{profileKey:profile,sceneId:scene,
        web:{renderer:'webgpu',capturePath:`materialProfile=a.json sha256:${a.slice(0,12)} recededProfile=r.json sha256:${b.slice(0,12)}`}},
        material:{interiorMeanNative:{value:.2},interiorMeanWeb:{value:mean}}};
      return {matrix:put(name,{schemaVersion:5,cells:[r]}),documents:{'a.json':a,'r.json':b}};
    };
    const context=prepareCurrent({declaration:put('scenes.json',decl),
      current:[matrix('current.json','0eac5b294cc2','b',.21)],
      references:[matrix('reference.json','eab099cc6698','4e68f81869f6',.2)],
      captures:{},referenceCaptures:{},python:'/not-used'});
    const result=evaluate(context,[matrix('candidate.json','c','d',.22)],{},context.current);
    const key=`${profile}/webgpu/${scene}`;
    assert.equal(result.cells[key].L1.native,.2);
    assert.equal(result.cells[key].L1.current,.21);
    assert.equal(result.cells[key].L1.candidate,.22);
    assert.equal(result.cells[key].L1.reference,.2);
    assert.equal(result.cells[key].L1.verdict,'failure');
    assert.equal(result.cells[key].M1.state,'NOT_APPLICABLE');
    assert.equal((result.intrinsic as any).X75.state,'UNMEASURED');
    const sorted=(v:any):any=>Array.isArray(v)?v.map(sorted):v&&typeof v==='object'
      ?Object.fromEntries(Object.keys(v).sort().map(k=>[k,sorted(v[k])])):v;
    assert.doesNotThrow(()=>evaluate(context,[],{},sorted(context.current)));
    const changed=structuredClone(context.current); changed.cells[key].L1.candidate=.99;
    assert.throws(()=>evaluate(context,[],{},changed),/differ/);
    assert.throws(()=>evaluate(context,[],{},{...context.current,noNewTrade:'changed'}),/differ/);
    assert.throws(()=>prepareCurrent({...context.inputs,
      references:[matrix('swapped.json','4e68f81869f6','eab099cc6698',.2)]}),/baseline/);
  } finally {rmSync(dir,{recursive:true});}
});

for(const [field,value] of Object.entries({sceneId:'other__box__rest',renderer:'css',
  samplingBackend:'none',pixelSize:[48,24]})) test(`capture rejects metadata ${field} swap`,()=>{
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {
    const capture=fixture(dir,0), meta=JSON.parse(readFileSync(capture.metadata.path,'utf8'));
    const bytes=Buffer.from(JSON.stringify({...meta,[field]:value}));
    writeFileSync(capture.metadata.path,bytes); capture.metadata.sha256=hash(bytes);
    assert.throws(()=>validateCapture(row(),capture),/scene|renderer|backend|size/i);
  } finally {rmSync(dir,{recursive:true});}
});
test('capture requires full document hashes and equal native/backdrop dimensions',()=>{
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {
    const capture=fixture(dir,0); capture.documents['a.json']='a'.repeat(12);
    assert.throws(()=>validateCapture(row(),capture),/document/);
    capture.documents['a.json']='a'.repeat(64);
    const small=PNG.sync.write({width:1,height:1,data:Buffer.from([0,0,0,255])} as PNG);
    writeFileSync(capture.native.path,small); capture.native.sha256=hash(small);
    assert.throws(()=>validateCapture(row(),capture),/dimension|size/i);
  } finally {rmSync(dir,{recursive:true});}
});
test('X1 refuses captures whose dimensions disagree with declared canvas and profile scale',()=>{
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {assert.throws(()=>recountBlack(C,row(),fixture(dir,0),{
    ...declaration,canvas:{width:48,height:24}}),/canvas|size|dimension/i);
  } finally {rmSync(dir,{recursive:true});}
});
function shadowBed(spans:number[], position='.5') {
  const profile=`apple-macos-27.0-1x-dark-standard-glass0${position}`;
  const components:Record<string,any>={},scenes:any[]=[],rows:any[]=[];
  for(const span of spans) {
    const component=`s${span}`; components[component]={kind:'rrect',size:[span,span]};
    const count=position==='.5'?C.c1.CONTRIBUTING_CELLS['1x dark'][span]:1;
    for(let i=0;i<count;i++) {
      const id=`synthetic-${i}__${component}__rest`;
      scenes.push({id,component,state:'rest',background:'synthetic'});
      const affine=C.c1.ADMITTED_BANDS[span].map((ringLabel:string)=>({direction:'all',ringLabel,slopeALinear:.8}));
      const clearance=Number(C.c1.ADMITTED_BANDS[span].at(-1).split('-')[1]);
      rows.push({...row(),key:{...row().key,profileKey:profile,sceneId:id},shadow:{
        affineNative:affine,affineWeb:structuredClone(affine),backdropSupport:{value:1},
        ...Object.fromEntries(['Above','Below','Left','Right'].map(side=>[`clearance${side}`,{value:clearance}]))}});
    }
  }
  return {rows,decl:{canvas:{width:320,height:240},components,scenes,
    split:{calibration:scenes.map(s=>s.id)}}};
}
test('C1 requires every declared span even when all remaining fixed counts match',()=>{
  for(const position of ['.5','.25']) {
    const {rows,decl}=shadowBed([96,128],position);
    assert.equal(c1Evidence(C,rows,decl,rows.map(identity)).state,'UNMEASURED');
  }
  const {rows,decl}=shadowBed([96,128,160]);
  assert.equal(c1Evidence(C,rows,decl,rows.map(identity)).verdict,'within');
});

test('candidate native/backdrop bytes are bound to the same-cell frozen-current inventory',async()=>{
  const {prepareCurrent,evaluate}=await import('./api.ts');
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {
    const put=(name:string,value:any)=>{
      const bytes=Buffer.from(JSON.stringify(value)),path=join(dir,name);
      writeFileSync(path,bytes); return {path,sha256:hash(bytes)};
    };
    const r={...row(),state:'inactive',key:{...row().key,sceneId:'checkerboard__box__inactive'}};
    const decl={...declaration,scenes:[{id:r.key.sceneId,component:'box',background:'checkerboard',state:'inactive'}],
      split:{calibration:[r.key.sceneId]}};
    const capture=fixture(dir,0);
    capture.metadata=put('inactive-meta.json',{...JSON.parse(readFileSync(capture.metadata.path,'utf8')),sceneId:r.key.sceneId});
    const matrix={matrix:put('matrix.json',{schemaVersion:5,cells:[r]}),documents:capture.documents};
    const inputs={declaration:put('declaration.json',decl),current:[matrix],references:[],
      captures:{[identity(r)]:capture},referenceCaptures:{},python:'/not-used'};
    const context=prepareCurrent(inputs);
    const changed={...capture,native:{path:join(dir,'other-native.png'),sha256:hash(pixels(10))}};
    writeFileSync(changed.native.path,pixels(10));
    assert.throws(()=>evaluate(context,[matrix],{[identity(r)]:changed},context.current),/frozen|native/i);
    const changedBackdrop={...capture,backdrop:changed.native};
    assert.throws(()=>evaluate(context,[matrix],{[identity(r)]:changedBackdrop},context.current),/frozen|backdrop/i);
    const unbound=prepareCurrent({...inputs,captures:{}});
    const result=evaluate(unbound,[matrix],{[identity(r)]:capture},unbound.current);
    assert.equal(result.cells[identity(r)].X1.state,'UNMEASURED');
  } finally {rmSync(dir,{recursive:true});}
});
test('C1 candidate report retains current numeric statistic beside slope arrays',async()=>{
  const {prepareCurrent,evaluate}=await import('./api.ts');
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {
    const put=(name:string,value:any)=>{
      const bytes=Buffer.from(JSON.stringify(value)),path=join(dir,name);
      writeFileSync(path,bytes); return {path,sha256:hash(bytes)};
    };
    const {rows,decl}=shadowBed([96,128,160]);
    const documents={'a.json':'a'.repeat(64),'r.json':'b'.repeat(64)};
    const current={matrix:put('current.json',{schemaVersion:5,cells:rows}),documents};
    const context=prepareCurrent({declaration:put('decl.json',decl),current:[current],references:[],
      captures:{},referenceCaptures:{},python:'/not-used'});
    const changed=structuredClone(rows);
    for(const r of changed) for(const band of r.shadow.affineWeb) band.slopeALinear=.79;
    const candidate={matrix:put('candidate.json',{schemaVersion:5,cells:changed}),documents};
    const result=evaluate(context,[candidate],{},context.current);
    const cell=result.cells[identity(rows[0])].C1;
    assert.equal(cell.currentT,0);
    assert.deepEqual(cell.current,rows[0].shadow.affineWeb);
    assert.ok(Math.abs(Number(cell.T)-.01)<1e-12);
    const aggregate=result.aggregates.C1;
    assert.equal((aggregate.current as any).perBed['0.5/1x dark/96'].T,0);
    assert.equal((aggregate.cells as any[])[0].currentT,0);
  } finally {rmSync(dir,{recursive:true});}
});
test('unadopted coherence still requires actual twin metrics, including inactive rows',async()=>{
  const {prepareCurrent}=await import('./api.ts');
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {
    const put=(name:string,value:any)=>{
      const bytes=Buffer.from(JSON.stringify(value)),path=join(dir,name);
      writeFileSync(path,bytes); return {path,sha256:hash(bytes)};
    };
    const r={...row('css'),state:'inactive',key:{...row('css').key,sceneId:'checkerboard__box__inactive'}};
    const decl={...declaration,scenes:[{id:r.key.sceneId,component:'box',background:'checkerboard',state:'inactive'}],
      split:{calibration:[r.key.sceneId]}};
    const context=prepareCurrent({declaration:put('decl.json',decl),
      current:[{matrix:put('current.json',{schemaVersion:5,cells:[r]}),documents:{'a.json':'a'.repeat(64),'r.json':'b'.repeat(64)}}],
      references:[],captures:{},referenceCaptures:{},python:'/not-used'});
    assert.equal(context.current.cells[identity(r)].coherence.state,'UNMEASURED');
    const css=fixture(dir,0,'css'),gpu=fixture(dir,0);
    const missing:any=row('css'); missing.material={};
    assert.equal(pairedCoherence(C,missing,row(),css,gpu).state,'UNMEASURED');
  } finally {rmSync(dir,{recursive:true});}
});

test('UNMEASURED E2 survives the actual JSON completed-reference transport',async()=>{
  const {prepareCurrent,evaluate}=await import('./api.ts');
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {
    const put=(name:string,bytes:Uint8Array)=>{
      const path=join(dir,name);writeFileSync(path,bytes);return {path,sha256:hash(bytes)};
    };
    const json=(name:string,value:any)=>put(name,Buffer.from(JSON.stringify(value)));
    const r=row(), tiny=PNG.sync.write({width:1,height:1,data:Buffer.from([0,0,0,255])} as PNG);
    const documents={'a.json':'a'.repeat(64),'r.json':'b'.repeat(64)};
    const capture:Capture={web:put('web.png',tiny),native:put('native.png',tiny),
      backdrop:put('backdrop.png',tiny),documents,
      metadata:json('meta.json',{engine:'chromium',engineVersion:'synthetic',renderer:'webgpu',
        samplingBackend:'gpu-texture',gpuAdapter:'synthetic',colorSpace:'srgb',
        sceneId:r.key.sceneId,pixelSize:[1,1],capturePath:descriptor,deterministic:true,repeatNoise:0})};
    const matrix={matrix:json('matrix.json',{schemaVersion:5,cells:[r]}),documents};
    const captures={[identity(r)]:capture};
    const context=prepareCurrent({declaration:json('decl.json',{...declaration,
      canvas:{width:1,height:1},components:{box:{kind:'rrect',size:[1,1],radius:0}}}),
      current:[matrix],references:[],captures,referenceCaptures:{},python:'/Users/new/vitrea-w49/py/bin/python'});
    assert.equal(context.current.cells[identity(r)].E2.state,'UNMEASURED');
    const transported=JSON.parse(JSON.stringify(context.current));
    const result=evaluate(context,[matrix],captures,transported);
    assert.equal(result.cells[identity(r)].E2.state,'UNMEASURED');
    assert.equal(Object.hasOwn(result.cells[identity(r)].E2,'reference'),false);
    assert.deepEqual(result,JSON.parse(JSON.stringify(result)));
  } finally {rmSync(dir,{recursive:true});}
});
test('coherence owner presence metadata does not promote optional diagnostics',async()=>{
  const {prepareCurrent}=await import('./api.ts');
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {
    const put=(name:string,value:any)=>{
      const bytes=Buffer.from(JSON.stringify(value)),path=join(dir,name);
      writeFileSync(path,bytes);return {path,sha256:hash(bytes)};
    };
    const r=row('css');
    const context=prepareCurrent({declaration:put('decl.json',declaration),
      current:[{matrix:put('matrix.json',{schemaVersion:5,cells:[r]}),
        documents:{'a.json':'a'.repeat(64),'r.json':'b'.repeat(64)}}],
      references:[],captures:{},referenceCaptures:{},python:'/not-used'});
    const evidence=context.current.cells[identity(r)].coherence;
    assert.equal(evidence.state,'UNMEASURED');
    assert.equal(evidence.sourceOwnerPresenceRequired,false);
    assert.equal(evidence.diagnosticOnly,true);
  } finally {rmSync(dir,{recursive:true});}
});
