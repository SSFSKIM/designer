/** Build one hypothetical identity candidate (DL5o): fit/candidate.ts buildCandidate with
 * charts = null, so the dark patches and digests are unchanged and only the records DL5o requires
 * are added. Called by owner/r3/identity.py with: BASELINE_PATH BASELINE_SHA256 OUTPUT. */
import { buildCandidate } from '../../fit/candidate.ts';

const [path, sha256, output] = process.argv.slice(2);
if (!path || !sha256 || !output || process.argv.length !== 5) {
  throw Error('Usage: identity-build.ts BASELINE_PATH BASELINE_SHA256 OUTPUT');
}
process.stdout.write(JSON.stringify(buildCandidate({ path, sha256 }, null, output,
  ['X1 owner self-check: the hypothetical identity candidate of W50 DL5o'])) + '\n');
