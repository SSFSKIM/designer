"""Run ONE DL5r successor analysis, after sealing and independent review.

    /Users/new/vitrea-w49/py/bin/python -I -B <this-file> run
    /Users/new/vitrea-w49/py/bin/python -I -B <this-file> status

There is no replay flag, output override, capture, fit, exposure or third-analysis operation.
The only public result is status/count/hash metadata. Detailed reports stay quarantined.
A marker without a complete terminal record means UNMEASURED/NEITHER on every later status
or invocation. Nothing remeasures or reconstructs a result on restart.
"""
import argparse
import copy
import os
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent


def source(path, name):
    m = types.ModuleType(name); m.__file__ = str(path); sys.modules[name] = m
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), m.__dict__)
    return m


A = source(HERE/'authority.py', 'w50_analysis2_authority')
W = A.W
R = source(HERE/'reads.py', 'w50_analysis2_reads')
TERMINAL = HERE/'analysis-2.terminal.json'
LOGICAL = Path(str(A.CONTRACT_PATH)+'.started.json')


class ReadOnlyDispatcher:
    """Only the unchanged read-admission surface, over the successor's genuine leased context.

    The underlying LIVE module is NOT prepared through root3 and its execute_analysis is NEVER
    called. Its lease, context immutability, receipt matching and read-membership implementations
    are reused unchanged. There is no render/native/owner/exposure grant on this facade.
    """
    def __init__(self, live, boundary, context):
        self.live, self.boundary, self.context = live, boundary, context
    @property
    def _LEASE(self): return self.live._LEASE
    def require_context(self, context): return self.live.require_context(context)
    def require_payload(self, context, item): return self.live.require_payload(context, item)
    def require_read_admission(self, context, run, current=False):
        return self.live.require_read_admission(context, run, current=current)
    def resolve_capture_run(self, context, receipt):
        return self.live.resolve_capture_run(context, receipt)
    def sha(self, path): return self.live.sha(path)
    def sealed(self, path): return self.live.sealed(path)
    def checked(self, repo, item): return self.live.checked(repo, item)
    def load(self, path): return self.live.load(path)
    def admission_module(self, doc):
        return R.Admission(self.live.admission_module(doc), self.boundary, self, self.context)


def modules():
    live = source(A.FIT/'live-execution/dispatch.py', 'w50_analysis2_live_mechanics')
    core = {name: source(A.FIT/'live-execution'/(filename+'.py'), 'w50_analysis2_'+filename)
            for name, filename in (('C', 'common'), ('A', 'authority'), ('L', 'lifecycle'),
                                   ('Q', 'quarantine'))}
    live._CORE = core
    return live, core


def admit(root, view, old_contract, batch, live, core):
    """Unchanged semantic validators, with the predecessor explicitly separate from the view."""
    D, L, authority = core['C'].D, core['L'], core['A']
    authority.validate_body(A.ROOT, view)
    # These proofs belong to root3, whose original source map they state. No rewriting to the
    # successor closure: the one source delta was admitted separately, before this call.
    if authority.verify_prefit(A.ROOT, root) != old_contract['preFitEvidence']:
        raise ValueError('Original pre-fit proof differs')
    batch_path = D.checked(A.REPO, old_contract['batch'])
    admitted_batch, expected = D.validate_batch(view, batch_path, 'gate')
    live._live_batch(view, admitted_batch)
    if admitted_batch != batch or len(expected) != 2553:
        raise ValueError('Original gate key membership differs')
    D.validate_fit_record(A.ROOT, root, batch['cohort'], D.checked(A.REPO, old_contract['fitRecord']))
    live._one_fit_point(A.ROOT, root, D.checked(A.REPO, old_contract['fitRecord']))
    store = L.Store(A.CONTRACT, batch, A.OLD_OUTPUT)
    union = store.complete_union()
    if union != W.parse(A.UNION.read_bytes()) or len(union['members']) != 1341:
        raise ValueError('Original complete capture union differs')
    # complete_union hashes every checkpoint payload and every capture artifact before the
    # successor marker. It does NOT parse the capture payloads for numerical values.
    if W.parse(A.MARKER.read_bytes()).get('captures') != W.pin(A.UNION):
        raise ValueError('Spent marker names another capture union')
    return (view, old_contract, batch_path, batch, expected, store), union


