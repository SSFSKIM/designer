"""Source-only access to the immutable original numerical/admission machinery, and the LIVE
judge-report validation over it (W50 DL5m item 4).

DL5m (4) admits UNMEASURED_REPORTED, with its cause, for a DL5a/b/c reported key whose reading
is incomplete, non-finite or out of domain; such a key never gates, so it does not change the
verdict. A nonfinite or out-of-domain side reaches the judge already nulled by the measurement
projection, and the cause carries the projection's defects (kind and side, never a value).
current3's validate_report is sealed and knows no such status: for a qualified verdict it
requires every reported key REPORTED with finite native/current/candidate.

validate_report below checks each UNMEASURED_REPORTED cell itself, then hands current3's
validate_report the WHOLE report with only those cells presented as the original accepts a
non-gating reported row (REPORTED, B null, zero placeholders on native/current/candidate).
Dropping the cells instead would break current3's exact membership check and force a copy of
it here; presenting them keeps every original check (cohort binding, scope, gate binding,
membership, exemption membership, empty-support witnesses, REPORTED shape, the qualified
intersection) running unchanged on every other row and on the presented rows' identities.
The presentation is a private deep copy that never leaves this module: only current3's
verdict (return or raise) does, and the sealed report keeps its null readings.

DL5a's reportedKeys contain DL5b/DL5c's emptySupportKeys (prefit.validate_empty_eligibility
refuses a root otherwise), so reportedKeys is the exact admitted set.

current3's checked_gate_result calls its own validate_report by global name, so the qualified
gate a LIVE exposure reads is re-validated by checked_gate_result below, a copy of that function
differing only in which validate_report it calls and in reading the gate from its root's own slot
(test_report.py proves the copy by syntax tree). Errors carry field names and keys only (DL5k).

The LIVE root chain (DL5o). A successor root is sealed BESIDE the root it supersedes, as
execution-root-<n>.json (n >= 2) after execution-root.json, and only the newest generation of a
directory is ever admitted (superseded; authority.predecessors validates each link). Each root's
phase slots and pre-fit evidence are its own, named by its stem (slot). Fit contracts stay in
the shared fit/ directory because the fit role (fit/live.fit_record) and the initializer
(fit/execution._bootstrap) bind fit/ and the sibling dispatcher to the root's directory, so a
directory per root would break both. slot_area names every file a root's slots, and the shared
slots of the dispatcher that sealed generation 1, could have written; a successor is sealed only
while it is empty.

DL5n: a completed native blind read that is not ready reaches the judge with its stops, and
each stopped key's cell is UNMEASURED with null readings and the cause NATIVE_NOT_READY.
current3 admits an UNMEASURED cell on a NEITHER verdict unchanged; check_native_not_ready holds
the readiness the report states to the stops it states (second pre-seal review P3): every
exposure report states it, a gate report never; a read that is not ready has stops and a NEITHER
verdict; stoppedKeys are exactly the stops expanded over both renderers within the phase's
expected keys, each stop naming at least one; and the NATIVE_NOT_READY cells are exactly those
keys, each an UNMEASURED blind non-reported key with null readings.
"""
import copy
import os
from pathlib import Path
import re
import sys
import types
HERE=Path(__file__).resolve().parent
FIT=HERE.parent
CURRENT3=FIT.parent/'2026-10-08-w50-g1-current3'
CANONICAL3=FIT.parent/'2026-10-08-w50-g1-canonical3'

def source(path,name):
    m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m
    exec(compile(Path(path).read_bytes(),str(path),'exec',dont_inherit=True),m.__dict__)
    return m

D=source(CURRENT3/'execution/dispatch.py','w50_live_immutable_mechanics')

# A chain root's name, or its sidecar's; dispatch.ROOT_CHAIN is the same pattern (test_chain).
ROOT_CHAIN=re.compile(r'execution-root(?:-([2-9]|[1-9][0-9]+))?\.json(?:\.sha256)?')
SLOT_NAMES={'gate':D.SLOTS['gate'],'exposure':D.SLOTS['exposure'],'prefit':'pre-fit-evidence.json'}


def generation(name):
    """A chain root's generation from its file name (or its sidecar's); None off the chain."""
    match=ROOT_CHAIN.fullmatch(name)
    return None if match is None else int(match.group(1) or 1)


def root_name(n):return 'execution-root.json' if n==1 else f'execution-root-{n}.json'


def _names(folder):return os.listdir(folder) if Path(folder).is_dir() else []


def superseded(path):
    """Whether a later generation of the chain, its document or its sidecar alone, exists beside
    this chain root. A torn successor seal supersedes too: the safe side."""
    path=Path(path).resolve();own=generation(path.name)
    return own is not None and any((generation(n) or 0)>own for n in _names(path.parent))


def newest_root(directory):
    """The newest chain root of a directory, the only one any entry admits."""
    found=[g for g in map(generation,_names(directory)) if g is not None]
    if not found:raise ValueError('No LIVE root in this directory')
    return Path(directory).resolve()/root_name(max(found))


