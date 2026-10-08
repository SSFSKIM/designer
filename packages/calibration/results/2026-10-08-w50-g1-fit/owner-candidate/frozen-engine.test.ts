import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { PNG } from 'pngjs';
import { createCandidateEngine } from './frozen-engine.ts';
import { candidateFixture, put, hash } from './identity.test.ts';
import { bindSource } from '../owner/source.ts';
import * as legacy from '../owner/referee.ts';

const home=dirname(fileURLToPath(import.meta.url));
const root=resolve(home,'../../../../..');
const prefix='packages/calibration/results/2026-10-08-w50-g1-fit/owner/';
// Caller-confirmed source-closure metadata, not self-selected live file hashes.
const hashes={
  'api.ts':'a80a4caea17002b88b5de44b5ac9abf7a88f9d90328041a2e8afde304b6b7a1a',
  'referee.ts':'9ea8e26d8e49ee083de96d27e38135dce9a368aff0c4ab4ff349193779c32ba1',
  'intrinsic.ts':'052a18daa895311275196dfb72d109bc8b7fe3776a1b15b8953235e649ce13e7',
  'source.ts':'1aea30da0199b81d1c05e5c80ea377cfb257f8bd99774c5272d35612d5b2f51e',
};
const sourcePins=Object.fromEntries(Object.entries(hashes).map(([name,sha256])=>
  [prefix+name,{path:resolve(root,prefix+name),sha256}]));
