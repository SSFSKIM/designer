// Fixed stdlib-only bootstrap. The live writer alone supplies request bytes on stdin;
// serialized snapshots carry provenance, never a reusable dispatcher capability.
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {dirname,resolve,relative,isAbsolute,normalize} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {isDeepStrictEqual} from 'node:util';

const HERE=dirname(fileURLToPath(import.meta.url));
const ROOT=resolve(HERE,'../../../../..');
const hash=raw=>createHash('sha256').update(raw).digest('hex');
function checked(pin) {
  if(!pin||Object.keys(pin).sort().join(',')!=='path,sha256'||typeof pin.path!=='string'
    ||!isAbsolute(pin.path)||fs.realpathSync(pin.path)!==pin.path||!/^[a-f0-9]{64}$/.test(pin.sha256))
    throw Error('Noncanonical live bootstrap pin');
  const raw=fs.readFileSync(pin.path);
  if(hash(raw)!==pin.sha256)throw Error(`Changed live bootstrap pin: ${pin.path}`);
  return raw;
}
const read=pin=>JSON.parse(checked(pin));
const configPin={path:process.env.W50_OWNER_LIVE_CONFIG,sha256:process.env.W50_OWNER_LIVE_CONFIG_SHA256};
const config=read(configPin);
if(config.schema!=='w50-owner-candidate-config-1')throw Error('Unknown live config');
for(const key of Object.keys(process.env)) {
  if(/^(?:NODE_|ESBUILD_|TSX_|TS_NODE_|BABEL_|SWC_|PYTHON)/.test(key)
    &&!(key==='TSX_DISABLE_CACHE'&&process.env[key]==='1'))
    throw Error(`Unadmitted child compiler/interpreter environment: ${key}`);
}
checked(config.node);checked(config.interpreter);checked(config.tsx);
// Retain the lexical venv executable; its canonical target alone selects base Python.
if(typeof config.pythonLaunch!=='string'||!isAbsolute(config.pythonLaunch)
  ||normalize(config.pythonLaunch)!==config.pythonLaunch
  ||fs.realpathSync(config.pythonLaunch)!==config.interpreter.path
  ||process.env.W50_OWNER_LIVE_PYTHON!==config.pythonLaunch)
  throw Error('Live Python launch differs from pinned interpreter');
checked(config.pythonVenvConfig);
if(typeof config.pythonPrefix!=='string'||!isAbsolute(config.pythonPrefix)
  ||fs.realpathSync(config.pythonPrefix)!==config.pythonPrefix
  ||dirname(config.pythonLaunch)!==resolve(config.pythonPrefix,'bin')
  ||config.pythonVenvConfig.path!==resolve(config.pythonPrefix,'pyvenv.cfg'))
  throw Error('Live Python prefix/config differs from launch');
if(fs.realpathSync(process.execPath)!==config.node.path)throw Error('Changed live Node executable');
if(config.python!==resolve(HERE,'live-python-shim'))throw Error('Not the fixed live Python shim');
if(process.env.W50_WEB_ROOT!==ROOT||process.env.W50_WEB_CLOSURE!==config.runtimeClosure.path
  ||process.env.W50_WEB_CLOSURE_SHA256!==config.runtimeClosure.sha256)
  throw Error('Live Node closure differs from config');
const closure=read(config.runtimeClosure),sources=new Map();
if(closure.schema!=='w50-owner-candidate-runtime-1'||closure.exercise!=='synthetic source-only'
  ||!isDeepStrictEqual(closure.toolchain,{node:config.node,tsx:config.tsx})
  ||!isDeepStrictEqual(closure.nodeEnvironment,{version:process.version,
    executable:fs.realpathSync(process.execPath),executableSha256:config.node.sha256})
  ||closure.probe.path!==resolve(HERE,'live-probe.mjs'))throw Error('Unexercised live Node closure');
checked(closure.probe);
for(const pin of closure.sources) {
  if(isAbsolute(pin.path)||pin.path.split('/').includes('..')||sources.has(pin.path))
    throw Error('Invalid live source closure');
  checked({path:resolve(ROOT,pin.path),sha256:pin.sha256});sources.set(pin.path,pin.sha256);
}
for(const path of [fileURLToPath(import.meta.url),resolve(HERE,'bridge.ts'),
  resolve(HERE,'live-python.py'),resolve(HERE,'live-python-shim'),
  resolve(HERE,'../owner/node-guard.mjs'),resolve(HERE,'../web/node-guard.mjs'),
  resolve(HERE,'../web/vite-guard.mjs'),resolve(HERE,'../execution/guard.py')]) {
  checked({path,sha256:sources.get(relative(ROOT,path))});
}
const request=JSON.parse(fs.readFileSync(0,'utf8'));
if(Object.keys(request).sort().join(',')!=='config,snapshot'||!isDeepStrictEqual(request.config,configPin)
  ||request.snapshot.sha256!==process.env.W50_OWNER_LIVE_SNAPSHOT_SHA256)
  throw Error('Request was not bound by the live snapshot writer');
const snapshot=read(request.snapshot),root=read(snapshot.executionRoot),claim=read(snapshot.claim);
const contract=read(snapshot.contract),batch=read(snapshot.batch),execution=read(snapshot.executionClaim);
const absolute=pin=>({path:resolve(ROOT,pin.path),sha256:pin.sha256});
const registered=pin=>root.inputs.some(item=>isDeepStrictEqual(absolute(item),pin));
if(snapshot.schema!=='w50-owner-live-capture-union-1'||snapshot.phase!=='exposure'
  ||snapshot.executionRoot.sha256!==process.env.W50_OWNER_LIVE_ROOT_SHA256
  ||contract.executionRootSha256!==snapshot.executionRoot.sha256||root.repo!==ROOT
  ||!registered(configPin)||!registered(config.runtimeClosure)||!isDeepStrictEqual(snapshot.config,configPin)
  ||claim.phase!=='exposure'||claim.output!==snapshot.output
  ||claim.contractSha256!==snapshot.contract.sha256||claim.batchSha256!==snapshot.batch.sha256
  ||request.snapshot.path!==resolve(claim.output,'owner-candidate.snapshot.json')
  ||snapshot.claim.path!==snapshot.contract.path+'.started.json'
  // The logical claim is whichever attempt first ran; the process binding is the analysis
  // marker the parent was issued under, held by exactly this parent.
  ||snapshot.executionClaim.path!==snapshot.contract.path+'.phase/analysis.started.json'
  ||execution.schema!=='w50-live-analysis-claim-1'||execution.pid!==process.ppid
  ||!isDeepStrictEqual(execution.logicalContract,snapshot.contract)||execution.output!==snapshot.output
  ||!isDeepStrictEqual(absolute(contract.batch),snapshot.batch)
  ||!isDeepStrictEqual(batch.cohort,snapshot.cohort))
  throw Error('Snapshot lacks the live parent claim/root binding');
// Guard installation happens before tsx, frozen engine, source AST readers or edge helpers.
await import('../owner/node-guard.mjs');
const compiler=await import(pathToFileURL(config.tsx.path).href);
compiler.register();
process.env.W50_OWNER_LIVE_NODE_PID=String(process.pid);
const {executeRequest}=await import('./bridge.ts');
const report=await executeRequest(request);
process.stdout.write(JSON.stringify(report)+'\n');
