// WGSL ports of the two candidate pseudo-SDF families that survived the error
// sweep, plus a null baseline for subtracting fixed pass overhead.
//
// Both are branchless in the corner algebra. The only guard is a clamp on the
// squared corner radius, which keeps the deep-interior case (rho == 0) from
// producing NaN without costing a branch.
//
// Instance data layout (see bench/run.ts): centre.xy, half.xy, re, k0..k4.

struct Shape {
  centre : vec2f,
  half   : vec2f,
  re     : f32,
  k0     : f32,
  k1     : f32,
  k2     : f32,
  k3     : f32,
  k4     : f32,
  _pad   : f32,
};

// ---------------------------------------------------------------------------
// Family A: analytic rounded box, radius reparameterized. The cheapest possible
// baseline and the thing every WebGL glass demo already ships.
// ---------------------------------------------------------------------------
fn sd_roundbox(p : vec2f, half : vec2f, re : f32) -> f32 {
  let q = abs(p) - half + vec2f(re, re);
  return length(max(q, vec2f(0.0, 0.0))) + min(max(q.x, q.y), 0.0) - re;
}

// ---------------------------------------------------------------------------
// Family D: radial-support field with a degree-5 corner correction in
// s2 = sin(2*theta), plus the first-order |grad| normalization.
//
// No transcendentals: s2 and cos(2*theta) both come out of the clamped corner
// vector by division. Cost over family A is one extra divide, one rsqrt, and
// about a dozen fused multiply-adds.
// ---------------------------------------------------------------------------
fn sd_rsupn(p : vec2f, half : vec2f, re : f32, k : vec4f, k4 : f32) -> f32 {
  let q  = abs(p) - half + vec2f(re, re);
  let c  = max(q, vec2f(0.0, 0.0));
  let r2 = max(dot(c, c), 1e-20);
  let inv = 1.0 / r2;
  let s2 = 2.0 * c.x * c.y * inv;             // sin(2*theta)
  let c2 = (c.x * c.x - c.y * c.y) * inv;     // cos(2*theta)

  // R(theta) = re * (1 + s2^2 * poly(s2)), Horner
  var acc = k4;
  acc = acc * s2 + k.w;
  acc = acc * s2 + k.z;
  acc = acc * s2 + k.y;
  acc = acc * s2 + k.x;
  let R = re * (1.0 + s2 * s2 * acc);

  // dR/d(s2) * d(s2)/dtheta, same Horner shape with the differentiated weights
  var dac = 6.0 * k4;
  dac = dac * s2 + 5.0 * k.w;
  dac = dac * s2 + 4.0 * k.z;
  dac = dac * s2 + 3.0 * k.y;
  dac = dac * s2 + 2.0 * k.x;
  let dRdt = re * s2 * dac * (2.0 * c2);

  let base = sqrt(r2) + min(max(q.x, q.y), 0.0) - R;
  let g = dRdt * inv * sqrt(r2);              // == dRdt / rho
  return base * inverseSqrt(1.0 + g * g);
}

// ---------------------------------------------------------------------------
// Family B: superellipse exponent, |grad|-normalized. Carried only to price the
// pow() calls against the transcendental-free families.
// ---------------------------------------------------------------------------
fn sd_superell(p : vec2f, half : vec2f, re : f32, n : f32) -> f32 {
  let q = abs(p) - half + vec2f(re, re);
  let c = max(q, vec2f(0.0, 0.0));
  let rho = length(c);
  if (c.x <= 0.0 || c.y <= 0.0) {
    return rho + min(max(q.x, q.y), 0.0) - re;
  }
  let g = pow(pow(c.x, n) + pow(c.y, n), 1.0 / n);
  let gx = pow(c.x / g, n - 1.0);
  let gy = pow(c.y / g, n - 1.0);
  return (g - re) / length(vec2f(gx, gy));
}

// ---------------------------------------------------------------------------
// Family C: family D minus the |grad| normalization. The two share a zero level
// set, and so one coefficient fit; the gap between them is exactly the price of
// the normalization -- one divide, one rsqrt and the differentiated Horner
// chain -- which is what carrying this variant in the benchmark buys.
// ---------------------------------------------------------------------------
fn sd_rsup(p : vec2f, half : vec2f, re : f32, k : vec4f, k4 : f32) -> f32 {
  let q  = abs(p) - half + vec2f(re, re);
  let c  = max(q, vec2f(0.0, 0.0));
  let r2 = max(dot(c, c), 1e-20);
  let s2 = 2.0 * c.x * c.y / r2;
  var acc = k4;
  acc = acc * s2 + k.w;
  acc = acc * s2 + k.z;
  acc = acc * s2 + k.y;
  acc = acc * s2 + k.x;
  let R = re * (1.0 + s2 * s2 * acc);
  return sqrt(r2) + min(max(q.x, q.y), 0.0) - R;
}
