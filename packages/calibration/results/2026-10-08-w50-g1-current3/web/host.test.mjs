import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {admitHost,installHost,SCENES} from './host.mjs';
const htmlPath=fileURLToPath(new URL('../../../web/index.html',import.meta.url));
const html=readFileSync(htmlPath,'utf8');

test('newbed host adds one renderer-independent border-box rule to real production HTML',()=>{
  admitHost(SCENES);
  const result=installHost(html,{filename:htmlPath},SCENES);
  assert.equal(result.length,1);
  assert.equal(result[0].tag,'style');
  assert.equal(result[0].injectTo,'head');
  assert.equal(result[0].children,'.glass-host { box-sizing: border-box; }');
  assert.equal(html,readFileSync(htmlPath,'utf8'));
});

test('newbed host refuses canonical, copied, missing or altered scene identity',()=>{
  const root=mkdtempSync(join(tmpdir(),'w50-host-'));
  try {
    const copy=join(root,'copy.json');writeFileSync(copy,readFileSync(SCENES));
    for(const scenes of [undefined,copy,fileURLToPath(new URL('../../../../../apps/reference-apple/scenes.json',import.meta.url))])
      assert.throws(()=>admitHost(scenes),/W50|scene/);
    assert.throws(()=>installHost(html,{filename:copy},SCENES),/HTML/);
    assert.throws(()=>installHost('<html></html>',{filename:htmlPath},SCENES),/stage/);
  } finally {rmSync(root,{recursive:true,force:true});}
});
