#!/usr/bin/env python3
"""Refresh measured witnesses after the sanctioned read, retaining prior digits (§5.172).

These are readings, not bounds. The existing owner tests still derive the missed
set and every adopted threshold remains unchanged. Prior table bytes are kept
beside the replacement rather than erased from the source's measurement history.
"""
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
CAL=HERE.parent.parent
cells=json.loads((CAL/'results/matrix.json').read_text())['cells']
chroma=json.loads((HERE/'chroma-cut.json').read_text())['cells']
byname={f"{c['tier']} / {c['fixtureSet']} / {c['key']['sceneId']} / {c['key']['profileKey']}":c for c in cells}
p=CAL/'test/adopted-thresholds.test.ts'
s=p.read_text(); start=s.index('const MISSED_27_ROWS:'); stop=s.index('\n};',start)+3
block=s[start:stop]; moves=[]
pattern=r'("([^"\n]+) :: ([^"\n]+)": \{ measured: )([0-9.]+)'
def replace(m):
    name,metric,old=m[2],m[3],float(m[4])
    cell=byname[name]
    if metric=='chromaStructureRatioR':
        value=next(c['R'] for c in chroma if c['profile']==cell['key']['profileKey'] and c['scene']==cell['key']['sceneId'])
    else:
        values=[v[metric]['value'] for v in cell.values() if isinstance(v,dict) and metric in v]
        assert len(values)==1,(name,metric)
        value=values[0]
    if round(value,5)==old:return m[0]
    moves.append(dict(kind='MISSED_27_ROWS',name=name,metric=metric,before=old,value=value))
    return m[1]+f'{value:.5f}'
new=re.sub(pattern,replace,block)
notes=''.join(f"// W33 G1b (§5.172): {m['name']} :: {m['metric']}\n// measured {m['before']:.5f} -> {m['value']:.5f}; still missed, bound unchanged.\n" for m in moves)
p.write_text(s[:start]+notes+new+s[stop:])
p=CAL/'test/tier-coherence.test.ts'; s=p.read_text()
start=s.index('  const RECORDED: Record<string, { webgpu: number; css: number }> = {')
stop=s.index('\n  };',start)+5
oldblock=s[start:stop]
profiles=re.findall(r'"(apple-macos-27[^\"]+)":',oldblock)
readings={}
for profile in profiles:
    readings[profile]={}
    for renderer in ('webgpu','css'):
        c=next(c for c in cells if c['key']['profileKey']==profile and c['key']['sceneId']=='checkerboard__rrect-md__rest' and c['key']['web']['renderer']==renderer)
        value=c['material']['interiorStdDevWeb']['value']/c['material']['interiorStdDevNative']['value']
        readings[profile][renderer]=round(value,6)
        moves.append(dict(kind='structure witness',profile=profile,renderer=renderer,value=value))
newblock='  const RECORDED: Record<string, { webgpu: number; css: number }> = {\n'+''.join(
    f'    "{p}": {{ webgpu: {v["webgpu"]:.6f}, css: {v["css"]:.6f} }},\n' for p,v in readings.items())+'  };'
note='''  /*
   * W33 G1b (§5.172): re-recorded after the sealed lift/anchor read. The mask is
   * native-derived; these are changed rendered values, not a moved extractor.
   * No structure constant or bound moved. W32's prior table is retained below.
'''+''.join('   * '+line.strip()+'\n' for line in oldblock.splitlines())+'   */\n'
p.write_text(s[:start]+note+newblock+s[stop:])
(HERE/'witness-moves.json').write_text(json.dumps(moves,indent=2)+'\n')
print('Refreshed current witnesses; prior readings retained, bounds unchanged.')
