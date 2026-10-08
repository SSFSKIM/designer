"""Original-null canonical artifact projection from two genuine completed-current chains.

The composed reader authenticates the actual roots/results before returning members. This
projection reuses its identical immutable repeat/report validator instance and never creates
a capture root, live capability, numerical reading or single-root compatibility config.
"""
import copy
from pathlib import Path
import types

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[4]
KEY=('profile','renderer','scene','statistic')


def source(path,name):
    value=types.ModuleType(name);value.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec',dont_inherit=True),value.__dict__)
    return value


C=source(HERE.parent/'current-analysis-composed/analysis.py','w50_reference_composed_analysis')


def complete_current_projection(repo, original_rows, composition_pin, *, scenes=None):
    """Fill only original gate canonical null artifact slots; retain every original value."""
    repo=Path(repo).resolve()
    admitted=C.admit_composition(repo,composition_pin)
    root=admitted['originalRoot']
    inventory=C.A.B.load(C.A.B.checked(repo,root['references']))
    originals={tuple(row[k] for k in KEY):row for row in inventory['cells']}
    keys=[tuple(row[k] for k in KEY) for row in original_rows]
    if len(originals) != len(inventory['cells']) or len(keys) != len(set(keys)):
        raise ValueError('Original completion reference keys are duplicate')
    for row,k in zip(original_rows,keys,strict=True):
        if originals.get(k) != row:
            raise ValueError('Caller row/numeric override differs from original G0 inventory')
    members={}
    for member in admitted['members']:
        receipt=member['receipt'];identity=tuple(receipt[k] for k in KEY[:3])
        if identity in members:raise ValueError('Duplicate admitted completed-current member')
        members[identity]=member
    projection=copy.deepcopy(original_rows);completed=[];provenance=[];verified={}
    for row in projection:
        missing=[name for name in ('currentEvidence','currentMetadata') if name in row and row[name] is None]
        if not missing:continue
        identity=tuple(row[k] for k in KEY[:3]);member=members.get(identity)
        if row.get('role') != 'gate' or row.get('statistic') not in \
                ('T1-low','T1-full-silhouette','low-end-path-level') or member is None or \
                member['run'].get('sceneSource') != 'canonical':
            raise ValueError('Original missing canonical key has no admitted gate current capture')
        if identity not in verified:
            if scenes is not None:
                matches=[scene for scene in scenes['scenes'] if scene['id'] == row['scene']]
                if len(matches) != 1:raise ValueError('Completion captured an undeclared canonical scene')
            C.bind_member(admitted,member,inventory['cells'])
            candidate=admitted['candidates'][member['run']['candidate']['sha256']]
            _,spec,_,arguments,actual=C.A.capture_inputs(member,candidate,argument_required=False)
            if spec['scene'] != row['scene'] or arguments:
                raise ValueError('Artifact-only canonical admission changed scene or supplied numerical arguments')
            verified[identity]=actual
        actual=verified[identity]
        for field,artifact in (('currentEvidence','capture'),('currentMetadata','cell')):
            if field in missing:row[field]=copy.deepcopy(actual[artifact])
        completed.append([row[k] for k in KEY])
        provenance.append(dict(key=[row[k] for k in KEY],
            **{name:copy.deepcopy(member[name]) for name in
               ('instrument','batch','contract','claim','result','run','receipt','output')},
            provenance=copy.deepcopy(actual)))
    return dict(schema='w50-admitted-current-reference-projection-2',
        originalRows=copy.deepcopy(original_rows),rows=projection,completedKeys=completed,
        memberProvenance=provenance,**C.anchors(admitted),
        policy='ONLY_ORIGINAL_NULL_CURRENT_ARTIFACT_PINS_NO_NUMERIC_ROLE_OR_HISTORY_CHANGE')


def source_probe(composition_pin=None, *, repo=REPO):
    """Exercise only composed source metadata/probes; never admit or open result evidence."""
    return C.source_probe(repo=repo,composition_pin=composition_pin)
