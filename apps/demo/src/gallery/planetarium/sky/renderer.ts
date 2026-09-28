/**
 * The sky, drawn: one WebGL2 canvas that is the environment vitrea samples.
 *
 * Four passes into a linear-light frame, then one pass that encodes it: (1) the sky itself per
 * pixel — night airglow, the Milky Way and the constellation figures sampled through the inverse
 * projection, twilight and day from the Sun's altitude, the ground below the horizon; (2) the
 * catalogue's stars and the planets as additive point sprites sized and coloured from magnitude
 * and B−V; (3) the Moon and the Sun as lit discs with a glow; (4) labels from a text atlas. The
 * final pass applies the page's dimming layer under each glass footprint (inward-feathered, so it
 * is a vignette inside the rim and never a halo outside it), the selection ring, the sRGB
 * transfer and a dither, because a dark gradient seen through a lens bands otherwise.
 *
 * `measure` renders the same frame at an eighth of the size and reads the mean level under each
 * box from those pixels — the tone input each glass group declares, taken from what is painted.
 */

import type { Vec3, View } from "./projection";
import type { StarCatalog } from "./catalog";

export interface DimRect {
  /** CSS px. */
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
  readonly radius: number;
  /** 0..1: how much light the layer removes under this footprint. */
  readonly strength: number;
  /** CSS px inside the edge over which the layer fades to nothing at the edge. */
  readonly feather: number;
}

export interface PointDraw {
  readonly ra: number;
  readonly dec: number;
  readonly mag: number;
  readonly bv: number;
}

export interface DiscDraw {
  readonly direction: Vec3;
  /** CSS px. */
  readonly radius: number;
  /** The light's direction in the disc's frame: screen-right, screen-up, toward the viewer. */
  readonly light: readonly [number, number, number];
  readonly colour: readonly [number, number, number];
  readonly glow: number;
  readonly sun: boolean;
}

export interface LabelDraw {
  readonly text: string;
  /** CSS px; the label's left edge and vertical centre. */
  readonly x: number;
  readonly y: number;
  readonly alpha: number;
}

export interface SkyFrame {
  readonly view: View;
  /** Radians. */
  readonly latitude: number;
  readonly lst: number;
  readonly sunAlt: number;
  readonly sunAz: number;
  readonly exposure: number;
  readonly figures: number;
  readonly planets: readonly PointDraw[];
  readonly discs: readonly DiscDraw[];
  readonly labels: readonly LabelDraw[];
  readonly ring: { readonly x: number; readonly y: number; readonly r: number; readonly alpha: number } | undefined;
  readonly dims: readonly DimRect[];
}

