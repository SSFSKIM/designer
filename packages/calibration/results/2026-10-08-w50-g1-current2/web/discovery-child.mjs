import fs from 'node:fs';
import childProcess from 'node:child_process';
import {Server} from 'node:net';
import {createHash} from 'node:crypto';
import {syncBuiltinESMExports} from 'node:module';
import {join,isAbsolute} from 'node:path';
import {pathToFileURL} from 'node:url';
import {CAL,ROOT,HERE,assertPreseal} from './discovery-common.mjs';
import {observe,event,finish,exerciseRuntimeGuard} from './discovery-hooks.mjs';

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
    const transformedHtml=await server.transformIndexHtml('/index.html',html);
    if(isW50 !== transformedHtml.includes('w50-dl5f-border-box'))throw Error('Wrong scene host: border-box must be NEWBED only');
    event('HOST_TRANSFORM_VERIFIED',{newbed:isW50,borderBox:transformedHtml.includes('w50-dl5f-border-box')});
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
  await exerciseRuntimeGuard(isW50?HERE:join(HERE,'../../2026-10-08-w50-g1-fit/web'),join(CAL,'web/scene.ts'));
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
    const profile='apple-macos-27.0-1x-dark-standard-glass0.25';
    const fixtureRoot=join(scratch,'original-native-tree');
    fs.mkdirSync(join(fixtureRoot,profile),{recursive:true});
    const manifestPath=join(fixtureRoot,'manifest.json');
    fs.writeFileSync(manifestPath,JSON.stringify({
      backgrounds:{[`${background}@1x`]:'synthetic-background.png'},caveats:['SOURCE ONLY: generated synthetic PNG, no reference image'],
      profiles:[{profileKey:'apple-macos-27.0-1x-dark-standard-glass0.25',colorScheme:'dark',
        a11yMode:'standard',display:{actualBackingScale:1},fixtures:[{sceneId:scene,file:`${profile}/${scene}.png`,
          fixtureSet:set,captureMethod:'synthetic-source-probe',materialRendered:true}]}],
    }));
    const {PNG}=await import('pngjs');
    const image=new PNG({width:2,height:2});image.data.fill(128);
    for(let i=3;i<image.data.length;i+=4)image.data[i]=255;
    const nativeBytes=PNG.sync.write(image);
    const nativePath=join(fixtureRoot,profile,scene+'.png');
    fs.writeFileSync(nativePath,nativeBytes,{flag:'wx'});
    const request={profile,scenes:[scene],sets:[set],
      fixtures:{path:fixtureRoot,manifest:{path:manifestPath,
        sha256:createHash('sha256').update(fs.readFileSync(manifestPath)).digest('hex')}},
      native:[{scene,path:nativePath,sha256:createHash('sha256').update(nativeBytes).digest('hex')}]};
    const requestBytes=JSON.stringify(request);
    const requestPath=join(scratch,'native-request.json'),receiptPath=join(scratch,'native-receipt.json');
    fs.writeFileSync(requestPath,requestBytes,{flag:'wx'});
    process.env.W50_NATIVE_REQUEST_SHA256=createHash('sha256').update(requestBytes).digest('hex');
    childProcess.spawnSync=(command,args)=>{
      const receipt=JSON.parse(fs.readFileSync(receiptPath,'utf8'));
      if(receipt.status!=='ADMITTED' || receipt.requestSha256!==process.env.W50_NATIVE_REQUEST_SHA256 ||
        JSON.stringify(receipt.native)!==JSON.stringify(request.native))throw Error('Synthetic native receipt differs');
      if(process.env.VITREA_FIXTURES!==fs.realpathSync(fixtureRoot) ||
        JSON.stringify(receipt.fixtures)!==JSON.stringify(request.fixtures))throw Error('Original synthetic tree not inherited');
      event('ORIGINAL_SYNTHETIC_TREE_INHERITED',{path:process.env.VITREA_FIXTURES});
      event('SYNTHETIC_NATIVE_RECEIPT_VERIFIED',{receipt:receiptPath,status:receipt.status});
      event('COMPARE_STOP_BEFORE_CHILD',{command,args});
      throw Error('W50 source discovery: compare stopped before capture subprocess');
    };
    syncBuiltinESMExports();
    const wrapper=join(HERE,'../../2026-10-08-w50-g1-fit/canonical/compare.ts');
    process.argv=[process.execPath,wrapper,'--admission',requestPath,'--receipt',receiptPath,'--',
      '--profile',request.profile,'--renderer','webgpu','--candidate-document',candidate25.path,
      '--set',set,'--scene',scene,'--alpha','--out-matrix',process.env.VITREA_MATRIX_PATH];
    await import(pathToFileURL(wrapper).href);
  }
}
