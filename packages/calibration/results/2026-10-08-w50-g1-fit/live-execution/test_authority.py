import ast
import copy
import hashlib
import importlib.util
import inspect
from pathlib import Path
import re
import tempfile
import textwrap
import unittest
import types
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('authority',H/'authority.py');A=importlib.util.module_from_spec(s);s.loader.exec_module(A)
class Authority(unittest.TestCase):
    def test_initializer_is_not_a_post_capture_fitter_placeholder(self):
        initializer=types.SimpleNamespace(initialize=lambda:None,assemble=lambda:None,bind_arguments=lambda:None)
        A.instrument_interface('initializer',initializer)
        with self.assertRaises(ValueError):A.instrument_interface('fit',initializer)
        with self.assertRaises(ValueError):A.instrument_interface('capture',types.SimpleNamespace(capture=lambda:None,verify=lambda:None))
    def test_native_role_must_carry_its_read_only_pre_start_admission(self):
        prepared=types.SimpleNamespace(prepare=lambda:None,verify=lambda:None)
        with self.assertRaisesRegex(ValueError,'role interface'):A.instrument_interface('native',prepared)
        A.instrument_interface('native',types.SimpleNamespace(admit=lambda:None,**vars(prepared)))
    def test_owner_role_must_carry_its_metadata_only_admission(self):
        evaluated=types.SimpleNamespace(evaluate=lambda:None)
        with self.assertRaisesRegex(ValueError,'role interface'):A.instrument_interface('owner',evaluated)
        A.instrument_interface('owner',types.SimpleNamespace(admit=lambda:None,**vars(evaluated)))
    def test_fit_role_must_export_the_record_the_gate_rederives(self):
        evaluated=types.SimpleNamespace(evaluate=lambda:None)
        with self.assertRaisesRegex(ValueError,'role interface'):A.instrument_interface('fit',evaluated)
        A.instrument_interface('fit',types.SimpleNamespace(fit_record=lambda:None,**vars(evaluated)))
    def test_missing_real_components_cannot_form_live_root(self):
        for roles in ({},{'fit':{}},{r:{} for r in A.ROLES}):
            with self.assertRaises(ValueError):A.instrument_shape(roles)
    def test_prospective_components_have_both_source_and_config_not_status_placeholders(self):
        p={'path':'source.py','sha256':'a'*64};c={'path':'config.json','sha256':'b'*64}
        roles={r:{'entrypoint':p,'config':c} for r in A.ROLES};A.instrument_shape(roles)
        for field in ('entrypoint','config'):
            broken={**roles,'judge':{**roles['judge'],field:{'status':'PENDING'}}}
            with self.assertRaises(ValueError):A.instrument_shape(broken)
    def test_root_refuses_singular_current_aliases_before_any_other_admission(self):
        with tempfile.TemporaryDirectory() as t:
            repo=Path(t).resolve()
            path=repo/'packages/calibration/results/2026-10-08-w50-g1-fit/live-execution/execution-root.json'
            doc={'repo':str(repo),'schema':'w50-g1-execution-root-1','lifecycle':'logical-phase-attempts-1',
                 'quarantine':'instrument-api-role-discipline-1'}
            with self.assertRaisesRegex(ValueError,'live component'):A.validate_body(path,doc)
            for alias in ('currentInstrument','currentResults'):
                with self.subTest(alias=alias),self.assertRaisesRegex(ValueError,'Wrong live lifecycle root'):
                    A.validate_body(path,{**doc,alias:{'path':'x','sha256':'a'*64}})


class Rebound(ast.NodeTransformer):
    """A LIVE copy's body as the original's: D.x read as x, each live expression as the original's.
    `rewrites` counts, per live expression, the occurrences replaced, so a proof can require that
    every one was."""
    def __init__(self,**expressions):
        self.map={ast.dump(ast.parse(k,mode='eval').body):(k,ast.parse(v,mode='eval').body) for k,v in expressions.items()}
        self.rewrites=dict.fromkeys(expressions,0)
    def visit(self,node):
        if ast.dump(node) in self.map:
            live,original=self.map[ast.dump(node)];self.rewrites[live]+=1
            return ast.copy_location(copy.deepcopy(original),node)
        node=self.generic_visit(node)
        if isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name) and node.value.id=='D':
            return ast.copy_location(ast.Name(node.attr,node.ctx),node)
        return node


def body_of(source):
    node=ast.parse(textwrap.dedent(source)).body[0];node.name='f'
    if isinstance(node.body[0],ast.Expr) and isinstance(node.body[0].value,ast.Constant):node.body=node.body[1:]
    return node


def body(function):return body_of(inspect.getsource(function))


