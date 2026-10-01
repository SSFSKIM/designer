"""W42 G2 perf wave (§17): the realisation's error per knee under each decimation rule, from the U2
mirror's runs with candidate 1 bridged (`u2_mirror.py`, W42_BRIDGED=1). A rule that changes only the
active pose's narrow levels is read as that run's active rows beside the oracle-rule run's receded
rows, which it leaves as they are.

    python3.12 -B perf/mirror_realisation.py     # writes perf/mirror_realisation.txt
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)


def rows(name):
    return json.load(open(os.path.join(UP, f'u2_mirror-{name}.json')))['rows']


q12 = rows('bridged-q12')
RULES = {
    'oracle rule, 12 device px everywhere (U2, bridged)': q12,
    'active narrow levels from 6 (adopted)':
        [r for r in rows('bridged-q6') if r['pose'] == 'active'] + [r for r in q12 if r['pose'] == 'receded'],
    'active narrow levels from 5':
        [r for r in rows('bridged-active-q5') if r['pose'] == 'active'] + [r for r in q12 if r['pose'] == 'receded'],
    'active narrow levels from 4.5':
        [r for r in rows('bridged-active-q4.5') if r['pose'] == 'active'] + [r for r in q12 if r['pose'] == 'receded'],
    'every width from 6 (receded too)': rows('bridged-q6'),
    'active from 5, companded 16-bit tiles (A float32)':
        [r for r in rows('bridged-active-q5-c16') if r['fmt'] == 'c16'],
}


def main():
    out = [__doc__.split('\n\n')[0], '',
           'Worst band-weighted output error in codes over the canonical cells (192) and family E (24),',
           'f32 tiles with the chain16 capture unless named; knee 1 adds its flip fraction and the worst',
           'error at a flip. Knees 0 and 2 are held to 0.15 (§11.1, ruled).', '']
    for label, rs in RULES.items():
        out.append(f'== {label}')
        for fam in (False, True):
            for src in (('chain16',) if not fam else ('chain16', 'exact8')):
                for knee in (0, 1, 2):
                    cells = []
                    for tone in ('cand1-landed', 'cand2-table'):
                        g = [r for r in rs if r['fmt'] in ('f32', 'c16') and r['src'] == src and r['knee'] == knee
                             and r['tone'] == tone and r['bg'].startswith('checker-') == fam]
                        if not g:
                            continue
                        worst = max(g, key=lambda r: r['bandw_max'])
                        text = f"{tone} {worst['bandw_max']:.3f} ({worst['bg']} {worst['comp']} {worst['scale']}x {worst['scheme']} {worst['pose']})"
                        if knee == 1:
                            text += (f" flips {max(r.get('flip_fraction', 0) for r in g):.3f}"
                                     f" at a flip {max(r.get('flip_worst', 0) for r in g):.3f}")
                        cells.append(text)
                    if cells:
                        out.append(f"  {'family E' if fam else 'canonical'} {src:8s} knee {knee}: " + ' | '.join(cells))
        out.append('')
    text = '\n'.join(out)
    open(os.path.join(HERE, 'mirror_realisation.txt'), 'w').write(text)
    print(text)


if __name__ == '__main__':
    main()