export interface Box {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

export interface Reading {
  /** Relative luminance from the encoded mean, decoded once. */
  readonly luminance: number;
  /** The encoded luma of the same mean. */
  readonly encoded: number;
}

const MAX_RECTS = 8;

const COMMON = /* glsl */ `
const float PI = 3.141592653589793;
vec3 dirOf(float alt, float az) { float c = cos(alt); return vec3(c * sin(az), c * cos(az), sin(alt)); }
vec3 basisRight(float az) { return vec3(cos(az), -sin(az), 0.0); }
vec3 basisUp(float alt, float az) { return vec3(-sin(alt) * sin(az), -sin(alt) * cos(az), cos(alt)); }
// Centred device px, y up; z is the cosine of the angle from the view centre.
vec3 projectDir(vec3 v, vec3 view) {
  vec3 c = dirOf(view.y, view.x);
  float cosC = dot(v, c);
  float k = 2.0 / (1.0 + max(cosC, -0.95));
  return vec3(k * dot(v, basisRight(view.x)) * view.z, k * dot(v, basisUp(view.y, view.x)) * view.z, cosC);
}
vec3 unprojectPx(vec2 p, vec3 view) {
  vec3 c = dirOf(view.y, view.x);
  vec3 r = basisRight(view.x);
  vec3 u = basisUp(view.y, view.x);
  vec2 q = p / view.z;
  float rho = length(q);
  if (rho < 1e-6) return c;
  float ang = 2.0 * atan(rho * 0.5);
  float s = sin(ang) / rho;
  return cos(ang) * c + s * (q.x * r + q.y * u);
}
vec3 horizontalOf(float ra, float dec, float lst, float lat) {
  float h = lst - ra;
  float cd = cos(dec);
  float xh = cd * cos(h);
  float yh = cd * sin(h);
  float zh = sin(dec);
  return vec3(-yh, zh * cos(lat) - xh * sin(lat), zh * sin(lat) + xh * cos(lat));
}
vec2 equatorialUv(vec3 v, float lst, float lat) {
  float xh = v.z * cos(lat) - v.y * sin(lat);
  float zh = v.z * sin(lat) + v.y * cos(lat);
  float yh = -v.x;
  float h = atan(yh, xh);
  float dec = asin(clamp(zh, -1.0, 1.0));
  float ra = lst - h;
  return vec2(fract(0.5 - ra / (2.0 * PI)), 0.5 - dec / PI);
}
`;

const FULLSCREEN_VS = /* glsl */ `#version 300 es
void main() {
  vec2 p = vec2((gl_VertexID == 1) ? 3.0 : -1.0, (gl_VertexID == 2) ? 3.0 : -1.0);
  gl_Position = vec4(p, 0.0, 1.0);
}
`;

const SKY_FS = /* glsl */ `#version 300 es
precision highp float;
${COMMON}
uniform vec2 u_res;
uniform vec3 u_view;
uniform float u_lat;
uniform float u_lst;
uniform vec2 u_sun;
uniform float u_exposure;
uniform float u_figures;
uniform sampler2D u_milky;
uniform sampler2D u_fig;
out vec4 o;
void main() {
  vec2 p = gl_FragCoord.xy - u_res * 0.5;
  vec3 v = unprojectPx(p, u_view);
  float alt = asin(clamp(v.z, -1.0, 1.0));
  vec3 sunDir = dirOf(u_sun.x, u_sun.y);
  float sunSep = acos(clamp(dot(v, sunDir), -1.0, 1.0));
  float sunAlt = u_sun.x;
  float kDay = smoothstep(-0.105, 0.07, sunAlt);
  float kTw = smoothstep(-0.31, -0.035, sunAlt);
  float starVis = 1.0 - smoothstep(-0.21, -0.02, sunAlt);
  float up = clamp(alt, 0.0, 1.5708) / 1.5708;
  vec3 night = mix(vec3(0.0075, 0.0090, 0.0170), vec3(0.036, 0.031, 0.028), pow(1.0 - up, 4.0));
  vec2 uv = equatorialUv(v, u_lst, u_lat);
  vec3 milky = texture(u_milky, uv).rgb * u_exposure;
  float fig = texture(u_fig, uv).r;
  float toSun = exp(-sunSep / 0.5) * pow(1.0 - up, 2.0);
  vec3 twilight = mix(vec3(0.045, 0.075, 0.20), vec3(0.85, 0.40, 0.12), toSun) * kTw * 0.32;
  vec3 day = mix(vec3(0.62, 0.70, 0.82), vec3(0.11, 0.27, 0.62), pow(up, 0.5)) + vec3(1.0, 0.95, 0.85) * exp(-sunSep / 0.3) * 0.45;
  vec3 sky = (night + milky * starVis + twilight) * (1.0 - kDay) + day * kDay;
  sky += vec3(0.62, 0.72, 1.0) * fig * u_figures * starVis;
  if (sunAlt > -0.03) {
    float disc = 1.0 - smoothstep(0.0044, 0.0060, sunSep);
    sky += vec3(6.0, 5.6, 5.0) * disc;
    sky += vec3(1.0, 0.85, 0.6) * exp(-sunSep / 0.035) * 0.9;
  }
  // The ground: a low ridge, its height a slow function of azimuth, dark, with the sky's own
  // light falling off just above it and a faint glow on the ridge itself.
  float az = atan(v.x, v.y);
  float ridge = 0.012 + 0.010 * sin(az * 3.0 + 0.7) + 0.006 * sin(az * 7.0 - 1.9) + 0.004 * sin(az * 13.0 + 2.3);
  if (alt < ridge) {
    vec3 ground = mix(vec3(0.0030, 0.0036, 0.0055), vec3(0.050, 0.058, 0.046), kDay);
    vec3 horizon = (night + twilight * 0.7) * (1.0 - kDay) + day * kDay * 0.35;
    float depth = (ridge - alt);
    float rim = exp(-depth / 0.004);
    sky = ground + horizon * rim * 0.35 + ground * exp(-depth / 0.03) * 0.8;
  } else {
    float haze = exp(-(alt - ridge) / 0.012);
    sky += ((night + twilight * 0.7) * (1.0 - kDay) + day * kDay * 0.25) * haze * 0.35;
  }
  o = vec4(sky, 1.0);
}
`;

const STAR_VS = /* glsl */ `#version 300 es
${COMMON}
in vec4 a_star;
uniform vec2 u_res;
uniform vec3 u_view;
uniform float u_lat;
uniform float u_lst;
uniform float u_dpr;
uniform float u_sunAlt;
uniform float u_planet;
out vec3 v_col;
out float v_int;
vec3 colourOf(float bv) {
  bv = clamp(bv, -0.4, 2.0);
  vec3 a = vec3(0.60, 0.72, 1.00);
  vec3 b = vec3(0.86, 0.91, 1.00);
  vec3 c = vec3(1.00, 0.96, 0.86);
  vec3 d = vec3(1.00, 0.80, 0.58);
  vec3 e = vec3(1.00, 0.62, 0.36);
  if (bv < 0.0) return mix(a, b, (bv + 0.4) / 0.4);
  if (bv < 0.6) return mix(b, c, bv / 0.6);
  if (bv < 1.2) return mix(c, d, (bv - 0.6) / 0.6);
  return mix(d, e, (bv - 1.2) / 0.8);
}
void main() {
  vec3 v = horizontalOf(a_star.x, a_star.y, u_lst, u_lat);
  float alt = asin(clamp(v.z, -1.0, 1.0));
  vec3 pr = projectDir(v, u_view);
  if (alt < -0.005 || pr.z < -0.3) {
    gl_Position = vec4(2.0, 2.0, 0.0, 1.0);
    gl_PointSize = 0.0;
    v_int = 0.0;
    v_col = vec3(0.0);
    return;
  }
  gl_Position = vec4(pr.xy / (u_res * 0.5), 0.0, 1.0);
  float mag = a_star.z;
  float starVis = 1.0 - smoothstep(-0.21, -0.02, u_sunAlt);
  float size = clamp((6.8 - mag) * 1.05, 1.7, 11.0) * u_dpr * (1.0 + 0.35 * u_planet);
  gl_PointSize = size;
  float bright = clamp(0.10 + 0.90 * (5.6 - mag) / 7.1, 0.06, 1.0);
  float extinction = 1.0 - 0.75 * exp(-alt / 0.07);
  v_int = bright * extinction * starVis * (1.0 + 0.4 * u_planet);
  v_col = colourOf(a_star.w);
}
`;

const STAR_FS = /* glsl */ `#version 300 es
precision highp float;
in vec3 v_col;
in float v_int;
out vec4 o;
void main() {
  vec2 p = gl_PointCoord * 2.0 - 1.0;
  float d2 = dot(p, p);
  if (d2 > 1.0) discard;
  float a = exp(-d2 * 4.2) * v_int;
  o = vec4(v_col * a, 0.0);
}
`;

const DISC_VS = /* glsl */ `#version 300 es
in vec2 a_corner;
uniform vec2 u_res;
uniform vec2 u_centre;
uniform float u_size;
out vec2 v_p;
void main() {
  v_p = a_corner;
  vec2 px = u_centre + a_corner * u_size;
  gl_Position = vec4(px / (u_res * 0.5), 0.0, 1.0);
}
`;

const DISC_FS = /* glsl */ `#version 300 es
precision highp float;
in vec2 v_p;
uniform vec3 u_light;
uniform vec3 u_col;
uniform float u_glow;
uniform float u_disc;
uniform float u_sun;
uniform float u_px;
out vec4 o;
void main() {
  float r = length(v_p);
  float rd = r / u_disc;
  float aa = u_px / u_disc;
  float edge = 1.0 - smoothstep(1.0 - aa, 1.0 + aa, rd);
  vec3 body = vec3(0.0);
  if (rd < 1.0 + aa) {
    float z = sqrt(max(0.0, 1.0 - min(rd, 1.0) * min(rd, 1.0)));
    vec3 n = vec3(v_p / u_disc, z);
    float lit = max(0.0, dot(n, u_light));
    body = mix(u_col * (lit * 1.7 + 0.025), vec3(9.0, 8.4, 7.4), u_sun);
  }
  float glow = exp(-(max(r - u_disc, 0.0)) / mix(0.22, 0.45, u_sun)) * u_glow * (1.0 - smoothstep(0.6, 1.0, r));
  o = vec4(body * edge + u_col * glow * (1.0 - edge), edge);
}
`;

const LABEL_VS = /* glsl */ `#version 300 es
in vec2 a_pos;
in vec2 a_uv;
in float a_alpha;
uniform vec2 u_res;
out vec2 v_uv;
out float v_alpha;
void main() {
  v_uv = a_uv;
  v_alpha = a_alpha;
  gl_Position = vec4(a_pos / (u_res * 0.5), 0.0, 1.0);
}
`;

const LABEL_FS = /* glsl */ `#version 300 es
precision highp float;
in vec2 v_uv;
in float v_alpha;
uniform sampler2D u_atlas;
out vec4 o;
void main() {
  vec4 t = texture(u_atlas, v_uv);
  // The atlas is sRGB-encoded and premultiplied; decode to the frame's linear light.
  vec3 c = pow(max(t.rgb, 0.0), vec3(2.2)) * (t.a > 0.0 ? 1.0 : 0.0);
  o = vec4(c * v_alpha * 0.85, t.a * v_alpha);
}
`;

const FINAL_FS = /* glsl */ `#version 300 es
precision highp float;
uniform sampler2D u_scene;
uniform vec2 u_res;
uniform vec4 u_rect[${String(MAX_RECTS)}];
uniform vec3 u_rectRS[${String(MAX_RECTS)}];
uniform int u_rectN;
uniform vec4 u_ring;
uniform float u_seed;
out vec4 o;
float roundedBox(vec2 p, vec4 rect, float r) {
  vec2 he = rect.zw * 0.5;
  vec2 q = abs(p - (rect.xy + he)) - (he - vec2(r));
  return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r;
}
vec3 encode(vec3 c) {
  vec3 lo = 12.92 * c;
  vec3 hi = 1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055;
  return mix(lo, hi, step(vec3(0.0031308), c));
}
float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233)) + u_seed) * 43758.5453); }
void main() {
  vec2 px = vec2(gl_FragCoord.x, u_res.y - gl_FragCoord.y);
  vec3 c = texture(u_scene, gl_FragCoord.xy / u_res).rgb;
  for (int i = 0; i < ${String(MAX_RECTS)}; i++) {
    if (i >= u_rectN) break;
    float d = roundedBox(px, u_rect[i], u_rectRS[i].x);
    float cover = 1.0 - smoothstep(-u_rectRS[i].z, 0.0, d);
    c *= 1.0 - u_rectRS[i].y * cover;
  }
  if (u_ring.w > 0.0) {
    float dist = abs(length(px - u_ring.xy) - u_ring.z);
    c += vec3(0.75, 0.85, 1.0) * (1.0 - smoothstep(0.6, 1.9, dist)) * u_ring.w;
  }
  vec3 e = encode(clamp(c, 0.0, 1.0));
  e += (hash(gl_FragCoord.xy) - 0.5) / 255.0;
  o = vec4(clamp(e, 0.0, 1.0), 1.0);
}
`;

interface Target {
  readonly scene: WebGLFramebuffer;
  readonly sceneTexture: WebGLTexture;
  readonly out: WebGLFramebuffer | null;
  /** The measurement target's 8-bit output, held so it is released with its framebuffer. */
  readonly outTexture: WebGLTexture | null;
  width: number;
  height: number;
}

interface AtlasEntry {
  readonly u0: number;
  readonly v0: number;
  readonly u1: number;
  readonly v1: number;
  /** CSS px at scale 1. */
  readonly width: number;
  readonly height: number;
}

const ATLAS_SCALE = 2;
/** A quarter: at an eighth a 48 px capsule was six rows and its edge rows read as undimmed sky. */
const MEASURE_SCALE = 1 / 4;

export class SkyRenderer {
  private readonly gl: WebGL2RenderingContext;
  private readonly skyProgram: WebGLProgram;
  private readonly starProgram: WebGLProgram;
  private readonly discProgram: WebGLProgram;
  private readonly labelProgram: WebGLProgram;
  private readonly finalProgram: WebGLProgram;
  private readonly milky: WebGLTexture;
  private readonly figures: WebGLTexture;
  private readonly atlas: WebGLTexture;
  private atlasEntries = new Map<string, AtlasEntry>();
  private readonly starBuffer: WebGLBuffer;
  private starCount = 0;
  private readonly planetBuffer: WebGLBuffer;
  private readonly cornerBuffer: WebGLBuffer;
  private readonly labelBuffer: WebGLBuffer;
  private readonly vaoStars: WebGLVertexArrayObject;
  private readonly vaoPlanets: WebGLVertexArrayObject;
  private readonly vaoDisc: WebGLVertexArrayObject;
  private readonly vaoLabels: WebGLVertexArrayObject;
  private readonly vaoEmpty: WebGLVertexArrayObject;
  private readonly floatTargets: boolean;
  private screen: Target | undefined;
  private small: Target | undefined;
  private smallPixels: Uint8Array = new Uint8Array(0);
  private width = 1;
  private height = 1;
  private dpr = 1;
  private disposed = false;
  readonly canvas: HTMLCanvasElement;

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    const gl = canvas.getContext("webgl2", {
      alpha: false,
      antialias: false,
      depth: false,
      stencil: false,
      preserveDrawingBuffer: true,
      premultipliedAlpha: true,
      powerPreference: "high-performance",
    });
    if (gl === null) throw new Error("Tonight needs WebGL2 to draw its sky.");
    this.gl = gl;
    this.floatTargets = gl.getExtension("EXT_color_buffer_float") !== null;
    const aniso = gl.getExtension("EXT_texture_filter_anisotropic");
    this.skyProgram = program(gl, FULLSCREEN_VS, SKY_FS);
    this.starProgram = program(gl, STAR_VS, STAR_FS);
    this.discProgram = program(gl, DISC_VS, DISC_FS);
    this.labelProgram = program(gl, LABEL_VS, LABEL_FS);
    this.finalProgram = program(gl, FULLSCREEN_VS, FINAL_FS);