SHARED='pre-fit-evidence.json';SITE="C.slot(path, 'prefit')";ORIGINAL="directory / '"+SHARED+"'"


def rebound_prefit(source):
    """The live _verify_prefit as current3's, once every occurrence is proven rebound. Comparing
    trees after the rewrite is one-sided: a site that still holds the ORIGINAL expression (a partial
    revert) compares equal whatever the rewrite did. So the live copy must name no shared file
    before the rewrite, and the rewrite must have met both sites, the read and the returned pin."""
    live=body_of(source)
    if any(isinstance(n,ast.Constant) and n.value==SHARED for n in ast.walk(live)):
        raise AssertionError('The live copy still names the shared '+SHARED)
    rebound=Rebound(**{SITE:ORIGINAL});live=rebound.visit(live)
    if rebound.rewrites[SITE]!=2:raise AssertionError(f'The evidence slot was rebound at {rebound.rewrites[SITE]} sites, not 2')
    return live


class PrefitCopy(unittest.TestCase):
    def test_live_verify_prefit_is_current3s_with_only_the_evidence_slot_rebound(self):
        """DL5o: each root reads and pins its own pre-fit evidence; nothing else differs."""
        live=rebound_prefit(inspect.getsource(A._verify_prefit))
        self.assertEqual(ast.dump(live),ast.dump(body(A.D.verify_prefit)))
        self.assertIs(A._verify_prefit.__globals__['C'],A.C)
    def test_a_site_reverted_to_the_shared_name_is_caught_though_the_trees_still_compare_equal(self):
        source=inspect.getsource(A._verify_prefit)
        for site in ("D.sealed("+SITE+")","D.pin(repo, "+SITE+")"):
            reverted=source.replace(site,site.replace(SITE,ORIGINAL));self.assertNotEqual(reverted,source)
            with self.subTest(site=site):
                # What the one-sided comparison accepted: the surviving site is rebound, the reverted one already matches.
                rebound=Rebound(**{SITE:ORIGINAL});live=rebound.visit(body_of(reverted))
                self.assertEqual(ast.dump(live),ast.dump(body(A.D.verify_prefit)));self.assertEqual(rebound.rewrites[SITE],1)
                with self.assertRaisesRegex(AssertionError,'still names the shared'):rebound_prefit(reverted)
    def test_a_rewrite_that_misses_a_site_is_caught_by_the_count_alone(self):
        source=inspect.getsource(A._verify_prefit)
        with self.assertRaisesRegex(AssertionError,'at 1 sites, not 2'):rebound_prefit(source.replace("D.pin(repo, "+SITE+")","D.pin(repo, path)"))


def pin(name):return {'path':name,'sha256':hashlib.sha256(name.encode()).hexdigest()}


class CurrentAuthority(unittest.TestCase):
    def setUp(self):
        roots=[{'pin':pin('current3-root'),'document':{}},{'pin':pin('canonical3-root'),'document':{}}]
        results=[{'pin':pin('current3-result')},{'pin':pin('canonical3-result')}]
        chain=[pin('chain-a'),pin('chain-b'),pin('chain-c')];baseline=[pin('baseline-025'),pin('baseline-05')]
        self.current={'roots':roots,'resultDocuments':results,'chainPins':chain,'candidates':baseline}
        self.doc={'currentComposition':pin('composition'),'currentEvidence':pin('evidence'),
                  'references':pin('references'),'baselineDocuments':copy.deepcopy(baseline)}
        self.doc['inputs']=[self.doc['currentComposition'],self.doc['currentEvidence'],*copy.deepcopy(chain)]
        self.evidence={'schema':'w50-completed-current-evidence-2','status':'EVIDENCE_ONLY',
            'currentComposition':self.doc['currentComposition'],'currentInstruments':[r['pin'] for r in roots],
            'currentResults':[r['pin'] for r in results],'chainPins':copy.deepcopy(chain),
            'originals':{'references':self.doc['references']}}
    def test_exact_ordered_composition_is_admitted(self):
        A.current_authority(self.doc,self.evidence,self.current)
    def test_reordered_missing_or_extra_chain_entries_refuse(self):
        for field in ('currentInstruments','currentResults','chainPins'):
            for mutation in ('reordered','missing','extra'):
                evidence=copy.deepcopy(self.evidence);value=evidence[field]
                if mutation=='reordered':value.reverse()
                elif mutation=='missing':value.pop()
                else:value.append(pin('foreign'))
                with self.subTest(field=field,mutation=mutation),self.assertRaisesRegex(ValueError,'composed authority'):
                    A.current_authority(self.doc,evidence,self.current)
    def test_chain_pin_absent_from_root_inputs_refuses(self):
        for item in (self.doc['currentComposition'],self.doc['currentEvidence'],self.current['chainPins'][1]):
            doc=copy.deepcopy(self.doc);doc['inputs'].remove(item)
            with self.subTest(item=item['path']),self.assertRaisesRegex(ValueError,'omitted from root'):
                A.current_authority(doc,self.evidence,self.current)
    def test_flattened_singular_current_instrument_refuses(self):
        evidence={**self.evidence,'currentInstrument':self.evidence['currentInstruments'][0]}
        with self.assertRaisesRegex(ValueError,'composed authority'):A.current_authority(self.doc,evidence,self.current)


