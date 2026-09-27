import { readFileSync } from "node:fs";
const R = JSON.parse(readFileSync("/tmp/sp-clear/recapture.json", "utf8"));
const F = JSON.parse(readFileSync("/tmp/sp-clear/final.json", "utf8"));
for (const m of R.matrix) {
  const f = F.matrix.find((x) => x.glass === "clear" && x.tier === m.tier && x.scheme === m.scheme && x.phase === m.phase && x.state === m.state);
  const same = f.fp.canvas === m.fp.canvas;
  const rects = Object.entries(m.fp.groups).map(([k, g]) => `${k}:${g.rect.join("x")}${JSON.stringify(g.rect) === JSON.stringify(f.fp.groups[k].rect) ? "" : "(was " + f.fp.groups[k].rect.join("x") + ")"}`).join(" ");
  const hints = Object.entries(m.fp.groups).map(([k, g]) => `${k}:${g.backdrop?.luminance}${g.backdrop?.luminance === f.fp.groups[k].backdrop?.luminance ? "" : "(was " + f.fp.groups[k].backdrop?.luminance + ")"}`).join(" ");
  if (!same) console.log(`${m.tier}/${m.scheme}/${m.phase}/${m.state} canvas DIFF size ${m.fp.canvasSize} vs ${f.fp.canvasSize}\n   rects ${rects}\n   hints ${hints}`);
}
console.log("done");