    this.milky = texture(gl);
    this.figures = texture(gl);
    this.atlas = texture(gl);
    if (aniso !== null) {
      for (const t of [this.milky, this.figures]) {
        gl.bindTexture(gl.TEXTURE_2D, t);
        gl.texParameterf(gl.TEXTURE_2D, aniso.TEXTURE_MAX_ANISOTROPY_EXT, 8);
      }
    }
    // A 1 × 1 placeholder in each, so a frame before the images decode draws a plain sky.
    for (const t of [this.milky, this.figures, this.atlas]) {
      gl.bindTexture(gl.TEXTURE_2D, t);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array(4));
    }

    this.starBuffer = buffer(gl);
    this.planetBuffer = buffer(gl);
    this.cornerBuffer = buffer(gl);
    this.labelBuffer = buffer(gl);
    gl.bindBuffer(gl.ARRAY_BUFFER, this.cornerBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]), gl.STATIC_DRAW);

    this.vaoEmpty = vao(gl);
    this.vaoStars = vao(gl);
    this.bindStarAttributes(this.vaoStars, this.starBuffer);
    this.vaoPlanets = vao(gl);
    this.bindStarAttributes(this.vaoPlanets, this.planetBuffer);
    this.vaoDisc = vao(gl);
    gl.bindVertexArray(this.vaoDisc);
    gl.bindBuffer(gl.ARRAY_BUFFER, this.cornerBuffer);
    const corner = gl.getAttribLocation(this.discProgram, "a_corner");
    gl.enableVertexAttribArray(corner);
    gl.vertexAttribPointer(corner, 2, gl.FLOAT, false, 0, 0);
    this.vaoLabels = vao(gl);
    gl.bindVertexArray(this.vaoLabels);
    gl.bindBuffer(gl.ARRAY_BUFFER, this.labelBuffer);
    const pos = gl.getAttribLocation(this.labelProgram, "a_pos");
    const uv = gl.getAttribLocation(this.labelProgram, "a_uv");
    const alpha = gl.getAttribLocation(this.labelProgram, "a_alpha");
    gl.enableVertexAttribArray(pos);
    gl.vertexAttribPointer(pos, 2, gl.FLOAT, false, 20, 0);
    gl.enableVertexAttribArray(uv);
    gl.vertexAttribPointer(uv, 2, gl.FLOAT, false, 20, 8);
    gl.enableVertexAttribArray(alpha);
    gl.vertexAttribPointer(alpha, 1, gl.FLOAT, false, 20, 16);
    gl.bindVertexArray(null);
  }

  private bindStarAttributes(target: WebGLVertexArrayObject, source: WebGLBuffer): void {
    const { gl } = this;
    gl.bindVertexArray(target);
    gl.bindBuffer(gl.ARRAY_BUFFER, source);
    const loc = gl.getAttribLocation(this.starProgram, "a_star");
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 4, gl.FLOAT, false, 0, 0);
    gl.bindVertexArray(null);
  }

  /** Decode and upload the two sky maps. Resolves when both are on the GPU. */
  async load(milkyWayUrl: string, figuresUrl: string): Promise<void> {
    const [milky, figures] = await Promise.all([decode(milkyWayUrl), decode(figuresUrl)]);
    if (this.disposed) {
      milky.close();
      figures.close();
      return;
    }
    const { gl } = this;
    gl.bindTexture(gl.TEXTURE_2D, this.milky);
    gl.pixelStorei(gl.UNPACK_COLORSPACE_CONVERSION_WEBGL, gl.NONE);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.SRGB8_ALPHA8, gl.RGBA, gl.UNSIGNED_BYTE, milky);
    gl.generateMipmap(gl.TEXTURE_2D);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
    gl.bindTexture(gl.TEXTURE_2D, this.figures);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.R8, gl.RED, gl.UNSIGNED_BYTE, figures);
    gl.generateMipmap(gl.TEXTURE_2D);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
    milky.close();
    figures.close();
  }

  setStars(catalog: StarCatalog): void {
    const data = new Float32Array(catalog.count * 4);
    for (let i = 0; i < catalog.count; i += 1) {
      data[i * 4] = catalog.ra[i] as number;
      data[i * 4 + 1] = catalog.dec[i] as number;
      data[i * 4 + 2] = catalog.mag[i] as number;
      data[i * 4 + 3] = catalog.bv[i] as number;
    }
    const { gl } = this;
    gl.bindBuffer(gl.ARRAY_BUFFER, this.starBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, data, gl.STATIC_DRAW);
    this.starCount = catalog.count;
  }

  /** Draw every label the page may show into the atlas, once. */
  setLabels(labels: readonly string[]): void {
    const scale = ATLAS_SCALE;
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    if (context === null) return;
    const font = `600 ${String(12.5 * scale)}px -apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif`;
    context.font = font;
    const pad = 4 * scale;
    const lineHeight = 18 * scale;
    const widths = labels.map((label) => Math.ceil(context.measureText(label).width) + pad * 2);
    const atlasWidth = 1024;
    let x = 0;
    let row = 0;
    const placed: { label: string; x: number; y: number; width: number }[] = [];
    labels.forEach((label, i) => {
      const width = widths[i] as number;
      if (x + width > atlasWidth) {
        x = 0;
        row += 1;
      }
      placed.push({ label, x, y: row * lineHeight, width });
      x += width;
    });
    const atlasHeight = Math.max(1, (row + 1) * lineHeight);
    canvas.width = atlasWidth;
    canvas.height = atlasHeight;
    context.font = font;
    context.textBaseline = "middle";
    context.fillStyle = "#fff";
    context.shadowColor = "rgba(0,0,0,0.9)";
    context.shadowBlur = 3 * scale;
    const entries = new Map<string, AtlasEntry>();
    for (const entry of placed) {
      context.fillText(entry.label, entry.x + pad, entry.y + lineHeight / 2);
      entries.set(entry.label, {
        u0: entry.x / atlasWidth,
        v0: entry.y / atlasHeight,
        u1: (entry.x + entry.width) / atlasWidth,
        v1: (entry.y + lineHeight) / atlasHeight,
        width: entry.width / scale,
        height: lineHeight / scale,
      });
    }
    const { gl } = this;
    gl.bindTexture(gl.TEXTURE_2D, this.atlas);
    gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, true);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, canvas);
    gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    this.atlasEntries = entries;
  }

  resize(width: number, height: number, dpr: number): void {
    const w = Math.max(1, Math.round(width * dpr));
    const h = Math.max(1, Math.round(height * dpr));
    if (this.canvas.width !== w) this.canvas.width = w;
    if (this.canvas.height !== h) this.canvas.height = h;
    this.width = width;
    this.height = height;
    this.dpr = dpr;
    this.screen = this.ensureTarget(this.screen, w, h, null);
    const sw = Math.max(8, Math.round(w * MEASURE_SCALE));
    const sh = Math.max(8, Math.round(h * MEASURE_SCALE));
    this.small = this.ensureTarget(this.small, sw, sh, "fbo");
    if (this.smallPixels.length !== sw * sh * 4) this.smallPixels = new Uint8Array(sw * sh * 4);
  }

  private ensureTarget(existing: Target | undefined, w: number, h: number, out: null | "fbo"): Target {
    const { gl } = this;
    if (existing !== undefined && existing.width === w && existing.height === h) return existing;
    if (existing !== undefined) this.releaseTarget(existing);
    const sceneTexture = texture(gl);
    gl.bindTexture(gl.TEXTURE_2D, sceneTexture);
    if (this.floatTargets) {
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA16F, w, h, 0, gl.RGBA, gl.HALF_FLOAT, null);
    } else {
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA8, w, h, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
    }
    const scene = gl.createFramebuffer();
    gl.bindFramebuffer(gl.FRAMEBUFFER, scene);
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, sceneTexture, 0);
    let outFbo: WebGLFramebuffer | null = null;
    let outTexture: WebGLTexture | null = null;
    if (out === "fbo") {
      outTexture = texture(gl);
      gl.bindTexture(gl.TEXTURE_2D, outTexture);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA8, w, h, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
      outFbo = gl.createFramebuffer();
      gl.bindFramebuffer(gl.FRAMEBUFFER, outFbo);
      gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, outTexture, 0);
    }
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    return { scene, sceneTexture, out: outFbo, outTexture, width: w, height: h };
  }

  private releaseTarget(target: Target): void {
    const { gl } = this;
    gl.deleteFramebuffer(target.scene);
    gl.deleteTexture(target.sceneTexture);
    if (target.out !== null) gl.deleteFramebuffer(target.out);
    if (target.outTexture !== null) gl.deleteTexture(target.outTexture);
  }

  render(frame: SkyFrame): void {
    if (this.screen === undefined) return;
    // The dither is one fixed pattern, not a new one per frame: a lens over changing noise crawls.
    this.draw(this.screen, frame, this.dpr, true);
  }

  /**
   * The mean level under each box, read from a quarter-scale render of the same frame — with or
   * without the dimming layer, so a page can size the layer from the undimmed level and then
   * declare the composite it painted.
   */
  measure(frame: SkyFrame, boxes: readonly Box[], withDimming: boolean): (Reading | undefined)[] {
    const target = this.small;
    if (target === undefined || target.out === null) return boxes.map(() => undefined);
    const scale = target.width / this.width;
    this.draw(target, withDimming ? frame : { ...frame, dims: [] }, this.dpr * MEASURE_SCALE, false);
    const { gl } = this;
    gl.bindFramebuffer(gl.FRAMEBUFFER, target.out);
    gl.readPixels(0, 0, target.width, target.height, gl.RGBA, gl.UNSIGNED_BYTE, this.smallPixels);
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    const pixels = this.smallPixels;
    return boxes.map((box) => {
      const x0 = Math.max(0, Math.floor(box.x * scale));
      const x1 = Math.min(target.width, Math.ceil((box.x + box.width) * scale));
      // readPixels rows run bottom to top.
      const yTop = Math.max(0, Math.floor(box.y * scale));
      const yBottom = Math.min(target.height, Math.ceil((box.y + box.height) * scale));
      if (x1 <= x0 || yBottom <= yTop) return undefined;
      let r = 0;
      let g = 0;
      let b = 0;
      let n = 0;
      for (let y = yTop; y < yBottom; y += 1) {
        const row = target.height - 1 - y;
        let i = (row * target.width + x0) * 4;
        for (let x = x0; x < x1; x += 1, i += 4) {
          r += pixels[i] as number;
          g += pixels[i + 1] as number;
          b += pixels[i + 2] as number;
          n += 1;
        }
      }
      const level = [r / n / 255, g / n / 255, b / n / 255] as const;
      const luminance = 0.2126 * decodeSrgb(level[0]) + 0.7152 * decodeSrgb(level[1]) + 0.0722 * decodeSrgb(level[2]);
      const encoded = 0.2126 * level[0] + 0.7152 * level[1] + 0.0722 * level[2];
      return { luminance, encoded };
    });
  }

  private draw(target: Target, frame: SkyFrame, dpr: number, dither: boolean): void {
    const { gl } = this;
    const w = target.width;
    const h = target.height;
    const view = [frame.view.az, frame.view.alt, frame.view.focal * dpr] as const;
    gl.bindFramebuffer(gl.FRAMEBUFFER, target.scene);
    gl.viewport(0, 0, w, h);
    gl.disable(gl.BLEND);

    // 1. The sky.
    gl.useProgram(this.skyProgram);
    gl.bindVertexArray(this.vaoEmpty);
    this.uniform2(this.skyProgram, "u_res", w, h);
    this.uniform3(this.skyProgram, "u_view", view[0], view[1], view[2]);
    this.uniform1(this.skyProgram, "u_lat", frame.latitude);
    this.uniform1(this.skyProgram, "u_lst", frame.lst);
    this.uniform2(this.skyProgram, "u_sun", frame.sunAlt, frame.sunAz);
    this.uniform1(this.skyProgram, "u_exposure", frame.exposure);
    this.uniform1(this.skyProgram, "u_figures", frame.figures);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.milky);
    gl.uniform1i(gl.getUniformLocation(this.skyProgram, "u_milky"), 0);
    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(gl.TEXTURE_2D, this.figures);
    gl.uniform1i(gl.getUniformLocation(this.skyProgram, "u_fig"), 1);
    gl.drawArrays(gl.TRIANGLES, 0, 3);

    // 2. Stars and planets, additive.
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.ONE, gl.ONE);
    gl.useProgram(this.starProgram);
    this.uniform2(this.starProgram, "u_res", w, h);
    this.uniform3(this.starProgram, "u_view", view[0], view[1], view[2]);
    this.uniform1(this.starProgram, "u_lat", frame.latitude);
    this.uniform1(this.starProgram, "u_lst", frame.lst);
    this.uniform1(this.starProgram, "u_dpr", dpr);
    this.uniform1(this.starProgram, "u_sunAlt", frame.sunAlt);
    this.uniform1(this.starProgram, "u_planet", 0);
    gl.bindVertexArray(this.vaoStars);
    gl.drawArrays(gl.POINTS, 0, this.starCount);
    if (frame.planets.length > 0) {
      const data = new Float32Array(frame.planets.length * 4);
      frame.planets.forEach((p, i) => {
        data[i * 4] = p.ra;
        data[i * 4 + 1] = p.dec;
        data[i * 4 + 2] = p.mag;
        data[i * 4 + 3] = p.bv;
      });
      gl.bindBuffer(gl.ARRAY_BUFFER, this.planetBuffer);
      gl.bufferData(gl.ARRAY_BUFFER, data, gl.DYNAMIC_DRAW);
      this.uniform1(this.starProgram, "u_planet", 1);
      gl.bindVertexArray(this.vaoPlanets);
      gl.drawArrays(gl.POINTS, 0, frame.planets.length);
    }

    // 3. The Moon and the Sun, premultiplied over.
    gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
    gl.useProgram(this.discProgram);
    gl.bindVertexArray(this.vaoDisc);
    this.uniform2(this.discProgram, "u_res", w, h);
    for (const disc of frame.discs) {
      const centre = projectPx(disc.direction, frame.view, dpr, w, h);
      if (centre === undefined) continue;
      const discPx = disc.radius * dpr;
      const size = discPx * 6;
      this.uniform2(this.discProgram, "u_centre", centre[0], centre[1]);
      this.uniform1(this.discProgram, "u_size", size);
      this.uniform1(this.discProgram, "u_disc", 1 / 6);
      this.uniform1(this.discProgram, "u_px", 1 / size);
      this.uniform3(this.discProgram, "u_light", disc.light[0], disc.light[1], disc.light[2]);
      this.uniform3(this.discProgram, "u_col", disc.colour[0], disc.colour[1], disc.colour[2]);
      this.uniform1(this.discProgram, "u_glow", disc.glow);
      this.uniform1(this.discProgram, "u_sun", disc.sun ? 1 : 0);
      gl.drawArrays(gl.TRIANGLES, 0, 6);
    }

    // 4. Labels.
    if (frame.labels.length > 0 && this.atlasEntries.size > 0) {
      const verts: number[] = [];
      for (const label of frame.labels) {
        const entry = this.atlasEntries.get(label.text);
        if (entry === undefined) continue;
        const x0 = (label.x - this.width / 2) * dpr;
        const y0 = (this.height / 2 - label.y) * dpr - (entry.height * dpr) / 2;
        const x1 = x0 + entry.width * dpr;
        const y1 = y0 + entry.height * dpr;
        const a = label.alpha;
        verts.push(
          x0, y0, entry.u0, entry.v1, a,
          x1, y0, entry.u1, entry.v1, a,
          x0, y1, entry.u0, entry.v0, a,
          x0, y1, entry.u0, entry.v0, a,
          x1, y0, entry.u1, entry.v1, a,
          x1, y1, entry.u1, entry.v0, a,
        );
      }
      if (verts.length > 0) {
        gl.useProgram(this.labelProgram);
        gl.bindVertexArray(this.vaoLabels);
        gl.bindBuffer(gl.ARRAY_BUFFER, this.labelBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(verts), gl.DYNAMIC_DRAW);
        this.uniform2(this.labelProgram, "u_res", w, h);
        gl.activeTexture(gl.TEXTURE2);
        gl.bindTexture(gl.TEXTURE_2D, this.atlas);
        gl.uniform1i(gl.getUniformLocation(this.labelProgram, "u_atlas"), 2);
        gl.drawArrays(gl.TRIANGLES, 0, verts.length / 5);
      }
    }

    // 5. Dimming, the ring, the transfer and the dither.
    gl.disable(gl.BLEND);
    gl.bindFramebuffer(gl.FRAMEBUFFER, target.out);
    gl.viewport(0, 0, w, h);
    gl.useProgram(this.finalProgram);
    gl.bindVertexArray(this.vaoEmpty);
    gl.activeTexture(gl.TEXTURE3);
    gl.bindTexture(gl.TEXTURE_2D, target.sceneTexture);
    gl.uniform1i(gl.getUniformLocation(this.finalProgram, "u_scene"), 3);
    this.uniform2(this.finalProgram, "u_res", w, h);
    const rects = new Float32Array(MAX_RECTS * 4);
    const rs = new Float32Array(MAX_RECTS * 3);
    const n = Math.min(MAX_RECTS, frame.dims.length);
    for (let i = 0; i < n; i += 1) {
      const d = frame.dims[i] as DimRect;
      rects[i * 4] = d.x * dpr;
      rects[i * 4 + 1] = d.y * dpr;
      rects[i * 4 + 2] = d.width * dpr;
      rects[i * 4 + 3] = d.height * dpr;
      rs[i * 3] = Math.min(d.radius, d.width / 2, d.height / 2) * dpr;
      rs[i * 3 + 1] = d.strength;
      rs[i * 3 + 2] = d.feather * dpr;
    }
    gl.uniform4fv(gl.getUniformLocation(this.finalProgram, "u_rect"), rects);
    gl.uniform3fv(gl.getUniformLocation(this.finalProgram, "u_rectRS"), rs);
    gl.uniform1i(gl.getUniformLocation(this.finalProgram, "u_rectN"), n);
    const ring = frame.ring;
    gl.uniform4f(
      gl.getUniformLocation(this.finalProgram, "u_ring"),
      ring === undefined ? 0 : ring.x * dpr,
      ring === undefined ? 0 : ring.y * dpr,
      ring === undefined ? 0 : ring.r * dpr,
      ring === undefined ? 0 : ring.alpha,
    );
    this.uniform1(this.finalProgram, "u_seed", dither ? 17.31 : 0);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
  }

  private uniform1(p: WebGLProgram, name: string, x: number): void {
    this.gl.uniform1f(this.gl.getUniformLocation(p, name), x);
  }
  private uniform2(p: WebGLProgram, name: string, x: number, y: number): void {
    this.gl.uniform2f(this.gl.getUniformLocation(p, name), x, y);
  }
  private uniform3(p: WebGLProgram, name: string, x: number, y: number, z: number): void {
    this.gl.uniform3f(this.gl.getUniformLocation(p, name), x, y, z);
  }

  /**
   * Release what this renderer allocated. The context itself is kept: a canvas hands back the same
   * context to a renderer mounted after this one (React's strict effects mount twice), and a lost
   * context would compile nothing for it.
   */
  dispose(): void {
    this.disposed = true;
    const { gl } = this;
    for (const p of [this.skyProgram, this.starProgram, this.discProgram, this.labelProgram, this.finalProgram]) gl.deleteProgram(p);
    for (const t of [this.milky, this.figures, this.atlas]) gl.deleteTexture(t);
    for (const b of [this.starBuffer, this.planetBuffer, this.cornerBuffer, this.labelBuffer]) gl.deleteBuffer(b);
    for (const v of [this.vaoStars, this.vaoPlanets, this.vaoDisc, this.vaoLabels, this.vaoEmpty]) gl.deleteVertexArray(v);
    for (const target of [this.screen, this.small]) {
      if (target !== undefined) this.releaseTarget(target);
    }
  }
}

