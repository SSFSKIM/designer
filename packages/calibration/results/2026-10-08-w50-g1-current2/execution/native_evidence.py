"""DL5g typed native provenance, without changing the sealed native reader.

Three native runs remain three runs. Their archived index entries and real PNG bytes are
bound to the role report and original reference identity/support, not replaced by a single
run or a material document. This validates PNG structure/hashes, never decodes image pixels.
"""
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import zlib

KEY=('profile','renderer','scene','statistic')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def same(a,b):
    return json.dumps(a,sort_keys=True,allow_nan=False)==json.dumps(b,sort_keys=True,allow_nan=False)


class NativeEvidence:
    def __init__(self,repo,manifest_pin=None):
        self.repo=Path(repo).resolve();self.manifest_pin=manifest_pin
        self.pins={};self.values={};self.pngs={};self.indexes={};self.cells={};self.blind_original_rows={}

    def check(self,pin):
        if not isinstance(pin,dict) or not isinstance(pin.get('path'),str) or \
                not isinstance(pin.get('sha256'),str) or not re.fullmatch('[0-9a-f]{64}',pin['sha256']):
            raise ValueError('Missing native/capture content pin')
        path=(self.repo/pin['path']).resolve()
        if path in self.pins:
            if self.pins[path]!=pin['sha256']:raise ValueError('Conflicting native/capture pin')
        elif not path.is_file() or sha(path)!=pin['sha256']:
            raise ValueError('Changed or missing native/capture evidence')
        self.pins[path]=pin['sha256'];return path

    def read(self,pin):
        path=self.check(pin)
        if path not in self.values:
            raw=path.read_bytes()
            self.values[path]=json.loads(gzip.decompress(raw) if path.name.endswith('.json.gz') else raw)
        return self.values[path]

    def png(self,pin,dimensions):
        path=self.check(pin)
        if path in self.pngs:
            if self.pngs[path]!=dimensions:raise ValueError('PNG dimensions differ from declared capture')
            return path
        raw=path.read_bytes()
        if raw[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError('Evidence is not a PNG image')
        offset=8;first=True;data=False;ended=False
        while offset<len(raw):
            if offset+12>len(raw):raise ValueError('Truncated PNG chunk')
            size=int.from_bytes(raw[offset:offset+4],'big');name=raw[offset+4:offset+8]
            end=offset+12+size
            if end>len(raw):raise ValueError('Truncated PNG content')
            chunk=raw[offset+8:offset+8+size]
            crc=int.from_bytes(raw[offset+8+size:end],'big')
            if zlib.crc32(name+chunk)!=crc:raise ValueError('PNG chunk checksum mismatch')
            if first:
                if name!=b'IHDR' or size!=13 or list(struct.unpack('>II',chunk[:8]))!=dimensions:
                    raise ValueError('PNG header/dimensions do not match declared native capture')
                first=False
            if name==b'IDAT':data=True
            if name==b'IEND':
                if size or end!=len(raw):raise ValueError('Malformed PNG ending')
                ended=True
            offset=end
        if not data or not ended:raise ValueError('PNG lacks image data or ending')
        self.pngs[path]=dimensions;return path

    def _blind_authority(self,row,envelope,context):
        dispatcher=sys.modules.get('w50_g1_dispatch')
        if dispatcher is None:raise ValueError('Blind native evidence is exposure-only')
        dispatcher.require_context(context)
        if not isinstance(context,dict) or context.get('phase')!='exposure':
            raise ValueError('Blind native evidence is exposure-only')
        if 'nativeBatch' in envelope or not envelope.get('nativeExposure'):
            raise ValueError('Blind evidence requires the actual one-shot exposure artifact chain')
        artifact=self.read(envelope['nativeExposure'])
        if artifact.get('schema')!='w50-native-exposure-artifacts-1' or artifact.get('role')!='blind' or \
                artifact.get('ready') is not True or artifact.get('nativeRead')!=envelope['nativeRead']:
            raise ValueError('Wrong or incomplete blind native exposure artifact')
        claim=self.read(artifact.get('claim'))
        if claim.get('schema')!='w50-native-blind-claim-1' or claim.get('role')!='blind':
            raise ValueError('Blind native evidence lacks its one-shot claim')
        for name,path in [('dispatcherContract',context['contract']),
                          ('dispatcherClaim',context['contract']+'.started.json'),('batch',context['batchPath'])]:
            if self.check(claim.get(name))!=Path(path).resolve():
                raise ValueError('Blind native evidence belongs to another exposure invocation')
        config_pin=claim.get('config')
        if config_pin not in context['inputs']:raise ValueError('Blind native config is not root-bound')
        config=self.read(config_pin)
        if config.get('schema')!='w50-native-exposure-inputs-1':raise ValueError('Wrong blind native config')
        original_root=Path(config.get('archiveRoot',''))
        if not original_root.is_absolute():raise ValueError('Blind native config lacks original archive identity')
        original_index=self.read({'path':str(original_root/'index.json'),'sha256':config.get('archiveIndexSha256')})
        if original_index.get('schema')!='w50-role-archive-1':raise ValueError('Wrong original native archive schema')
        original_rows={}
        for entry in original_index.get('files',[]):
            if entry.get('kind')!='frame' or 'blind' not in entry.get('roles',[]):continue
            identity=(entry.get('cell'),entry.get('run'))
            if identity in original_rows:raise ValueError('Ambiguous original native archive member')
            original_rows[identity]=entry
        self.blind_original_rows=original_rows
        export={'role':'blind','root':artifact['export']['path'],'indexSha256':artifact['export']['indexSha256']}
        if envelope.get('nativeExport')!=export:raise ValueError('Blind native export differs from admitted exposure')
        if self.manifest_pin is not None and (self.check(config.get('manifest')) != self.check(self.manifest_pin) or
                config['manifest']['sha256'] != self.manifest_pin['sha256']):
            raise ValueError('Blind native exposure names another original bed')
        manifest=self.read(config['manifest'])
        dependencies=[d for d in manifest.get('references',[]) if d.get('id')==row['referenceIdentity']]
        if len(dependencies)!=1 or 'blind' not in dependencies[0].get('roles',[]):
            raise ValueError('Blind no-glass dependency lacks its original declared role set')
        return config['partOne']['sha256'], dependencies[0]['roles']

    def validate(self,row,pin,exposure=None):
        # Refuse even opening a blind envelope outside the real live exposure capability.
        if row.get('role')=='blind':
            dispatcher=sys.modules.get('w50_g1_dispatch')
            if dispatcher is None:raise ValueError('Blind native evidence is exposure-only')
            dispatcher.require_context(exposure)
            if exposure.get('phase')!='exposure':raise ValueError('Blind native evidence is exposure-only')
        envelope=self.read(pin)
        names=('profile','scene','nativeIdentity','referenceIdentity','role','support','statistic')
        if envelope.get('schema')!='w50-native-three-run-evidence-1' or any(envelope.get(k)!=row.get(k) for k in names):
            raise ValueError('Native three-run envelope changed original identity/support/statistic')
        if row['nativeIdentity']!=row['profile']+'/'+row['scene'] or not isinstance(row.get('support'),str) or not row['support']:
            raise ValueError('Native evidence requires original reference identity and support prose')
        export=envelope.get('nativeExport',{})
        if export.get('role')!=row['role'] or not isinstance(export.get('root'),str) or not Path(export['root']).is_absolute():
            raise ValueError('Native envelope has another role/export root')
        if row['role']=='blind':
            declaration,dependency_roles=self._blind_authority(row,envelope,exposure)
        else:
            if row['role'] not in ('calibration','validation') or 'nativeExposure' in envelope:
                raise ValueError('Exposed native envelope cannot impersonate blind exposure')
            batch=self.read(envelope.get('nativeBatch'))
            if batch.get('schema')!='w50-native-read-batch-1' or export not in batch.get('exports',[]):
                raise ValueError('Native export is not bound to the exposed native batch')
            declaration_pin=batch.get('inputs',{}).get('declaration');self.check(declaration_pin)
            declaration=declaration_pin['sha256'];dependency_roles=[row['role']]
            if self.manifest_pin is not None:
                actual=batch.get('inputs',{}).get('manifest')
                if self.check(actual)!=self.check(self.manifest_pin) or actual['sha256']!=self.manifest_pin['sha256']:
                    raise ValueError('Native batch names another original bed manifest')
        report=self.read(envelope.get('nativeRead'))
        if (report.get('schema')!='w50-native-role-read-1' or report.get('role')!=row['role'] or
                report.get('indexSha256')!=export.get('indexSha256') or
                report.get('declarationSha256')!=declaration or report.get('ready') is not True or report.get('stops')!=[]):
            raise ValueError('Native read is not a complete same-role admitted report')
        export_root=Path(export['root']).resolve()
        index=self.read({'path':str(export_root/'index.json'),'sha256':export['indexSha256']})
        if index.get('schema')!='w50-role-archive-1':raise ValueError('Missing native role archive index')
        index_key=(str(export_root),export['indexSha256'])
        if index_key not in self.indexes:
            entries={}
            for entry in index.get('files',[]):
                identity=(entry.get('cell'),entry.get('run'))
                if identity in entries:raise ValueError('Ambiguous native role-index identity')
                entries[identity]=entry
            self.indexes[index_key]=entries
        report_key=self.check(envelope['nativeRead'])
        if report_key not in self.cells:
            entries={}
            for entry in report.get('cells',[]):
                identity=(entry.get('profile'),entry.get('scene'))
                if identity in entries:raise ValueError('Ambiguous native report identity')
                entries[identity]=entry
            self.cells[report_key]=entries
        cell=self.cells[report_key].get((row['profile'],row['scene']))
        if not cell:raise ValueError('Native report identity absent')
        runs=cell.get('runs',[])
        if cell.get('id')!=row['nativeIdentity'] or cell.get('reference')!=row['referenceIdentity'] or \
                cell.get('role')!=row['role'] or [r.get('run') for r in runs]!=[1,2,3] or \
                envelope.get('runs')!=[r.get('evidence') for r in runs] or any(r.get('dependency')!=row['referenceIdentity'] for r in runs):
            raise ValueError('Native envelope must retain all three exact run/dependency records')
        if 'native' in row and not same(cell.get('statistics',{}).get(row['statistic'],{}).get('value'),row['native']):
            raise ValueError('Native reference reading differs from its three-run aggregate')
        scale=re.search(r'-([12])x-',row['profile'])
        if not scale or report.get('canvas')!={'width':512,'height':384}:raise ValueError('Native canvas/scale differs')
        dimensions=[512*int(scale[1]),384*int(scale[1])]
        dependency=[d for d in report.get('dependencies',[]) if d.get('id')==row['referenceIdentity']]
        if len(dependency)!=1:raise ValueError('Native report lacks its exact no-glass dependency')
        for evidence,identity in [(r['evidence'],row['nativeIdentity']) for r in runs]+[(dependency[0]['evidence'],row['referenceIdentity'])]:
            expected_roles=dependency_roles if identity==row['referenceIdentity'] else [row['role']]
            if (evidence.get('cell')!=identity or evidence.get('roles')!=expected_roles or evidence.get('kind')!='frame' or
                    evidence.get('declarationSha256')!=declaration or not same(
                        self.indexes[index_key].get((identity,evidence.get('run'))),evidence)):
                raise ValueError('Native record differs from its role index/declared sitting')
            if row['role']=='blind' and not same(self.blind_original_rows.get((identity,evidence['run'])),evidence):
                raise ValueError('Blind native frame differs from the root-pinned original archive')
            image=(export_root/evidence['path']).resolve()
            if not image.is_relative_to(export_root):raise ValueError('Native image escapes role export')
            metadata=evidence.get('native',{})
            if metadata.get('sceneId')!=identity.split('/')[-1] or metadata.get('file')!=identity+'.png' or \
                    [metadata.get('width'),metadata.get('height')]!=dimensions:
                raise ValueError('Native metadata identity/dimensions differ from actual frame')
            self.png({'path':str(image),'sha256':evidence['sha256']},dimensions)
        return envelope

    def finish(self):
        for path,digest in self.pins.items():
            if not path.is_file() or sha(path)!=digest:raise ValueError('Native/capture evidence changed during validation')