def slot(root,phase,batch_sha256=None):
    """This root's own slot: a fit contract (named by its batch's hash), the gate or exposure
    contract, or the pre-fit evidence ('prefit'). Every journal file of a contract extends its
    name (.sha256, .started.json, .phase/, .result.json)."""
    root=Path(root).resolve();stem=root.name.removesuffix('.json')
    if phase=='fit':
        if not isinstance(batch_sha256,str) or not re.fullmatch('[0-9a-f]{64}',batch_sha256):
            raise ValueError('A fit slot is named by its batch hash')
        return root.parent/D.SLOTS['fit']/f'{stem}.{batch_sha256}.json'
    return root.parent/f'{stem}.{SLOT_NAMES[phase]}'


def slot_area(root):
    """(directory, name pattern) pairs covering every file this root's slots could hold, and the
    shared slots (fit/<batch>.json, gate-contract.json, exposure-contract.json,
    pre-fit-evidence.json) of the dispatcher that sealed generation 1, which nothing writes now."""
    root=Path(root).resolve();stem=re.escape(root.name.removesuffix('.json'))
    names='(?:'+'|'.join(re.escape(SLOT_NAMES[k]) for k in ('gate','exposure','prefit'))+')'
    fit=root.parent/D.SLOTS['fit']
    return [(fit,stem+r'\..*'),(root.parent,stem+r'\.'+names+'.*'),(fit,r'[0-9a-f]{64}\.json.*'),(root.parent,names+'.*')]


def slot_entries(root):
    """Every existing file or directory in this root's slot area."""
    return [Path(folder)/name for folder,pattern in slot_area(root) for name in sorted(_names(folder))
            if re.fullmatch(pattern,name)]

UNMEASURED_REPORTED='UNMEASURED_REPORTED'
CAUSES=('INCOMPLETE_READING','NON_FINITE_READING','OUT_OF_DOMAIN_READING')
DEFECTS=('NON_FINITE_READING','OUT_OF_DOMAIN_READING')
SIDES=('native','current','candidate')
NULL_FIELDS=SIDES+('value','fidelity','B')
PASS_FIELDS=('joinIdentity','heldDifference','emptySupportWitness')
NATIVE_NOT_READY='NATIVE_NOT_READY'
NATIVE_STOPS=('UNMEASURED_UNAUTHORISED_POPULATION','NATIVE_SPREAD_EXCEEDS_ONE_CODE')


def check_unmeasured_reported(doc,cell):
    """Refuse the status off the enumerated keys, without a cause, or beside a passable value."""
    if tuple(cell.get(k) for k in D.KEY) not in {tuple(k) for k in doc['reportedKeys']}:
        raise ValueError('UNMEASURED_REPORTED is admitted only on an enumerated DL5a/b/c reported key')
    cause=cell.get('cause')
    if not isinstance(cause,dict) or set(cause)-{'defects'}!={'kind','sides','routeStatus','unmeasured'} or \
            cause['kind'] not in CAUSES or cause['routeStatus'] not in ('DIAGNOSTIC','UNMEASURED') or \
            not isinstance(cause['sides'],list) or any(s not in SIDES for s in cause['sides']) or \
            len(set(cause['sides']))!=len(cause['sides']) or not isinstance(cause['unmeasured'],list) or \
            any(type(u) is not str for u in cause['unmeasured']) or \
            not (cause['sides'] or (cause['routeStatus']=='UNMEASURED' and cause['unmeasured'])) or \
            (cause['kind']=='NON_FINITE_READING' and not cause['sides']):
        raise ValueError('UNMEASURED_REPORTED requires its stated cause')
    # The projection's defects, when present: kind and side only, each side one of the cause's
    # sides, and the cause's kind the one they imply (an out-of-domain kind has no other source).
    defects=cause.get('defects',[])
    if ('defects' in cause and (not isinstance(defects,list) or not defects)) or any(
            not isinstance(d,dict) or set(d)!={'kind','side'} or d['kind'] not in DEFECTS or
            d['side'] not in cause['sides'] for d in defects) or \
            len({d['side'] for d in defects})!=len(defects) or \
            (cause['kind']=='OUT_OF_DOMAIN_READING')!=(bool(defects) and cause['kind']!='NON_FINITE_READING') or \
            (any(d['kind']=='NON_FINITE_READING' for d in defects) and cause['kind']!='NON_FINITE_READING'):
        raise ValueError('UNMEASURED_REPORTED requires its stated cause')
    if any(name not in cell or cell[name] is not None for name in NULL_FIELDS) or any(name in cell for name in PASS_FIELDS):
        raise ValueError('UNMEASURED_REPORTED must carry null readings and no passable value')


