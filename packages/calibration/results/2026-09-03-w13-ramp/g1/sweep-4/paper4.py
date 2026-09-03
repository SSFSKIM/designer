"""The fourth form's closed-form projection on the real spans, per far value. No GPU.
Mirrors material.ts: sDeep, s0 (thin/thick/far), the excursion, and the area mean over the
cell's own box (the CSS tier's number and the proxy's)."""
import sys
FLOOR, SPAN_MIN, SPAN_MAX, SCATTER_MAX = 0.4, 32, 96, 256
THIN, THICK, REACH = 0.72, 0.52, 80
CELLS = [("rrect-sm", 64, 32), ("capsule-button", 120, 44), ("toolbar-group", 44, 44),
         ("rrect-md", 160, 96), ("rrect-ml", 224, 128), ("glass-over-glass", 220, 130), ("rrect-lg", 280, 160)]
def ss(a, b, x):
    t = min(1, max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t)
def s_deep(span): return 1 - (FLOOR + (1 - FLOOR) * ss(SPAN_MIN, SCATTER_MAX, span))
def s0(span, far): return THIN + (THICK - THIN) * ss(SPAN_MIN, SPAN_MAX, span) + (far - THICK) * ss(SPAN_MAX, SCATTER_MAX, span)
def area_mean_k(w, h, span, far):
    deep = 1 - s_deep(span); amp = max(s0(span, far) - s_deep(span), 0)
    if amp <= 0: return deep
    # triangle of height amp over depth 0..R on a rectangle: measure P - 8u at depth u
    R = REACH; P = 2 * (w + h); umax = min(R, min(w, h) / 2)
    # integral of amp*(1-u/R)*(P-8u) du / (w*h)
    I = amp * (P * umax - P * umax**2 / (2 * R) - 4 * umax**2 + 8 * umax**3 / (3 * R))
    return deep - I / (w * h)
G0 = {"rrect-sm": 0.637, "capsule-button": 0.642, "rrect-md": 0.512, "rrect-ml": 0.501, "rrect-lg": 0.410}
fars = [float(x) for x in sys.argv[1:]] or [0.30, 0.35, 0.40, 0.45, 0.52]
print("cell               span  sDeep   G0 s0 | " + " | ".join(f"far={f:.2f}: s0  exc  kbar" for f in fars))
for name, w, h, span in [(c[0], c[1], c[2], min(c[1], c[2])) for c in CELLS]:
    row = f"{name:<18}{span:>5}  {s_deep(span):.3f}  {G0.get(name, float('nan')):.3f} | "
    row += " | ".join(f"{s0(span,f):.3f} {max(s0(span,f)-s_deep(span),0):.3f} {area_mean_k(w,h,span,f):.3f}" for f in fars)
    print(row)
print("\nthird form (far == thick 0.52) is the last column; the reference's implied excursion at 1x:",
      {k: round(v - s_deep(s), 3) for (k, w, h), s, v in [((c[0], c[1], c[2]), min(c[1], c[2]), G0.get(c[0])) for c in CELLS] if v})
