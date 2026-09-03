"""The third form on paper: which cells the excursion touches at each grid point,
and the per-surface projection the CSS tier renders. No GPU, no fixture."""
FLOOR = 0.4
SPAN_MIN, SPAN_MAX, SCATTER_SPAN_MAX = 32, 96, 256
BED = [("rrect-sm", 64, 32), ("capsule-button", 120, 44), ("toolbar-group", 44, 44),
       ("rrect-md", 160, 96), ("rrect-ml", 224, 128), ("glass-over-glass", 220, 130),
       ("rrect-lg", 280, 160)]


def smoothstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def thickness(span):
    return smoothstep(SPAN_MIN, SPAN_MAX, span)


def kdeep(span):
    return FLOOR + (1 - FLOOR) * smoothstep(SPAN_MIN, SCATTER_SPAN_MAX, span)


def start(span, thin, thick):
    return thin + (thick - thin) * thickness(span)


def area_mean(w, h, thin, thick, reach_device, dpr):
    deep = kdeep(min(w, h))
    amp = max(start(min(w, h), thin, thick) - (1 - deep), 0.0)
    if amp <= 0:
        return deep
    R = reach_device / dpr
    P, A = 2 * (w + h), w * h
    m = min(R, min(w, h) / 2)
    tbar = (P * m - 4 * m * m - (P * m * m) / (2 * R) + (8 * m ** 3) / (3 * R)) / A
    return deep - amp * tbar


def table(thin, thick, reach, dpr, label):
    print(f"\n**{label}** — s0(span) = {thin} + ({thick} - {thin})*sizeThickness(span), "
          f"reach {reach} device px, dpr {dpr}\n")
    print("| cell | span | sizeThickness | s0(span) | sDeep | excursion | moves? | area mean k |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for name, w, h in BED:
        span = min(w, h)
        s0, sd = start(span, thin, thick), 1 - kdeep(span)
        exc = s0 - sd
        print(f"| `{name}` | {span} | {thickness(span):.4f} | {s0:.4f} | {sd:.4f} | "
              f"{max(exc,0):.4f} ({exc:+.4f}) | {'YES' if exc>0 else 'no'} | "
              f"{area_mean(w,h,thin,thick,reach,dpr):.4f} |")


if __name__ == "__main__":
    table(0.64, 0.52, 120, 1, "the shipped 1x anchors")
    table(0.46, 0.17, 100, 2, "the shipped 2x anchors")
    print("\n### the 1x grid's corners, by whether each cell moves at all\n")
    print("| thin | thick | sm(0.600) | caps/tb(0.595) | md(0.481) | ml(0.364) | "
          "gog(0.356) | lg(0.236) |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for thin in (0.60, 0.64, 0.68):
        for thick in (0.50, 0.52, 0.56):
            cells = []
            for name, w, h in BED:
                if name == "toolbar-group":
                    continue
                span = min(w, h)
                cells.append("YES" if start(span, thin, thick) > 1 - kdeep(span) else "no")
            print(f"| {thin} | {thick} | " + " | ".join(cells) + " |")
