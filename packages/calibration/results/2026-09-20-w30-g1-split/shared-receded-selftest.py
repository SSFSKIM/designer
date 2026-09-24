"""W36: real apply calls on synthetic generations; no canonical path is writable here (§5.179)."""
import contextlib,hashlib,importlib.util,io,json,pathlib,sys,tempfile,unittest
HERE=pathlib.Path(__file__).resolve().parent

class SharedReceded(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        spec=importlib.util.spec_from_file_location('split',HERE/'split-generation.py')
        self.tool=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.tool)
        t=self.tool;t.ROOT=self.root;t.RESULTS=self.root/'results';t.MATRIX=t.RESULTS/'matrix.json';t.SUPERSEDED=t.RESULTS/'superseded';t.PROFILES=self.root/'profiles'
        t.SUPERSEDED.mkdir(parents=True);t.PROFILES.mkdir()
        for name in ['light.json','light-receded.json']:(t.PROFILES/name).write_text('{"current":true}\n')
        self.a='a'*12;self.b='b'*12;self.c='c'*12;self.d='d'*12
        self.index={'what':'historical lookup','rule':'historical rule','claimsFields':'historical claims','files':{},'byDocumentSha256':{}}
        self.evidence=self.root/'evidence';self.evidence.mkdir()
        (t.SUPERSEDED/'README.md').write_text(t.README_BEGIN+'\n'+t.README_END+'\n')
        self.add_prior(self.a,self.c)
        self.rows=[self.row(self.b,self.c),self.row(None,None)]

    def row(self,active,receded):
        clauses=[]
        if active:clauses.append('materialProfile=profiles/light.json sha256:'+active)
        if receded:clauses.append('recededProfile=profiles/light-receded.json sha256:'+receded)
        return {'key':{'profileKey':'apple-macos-27.0-1x-light-standard-glass0.5','sceneId':'scene-'+str(active),'web':{'capturePath':' '.join(clauses)}},'tier':'texture','fixtureSet':'calibration','capturedAt':'2026-09-22T00:00:00Z','reading':0.12345678901234567}

    def add_prior(self,active,receded,filename=None):
        filename=filename or active+'.json';raw=(json.dumps({'schemaVersion':5,'cells':[self.row(active,receded)]},indent=2)+'\n').encode()
        (self.tool.SUPERSEDED/filename).write_bytes(raw)
        docs=[{'path':'profiles/light.json','sha256':active}]
        if receded:docs.append({'path':'profiles/light-receded.json','sha256':receded})
        self.index['files'][filename]={'activeDocumentSha256':active,'documents':docs,'readUnderClaims':'old reader','movedUnderClaims':'old mover','capturedAt':{'first':'2026-09-22T00:00:00Z','last':'2026-09-22T00:00:00Z'},'supersededOn':'2026-09-23','rowCount':1,'rowsByProfileKey':{'apple-macos-27.0-1x-light-standard-glass0.5':1},'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        self.index['byDocumentSha256'].setdefault(active,filename)
        if receded:self.index['byDocumentSha256'].setdefault(receded,filename)

    def run_apply(self):
        t=self.tool;raw=(json.dumps({'schemaVersion':5,'cells':self.rows},indent=2)+'\n').encode();t.MATRIX.write_bytes(raw)
        (t.SUPERSEDED/'index.json').write_text(json.dumps(self.index,indent=2)+'\n')
        argv=sys.argv;sys.argv=['split-generation.py','apply','--evidence',str(self.evidence),'--claims','new mover','--read-claims','new reader']
        try:
            with contextlib.redirect_stdout(io.StringIO()) as log:status=t.main()
        finally:sys.argv=argv
        return status,log.getvalue(),raw

    def assert_refused(self):
        status,log,raw=self.run_apply();self.assertEqual(status,1,log)
        self.assertEqual(self.tool.MATRIX.read_bytes(),raw)
        self.assertEqual(json.loads((self.tool.SUPERSEDED/'index.json').read_text()),self.index)
        self.assertFalse((self.evidence/'before-manifest.json').exists())

    def test_shared_receded_keeps_alias_and_raw_rows(self):
        status,log,raw=self.run_apply();self.assertEqual(status,0,log)
        actual=json.loads((self.tool.SUPERSEDED/'index.json').read_text())
        self.assertEqual(actual['byDocumentSha256'][self.c],self.a+'.json')
        self.assertEqual(actual['byDocumentSha256'][self.b],self.b+'.json')
        self.assertEqual(actual['sharedReceded'][self.c],[self.a+'.json',self.b+'.json'])
        self.assertEqual(actual['files'][self.a+'.json'],self.index['files'][self.a+'.json'])
        for k,v in self.index['byDocumentSha256'].items():self.assertEqual(actual['byDocumentSha256'][k],v)
        moved=(self.tool.SUPERSEDED/(self.b+'.json')).read_bytes()
        a=self.tool.elements(raw)[1][0];b=self.tool.elements(moved)[1][0]
        self.assertEqual(raw[a[0]:a[1]],moved[b[0]:b[1]])
        readme=(self.tool.SUPERSEDED/'README.md').read_text()
        self.assertIn('Shared receded documents',readme);self.assertIn(self.c,readme)

    def test_active_alias_collision_still_refuses_before_write(self):
        self.add_prior(self.b,self.d,'earlier-compound.json')
        self.assert_refused()

    def test_shared_list_extends_without_repointing_history(self):
        self.add_prior(self.d,self.c)
        self.index['sharedReceded']={self.c:[self.a+'.json',self.d+'.json']}
        status,log,_=self.run_apply();self.assertEqual(status,0,log)
        actual=json.loads((self.tool.SUPERSEDED/'index.json').read_text())
        self.assertEqual(actual['sharedReceded'][self.c],[self.a+'.json',self.d+'.json',self.b+'.json'])
        self.assertEqual(actual['byDocumentSha256'][self.c],self.a+'.json')

    def test_receded_hash_cannot_reinterpret_an_active_alias(self):
        self.index['byDocumentSha256'][self.c]=self.a+'.json'
        self.index['files'][self.a+'.json']['activeDocumentSha256']=self.c
        self.assert_refused()

    def test_corrupt_historical_file_refuses_before_write(self):
        with (self.tool.SUPERSEDED/(self.a+'.json')).open('ab') as f:f.write(b'changed')
        self.assert_refused()

    def test_unrelated_new_receded_hash_gets_an_ordinary_alias(self):
        self.rows=[self.row(self.b,self.d),self.row(None,None)]
        status,log,_=self.run_apply();self.assertEqual(status,0,log)
        actual=json.loads((self.tool.SUPERSEDED/'index.json').read_text())
        self.assertEqual(actual['byDocumentSha256'][self.d],self.b+'.json')
        self.assertNotIn(self.d,actual.get('sharedReceded',{}))

if __name__=='__main__':unittest.main()