const make=(declarations:any[]=[])=>createCandidateEngine({sourcePins,declarations});
function fixture(dir:string,row:any,documents:Record<string,string>,level=0) {
  const image=PNG.sync.write({width:4,height:4,data:Buffer.from(Array.from({length:64},(_,i)=>i%4===3?255:level))} as PNG);
  const name=row.key.web.renderer+level;
  return {web:put(dir,`web-${name}.png`,image),native:put(dir,'native.png',image),
    backdrop:put(dir,'backdrop.png',image),metadata:put(dir,`meta-${name}.json`,{
      capturePath:row.key.web.capturePath,sceneId:row.key.sceneId,renderer:row.key.web.renderer,
      samplingBackend:row.key.web.samplingBackend,pixelSize:[4,4]}),documents};
}
test('exported AST declarations bind explicitly and unresolved runtime dependencies refuse',()=>{
  const text='export function calculate(n:number) { return helper(n); }';
  assert.throws(()=>bindSource(text,hash(text),['calculate'],{exports:{}}),/Unbound.*helper/);
  assert.equal(bindSource(text,hash(text),['calculate'],{exports:{},helper:(n:number)=>n+1}).calculate(2),3);
  assert.throws(()=>bindSource(text+' ',hash(text),['calculate'],{exports:{},helper:()=>0}),/hash/);
});
test('factory refuses missing and mutated external source authority before evaluation',()=>{
  assert.throws(()=>createCandidateEngine({sourcePins:{},declarations:[]}),/pin|source/i);
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {
    const key=prefix+'api.ts',path=join(dir,'changed-api.ts');
    writeFileSync(path,readFileSync(sourcePins[key]!.path,'utf8')+' ');
    assert.throws(()=>createCandidateEngine({sourcePins:{...sourcePins,[key]:{...sourcePins[key]!,path}},declarations:[]}),/hash/i);
  } finally {rmSync(dir,{recursive:true});}
});
test('candidate PNG kernel binds untouched metadata, full endpoints and declared raster',()=>{
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {
    const f=candidateFixture(dir),engine=make([f.pin]);
    const capture=fixture(dir,f.row,engine.identityResolver.documents(f.row));
    const original=JSON.stringify(f.row),decl={canvas:{width:4,height:4}};
    assert.equal(engine.captureBytes(f.row,capture,decl).web.length,readFileSync(capture.web.path).length);
    assert.equal(JSON.stringify(f.row),original);
    for(const field of ['sceneId','renderer','samplingBackend','capturePath','pixelSize']) {
      const metadata=JSON.parse(readFileSync(capture.metadata.path,'utf8'));
      metadata[field]=field==='pixelSize'?[8,8]:'wrong';
      assert.throws(()=>engine.captureBytes(f.row,{...capture,metadata:put(dir,'wrong.json',metadata)},decl));
    }
    const badDocs={...capture.documents};const path=Object.keys(badDocs)[0]!;
    badDocs[path]=badDocs[path]!.slice(0,12)+'0'.repeat(52);
    assert.throws(()=>engine.captureBytes(f.row,{...capture,documents:badDocs},decl),/pair|document/);
    assert.throws(()=>engine.captureBytes(f.row,capture,{canvas:{width:8,height:4}}),/canvas|size/);
    assert.throws(()=>engine.captureBytes(f.row,{...capture,web:{...capture.web,sha256:'a'.repeat(64)}},decl),/hash/);
  } finally {rmSync(dir,{recursive:true});}
});
test('rowsOf preserves raw candidate labels and requires full endpoint sidecars',()=>{
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {
    const f=candidateFixture(dir),engine=make([f.pin]);
    const input={matrix:put(dir,'matrix.json',{schemaVersion:5,cells:[f.row]}),documents:engine.identityResolver.documents(f.row)};
    assert.deepEqual(engine.rowsOf([input]),[f.row]);
    const bad={...input.documents};const key=Object.keys(bad)[0]!;bad[key]=bad[key]!.slice(0,12)+'0'.repeat(52);
    assert.throws(()=>engine.rowsOf([{...input,documents:bad}]),/document|pair/);
    assert.throws(()=>engine.rowsOf([input,input]),/Multiple/);
  } finally {rmSync(dir,{recursive:true});}
});
test('paired coherence reuses frozen arithmetic with candidate identity and rejects mixed cohorts',()=>{
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {
    const f=candidateFixture(dir),engine=make([f.pin]),C=engine.loadContracts();
    const css={...f.row,tier:'dom',key:{...f.row.key,web:{...f.row.key.web,renderer:'css',samplingBackend:'css-backdrop'}}};
    const docs=engine.identityResolver.documents(f.row),gpuCapture=fixture(dir,f.row,docs),cssCapture=fixture(dir,css,docs);
    const result=engine.pairedCoherence(C,css,f.row,cssCapture,gpuCapture);
    assert.equal(result.state,'MEASURED');assert.equal(result.deltaE,0);assert.equal(result.ratio,1);
    const other=candidateFixture(dir,.25,'another');
    assert.throws(()=>engine.pairedCoherence(C,css,other.row,cssCapture,gpuCapture),/registered|declaration|descriptor/);
    assert.equal(engine.pairedCoherence(C,css,undefined).state,'UNMEASURED');
  } finally {rmSync(dir,{recursive:true});}
});
test('legacy pixels and classification retain the original frozen verdicts',()=>{
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {
    const f=candidateFixture(dir),engine=make();
    const row={...f.row,key:{...f.row.key,web:{...f.row.key.web,capturePath:'materialProfile=a sha256:aaaaaaaaaaaa recededProfile=r sha256:bbbbbbbbbbbb'}}};
    const capture=fixture(dir,row,{a:'a'.repeat(64),r:'b'.repeat(64)});
    assert.doesNotThrow(()=>legacy.validateCapture(row,capture));
    assert.doesNotThrow(()=>engine.validateCapture(row,capture));
    assert.deepEqual(engine.classifyCell(engine.loadContracts(),row),legacy.classifyCell(legacy.loadContracts(),row));
  } finally {rmSync(dir,{recursive:true});}
});
test('candidate intrinsic function accepts registered full declarations and rejects role/position changes',()=>{
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {
    const a=candidateFixture(dir,.25,'quarter'),b=candidateFixture(dir,.5,'half');
    const engine=make([a.pin,b.pin]);
    const input={candidateDeclarations:[a.pin,b.pin],recededRecords:{}};
    const result=engine.candidateIntrinsics(input,[a.row,b.row],[]);
    assert.equal(Object.keys(result.X75).length,12);
    assert.equal(result.X76['0.25'].state,'UNMEASURED');
    assert.throws(()=>engine.candidateIntrinsics({...input,candidateDeclarations:[a.pin,{...b.pin,sha256:'a'.repeat(64)}]},[a.row,b.row]),/hash/);
    const doc=JSON.parse(readFileSync(a.endpoints['receded.dark'].path,'utf8'));
    assert.doesNotThrow(()=>engine.assertEndpointIdentity(doc,.25,'receded'));
    assert.throws(()=>engine.assertEndpointIdentity(doc,.25,'active'),/identity|pose/);
    assert.throws(()=>engine.assertEndpointIdentity({...doc,patch:{sizeSpanMin:999}},.25,'receded'),/identity|pose/);
  } finally {rmSync(dir,{recursive:true});}
});

