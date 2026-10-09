// Reuse production Vite configuration; add source admission rather than a second scene page.
import { createRequire } from 'node:module';
import { isAbsolute } from 'node:path';
import { pathToFileURL } from 'node:url';
import { checkSource } from './node-guard.mjs';
const require = createRequire(import.meta.url);
const vite = await import(pathToFileURL(require.resolve('vite')).href);
export const defineConfig = vite.defineConfig;

export function sourcePlugin() {
  return {
    name:'w50-prospective-source-closure', enforce:'pre',
    load(id) {
      const path=id.split('?')[0];
      if (isAbsolute(path) && !path.startsWith('\0')) checkSource(path);
      return null;
    },
    transform(_code,id) {
      const path=id.split('?')[0];
      if (isAbsolute(path) && !path.startsWith('\0')) checkSource(path);
      return null;
    },
    transformIndexHtml: {order:'pre',handler(html,context) {
      checkSource(context.filename);
      return html;
    }},
  };
}

export async function createServer(config) {
  // Native config loading avoids an unpinned esbuild-generated config bundle. Every
  // repository import is checked by the synchronous Node hook before it executes.
  return vite.createServer({...config,configLoader:'native',
    plugins:[sourcePlugin(),...(config.plugins ?? [])],
    optimizeDeps:{...config.optimizeDeps,noDiscovery:true,include:[]}});
}
