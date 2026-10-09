import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { loadContracts, classifyCell, readMatrix, checkInheritance, checkOpacity } from './referee.ts';
const C = loadContracts();
const row = (scene = 'photo__rrect-sm__rest', position = '0.25') => ({
  key: { profileKey: `apple-macos-27.0-1x-dark-standard-glass${position}`, sceneId: scene,
    web: { renderer: 'webgpu', capturePath: 'candidate' } },
  tier: 'texture', fixtureSet: 'validation', state: 'rest',
  material: Object.fromEntries(Object.entries({chromaStructureRatioNative: 1,
    chromaStructureRatioWeb: 1, interiorStdDevNative: .2, interiorStdDevWeb: .1,
    interiorMeanNative: .2, interiorMeanWeb: .21}).map(([k,value]) => [k,{value}])),
});
test('M2 keeps directional named misses but refuses away and overshoot', () => {
  const current = row(), baseline = row();
  baseline.material.interiorStdDevWeb.value = .1;
  current.material.interiorStdDevWeb.value = .15;
  assert.equal(classifyCell(C, current, baseline).M2.verdict, 'named-miss');
  current.material.interiorStdDevWeb.value = .05;
  assert.equal(classifyCell(C, current, baseline).M2.verdict, 'failure');
  current.material.interiorStdDevWeb.value = .21;
  assert.equal(classifyCell(C, current, baseline).M2.verdict, 'failure');
});
test('L1 missing fixed baseline is unmeasured, never a no-change reference', () => {
  assert.equal(classifyCell(C, row(), undefined).L1.state, 'UNMEASURED');
});
test('M1 absolute misses cannot silently become named', () => {
  const c = row(); c.material.chromaStructureRatioWeb.value = 2;
  assert.equal(classifyCell(C, c, row()).M1.verdict, 'failure');
});
test('matrix bytes and schema are checked before any rows become evidence', () => {
  const raw = Buffer.from(JSON.stringify({schemaVersion: 5, cells: [row()]}));
  const sha256 = createHash('sha256').update(raw).digest('hex');
  assert.equal(readMatrix(raw, sha256).length, 1);
  assert.throws(() => readMatrix(Buffer.concat([raw,Buffer.from(' ')]),sha256), /hash/);
});
test('X76 refuses silently inherited active-fitted leaves and allows explicit held reading', () => {
  const input = { activeResolved: {tone: 3}, activePatch: {tone: 3},
    activeEntries: {tone: {status: 'measured'}}, beforePatch: {}, beforeEntries: {},
    candidatePatch: {}, methods: {} };
  assert.deepEqual(checkInheritance(input).missing, ['tone']);
  input.methods = {tone: {held: ['native reading is held at this candidate']}};
  assert.deepEqual(checkInheritance(input).missing, []);
});
test('X75 uses both tiers and both scale branches across the full integer span domain', () => {
  const result = checkOpacity({synthetic:{optics:{regular:{tintAlpha:.8}},
    tintAlphaFar1x:.2,tintAlphaFar2x:.2,tintAlphaSpanMax:160,tintAlphaSpanMax2x:192}}).synthetic;
  assert.equal(result.verdict,'failure');
  assert.deepEqual(new Set(result.violations.map((v:any)=>v.tier)),new Set(['webgpu','css']));
  assert.deepEqual(new Set(result.violations.map((v:any)=>v.dpr)),new Set([1,2]));
  assert.ok(result.violations.some((v:any)=>v.span===1024));
});

test('M2 keeps original ruled failure membership without calling it directional success', () => {
  const r=row('photo__rrect-sm__inactive');
  r.key.profileKey='apple-macos-27.0-2x-light-standard-glass0.25'; r.state='inactive';
  const base=structuredClone(r); r.material.interiorStdDevWeb.value=.05;
  const e=classifyCell(C,r,base).M2;
  assert.equal(e.verdict,'named-miss');
  assert.equal(e.structureVerdict,'failure');
  assert.equal(e.originalOwnerNamedListMember,true);
  assert.equal(e.originalOwnerRuledFailure,true);
  assert.equal(e.wouldRequireNewOwnerRecord,false);
});
test('M2 distinguishes a new directional record from an existing owner record', () => {
  const r=row('photo__synthetic__rest'), base=structuredClone(r);
  r.material.interiorStdDevWeb.value=.15;
  const fresh=classifyCell(C,r,base).M2;
  assert.equal(fresh.structureVerdict,'named');
  assert.equal(fresh.originalOwnerNamedListMember,false);
  assert.equal(fresh.wouldRequireNewOwnerRecord,true);
  r.key.sceneId='photo__rrect-md__rest'; r.fixtureSet='calibration';
  const existing=classifyCell(C,r,base).M2;
  assert.equal(existing.originalOwnerNamedListMember,true);
  assert.equal(existing.originalOwnerRuledFailure,false);
  assert.equal(existing.wouldRequireNewOwnerRecord,false);
});

