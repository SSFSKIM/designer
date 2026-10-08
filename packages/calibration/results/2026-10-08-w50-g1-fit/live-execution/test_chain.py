"""The LIVE root chain and its per-root slots (W50 DL5o), on synthetic git repositories.

A successor root is sealed beside the root it supersedes and names it in a supersedes record;
only the newest generation is admitted by any entry, and a successor is never sealed over a
predecessor whose slot area holds anything. Nothing here reads the real sealed root.
"""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
H=Path(__file__).resolve().parent


def module(name,file):
    s=importlib.util.spec_from_file_location(name,H/file);m=importlib.util.module_from_spec(s)
    sys.modules[s.name]=m;s.loader.exec_module(m);return m


A=module('chain_test_authority','authority.py');C=A.C;D=A.D
ROOT={'schema':'w50-g1-execution-root-1','lifecycle':'logical-phase-attempts-1','quarantine':'instrument-api-role-discipline-1'}


class Chain(unittest.TestCase):
    """A synthetic repository whose live-execution directory holds a chain of sealed roots, each
    committed alone so its sealing commit is the one that introduced it."""
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.repo=Path(t.name).resolve();self.live=self.repo/A.FIT_REL/'live-execution';self.live.mkdir(parents=True)
        self.git('init','-q');self.git('commit','-q','--allow-empty','-m','base')
        self.commits={};self.docs={}

    def git(self,*args):
        return subprocess.run(['git','-C',str(self.repo),'-c','user.name=synthetic','-c','user.email=synthetic@invalid',*args],
                              check=True,capture_output=True,text=True).stdout.strip()

    def path(self,n):return self.live/C.root_name(n)
    def pin(self,path):return D.pin(self.repo,path)

    def ruling(self,n,commit,text=None,name=None):
        path=self.live/'rulings'/(name or f'DL9{chr(96+n)}.txt');path.parent.mkdir(exist_ok=True)
        path.write_text(text if text is not None else
                        f'DL9{chr(96+n)} (synthetic). Nothing executed under root `{commit[:9]}`; a successor is sealed.\n')
        return self.pin(path)

    def record(self,n,commit=None):
        """Generation n's exact supersedes record, its ruling pinned among its inputs."""
        commit=commit or self.commits[n-1];text=self.ruling(n,commit)
        return {'schema':A.SUPERSESSION,'root':self.pin(self.path(n-1)),'sealingCommit':commit,
                'ruling':{'id':f'DL9{chr(96+n)}','text':text},'unexecuted':A.unexecuted(self.repo,self.path(n-1))}

    def doc(self,n,record=None):
        doc={**ROOT,'repo':str(self.repo),'inputs':[]}
        if n>1:
            doc['supersedes']=record or self.record(n);doc['inputs'].append(doc['supersedes']['ruling']['text'])
        return doc

    def seal(self,n,doc=None):
        doc=doc or self.doc(n);path=self.path(n);D.write_sealed(path,doc)
        self.git('add','-f',str(path),str(path)+'.sha256',str(self.live/'rulings') if n>1 else str(path))
        self.git('commit','-q','-m',f'seal {n}');self.commits[n]=self.git('rev-parse','HEAD');self.docs[n]=doc
        return path

    def refuses(self,pattern,n,doc):
        with self.assertRaisesRegex(ValueError,pattern):A.predecessors(self.path(n),doc)


