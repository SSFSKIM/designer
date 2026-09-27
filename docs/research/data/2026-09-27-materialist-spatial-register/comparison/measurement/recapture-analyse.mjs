// Summaries from recapture.json: the clear rows of the record's table, each cell against the
// first run (canvas, pixels, lifts), and the comparison captures' runtime readings. No browser.
import { readFileSync } from "node:fs";
const R = JSON.parse(readFileSync("/tmp/sp-clear/recapture.json", "utf8"));
const F = JSON.parse(readFileSync("/tmp/sp-clear/final.json", "utf8"));
const pct = (xs, q) => { const s = [...xs].sort((a, b) => a - b); return s[Math.round(q * (s.length - 1))]; };
const w = (xs) => xs.reduce((a, b) => (!a || b.worst < a.worst ? b : a), null);
const fmt = (l) => l ? `${l.worst.toFixed(2)} "${l.text}" [${l.host}, ${l.phase} ${l.state}]` : "-";
for (const tier of ["webgpu", "css"]) for (const scheme of ["light", "dark"]) {
  const rows = R.matrix.filter((m) => m.tier === tier && m.scheme === scheme);
  const all = rows.flatMap((m) => m.lines.map((l) => ({ ...l, phase: m.phase, state: m.state })));
  const gated = all.filter((l) => l.lineState === "visible");
  const text = gated.filter((l) => l.kind === "text" && l.floor === 4.5), large = gated.filter((l) => l.kind === "text" && l.floor === 3), icon = gated.filter((l) => l.kind === "icon");
  console.log(`clear ${tier} ${scheme}: gated ${gated.length} (text ${text.length}, large ${large.length}, marks ${icon.length}), failing ${gated.filter((l) => !l.pass).length}; worst text ${fmt(w(text))}; large ${fmt(w(large))}; marks ${fmt(w(icon))}; median text ${pct(text.map((l) => l.worst), 0.5)?.toFixed(2)}; platter worst ${fmt(w(gated.filter((l) => l.state === "platter")))}`);
  for (const l of gated.filter((l) => !l.pass)) console.log(`   FAIL ${l.phase}/${l.state} ${l.worst}<${l.floor} "${l.text}" [${l.host}/${l.cls}] surf ${l.surface} ink ${l.color}`);
  // Lifted-fill lines: the ones the revert touched (Places tiles, the current event, pressed rows).
  const first = F.matrix.filter((m) => m.glass === "clear" && m.tier === tier && m.scheme === scheme).flatMap((m) => m.lines.map((l) => ({ ...l, phase: m.phase, state: m.state })));
  const key = (l) => `${l.phase}/${l.state}/${l.host}/${l.cls}/${l.text}`;
  const firstBy = new Map(first.map((l) => [key(l), l]));
  const moved = gated.map((l) => ({ l, f: firstBy.get(key(l)) })).filter((x) => x.f && Math.abs(x.f.surface - x.l.surface) > 0.01);
  const surf = moved.map((x) => x.l.surface - x.f.surface);
  console.log(`   lines whose surface moved > 0.01 vs run 1: ${moved.length} of ${gated.length}; surface delta ${surf.length ? `${Math.min(...surf).toFixed(3)}..${Math.max(...surf).toFixed(3)}` : "-"}; their worst ratio run1 ${moved.length ? Math.min(...moved.map((x) => x.f.worst)).toFixed(2) : "-"} -> run2 ${moved.length ? Math.min(...moved.map((x) => x.l.worst)).toFixed(2) : "-"}; hosts ${[...new Set(moved.map((x) => x.l.host))].join(", ") || "-"}`);
  console.log(`   canvas same as run 1: ${rows.filter((m) => m.first?.canvas === m.fp.canvas).length}/${rows.length}; pixels same: ${rows.filter((m) => m.first?.pixels === m.pixels).length}/${rows.length}; lifts ${[...new Set(rows.map((m) => m.lifts.join(" ")))].join(" | ")}; diags ${rows.flatMap((m) => m.fp.diags.map((d) => d.code)).join(",") || "none"}`);
  const deltas = rows.flatMap((m) => Object.values(m.fp.groups).map((g) => Math.abs(g.hintDelta ?? 99)));
  console.log(`   hint vs painted canvas: max |delta| ${Math.max(...deltas)}`);
}
for (const c of R.comparisons) console.log("comparison", c.name, c.glass, "drew", Object.values(c.fp.groups).map((g) => `${g.caps?.activeRenderer}/${g.caps?.samplingBackend}`).join(","), "diags", c.fp.diags.map((d) => d.code).join(",") || "none", "inks", Object.entries(c.fp.inks).map(([k, v]) => `${k}=${v}`).join(" "), "materials", [...new Set(Object.values(c.fp.groups).map((g) => JSON.stringify(g.material)))].join(" "), "hints", Object.entries(c.fp.groups).map(([k, g]) => `${k} ${g.backdrop?.luminance}`).join(" · "));
console.log("errors", R.errors.length, R.errors.slice(0, 10).join("\n"));
