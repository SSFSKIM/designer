"""Deterministic joins over already registered evidence, never a reader or permission root.

Original G0 fields/order remain authoritative. This module computes no pixel statistic and
issues no pre-fit PASS. The parent binds inputs/sources, writes the returned content-addressed
provenance artifacts, and invokes the corrected current2 pre-fit validator before fitting.
"""
import copy
import hashlib
import json
import math
from pathlib import PurePosixPath

KEY = ('profile', 'renderer', 'scene', 'statistic')
FILLABLE = {'native', 'current', 'B', 'fidelity', 'nativeEvidence', 'currentEvidence', 'currentMetadata'}


def key(row): return tuple(row[k] for k in KEY)


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def finite(value): return type(value) in (int,float) and math.isfinite(value)


def preserved(original, supplied):
    """An upstream completion may fill original null placeholders, never change known fields."""
    for name, value in original.items():
        if name == 'status' or (name in FILLABLE and value is None): continue
        if name not in supplied or supplied[name] != value:
            raise ValueError(f'Original reference field changed: {key(original)}/{name}')


def fill(row, name, value):
    if name not in FILLABLE: raise ValueError('Not an authorised completion slot')
    if row.get(name) is None: row[name] = copy.deepcopy(value)


class Artifacts:
    """A pure content-addressed plan; constructing it creates no directory or file."""
    def __init__(self, root):
        self.root = PurePosixPath(root)
        if not self.root.is_absolute() or '..' in self.root.parts:
            raise ValueError('Artifact output needs an explicit absolute ordinary root')
        self.documents = {}

    def add(self, value):
        raw = encoded(value); digest = hashlib.sha256(raw).hexdigest()
        path = str(self.root/(digest+'.json'))
        if path in self.documents and self.documents[path] != value:
            raise ValueError('Conflicting deterministic artifact identity')
        self.documents[path] = copy.deepcopy(value)
        return {'path': path, 'sha256': digest}


def equal_budget(values):
    """A scalar can stand for a joint cut only when every declared budget is identical."""
    flat = []
    def collect(value):
        if isinstance(value, list):
            if not value: raise ValueError('Empty per-field budget')
            for item in value: collect(item)
        elif finite(value) and value > 0: flat.append(value)
        else: raise ValueError('Missing positive source budget')
    for value in values: collect(value)
    if not flat or any(value != flat[0] for value in flat):
        raise ValueError('Unequal per-field budget requires an explicit scalar-summary ruling')
    return flat[0]


def native_budget(statistic, repeat):
    if not isinstance(repeat, dict) or repeat.get('passes') is not True:
        raise ValueError('Native repeat readiness is missing')
    if statistic == 'T1-full-silhouette':
        code, bar = repeat.get('codeStepLinear'), repeat.get('barLinear')
        if not finite(code) or code <= 0 or not finite(bar) or bar < 0:
            raise ValueError('Missing own native linear T1 repeat budget')
        return max(code, 2*bar)
    bars = repeat.get('barCodes')
    bars = bars if isinstance(bars,list) else [bars]
    if any(not finite(b) or b < 0 for b in bars): raise ValueError('Missing own encoded native repeat bars')
    return equal_budget([max(1,2*b) for b in bars])


