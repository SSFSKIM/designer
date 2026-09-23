#!/usr/bin/env python3.12
"""Audit the spent receipt's bookkeeping discrepancy without reading a payload."""
import copy
import hashlib
import json
import subprocess
import identification as M

path=M.G0/'wave-identification-receipt.jsonl'
raw=path.read_bytes()
relative=path.relative_to(M.W.ROOT)
committed=subprocess.check_output(['git','-C',str(M.W.ROOT),'show','44e007f8:'+str(relative)])
assert raw==committed, 'The spent receipt log must remain byte-for-byte unchanged'
events=[json.loads(line) for line in raw.splitlines()]
assert [r['event'] for r in events]==['begin','complete']
sha=lambda value:hashlib.sha256(M.W.stable(value).encode()).hexdigest()
begin,complete=[r['configuration'] for r in events]
clean=copy.deepcopy(complete);removed=[]
for i,entry in enumerate(clean['candidate']['document']['candidates']):
    value=entry['fit'].pop('receiptCandidateIndex')
    assert value==i
    removed.append(dict(path=f'candidate.document.candidates[{i}].fit.receiptCandidateIndex',value=value))
assert len(removed)==40
assert M.W.stable(clean)==M.W.stable(begin)
assert sha(begin)==events[0]['configurationSha256']
assert sha(complete)!=events[1]['configurationSha256']
audit=dict(receiptPath=str(relative),receiptFileSha256=hashlib.sha256(raw).hexdigest(),
    originalCommit='44e007f8',logByteIdenticalToOriginal=True,
    events=[dict(event=r['event'],recordedConfigurationSha256=r['configurationSha256'],
                 actualConfigurationSha256=sha(r['configuration'])) for r in events],
    removedBookkeepingFields=removed,removedCount=len(removed),
    strippedCompleteConfigurationSha256=sha(clean),
    strippedCompleteExactlyEqualsBegin=True,
    coefficientsAndAllOtherConfigurationFieldsUnchanged=True,
    finding='The complete event does not reproduce its recorded digest. Removing only forty bookkeeping indices restores exact canonical-JSON equality with begin. This is a metadata-only discrepancy; the original spent log is preserved, not repaired or re-spent.',
    payloadAccess='None: only the committed receipt events are read; no held PNG, crop, statistic or capture is opened.')
M.save(M.HERE/'review-fix/receipt-integrity-audit.json',audit)
for r in audit['events']:print(r['event'],r['actualConfigurationSha256'])
print('After stripping only bookkeeping:',sha(clean),'exact equality:',audit['strippedCompleteExactlyEqualsBegin'])
