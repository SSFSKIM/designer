"""W42 G0 instrument: the depth-graded radius reader (charter Design, "The instrument"; the bed's family C
depth sweep: S 8 at the centre, s/4 and 4 pt from the edge on rrect-md and rrect-lg).

The declared active opacity is 0.8t at the centre falling linearly in depth to 0.4t at 1 pt inside the edge,
and memo E reads that opacity as the narrow blur's radius scale, sigma_n = k 5 o(d). This reader measures
sigma_n at each patch's depth and returns the RATIO sigma_n(d) / sigma_n(centre) beside the o-law's ratio
o(d) / o(centre) at the patch's centre depth, so the law is tested without k: the ratio is 0.5 at 1 pt
inside the edge whatever k is. In the receded pose the declared opacity is flat in depth, so the same sweep
is a free falsification control and must read a ratio of 1.

Each depth is read by the patch reader on a SMALL window (R_DEPTH pt around the cell's declared patch,
bed.json's patchCentre), so the width it reads is local, with sigma_w and lam held at the centre patch's read
(they are the same at every depth under every declared family) and w and the gain free. Pixels are the
cell's declared deep mask. In the ACTIVE pose that mask sits beyond the inner-refraction band plus two
narrow widths (forward.band_d_in; the parent's ruling on the bed stream's finding), because LT models no
refraction: the patches 4 pt from the edge lie inside the band and are excluded (bed.refraction_exclusions),
and each row reports its band status (outside / across / inside). The grading law is therefore read in the
active pose only between the deepest patches the band leaves: rrect-lg's 80 and 40 pt, and rrect-md's 48
and 24 pt, whose 24-pt patch (content 20-28 pt) is read only on its inner side (the mask starts at 25.6).
"""
import numpy as np

import forward as F
import read_patch as P

R_DEPTH = 16.0
MIN_PX = 60


def _support(cell, reading):
    """W's support for the held read: the canvas for vitrea's linear control; LT's declared R_fp and edge
    mode (clamp active, normalised receded) in the native reading."""
    if reading == 'linear':
        return (('canvas', 'clamp', None),)
    return (('box', 'clamp' if cell.active else 'norm', None),)


def target_patch(cell):
    """(label, cy, cx) of the patch the cell declares (bed.json's patchCentre), else the deepest one."""
    cen = P.patch_centres(cell)
    g = getattr(cell, 'geometry', None) or {}
    if 'patchCentre' in g:
        px, py = g['patchCentre']
        return min(cen, key=lambda r: (r[2] - px) ** 2 + (r[1] - py) ** 2)
    s = cell.scale
    return max(cen, key=lambda r: -cell.d[int(r[1] * s), int(r[2] * s)])


def patch_depth(cell):
    """Depth (pt, positive inside) of the target patch's centre."""
    _, cy, cx = target_patch(cell)
    s = cell.scale
    return float(-cell.d[int(cy * s), int(cx * s)])


def band_status(cell, depth, size, R):
    """Where the read sits against the active inner-refraction band (forward.BAND_IN): 'receded (no band)';
    'outside' when the patch and every pixel the window reads are beyond the band; 'across' when the window's
    shallow side reaches the band but the declared mask cuts it (the patch itself beyond the band); 'inside'
    when the patch itself reaches into the band."""
    if not cell.active:
        return 'receded (no band)'
    near = depth - size / 2
    if near < F.BAND_IN:
        return 'inside'
    return 'outside' if near - R >= F.BAND_IN else 'across'


def olaw_ratio(cell, depth, centre_depth):
    o = F.opacity_law(np.array([-depth, -centre_depth]), cell.span, cell.active)
    return float(o[0] / o[1]) if o[1] > 0 else float('nan')


