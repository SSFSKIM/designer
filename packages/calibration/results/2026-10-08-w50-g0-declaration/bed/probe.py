"""Prospective native closure exercise: synthetic arrays/files, no native launch or held read."""
import importlib.util
import io
from pathlib import Path
import tempfile
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('w50_native_entrypoint', HERE/'sitting/w50.py')
W = importlib.util.module_from_spec(spec)
spec.loader.exec_module(W)
W.dry_imports()                           # trusted prospective closure discovery, no CLI bypass
W.dry_exercise()
W.B.verify()                              # live pin check also imports the W42 timing estimator
W.configure(HERE/'sitting-g1.json')
W.load('w50_root_declaration', HERE.parent/'declare.py')
W.load('w50_native_next_wave', HERE.parent/'audit/next_wave.py')
C = W.load('w50_cuts', HERE/'sitting/cuts.py')
A = W.load('w50_archive', HERE/'sitting/archive.py')
image = np.full((384,512,3),20,dtype=np.uint8)
reading = C.read(image, {'kind':'rrect','size':[280,160],'radius':34}, 1)
assert C.repeat_verdict([reading]*3)['passes']
assert C.sentinel_verdict(reading,reading)['passes']
W.S.classify([dict(pid=1,executable='/bin/node',argv=['node','compare.ts'])])
W.S.grant_row([])
with tempfile.TemporaryDirectory(prefix='w50-native-probe-') as td:
    source=Path(td)/'source'; source.mkdir()
    (source/'synthetic').write_bytes(b'synthetic, no pixels')
    A.write_archive(source,Path(td)/'archive',[dict(path='synthetic',sha256=A.sha(b'synthetic, no pixels'),
                    roles=['calibration'],kind='frame')])
    A.export_role(Path(td)/'archive',Path(td)/'calibration','calibration')
    A.verify_archive(Path(td)/'calibration')
    assert W.S.restore(lambda: {'restored':True},lambda: {'restored':True})['restored']
# Exercise the non-identity numerical bridge branch, not merely its hash fast path.
def png(level):
    stream=io.BytesIO()
    Image.new('RGB',(320,200),(level,)*3).save(stream,format='PNG')
    return stream.getvalue()
assert not W.S.driver().bridge_verdict(png(40),png(50),{'kind':'solid','srgb':[28,28,30]},
    {'kind':'rrect','size':[280,160],'radius':34},1,'dark','receded')['agrees']
