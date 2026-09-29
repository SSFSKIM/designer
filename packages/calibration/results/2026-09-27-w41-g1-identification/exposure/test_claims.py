"""Scope and identity regressions: committed synthetic pixels, public metadata only."""
from copy import deepcopy
import unittest
from PIL import Image
import runner
from test_runner import ExposureTests, ProductionScopeTests, ALL_ENDPOINTS
from test_domain import DOMAIN, evidence


class PartialScopeTests(ExposureTests):
    # The inherited lifecycle tests also run with the mandatory all-endpoint declaration.
    def refreeze(self):
        self.commit()
        self.manifest = runner.freeze(self.root, self.wave, self.candidates,
            config='config.json', scorer='scorer.py', declaration='declaration.txt',
            closure='closure.json', dry_cells=self.cells)
        self.put('frozen.json', self.manifest)
        self.commit()

    def partial(self):
        # Deliberately cross scheme, pose and scale. Never infer endpoint from filename.
        allowed = runner.cells_for(self.wave, ('calibration',), True)
        profiles = {p['key']: p['colorScheme'] for p in self.wave.spec['profiles']}
        def endpoint(c):
            profile, sid = c.split('/')
            return (profiles[profile], self.wave.scenes[sid]['state'])
        self.cells = [next(c for c in allowed if endpoint(c) == (scheme, pose)
                           and f'-{scale}x-' in c)
                      for scheme, pose, scale in [('light','inactive',1), ('light','inactive',2),
                                                 ('light','rest',1), ('dark','inactive',2)]]
        evidence(self, self.cells)
        self.claimed = self.cells[:2]
        self.unclaimed = self.cells[2:]
        self.put('claim.json', {'endpoints': [{'colorScheme':'light','activation':'inactive'}], 'domain':DOMAIN,'numericalDomain':'uniform-backdrop', 'renderedDeepDomain':'uniform-backdrop'})
        self.put('predictions.json', {'cells': {c:[80,90,100] for c in self.cells}})
        images = {c:{'png':'0.png','projection':'0.json'} for c in self.cells}
        self.put('rendered.json', {'cells':images})
        self.put('baseline.json', {'cells':{c:images[c] for c in self.unclaimed}})
        self.candidates[0]['identityBaseline'] = 'baseline.json'
        rows = {c:True if c in self.claimed else {
            'status':'not claimed (identity)', 'passes':None,
            'score':{'status':'measured','passes':False,'worstResidualCodes':25}}
            for c in self.cells}
        self.put('survival.json', {'numerical':rows,'rendered':rows,
                                 'veto':{c:True for c in self.cells}})
        self.refreeze()

    def test_scope_is_explicit_committed_and_schema_bound(self):
        self.assertIn('claim.json', self.manifest['files'])
        self.assertTrue(any(p.endswith('/exposure/manifest.schema.json') for p in self.manifest['files']))
        self.assertEqual(self.manifest['schema'], 'w41-renderer-exposure-2')
        self.candidates[0].pop('claimScope')
        with self.assertRaisesRegex(ValueError, 'claimScope'):
            self.refreeze()

    def test_no_selective_cells_scales_empty_duplicate_or_unknown_endpoints(self):
        for scope in ({'endpoints':[]}, {'endpoints':ALL_ENDPOINTS,'cells':self.cells},
                      {'endpoints':[ALL_ENDPOINTS[0],ALL_ENDPOINTS[0]]},
                      {'endpoints':[{'colorScheme':'light','activation':'rest'}]},
                      {'endpoints':[dict(ALL_ENDPOINTS[0],scale=1)]}):
            with self.subTest(scope=scope):
                self.put('claim.json', dict(scope, domain=DOMAIN, numericalDomain='uniform-backdrop', renderedDeepDomain='uniform-backdrop'))
                with self.assertRaisesRegex(ValueError, 'claim scope'):
                    self.refreeze()

    def test_unclaimed_misses_retained_but_never_passes_or_candidate_failures(self):
        self.partial()
        def scores(request):
            result = self.score(request)
            for kind in ('numerical','rendered'):
                for cell in self.unclaimed:
                    result['standin'][kind][cell].update(passes=False,worstResidualCodes=25)
            return result
        result = self.run_exposure(score=scores)
        for kind in ('numerical','rendered'):
            self.assertEqual(result['coverage']['standin'][kind],
                {'measured':2,'censored':0,'total':2,'fraction':1.0,'scoredTotal':4,'notClaimed':2})
            for cell in self.unclaimed:
                row = result['assessments']['standin'][kind][cell]
                self.assertEqual(row['status'], 'not claimed (identity)')
                self.assertIsNone(row['passes'])
                self.assertEqual(row['score']['worstResidualCodes'],25)
                self.assertFalse(result['scores']['standin'][kind][cell]['passes'])
        self.assertEqual(len(runner.load(self.score_report)['scores']['standin']['rendered']),4)

    def test_claimed_failure_still_spends_and_preserves_all_scores(self):
        self.partial()
        def fail(request):
            result = self.score(request)
            result['standin']['rendered'][self.claimed[1]]['passes'] = False
            return result
        with self.assertRaisesRegex(ValueError, 'closure failed'):
            self.run_exposure(score=fail)
        self.assertEqual(self.events(), ['begin','failed'])
        self.assertEqual(len(runner.load(self.score_report)['scores']['standin']['rendered']),4)

    def test_claimed_censor_constraint_failure_cannot_hide_behind_scope(self):
        self.partial()
        def fail(request):
            result = self.score(request)
            result['standin']['numerical'][self.claimed[0]] = {
                'status':'UNMEASURED','reason':'censored','passes':None,'constraintsPass':False}
            return result
        with self.assertRaisesRegex(ValueError, 'closure failed'):
            self.run_exposure(score=fail)

    def test_identity_baseline_payload_and_projection_must_equal_candidate(self):
        self.partial()
        baseline = runner.load(self.root/'baseline.json')
        Image.new('RGB',(2,2),(81,90,100)).save(self.root/'different.png')
        baseline['cells'][self.unclaimed[0]]['png']='different.png'
        self.put('baseline.json',baseline)
        with self.assertRaisesRegex(ValueError, 'identity baseline'):
            self.refreeze()
        baseline['cells'][self.unclaimed[0]]['png']='0.png'
        self.put('different.json',{'rgb':[81,90,100]})
        baseline['cells'][self.unclaimed[0]]['projection']='different.json'
        self.put('baseline.json',baseline)
        with self.assertRaisesRegex(ValueError, 'identity baseline'):
            self.refreeze()

    def test_unclaimed_calibration_cannot_be_labeled_true_or_skip_veto(self):
        self.partial()
        original=runner.load(self.root/'survival.json')
        for kind in ('numerical','rendered','veto'):
            survival=deepcopy(original)
            survival[kind][self.unclaimed[0]]=False if kind=='veto' else True
            self.put('survival.json',survival)
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.refreeze()

    def test_unclaimed_heldout_veto_is_independent_of_fidelity_claim(self):
        self.partial()
        def fail(request):
            result = self.score(request)
            result['standin']['rendered'][self.unclaimed[0]]['vetoPass'] = False
            return result
        with self.assertRaisesRegex(ValueError, 'per-bin veto'):
            self.run_exposure(score=fail)
        self.assertEqual(len(runner.load(self.score_report)['scores']['standin']['rendered']), 4)

    def test_added_g1_import_source_refuses_before_begin(self):
        self.put('packages/calibration/results/2026-09-27-w41-g1-identification/scorer_helper.py',
                 'NEW_INPUT = 1')
        self.commit()
        with self.assertRaisesRegex(ValueError, 'source inventory'):
            self.run_exposure()
        self.assertFalse(self.log.exists())

    def test_changed_schema_refuses_before_begin(self):
        name = next(p for p in self.manifest['files'] if p.endswith('/manifest.schema.json'))
        self.put(name, {'changed': True})
        self.commit()
        with self.assertRaisesRegex(ValueError, 'frozen artifact changed'):
            self.run_exposure()
        self.assertFalse(self.log.exists())


    def test_unclaimed_scores_still_require_complete_valid_measurements(self):
        self.partial()
        def omit(request):
            result=self.score(request)
            del result['standin']['numerical'][self.unclaimed[0]]
            return result
        with self.assertRaisesRegex(ValueError,'coverage mismatch'):
            self.run_exposure(score=omit)