def complete_native(original, evidence, artifacts, exemptions, empty_support_keys):
    if evidence.get('originalReference') != original or key(evidence) != key(original) \
            or evidence.get('role') != original['role'] \
            or evidence.get('currentDocumentPair') != original['currentDocumentPair'] \
            or evidence.get('currentGeneration') != original['currentGeneration'] \
            or evidence.get('evidenceKind') != 'completed-current-gate0':
        raise ValueError('Completed-current evidence differs from exact original G0 reference')
    envelope = evidence.get('nativeEvidenceEnvelope', {})
    if envelope.get('schema') != 'w50-native-three-run-evidence-1' or any(
            envelope.get(k) != original.get(k) for k in
            ('profile','scene','statistic','role','support','nativeIdentity','referenceIdentity')):
        raise ValueError('Native provenance envelope changed original support/identity')
    row=copy.deepcopy(original); measurement=evidence['measurement']; provenance=evidence['provenance']
    for name, value in (('nativeEvidence',artifacts.add(envelope)),
                        ('currentEvidence',provenance['capture']),('currentMetadata',provenance['cell'])):
        fill(row,name,value)
    row['currentMeasurementEvidence'] = copy.deepcopy(provenance)
    row['nativeRepeat'] = copy.deepcopy(measurement['nativeRepeat'])
    row['nativeSupportWitnesses'] = copy.deepcopy(measurement['nativeSupportWitnesses'])
    exempt = key(row) in {tuple(k) for k in exemptions}
    if measurement.get('status') == 'UNMEASURED_EMPTY_SUPPORT':
        witnesses=measurement.get('nativeSupportWitnesses', [])
        if key(row) not in {tuple(k) for k in empty_support_keys} or not exempt \
                or measurement.get('required') is not False \
                or measurement.get('measurementStatus') != 'UNMEASURED_EMPTY_SUPPORT' \
                or any(measurement.get(k) is not None for k in ('value','nativeValue','nativeRepeat')) \
                or measurement.get('runValues') != [None,None,None] \
                or [w.get('run') for w in witnesses] != [1,2,3] or any(w.get('pixels') != 0 for w in witnesses):
            raise ValueError('Missing exact eligible three-run empty-support evidence')
        for name in ('native','current','fidelity','B'): fill(row,name,None)
        row['value']=None; row['status']='UNMEASURED_EMPTY_SUPPORT'
        row['emptySupportWitness']=artifacts.add(dict(schema='w50-empty-native-support-witness-1',
            profile=row['profile'],scene=row['scene'],nativeRead=copy.deepcopy(provenance['nativeRead'])))
        return row
    if measurement.get('measurementStatus') != 'MEASURED' or measurement.get('status') != \
            ('REPORTED' if exempt else 'MEASURED') or measurement.get('required') is not (not exempt) \
            or measurement.get('nativeValue') is None or measurement.get('value') is None:
        raise ValueError('Missing measured native/current evidence for original key')
    fill(row,'native',measurement['nativeValue']); fill(row,'current',measurement['value'])
    fill(row,'B',None if exempt else native_budget(row['statistic'],measurement['nativeRepeat']))
    row['status']='REPORTED' if exempt else 'MEASURED'
    return row


def measured_reading(readings, name):
    value=readings.get(name)
    if not isinstance(value,dict) or value.get('status') != 'MEASURED' \
            or value.get('native') is None or value.get('current') is None or value.get('B') is None:
        raise ValueError('UNMEASURED canonical statistic: '+name)
    return value


def complete_canonical(original, evidence):
    if key(evidence) != key(original) or evidence.get('role') != original['role'] \
            or evidence.get('status') != 'MEASURED':
        raise ValueError('UNMEASURED or wrong-key canonical reference evidence')
    preserved(original,evidence.get('reference', {}))
    row=copy.deepcopy(original); statistic=row['statistic']
    if statistic in ('T1-full-silhouette','T1-low') and row['profile'].endswith('-glass0.25'):
        if any(row.get(k) is None for k in ('native','current','B','fidelity')):
            raise ValueError('Original 0.25 T1 evidence is incomplete, not a refit input')
        return row
    readings=evidence['readings']
    if statistic in ('T1-full-silhouette','T1-low'):
        primary=measured_reading(readings,statistic)
        fidelity_name='T1-fine' if statistic=='T1-low' else 'T1-full-silhouette'
        fidelity=measured_reading(readings,fidelity_name)
        for name in ('native','current','B'): fill(row,name,primary[name])
        fill(row,'fidelity',dict(statistic=fidelity_name,native=fidelity['native'],
                                 current=fidelity['current'],reference=fidelity['current']))
    elif statistic == 'low-end-path-level':
        fields=({'deep8Far24LumaMean':'deep8-far24-luma-mean',
                 'deep8Far24LumaMedian':'deep8-far24-luma-median'} if row['scene'].startswith('impulse__') else
                {'deep8ChannelMedian':'deep8-channel-median'})
        selected={field:measured_reading(readings,name) for field,name in fields.items()}
        for name in ('native','current'):
            fill(row,name,{field:value[name] for field,value in selected.items()})
        # Preserve every individual source stop even when the scalar is representable.
        row['perFieldBudgets']={field:dict(statistic=fields[field], B=copy.deepcopy(value['B']),
            repeat=copy.deepcopy(value['repeat']),units=value['units'],support=value.get('support'))
            for field,value in selected.items()}
        summary=equal_budget([value['B'] for value in selected.values()])
        fill(row,'B',summary)
    else: raise ValueError('Unknown original canonical statistic')
    pins=evidence['pins']
    for name, source in (('nativeEvidence','native'),('currentEvidence','current'),('currentMetadata','currentMetadata')):
        fill(row,name,pins[source])
    row['canonicalReadings']=copy.deepcopy(readings)
    row['canonicalEvidence']=copy.deepcopy({k:evidence[k] for k in ('pins','source','runs')})
    if statistic in ('T1-full-silhouette','T1-low') and row['profile'].endswith('-glass0.5'):
        row['canonicalEvidence']['fidelityReference']=dict(kind='OWN_FROZEN_CURRENT',
            currentDocumentPair=copy.deepcopy(original['currentDocumentPair']),
            currentGeneration=original['currentGeneration'],currentEvidence=copy.deepcopy(row['currentEvidence']),
            currentMetadata=copy.deepcopy(row['currentMetadata']),statistic=row['fidelity']['statistic'],
            value=row['fidelity']['current'])
        if row['fidelity']['reference'] != row['fidelity']['current']:
            raise ValueError('New 0.5 fidelity reference differs from its own frozen current')
    row['status']='MEASURED'
    return row


