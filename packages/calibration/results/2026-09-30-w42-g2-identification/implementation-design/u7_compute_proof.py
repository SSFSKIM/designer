"""W42 G2 step 3, U7: a native Metal compute proof of the law's per-pixel WGSL, against numpy.

The pattern is W41's `body-leaf/e3-gpu-proof.py`. The runtime's functions are extracted from
`wgsl/optics.ts` without changing their arithmetic and called from a compute wrapper, with the
optics uniform struct itself declared as a private copy that each invocation loads. No browser
and no pixels are involved. This proves the functions' arithmetic on a real adapter, and not the
stage's textures or the rendered composite; those are `e2e/gpu/w42-body-law.spec.ts`.

Held against the declared oracles, in f64:
- landed: candidate 1's landed tone as amended below the black join
  (`candidate1_black_join.bridge` over the rehearsal's `solve` + `compose`), at every endpoint and
  four sizeKs, and the unamended solve beside it;
- e3: E3 with the F extension and g at L(W) (`u2_fixtures.e3_ext`);
- table: candidate 2's table on the pre-read addendum's grid (`native_t.grid_eval`) with its
  chroma;
- body: the precedence and the linear-light mixes of fractional strengths.
Arguments include greys across the black-join interval, near-black chromatics, random colours,
the cube's corners and out-of-range arguments, which A now carries unclipped.

    /path/to/venv-with-wgpu/bin/python -B u7_compute_proof.py    # writes u7_compute_proof.json
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
import wgpu

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import candidate1_black_join as CB  # noqa: E402
import u2_fixtures as U  # noqa: E402
import native_t as NT  # noqa: E402

ROOT = HERE.parents[4]
OPTICS = ROOT / 'packages/renderer-webgpu/src/wgsl/optics.ts'
PRELUDE = ROOT / 'packages/renderer-webgpu/src/wgsl/prelude.ts'
BODY = U.BODY


def module_text(path, symbol):
    text = path.read_text()
    begin = text.index('export const ' + symbol + ' = `')
    return text[begin:].split('`', 1)[1].rsplit('`', 1)[0]


OPTICS_WGSL = module_text(OPTICS, 'WGSL_OPTICS_PASS')
PRELUDE_WGSL = module_text(PRELUDE, 'WGSL_PRELUDE')


def function(name):
    source = OPTICS_WGSL + '\n' + PRELUDE_WGSL
    start = source.index('fn ' + name + '(')
    brace = source.index('{', start)
    end, depth = brace + 1, 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


STRUCT = OPTICS_WGSL[OPTICS_WGSL.index('struct OpticsUniforms {'):]
STRUCT = STRUCT[:STRUCT.index('};') + 2]
OFFSET, at = {}, 0
for m in re.finditer(r'^\s*(\w+)\s*:\s*(vec4f|array<vec4f,\s*(\d+)>)\s*,', STRUCT, re.M):
    OFFSET[m.group(1)] = at
    at += 4 if m.group(3) is None else 4 * int(m.group(3))
FLOATS = at
assert FLOATS == 248, FLOATS

FUNCTIONS = ['srgb_to_linear', 'linear_to_srgb', 'srgb_encode', 'tone_response', 'gamut_at_luma',
             'body_chroma_retention', 'body_e3_neutral', 'body_law_gain', 'body_law_e3_codes',
             'body_table_lane', 'body_table_row', 'body_table_codes', 'body_law_landed_solve',
             'body_law_landed', 'body_law_body']
WRAPPER = STRUCT + '''
const LAW_LUMA = vec3f(0.2126, 0.7152, 0.0722);
const LAW_BLACK_JOIN_END = 0.003;
var<private> ou : OpticsUniforms;
struct Case { args : vec4f, colour : vec4f };
@group(0) @binding(0) var<storage, read> uniformSets : array<OpticsUniforms>;
@group(0) @binding(1) var<storage, read> cases : array<Case>;
@group(0) @binding(2) var<storage, read_write> outputs : array<vec4f>;
''' + '\n'.join(function(n) for n in FUNCTIONS) + '''
@compute @workgroup_size(1)
fn main(@builtin(global_invocation_id) gid : vec3u) {
  let c = cases[gid.x];
  ou = uniformSets[u32(c.colour.w)];
  let kind = u32(c.args.x);
  let sizeK = c.args.y;
  let span = c.args.z;
  let neutral = ou.tint.rgb;
  var out = vec3f(0.0);
  if (kind == 0u) { out = body_law_landed(c.colour.rgb, sizeK, 0.0, neutral); }
  else if (kind == 1u) { out = body_law_landed_solve(c.colour.rgb, sizeK, 0.0, neutral); }
  else if (kind == 2u) { out = body_law_e3_codes(c.colour.rgb * 255.0, c.args.w * 255.0); }
  else if (kind == 3u) { out = body_table_codes(c.colour.rgb * 255.0, span); }
  else { out = body_law_body(vec4f(c.colour.rgb, c.args.w), span, sizeK, 0.0, neutral); }
  outputs[gid.x] = vec4f(out, 1.0);
}
'''
assert 'const LAW_BLACK_JOIN_END = 0.003;' in OPTICS_WGSL and 'const LAW_LUMA' in OPTICS_WGSL


def lanes(values):
    d = np.zeros(FLOATS, np.float32)
    for name, vec in values.items():
        d[OFFSET[name]:OFFSET[name] + len(vec)] = vec
    return d


def uniform_for(e, e3=0.0, high=0.0, table=0.0, tab=None, tgains=(1, 1, 1), tscale=1.0):
    """The optics uniform the renderer packs for this endpoint, in the lanes the law reads."""
    silhouette = CB.silhouette(e)
    ax, th, tk = e['anchorX'], e['thin'], e['thick']
    values = dict(
        tint=[e['tint'][0]] * 3 + [e['tintAlpha']],
        size=[0, e['sizeOcclusionGain'], 0, 0],
        toneAdapt=[e['backdropToneLow'], e['backdropToneHigh'], e['backdropToneSizeBias'], 0],
        toneAnchor=[ax[0], ax[1], ax[2], 0], toneRowThin=[th[0], th[1], th[2], e['responseStrength']],
        toneRowThick=[tk[0], tk[1], tk[2], 0],
        toneExtra=[ax[3], th[3], tk[3], 1] if len(ax) == 4 else [0, 0, 0, 0],
        toneBlack=[e['black'][0], e['black'][1], e['black'][2], 0],
        bodyChroma=[e['bodyChromaRetention'], 0, 0, 0],
        bodyE3=[0, *U.BODY.E3_GAINS], bodyE3Neutral0=list(U.BODY.E3_NEUTRAL[:4]),
        bodyE3Neutral1=list(U.BODY.E3_NEUTRAL[4:]) + [0],
        bodyLawA=[0, 0, e['backdropToneMax'], 1 if silhouette else 0],
        bodyLawTone=[e3, high, table, 0],
        bodyE3High0=HIGH[:4], bodyE3High1=HIGH[4:] + [0],
    )
    if tab is not None:
        values['bodyTable'] = (list(NT.GRID_LEVELS) + list(NT.GRID_SPANS) + list(np.ravel(tab))
                               + list(tgains) + [tscale, 0])
    return lanes(values)


HIGH = [206.0, 214.0, 222.0, 229.0, 234.0, 238.0, 240.0]


def table_oracle(tab, codes, span, gains, scale):
    L = float(np.dot(codes, U.G.W709))
    f = float(np.clip(NT.grid_eval(tab, np.array([L]), span)[0], 0, 255))
    if codes[0] == codes[1] == codes[2]:
        return np.array([f, f, f])
    g = scale * float(np.where(L > 93, gains[1] + np.clip((L - 93) / 25, 0, 1) * (gains[2] - gains[1]),
                               gains[0] + np.clip((L - 63) / 30, 0, 1) * (gains[1] - gains[0])))
    return np.clip(f + g * (np.asarray(codes) - L), 0, 255)


def arguments():
    rng = np.random.default_rng(20261003)
    greys = [0, 1e-4, 5e-4, 0.001, 0.0015, 0.002, 0.0025, 0.0029, 0.003, 0.0031, 0.004, 0.01,
             0.05, 0.1, 0.2, 0.35, 0.5, 0.7, 0.9, 1.0]
    out = [[g, g, g] for g in greys]
    out += [list(rng.uniform(0, 0.012, 3)) for _ in range(24)]
    out += [list(rng.uniform(0, 1, 3)) for _ in range(48)]
    out += [[(i >> k) & 1 for k in range(3)] for i in range(8)]
    out += [list(rng.uniform(-0.2, 1.3, 3)) for _ in range(16)]      # out of range, as A may be
    return np.array(out, float)


def main():
    A = arguments()
    uniforms, cases, expected, labels = [], [], [], []

    def add(u, kind, sizeK, span, extra, a, value, label):
        if not uniforms or not np.array_equal(uniforms[-1], u):
            uniforms.append(u)
        cases.append([kind, sizeK, span, extra, a[0], a[1], a[2], len(uniforms) - 1])
        expected.append(value)
        labels.append(label)

    for ep, e in BODY.RES.items():
        for sizeK in (0.0, 0.0923, 0.35, 1.0):
            u = uniform_for(e)
            amended = CB.bridge(lambda X: CB.landed_at(e, sizeK, X), e, A)
            solved = CB.landed_at(e, sizeK, A)
            for i, a in enumerate(A):
                add(u, 0, sizeK, 96, 0, a, amended[i], f'landed {ep} {sizeK}')
                add(u, 1, sizeK, 96, 0, a, solved[i], f'solve {ep} {sizeK}')
    e = BODY.RES['light-receded']
    for strength in (0.0, 0.4, 1.0):
        u = uniform_for(e, high=strength)
        for i, a in enumerate(A):
            gl = float(np.clip(np.dot(a, U.G.W709) + 0.05 * ((i % 5) - 2), 0, 1))
            want = U.e3_ext(255 * a, 255 * gl, list(U.BODY.E3_GAINS), list(U.BODY.E3_NEUTRAL), HIGH, strength)
            add(u, 2, 0, 96, gl, a, np.array(want), f'e3 high {strength}')
    for ep, scheme in (('light-inactive', 'light'), ('dark-rest', 'dark')):
        tab = NT.NativeT(NT.stand_in(ep, scheme), scheme).table()
        gains, scale = (0.95, 0.949, 0.933), 1.07
        u = uniform_for(BODY.RES['light-active'], tab=tab, tgains=gains, tscale=scale)
        for span in (32, 64, 72, 96, 112, 128, 150, 160, 200):
            for a in A:
                add(u, 3, 0, span, 0, a, table_oracle(tab, 255 * a, span, gains, scale), f'table {ep} {span}')
    # The precedence and its linear-light mixes, on one endpoint with every tone present.
    e = BODY.RES['dark-active']
    tab = NT.NativeT(NT.stand_in('dark-rest', 'dark'), 'dark').table()
    gains, scale = (1.203, 1.165, 1.070), 1.0
    for e3s, ts in ((0, 0), (0.5, 0), (1, 0), (0, 0.4), (0.5, 0.4), (1, 1)):
        u = uniform_for(e, e3=e3s, table=ts, tab=tab, tgains=gains, tscale=scale)
        landed = CB.bridge(lambda X: CB.landed_at(e, 0.35, X), e, A)
        for i, a in enumerate(A):
            gl = float(np.clip(np.dot(a, U.G.W709), 0, 1))
            dec = lambda c: BODY.dec(np.asarray(c) / 255)
            body = landed[i] if (e3s < 1 and ts < 1) else np.zeros(3)
            if e3s > 0 and ts < 1:
                e3v = dec(U.e3_ext(255 * a, 255 * gl, list(U.BODY.E3_GAINS), list(U.BODY.E3_NEUTRAL), HIGH, 0))
                body = body + (e3v - body) * e3s
            if ts > 0:
                body = body + (dec(table_oracle(tab, 255 * a, 112, gains, scale)) - body) * ts
            add(u, 4, 0.35, 112, gl, a, body, f'body e3 {e3s} table {ts}')

    adapter = wgpu.gpu.request_adapter_sync(power_preference='high-performance')
    assert adapter.info['backend_type'] == 'Metal' and adapter.info['adapter_type'] != 'CPU'
    device = adapter.request_device_sync()
    device.create_shader_module(code=PRELUDE_WGSL + '\n' + OPTICS_WGSL)   # the complete module compiles
    shader = device.create_shader_module(code=WRAPPER)
    pipeline = device.create_compute_pipeline(layout='auto', compute=dict(module=shader, entry_point='main'))
    ub = device.create_buffer_with_data(data=np.concatenate(uniforms).astype(np.float32),
                                        usage=wgpu.BufferUsage.STORAGE)
    cb = device.create_buffer_with_data(data=np.asarray(cases, np.float32), usage=wgpu.BufferUsage.STORAGE)
    ob = device.create_buffer(size=len(cases) * 16, usage=wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_SRC)
    bind = device.create_bind_group(layout=pipeline.get_bind_group_layout(0), entries=[
        dict(binding=0, resource=dict(buffer=ub)), dict(binding=1, resource=dict(buffer=cb)),
        dict(binding=2, resource=dict(buffer=ob))])
    encoder = device.create_command_encoder()
    compute = encoder.begin_compute_pass()
    compute.set_pipeline(pipeline)
    compute.set_bind_group(0, bind)
    compute.dispatch_workgroups(len(cases))
    compute.end()
    device.queue.submit([encoder.finish()])
    actual = np.frombuffer(device.queue.read_buffer(ob), np.float32).reshape(-1, 4)[:, :3].astype(float)
    expected = np.array(expected, float)
    assert np.all(np.isfinite(actual))

    kinds = np.array([label.split()[0] for label in labels])
    report = {}
    for kind in ('landed', 'solve', 'body'):   # linear light out: compare in encoded codes
        m = kinds == kind
        err = np.abs(255 * BODY.enc(actual[m]) - 255 * BODY.enc(expected[m])).max(axis=1)
        report[kind] = dict(cases=int(m.sum()), maxCodes=float(err.max()),
                            worst=labels[int(np.flatnonzero(m)[err.argmax()])])
    for kind in ('e3', 'table'):               # codes out
        m = kinds == kind
        err = np.abs(actual[m] - expected[m]).max(axis=1)
        report[kind] = dict(cases=int(m.sum()), maxCodes=float(err.max()),
                            worst=labels[int(np.flatnonzero(m)[err.argmax()])])
    ok = all(v['maxCodes'] < 0.01 for v in report.values())
    doc = dict(adapter=dict(adapter.info), cases=len(cases), results=report, passed=ok,
               bound='0.01 code per channel, f32 on the adapter against f64 numpy',
               fullOpticsModuleCompiled=True, browserRuns=0,
               sources={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in (Path(__file__), OPTICS, PRELUDE, HERE / 'candidate1_black_join.py')},
               wrapperSha256=hashlib.sha256(WRAPPER.encode()).hexdigest())
    (HERE / 'u7_compute_proof.json').write_text(json.dumps(doc, indent=2) + '\n')
    print(json.dumps(doc, indent=2))
    assert ok


if __name__ == '__main__':
    main()