/** Centred device px, y up, of a direction; `undefined` far behind the view. */
function projectPx(v: Vec3, view: View, dpr: number, w: number, h: number): readonly [number, number] | undefined {
  const az = view.az;
  const alt = view.alt;
  const c: Vec3 = [Math.cos(alt) * Math.sin(az), Math.cos(alt) * Math.cos(az), Math.sin(alt)];
  const right: Vec3 = [Math.cos(az), -Math.sin(az), 0];
  const up: Vec3 = [-Math.sin(alt) * Math.sin(az), -Math.sin(alt) * Math.cos(az), Math.cos(alt)];
  const dot = (a: Vec3, b: Vec3): number => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const cosC = dot(v, c);
  if (cosC < -0.3) return undefined;
  const k = 2 / (1 + cosC);
  const focal = view.focal * dpr;
  const x = k * dot(v, right) * focal;
  const y = k * dot(v, up) * focal;
  if (Math.abs(x) > w || Math.abs(y) > h) return undefined;
  return [x, y];
}

function decodeSrgb(encoded: number): number {
  return encoded <= 0.04045 ? encoded / 12.92 : Math.pow((encoded + 0.055) / 1.055, 2.4);
}

async function decode(url: string): Promise<ImageBitmap> {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`A sky map did not load (${String(response.status)}).`);
  return createImageBitmap(await response.blob(), { colorSpaceConversion: "none", premultiplyAlpha: "none" });
}

