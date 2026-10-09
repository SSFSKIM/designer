// Prospective source discovery plus guarded production exercise on synthetic documents.
// Returns an UNSEALED runtime-closure document. No live config/root, native observation,
// actual W50 candidate or committed output is read/written; temp fixtures are removed.
import { createHash } from 'node:crypto';
import { mkdtempSync, readFileSync, realpathSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { discoverSources } from '../owner/discover.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = realpathSync(resolve(HERE, '../../../../..'));
const sha = path => createHash('sha256').update(readFileSync(path)).digest('hex');

export function discoverRuntime() {
  const sources = discoverSources(ROOT, [
    resolve(HERE, 'runtime-entry.mjs'), resolve(HERE, 'runtime-probe.ts'),
    resolve(HERE, 'runtime-bridge.ts'), resolve(HERE, '../owner/node-guard.mjs'),
  ], [resolve(HERE, 'runtime-discovery.mjs'), resolve(HERE, '../owner/discover.mjs'),
    resolve(HERE, '../web/vite-guard.mjs'), resolve(ROOT, 'pnpm-lock.yaml'),
    resolve(ROOT, 'tsconfig.base.json')]).sources;
  const node = { path: realpathSync(process.execPath), sha256: sha(realpathSync(process.execPath)) };
  const provisional = { schema:'w50-fit-runtime-closure-1', sources, node, pixels:'NONE',
    discovery:'owner static import discovery + guarded production joins/builder/transfer exercise' };
  const scratch = realpathSync(mkdtempSync(resolve(tmpdir(), 'w50-fit-runtime-probe-')));
  try {
    const closurePath = resolve(scratch, 'runtime-closure.json');
    writeFileSync(closurePath, JSON.stringify(provisional)+'\n', { flag:'wx' });
    const env = Object.fromEntries(['HOME','TMPDIR','TMP','TEMP'].filter(k => process.env[k] !== undefined)
      .map(k => [k, process.env[k]]));
    Object.assign(env, { PATH:'/usr/bin:/bin:/usr/sbin:/sbin', LC_ALL:'C', TSX_DISABLE_CACHE:'1',
      W50_WEB_ROOT:ROOT, W50_WEB_CLOSURE:closurePath, W50_WEB_CLOSURE_SHA256:sha(closurePath) });
    const child = spawnSync(node.path, ['--import', resolve(HERE, '../owner/node-guard.mjs'),
      '--import', 'tsx', resolve(HERE, 'runtime-probe.ts'), scratch],
      { cwd:resolve(ROOT, 'packages/calibration'), env, encoding:'utf8', maxBuffer:8*1024*1024 });
    if (child.status !== 0) throw Error(child.stderr || child.stdout || 'Runtime exercise did not complete');
    const exercise = JSON.parse(child.stdout);
    if (exercise.status !== 'SYNTHETIC_PRODUCTION_BRIDGE_EXERCISED' || exercise.pixels !== 'NONE') {
      throw Error('Production bridge synthetic exercise has no completion witness');
    }
    for (const pin of sources) {
      if (sha(resolve(ROOT,pin.path)) !== pin.sha256) throw Error('Source changed during runtime discovery');
    }
    return { ...provisional, exercise: { ...exercise,
      probe: { path: sources.find(pin => pin.path.endsWith('/fit/runtime-probe.ts')).path,
        sha256: sha(resolve(HERE, 'runtime-probe.ts')) } } };
  } finally { rmSync(scratch, { recursive:true, force:true }); }
}
