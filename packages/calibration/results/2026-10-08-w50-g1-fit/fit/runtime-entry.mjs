// Internal stdlib-first child of execution.py. It reads material documents, never native values.
// This is a source-guarded arithmetic/builder helper, not a standalone pre-fit permission issuer.
import { createHash } from 'node:crypto';
import { readFileSync, realpathSync } from 'node:fs';
import { dirname, isAbsolute, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const hash = path => createHash('sha256').update(readFileSync(path)).digest('hex');
const request = JSON.parse(readFileSync(0, 'utf8'));
const rootPath = realpathSync(request.executionRoot);
if (readFileSync(rootPath+'.sha256', 'utf8') !== `${hash(rootPath)}  ${rootPath.split('/').at(-1)}\n`) {
  throw Error('Changed configured execution root');
}
const root = JSON.parse(readFileSync(rootPath, 'utf8'));
if (root.schema !== 'w50-g1-execution-root-1') throw Error('Runtime bridge requires the configured live root');
const repo = realpathSync(root.repo);
const closurePin = request.runtimeClosure;
if (!root.inputs.some(p => p.path === closurePin?.path && p.sha256 === closurePin?.sha256)) {
  throw Error('Runtime closure is not a separately bound live-root input');
}
const closurePath = realpathSync(resolve(repo, closurePin.path));
if (hash(closurePath) !== closurePin.sha256 ||
    realpathSync(process.env.W50_WEB_ROOT) !== repo ||
    realpathSync(process.env.W50_WEB_CLOSURE) !== closurePath ||
    process.env.W50_WEB_CLOSURE_SHA256 !== closurePin.sha256) {
  throw Error('Preloaded runtime guard differs from the configured closure');
}
const closure = JSON.parse(readFileSync(closurePath, 'utf8'));
if (closure.schema !== 'w50-fit-runtime-closure-1') throw Error('Wrong fitting runtime closure');
const sources = Object.fromEntries(closure.sources.map(pin => [pin.path, pin.sha256]));
function inside(path) {
  const absolute = realpathSync(resolve(repo, path));
  const rel = relative(repo, absolute);
  if (rel.startsWith('..') || isAbsolute(rel)) throw Error('Runtime input/source escapes repository');
  return { absolute, rel };
}
for (const [path, sha256] of Object.entries(sources)) {
  if (hash(inside(path).absolute) !== sha256) throw Error('Changed root source closure');
}
const self = fileURLToPath(import.meta.url);
if (sources[relative(repo, self)] !== hash(self)) throw Error('Runtime entry is outside its source closure');
// execution.py preloads owner/node-guard.mjs BEFORE tsx. Its original-byte read guards
// and shared web _compile hook cover CJS transform paths that registerHooks alone misses.
// Importing it here too makes direct helper invocation fail closed rather than trust env labels.
await import('../owner/node-guard.mjs');
function pinned(item) {
  const path = inside(item.path).absolute;
  if (hash(path) !== item.sha256) throw Error('Changed candidate bytes');
  return { path, sha256: item.sha256 };
}
if (!root.baselineDocuments.some(p => p.path === request.baseline?.path && p.sha256 === request.baseline?.sha256)) {
  throw Error('Bridge baseline is not the frozen gate0 document');
}
const baseline = pinned(request.baseline);
const bridge = await import('./runtime-bridge.ts');
let output;
if (request.operation === 'joins') output = await bridge.fixedGate0Joins(baseline);
else if (request.operation === 'transfer') output = await bridge.proveTransfer(baseline, pinned(request.evaluation));
else if (request.operation === 'build') {
  const destination = resolve(request.output);
  const fitDirectory = dirname(self);
  if (!destination.startsWith(fitDirectory+'/')) throw Error('Candidate destination is outside fitting scratch');
  output = await bridge.assembleCandidate(baseline, request.charts, destination);
} else throw Error('Unknown bounded runtime operation');
for (const [path, sha256] of Object.entries(sources)) {
  if (hash(inside(path).absolute) !== sha256) throw Error('Runtime source changed during arithmetic');
}
process.stdout.write(JSON.stringify(output)+'\n');
