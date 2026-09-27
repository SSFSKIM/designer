/** G0's amended scope: reread committed canonical cal/val only, without a browser or capture.
 * Holdout, recorded, probe and EVERY W39 pixel stay closed. This is not an exposure runner.
 */
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { resolve, relative, isAbsolute, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { canonicalRole, inspectCell, inventory, renderCell, type Cell } from './sheets';

const HERE = fileURLToPath(new URL('.', import.meta.url));
const ROOT = resolve(HERE, '../../../../..');
const sha = (bytes: Uint8Array | string) => createHash('sha256').update(bytes).digest('hex');
interface Options {
  repositoryRoot: string; fixtureRoot: string; captureRoot: string; outputRoot: string; png?: boolean;
}
interface RenderRecord {
  bed: string; profileKey: string; sceneId: string; role?: string;
  status: 'RENDERED' | 'SKIPPED' | 'UNMEASURED'; reason?: string;
  html?: string; htmlSha256?: string; nativeSha256?: string; shippedSha256?: string;
  png?: string; pngSha256?: string;
}
function beneath(root: string, path: string) {
  const rel = relative(resolve(root), resolve(path));
  return rel === '' || (rel !== '..' && !rel.startsWith('../') && !isAbsolute(rel));
}
export async function renderCalval(cells: readonly Cell[], options: Options): Promise<RenderRecord[]> {
  const protectedRoots = [options.fixtureRoot, options.captureRoot,
    ...['apps/reference-apple/fixtures', 'packages/calibration/profiles',
      'packages/calibration/results/generations', 'packages/calibration/results/superseded',
      'packages/calibration/web-captures', 'packages/calibration/web-captures-superseded']
      .map(p => resolve(options.repositoryRoot, p))];
  if (protectedRoots.some(root => beneath(root, options.outputRoot))) {
    throw new Error('sheet output must not enter a protected evidence/capture tree');
  }
  mkdirSync(options.outputRoot, { recursive: true });
  const records: RenderRecord[] = [];
  for (const cell of cells) {
    const identity = { bed: cell.bed, profileKey: cell.profileKey, sceneId: cell.sceneId };
    if (cell.bed !== 'canonical') {
      records.push({ ...identity, status: 'UNMEASURED', reason: 'G0 never opens W39 pixels' });
      continue;
    }
    const role = canonicalRole(cell.sceneId, options.repositoryRoot);
    if (role !== 'calibration' && role !== 'validation') {
      records.push({ ...identity, role, status: 'SKIPPED', reason: 'G0 canonical cal/val only' });
      continue;
    }
    // Admission is settled before even checking the native path's existence.
    const nativePath = resolve(options.fixtureRoot, cell.profileKey, `${cell.sceneId}.png`);
    if (!beneath(options.fixtureRoot, nativePath)) throw new Error('native path escapes fixture root');
    const inspected = inspectCell(cell, options.repositoryRoot, options.captureRoot);
    const native = existsSync(nativePath) ? readFileSync(nativePath) : undefined;
    const html = await renderCell(cell, { repositoryRoot: options.repositoryRoot,
      captureRoot: options.captureRoot, readNative: async () => native });
    const filename = `${encodeURIComponent(cell.profileKey)}__${encodeURIComponent(cell.sceneId)}.html`;
    writeFileSync(join(options.outputRoot, filename), html, { flag: 'wx' });
    const png = options.png ? execFileSync('python3.12', [join(HERE, 'export-png.py')],
      { input: html, maxBuffer: 16 * 1024 * 1024 }) : undefined;
    const pngName = filename.replace(/\.html$/, '.png');
    if (png) writeFileSync(join(options.outputRoot, pngName), png, { flag: 'wx' });
    records.push({ ...identity, role,
      status: native && inspected.status === 'MATCH' ? 'RENDERED' : 'UNMEASURED',
      html: filename, htmlSha256: sha(html),
      ...(png ? { png: pngName, pngSha256: sha(png) } : {}),
      ...(native ? { nativeSha256: sha(native) } : {}),
      ...(inspected.status === 'MATCH' ? { shippedSha256: sha(readFileSync(inspected.pngPath)) } : {}),
    });
  }
  return records;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const { values } = parseArgs({ options: {
    'repository-root': { type: 'string', default: ROOT },
    'fixture-root': { type: 'string', default: resolve(ROOT, 'apps/reference-apple/fixtures') },
    'capture-root': { type: 'string', default: resolve(ROOT, 'packages/calibration/web-captures') },
    'output-root': { type: 'string' },
    'png': { type: 'boolean', default: false },
  } });
  if (!values['output-root']) throw new Error('--output-root must name a fresh scratch or gate directory');
  const options = { repositoryRoot: resolve(values['repository-root']!),
    fixtureRoot: resolve(values['fixture-root']!), captureRoot: resolve(values['capture-root']!),
    outputRoot: resolve(values['output-root']), png: values['png']! };
  const metadata = inventory(options.repositoryRoot, options.captureRoot, resolve(HERE, 'absent-w39-captures'));
  const records = await renderCalval(metadata.cells, options);
  const report = { mode: 'canonical-calibration-validation-shipped-only', ...options,
    canonicalHoldoutPixelsOpened: 0, w39PixelsOpened: 0, candidate: 'EMPTY — awaiting G2 document',
    rendered: records.filter(r => r.status === 'RENDERED').length,
    UNMEASURED: records.filter(r => r.status === 'UNMEASURED').length,
    skipped: records.filter(r => r.status === 'SKIPPED').length,
    records };
  writeFileSync(join(options.outputRoot, 'render-inventory.json'), JSON.stringify(report, null, 2) + '\n',
    { flag: 'wx' });
  console.log(JSON.stringify({ ...report, records: undefined }, null, 2));
}
