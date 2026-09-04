/**
 * The field, on the GPU. See `noise.ts` for the same function in JavaScript and
 * for why the two must stay equivalent.
 */

import type { FieldLayer } from "./palettes";

const VERTEX = `#version 300 es
precision highp float;
const vec2 corners[3] = vec2[3](vec2(-1.0, -1.0), vec2(3.0, -1.0), vec2(-1.0, 3.0));
void main() { gl_Position = vec4(corners[gl_VertexID], 0.0, 1.0); }
`;

const FRAGMENT = `#version 300 es
precision highp float;
out vec4 fragColor;

uniform vec2 u_resolution;
uniform float u_time;
uniform float u_scale;
uniform float u_warp;
uniform float u_rate;
uniform float u_detail;
uniform float u_jet;
uniform float u_front;
uniform vec3 u_stops[4];

vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec2 mod289(vec2 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec3 permute(vec3 x) { return mod289(((x * 34.0) + 1.0) * x); }

float snoise(vec2 v) {
  const vec4 C = vec4(0.211324865405187, 0.366025403784439, -0.577350269189626, 0.024390243902439);
  vec2 i = floor(v + dot(v, C.yy));
  vec2 x0 = v - i + dot(i, C.xx);
  vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
  vec4 x12 = x0.xyxy + C.xxzz;
  x12.xy -= i1;
  i = mod289(i);
  vec3 p = permute(permute(i.y + vec3(0.0, i1.y, 1.0)) + i.x + vec3(0.0, i1.x, 1.0));
  vec3 m = max(0.5 - vec3(dot(x0, x0), dot(x12.xy, x12.xy), dot(x12.zw, x12.zw)), 0.0);
  m = m * m;
  m = m * m;
  vec3 x = 2.0 * fract(p * C.www) - 1.0;
  vec3 h = abs(x) - 0.5;
  vec3 ox = floor(x + 0.5);
  vec3 a0 = x - ox;
  m *= 1.79284291400159 - 0.85373472095314 * (a0 * a0 + h * h);
  vec3 g;
  g.x = a0.x * x0.x + h.x * x0.y;
  g.yz = a0.yz * x12.xz + h.yz * x12.yw;
  return 130.0 * dot(m, g);
}

float fbm(vec2 p) {
  float value = 0.0;
  float amplitude = 0.5;
  for (int octave = 0; octave < 4; octave += 1) {
    value += amplitude * snoise(p);
    p = p * 2.02 + vec2(17.3, 9.1);
    amplitude *= 0.5;
  }
  return value;
}

float fieldValue(vec2 p, float time) {
  float t = time * u_rate;
  vec2 q = vec2(fbm(p + vec2(t * 0.05, 0.0)), fbm(p + vec2(5.2, 1.3 - t * 0.04)));
  vec2 r = vec2(
    fbm(p + u_warp * q + vec2(1.7 + t * 0.07, 9.2)),
    fbm(p + u_warp * q + vec2(8.3, 2.8 - t * 0.06))
  );
  float v = fbm(p + 2.0 * r);
  float fine = fbm(p * 5.0 + 5.0 * r);
  float centre = u_scale * (0.5 + 0.13 * sin(p.x * 3.2 / u_scale - t * 0.15) + 0.12 * r.y);
  float d = (p.y - centre) / (0.11 * u_scale);
  float jet = exp(-d * d);
  float front = -tanh(d * 0.7);
  float s = 0.12
    + 0.3 * (v + 0.6)
    + u_jet * jet * (0.85 + 0.3 * r.x)
    + u_front * (1.0 + front)
    + u_detail * 4.0 * fine;
  return clamp(s, 0.0, 1.0);
}

vec3 ramp(float s) {
  float x = clamp(s, 0.0, 1.0) * 3.0;
  if (x < 1.0) return mix(u_stops[0], u_stops[1], x);
  if (x < 2.0) return mix(u_stops[1], u_stops[2], x - 1.0);
  return mix(u_stops[2], u_stops[3], x - 2.0);
}

vec3 encode(vec3 linear) {
  vec3 low = linear * 12.92;
  vec3 high = 1.055 * pow(linear, vec3(1.0 / 2.4)) - 0.055;
  return mix(low, high, step(0.0031308, linear));
}

void main() {
  vec2 uv = gl_FragCoord.xy / u_resolution;
  float aspect = u_resolution.x / u_resolution.y;
  vec2 p = vec2(uv.x * aspect, uv.y) * u_scale;
  float speed = fieldValue(p, u_time);
  fragColor = vec4(encode(ramp(speed)), 1.0);
}
`;

export interface FieldRenderer {
  draw(layer: FieldLayer, time: number, width: number, height: number): void;
  destroy(): void;
}

function compile(gl: WebGL2RenderingContext, type: number, source: string): WebGLShader {
  const shader = gl.createShader(type);
  if (shader === null) throw new Error("Could not create a shader.");
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    const log = gl.getShaderInfoLog(shader) ?? "";
    gl.deleteShader(shader);
    throw new Error(`Shader failed to compile: ${log}`);
  }
  return shader;
}

/**
 * `null` where WebGL2 is unavailable, and the caller paints the static fallback.
 * `preserveDrawingBuffer` is on because vitrea imports the canvas on *its* frame,
 * after this one has drawn; a cleared buffer would hand the glass a black field.
 */
export function createFieldRenderer(canvas: HTMLCanvasElement): FieldRenderer | null {
  const gl = canvas.getContext("webgl2", {
    alpha: false,
    antialias: false,
    depth: false,
    stencil: false,
    preserveDrawingBuffer: true,
    powerPreference: "high-performance",
  });
  if (gl === null) return null;

  const program = gl.createProgram();
  if (program === null) return null;
  gl.attachShader(program, compile(gl, gl.VERTEX_SHADER, VERTEX));
  gl.attachShader(program, compile(gl, gl.FRAGMENT_SHADER, FRAGMENT));
  gl.linkProgram(program);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    throw new Error(`Program failed to link: ${gl.getProgramInfoLog(program) ?? ""}`);
  }
  gl.useProgram(program);

  const uniform = (name: string): WebGLUniformLocation | null => gl.getUniformLocation(program, name);
  const resolution = uniform("u_resolution");
  const time = uniform("u_time");
  const scale = uniform("u_scale");
  const warp = uniform("u_warp");
  const rate = uniform("u_rate");
  const detail = uniform("u_detail");
  const jet = uniform("u_jet");
  const front = uniform("u_front");
  const stops = uniform("u_stops");
  const stopBuffer = new Float32Array(12);

  return {
    draw(layer, t, width, height) {
      if (canvas.width !== width || canvas.height !== height) {
        canvas.width = width;
        canvas.height = height;
      }
      gl.viewport(0, 0, width, height);
      gl.uniform2f(resolution, width, height);
      gl.uniform1f(time, t);
      gl.uniform1f(scale, layer.scale);
      gl.uniform1f(warp, layer.warp);
      gl.uniform1f(rate, layer.rate);
      gl.uniform1f(detail, layer.detail);
      gl.uniform1f(jet, layer.jet);
      gl.uniform1f(front, layer.front);
      layer.stops.forEach((stop, index) => stopBuffer.set(stop.linear, index * 3));
      gl.uniform3fv(stops, stopBuffer);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    },
    // The context is left alive on purpose: a remount on the same canvas (React's
    // StrictMode does one) gets the same context back, and a deliberately lost
    // one would fail every compile after it with an empty log.
    destroy() {
      gl.deleteProgram(program);
    },
  };
}
