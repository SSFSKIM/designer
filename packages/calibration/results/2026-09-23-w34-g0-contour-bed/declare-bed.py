#!/usr/bin/env python3
"""Generate the sparse crossed bed and audit semantic twins before its split (§5.174).

The phase axis is omitted only on the separately recorded scratch finding. The
full crossed product is never generated and silently trimmed afterwards.
"""
import copy
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]


def write(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic(value):
    return {k:semantic(v) if isinstance(v,dict) else v for k,v in value.items()
            if not k.startswith('$') and k not in ['opaque','fillSRGB']}


def main():
    phase=json.loads((HERE/'phase-reading.json').read_text())
    if phase['verdict']!='UNREACHABLE at 1x and 2x':
        raise SystemExit('Phase omission needs both scales measured, not an assumed snap')
    old=json.loads((ROOT/'apps/reference-apple/scenes.json').read_text())
    bg={f'grey-{v}':{'kind':'solid','srgb':[v,v,v]} for v in [0,32,64,96,128,160,208,255]}
    for name,rgb in zip(['red','green','blue','yellow','magenta','cyan'],
                       [[192,32,32],[32,192,32],[32,32,192],[192,192,32],[192,32,192],[32,192,192]]):
        bg[name]={'kind':'solid','srgb':rgb}
    for angle in [0,45,90,135]:
        for magnitude,a,b in [('small',96,160),('large',32,224)]:
            bg[f'gradient-{angle}-{magnitude}']={'kind':'linear-gradient','from':[a]*3,'to':[b]*3,'angle':angle}
    for axis,position in [('x',100),('y',78)]:
        for outside in [64,192]:
            bg[f'local-{axis}-{outside}']={'kind':'split','from':[outside]*3,'to':[128]*3,
                                         'axis':axis,'position':position}
    for name in ['checkerboard-4','checkerboard','checkerboard-64']:bg[name]=copy.deepcopy(old['backgrounds'][name])
    sweep=list(bg)
    for name in ['light-solid','dark-solid','photo']:bg[name]=copy.deepcopy(old['backgrounds'][name])
    components={
        'circular-120':{'kind':'capsule-circular','size':[120,44]},
        'capsule-button':copy.deepcopy(old['components']['capsule-button']),
        'circular-160':{'kind':'capsule-circular','size':[160,96]},
        'continuous-160':{'kind':'capsule','size':[160,96]},
        'circular-200':{'kind':'capsule-circular','size':[200,44]},
        'continuous-200':{'kind':'capsule','size':[200,44]},
        'rectangle-120':{'kind':'rrect','size':[120,44],'radius':12},
    }
    geometries=list(components)
    for geometry in geometries:
        for fill in [0,255]:components[f'{geometry}-opaque-{fill}']={**components[geometry],'opaque':True,'fillSRGB':[fill]*3}
    components['none']={'kind':'none'}
    pairs=[(b,'circular-120') for b in sweep]
    pairs += [(b,c) for c in geometries[1:] for b in ['grey-128','grey-255','red']]
    pairs += [(b,'capsule-button') for b in ['light-solid','dark-solid','photo','checkerboard']]
    pairs += [('grey-255' if fill==0 else 'grey-0',f'{c}-opaque-{fill}')
              for c in geometries for fill in [0,255]]
    pairs += [(b,'none') for b in bg]
    scenes=[{'id':f'{b}__{c}__{pose}','background':b,'component':c,'state':pose}
            for pose in ['rest','inactive'] for b,c in pairs]
    # Compare declarations, never open a canonical holdout pixel. The geometry/
    # backdrop rule is conservative across tint and pose; controls are not glass.
    old_roles={sid:role for role,ids in old['split'].items() if not role.startswith('$') for sid in ids}
    audit=[]
    for scene in scenes:
        c=components[scene['component']]
        twins=[]
        if c['kind']!='none' and not c.get('opaque'):
            for previous in old['scenes']:
                if previous.get('label'):continue
                if semantic(c)==semantic(old['components'][previous['component']]) and \
                        semantic(bg[scene['background']])==semantic(old['backgrounds'][previous['background']]):
                    twins.append({'scene':previous['id'],'role':old_roles[previous['id']],
                                  'pose':previous['state'],'tint':previous.get('tint')})
        audit.append({'scene':scene['id'],'canonicalTwins':twins,
                      'excluded':any(t['role']=='holdout' for t in twins)})
    excluded={row['scene'] for row in audit if row['excluded']}
    # Conservative geometry/backdrop twins stay only on the wave holdout,
    # even where the canonical twin differs in tint or pose. They never enter
    # calibration, validation or the published bar.
    # The audit is computed before any identification membership is assigned.
    split={r:[] for r in ['calibration','validation','holdout']}
    for scene in scenes:
        b,c=scene['background'],scene['component']
        if scene['id'] in excluded or c.startswith(('circular-160','continuous-200')) or b in ['grey-208','gradient-135-large']:
            role='holdout'
        elif c.startswith('continuous-160') or b in ['grey-96','cyan','gradient-45-small','gradient-90-large']:
            role='validation'
        else:role='calibration'
        split[role].append(scene['id'])
    profiles=[]
    for scale in [1,2]:
        for scheme in ['light','dark']:
            ids=[s['id'] for s in scenes if scheme=='light' or
                 (components[s['component']]['kind']!='none' and not components[s['component']].get('opaque'))]
            profiles.append({'key':f'apple-macos-27.0-{scale}x-{scheme}-standard-glass0.5',
                             'colorScheme':scheme,'a11y':'standard','scenes':ids})
    doc={'version':1,'$comment':{
        'purpose':'W34 contour identification; probe only; no canonical bed changes.',
        'colours':'Circular 120x44 anchor carries eight greys and six chromatic solids.',
        'structure':'Eight encoded gradients, four matched local-colour steps, pitches 4/16/64.',
        'geometry':'Six matched geometry contrasts over grey128, white and red; full colour product declined.',
        'controls':'Every backdrop has a no-glass reference; seven paths have both opaque high-contrast fills. Controls captured in light only, separately in both poses/scales; these are native-only.',
        'phase':'UNREACHABLE at both scales by scratch capture. No window-origin workaround. Phase evidence hash '+sha(HERE/'phase-reading.json'),
        'bridge':'Canonical capsule over light-solid, dark-solid, photo and checkerboard; canonical holdout twins audited before split.',
        'split':'All fixture roles probe. Identification uses the pinned wave-local split and wave.py, never bare --set probe.',
        'sentinels':'Grey128 and checkerboard circular anchor also run three times at initial-settle8 with seed3401; normal seven-run sitting remains separate.'},
        'canvas':{'width':320,'height':200},'backgrounds':bg,'components':components,'tints':{},
        'scenes':scenes,'profiles':profiles,
        'split':{'calibration':[],'validation':[],'holdout':[],'probe':[s['id'] for s in scenes]}}
    write(HERE/'semantic-twin-audit.json',{'canonicalScenesSha256':sha(ROOT/'apps/reference-apple/scenes.json'),
          'compared':['geometry','backdrop declaration'],'poseAndTint':'Recorded beside matches, not used to excuse a geometry/backdrop twin.','rows':audit,
          'excludedFromFitAndBar':sorted(excluded),'disposition':'Retained as identification holdout only','holdoutPixelsOpened':False})
    write(ROOT/'apps/reference-apple/scenes-w34-contour.json',doc)
    write(HERE/'split.json',split)
    write(HERE/'pins.json',{'scenesSha256':sha(ROOT/'apps/reference-apple/scenes-w34-contour.json'),
          'splitSha256':sha(HERE/'split.json'),'phaseReadingSha256':sha(HERE/'phase-reading.json')})
    print('scenes',len(scenes),'split',{k:len(v) for k,v in split.items()},'excluded',sorted(excluded))


if __name__=='__main__':main()
