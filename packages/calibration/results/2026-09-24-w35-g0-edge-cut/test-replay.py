"""Replay deep bars from guarded lossless states with raw sitting access forbidden."""
import base64,gzip,json,sys,unittest
from pathlib import Path
import numpy as np
from edge import HERE,G1,W,I,geometry,bar

class Replay(unittest.TestCase):
    def test_normal_and_long_witnesses_from_archive(self):
        def deny_raw(event,args):
            if event=='open' and args and isinstance(args[0],(str,bytes)):
                p=str(args[0])
                if '/Users/new/vitrea-w34/' in p:raise AssertionError('raw sitting read')
        sys.addaudithook(deny_raw)
        declared=json.loads(gzip.decompress((HERE/'deep-bars.json.gz').read_bytes()))
        wave=W.default_wave();reader=wave.reader(G1/'repeat')
        # Maximum witnesses exercise non-unanimous normal and long states;
        # deepest bins exercise the new domain rather than W34's old six shells.
        for protocol in ['normal','long']:
            records=[r for r in declared if r['protocol']==protocol and r['runs']>=2]
            row=max(records,key=lambda r:max(max(b['barRGB']) for b in r['bins']))
            crop=json.loads(gzip.decompress(reader.read(row['cell'],'crop')))
            runs=[r for r in crop['runs'] if r['admitted'] and r['protocol']==protocol]
            states={s:I.unpack(base64.b64decode(crop['states'][s])) for s in {r['state'] for r in runs}}
            p=states[runs[0]['state']];d,nx,ny,arc,bins,whole=geometry(p)
            # Check every shell on each maximum-witness cell, including zero
            # envelopes, not just the previously recorded six contour shells.
            for b in row['bins']:
                mask=(arc if b['part']=='arc' else ~arc)&(bins==b['bin'])&(d>=b['shell'])&(d<b['shell']+1)
                self.assertEqual(int(mask.sum()),b['pixels'])
                images=[states[r['state']]['rgb'][mask] for r in runs]
                np.testing.assert_array_equal(bar(images),b['barRGB'])
            self.assertLess(min(b['shell'] for b in row['bins']),-6)

if __name__=='__main__':unittest.main()
