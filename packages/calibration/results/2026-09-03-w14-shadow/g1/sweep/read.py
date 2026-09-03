"""Read the W14 G1 sweep's quantities out of point matrices."""
import json, os, sys, glob

def cells(path):
    return json.load(open(path))['cells']

def key(c):
    return (c['key']['profileKey'], c['key']['sceneId'], c['tier'])

def band(cell, which, direction, ring):
    for s in cell.get('shadow', {}).get(which, []) or []:
        if s['direction'] == direction and s['ringLabel'] == ring:
            return s
    return None

def pair(cell, which, direction='below', ring='3-6'):
    b = band(cell, which, direction, ring)
    if b is None or 'slopeALinear' not in b:
        return (None, None)
    return (b['slopeALinear'], b['interceptCLinear'])

def v(cell, axis, field):
    r = cell.get(axis) or {}
    x = r.get(field)
    return None if x is None else x['value']

def level(cell, which, direction='below', ring='3-6'):
    b = band(cell, which, direction, ring)
    if b is None: return (None, None)
    return (b.get('renderedLevelLinear'), b.get('backdropMeanLinear'))

def occl(cell, which, direction='below', ring='3-6'):
    """(bg - level)/bg off the band."""
    lv, bg = level(cell, which, direction, ring)
    if lv is None or not bg: return None
    return (bg - lv) / bg

def fmt(x, n=5):
    return '   —   ' if x is None else f'{x:.{n}f}'
