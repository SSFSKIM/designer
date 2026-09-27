"""Synthetic Metal compute proof of the actual E3 WGSL; no browser or pixels.

Extract the runtime functions without changing their arithmetic. Uniforms and
straight colours are synthetic. This verifies neither backdrop sampling nor the
complete rendered composite; candidate renders stay blocked on baseline freeze.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np
import wgpu

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
G0 = HERE.parents[1] / '2026-09-27-w41-g0-declaration'
spec = importlib.util.spec_from_file_location('body41', G0 / 'body-instrument/body41.py')
body = importlib.util.module_from_spec(spec); spec.loader.exec_module(body)
optics = ROOT / 'packages/renderer-webgpu/src/wgsl/optics.ts'
prelude = ROOT / 'packages/renderer-webgpu/src/wgsl/prelude.ts'
source = optics.read_text() + '\n' + prelude.read_text()


def function(name):
    start = source.index('fn ' + name + '(')
    brace = source.index('{', start); end = brace + 1; depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}'); end += 1
    return source[start:end]


wgsl = '''
struct Uniforms { flags:vec4f, bodyE3:vec4f, bodyE3Neutral0:vec4f, bodyE3Neutral1:vec4f };
var<private> ou:Uniforms;
@group(0) @binding(0) var<storage,read> inputs:array<vec4f>;
@group(0) @binding(1) var<storage,read_write> outputs:array<vec4f>;
''' + '\n'.join(function(n) for n in ['srgb_to_linear', 'linear_to_srgb',
    'body_e3_neutral', 'body_e3_codes', 'body_e3_composite']) + '''
@compute @workgroup_size(1)
fn main(@builtin(global_invocation_id) gid:vec3u) {
  let i=gid.x*7u;
  ou.flags=inputs[i];ou.bodyE3=inputs[i+1u];
  ou.bodyE3Neutral0=inputs[i+2u];ou.bodyE3Neutral1=inputs[i+3u];
  let encoded=inputs[i+4u].xyz;
  let original=inputs[i+5u].xyz;let presence=inputs[i+5u].w;
  if(inputs[i+6u].x>0.5){
    outputs[gid.x]=vec4f(body_e3_codes(encoded),1.);
  }else{
    let backdrop=srgb_to_linear(encoded/255.);
    outputs[gid.x]=vec4f(body_e3_composite(original,backdrop,presence),1.);
  }
}
'''
q = [0.929205829365914, 0.9597570955316058, 0.9383102545096953]
n = [150., 157., 164., 171., 178., 188., 197.]
levels = [0, 5, 32, 40, 56, 63, 72, 88, 93, 104, 118, 128, 150, 192, 250, 255]
x = np.vstack([np.repeat(np.array(levels)[:, None], 3, axis=1),
               [[192, 32, 32], [32, 192, 32], [0, 255, 0], [255, 0, 255]],
               np.random.default_rng(4102).uniform(0, 255, (128, 3))]).astype(np.float32)
packed = []; expected = []; identity = []; kinds = []
original = np.array([.123456, .234567, .345678], np.float32)
for gates in [q, [0., 3., 1.5]]:
    for neutral in [n, [0., 50., 90., 140., 190., 220., 255.]]:
        target = body.forward('E3', x.astype(float), neutral, gates)
        for i, colour in enumerate(x):
            for strength, sampled, presence, raw in [(1, 1, 1, True), (1, 1, 1, False),
                    (1, 1, .25, False), (.5, 1, .75, False), (0, 1, 1, False),
                    (1, 0, 1, False), (1, 1, 0, False)]:
                packed.extend([[sampled, 0, 0, 0], [strength, *gates], neutral[:4],
                               [*neutral[4:], 0], [*colour, 0], [*original, presence],
                               [int(raw), 0, 0, 0]])
                if raw:
                    value = target[i]; exact = False
                elif strength == 0 or sampled == 0 or presence == 0:
                    value = original.astype(float); exact = True
                else:
                    bg = body.colour.decode(colour.astype(float) / 255)
                    full = body.colour.decode(target[i] / 255)
                    posed = bg + (full - bg) * presence
                    value = original + (posed - original) * strength
                    exact = False
                expected.append(value); identity.append(exact); kinds.append('raw' if raw else 'composite')
adapter = wgpu.gpu.request_adapter_sync(power_preference='high-performance')
assert adapter.info['backend_type'] == 'Metal' and adapter.info['adapter_type'] != 'CPU'
device = adapter.request_device_sync()
# Compile the COMPLETE module too: the extraction alone cannot prove its actual
# uniform declaration, callsite and surrounding WGSL remain structurally legal.
def module_text(path, symbol):
    text = path.read_text(); begin = text.index('export const ' + symbol + ' = `')
    return text[begin:].split('`', 1)[1].rsplit('`', 1)[0]
full_module = module_text(prelude, 'WGSL_PRELUDE') + '\n' + module_text(optics, 'WGSL_OPTICS_PASS')
device.create_shader_module(code=full_module)
shader = device.create_shader_module(code=wgsl)
pipeline = device.create_compute_pipeline(layout='auto', compute=dict(module=shader, entry_point='main'))
a = device.create_buffer_with_data(data=np.asarray(packed, np.float32), usage=wgpu.BufferUsage.STORAGE)
b = device.create_buffer(size=len(expected)*16, usage=wgpu.BufferUsage.STORAGE|wgpu.BufferUsage.COPY_SRC)
bind = device.create_bind_group(layout=pipeline.get_bind_group_layout(0), entries=[
    dict(binding=0,resource=dict(buffer=a)), dict(binding=1,resource=dict(buffer=b))])
encoder = device.create_command_encoder(); compute = encoder.begin_compute_pass()
compute.set_pipeline(pipeline); compute.set_bind_group(0, bind); compute.dispatch_workgroups(len(expected)); compute.end()
device.queue.submit([encoder.finish()])
actual = np.frombuffer(device.queue.read_buffer(b), np.float32).reshape(-1,4)[:,:3]
expected = np.array(expected)
raw = np.array(kinds) == 'raw'; exact = np.array(identity)
errors = abs(actual - expected)
assert np.all(np.isfinite(actual))
assert np.array_equal(actual[exact], np.tile(original, (int(exact.sum()), 1)))
assert errors[raw].max() < .001
assert errors[~raw].max() < .001 / 255
print(json.dumps(dict(adapter=dict(adapter.info), cases=len(expected),
    rawCases=int(raw.sum()), identityCases=int(exact.sum()),
    maximumEncodedCodes=float(errors[raw].max()), maximumCompositeLinear=float(errors[~raw].max()),
    fullOpticsModuleCompiled=True, exactOffUnsampledZeroPresence=True,
    nativePayloadReads=0, browserRuns=0, candidateRenders=0,
    scope='synthetic compute arithmetic, not rendered texture reconstruction or composite survival',
    sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
             [Path(__file__), optics, prelude, G0/'body-instrument/body41.py']},
    wrapperSha256=hashlib.sha256(wgsl.encode()).hexdigest()), indent=2))
