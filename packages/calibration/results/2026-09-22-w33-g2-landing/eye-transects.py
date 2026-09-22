#!/usr/bin/env python3.12
"""Resolve the eye's suspected banding using raw stored pixels, not resized previews (§5.173)."""
import json
from pathlib import Path
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
path=HERE/'laws-shadow-active-160.png'
a=np.array(Image.open(path).convert('RGB'),dtype=float)
luma=a@np.array([.2126,.7152,.0722])


def read(label, positions, values):
    centered=values-values.mean()
    spectrum=np.abs(np.fft.rfft(centered));spectrum[0]=0
    k=int(np.argmax(spectrum))
    # Read the known painted 64-device-px period without silently rounding it
    # to the FFT bin. A linear nuisance trend is included, but never removed
    # from the recorded raw min/max or the requested transect.
    q=np.column_stack([np.ones(len(positions)),positions-positions.mean(),
        np.sin(2*np.pi*positions/64),np.cos(2*np.pi*positions/64)])
    fitted=np.linalg.lstsq(q,values,rcond=None)[0]
    row=dict(label=label,coordinates=positions.tolist(),encodedLumaBytes=values.tolist(),
             count=len(values),minimum=float(values.min()),maximum=float(values.max()),
             peakToPeakBytes=float(np.ptp(values)),standardDeviationBytes=float(values.std()),
             fftDominantPeriodDevicePx=float(len(values)/k) if k else None,
             period64PeakToPeakBytes=float(2*np.hypot(fitted[2],fitted[3])))
    print(label,{k:v for k,v in row.items() if k not in ('coordinates','encodedLumaBytes','label')})
    return row

rows=[]
xs=np.arange(100,681);ys=np.arange(120,401)
rows.append(read('requested horizontal y=250, x=100..680; crosses the 160px text',xs,luma[250,xs]))
rows.append(read('requested vertical x=300, y=120..400; no text',ys,luma[ys,300]))
# Matched, label-free interior transects. Their low signal is not a reason to
# treat contour/lens edge variation as the body's global modulation.
xs=np.arange(160,321);ys=np.arange(176,337)
rows.append(read('label-free horizontal core y=200, x=160..320',xs,luma[200,xs]))
rows.append(read('label-free vertical core x=300, y=176..336',ys,luma[ys,300]))
# Near-top row shows whether a faint surviving checker has both polarities in y.
xs=np.arange(192,321)
rows.append(read('near-top horizontal y=128, x=192..320',xs,luma[128,xs]))
rows.append(read('near-top horizontal y=160, x=192..320',xs,luma[160,xs]))
(HERE/'eye-transects.json').write_text(json.dumps(dict(source=path.name,
    luma='encoded RGB byte dot (0.2126,0.7152,0.0722); not linear-light luminance',
    note='Raw requested horizontal crosses the dark 160px label; not a material-only signal.',
    transects=rows),indent=2)+'\n')
