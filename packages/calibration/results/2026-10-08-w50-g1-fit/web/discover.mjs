#!/usr/bin/env node
/** Exercise prospective Node/Vite imports into a fresh scratch proposal, never a runtime seal.
 * CLI: node web/discover.mjs /absolute/new/scratch-directory
 * A real execution-root.json anywhere in this wave makes discovery unavailable.
 */
import {mkdirSync,writeFileSync,readFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {HERE,CAL,ROOT,assertPreseal,freshExternal} from './discovery-common.mjs';
const hash=raw=>createHash('sha256').update(raw).digest('hex');

export function discover(destination) {
  assertPreseal();
  const output=freshExternal(destination);mkdirSync(output,{recursive:true});
  const sources=new Map(),routes=[];
  for(const route of ['capture-canonical','capture-w50','compare-canonical','browser-canonical','browser-w50']) {
    assertPreseal();
    const scratch=join(output,route);mkdirSync(scratch);
    const env=Object.fromEntries(Object.entries(process.env).filter(([key])=>
      !key.startsWith('VITREA_')&&!key.startsWith('W50_')&&!['NODE_OPTIONS','NODE_PATH'].includes(key)));
    Object.assign(env,{W50_DISCOVERY_SCRATCH:scratch,W50_DISCOVERY_ROUTE:route});
    const result=spawnSync(process.execPath,['--import','tsx','--import',join(HERE,'discovery-hooks.mjs'),
      join(HERE,'discovery-child.mjs')],{cwd:CAL,env,encoding:'utf8',timeout:90000,maxBuffer:16*1024*1024});
    writeFileSync(join(scratch,'process.log'),(result.stdout??'')+(result.stderr??''),{flag:'wx'});
    if(!existsSync(join(scratch,'observed.json')))throw Error(`No discovery result for ${route}: ${result.stderr}`);
    const report=JSON.parse(readFileSync(join(scratch,'observed.json'),'utf8'));
    const expected=route.startsWith('browser-')?'BROWSER_GRAPH_TRANSFORMED':
      route.startsWith('capture-')?'CAPTURE_STOP_BEFORE_LISTEN':'COMPARE_STOP_BEFORE_CHILD';
    if(result.error || result.signal || !report.events.some(e=>e.kind===expected) ||
      !report.events.some(e=>e.kind==='BROWSER_STUB_INSTALLED') ||
      report.events.some(e=>['BROWSER_LAUNCH_REFUSED','NETWORK_LISTEN_REFUSED'].includes(e.kind)) ||
      (route.startsWith('browser-') && result.status!==0)) {
      throw Error(`Source discovery did not reach its fixed safe boundary: ${route}\n${result.stderr}`);
    }
    if(route.startsWith('capture-') && report.events.filter(e=>e.kind===expected).length!==2)
      throw Error('Capture discovery did not exercise both candidate startup variants');
    routes.push({route,exitCode:result.status,browserLaunched:false,realMeasurementDataRead:false,
      events:report.events,observations:{path:join(scratch,'observed.json'),sha256:hash(readFileSync(join(scratch,'observed.json')))}});
    for(const pin of report.sources) {
      const old=sources.get(pin.path);
      if(old && old.sha256!==pin.sha256)throw Error(`Source changed across probes: ${pin.path}`);
      sources.set(pin.path,{path:pin.path,sha256:pin.sha256,
        via:[...new Set([...(old?.via??[]),...pin.via])],routes:[...new Set([...(old?.routes??[]),route])]});
    }
  }
  assertPreseal();
  for(const pin of sources.values())if(hash(readFileSync(join(ROOT,pin.path)))!==pin.sha256)
    throw Error(`Source changed before proposal completion: ${pin.path}`);
  const proposal={schema:'w50-web-source-proposal-1',status:'PROPOSED_SOURCE_ONLY',runtimeAuthorization:false,
    repo:ROOT,environment:{node:process.version,executable:process.execPath},routes,
    sources:[...sources.values()].sort((a,b)=>a.path.localeCompare(b.path)),
    limitations:[
      'No browser or native render, fixture image, screenshot statistic, GPU adaptation or draw was executed.',
      'Browser dependencies were exercised by Vite transformation, including statically resolved dynamic imports; computed imports are not guessed.',
      'Capture startup stops before server listen; compare startup stops before its capture subprocess, using synthetic fixture metadata.',
      'Runtime admission still requires a reviewed root-pinned exact source closure; this proposal supplies no execution capability.',
    ]};
  writeFileSync(join(output,'proposal.json'),JSON.stringify(proposal,null,2)+'\n',{flag:'wx'});
  return {path:join(output,'proposal.json'),sha256:hash(readFileSync(join(output,'proposal.json'))),sources:proposal.sources.length};
}
if(process.argv[1] && resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  if(process.argv.length!==3)throw Error('Usage: discover.mjs <fresh absolute scratch directory>');
  console.log(JSON.stringify(discover(process.argv[2])));
}
