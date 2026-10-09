"""Actual corrected pre-fit consumer roundtrips, using generated native/owner fixtures only."""
import copy
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
FIT=HERE.parent
EXECUTION=FIT.parent/'2026-10-08-w50-g1-current2/execution'


def source(path,name):
    module=types.ModuleType(name);module.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module


A=source(HERE/'assembler.py','synthetic_join_for_validator')
B=source(HERE/'bound.py','synthetic_bound_for_validator')
P=source(EXECUTION/'prefit.py','actual_corrected_prefit')


class ConsumerRoundtrip(unittest.TestCase):
    def test_native_three_run_envelope_and_current_values_pass_actual_corrected_validator(self):
        fixtures=source(EXECUTION/'test_native_evidence.py','synthetic_native_consumer_fixture')
        with patch.object(tempfile,'tempdir',str(Path(tempfile.gettempdir()).resolve())):
            fixture=fixtures.NativeEnvelope();fixture.setUp();self.addCleanup(fixture.doCleanups)
        original={k:v for k,v in fixture.row.items() if k!='native'}
        original.update(nativeEvidence=None,currentEvidence=None,currentMetadata=None,B=None,status='UNMEASURED',
            currentDocumentPair={'active.dark':'a'*64,'receded.dark':'b'*64},currentGeneration='a'*12,historical=[])
        current_path=fixture.repo/'current.png';current_path.write_bytes(fixtures.png())
        current={'path':str(current_path),'sha256':fixtures.N.sha(current_path)}
        metadata=fixture.put('current-metadata.json',{'synthetic':'metadata'})
        evidence=dict(**{k:original[k] for k in A.KEY},role=original['role'],originalReference=copy.deepcopy(original),
            currentDocumentPair=original['currentDocumentPair'],currentGeneration=original['currentGeneration'],
            evidenceKind='completed-current-gate0',nativeEvidenceEnvelope=fixture.envelope,
            measurement=dict(status='MEASURED',measurementStatus='MEASURED',required=True,value=[2,3,4],nativeValue=[1,2,3],
                nativeRepeat={'barCodes':[.5]*3,'spreadCodes':[0]*3,'passes':True},nativeSupportWitnesses=[]),
            provenance={'capture':current,'cell':metadata,'nativeRead':fixture.native_read})
        artifacts=A.Artifacts(str(fixture.repo/'assembled-provenance'))
        completed=A.complete_native(original,evidence,artifacts,(),())
        B.materialize_artifacts({'artifacts':artifacts.documents})
        before={'schema':'w50-reference-inventory-1','inputs':{'bed':fixture.manifest},'cells':[original]}
        after={**before,'cells':[completed]}
        P.validate_completion(before,after,[],fixture.repo)
        self.assertEqual(completed['support'],original['support'])
        self.assertIsInstance(completed['nativeEvidence'],dict)
        changed=copy.deepcopy(after);changed['cells'][0]['native']=[9,9,9]
        with self.assertRaises(ValueError):P.validate_completion(before,changed,[],fixture.repo)

    def test_source_owned_owner_failure_is_readable_without_invented_native_current_or_scalar_budget(self):
        fixtures=source(FIT/'execution/test_owner_evidence.py','synthetic_owner_consumer_fixture')
        with patch.object(tempfile,'tempdir',str(Path(tempfile.gettempdir()).resolve())):
            fixture=fixtures.OwnerEvidence();fixture.setUp();self.addCleanup(fixture.doCleanups)
        original=copy.deepcopy(fixture.row)
        original.update(role='gate',support='Original source-owned owner applicability prose',
                        status='UNMEASURED',B=None,historical=[])
        inventory={'schema':'w50-reference-inventory-1','cells':[original]}
        inventory_pin=fixture.put('original-inventory.json',inventory)
        batch=dict(schema='w50-owner-evidence-batch-1',inventoryPin=inventory_pin,
            **{name:fixture.projection[name] for name in ('inputsPin','reportPin','contractsPin')},rows=[fixture.projection])
        batch_pin=fixture.put('batch.json',batch)
        index=dict(schema='w50-owner-projection-index-1',source=batch_pin,
                   rows=[{'key':list(A.key(original)),'evidence':fixture.evidence}])
        provenance=dict(original=inventory_pin,ownerBatch=batch_pin,ownerContracts=fixture.contract,ownerSource=fixture.owner)
        joined=A.owner_join([original],index,batch,{fixture.evidence['path']:fixture.projection},provenance,fixture.repo)
        completed=joined[A.key(original)]
        P.validate_completion(inventory,{**inventory,'cells':[completed]},[],fixture.repo,
            owner_budget_keys=[list(A.key(original))],owner_contracts=fixture.contract,owner_source=fixture.owner)
        self.assertEqual(completed['status'],'MEASURED');self.assertIsNone(completed['B'])
        self.assertNotIn('native',completed);self.assertNotIn('current',completed)
        self.assertEqual(fixture.projection['axes']['M1']['evidence']['verdict'],'failure')


if __name__=='__main__':unittest.main()
