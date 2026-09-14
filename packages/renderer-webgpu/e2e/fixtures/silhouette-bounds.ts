import { silhouetteReductionModule } from "../../src/wgsl/silhouette-tone";

/** A huge clipped rectangle previously overflowed the unbounded u32 iteration
 * area to zero. This probes the reduction directly, independent of optical culling. */
export async function silhouetteBoundsProbe() {
  const adapter = await navigator.gpu.requestAdapter();
  if (adapter === null) throw new Error("No adapter");
  const device = await adapter.requestDevice();
  device.pushErrorScope("validation");
  const source = device.createTexture({ size: [16, 16], format: "rgba8unorm",
    usage: GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.COPY_DST });
  device.queue.writeTexture({ texture: source }, new Uint8Array(16 * 16 * 4).fill(255),
    { bytesPerRow: 16 * 4 }, [16, 16]);
  const shapes = new Float32Array([
    4, 4, 8, 8, 0, 0, 0, 0,
    -4, -4, 8, 8, 0, 0, 0, 0,
    -32768, -32768, 65536, 65536, 0, 0, 0, 0,
    32768, 32768, 65536, 65536, 0, 0, 0, 0,
  ]);
  const shapeBuffer = device.createBuffer({ size: shapes.byteLength,
    usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST });
  device.queue.writeBuffer(shapeBuffer, 0, shapes);
  const uniforms = device.createBuffer({ size: 32,
    usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST });
  device.queue.writeBuffer(uniforms, 0, new Float32Array([16, 16, 0, 0, 1, 1, 0, 0]));
  const tones = device.createBuffer({ size: shapes.byteLength,
    usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC });
  const readback = device.createBuffer({ size: shapes.byteLength,
    usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ });
  const pipeline = device.createComputePipeline({ layout: "auto", compute: {
    module: device.createShaderModule({ code: silhouetteReductionModule() }),
    entryPoint: "reduce_tone",
  } });
  const encoder = device.createCommandEncoder();
  const pass = encoder.beginComputePass();
  pass.setPipeline(pipeline);
  pass.setBindGroup(0, device.createBindGroup({ layout: pipeline.getBindGroupLayout(0),
    entries: [
      { binding: 0, resource: { buffer: uniforms } },
      { binding: 1, resource: source.createView() },
      { binding: 3, resource: { buffer: shapeBuffer } },
      { binding: 4, resource: { buffer: tones } },
    ],
  }));
  pass.dispatchWorkgroups(4);
  pass.end();
  encoder.copyBufferToBuffer(tones, 0, readback, 0, shapes.byteLength);
  device.queue.submit([encoder.finish()]);
  await readback.mapAsync(GPUMapMode.READ);
  const values = Array.from(new Float32Array(readback.getMappedRange()));
  readback.unmap();
  const error = await device.popErrorScope();
  source.destroy(); shapeBuffer.destroy(); uniforms.destroy(); tones.destroy(); readback.destroy();
  device.destroy();
  if (error !== null) throw new Error(error.message);
  return values;
}
