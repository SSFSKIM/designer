"""Prove the port against unchanged WGSL arithmetic on actual Metal compute.

As W39 H2 did, replace resource inputs with synthetic uniforms. Texture field
sampling/UV reconstruction are not claimed: shadowField.x is the supplied-path
shifted distance, shadowAux.z its span, and presence is one. The function's
actual early return, size law, occlusion and CDF suffix remain unchanged.
"""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import wgpu
import instrument as m
import shadow
source=(m.ROOT/'packages/renderer-webgpu/src/wgsl/optics.ts').read_text()
def function(name):
    start=source.index('fn '+name+'(');brace=source.index('{',start);i=brace+1;depth=1
    while depth:
        depth+=(source[i]=='{')-(source[i]=='}');i+=1
    return source[start:i]
fn=function('outer_shadow')
begin=fn[fn.index('{')+1:fn.index('  /*')]
suffix=fn[fn.index('  let castMat ='):]
wgsl='''
struct Uniforms { shadow:vec4f, shadowSigma:vec4f, shadowThick:vec4f,
 scatter:vec4f, shadowSize:vec4f, tone:vec4f };
struct ShadowSample {alpha:f32,falloff:f32,castSpanCss:f32,castMat:f32};
@group(0) @binding(0) var<storage,read> inputs:array<vec4f>;
@group(0) @binding(1) var<storage,read_write> outputs:array<vec4f>;
var<private> ou:Uniforms;
'''+ '\n'.join(function(n) for n in ['outer_shadow_sigma','outer_shadow_thick','outer_shadow_falloff'])+'''
fn synthetic_shadow(v:vec4f)->ShadowSample {
'''+begin+'''
 let shadowField=vec4f(v.x,0.,0.,0.);
 let shadowAux=vec4f(0.,0.,v.y,0.);
 let shadowPresence=vec4f(1.,0.,0.,0.);
 let clampedOffCss=0.;
'''+suffix+'''
@compute @workgroup_size(1)
fn main(@builtin(global_invocation_id) gid:vec3u) {
 let i=gid.x*6u;
 ou.shadow=inputs[i]; ou.shadowSigma=inputs[i+1u]; ou.shadowThick=inputs[i+2u];
 ou.scatter=inputs[i+3u];ou.shadowSize=inputs[i+4u];ou.tone=vec4f(0.,0.,0.,1.);
 let s=synthetic_shadow(inputs[i+5u]);
 outputs[gid.x]=vec4f(s.alpha*s.falloff,s.alpha,s.falloff,s.castSpanCss);
}
'''
materials=shadow.materials()
cpu=json.loads((m.HERE/'shadow-cpu-values.json').read_text())
rows=[];packed=[];expected=[];cpu_errors=[]
for row in cpu:
    mat=materials[row['endpoint']];s=mat['outerShadow'];span=row['span'];l=row['luminance']
    cpu_errors.extend([abs(shadow.thin(l,s)-row['thin']),abs(shadow.sigma(span,s)-row['sigma']),abs(shadow.occlusion(span,mat,l)-row['occlusion'])])
    for d in [-1000,-30,-8,-1,0,.5,2,8,1000]:
        packed.extend([[row['thin'],s['sigmaPx'],s['spreadPx'],s['offsetPx']],
                       [s['sigmaSlopePerSpan'],s['sigmaSpanRefPx'],s['sigmaThinOffsetPx'],0],
                       [s['thickOcclusionAt96'],s['thickOcclusionAt128'],s['thickOcclusionAt160'],0],
                       [0,0,mat['sizeSpanMin'],mat['sizeSpanMax']],
                       [s['sizeGain'],0,0,0],[d,span,l,0]])
        expected.append(float(shadow.from_distance(np.array([d]),span,mat,l)[0]))
        rows.append(dict(endpoint=row['endpoint'],span=span,luminance=l,shiftedDistanceCSS=d))
adapter=wgpu.gpu.request_adapter_sync(power_preference='high-performance')
if adapter.info['adapter_type']=='CPU' or adapter.info['backend_type']!='Metal':raise RuntimeError('real Metal adapter required')
device=adapter.request_device_sync()
a=np.asarray(packed,np.float32)
buf=device.create_buffer_with_data(data=a,usage=wgpu.BufferUsage.STORAGE)
out=device.create_buffer(size=len(rows)*16,usage=wgpu.BufferUsage.STORAGE|wgpu.BufferUsage.COPY_SRC)
shader=device.create_shader_module(code=wgsl)
pipeline=device.create_compute_pipeline(layout='auto',compute=dict(module=shader,entry_point='main'))
bind=device.create_bind_group(layout=pipeline.get_bind_group_layout(0),entries=[dict(binding=0,resource=dict(buffer=buf)),dict(binding=1,resource=dict(buffer=out))])
encoder=device.create_command_encoder();p=encoder.begin_compute_pass();p.set_pipeline(pipeline);p.set_bind_group(0,bind);p.dispatch_workgroups(len(rows));p.end();device.queue.submit([encoder.finish()])
gpu=np.frombuffer(device.queue.read_buffer(out),np.float32).reshape(-1,4)[:,0].astype(float)
err=abs(gpu-np.array(expected))*255
report=dict(schema='w41-shadow-proof-1',adapter=dict(adapter.info),python=sys.version,numpy=np.__version__,wgpu=wgpu.__version__,cases=len(rows),cpuCases=len(cpu),maximumCPUAbsolute=max(cpu_errors),maximumShaderCodes=float(err.max()),worst={**rows[int(err.argmax())], 'pythonAlpha':expected[int(err.argmax())],'shaderAlpha':float(gpu[err.argmax()])},nativePixelsRead=0,browserRuns=0,fallback=False,scope='unchanged WGSL optical arithmetic with synthetic field inputs; supplied-path shift tested separately, not texture reconstruction',sources={str(p.relative_to(m.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),m.HERE/'shadow.py',m.HERE/'shadow-cpu-proof.ts',m.G2/'instrument/resolved-materials.json',m.G2/'instrument/resolved-materials.provenance.json',m.ROOT/'packages/renderer-webgpu/src/wgsl/optics.ts']},wrapperSha256=hashlib.sha256(wgsl.encode()).hexdigest())
print(json.dumps(report,indent=2,allow_nan=False))
assert max(cpu_errors)<1e-12
assert np.all(np.isfinite(gpu)) and err.max()<.001
