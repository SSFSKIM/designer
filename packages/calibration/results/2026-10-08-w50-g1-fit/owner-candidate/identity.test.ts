import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, rmSync, readFileSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } from '@vitrea/renderer-webgpu';
import { cssTierMappingSha256, resolvedDigest, readCandidateDocument } from '../../../scripts/candidate-document.ts';
import { candidateMaterialLabel } from '../../../src/material-selection.ts';
import { documentRoles, assertDocumentPair } from '../owner/referee.ts';
import { createIdentityResolver } from './identity.ts';

const home=dirname(fileURLToPath(import.meta.url));
export const hash=(bytes:string|Uint8Array)=>createHash('sha256').update(bytes).digest('hex');
export function put(dir:string,name:string,value:any) {
  const bytes=Buffer.isBuffer(value)?value:Buffer.from(JSON.stringify(value));
  const path=join(dir,name);writeFileSync(path,bytes);return {path,sha256:hash(bytes)};
}
export function candidateFixture(dir:string,position=.25,name='synthetic') {
  const patch={sizeSpanMin:DEFAULT_MATERIAL_PROFILE.sizeSpanMin};
  const digest=resolvedDigest(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE,patch));
  const mapping={blurSigmaScale:1};
  const endpoints=Object.fromEntries(['active','receded'].flatMap(pose=>['light','dark'].map(scheme=>{
    const endpoint=put(dir,`${name}-${pose}-${scheme}.json`,{
      profileKey:`apple-macos-27.0-2x-${scheme}-standard-glass${position}${pose==='receded'?'-receded':''}`,
      ...(pose==='receded'?{kind:'receded-endpoint'}:{cssTierMapping:mapping}),
      patch,resolvedMaterialSha256:digest,
    });
    return [`${pose}.${scheme}`,endpoint];
  })));
  const pin=put(dir,`${name}.json`,{kind:'vitrea-candidate-material-document',schemaVersion:1,
    name,platform:'macOS 27.0',glassTintAmount:position,endpoints,
    cssTierMappingSha256:cssTierMappingSha256(mapping)});
  const candidate=readCandidateDocument(pin.path);
  const relativePath=relative(resolve(home,'../../../../..'),pin.path);
  const shown=relativePath.startsWith('..')?pin.path:relativePath;
  const label=candidateMaterialLabel({declaration:shown,sha256:pin.sha256.slice(0,12),
    name,glassTintAmount:position});
  const row={key:{profileKey:`apple-macos-27.0-1x-dark-standard-glass${position}`,
    sceneId:'checkerboard__box__rest',web:{renderer:'webgpu',samplingBackend:'gpu-texture',
      capturePath:`viewport=4x4, deviceScaleFactor=1, ${label}`}},
    tier:'texture',fixtureSet:'calibration',state:'rest',material:{interiorMeanWeb:{value:.2}}};
  return {pin,candidate,label,row,endpoints,shown};
}
const resolver=(pins:any[])=>createIdentityResolver(pins,{documentRoles,assertDocumentPair});
test('real production candidate stamps retain raw bytes and derive full actual endpoints',()=>{
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {
    const f=candidateFixture(dir), r=resolver([f.pin]), original=JSON.stringify(f.row);
    const resolved=r.resolve(f.row)!;
    assert.equal(resolved.declaration.sha256,f.pin.sha256);
    assert.deepEqual(r.documents(f.row),Object.fromEntries(['active.dark','receded.dark'].map(slot=>{
      const e=f.endpoints[slot];return [e.path,e.sha256];
    })));
    r.assertDocumentPair(f.row,f.endpoints['active.dark'].sha256,f.endpoints['receded.dark'].sha256);
    assert.equal(JSON.stringify(f.row),original);
    assert.throws(()=>r.assertDocumentPair(f.row,f.endpoints['receded.dark'].sha256,
      f.endpoints['active.dark'].sha256),/pair|role/);
  } finally {rmSync(dir,{recursive:true});}
});
test('unregistered, changed, cross-position, ambiguous and fabricated role stamps refuse',()=>{
  const dir=mkdtempSync(join(home,'.synthetic-'));
  try {
    const f=candidateFixture(dir),r=resolver([f.pin]);
    const alter=(path:string)=>({...f.row,key:{...f.row.key,web:{...f.row.key.web,capturePath:path}}});
    for(const path of [f.row.key.web.capturePath.replace(f.pin.sha256.slice(0,12),'a'.repeat(12)),
      f.row.key.web.capturePath.replace(f.shown,f.shown+'other'),
      f.row.key.web.capturePath.replace(f.shown,f.pin.path),
      f.row.key.web.capturePath.replace('name=synthetic','name=other'),
      f.row.key.web.capturePath+', crossPosition=candidate-glass0.25-against-glass0.5',
      f.row.key.web.capturePath+' recededProfile=fake sha256:aaaaaaaaaaaa',
      f.row.key.web.capturePath+' '+f.label]) assert.throws(()=>r.resolve(alter(path)));
    assert.throws(()=>r.resolve({...f.row,key:{...f.row.key,profileKey:f.row.key.profileKey.replace('0.25','0.5')}}));
    assert.throws(()=>resolver([{...f.pin,sha256:f.pin.sha256.slice(0,12)}]),/hash|SHA|pin/i);
    assert.throws(()=>resolver([f.pin,candidateFixture(dir,.25,'other').pin]),/position|cohort/i);
    assert.throws(()=>resolver([]).resolve(f.row),/registered|declaration/i);
    writeFileSync(f.pin.path,readFileSync(f.pin.path,'utf8')+' ');
    assert.throws(()=>r.resolve(f.row),/hash/i);
  } finally {rmSync(dir,{recursive:true});}
});
test('legacy role parser stays role-sensitive and unchanged',()=>{
  const row={key:{web:{capturePath:'materialProfile=a sha256:aaaaaaaaaaaa recededProfile=r sha256:bbbbbbbbbbbb'}}};
  const r=resolver([]);
  assert.equal(r.resolve(row),undefined);
  assert.deepEqual(r.roles(row),documentRoles(row));
  assert.throws(()=>r.assertDocumentPair(row,'b'.repeat(64),'a'.repeat(64)),/pair|role/);
  assert.throws(()=>r.roles({key:{web:{capturePath:'materialProfile=candidate'}}}));
});
