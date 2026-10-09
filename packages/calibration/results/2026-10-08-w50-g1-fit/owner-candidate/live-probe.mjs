// Fixed exercised-discovery entry. Only source binding and empty synthetic membership;
// never evaluateRequest/evaluateRows, a material document, a matrix, or an image.
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const hash=raw=>createHash('sha256').update(raw).digest('hex');
const closure=JSON.parse(fs.readFileSync(process.env.W50_WEB_CLOSURE,'utf8'));
const compiler=process.env.W50_OWNER_PROBE_TSX;
if(hash(fs.readFileSync(compiler))!==process.env.W50_OWNER_PROBE_TSX_SHA256)
  throw Error('Changed probe compiler entry');
(await import(pathToFileURL(compiler).href)).register();
await import('./bridge.ts');
const {createCandidateEngine}=await import('./frozen-engine.ts');
const {selectOwnerUnion}=await import('./union.ts');
const prefix='packages/calibration/results/2026-10-08-w50-g1-fit/owner/';
const sourcePins=Object.fromEntries(['api.ts','referee.ts','intrinsic.ts','source.ts'].map(name=>{
  const rel=prefix+name,item=closure.sources.find(pin=>pin.path===rel);
  if(!item)throw Error('Frozen source authority absent from probe closure');
  return [rel,{path:resolve(process.env.W50_WEB_ROOT,rel),sha256:item.sha256}];
}));
createCandidateEngine({sourcePins,declarations:[]});
const empty={status:'CAPTURED',captures:[],candidateSha256s:[]};
selectOwnerUnion([],{gateKeys:[],exposureKeys:[],ownerUnionKeys:[]},[],empty,empty);
process.stdout.write(JSON.stringify({exercise:'synthetic source-only',pixels:'NONE',
  sourcesSha256:hash(Buffer.from(JSON.stringify(closure.sources))),
  nodeEnvironment:{version:process.version,executable:fs.realpathSync(process.execPath),
    executableSha256:hash(fs.readFileSync(process.execPath))}})+'\n');