class Succession(Chain):
    def test_an_unexecuted_predecessor_accepts_a_successor_then_is_refused_everywhere(self):
        one=self.seal(1);two=self.doc(2)
        # In memory, at the successor's own path, before anything is written there.
        self.assertEqual(A.predecessors(self.path(2),two),[self.pin(one),self.pin(Path(str(one)+'.sha256'))])
        self.assertEqual(A.predecessors(one,self.docs[1]),[])
        self.seal(2,two)
        self.assertEqual(C.newest_root(self.live),self.path(2))
        for call in (lambda:A.predecessors(one,self.docs[1]),lambda:A.validate_body(one,self.docs[1]),
                     lambda:A.root_doc(one),lambda:A.verify_prefit(one,self.docs[1])):
            with self.assertRaisesRegex(ValueError,'Superseded LIVE root'):call()
        # The successor clears the chain and is refused only later, by its synthetic body.
        with self.assertRaisesRegex(ValueError,'live component'):A.validate_body(self.path(2),two)

    def test_a_predecessor_with_anything_in_its_slot_area_refuses_a_successor(self):
        one=self.seal(1);batch='a'*64
        artefacts=[C.slot(one,'fit',batch),Path(str(C.slot(one,'gate'))+'.sha256'),
                   Path(str(C.slot(one,'exposure'))+'.phase/attempts/000001/contract.json'),C.slot(one,'prefit'),
                   # The shared names of the dispatcher that sealed generation 1 (a09e02e94).
                   self.live/'fit'/f'{batch}.json.started.json',self.live/'gate-contract.json',
                   self.live/'exposure-contract.json.result.json',self.live/'pre-fit-evidence.json.sha256']
        for artefact in artefacts:
            with self.subTest(artefact=str(artefact.relative_to(self.live))):
                artefact.parent.mkdir(parents=True,exist_ok=True);artefact.write_text('{}')
                self.assertTrue(C.slot_entries(one))
                self.refuses('executed history',2,self.doc(2))
                with self.assertRaisesRegex(ValueError,'executed history'):A.seal_root(self.path(2),{**self.doc(2),**ROOT})
                self.assertFalse(self.path(2).exists())
                shutil.rmtree(self.live/'fit',ignore_errors=True)
                for p in self.live.iterdir():
                    if C.generation(p.name) is None and p.name!='rulings':shutil.rmtree(p) if p.is_dir() else p.unlink()
        A.predecessors(self.path(2),self.doc(2))
        # A sealed successor stays admitted only while its predecessor's area stays empty.
        self.seal(2);C.slot(one,'gate').write_text('{}')
        self.refuses('executed history',2,self.docs[2])

    def test_a_chain_of_three_resolves_to_the_newest(self):
        one=self.seal(1);two=self.seal(2);three=self.seal(3)
        self.assertEqual(C.newest_root(self.live),three)
        self.assertEqual(A.predecessors(three,self.docs[3]),
            [self.pin(two),self.pin(Path(str(two)+'.sha256')),self.pin(one),self.pin(Path(str(one)+'.sha256'))])
        for n in (1,2):
            self.refuses('Superseded LIVE root',n,self.docs[n])
        # Every link is re-read: a later change in generation 1's area refuses generation 3.
        (self.live/'fit').mkdir();(self.live/'fit'/('execution-root.'+'b'*64+'.json')).write_text('{}')
        self.refuses('executed history',3,self.docs[3])

    def test_a_torn_or_partial_successor_already_supersedes(self):
        one=self.seal(1);Path(str(self.path(2))+'.sha256').write_text('torn\n')
        self.refuses('Superseded',1,self.docs[1])
        self.assertEqual(C.newest_root(self.live),self.path(2))

    def test_forged_or_mismatched_records_refuse(self):
        self.seal(1);self.seal(2);self.git('commit','-q','--allow-empty','-m','later')
        def case(change):
            doc=copy.deepcopy(self.doc(3));change(doc);return doc
        def ruled(doc,text):
            doc['inputs'].remove(doc['supersedes']['ruling']['text'])
            pin=self.ruling(3,self.commits[2],text,name='forged.txt')
            doc['supersedes']['ruling']['text']=pin;doc['inputs'].append(pin)
        cases={
            'no record':('exact supersedes',lambda d:d.pop('supersedes')),
            'an extra field':('exact supersedes',lambda d:d['supersedes'].update(note='x')),
            'a missing field':('exact supersedes',lambda d:d['supersedes'].pop('unexecuted')),
            'another schema':('exact supersedes',lambda d:d['supersedes'].update(schema='w50-live-root-supersession-0')),
            'skipping a generation':('generation before it',lambda d:d['supersedes'].update(root=self.pin(self.path(1)))),
            'another content hash':('generation before it',lambda d:d['supersedes']['root'].update(sha256='0'*64)),
            'an absolute pin':('generation before it',lambda d:d['supersedes']['root'].update(path=str(self.path(2)))),
            'an abbreviated commit':('not a commit',lambda d:d['supersedes'].update(sealingCommit=self.commits[1][:9])),
            'an absent commit':('not a commit',lambda d:d['supersedes'].update(sealingCommit='0'*40)),
            'the predecessor\'s own predecessor\'s commit':('does not hold',lambda d:d['supersedes'].update(sealingCommit=self.commits[1])),
            'a later commit holding it':('did not introduce',lambda d:d['supersedes'].update(sealingCommit=self.git('rev-parse','HEAD'))),
            'a ruling outside the inputs':('prospectively bound',lambda d:d['inputs'].clear()),
            'a ruling without an id':('prospectively bound',lambda d:d['supersedes']['ruling'].update(id='ruling')),
            'a ruling under another id':('does not name',lambda d:d['supersedes']['ruling'].update(id='DL9z')),
            'a ruling naming another commit':('does not name',lambda d:ruled(d,f'DL9c (synthetic) names `{self.commits[1][:9]}`.\n')),
            'a ruling naming no commit':('does not name',lambda d:ruled(d,'DL9c (synthetic) names nothing.\n')),
            'a restated statement':('misstates',lambda d:d['supersedes']['unexecuted'].update(statement='nothing ran')),
            'a narrowed area':('misstates',lambda d:d['supersedes']['unexecuted']['slots'].pop()),
        }
        for name,(pattern,change) in cases.items():
            with self.subTest(name):self.refuses(pattern,3,case(change))
        A.predecessors(self.path(3),self.doc(3))
        # A ruling text changed after it was pinned, a predecessor whose seal changed, a first root
        # naming a predecessor and a name off the chain.
        doc=self.doc(3);Path(self.repo/doc['supersedes']['ruling']['text']['path']).write_text('DL9c changed\n')
        self.refuses('Changed or missing',3,doc)
        sidecar=Path(str(self.path(2))+'.sha256');sealed=sidecar.read_text();sidecar.write_text('0'*64+'  x\n')
        self.refuses('prospective seal',3,self.doc(3));sidecar.write_text(sealed)
        with self.assertRaisesRegex(ValueError,'Wrong live lifecycle root'):
            A.predecessors(self.live/'execution-root-1.json',self.docs[1])
        self.assertIsNone(C.generation('execution-root-2.draft.json'));self.assertIsNone(C.generation('execution-root-02.json'))

    def test_the_first_root_supersedes_nothing(self):
        self.seal(1);self.refuses('supersedes nothing',1,{**self.docs[1],'supersedes':{'schema':A.SUPERSESSION}})

    def test_another_repository_cannot_be_superseded(self):
        self.seal(1,{**self.doc(1),'repo':'/elsewhere'})
        self.refuses('another repository',2,self.doc(2))


