// Prospective closure enforcement for the production Node driver and its Vite module graph.
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, realpathSync } from 'node:fs';
import { Module, registerHooks } from 'node:module';
import { dirname, relative, resolve, isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';

const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const root = realpathSync(process.env.W50_WEB_ROOT);
const raw = readFileSync(process.env.W50_WEB_CLOSURE);
if (hash(raw) !== process.env.W50_WEB_CLOSURE_SHA256) throw Error('Changed web source closure');
const pins = new Map(JSON.parse(raw).sources.map(pin => [pin.path, pin.sha256]));

function checkPin(physical) {
  const rel = relative(root, physical);
  if (rel.startsWith('..') || isAbsolute(rel) || pins.get(rel) !== hash(readFileSync(physical))) {
    throw Error(`Unsealed or changed web source: ${physical}`);
  }
}

export function checkSource(path) {
  const physical = realpathSync(path);
  // Third-party packages are pinned by pnpm-lock.yaml; repository sources must be named.
  if (physical.split('/').includes('node_modules')) return;
  checkPin(physical);
  // Identical source bytes under a different package format need not execute the same way.
  // Existing or newly introduced format boundaries must therefore be in the same closure.
  for (let directory = dirname(physical); ; directory = dirname(directory)) {
    const manifest = resolve(directory,'package.json');
    if (existsSync(manifest)) checkPin(realpathSync(manifest));
    if (directory === root) break;
  }
}

for (const [path] of pins) checkSource(resolve(root,path));

// tsx's CommonJS extension hooks can bypass registerHooks.load, including below an
// ESM parent. They still hand the transformed module to _compile before its body
// executes. Admit the ORIGINAL file there, not the transformed string: the closure
// pins source bytes, and tsx itself is a lockfile-pinned compiler dependency.
const compile = Module.prototype._compile;
Module.prototype._compile = function guardedCompile(content, filename, ...args) {
  checkSource(filename);
  return Reflect.apply(compile, this, [content, filename, ...args]);
};

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
