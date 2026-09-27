import assert from 'node:assert/strict';
import { test } from 'node:test';
import { capturePlan } from './plan';

test('canonical diagnostic admits cal/val only and changes only macOS27 light receded clauses', () => {
  const plan = capturePlan();
  assert.equal(plan.cells.length, 330);
  assert.equal(new Set(plan.cells.map(c => c.profileKey)).size, 12);
  assert(plan.cells.every(c => ['calibration', 'validation'].includes(c.role)));
  for (const cell of plan.cells) {
    const changed = cell.documents.filter((doc, i) =>
      doc.path !== cell.shippedDocuments[i]!.path || doc.sha256 !== cell.shippedDocuments[i]!.sha256);
    if (cell.profileKey.startsWith('apple-macos-27.0-') && cell.profileKey.includes('-light-')) {
      assert.equal(changed.length, 1);
      assert.equal(changed[0]!.kind, 'recededProfile');
    } else assert.equal(changed.length, 0);
    if (cell.profileKey.startsWith('apple-macos-26.5-')) assert.equal(cell.documents.length, 1);
  }
});
