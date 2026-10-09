import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,rmSync} from 'node:fs';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {retainPair} from './pair.ts';

test('retains distinct first/second bytes and page reports without coercing determinism',async()=>{
 const dir=mkdtempSync(join(tmpdir(),'w50-pair-'));
 try {
  const first={png:Buffer.from('first synthetic PNG bytes'),report:{sceneId:'synthetic',value:1}};
  const second={png:Buffer.from('second synthetic PNG bytes'),report:{sceneId:'synthetic',value:2}};
  const pair=await retainPair(dir,'synthetic','css',first,second,false,.000001);
  assert.equal(pair.reading,'first');assert.equal(pair.deterministic,false);assert.equal(pair.repeatNoise,.000001);
  assert.deepEqual(readFileSync(pair.first.image.path),first.png);
  assert.deepEqual(readFileSync(pair.second.image.path),second.png);
  assert.deepEqual(JSON.parse(readFileSync(pair.second.report.path,'utf8')),second.report);
  assert.notEqual(pair.first.image.sha256,pair.second.image.sha256);
  await assert.rejects(retainPair(dir,'synthetic','css',first,second,false,.000001));
 }finally{rmSync(dir,{recursive:true,force:true});}
});
