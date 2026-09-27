"""Copy already saved, guarded calibration bundles; never create an archive Reader."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
STROKE=HERE.parent
SOURCES=[(1, STROKE/'m0-certificate/white-extension'),
         (2, STROKE/'neutral-ratio-certificate/scale2')]
GENERATION='58329732f947d42cd5e1518962016191faaa79d89b7089c6dadf5724dde35f61'


def sha(raw): return hashlib.sha256(raw).hexdigest()


def main():
    out=HERE/'inputs'; out.mkdir(exist_ok=False)
    records=[]; sources=[]
    for scale,root in SOURCES:
        raw=(root/'manifest.json').read_bytes(); manifest=json.loads(raw)
        if scale==2:
            assert sha(raw)=='b7868018335cfbac95fb0de18e236af661c6166e7d0b28e5828007109cd01e2a'
        assert manifest['archiveGeneration']==GENERATION and manifest['roles']==['calibration']
        assert len(manifest['records'])==16
        sources.append(dict(scale=scale,path=str(root/'manifest.json'),sha256=sha(raw)))
        (out/f'source-manifest-{scale}x.json').write_bytes(raw)
        for row in manifest['records']:
            assert row['role']=='calibration' and row['archiveEntry']['admitted']
            assert f'-{scale}x-' in row['cell'] and row['cell'].endswith('__inactive')
            payload=(root/row['file']).read_bytes()
            assert sha(payload)==row['sha256']==row['archiveEntry']['sha256']
            file=f"{row['endpoint']}-{scale}x-{row['b']}.bundle"
            with (out/file).open('xb') as f: f.write(payload)
            records.append(dict(**{k:v for k,v in row.items() if k!='file'},
                                scale=scale,file=file,copiedFrom=str((root/row['file']).resolve())))
    assert len({r['cell'] for r in records})==32
    value=dict(schema='w41-css-width-saved-inputs-1',archiveGeneration=GENERATION,
               roles=['calibration'],newArchiveReads=0,sources=sources,records=records)
    (out/'manifest.json').write_text(json.dumps(value,indent=2)+'\n')
    print('Copied32 existing calibration bundles; no archive reader, no new native read.')


if __name__=='__main__':main()