def read(depth_cells, reading='native', sw=None, lam=None, centre=None, R=R_DEPTH, d_in=None):
    """depth_cells: [(label, cell)] each declaring one target patch, the centre first unless `centre` names
    it. Pixels: the cell's declared deep mask (d_in None), which in the active pose already sits beyond the
    refraction band (forward.band_d_in). Returns per label: depth, sigma_n and its interval, the ratio to the
    centre, the o-law's ratio and the band status; a patch with fewer than MIN_PX readable pixels near it is
    reported UNREAD."""
    labels = [lb for lb, _ in depth_cells]
    centre = centre or labels[0]
    cells = dict(depth_cells)
    c0 = cells[centre]
    t0 = target_patch(c0)[0]
    pix0 = P.reader_mask(c0, R=48.0, d_in=d_in, which=t0)
    sup = _support(c0, reading)
    ref = P.read([(c0, pix0)], reading, sw=sw, lam=lam, supports=sup, intervals=False)['best']
    sw_, lam_ = ref['sw'], ref['lam']
    d0 = patch_depth(c0)
    out = {'centre': centre, 'sw': sw_, 'lam': lam_, 'rows': {}}
    for lb, c in depth_cells:
        tp = target_patch(c)[0]
        pix = P.reader_mask(c, R=R, d_in=d_in, which=tp)
        dpt = patch_depth(c)
        size = c.bg_spec['size']
        row = dict(depth=dpt, band=band_status(c, dpt, size, R), n=int(pix.sum()))
        if pix.sum() < MIN_PX:
            row.update(sn=None, note='no readable pixels near the patch inside the declared mask')
        else:
            r = P.read([(c, pix)], reading, sw=sw_, lam=lam_, supports=sup)['best']
            row.update(sn=r['sn'], sn_iv=r.get('sn_iv'), rms=r['rms'], w=r['w'])
        out['rows'][lb] = row
    s0 = out['rows'][centre]['sn']
    for lb, row in out['rows'].items():
        row['ratio'] = row['sn'] / s0 if (row['sn'] is not None and s0) else None
        row['olaw_ratio'] = olaw_ratio(cells[lb], row['depth'], d0)
    return out


DEPTH_BINS = (4.0, 8.0, 12.0, 16.0, 24.0, 32.0, 48.0, 64.0, 96.0)


def read_bins(cell, reading='native', sw=None, lam=None, bins=DEPTH_BINS, d_min=None, min_px=400):
    """The same ratio read on any structured cell (a checker, an impulse lattice): pixels grouped by SDF
    depth, sigma_n read per depth bin (flat within the bin) with sigma_w and lam held at the whole cell's read
    and w and the gain free per bin, so a share that varies with depth (vitrea's sharp ramp) cannot pass for
    a width that does. The deepest populated bin is the reference. d_min drops a band (vitrea's lens)."""
    import read_patch as RP
    sup = _support(cell, reading)
    whole = RP.read([(cell, cell.mask)], reading, sw=sw, lam=lam, supports=sup, intervals=False)['best']
    sw_, lam_ = whole['sw'], whole['lam']
    depth = -cell.d
    rows = {}
    for a, b in zip(bins[:-1], bins[1:]):
        if d_min is not None and a < d_min:
            continue
        pix = cell.mask & (depth >= a) & (depth < b)
        if pix.sum() < min_px:
            continue
        r = RP.read([(cell, pix)], reading, sw=sw_, lam=lam_, supports=sup)['best']
        mid = float(np.median(depth[pix]))
        rows[f'{a:g}-{b:g}'] = dict(depth=mid, sn=r['sn'], sn_iv=r.get('sn_iv'), w=r['w'], rms=r['rms'],
                                    n=int(pix.sum()))
    if not rows:
        return dict(sw=sw_, lam=lam_, rows={})
    ref = max(rows, key=lambda k: rows[k]['depth'])
    s0, d0 = rows[ref]['sn'], rows[ref]['depth']
    for row in rows.values():
        row['ratio'] = row['sn'] / s0 if s0 > 0 else float('nan')
        row['olaw_ratio'] = olaw_ratio(cell, row['depth'], d0)
    return dict(sw=sw_, lam=lam_, ref=ref, rows=rows)
