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
differing only in which validate_report it calls (test_report.py proves the copy by syntax
tree). Errors carry field names and keys only (DL5k).
"""
import copy
from pathlib import Path
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

UNMEASURED_REPORTED='UNMEASURED_REPORTED'
CAUSES=('INCOMPLETE_READING','NON_FINITE_READING','OUT_OF_DOMAIN_READING')
DEFECTS=('NON_FINITE_READING','OUT_OF_DOMAIN_READING')
SIDES=('native','current','candidate')
NULL_FIELDS=SIDES+('value','fidelity','B')
PASS_FIELDS=('joinIdentity','heldDifference','emptySupportWitness')


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


def presented(doc,report):
    """current3's view: each checked UNMEASURED_REPORTED cell as an accepted non-gating row."""
    out=copy.deepcopy(report)
    for cell in out.get('cells',[]) if isinstance(out,dict) else []:
        if isinstance(cell,dict) and cell.get('status')==UNMEASURED_REPORTED:
            check_unmeasured_reported(doc,cell)
            cell.update(status='REPORTED',native=0,current=0,candidate=0,B=None)
    return out


def validate_report(doc,batch,expected,report,gate_result=None):
    D.validate_report(doc,batch,expected,presented(doc,report),gate_result=gate_result)


def checked_gate_result(path, doc):
    gate = Path(path).resolve().parent / D.SLOTS['gate']
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
