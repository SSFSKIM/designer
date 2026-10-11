"""DL5 authority cannot drift between admission, the marker, and publication.

All documents here are small controlled metadata; no historical gate payload is opened.
"""
import copy
from pathlib import Path
import runpy
import tempfile
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
R = runpy.run_path(str(HERE/'root.py'))
S = runpy.run_path(str(HERE/'static.py'))
RUN = R['source'](HERE/'run.py', 'w51_dl5_lifecycle_run')


class PolicyFixture(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name).resolve()
        self.key = ['p', 'webgpu', 's', 'T1-full-silhouette']
        self.population = self.put('population.json', {'statisticKeys':[self.key],
            'physicalCells':[self.key[:3]], 'physicalCount':1, 'statisticCount':1})
        self.source_pin = self.put('scientific.json', {'native':.25, 'current':.375})
        member = {'key':self.key, 'statistic':self.key[3], 'component':None,
                  'native':.25, 'current':.375, 'epsilon':.03125,
                  'provenance':{'source':self.source_pin, 'selector':self.key}}
        self.policy = {'schema':'w51-dl5-policy-1', 'dataOrigin':'synthetic',
            'completePopulation':self.population, 'completeKeys':[self.key], 'sources':[self.source_pin],
            'primaryT1GrowthMultiplier':2,
            'exceptions':[], 'aggregates':[{'id':'C-rest', 'kind':'t1',
                'dimensions':{'stratum':'C'}, 'gate':True, 'reduction':'median-log-ratio',
                'timing':'population-full', 'members':[member],
                'membershipSha256':R['digest']([member])}]}
        self.policy_pin = self.put('policy.json', self.policy)
        self.declaration_pin = self.put('declaration-v3/declaration.json', {'policies':[self.policy_pin]})
        self.charter = self.put('charter.json', {'landingPolicies':{'synthetic':self.policy_pin},
            'artifacts':[self.policy_pin, self.population, self.declaration_pin, self.source_pin]})
        self.config = self.put('judge-config.json', {'landingPolicy':self.policy_pin})
        self.inputs = [self.charter, self.policy_pin, self.population, self.declaration_pin, self.config, self.source_pin]
        self.science = {'dataOrigin':'synthetic', 'landingPolicy':self.policy_pin,
            'instruments':{'judge':{'config':self.config}}, 'inputs':copy.deepcopy(self.inputs)}
        self.root = {'repo':str(self.home), 'charter':self.charter, 'inputs':copy.deepcopy(self.inputs),
            'populations':{'synthetic-rehearsal':{'dataset':'synthetic', 'manifest':self.population}}}

    def put(self, name, value):
        path = self.home/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(R['encoded'](value))
        return {'path':str(path), 'sha256':R['sha'](path)}

    def bound(self):
        return S['bound_landing_policy'](self.root, self.science, self.science['inputs'])

    def test_sealed_policy_is_bound_without_reopening_its_scientific_payloads(self):
        self.assertEqual(self.bound(), self.policy)
        original = Path.read_bytes
        def permitted(path):
            if str(path) == self.source_pin['path']:
                self.fail('Runtime policy admission reopened a scientific source payload')
            return original(path)
        with patch.object(Path, 'read_bytes', permitted):
            self.assertEqual(self.bound()['aggregates'][0]['members'][0]['native'], .25)

    def test_changed_policy_wrong_dataset_and_registered_substitute_refuse(self):
        self.assertEqual(self.bound(), self.policy)
        for mutation in ('bytes', 'origin', 'substitute', 'membership', 'complete', 'unregistered'):
            with self.subTest(mutation=mutation):
                saved = copy.deepcopy((self.root, self.science))
                policy = copy.deepcopy(self.policy)
                if mutation == 'bytes':
                    policy['exceptions'] = [{'key':self.key}]
                    self.put('policy.json', policy)
                elif mutation == 'origin': self.science['dataOrigin'] = 'measured-native'
                elif mutation == 'substitute':
                    other = self.put('substitute.json', policy)
                    self.root['inputs'].append(other); self.science['inputs'].append(other)
                    self.science['landingPolicy'] = other
                elif mutation == 'membership':
                    policy['aggregates'][0]['members'][0]['key'] = ['p','webgpu','other','T1-full-silhouette']
                    changed = self.put('changed.json', policy)
                    self.science['landingPolicy'] = changed
                elif mutation == 'complete':
                    self.root['populations']['synthetic-rehearsal']['manifest'] = self.declaration_pin
                else: self.science['inputs'].remove(self.declaration_pin)
                with self.assertRaises(ValueError): self.bound()
                self.root, self.science = saved; self.put('policy.json', self.policy)

    def test_runtime_authority_covers_policy_population_and_declaration(self):
        pins = S['landing_policy_pins'](self.root, self.science)
        for pin in (self.policy_pin, self.population, self.declaration_pin, self.charter, self.config):
            self.assertIn(pin, pins)

    def test_exception_change_after_marker_invalidates_context(self):
        engine = RUN.Engine.__new__(RUN.Engine)
        engine.R = types.SimpleNamespace(REPO=self.home, checked=R['checked'],
            source=R['source'])
        engine.doc, engine.science = self.root, self.science
        engine._LEASE = {'token':'controlled'}
        hashes = engine.policy_authority_hashes()
        context = {'stage':'analysis'}
        engine.active = {'context':context, 'snapshot':copy.deepcopy(context), 'hashes':hashes}
        with patch.object(RUN, 'lease_owned', return_value=True):
            engine.require_context(context)
            changed = copy.deepcopy(self.policy); changed['exceptions'].append({'key':self.key})
            self.put('policy.json', changed)
            with self.assertRaisesRegex(ValueError, 'authority'): engine.require_context(context)

    def test_changed_policy_is_refused_before_consuming_marker(self):
        engine = RUN.Engine.__new__(RUN.Engine)
        engine.R = types.SimpleNamespace(REPO=self.home, checked=R['checked'], source=R['source'])
        engine.doc, engine.science = self.root, self.science
        engine._LEASE = {'token':'controlled'}
        marker = self.home/'analysis.started.json'
        engine.store = types.SimpleNamespace(analysis_marker=marker,
            start_analysis=lambda token:self.fail('Changed policy reached the analysis marker'))
        changed = copy.deepcopy(self.policy); changed['exceptions'].append({'key':self.key})
        self.put('policy.json', changed)
        with patch.object(RUN, 'lease_owned', return_value=True):
            with self.assertRaises(ValueError):engine.analyze({'members':[]}, {})
        self.assertFalse(marker.exists())

    def witness_case(self, *, pending=False):
        # A complete one-cell real fixture isolates the clause-C veto from old owner targets.
        policy = copy.deepcopy(self.policy); policy['dataOrigin'] = 'measured-native'
        pin = self.put('policy.json', policy)
        self.root['charter'] = self.put('charter.json', {'landingPolicies':{'real':pin},
            'artifacts':[pin, self.population, self.declaration_pin, self.source_pin]})
        self.science.update(dataOrigin='measured-native', landingPolicy=pin, reportedKeys=[])
        self.config = self.put('judge-config.json', {'landingPolicy':pin})
        self.science['instruments']['judge']['config'] = self.config
        self.inputs = [self.root['charter'], pin, self.population, self.declaration_pin, self.config, self.source_pin]
        self.root['inputs'] = self.science['inputs'] = self.inputs
        self.root['populations'] = {'gate':{'dataset':'real', 'manifest':self.population}}
        self.root.update(closure={'sources':{}}, importedFit={'path':'untouched-fit', 'sha256':'f'*64})
        self.science['references'] = self.population
        reading = {'native':.25, 'current':.375, 'candidate':.4,
            **{side+'MeasurementStatus':'MEASURED' for side in ('native','current','candidate')}}
        row = dict(zip(R['KEY'], self.key))
        row.update(family='texture', position=.5, readings={self.key[3]:reading})
        row['evidence'] = self.put('measurement.json', {'row':copy.deepcopy(row)})
        measured = {'rows':[row], 'snapshot':row['evidence']}
        rules = R['source'](HERE/'judge_rules.py', 'w51_dl5_witness_rules')
        clause = rules.route_aggregates([row], landing_policy=policy, policy_sha256=pin['sha256'],
            complete_keys=[self.key], full_union=not pending)
        report = {'cells':[{**row, 'status':'PASS'}], 'status':'NEITHER' if not pending else
            'PASS_EXPOSED_OWNER_PENDING', 'clauseC':clause, 'landingPolicy':pin,
            'ownerChecks':'PENDING_FULL_UNION', 'targetChecks':'PENDING_FULL_UNION',
            'pendingOwnerKeys':[]}
        capture = dict(zip(R['KEY'][:3], self.key[:3])); capture['lane'] = 'candidate'
        payload = self.put('capture.json', capture)
        union = {'members':[{'payload':payload}]}; self.put('captures.complete.json', union)
        root_pin = self.put('execution-root.json', self.root)
        context = {'expectedCells':[dict(zip(R['KEY'], self.key))],
            'populationPin':self.population, 'datasetPin':self.config,
            'executionRoot':root_pin['path'], 'executionClaim':self.config,
            'phaseDependencies':{'pendingOwnerKeys':[]}, 'inputs':self.inputs}
        if pending:
            context['populationPin'] = self.put('partial.json', {'statisticKeys':[self.key]})
        journal = R['source'](HERE/'journal.py', 'w51_dl5_witness_journal')
        engine = types.SimpleNamespace(require_context=lambda c:None,
            R=types.SimpleNamespace(**{k:R[k] for k in ('checked','source','digest','encoded','verify_web_sources')},
                                    REPO=self.home), J=journal,
            doc=self.root, science=self.science, batch={'runs':[], 'cohort':[]}, output=self.home,
            store=types.SimpleNamespace(home=self.home, complete_union=lambda:union),
            A=types.SimpleNamespace(validate_captures=lambda *a:{}))
        return engine, context, union, {'captures':[capture]}, {}, measured, report

    def test_aggregate_only_failure_completes_witness_as_scientific_neither(self):
        witness = R['source'](HERE/'witness.py', 'w51_dl5_witness')
        args = self.witness_case()
        result = witness.verify(*args)
        self.assertEqual(result['status'], 'COMPLETE')
        self.assertTrue(result['judgeCompleted'])
        self.assertEqual(result['reportStatus'], 'NEITHER')
        self.assertEqual(result['clauseC']['status'], 'EXCEEDS')

    def test_complete_gate_cannot_claim_aggregate_pending_or_forged_members(self):
        witness = R['source'](HERE/'witness.py', 'w51_dl5_witness')
        args = self.witness_case(pending=True)
        self.assertEqual(witness.verify(*args)['clauseC']['status'], 'PENDING_FULL_UNION')
        args[1]['populationPin'] = self.population
        with self.assertRaisesRegex(ValueError, 'aggregate'): witness.verify(*args)
        args = self.witness_case()
        args[-1]['clauseC']['aggregates'][0]['membershipSha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'aggregate'): witness.verify(*args)


if __name__ == '__main__': unittest.main()