def activate(live, core, data, union, claim, boundary):
    D, L, Q = core['C'].D, core['L'], core['Q']
    context, hashes = live._template(A.ROOT, A.CONTRACT, data)
    context.update(executionRoot=str(A.VIEW_PATH), contract=str(A.CONTRACT_PATH),
        output=str(A.OUTPUT), stage='analysis', executionClaim=claim, logicalClaim=W.pin(LOGICAL))
    hashes.extend((str(p), W.sha(p)) for p in
                  (A.VIEW_PATH, A.CONTRACT_PATH, A.AUTHORITY_PATH, LOGICAL, A.NEW_MARKER, A.UNION))
    live._ACTIVE = {'context': context, 'snapshot': copy.deepcopy(context), 'hashes': hashes,
        'doc': data[0], 'store': data[5],
        'numerical': W.parse(LOGICAL.read_bytes())['numericalAdmission'],
        'members': [r['member'] for r in union['members']],
        'payloads': [r['payload'] for r in union['members']], 'records': {}}
    facade = ReadOnlyDispatcher(live, boundary, context)
    sys.modules['w50_g1_dispatch'] = facade
    # Reading capture payloads is allowed only after the irreversible analysis-2 marker.
    records = [Q.read_payload(context, r['payload']) for r in union['members']]
    live._ACTIVE['records'] = {r['member']['id']: payload for r, payload in zip(union['members'], records)}
    return context, {'schema': 'w50-live-composed-captures-1', 'status': 'CAPTURED',
        'candidateSha256s': sorted(p['sha256'] for p in data[3]['cohort']), 'captures': records}


def authority_bindings(context):
    return {**{name: W.pin(context[field]) for name, field in
        (('executionRoot', 'executionRoot'), ('contract', 'contract'), ('batch', 'batchPath'))},
        'executionClaim': context['executionClaim']}


def analyze(live, core, data, union, manifest, boundary):
    D, Q = core['C'].D, core['Q']
    view, old_contract, batch_path, batch, expected, store = data
    roles = {name: live._component(view, name) for name in ('measurement', 'judge')}
    old_authority = {'executionRoot': W.pin(A.ROOT), 'contract': W.pin(A.CONTRACT),
                     'batch': W.pin(batch_path), 'executionClaim': W.pin(A.MARKER)}
    claim = {'schema': 'w50-live-analysis-claim-1', 'analysis': 2, 'ruling': 'DL5r',
        'logicalContract': W.pin(A.CONTRACT_PATH), 'pid': os.getpid(), 'gpuLease': live._LEASE['token'],
        'output': str(A.OUTPUT), 'spentMarker': W.pin(A.MARKER), 'captures': W.pin(A.UNION),
        'unreadManifest': W.pin(A.MANIFEST), 'authority': W.pin(A.AUTHORITY_PATH)}
    state = {}

    def measure():
        ctx, captures = activate(live, core, data, union, W.pin(A.NEW_MARKER), boundary)
        state.update(context=ctx, captures=captures)
        # Retained paths still belong to the ORIGINAL capture output, not the successor output.
        # Admission's artifact ownership checks read the capture receipts, never relocate them.
        facade = sys.modules['w50_g1_dispatch']
        state['receipt'] = facade.admission_module(view).validate_captures(batch, captures, A.OUTPUT)
        module, config = roles['measurement']
        R.install(module, boundary, facade, ctx, {'executionRoot': W.pin(A.ROOT),
            'contract': W.pin(A.CONTRACT), 'batchPath': W.pin(batch_path)})
        measured = module.evaluate(ctx, captures, config)
        live.require_context(ctx)
        return measured

    def witness():
        return W.compare(manifest, A.OLD_OUTPUT/'measurement', A.OUTPUT/'measurement',
            [[row[k] for k in W.KEY] for row in expected], old_authority,
            authority_bindings(state['context']))

    def judge(measured):
        module, config = roles['judge']
        report = module.evaluate(state['context'], {'measurement': measured, 'owner': None,
                                                    'captures': state['captures']}, config)
        live.require_context(state['context'])
        core['C'].validate_report(view, batch, expected, report, gate_result=None)
        # Recheck all predecessor/config/source bytes after judgment before publishing status.
        A.verify_seal()
        if store.complete_union() != union: raise ValueError('Capture union changed during analysis')
        if state['captures']['captures'] != [L.read(L.checked(r['payload'])) for r in union['members']]:
            raise ValueError('Analysis mutated original capture records')
        return report

    L = core['L']
    result = W.once(A.NEW_MARKER, claim, measure, witness, judge)
    artifact = W.write_once(A.OUTPUT/'quarantine/result.json', {
        'schema': 'w50-dl5r-successor-result-1', 'analysis': 2, 'authority': W.pin(A.AUTHORITY_PATH),
        'analysisClaim': W.pin(A.NEW_MARKER), 'originalContract': W.pin(A.CONTRACT),
        'captureUnion': W.pin(A.UNION), 'unreadManifest': W.pin(A.MANIFEST), **result})
    public = {'schema': 'w50-dl5r-public-result-1', 'analysis': 2, 'status': result['status'],
              'sha256': artifact['sha256']}
    if 'witness' in result:
        public.update(witnessCount=result['witness']['count'], witnessSha256=result['witness']['sha256'])
    else: public['measurementStatus'] = 'UNMEASURED'
    W.write_once(TERMINAL, public)
    return public


