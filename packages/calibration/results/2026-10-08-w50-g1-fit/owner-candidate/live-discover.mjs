// Prospective source-only tooling. Importing this module neither discovers nor writes a root.
// Static discovery is not an exercised runtime closure and is deliberately not admissible.
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {dirname,resolve,relative,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
import {discoverSources,ownerSources} from '../owner/discover.mjs';

const HERE=dirname(fileURLToPath(import.meta.url));
const ROOT=resolve(HERE,'../../../../..');
const hash=raw=>createHash('sha256').update(raw).digest('hex');
const pin=path=>({path:fs.realpathSync(path),sha256:hash(fs.readFileSync(path))});
function checked(item) {
  if(!item||!isAbsolute(item.path)||fs.realpathSync(item.path)!==item.path
    ||hash(fs.readFileSync(item.path))!==item.sha256)throw Error('Changed discovery input pin');
  return item.path;
}
export function discoverLiveSources(root,entries,readers=[]) {
  return {...discoverSources(root,entries,readers),schema:'w50-owner-candidate-static-1'};
}

/** The existing owner graph supplies its explicit historical AST readers. The new bridge
 * graph adds the candidate identity/document reader and frozen engine. The bootstrap has
 * two intentional dynamic edges: the separately pinned tsx API and fixed bridge/guard
 * entries below. Listing that bootstrap as source does not waive dynamic-import rejection
 * in the bridge graph or admit any caller-selected module or source directory. */
export function candidateSources() {
  const frozen=ownerSources();
  const additional=discoverLiveSources(ROOT,[resolve(HERE,'bridge.ts')],
    ['live.py','live-node.mjs','live-python.py','live-discover.mjs','live-probe.mjs']
      .map(name=>resolve(HERE,name)).concat([resolve(HERE,'../execution/guard.py')]));
  const sources=new Map();
  for(const item of [...frozen.sources,...additional.sources]) {
    if(sources.has(item.path)&&sources.get(item.path)!==item.sha256)throw Error('Source moved during discovery');
    sources.set(item.path,item.sha256);
  }
  // The shell entry is an explicit executable edge, not an import or data reader.
  const shim=resolve(HERE,'live-python-shim');
  sources.set(relative(ROOT,shim),pin(shim).sha256);
  return {...additional,sources:[...sources].sort(([a],[b])=>a.localeCompare(b))
    .map(([path,sha256])=>({path,sha256}))};
}

/** Run only the fixed source/synthetic probe; no owner input, candidate, capture or root is
 * accepted. The caller reviews the returned closure and registers it in a FUTURE root. */
export function exerciseRuntime(root,staticPin,toolchain,output) {
  root=fs.realpathSync(root);
  const closure=JSON.parse(fs.readFileSync(checked(staticPin),'utf8'));
  if(closure.schema!=='w50-owner-candidate-static-1'||closure.exercise!==undefined)
    throw Error('Require an unexercised static candidate source list');
  checked(toolchain.node);checked(toolchain.tsx);
  const here=resolve(root,'packages/calibration/results/2026-10-08-w50-g1-fit/owner-candidate');
  const probe=pin(resolve(here,'live-probe.mjs'));
  for(const required of [probe.path,resolve(here,'../owner/node-guard.mjs')]) {
    const found=closure.sources.find(item=>item.path===relative(root,required));
    if(!found||found.sha256!==pin(required).sha256)throw Error('Static closure omits fixed probe/guard');
  }
  const parent=fs.realpathSync(dirname(output));
  const rel=relative(root,parent);
  if(!isAbsolute(output)||fs.existsSync(output)||(!rel.startsWith('..')&&!isAbsolute(rel)))
    throw Error('Runtime closure output must be fresh external scratch');
  const env=Object.fromEntries(['HOME','TMPDIR','TMP','TEMP'].filter(key=>key in process.env)
    .map(key=>[key,process.env[key]]));
  Object.assign(env,{PATH:'/usr/bin:/bin:/usr/sbin:/sbin',LC_ALL:'C',TSX_DISABLE_CACHE:'1',
    W50_WEB_ROOT:root,W50_WEB_CLOSURE:staticPin.path,W50_WEB_CLOSURE_SHA256:staticPin.sha256,
    W50_OWNER_PROBE_TSX:toolchain.tsx.path,W50_OWNER_PROBE_TSX_SHA256:toolchain.tsx.sha256});
  const stdout=execFileSync(toolchain.node.path,['--import',resolve(here,'../owner/node-guard.mjs'),probe.path],
    {cwd:root,env,encoding:'utf8',maxBuffer:1024*1024});
  const result=JSON.parse(stdout);
  if(result.exercise!=='synthetic source-only'||result.pixels!=='NONE'
    ||result.sourcesSha256!==hash(Buffer.from(JSON.stringify(closure.sources))))
    throw Error('Source-only probe did not attest this static source list');
  // Recheck even after the child: discovery cannot silently mix source generations.
  checked(staticPin);checked(probe);checked(toolchain.node);checked(toolchain.tsx);
  for(const item of closure.sources)checked({path:resolve(root,item.path),sha256:item.sha256});
  const runtime={...closure,schema:'w50-owner-candidate-runtime-1',exercise:result.exercise,
    probe,toolchain,nodeEnvironment:result.nodeEnvironment,
    exerciseSha256:hash(Buffer.from(stdout))};
  fs.writeFileSync(output,JSON.stringify(runtime,null,2)+'\n',{flag:'wx'});
  return pin(output);
}
