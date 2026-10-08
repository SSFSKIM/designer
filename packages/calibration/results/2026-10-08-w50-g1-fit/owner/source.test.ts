import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { bindSource } from './source.ts';
const hash = (s: string) => createHash('sha256').update(s).digest('hex');
test('source changes and omitted dependencies refuse before evaluation', () => {
  const text = 'const bound = 2; const judge = (n: number) => n <= bound;';
  assert.throws(() => bindSource(text + ' ', hash(text), ['bound', 'judge']), /hash/);
  assert.throws(() => bindSource(text, hash(text), ['judge']), /bound/);
  const api = bindSource(text, hash(text), ['bound', 'judge']);
  assert.equal(api.judge(2), true);
  assert.equal(api.judge(3), false);
});
test('only requested declarations execute, never source-level reads or test registration', () => {
  const text = 'throw new Error("forbidden"); const limit = 3; describe("scope", () => { const local = (n: number) => n + limit; it("forbidden", () => { throw 1; }); });';
  const api = bindSource(text, hash(text), ['limit', 'scope/local']);
  assert.equal(api.local(2), 5);
});

test('explicit test-local source declarations bind without executing the test',()=>{
  const text='const profiles = ["existing"]; describe("owner", () => { it("presence", () => { throw new Error("never execute"); const required = [...profiles, "another"]; }); });';
  const api=bindSource(text,hash(text),['profiles','owner/it:presence/required']);
  assert.deepEqual(api.required,['existing','another']);
});