function program(gl: WebGL2RenderingContext, vs: string, fs: string): WebGLProgram {
  const p = gl.createProgram();
  const v = shader(gl, gl.VERTEX_SHADER, vs);
  const f = shader(gl, gl.FRAGMENT_SHADER, fs);
  gl.attachShader(p, v);
  gl.attachShader(p, f);
  gl.linkProgram(p);
  if (gl.getProgramParameter(p, gl.LINK_STATUS) !== true) {
    throw new Error(`Sky shader link failed: ${gl.getProgramInfoLog(p) ?? ""}`);
  }
  gl.deleteShader(v);
  gl.deleteShader(f);
  return p;
}

function shader(gl: WebGL2RenderingContext, kind: number, source: string): WebGLShader {
  const s = gl.createShader(kind);
  if (s === null) throw new Error("Sky shader could not be created.");
  gl.shaderSource(s, source);
  gl.compileShader(s);
  if (gl.getShaderParameter(s, gl.COMPILE_STATUS) !== true) {
    throw new Error(`Sky shader compile failed: ${gl.getShaderInfoLog(s) ?? ""}`);
  }
  return s;
}

function texture(gl: WebGL2RenderingContext): WebGLTexture {
  const t = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, t);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  return t;
}

function buffer(gl: WebGL2RenderingContext): WebGLBuffer {
  return gl.createBuffer();
}

function vao(gl: WebGL2RenderingContext): WebGLVertexArrayObject {
  return gl.createVertexArray();
}
