import {createRequire} from 'node:module';
import {isAbsolute} from 'node:path';
import {pathToFileURL} from 'node:url';
import {observe,event} from './discovery-hooks.mjs';
const require=createRequire(import.meta.url);
const vite=await import(pathToFileURL(require.resolve('vite')).href);
export const defineConfig=vite.defineConfig;

export async function createServer(config) {
  if(!process.env.W50_DISCOVERY_ROUTE?.startsWith('browser-')) {
    event('CAPTURE_STOP_BEFORE_LISTEN');
    throw Error('W50 source discovery: capture stopped before Vite listen or browser launch');
  }
  return vite.createServer({...config,configLoader:'native',
    cacheDir:process.env.W50_DISCOVERY_SCRATCH+'/vite-cache',
    server:{...config.server,middlewareMode:true,hmr:false,ws:false,watch:null},
    optimizeDeps:{...config.optimizeDeps,noDiscovery:true,include:[]},
    plugins:[{name:'w50-discovery',enforce:'pre',
      load(id){const path=id.split('?')[0];if(isAbsolute(path))observe(path,'vite-load');return null;},
      transform(_code,id){const path=id.split('?')[0];if(isAbsolute(path))observe(path,'vite-transform');return null;},
      transformIndexHtml:{order:'pre',handler(html,context){observe(context.filename,'vite-html');return html;}},
    },...(config.plugins??[])]});
}