def unique(rows, what, identity=key):
    if not isinstance(rows,list): raise ValueError('Missing '+what+' population')
    result={}
    for row in rows:
        k=identity(row)
        if k in result: raise ValueError('Duplicate '+what+' identity')
        result[k]=row
    return result


def same_pin(a, b, repo):
    def identity(item):
        if not isinstance(item,dict) or set(item) != {'path','sha256'} \
                or not isinstance(item['path'],str) or not isinstance(item['sha256'],str) \
                or len(item['sha256']) != 64 or any(c not in '0123456789abcdef' for c in item['sha256']):
            raise ValueError('Missing exact input content pin')
        path=PurePosixPath(item['path'])
        if '..' in path.parts: raise ValueError('Input pin escapes its original path')
        return (str(path if path.is_absolute() else PurePosixPath(repo)/path),item['sha256'])
    if identity(a) != identity(b): raise ValueError('Input pin differs from registered original identity')


def partition(original):
    if original.get('schema') != 'w50-reference-inventory-1' or not original.get('cells'):
        raise ValueError('Missing original G0 reference inventory')
    unique(original['cells'],'original reference')
    groups={name:[] for name in ('newbed','canonical','owners','blind')}
    for row in original['cells']:
        if row['role']=='blind': group='blind'
        elif row['statistic']=='owner-contracts': group='owners'
        elif row.get('nativeIdentity') and row['role'] in ('calibration','validation'): group='newbed'
        elif row['statistic'] in ('T1-low','T1-full-silhouette','low-end-path-level') \
                and row['role'] in ('gate','historical-prediction-check','reference-only'): group='canonical'
        else: raise ValueError('Original row has no declared completion source: '+str(key(row)))
        groups[group].append(row)
    return groups


