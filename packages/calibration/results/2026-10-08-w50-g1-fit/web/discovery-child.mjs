import fs from 'node:fs';
import childProcess from 'node:child_process';
import {Server} from 'node:net';
import {syncBuiltinESMExports} from 'node:module';
import {join,isAbsolute} from 'node:path';
import {pathToFileURL} from 'node:url';
import {CAL,ROOT,HERE,assertPreseal} from './discovery-common.mjs';
import {observe,event,finish} from './discovery-hooks.mjs';

assertPreseal();
const route=process.env.W50_DISCOVERY_ROUTE;
if(!['capture-canonical','capture-w50','compare-canonical','browser-canonical','browser-w50'].includes(route))
  throw Error('Unknown fixed source-discovery route');
const scratch=process.env.W50_DISCOVERY_SCRATCH;
process.once('exit',()=>finish({route,browserLaunched:false,realMeasurementDataRead:false}));
// A second independent stop: even a future startup refactor cannot launch a browser.
const playwright=await import('@playwright/test');
const denyLaunch=async()=>{event('BROWSER_LAUNCH_REFUSED');throw Error('Discovery never launches browsers');};
for(const type of [playwright.chromium,playwright.firefox,playwright.webkit]) {
  type.launch=denyLaunch;type.launchPersistentContext=denyLaunch;
  if(type.launch!==denyLaunch || type.launchPersistentContext!==denyLaunch)throw Error('Browser launch refusal not installed');
}
event('BROWSER_STUB_INSTALLED');
Server.prototype.listen=function(){event('NETWORK_LISTEN_REFUSED');throw Error('Discovery never opens a listener');};
const isW50=route.endsWith('-w50');
const scenes=join(ROOT,isW50
  ? 'packages/calibration/results/2026-10-08-w50-g0-declaration/bed/scenes-w50.json'
  : 'apps/reference-apple/scenes.json');
process.env.VITREA_SCENES=scenes;
process.env.VITREA_FIXTURES=join(scratch,'fixtures');
process.env.VITREA_WEB_CAPTURES=join(scratch,'captures');
process.env.VITREA_MATRIX_PATH=join(scratch,'synthetic-matrix.json');
fs.mkdirSync(process.env.VITREA_FIXTURES);
observe(scenes,'declared-scene-input');
const sceneDoc=JSON.parse(fs.readFileSync(scenes,'utf8'));

if(route.startsWith('browser-')) {
  const {createServer}=await import('vite');
  const server=await createServer({configFile:join(CAL,'web/vite.config.ts')});
  try {
    const html=fs.readFileSync(join(CAL,'web/index.html'),'utf8');
    await server.transformIndexHtml('/index.html',html);
    const queue=['/scene.ts'],seen=new Set();
    while(queue.length) {
      const url=queue.shift();
      if(seen.has(url))continue;
      seen.add(url);
      const transformed=await server.transformRequest(url);
      if(!transformed)throw Error(`Untransformed browser module: ${url}`);
      const mod=await server.moduleGraph.getModuleByUrl(url);
      if(!mod)throw Error(`Missing transformed browser module: ${url}`);
      for(const child of mod.importedModules) {
        if(child.id?.startsWith('\0') || !child.id)continue;
        const file=child.id.split('?')[0];
        if(isAbsolute(file) && !file.split('/').includes('node_modules')) {
          observe(file,'vite-import-edge');queue.push(child.url);
        }
      }
    }
    event('BROWSER_GRAPH_TRANSFORMED',{canvas:sceneDoc.canvas,moduleCount:seen.size,urls:[...seen].sort()});
  } finally {await server.close();}
} else {
  const {buildCurrent}=await import('./current.ts');
  const candidate25=buildCurrent(.25,join(scratch,'current025'));
  const candidate50=buildCurrent(.5,join(scratch,'current050'));
  if(route.startsWith('capture-')) {
    for(const [index,variant] of [
      {candidate:candidate25,renderer:'css',scale:1,pose:'rest'},
      {candidate:candidate50,renderer:'webgpu',scale:2,pose:'inactive'},
    ].entries()) {
      const scene=isW50?`cell-grey-004-s096__${variant.pose}`:`dark-solid__rrect-md__${variant.pose}`;
      process.argv=[process.execPath,join(CAL,'scripts/capture-web.ts'),scene,
        '--renderer',variant.renderer,'--scale',String(variant.scale),'--color-scheme','dark',
        '--candidate-document',variant.candidate.path,'--out',join(scratch,`captures${index}`)];
      event('CAPTURE_STARTUP_VARIANT',{scene,...variant});
      await import(pathToFileURL(join(CAL,'scripts/capture-web.ts')).href+`?discovery=${index}`);
    }
  } else {
    const scene='dark-solid__rrect-md__rest';
    const set=Object.entries(sceneDoc.split).find(([,ids])=>ids.includes(scene))[0];
    const background=sceneDoc.scenes.find(s=>s.id===scene).background;
    fs.writeFileSync(join(process.env.VITREA_FIXTURES,'manifest.json'),JSON.stringify({
      backgrounds:{[`${background}@1x`]:'synthetic-background.png'},caveats:['SOURCE ONLY: no image files'],
      profiles:[{profileKey:'apple-macos-27.0-1x-dark-standard-glass0.25',colorScheme:'dark',
        a11yMode:'standard',display:{actualBackingScale:1},fixtures:[{sceneId:scene,file:'synthetic-native.png',
          fixtureSet:set,captureMethod:'synthetic-source-probe',materialRendered:true}]}],
    }));
    childProcess.spawnSync=(command,args)=>{
      event('COMPARE_STOP_BEFORE_CHILD',{command,args});
      throw Error('W50 source discovery: compare stopped before capture subprocess');
    };
    syncBuiltinESMExports();
    process.argv=[process.execPath,join(CAL,'cli/compare.ts'),'--profile','apple-macos-27.0-1x-dark-standard-glass0.25',
      '--renderer','webgpu','--candidate-document',candidate25.path,'--set',set,'--scene',scene,
      '--alpha','--allow-colourless-tints','--out-matrix',process.env.VITREA_MATRIX_PATH];
    await import(pathToFileURL(join(CAL,'cli/compare.ts')).href);
  }
}