class Slots(Chain):
    def test_slots_are_per_root_and_do_not_collide(self):
        batch='c'*64;roots=[self.path(n) for n in (1,2,20)]
        slots={root:[C.slot(root,'fit',batch),C.slot(root,'gate'),C.slot(root,'exposure'),C.slot(root,'prefit')] for root in roots}
        every=[p for paths in slots.values() for p in paths]
        self.assertEqual(len(set(every)),len(every))
        self.assertEqual([p.parent for p in slots[self.path(2)]],[self.live/'fit',self.live,self.live,self.live])
        for root,paths in slots.items():
            for p in paths:
                p.parent.mkdir(exist_ok=True);p.write_text('{}');Path(str(p)+'.sha256').write_text('x\n')
            entries=sorted(C.slot_entries(root))
            self.assertEqual(entries,sorted(paths+[Path(str(p)+'.sha256') for p in paths]))
            for other in roots:
                if other!=root:self.assertEqual(C.slot_entries(other),[])
            for p in paths:p.unlink();Path(str(p)+'.sha256').unlink()
        with self.assertRaisesRegex(ValueError,'batch hash'):C.slot(self.path(2),'fit','../x')


class DispatchEntries(Chain):
    """Every dispatcher entry refuses a superseded root before reading anything else."""
    def dispatcher(self):
        name='chain_test_dispatch_'+uuid.uuid4().hex;return module(name,'dispatch.py')

    def test_every_entry_refuses_a_superseded_root(self):
        one=self.seal(1);self.seal(2);output=self.repo.parent/(self.repo.name+'-output')
        contract=self.live/'execution-root.exposure-contract.json'
        Dm=self.dispatcher()
        calls={'root_doc':lambda:Dm.root_doc(one),'current_evidence':lambda:Dm.current_evidence(one),
               'verify_prefit':lambda:Dm.verify_prefit(one,self.docs[1]),
               'create_phase':lambda:Dm.create_phase(one,self.repo/'batch.json',output),
               'prepare_attempt':lambda:Dm.prepare_attempt(one,contract),
               'execute_attempt':lambda:Dm.execute_attempt(one,contract,{'ordinal':1}),
               'execute_analysis':lambda:Dm.execute_analysis(one,contract),
               'stop_stale_attempt':lambda:Dm.stop_stale_attempt(one,contract,'INSTRUMENT_FAULT')}
        for name,call in calls.items():
            with self.subTest(name),self.assertRaisesRegex(ValueError,'Superseded LIVE root'):call()
            self.assertIsNone(Dm._CORE)
        self.assertEqual(Dm.public_status(one,contract),{'schema':'w50-live-public-event-1','code':'REFUSED'})
        self.assertFalse(output.exists());self.assertEqual(C.slot_entries(one),[])

    def test_a_process_serving_a_root_refuses_it_once_a_successor_is_sealed(self):
        self.seal(1);two=self.seal(2);Dm=self.dispatcher()
        Dm._CORE={'root':str(two),'sha':Dm.sha(two)}
        self.assertIs(Dm._prepare(two),Dm._CORE)
        self.seal(3)
        with self.assertRaisesRegex(ValueError,'Superseded LIVE root'):Dm._prepare(two)

    def test_the_dispatchers_early_check_is_the_chains(self):
        Dm=self.dispatcher();self.assertEqual(Dm.ROOT_CHAIN.pattern,C.ROOT_CHAIN.pattern)
        names=['execution-root.json','execution-root.json.sha256','execution-root-2.json','execution-root-2.json.sha256',
               'execution-root-3.json.sha256','execution-root-10.json','execution-root-1.json','execution-root-2.draft.json',
               'root.json']
        for present in ([],names[:2],names[:4],names[:5],names[:6],names[6:]):
            for p in self.live.iterdir():
                if p.is_file():p.unlink()
            for name in present:(self.live/name).write_text('{}')
            for name in names:
                with self.subTest(present=present,name=name):
                    self.assertEqual(Dm._superseded(self.live/name),C.superseded(self.live/name))


