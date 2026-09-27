// Summaries for the record from final.json (and the sweep), plus the default-state comparison
// against the pre-change baselines. No browser.
import { readFileSync } from "node:fs";
const F = JSON.parse(readFileSync("/tmp/sp-clear/final.json", "utf8"));
const S = JSON.parse(readFileSync("/tmp/sp-clear/sweep.json", "utf8"));
const A = JSON.parse(readFileSync("/tmp/sp-clear/baseline-a.json", "utf8"));
const B = JSON.parse(readFileSync("/tmp/sp-clear/baseline-b.json", "utf8"));
console.log("chosen", JSON.stringify(F.chosen));
for (const st of S.steps) console.log(`sweep ${st.scheme} ${st.strength} gated ${st.gated} failing ${st.failing} worst ${st.worst?.ratio}/${st.worst?.floor} "${st.worst?.text}" [${st.worst?.host} ${st.worst?.phase} ${st.worst?.state}] diags ${st.diags.join(",") || "none"}`);
const pct = (xs, q) => { const s = [...xs].sort((a, b) => a - b); return s[Math.round(q * (s.length - 1))]; };
for (const glass of ["regular", "clear"]) {
  console.log(`\n== ${glass} ==`);
  for (const tier of ["webgpu", "css"]) for (const scheme of ["light", "dark"]) {
    const rows = F.matrix.filter((m) => m.glass === glass && m.tier === tier && m.scheme === scheme);
    const all = rows.flatMap((m) => m.lines.map((l) => ({ ...l, phase: m.phase, state: m.state })));
    const gated = all.filter((l) => l.lineState === "visible");
    const text = gated.filter((l) => l.kind === "text" && l.floor === 4.5), large = gated.filter((l) => l.kind === "text" && l.floor === 3), icon = gated.filter((l) => l.kind === "icon");
    const w = (xs) => xs.reduce((a, b) => (!a || b.worst < a.worst ? b : a), null);
    const fmt = (l) => l ? `${l.worst.toFixed(2)} "${l.text}" [${l.host}, ${l.phase} ${l.state}]` : "-";
    console.log(`${tier} ${scheme}: readings ${all.length}, gated ${gated.length} (text ${text.length}, large ${large.length}, marks ${icon.length}), failing ${gated.filter((l) => !l.pass).length}; worst text ${fmt(w(text))}; large ${fmt(w(large))}; marks ${fmt(w(icon))}; median text ${pct(text.map((l) => l.worst), 0.5)?.toFixed(2)}; excluded scroll-edge ${all.length - gated.length}`);
    for (const l of gated.filter((l) => !l.pass)) console.log(`   FAIL ${l.phase}/${l.state} ${l.worst}<${l.floor} med ${l.median} "${l.text}" [${l.host}/${l.cls}] surf ${l.surface} ${JSON.stringify(l.surfaceRange)} ink ${l.color}`);
    // Platter lines only, and the new switch's label.
    const plat = gated.filter((l) => l.state === "platter");
    const sw = gated.filter((l) => /Clear glass/.test(l.text) || /knob on Clear/.test(l.text));
    console.log(`   platter gated ${plat.length}, worst ${fmt(w(plat))}; clear-switch label/knob worst ${fmt(w(sw))}`);
  }
  const fps = F.matrix.filter((m) => m.glass === glass);
  const diags = fps.flatMap((m) => m.fp.diags);
  console.log(`diagnostics over ${fps.length} states: ${diags.length} ${[...new Set(diags.map((d) => d.code))].join(",")}`);
  const deltas = fps.flatMap((m) => Object.entries(m.fp.groups).map(([id, g]) => ({ id, d: Math.abs(g.hintDelta ?? 99), k: `${m.tier}/${m.scheme}/${m.phase}/${m.state}` })));
  const dmax = deltas.reduce((a, b) => (b.d > a.d ? b : a));
  console.log(`hint vs painted canvas under each host: max |delta| ${dmax.d} (${dmax.id} ${dmax.k}); over 0.0015: ${deltas.filter((x) => x.d > 0.0015).length} of ${deltas.length}`);
  const vari = new Set(fps.flatMap((m) => (m.fp.nodes ?? []).map((n) => `${n.variant}/${n.adaptation}/${n.dimming ? n.dimming.scrim : "-"}/σ${n.blurSigma}/α${n.tintAlpha}`)));
  console.log(`resolved node materials: ${[...vari].join(" | ")}`);
  const pads = new Set(fps.flatMap((m) => (m.fp.groupInputs ?? []).map((g) => `${m.scheme}:${g.group}:${g.samplingPadding}`)));
  console.log(`group sampling paddings: ${[...pads].sort().join(" ")}`);
  const caps = new Set(fps.map((m) => `${m.tier}->` + Object.values(m.fp.groups).map((g) => `${g.caps?.activeRenderer}/${g.caps?.samplingBackend}/${g.caps?.cssBody ?? ""}`).join(",")));
  console.log(`drew: ${[...caps].join(" ; ")}`);
  const inks = new Set(fps.map((m) => `${m.tier}/${m.scheme}/${m.phase}/${m.state}: ` + Object.entries(m.fp.inks).map(([k, v]) => `${k}=${v}`).join(" ")));
  if (glass === "clear") for (const i of inks) console.log("  ink " + i);
  const hints = fps.filter((m) => m.tier === "webgpu" && m.state === "rest").map((m) => `${m.scheme}/${m.phase}: ` + Object.entries(m.fp.groups).map(([k, g]) => `${k} ${g.backdrop?.tone} ${g.backdrop?.luminance}`).join(" · "));
  for (const h of hints) console.log("  hint " + h);
}
console.log("\n== default state against the pre-change baselines ==");
for (const m of F.matrix.filter((m) => m.glass === "regular")) {
  const k = `${m.tier}/${m.scheme}/${m.phase}/${m.state}`; const a = A[k], b = B[k];
  const same = (x, y) => JSON.stringify(x) === JSON.stringify(y);
  const groupsNow = Object.fromEntries(Object.entries(m.fp.groups).map(([id, g]) => [id, { descriptor: { backdrop: g.backdrop, material: g.material ?? undefined }, caps: g.caps }]));
  const groupsA = Object.fromEntries(Object.entries(a.groups).map(([id, g]) => [id, { descriptor: { backdrop: g.descriptor.backdrop, material: g.descriptor.material }, caps: g.caps }]));
  const hostsNow = Object.values(m.fp.groups).map((g) => g.rect.join("x"));
  console.log(`${k.padEnd(28)} canvas ${m.fp.canvas === a.canvas ? "same" : "DIFF"} hints+material+caps ${same(groupsNow, groupsA) ? "same" : "DIFF"} pixels ${m.pixels === a.pixels || m.pixels === b.pixels ? "same" : "differ"} hosts ${hostsNow.join(",")}`);
}
console.log("\nrt platter", JSON.stringify(F.rtPlatter));
const T = F.toggle;
if (T) {
  console.log("toggle urls", T.before.url, T.on.url, T.off.url, "attr", T.on.glassAttr, T.off.glassAttr, "focus", JSON.stringify(T.focusOn));
  const clearPlatter = F.matrix.find((m) => m.glass === "clear" && m.tier === "webgpu" && m.scheme === "dark" && m.phase === "day" && m.state === "platter");
  const regPlatter = F.matrix.find((m) => m.glass === "regular" && m.tier === "webgpu" && m.scheme === "dark" && m.phase === "day" && m.state === "platter");
  console.log("toggled-on canvas == loaded ?glass=clear canvas:", T.on.canvas === clearPlatter.fp.canvas, "| toggled-off canvas == default canvas:", T.off.canvas === regPlatter.fp.canvas, T.before.canvas === T.off.canvas);
  console.log("materials on", JSON.stringify(Object.values(T.on.groups).map((g) => g.material)), "off", JSON.stringify(Object.values(T.off.groups).map((g) => g.material)));
  console.log("probe", JSON.stringify(T.pBefore), JSON.stringify(T.pOn), JSON.stringify(T.pOff));
  console.log("diags toggle", [T.before, T.on, T.off].flatMap((f) => f.diags.map((d) => d.code)).join(",") || "none");
}
if (F.trace) for (const [k, t] of Object.entries(F.trace)) { const d = t.map((f) => Math.abs(f[2] - f[3])); console.log(`trace ${k}: frames ${t.length}, sizes ${t[0]?.slice(0, 2)} -> ${t.at(-1)?.slice(0, 2)}, max |canvas-hint| ${Math.max(...d).toFixed(4)}, frames over 0.005: ${d.filter((x) => x > 0.005).length}`); }
for (const c of F.comparisons) console.log("comparison", c.name, c.glass, c.fp.diags.map((d) => d.code).join(",") || "no-diags", Object.entries(c.fp.inks).map(([k, v]) => `${k}=${v}`).join(" "));
console.log("errors", F.errors.length, F.errors.slice(0, 10).join("\n"));