def stopped_keys(readiness,expected):
    """The phase keys a report's stated stops name: each stop's (profile, scene, statistic) on
    both renderers, within the expected keys; a stop naming none refuses (judge/live.native_stops)."""
    stops=readiness['stops'];phase={tuple(c[k] for k in D.KEY) for c in expected};keys=set()
    if any(not isinstance(s,dict) or set(s)!={'cell','statistic','reason'} or s['reason'] not in NATIVE_STOPS or
           not isinstance(s['cell'],str) or s['cell'].count('/')!=1 or not isinstance(s['statistic'],str)
           for s in stops) or len({(s['cell'],s['statistic']) for s in stops})!=len(stops):
        raise ValueError('A stated native stop is metadata on one statistic')
    for stop in stops:
        profile,scene=stop['cell'].split('/')
        named={(profile,renderer,scene,stop['statistic']) for renderer in ('webgpu','css')}&phase
        if not named:raise ValueError('A stated native stop names no key of this phase')
        keys|=named
    return sorted(keys)


def check_native_not_ready(doc,report,expected):
    """DL5n: the readiness a report states binds its NATIVE_NOT_READY cells (module docstring).
    `expected` is the phase's expected keys, as validate_report receives them."""
    if not isinstance(report,dict):return
    cells=[c for c in report.get('cells',[]) if isinstance(c,dict) and (c.get('cause') or {}).get('kind')==NATIVE_NOT_READY]
    if report.get('phase')!='exposure':
        if cells or 'nativeReadiness' in report:raise ValueError('Native readiness belongs to an exposure report only')
        return
    readiness=report.get('nativeReadiness')
    if not isinstance(readiness,dict) or set(readiness)!={'ready','stops','stoppedKeys'} or \
            type(readiness['ready']) is not bool or not isinstance(readiness['stops'],list) or \
            not isinstance(readiness['stoppedKeys'],list) or readiness['ready']!=(readiness['stops']==[]):
        raise ValueError('An exposure report states its native readiness and its stops')
    keys=stopped_keys(readiness,expected)
    if not readiness['ready'] and report.get('status')!='NEITHER':
        raise ValueError('A native read that is not ready admits only a NEITHER exposure')
    if [tuple(k) if isinstance(k,list) else k for k in readiness['stoppedKeys']]!=keys or \
            sorted(tuple(c.get(k) for k in D.KEY) for c in cells)!=keys:
        raise ValueError('NATIVE_NOT_READY is admitted only on the stopped keys of a NEITHER exposure')
    if not cells:return
    roles={tuple(c[k] for k in D.KEY):c['role'] for c in D.load(D.checked(doc['repo'],doc['references']))['cells']}
    reported={tuple(k) for k in doc['reportedKeys']}
    for cell,identity in zip(cells,(tuple(c.get(k) for k in D.KEY) for c in cells)):
        if cell.get('status')!='UNMEASURED' or roles.get(identity)!='blind' or identity in reported or \
                set(cell['cause'])!={'kind','reason'} or cell['cause']['reason'] not in NATIVE_STOPS or \
                any(name not in cell or cell[name] is not None for name in NULL_FIELDS) or \
                any(name in cell for name in PASS_FIELDS):
            raise ValueError('NATIVE_NOT_READY requires an UNMEASURED blind key with null readings')


def presented(doc,report):
    """current3's view: each checked UNMEASURED_REPORTED cell as an accepted non-gating row."""
    out=copy.deepcopy(report)
    for cell in out.get('cells',[]) if isinstance(out,dict) else []:
        if isinstance(cell,dict) and cell.get('status')==UNMEASURED_REPORTED:
            check_unmeasured_reported(doc,cell)
            cell.update(status='REPORTED',native=0,current=0,candidate=0,B=None)
    return out


def validate_report(doc,batch,expected,report,gate_result=None):
    check_native_not_ready(doc,report,expected)
    D.validate_report(doc,batch,expected,presented(doc,report),gate_result=gate_result)


def checked_gate_result(path, doc):
    gate = slot(path, 'gate')
    if not gate.is_file() or not Path(str(gate)+'.result.json').is_file():
        raise ValueError('Exposure requires a completed qualified gate success')
    contract = D.sealed(gate)
    if contract.get('executionRootSha256') != D.sha(path) or contract.get('phase') != 'gate':
        raise ValueError('Gate belongs to another root/phase')
    batch, expected = D.validate_batch(doc, D.checked(doc['repo'], contract['batch']), 'gate')
    result = D.result_for(gate)
    claim = D.load(Path(str(gate)+'.started.json'))
    receipt = D.admission_module(doc).validate_captures(batch, result['captures'], claim['output'])
    if D.repeat_artifact_pins(doc['repo'],result['captures'])!=result.get('repeatReceipt'):
        raise ValueError('Gate result omitted paired repeat evidence')
    if receipt != result['captureReceipt']:
        raise ValueError('Gate capture result differs from complete declared membership')
    validate_report(doc, batch, expected, result['report'])
    if result['report']['status'] != D.GATE_SUCCESS:
        raise ValueError('Only PASS on exposed cells with owners pending admits exposure')
    return gate, result