test('L1 named absent means do not excuse a missing original reference',()=>{
  const r=row('dark-solid__rrect-md__inactive','0.5'); r.state='inactive';
  const base=structuredClone(r);
  (r.material as any).interiorMeanNative={value:null};
  (base.material as any).interiorMeanNative={value:null};
  assert.equal(classifyCell(C,r,base).L1.namedExclusion,true);
  assert.equal(classifyCell(C,r).L1.namedExclusion,false);
  const mismatched=structuredClone(base); mismatched.material.interiorMeanNative.value=.2;
  assert.equal(classifyCell(C,r,mismatched).L1.namedExclusion,false);
});
test('L1 reads an absent mean as the owner test does: null, so the named exclusion holds',()=>{
  // The macOS 27 generations omit both means on the named dark inactive dark-solid cells.
  const absent=(scene:string,position:string)=>{
    const r=row(scene,position); r.state='inactive';
    delete (r.material as any).interiorMeanNative; delete (r.material as any).interiorMeanWeb;
    return r;
  };
  for(const position of ['0.25','0.5']) {
    const r=absent('dark-solid__capsule-button__inactive',position), base=structuredClone(r);
    const L1=classifyCell(C,r,base).L1;
    assert.equal(L1.state,'UNMEASURED');
    assert.equal(L1.namedExclusion,true);
    assert.equal(classifyCell(C,r).L1.namedExclusion,false);
    const nulled=structuredClone(base);
    (nulled.material as any).interiorMeanNative={value:null};
    (nulled.material as any).interiorMeanWeb={value:null};
    assert.equal(classifyCell(C,r,nulled).L1.namedExclusion,true);
    const measured=structuredClone(base); (measured.material as any).interiorMeanNative={value:.2};
    assert.equal(classifyCell(C,r,measured).L1.namedExclusion,false);
  }
  const unnamed=absent('dark-solid__rrect-lg__inactive','0.5');
  assert.equal(classifyCell(C,unnamed,structuredClone(unnamed)).L1.namedExclusion,false);
  const nullEntry=absent('dark-solid__rrect-md__inactive','0.5');
  (nullEntry.material as any).interiorMeanWeb=null;
  assert.throws(()=>classifyCell(C,nullEntry,structuredClone(nullEntry)),TypeError);
});

import * as referee from './referee.ts';
test('coherence source presence follows exact profiles and gated-bed exclusions',()=>{
  const r:any=row(); r.key.web.renderer='css';r.tier='dom';
  const decl={scenes:[{id:r.key.sceneId,state:'rest'}],split:{recorded:[]}};
  const scope=()=>referee.coherenceOwnerScope(C,r,decl);
  assert.equal(scope().sourceOwnerPresenceRequired,false);
  assert.equal(scope().diagnosticOnly,true);
  r.key.profileKey='apple-macos-26.5-1x-light-standard';
  assert.equal(scope().sourceOwnerPresenceRequired,true);
  assert.equal(scope().sourceOwnerNumericWindowAdopted,true);
  r.key.profileKey='apple-macos-26.5-1x-light-reduced-transparency';
  assert.equal(scope().sourceOwnerPresenceRequired,true);
  assert.equal(scope().sourceOwnerNumericWindowAdopted,false);
  for(const fixtureSet of ['probe','recorded']) {
    r.fixtureSet=fixtureSet;
    assert.equal(scope().sourceOwnerPresenceRequired,false);
    assert.equal(scope().diagnosticOnly,true);
  }
  r.fixtureSet='validation';r.state='inactive';
  assert.equal(scope().sourceOwnerPresenceRequired,false);
  r.state='rest';decl.scenes[0]!.state='inactive';
  assert.equal(scope().sourceOwnerPresenceRequired,false);
  decl.scenes[0]!.state='rest';(decl.split.recorded as string[]).push(r.key.sceneId);
  assert.equal(scope().sourceOwnerPresenceRequired,false);
});
