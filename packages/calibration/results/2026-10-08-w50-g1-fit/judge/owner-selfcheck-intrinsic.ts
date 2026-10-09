/** The owner self-check's Node half (DL5o): X75 and X76 on a hypothetical identity candidate,
 * read through the owner-candidate bridge's frozen engine. owner_selfcheck.py launches it from
 * packages/calibration with one JSON request on stdin, {config, records}, both repository-pinned
 * {path, sha256}; stdout is the intrinsic report, which the Python half grades with the judge's
 * own grade_owner_report and never prints. Nothing is written. */
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { isDeepStrictEqual } from 'node:util';
import { selfcheckIntrinsics } from '../owner-candidate/bridge.ts';

const REPO = resolve(dirname(fileURLToPath(import.meta.url)), '../../../../..');
const request = JSON.parse(readFileSync(0, 'utf8'));
// tsx resolves from packages/calibration; the frozen engine then reads record pins with the
// repository as its working directory, as the live owner child does (owner-candidate/live.py).
process.chdir(REPO);
if (!request || !isDeepStrictEqual(Object.keys(request).sort(), ['config', 'records'])) {
  throw Error('Self-check request is {config, records}');
}
process.stdout.write(JSON.stringify(selfcheckIntrinsics(request.config, request.records, REPO)) + '\n');
