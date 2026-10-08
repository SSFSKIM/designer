import test from 'node:test';
import assert from 'node:assert/strict';
import { executeRequest } from './bridge.ts';
test('bridge refuses raw contexts and numeric reference maps',()=>{
  assert.throws(()=>executeRequest({mode:'evaluate',context:{current:{verdict:'PASS'}},
    completedReferences:{cells:{}}}),/pin/i);
});
test('bridge refuses unknown mode without opening any data',()=>{
  assert.throws(()=>executeRequest({mode:'publish'}),/mode/);
});
test('bridge exposes a JSON-native source contract snapshot without evidence inputs',()=>{
  const result=executeRequest({mode:'contracts',python:'/Users/new/vitrea-w49/py/bin/python'});
  if(!('schema' in result)||result.schema!=='w50-owner-contracts-1') assert.fail('Wrong bridge schema');
  assert.deepEqual(JSON.parse(JSON.stringify(result)),result);
  assert.equal(result.intrinsic.X75.referenceReading,'NOT_APPLICABLE');
});