class Lineage(Chain):
    """Supersession records of every evidence generation, written synthetically under FIT_REL."""
    def put(self,relative,value):
        path=self.repo/A.FIT_REL/relative;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(value if isinstance(value,str) else json.dumps(value));return path

    def superseded(self,relative):return self.pin(self.put(relative,{'synthetic':relative}))

    def generations(self,records=('owner/r2','completion/registered-2','owner/r3','completion/registered-3','prefit-proofs-r3')):
        """One record per generation; each supersedes one file, and registered-3 also an archive
        whose manifest names, by content, the inventory it archived."""
        self.files={}
        for folder in records:
            target=folder.replace('/','-')+'/stale.json';self.files[folder]=self.superseded('old/'+target)
            superseded={'stale':self.files[folder]}
            if folder=='completion/registered-3':
                inventory=self.superseded('live-inputs/completed-references-r2.json');self.files['inventory']=inventory
                manifest=self.put('completion/registered-2/evidence/archive.json',
                                  {'schema':'w50-reference-assembly-archive-1','completedReferences':{'original':inventory}})
                superseded['archive']=self.pin(manifest)
            self.put(folder+'/supersedes.json',{'schema':'synthetic','superseded':superseded})

    def evidence(self,*extra,proof=()):
        inventory=self.superseded('live-inputs/completed-references-r3.json')
        completion=self.pin(self.put('prefit-proofs-r3/referenceCompletion.json',{'sources':[inventory,*proof]}))
        return {'evidence':{'referenceCompletion':completion},'references':inventory,'sources':list(extra)}

    def test_every_generation_of_every_series_is_read(self):
        self.generations()
        self.assertEqual(A.supersession_records(self.repo),['owner/r2/supersedes.json','owner/r3/supersedes.json',
            'completion/registered-2/supersedes.json','completion/registered-3/supersedes.json','prefit-proofs-r3/supersedes.json'])
        A.prefit_lineage(self.repo,self.evidence())
        for name,item in self.files.items():
            with self.subTest(name):
                with self.assertRaisesRegex(ValueError,'evidence pins evidence a recorded recovery superseded'):
                    A.prefit_lineage(self.repo,self.evidence(item))
                with self.assertRaisesRegex(ValueError,'referenceCompletion pins evidence'):
                    A.prefit_lineage(self.repo,self.evidence(proof=[item]))
        # The archived inventory refuses by content, under any name.
        moved={'path':'elsewhere.json','sha256':self.files['inventory']['sha256']}
        with self.assertRaisesRegex(ValueError,'superseded'):A.prefit_lineage(self.repo,self.evidence(moved))

    def test_a_gap_a_missing_base_or_an_empty_record_refuses(self):
        self.generations(('owner/r2','completion/registered-2','owner/r4'))
        with self.assertRaisesRegex(ValueError,'missing from its series'):A.supersession_records(self.repo)
        self.put('owner/r3/supersedes.json',{'superseded':{}});A.supersession_records(self.repo)
        (self.repo/A.FIT_REL/'owner/r2/supersedes.json').unlink()
        with self.assertRaisesRegex(ValueError,'r2 supersession records are required'):A.supersession_records(self.repo)
        self.put('owner/r2/supersedes.json',{'superseded':'nothing'})
        with self.assertRaisesRegex(ValueError,'names nothing superseded'):A.prefit_lineage(self.repo,self.evidence())


