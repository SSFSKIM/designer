// Pre-seal observation only. This file cannot authorize a production capture.
import fs from 'node:fs';
import fsPromises from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {Module,registerHooks,syncBuiltinESMExports} from 'node:module';
import {dirname,relative,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {ROOT,HERE,assertPreseal,assertDataPath,inside} from './discovery-common.mjs';
assertPreseal();
const scratch=process.env.W50_DISCOVERY_SCRATCH;
if(!scratch || process.env.W50_WEB_CLOSURE || process.env.W50_WEB_CLOSURE_SHA256)
  throw Error('Discovery requires its own scratch context, never runtime authorization');
const rawRead=fs.readFileSync;
const observed=new Map();
const events=[];
const digest=raw=>createHash('sha256').update(raw).digest('hex');

export function observe(path,via='node-import') {
  if(path.startsWith('\0'))return;
  const physical=fs.realpathSync(path);
  if(!inside(physical,ROOT) || physical.split('/').includes('node_modules'))return;
  assertDataPath(physical,scratch);
  const rel=relative(ROOT,physical),sha256=digest(rawRead(physical));
  const prior=observed.get(rel);
  if(prior && prior.sha256!==sha256)throw Error(`Source changed during discovery: ${rel}`);
  observed.set(rel,{path:rel,sha256,via:[...new Set([...(prior?.via??[]),via])]});
  for(let dir=dirname(physical);;dir=dirname(dir)) {
    for(const name of ['package.json','tsconfig.json']) {
      const file=resolve(dir,name);
      if(fs.existsSync(file)) {
        const key=relative(ROOT,file),hash=digest(rawRead(file));
        if(observed.has(key) && observed.get(key).sha256!==hash)throw Error(`Changed metadata: ${key}`);
        observed.set(key,{path:key,sha256:hash,via:['resolution-metadata']});
      }
    }
    if(dir===ROOT)break;
  }
}
export function event(kind,details={}) {events.push({kind,...details});}
export function finish(details={}) {
  assertPreseal();
  for(const rel of ['pnpm-lock.yaml','tsconfig.base.json',
    'packages/calibration/web/tsconfig.json','packages/calibration/scripts/tsconfig.json'])observe(resolve(ROOT,rel),'anchor');
  for(const name of ['node-guard.mjs','vite-guard.mjs','discovery-hooks.mjs','discovery-common.mjs',
    'discovery-child.mjs','discovery-vite.mjs','discover.mjs'])observe(resolve(HERE,name),'instrument');
  fs.writeFileSync(resolve(scratch,'observed.json'),JSON.stringify({sources:[...observed.values()],events,...details},null,2)+'\n',{flag:'wx'});
}
function guard(path) {assertDataPath(path,scratch);}
fs.readFileSync=function(path,...args){guard(path);return Reflect.apply(rawRead,this,[path,...args]);};
for(const name of ['readFile','createReadStream']) {
  const original=fs[name];fs[name]=function(path,...args){guard(path);return Reflect.apply(original,this,[path,...args]);};
}
const promiseRead=fsPromises.readFile;
fsPromises.readFile=function(path,...args){guard(path);return Reflect.apply(promiseRead,this,[path,...args]);};
syncBuiltinESMExports();
const compile=Module.prototype._compile;
Module.prototype._compile=function(content,path,...args){observe(path,'commonjs-compile');return Reflect.apply(compile,this,[content,path,...args]);};
const shim=new URL('./discovery-vite.mjs',import.meta.url).href;
registerHooks({
  resolve(specifier,context,next) {
    if(specifier==='vite' && context.parentURL!==shim)return {url:shim,shortCircuit:true};
    return next(specifier,context);
  },
  load(url,context,next) {
    if(url.startsWith('file:'))observe(fileURLToPath(url));
    return next(url,context);
  },
});
