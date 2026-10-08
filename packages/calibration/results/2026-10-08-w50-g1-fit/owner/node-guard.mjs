// The shared guard enforces imported modules. This additional guard admits source bytes
// consumed by AST readers, which do not pass through an import hook, and TS boundaries.
import fs from 'node:fs';
import promises from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {syncBuiltinESMExports} from 'node:module';
import {dirname,relative,resolve,isAbsolute,basename} from 'node:path';
import {fileURLToPath} from 'node:url';
const originalRead=fs.readFileSync, rawOpen=fs.openSync, rawClose=fs.closeSync;
const rawRealpath=fs.realpathSync, rawExists=fs.existsSync;
function rawRead(path) {
  const fd=rawOpen(path,'r');
  try{return originalRead(fd);}finally{rawClose(fd);}
}
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const root=rawRealpath(process.env.W50_WEB_ROOT);
const raw=rawRead(process.env.W50_WEB_CLOSURE);
if(hash(raw)!==process.env.W50_WEB_CLOSURE_SHA256)throw Error('Changed owner source closure');
const pins=new Map(JSON.parse(raw).sources.map(pin=>[pin.path,pin.sha256]));
function check(path) {
  const physical=rawRealpath(path),rel=relative(root,physical);
  if(rel.startsWith('..')||isAbsolute(rel)||pins.get(rel)!==hash(rawRead(physical)))
    throw Error(`Unsealed or changed owner source: ${physical}`);
  return physical;
}
function admit(path) {
  if(typeof path!=='string'&&!(path instanceof URL)&&!Buffer.isBuffer(path))return;
  const requested=path instanceof URL?fileURLToPath(path):path;
  if(!rawExists(requested))return; // A new data/cache output is not an imported source.
  const physical=rawRealpath(requested);
  if(physical.split('/').includes('node_modules'))return; // Same lockfile trust as web guard.
  if(!/\.(?:[cm]?[jt]sx?|py|pyc|node)$/.test(physical) &&
    !/^(?:package\.json|tsconfig[^/]*\.json|pnpm-lock\.yaml)$/.test(basename(physical)))return;
  check(physical);
  for(let dir=dirname(physical);;dir=dirname(dir)) {
    for(const name of ['package.json','tsconfig.json']) {
      const file=resolve(dir,name);if(rawExists(file))check(file);
    }
    if(dir===root)break;
  }
}
// Recheck on every read, not only at startup: a previously admitted AST file may change.
for(const name of ['readFileSync','readFile','createReadStream','openSync','open']) {
  const original=fs[name];
  fs[name]=function(path,...args){admit(path);return Reflect.apply(original,this,[path,...args]);};
}
for(const name of ['readFile','open']) {
  const original=promises[name];
  promises[name]=function(path,...args){admit(path);return Reflect.apply(original,this,[path,...args]);};
}
syncBuiltinESMExports();
for(const [path] of pins)admit(resolve(root,path));
await import('../web/node-guard.mjs');