class PrefitLineage(unittest.TestCase):
    """Second pre-seal review P2, on the committed proofs and supersession records: the newest
    generation of each of the ten standing proofs, and the inventory its referenceCompletion
    completes, pass; every older generation of a rebuilt proof, the superseded inventory and a
    completion that names another inventory refuse. Generations are read from the tree
    (prefit-proofs, prefit-proofs-r2, ...), so a later cascade (DL5o's r3) is held to the same
    statement. Only proof and record JSON is read."""
    REPO=H.parents[4];FIT='packages/calibration/results/2026-10-08-w50-g1-fit/'
    KINDS=[k for k in A.D.PROOFS if k not in ('executionClosure','independentReview')]
    def folders(self,kind):
        found=[p for p in (self.REPO/self.FIT).glob('prefit-proofs*/'+kind+'.json') if re.fullmatch(r'prefit-proofs(-r[0-9]+)?',p.parent.name)]
        return [p.parent.name for p in sorted(found,key=lambda p:int(p.parent.name.rpartition('-r')[2] or 1) if '-r' in p.parent.name else 1)]
    def proof(self,folder,kind):return A.D.pin(self.REPO,self.REPO/self.FIT/folder/(kind+'.json'))
    def evidence(self,**folders):
        proofs={k:self.proof(folders.get(k,self.folders(k)[-1]),k) for k in self.KINDS}
        # The inventory the NEWEST completion completes, whichever generation a case substitutes.
        completion=A.D.load(self.REPO/self.proof(self.folders('referenceCompletion')[-1],'referenceCompletion')['path'])
        [references]=[p for p in completion['sources'] if re.search(r'live-inputs/completed-references(-r[0-9]+)?\.json$',p['path'])]
        return {'evidence':proofs,'references':references,'sources':[]}
    def test_the_rebuilt_proofs_and_their_inventory_pass(self):
        self.assertEqual(sorted(self.KINDS),sorted(['nativeArchive','repeatBar','referenceCompletion','dark05Bands',
            'active05ScratchBaselines','identityDigestsGoldens','numericalRehearsal','shaderCpuAgreement',
            'negativeNeutralDiagnostic','newBedRendererAdapter']))
        self.assertTrue(all(self.folders(k) for k in self.KINDS))
        A.prefit_lineage(self.REPO,self.evidence())
    def test_each_superseded_proof_refuses(self):
        older=[(k,f) for k in self.KINDS for f in self.folders(k)[:-1]]
        self.assertTrue({'referenceCompletion','repeatBar','dark05Bands','active05ScratchBaselines'}<={k for k,_ in older})
        for kind,folder in older:
            # A record that names the proof file itself refuses it as the evidence's own pin (r3's
            # prefit-proofs-r3/supersedes.json); one that names only what it pins refuses it as the proof's.
            with self.subTest(kind=kind,folder=folder),self.assertRaisesRegex(ValueError,'(evidence|'+kind+') pins evidence a recorded recovery superseded'):
                A.prefit_lineage(self.REPO,self.evidence(**{kind:folder}))
    def test_the_superseded_inventory_and_another_inventory_refuse(self):
        old=A.D.load(self.REPO/self.FIT/'prefit-proofs/repeatBar.json')
        stale=next(p for p in old['sources'] if p['path'].endswith('live-inputs/completed-references.json'))
        with self.assertRaisesRegex(ValueError,'evidence pins evidence a recorded recovery superseded'):
            A.prefit_lineage(self.REPO,{**self.evidence(),'references':stale})
        with self.assertRaisesRegex(ValueError,'superseded'):
            A.prefit_lineage(self.REPO,{**self.evidence(),'sources':[{'path':self.FIT+'completion/registered/run.py','sha256':'0'*64}]})
        other={'path':self.FIT+'live-inputs/completed-references-r9.json','sha256':'1'*64}
        with self.assertRaisesRegex(ValueError,'own inventory'):A.prefit_lineage(self.REPO,{**self.evidence(),'references':other})

if __name__=='__main__':unittest.main()
