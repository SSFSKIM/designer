import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { assertedNumbers } from './source.ts';
test('inline owner assertion bounds are read structurally and ambiguity refuses',()=>{
  const source='expect(CUT.absoluteBound).toBe(0.055);';
  const hash=(s:string)=>createHash('sha256').update(s).digest('hex');
  assert.deepEqual(assertedNumbers(source,hash(source),['CUT.absoluteBound']),{'CUT.absoluteBound':.055});
  assert.throws(()=>assertedNumbers(source+source,hash(source+source),['CUT.absoluteBound']),/ambiguous/);
});
