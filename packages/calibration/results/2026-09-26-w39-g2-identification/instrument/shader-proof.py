"""H2 versus the shipped WGSL on Metal, with no browser or pixel capture.

Run in /tmp/w39-g2-wgpu (wgpu 0.32.0). The compute wrapper substitutes only
uniform inputs for uniform synthetic backdrops. The response, solve, composite,
retention and gamut code is extracted unchanged from the runtime shader. This
checks optical arithmetic, not texture sampling or the browser compositor.
"""
import copy
import hashlib
import json
from pathlib import Path
import numpy as np
import wgpu
import body

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parents[3]/'renderer-webgpu/src/wgsl/optics.ts'
source=SOURCE.read_text()

def function(name):
    start=source.index('fn '+name+'(');brace=source.index('{',start);depth=1;i=brace+1
    while depth:
        depth+=(source[i]=='{')-(source[i]=='}');i+=1
    return source[start:i]

start=source.index('  var toneAdapt = 0.0;')
end=source.index('  var colour = mix(backdrop, adapted, presentAlpha);',start)
block=source[start:end+len('  var colour = mix(backdrop, adapted, presentAlpha);')]
wgsl='''
struct Uniforms {
  tint: vec4f, size: vec4f, toneRowThin: vec4f, toneRowThick: vec4f,
  toneAnchor: vec4f, toneExtra: vec4f, toneBlack: vec4f,
  toneAdapt: vec4f, flags: vec4f,
};
@group(0) @binding(0) var<storage,read> inputs: array<vec4f>;
@group(0) @binding(1) var<storage,read_write> outputs: array<vec4f>;
var<private> ou: Uniforms;
'''+ '\n'.join(function(n) for n in ['srgb_encode','tone_response','gamut_at_luma','body_chroma_retention'])+'''
@compute @workgroup_size(1)
fn main(@builtin(global_invocation_id) gid: vec3u) {
  let i=gid.x*13u;
  ou.tint=inputs[i]; ou.size=inputs[i+1u];
  ou.toneRowThin=inputs[i+2u]; ou.toneRowThick=inputs[i+3u];
  ou.toneAnchor=inputs[i+4u]; ou.toneExtra=inputs[i+5u];
  ou.toneBlack=inputs[i+6u]; ou.toneAdapt=inputs[i+7u]; ou.flags=vec4f(1.0);
  let backdrop=inputs[i+8u].rgb;
  let toneColour=vec4f(backdrop,inputs[i+8u].w);
  let sizeK=inputs[i+9u].x;
  let toneStrength=ou.toneAdapt.w;
  let toneLinearMean=inputs[i+9u].y;
  let mat=inputs[i+9u].z;
  let retention=inputs[i+9u].w;
  let neutral=ou.tint.rgb;
  let toneLevelFar=0.0;
  let domMaterial=false;
'''+block+'''
  colour=body_chroma_retention(colour,backdrop,retention);
  outputs[gid.x]=vec4f(srgb_encode(colour.r),srgb_encode(colour.g),srgb_encode(colour.b),1.0);
}
'''
materials=json.loads((HERE/'resolved-materials.json').read_text())
colours=np.array([[0,0,0],[.01,.02,.03],[.5,.5,.5],[1,1,1],[40,56,150],[90,70,100],[90,100,70],[128,128,128],[255,0,255]],float)/255
cases=[];packed=[];expected=[]
for endpoint,m0 in materials.items():
  if endpoint=='default':continue
  for span in [32,44,64,96]:
    for r in [0,m0['bodyChromaRetention'],1]:
      m=copy.deepcopy(m0);m['bodyChromaRetention']=r
      for colour in colours:
        b=body.decode(colour);mean=float(b@body.W)
        tone=float(body.decode(colour@body.W)) if isinstance(m.get('backdropToneAbscissa'),dict) else mean
        size=float(body.smooth(m['sizeSpanMin'],m['sizeSpanMax'],span));o=m['optics']['regular']
        xs=m['backdropToneAnchorX'];thin=m['backdropToneResponseThin'];thick=m['backdropToneResponseThick']
        packed.extend([ [*o['tint'],o['tintAlpha']], [0,m['sizeOcclusionGain'],0,0],
          [*thin[:3],m['backdropToneResponseStrength']],[*thick[:3],m['collapseTransmission']],
          [*xs[:3],mean],[xs[3],thin[3],thick[3],1],
          [m['backdropToneBlackStrength'],m['backdropToneBlackThin'],m['backdropToneBlackThick'],0],
          [m['backdropToneLow'],max(m['backdropToneHigh'],m['backdropToneLow']+1e-4),m['backdropToneSizeBias'],m['backdropToneMax']],
          [*b,tone],[size,mean,1,r],[0]*4,[0]*4,[0]*4 ])
        expected.append(body.h2(colour,m,span)[0])
        cases.append(dict(endpoint=endpoint,span=span,retention=r,inputCodes=(colour*255).tolist()))
adapter=wgpu.gpu.request_adapter_sync(power_preference='high-performance')
if adapter.info['adapter_type']=='CPU':raise RuntimeError('software adapter refused')
device=adapter.request_device_sync()
a=np.asarray(packed,dtype=np.float32)
buf=device.create_buffer_with_data(data=a,usage=wgpu.BufferUsage.STORAGE)
out=device.create_buffer(size=len(cases)*16,usage=wgpu.BufferUsage.STORAGE|wgpu.BufferUsage.COPY_SRC)
shader=device.create_shader_module(code=wgsl)
pipeline=device.create_compute_pipeline(layout='auto',compute=dict(module=shader,entry_point='main'))
bind=device.create_bind_group(layout=pipeline.get_bind_group_layout(0),entries=[
    dict(binding=0,resource=dict(buffer=buf)),dict(binding=1,resource=dict(buffer=out))])
encoder=device.create_command_encoder();p=encoder.begin_compute_pass()
p.set_pipeline(pipeline);p.set_bind_group(0,bind);p.dispatch_workgroups(len(cases));p.end()
device.queue.submit([encoder.finish()])
gpu=np.frombuffer(device.queue.read_buffer(out),dtype=np.float32).reshape(-1,4)[:,:3].astype(float)
expected=np.asarray(expected);error=abs(gpu-expected)*255
rows=[dict(**c,pythonCodes=(expected[i]*255).tolist(),shaderCodes=(gpu[i]*255).tolist(),errorCodes=error[i].tolist()) for i,c in enumerate(cases)]
report=dict(adapter=dict(adapter.info),wgpuVersion=wgpu.__version__,shaderSha256=hashlib.sha256(source.encode()).hexdigest(),
    wrapperSha256=hashlib.sha256(wgsl.encode()).hexdigest(),nativePixelsRead=0,cases=len(cases),maximumCodes=float(error.max()),rows=rows)
print(json.dumps(report,indent=2,allow_nan=False))
assert error.max()<.001, 'Python port disagrees with shipped shader'