def owner_join(originals, index, batch, documents, provenance, repo):
    if index.get('schema') != 'w50-owner-projection-index-1' or batch.get('schema') != 'w50-owner-evidence-batch-1':
        raise ValueError('Unknown source-owned owner batch/index')
    same_pin(index.get('source'),provenance['ownerBatch'],repo)
    same_pin(batch.get('inventoryPin'),provenance['original'],repo)
    same_pin(batch.get('contractsPin'),provenance['ownerContracts'],repo)
    entries=unique(index.get('rows'),'owner index',lambda row:tuple(row['key']))
    source=unique(batch.get('rows'),'source-owned owner batch',lambda row:key(row['row']))
    wanted={key(row) for row in originals}
    if set(entries) != wanted or set(source) != wanted or set(documents) != {r['evidence']['path'] for r in entries.values()}:
        raise ValueError('Owner index/batch/member population differs from original keys')
    result={}
    for row in originals:
        k=key(row); pin=entries[k]['evidence']; supplied=documents[pin['path']]; actual=source[k]
        if encoded(supplied) != encoded(actual) or actual.get('schema') != 'w50-owner-evidence-1' \
                or actual.get('cellId') != '/'.join(row[name] for name in KEY[:3]):
            raise ValueError('Owner projection differs from source-owned batch member')
        for field in ('inputsPin','reportPin','contractsPin'): same_pin(actual.get(field),batch.get(field),repo)
        same_pin(actual.get('ownerSource'),provenance['ownerSource'],repo)
        if row.get('B') is not None: raise ValueError('Original owner row has a scalar budget')
        completed=copy.deepcopy(row); completed.update(status='MEASURED',B=None,ownerEvidence=copy.deepcopy(pin))
        result[k]=completed
    return result


def assemble(original, current, canonical, owner_index, owner_batch, owner_documents, *,
             provenance, artifact_root, exemptions=(), empty_support_keys=(), repo='/'):
    """Join all and only original rows; return immutable inventory and a provenance-artifact plan.

    Inputs here are decoded, already content-verified documents. bound.py performs the registered
    hash/producer-root checks before calling this pure join. The pre-fit reader, not this function,
    remains the authority on the assembled rows and their materialized evidence.
    """
    groups=partition(original)
    if current.get('schema') != 'w50-completed-current-evidence-1' or current.get('status') != 'EVIDENCE_ONLY':
        raise ValueError('Only completed current-analysis evidence can be assembled')
    same_pin(current.get('originals',{}).get('references'),provenance['original'],repo)
    if canonical.get('schema') != 'w50-canonical-reference-evidence-1' or \
            canonical.get('purpose') != 'REFERENCE_EVIDENCE_ONLY_NOT_COEFFICIENT_INPUT':
        raise ValueError('Only registered canonical reference evidence can be assembled')
    same_pin(canonical.get('inputs',{}).get('inventory'),provenance['original'],repo)
    if canonical.get('originalReferences') != groups['canonical'] or \
            canonical.get('selectedKeys') != [list(key(row)) for row in groups['canonical']]:
        raise ValueError('Canonical report changed original selection/fields/order')
    partitions=canonical.get('partitions',{})
    if set(partitions) != {'gate','historical-prediction-check','reference-only'}:
        raise ValueError('Canonical role partitions differ')
    canonical_rows=[]
    for role,rows in partitions.items():
        if any(row.get('role') != role for row in rows): raise ValueError('Canonical row changed partition role')
        canonical_rows.extend(rows)
    natives=unique(current.get('referenceEvidence'),'completed newbed evidence')
    canonicals=unique(canonical_rows,'canonical reference evidence')
    if set(natives) != {key(r) for r in groups['newbed']} or set(canonicals) != {key(r) for r in groups['canonical']}:
        raise ValueError('Reference evidence omitted or added original cells')
    owners=owner_join(groups['owners'],owner_index,owner_batch,owner_documents,provenance,repo)
    artifacts=Artifacts(artifact_root); completed=copy.deepcopy(original); joined=[]
    for row in original['cells']:
        k=key(row)
        if row['role']=='blind':
            value=copy.deepcopy(row); value['status']='SEALED_BLIND'
        elif k in natives: value=complete_native(row,natives[k],artifacts,exemptions,empty_support_keys)
        elif k in canonicals: value=complete_canonical(row,canonicals[k])
        elif k in owners: value=owners[k]
        else: raise ValueError('Uncompleted original reference: '+str(k))
        preserved(row,value); joined.append(value)
    completed['cells']=joined
    return dict(schema='w50-reference-assembly-1',status='ASSEMBLED_EVIDENCE_ONLY',completed=completed,
        artifacts=artifacts.documents,inputs=copy.deepcopy(provenance),
        counts={name:len(rows) for name,rows in groups.items()},
        policy='ORIGINAL_FIELDS_RETAINED_NO_NEW_STATISTIC_NO_PREFIT_PASS_NO_RENDER_AUTHORITY')