class FullMembershipClaimsTests(ProductionScopeTests):
    def test_rendered_deep_domain_is_explicit_and_separate(self):
        scope=runner.load(self.root/'claim.json')
        scope.pop('renderedDeepDomain',None)
        self.put('claim.json',scope)
        self.commit()
        with self.assertRaisesRegex(ValueError,'renderedDeepDomain'):
            self.freeze()

    def test_structured_rendered_deep_is_diagnostic_but_veto_and_pixels_remain_bound(self):
        structured=[c for c in self.rendered if
            self.wave.spec['backgrounds'][self.wave.scenes[c.split('/')[1]]['background']]['kind']!='solid']
        self.assertTrue(structured)
        self.assertFalse(any(self.wave.roles[c.split('/')[1]]=='holdout' for c in structured))
        survival=runner.load(self.root/'survival.json')
        for cell in structured:
            survival['rendered'][cell]={'status':'not claimed (structured backdrop)',
                'passes':None,'score':{'status':'measured','passes':False,'worstResidualCodes':25}}
        self.put('survival.json',survival)
        self.commit()
        manifest=self.freeze()
        self.assertEqual(len(manifest['renderedCells']),600)
        self.assertEqual(len(survival['veto']),536)
        self.assertEqual(manifest['identityEquality']['standin'],{})
        for cell in structured:
            self.assertIn(cell,manifest['renderedCells'])
            self.assertNotIn('diagnostic',survival['rendered'][cell]['score'])
        # Actual rendered observations, not S0 numerical predictions. A failing
        # absolute-deep score is retained; a failing full veto is still fatal.
        scores={'standin':{'numerical':{},'rendered':{c:{'status':'measured',
            'passes':False,'vetoPass':True,'worstResidualCodes':25} for c in structured}}}
        counts,assessments=runner.aggregate(self.wave,scores,{'standin':self.candidates[0]},
            manifest['claimScopes'],[],structured)
        self.assertEqual(counts['standin']['rendered']['notClaimed'],len(structured))
        self.assertEqual(assessments['standin']['rendered'][structured[0]]['score']['worstResidualCodes'],25)
        scores['standin']['rendered'][structured[0]]['vetoPass']=False
        with self.assertRaisesRegex(ValueError,'per-bin veto'):
            runner.aggregate(self.wave,scores,{'standin':self.candidates[0]},
                manifest['claimScopes'],[],structured)
        # The same miss on a uniform claimed endpoint still fails closure.
        uniform=next(c for c in self.rendered if c not in structured)
        scores['standin']['rendered']={uniform:{'status':'measured','passes':False,'vetoPass':True}}
        with self.assertRaisesRegex(ValueError,'closure failed'):
            runner.aggregate(self.wave,scores,{'standin':self.candidates[0]},
                manifest['claimScopes'],[],[uniform])
        for name in ('veto','rendered'):
            changed=deepcopy(survival)
            changed[name][structured[0]]=False if name=='veto' else True
            self.put('survival.json',changed)
            self.commit()
            with self.subTest(kind=name),self.assertRaises(ValueError):
                self.freeze()

    def test_numerical_uniform_domain_is_explicit_not_assumed(self):
        scope=runner.load(self.root/'claim.json')
        scope.pop('numericalDomain',None)
        self.put('claim.json',scope)
        self.commit()
        with self.assertRaisesRegex(ValueError,'numericalDomain'):
            self.freeze()

    def test_structured_numerical_diagnostic_is_not_admission_or_shader_disable(self):
        manifest=self.freeze()
        structured=[c for c in self.numerical if
            self.wave.spec['backgrounds'][self.wave.scenes[c.split('/')[1]]['background']]['kind']!='solid']
        self.assertTrue(structured)
        self.assertFalse(any(self.wave.roles[c.split('/')[1]]=='holdout' for c in structured))
        survival=runner.load(self.root/'survival.json')
        for cell in structured:
            self.assertEqual(survival['numerical'][cell]['status'],'not claimed (structured backdrop)')
            self.assertEqual(survival['numerical'][cell]['score']['diagnostic'],'S0')
            self.assertIn(cell,manifest['numericalCells'])
            if cell in self.rendered:
                self.assertEqual(survival['rendered'][cell]['status'],
                                 'not claimed (structured backdrop)')
                self.assertNotIn('diagnostic',survival['rendered'][cell]['score'])
                self.assertIs(survival['veto'][cell],True)
        survival['numerical'][structured[0]]=True
        self.put('survival.json',survival)
        self.commit()
        with self.assertRaisesRegex(ValueError,'not claimed'):
            self.freeze()

    def test_partial_claim_retains_every_cell_and_freezes_blind_heldout_identity(self):
        self.put('claim.json',{'endpoints':[{'colorScheme':'light','activation':'inactive'}], 'domain':DOMAIN,'numericalDomain':'uniform-backdrop', 'renderedDeepDomain':'uniform-backdrop'})
        def claimed(cell):
            profile,sid=cell.split('/')
            scheme=next(p['colorScheme'] for p in self.wave.spec['profiles'] if p['key']==profile)
            return scheme=='light' and self.wave.scenes[sid]['state']=='inactive'
        survival=runner.load(self.root/'survival.json')
        for kind in ('numerical','rendered'):
            for cell in survival[kind]:
                if not claimed(cell):
                    survival[kind][cell]={'status':'not claimed (identity)','passes':None,
                                         'score':{'status':'measured','passes':False}}
        self.put('survival.json',survival)
        images=runner.load(self.root/'rendered.json')['cells']
        self.put('baseline.json',{'cells':{c:images[c] for c in self.rendered if not claimed(c)}})
        self.candidates[0]['identityBaseline']='baseline.json'
        self.commit()
        manifest=self.freeze()
        self.assertEqual((len(manifest['numericalCells']),len(manifest['renderedCells'])),(648,600))
        heldout = {kind: [c for c in cells if self.wave.roles[c.split('/')[1]] == 'holdout']
                   for kind, cells in self.expected.items()}
        scores = {'standin': {kind: {c: {'status':'measured', 'passes':claimed(c),
                                        'vetoPass':True} for c in cells}
                             for kind, cells in heldout.items()}}
        counts, rows = runner.aggregate(self.wave, scores, {'standin':self.candidates[0]},
            manifest['claimScopes'], heldout['numerical'], heldout['rendered'])
        self.assertEqual(counts['standin']['numerical'],
            {'measured':18,'censored':0,'total':18,'fraction':1.0,'scoredTotal':72,'notClaimed':54})
        self.assertEqual(counts['standin']['rendered'],
            {'measured':16,'censored':0,'total':16,'fraction':1.0,'scoredTotal':64,'notClaimed':48})
        identity=manifest['identityEquality']['standin']
        self.assertEqual(len(identity),450)
        self.assertEqual(sum(self.wave.roles[c.split('/')[1]]=='holdout' for c in identity),48)
        for cell,record in identity.items():
            self.assertEqual(record['baselinePngSha256'],record['candidatePngSha256'])
        heldout=next(c for c in identity if self.wave.roles[c.split('/')[1]]=='holdout')
        baseline=runner.load(self.root/'baseline.json')
        del baseline['cells'][heldout]
        self.put('baseline.json',baseline)
        self.commit()
        with self.assertRaisesRegex(ValueError,'identity baseline coverage mismatch'):
            self.freeze()


if __name__=='__main__':
    unittest.main()


def load_tests(loader, standard_tests, pattern):
    # The original 41 regressions run once in test_runner; only new methods here.
    return unittest.TestSuite(loader.loadTestsFromName(name, cls)
        for cls in (PartialScopeTests, FullMembershipClaimsTests)
        for name in cls.__dict__ if name.startswith('test_'))