test('evaluateRows reproduces frozen owner report on the exact synthetic union without row relabelling',async()=>{
  const {prepareCurrent,evaluate}=await import('../owner/api.ts');
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {
    const f=candidateFixture(dir,.5),engine=make([f.pin]),C=engine.loadContracts();
    const scene='dark-solid__box__rest';
    const row={...f.row,fixtureSet:'validation',key:{...f.row.key,sceneId:scene},
      material:{interiorMeanNative:{value:.2},interiorMeanWeb:{value:.22}}};
    const declared={canvas:{width:4,height:4},components:{box:{kind:'rrect',size:[2,2]}},
      scenes:[{id:scene,component:'box',background:'dark-solid',state:'rest'}],split:{validation:[scene]}};
    const matrix=(name:string,active:string,receded:string,mean:number)=>{
      const r={...row,key:{...row.key,web:{...row.key.web,capturePath:
        `materialProfile=a sha256:${active.slice(0,12)} recededProfile=r sha256:${receded.slice(0,12)}`}},
        material:{interiorMeanNative:{value:.2},interiorMeanWeb:{value:mean}}};
      return {matrix:put(dir,name,{schemaVersion:5,cells:[r]}),documents:{a:active,r:receded}};
    };
    const baseline=C.BASELINE.dark;
    const context=prepareCurrent({declaration:put(dir,'scenes.json',declared),
      current:[matrix('current.json','c'.repeat(64),'d'.repeat(64),.21)],
      references:[matrix('reference.json',baseline.active.padEnd(64,'0'),baseline.receded.padEnd(64,'0'),.2)],
      captures:{},referenceCaptures:{},python:'/not-used'});
    const before=JSON.stringify(row);
    const original=evaluate(context,[matrix('legacy-candidate.json','e'.repeat(64),'f'.repeat(64),.22)],{},context.current);
    const candidate=engine.evaluateRows(context,[row],{});
    // evaluate() replaces the intrinsic placeholder after evaluateRows(); these reports
    // compare every pixel/statistic axis and provenance, not that wrapper-only message.
    const {intrinsic:originalIntrinsic,...originalAxes}=original;
    const {intrinsic:candidateIntrinsic,...candidateAxes}=candidate;
    assert.equal((originalIntrinsic as any).X75.state,'UNMEASURED');
    assert.equal((candidateIntrinsic as any).X75.state,'UNMEASURED');
    assert.deepEqual(candidateAxes,originalAxes);
    assert.equal(candidate.cells[legacy.identity(row)].L1.reference,.2);
    assert.equal(candidate.cells[legacy.identity(row)].L1.current,.21);
    assert.equal(candidate.cells[legacy.identity(row)].L1.candidate,.22);
    assert.equal(JSON.stringify(row),before);
    assert.deepEqual(engine.evaluateRows(context,context.currentRows,{},false),context.current);
    assert.throws(()=>engine.evaluateRows(context,[{...row,key:{...row.key,sceneId:'unexpected'}}],{}),/Unexpected/);
  } finally {rmSync(dir,{recursive:true});}
});

test('candidate X1 recount keeps both frozen pixel masks',()=>{
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {
    const f=candidateFixture(dir),engine=make([f.pin]),C=engine.loadContracts();
    const row={...f.row,key:{...f.row.key,web:{...f.row.key.web,
      capturePath:f.row.key.web.capturePath.replace('4x4','24x24')}}};
    const docs=engine.identityResolver.documents(row),capture=fixture(dir,row,docs);
    const png=(level:number)=>PNG.sync.write({width:24,height:24,
      data:Buffer.from(Array.from({length:24*24*4},(_,i)=>i%4===3?255:level))} as PNG);
    capture.web=put(dir,'24-web.png',png(1));capture.native=put(dir,'24-native.png',png(0));
    capture.backdrop=put(dir,'24-backdrop.png',png(0));
    capture.metadata=put(dir,'24-meta.json',{capturePath:row.key.web.capturePath,
      sceneId:row.key.sceneId,renderer:'webgpu',samplingBackend:'gpu-texture',pixelSize:[24,24]});
    const decl={canvas:{width:24,height:24},components:{box:{kind:'rrect',size:[8,8]}},
      scenes:[{id:row.key.sceneId,component:'box',background:'checkerboard',state:'rest'}],
      split:{calibration:[row.key.sceneId]}};
    const result=engine.recountBlack(C,row,capture,decl);
    assert.equal(result.state,'MEASURED');assert.equal(result.verdict,'failure');
    assert.ok(result.readings.analytic.aboveZero>0);assert.equal(result.readings.analytic.aboveOne,0);
    assert.ok(result.readings.integer.aboveZero>0);
  } finally {rmSync(dir,{recursive:true});}
});