def status():
    if TERMINAL.exists():
        value = W.parse(TERMINAL.read_bytes())
        allowed = {'schema', 'analysis', 'status', 'sha256', 'witnessCount', 'witnessSha256', 'measurementStatus'}
        if not set(value) <= allowed or value.get('analysis') != 2 or value.get('status') not in (
                'NEITHER', 'PASS_EXPOSED_OWNER_PENDING'):
            raise ValueError('Invalid public terminal record')
        if ('measurementStatus' in value and value['measurementStatus'] != 'UNMEASURED') or (
                'schema' in value and value['schema'] != 'w50-dl5r-public-result-1'):
            raise ValueError('Invalid public status metadata')
        if 'witnessCount' in value and (value['witnessCount'] != 634 or
                not isinstance(value.get('witnessSha256'), str) or len(value['witnessSha256']) != 64 or
                any(c not in '0123456789abcdef' for c in value['witnessSha256'])):
            raise ValueError('Invalid public witness metadata')
        if 'sha256' in value:
            if W.sha(A.OUTPUT/'quarantine/result.json') != value['sha256'] or not A.NEW_MARKER.is_file():
                raise ValueError('Terminal result lost its pinned payload or marker')
        elif value['status'] != 'NEITHER' or value.get('measurementStatus') != 'UNMEASURED':
            raise ValueError('A successful terminal result requires a sealed payload')
        return value
    if A.NEW_MARKER.exists() or A.OUTPUT.exists() or LOGICAL.exists():
        return {'status': 'NEITHER', 'measurementStatus': 'UNMEASURED', 'analysis': 2}
    return {'status': 'NOT_STARTED', 'analysis': 2}


def run():
    # Any prior attempt, including a crash before/after the marker, is terminal. This path
    # neither remeasures nor invokes a judge, and accepts no caller-supplied output/marker.
    previous = status()
    if previous['status'] != 'NOT_STARTED': return previous
    root, view, old_contract, batch, manifest, authority, guard = A.verify_seal()
    guard.enforce(A.REPO, authority['closure']['sources'])
    live, core = modules()
    # Output mkdir is exclusive and is also a conservative crash tombstone before marker write.
    A.OUTPUT.mkdir(parents=False, exist_ok=False)
    directory = os.open(A.OUTPUT.parent, os.O_RDONLY)
    try: os.fsync(directory)
    finally: os.close(directory)
    def work():
        with live._gpu_lease():
            try:
                data, union = admit(root, view, old_contract, batch, live, core)
                original_claim = W.parse(Path(str(A.CONTRACT)+'.started.json').read_bytes())
                W.write_once(LOGICAL, {'schema': 'w50-dl5r-analysis-logical-claim-1', 'analysis': 2,
                    'executionAuthority': W.pin(A.AUTHORITY_PATH),
                    'originalClaim': W.pin(str(A.CONTRACT)+'.started.json'),
                    'numericalAdmission': original_claim['numericalAdmission']})
                with R.Boundary(A.OLD_OUTPUT, A.OUTPUT, union) as boundary:
                    return analyze(live, core, data, union, manifest, boundary)
            finally:
                live._ACTIVE = None
                sys.modules.pop('w50_g1_dispatch', None)
    ok, result = core['Q'].run_private(A.OUTPUT/'quarantine/analysis.log', work)
    if not ok:
        result = {'status': 'NEITHER', 'measurementStatus': 'UNMEASURED', 'analysis': 2}
        if not TERMINAL.exists(): W.write_once(TERMINAL, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('run', 'status'))
    args = parser.parse_args()
    # Even pre-marker refusals publish no exception text or values.
    try: result = run() if args.operation == 'run' else status()
    except BaseException:
        result = {'status': 'NEITHER', 'measurementStatus': 'UNMEASURED', 'analysis': 2}
        if (args.operation == 'run' and not TERMINAL.exists() and not A.OUTPUT.exists()
                and not A.NEW_MARKER.exists() and not LOGICAL.exists()):
            W.write_once(TERMINAL, result)
    print(W.encode(result).decode(), end='')
    return 0 if result['status'] == 'PASS_EXPOSED_OWNER_PENDING' else 1


if __name__ == '__main__': sys.exit(main())
