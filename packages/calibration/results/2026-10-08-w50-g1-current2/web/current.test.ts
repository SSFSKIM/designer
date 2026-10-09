import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { buildCurrent } from './current.ts';
import { readCandidateDocument } from '../../../scripts/candidate-document.ts';

for (const position of [0.25,0.5]) {
  test(`complete current-material candidate at ${position} passes production parser`,()=>{
    const root=mkdtempSync(join(tmpdir(),'w50-current-docs-'));
    try {
      const pin=buildCurrent(position,join(root,'new'));
      const candidate=readCandidateDocument(pin.path);
      assert.equal(candidate.document.glassTintAmount,position);
      const witness=JSON.parse(readFileSync(join(root,'new/current-sources.json'),'utf8'));
      for (const [slot,endpoint] of Object.entries(candidate.endpoints)) {
        const source=JSON.parse(readFileSync(witness.endpoints[slot].source.path,'utf8'));
        const derived=JSON.parse(readFileSync(endpoint.path,'utf8'));
        assert.deepEqual(derived,{...source,profileKey:source.profileKey.replace(`glass${position}`,`glass${position.toFixed(3)}`)});
        assert.equal(endpoint.resolvedMaterialSha256,source.resolvedMaterialSha256);
        assert.notEqual(endpoint.profileKey,source.profileKey);
      }
    } finally {rmSync(root,{recursive:true,force:true});}
  });
}
