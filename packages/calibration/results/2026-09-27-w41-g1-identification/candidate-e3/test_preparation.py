"""Preparation refuses incomplete images instead of manufacturing survival."""
from pathlib import Path
import hashlib
import sys
import tempfile
import unittest
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import prepare as p


class PreparationTests(unittest.TestCase):
    def test_unclaimed_miss_stays_raw_not_true(self):
        cell=next(c for c in p.s.wave.cells if p.s.identity(c)[0]=='dark-active')
        raw={'status':'measured','passes':False,'members':[{'raw':'retained'}]}
        row=p.admission(cell,raw)
        self.assertEqual(row,{'status':'not claimed (identity)','passes':None,'score':raw})

    def test_structured_claimed_deep_miss_stays_diagnostic(self):
        cell=next(c for c in p.s.wave.cells if p.s.disposition(c)=='not claimed (structured backdrop)')
        raw={'status':'measured','passes':False,'diagnostic':'S0'}
        self.assertEqual(p.admission(cell,raw)['score'],raw)

    def test_claimed_rail_failure_cannot_be_admitted(self):
        cell=next(c for c in p.s.wave.cells if p.s.disposition(c)=='claimed uniform body')
        raw={'status':'UNMEASURED','reason':'censored','passes':None,'constraintsPass':False}
        self.assertFalse(p.admission(cell,raw))
        raw['constraintsPass']=True
        self.assertTrue(p.admission(cell,raw))

    def test_missing_rendered_capture_fails_before_native_reader(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'empty.json'
            p.save(path,{'cells':{}})
            with self.assertRaisesRegex(ValueError,'membership'):
                p.render_calval(path,path,Path(t)/'out')
            self.assertFalse((Path(t)/'out').exists())

    def test_external_png_is_snapshotted_without_rewriting_blind_reference(self):
        with tempfile.TemporaryDirectory() as t:
            temp=Path(t); root=temp/'repo'; candidate=root/'candidate-e3'
            root.mkdir(); candidate.mkdir()
            external=temp/'production.png'; external.write_bytes(b'external shipped PNG')
            blind=root/'blind.png'; blind.write_bytes(b'blind shipped PNG')
            projection=root/'projection.json'; p.save(projection,{'verified':True})
            def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
            cal=root/'cal.json'; frozen=root/'blind.json'
            p.save(cal,{'captures':{'cal':dict(png=str(external),pngSha256=digest(external),
                projection='projection.json',projectionSha256=digest(projection))}})
            p.save(frozen,{'captures':{'blind':dict(png='blind.png',pngSha256=digest(blind),
                projection='projection.json',projectionSha256=digest(projection))}})
            out=candidate/'shipped-baseline.json'
            options=dict(sources=(cal,frozen),root=root,candidate_dir=candidate,
                         expected={'cal','blind'},projector=lambda cell,path:{'verified':True})
            p.baseline_map(out,**options)
            mapped=p.read(out)
            snapshot=candidate/'shipped-payloads'/f'{digest(external)}.png'
            self.assertEqual(mapped['cells']['cal']['png'],str(snapshot.relative_to(root)))
            self.assertEqual(snapshot.read_bytes(),external.read_bytes())
            self.assertEqual(mapped['cells']['blind']['png'],'blind.png')
            self.assertEqual(mapped['source'],{'cal.json':digest(cal),'blind.json':digest(frozen)})
            self.assertEqual(list((candidate/'shipped-payloads').iterdir()),[snapshot])
            p.baseline_map(candidate/'second-map.json',**options)
            self.assertEqual(p.read(candidate/'second-map.json'),mapped)
            external.unlink()
            self.assertEqual((root/mapped['cells']['cal']['png']).read_bytes(),b'external shipped PNG')

    def test_snapshot_rejects_existing_payload_collision(self):
        with tempfile.TemporaryDirectory() as t:
            temp=Path(t); root=temp/'repo'; candidate=root/'candidate-e3'
            (candidate/'shipped-payloads').mkdir(parents=True)
            external=temp/'production.png'; external.write_bytes(b'correct PNG')
            digest=hashlib.sha256(external.read_bytes()).hexdigest()
            (candidate/'shipped-payloads'/f'{digest}.png').write_bytes(b'wrong PNG')
            projection=root/'projection.json'; p.save(projection,{'verified':True})
            cal=root/'cal.json'; blind=root/'blind.json'
            p.save(cal,{'captures':{'cal':dict(png=str(external),pngSha256=digest,
                projection='projection.json',projectionSha256=p.s.sha(projection))}})
            p.save(blind,{'captures':{}})
            out=candidate/'shipped-baseline.json'
            with self.assertRaisesRegex(ValueError,'collision'):
                p.baseline_map(out,sources=(cal,blind),root=root,candidate_dir=candidate,
                               expected={'cal'},projector=lambda cell,path:{'verified':True})
            self.assertFalse(out.exists())
            self.assertEqual((candidate/'shipped-payloads'/f'{digest}.png').read_bytes(),b'wrong PNG')

    def test_record_is_exclusive_not_rewritable(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'artifact.json.gz'
            p.save(path,{'a':1})
            with self.assertRaises(FileExistsError):p.save(path,{'a':2})
            self.assertEqual(p.read(path),{'a':1})


if __name__=='__main__':unittest.main()
