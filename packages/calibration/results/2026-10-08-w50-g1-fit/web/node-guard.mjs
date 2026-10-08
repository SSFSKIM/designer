// Prospective closure enforcement for the production Node driver and its Vite module graph.
import { createHash } from 'node:crypto';
import { readFileSync, realpathSync } from 'node:fs';
import { registerHooks } from 'node:module';
import { relative, resolve, isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';

const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const root = realpathSync(process.env.W50_WEB_ROOT);
const raw = readFileSync(process.env.W50_WEB_CLOSURE);
if (hash(raw) !== process.env.W50_WEB_CLOSURE_SHA256) throw Error('Changed web source closure');
const pins = new Map(JSON.parse(raw).sources.map(pin => [pin.path, pin.sha256]));

export function checkSource(path) {
  const physical = realpathSync(path);
  const rel = relative(root, physical);
  // Third-party packages are pinned by pnpm-lock.yaml; repository sources must be named.
  if (physical.split('/').includes('node_modules')) return;
  if (rel.startsWith('..') || isAbsolute(rel) || pins.get(rel) !== hash(readFileSync(physical))) {
    throw Error(`Unsealed or changed web source: ${physical}`);
  }
}

for (const [path] of pins) checkSource(resolve(root,path));
const viteShim = new URL('./vite-guard.mjs', import.meta.url).href;
registerHooks({
  resolve(specifier, context, next) {
    if (specifier === 'vite' && context.parentURL !== viteShim) {
      checkSource(fileURLToPath(viteShim));
      return { url:viteShim, shortCircuit:true };
    }
    return next(specifier,context);
  },
  load(url, context, next) {
    if (url.startsWith('file:')) checkSource(fileURLToPath(url));
    return next(url,context);
  },
});