class PrefitBinding(Lineage):
    """verify_prefit reads each root's own evidence slot, and its lineage refuses every
    superseded root of the chain, so evidence written for one root never stands for another."""
    def setUp(self):
        super().setUp();self.generations(('owner/r2','completion/registered-2'))
        stub='def validate_exemptions(*a,**k):pass\ndef validate_completion(*a,**k):pass\ndef validate_proof(*a,**k):pass\n'
        (self.live/'prefit.py').write_text(stub)
        self.fields={'partTwo':self.superseded('part-two.json'),'references':self.superseded('references.json'),
                     'manifest':self.superseded('manifest.json'),'closure':{'sources':{},'environment':{}},
                     'reportedKeys':[],'emptySupportKeys':[],'ownerBudgetKeys':[],'ownerContracts':None}
        self.one=self.seal(1,{**self.doc(1),**self.fields})
        self.two=self.seal(2,{**self.doc(2),**self.fields})

    def write(self,root,*extra,proof=()):
        evidence=self.evidence(proof=proof)
        sources=[self.pin(root),self.pin(Path(str(root)+'.sha256')),*extra]
        others={k:self.pin(self.put(f'proofs/{k}.json','{}')) for k in D.PROOFS if k!='referenceCompletion'}
        value={'partTwoSha256':self.fields['partTwo']['sha256'],'sources':sources,'executionClosure':self.fields['closure'],
               'references':evidence['references'],'evidence':{**evidence['evidence'],**others}}
        target=C.slot(root,'prefit')
        for path in (target,Path(str(target)+'.sha256')):path.unlink(missing_ok=True)
        D.write_sealed(target,value);return target

    def test_evidence_for_one_root_never_stands_for_another(self):
        slot=self.write(self.two)
        self.assertEqual(A.verify_prefit(self.two,self.docs[2]),self.pin(slot))
        # The superseded root, its seal, its bytes under another name, and a proof pinning it.
        copy_of_one=self.put('copy-of-one.json',self.one.read_text())
        for name,extra in (('root',self.pin(self.one)),('seal',self.pin(Path(str(self.one)+'.sha256'))),
                           ('content',self.pin(copy_of_one))):
            self.write(self.two,extra)
            with self.subTest(name),self.assertRaisesRegex(ValueError,'evidence pins a superseded LIVE root'):
                A.verify_prefit(self.two,self.docs[2])
        self.write(self.two,proof=[self.pin(self.one)])
        with self.assertRaisesRegex(ValueError,'referenceCompletion pins a superseded LIVE root'):
            A.verify_prefit(self.two,self.docs[2])
        # Root 1's evidence copied into root 2's slot names the wrong root.
        self.write(self.one);slot=C.slot(self.two,'prefit')
        for path in (slot,Path(str(slot)+'.sha256')):path.unlink()
        D.write_sealed(slot,D.sealed(C.slot(self.one,'prefit')))
        with self.assertRaisesRegex(ValueError,'executed history'):A.verify_prefit(self.two,self.docs[2])
        for path in C.slot_entries(self.one):path.unlink()
        with self.assertRaisesRegex(ValueError,'did not prospectively pin execution root'):A.verify_prefit(self.two,self.docs[2])
        # And the reverse: the superseded root admits no evidence at all.
        with self.assertRaisesRegex(ValueError,'Superseded LIVE root'):A.verify_prefit(self.one,self.docs[1])

    def test_evidence_at_the_shared_name_is_not_read_and_refuses_the_successor(self):
        self.write(self.two);shared=self.live/'pre-fit-evidence.json'
        D.write_sealed(shared,D.sealed(C.slot(self.two,'prefit')))
        with self.assertRaisesRegex(ValueError,'executed history'):A.verify_prefit(self.two,self.docs[2])
        for path in (shared,Path(str(shared)+'.sha256')):path.unlink()
        A.verify_prefit(self.two,self.docs[2])


if __name__=='__main__':unittest.main()
