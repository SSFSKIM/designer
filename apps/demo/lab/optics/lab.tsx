/**
 * The optics bench the chronograph's material was tuned on (docs/doperpowers/specs/
 * 2026-09-29-chronograph-flagship.md, Decision Log 2 and 3). Served by the dev server at
 * `/lab/optics/`, never built. One canvas of grid, dial, colour bars and text under circles from
 * span 44 to 500, a capsule, a rounded rectangle and a loupe-sized circle; the query string picks
 * the material:
 *
 *   tune=calibrated | optical | dome, scheme=light|dark
 *   bt, st, lt        thickness of the big circle, the small shapes, the loupe circle
 *   blur, ta, tone    the optical body's blur, tint alpha and tone response strength
 *   p, ext, hmax, amax, gain   the dome's lens leaves
 *   sweep, rimw       hold the sweep channel at a phase with full shimmer; widen the rim
 *
 * The captures under docs/research/data/2026-09-29-chronograph/lab/ are this page.
 */

import {
  GlassGroup,
  GlassRoot,
  GlassSurface,
  useGlassRoot,
  useGlassCapabilities,
} from "@vitreajs/vitrea-react";
import type { RendererMaterialProfile } from "@vitreajs/vitrea-web";
import { useEffect, useRef, type ReactNode } from "react";
import { createRoot } from "react-dom/client";

const q = new URLSearchParams(location.search);
const tune = q.get("tune") ?? "calibrated";
const scheme = (q.get("scheme") ?? "light") as "light" | "dark";
const bigT = Number(q.get("bt") ?? "8");
const smallT = Number(q.get("st") ?? "8");
const loupeT = Number(q.get("lt") ?? "24");
const num = (k: string, d: number): number => (q.has(k) ? Number(q.get(k)) : d);

const OPTICAL: RendererMaterialProfile = {
  optics: { regular: { blurSigma: num("blur", 0.3), tintAlpha: num("ta", 0.05), ...(q.has("rimw") ? { rimWidth: num("rimw", 6.5) } : {}) } },
  sizeOcclusionGain: 0,
  sizeScatterGainMax: 1,
  sizeScatterGainMax2x: 1,
  sizeScatterGainFar2x: 1,
  sizeHeavyTapSigma: 0,
  sizeHeavyTapSigma2x: 0,
  backdropToneResponseStrength: num("tone", 0),
  bodyChromaRetention: 1,
};
const DOME: RendererMaterialProfile = {
  ...OPTICAL,
  lensProfileExponent: num("p", 3.69),
  lensExtentGain: num("ext", 1.337),
  lensHeightMax: num("hmax", 250),
  lensAmountMax: num("amax", 60),
  lensRefractionGain: num("gain", 0.745),
};
const PROFILES: Record<string, RendererMaterialProfile | undefined> = {
  calibrated: undefined,
  optical: OPTICAL,
  dome: DOME,
};

const W = window.innerWidth;
const H = window.innerHeight;

function paint(canvas: HTMLCanvasElement): void {
  const dpr = window.devicePixelRatio;
  canvas.width = Math.round(W * dpr);
  canvas.height = Math.round(H * dpr);
  const c = canvas.getContext("2d")!;
  c.scale(dpr, dpr);
  const dark = scheme === "dark";
  c.fillStyle = dark ? "#0d1f1a" : "#2f6b57";
  c.fillRect(0, 0, W, H);
  // cutting-mat grid
  for (let x = 0; x < W; x += 10) {
    c.strokeStyle = x % 50 === 0 ? "rgb(255 255 255 / 45%)" : "rgb(255 255 255 / 16%)";
    c.lineWidth = x % 50 === 0 ? 1 : 0.6;
    c.beginPath(); c.moveTo(x + 0.5, 0); c.lineTo(x + 0.5, H); c.stroke();
  }
  for (let y = 0; y < H; y += 10) {
    c.strokeStyle = y % 50 === 0 ? "rgb(255 255 255 / 45%)" : "rgb(255 255 255 / 16%)";
    c.lineWidth = y % 50 === 0 ? 1 : 0.6;
    c.beginPath(); c.moveTo(0, y + 0.5); c.lineTo(W, y + 0.5); c.stroke();
  }
  // dial
  const cx = 420, cy = H / 2, R = 280;
  const g = c.createRadialGradient(cx, cy, 0, cx, cy, R);
  g.addColorStop(0, dark ? "#16233a" : "#e9edf2");
  g.addColorStop(1, dark ? "#0a1222" : "#c9d1db");
  c.fillStyle = g; c.beginPath(); c.arc(cx, cy, R, 0, Math.PI * 2); c.fill();
  // sunburst
  for (let i = 0; i < 720; i++) {
    const a = (i / 720) * Math.PI * 2;
    const k = Math.pow(Math.abs(Math.cos(a - 0.8)), 6);
    c.strokeStyle = `rgb(255 255 255 / ${0.02 + 0.1 * k})`;
    c.lineWidth = 0.5;
    c.beginPath(); c.moveTo(cx, cy); c.lineTo(cx + Math.cos(a) * R, cy + Math.sin(a) * R); c.stroke();
  }
  const ink = dark ? "#e8eef7" : "#111418";
  for (let i = 0; i < 300; i++) {
    const a = (i / 300) * Math.PI * 2;
    const major = i % 25 === 0, mid = i % 5 === 0;
    const r0 = R - (major ? 26 : mid ? 16 : 9), r1 = R - 4;
    c.strokeStyle = ink; c.lineWidth = major ? 2.5 : mid ? 1.4 : 0.7;
    c.beginPath(); c.moveTo(cx + Math.cos(a) * r0, cy + Math.sin(a) * r0);
    c.lineTo(cx + Math.cos(a) * r1, cy + Math.sin(a) * r1); c.stroke();
  }
  c.fillStyle = ink; c.font = "600 26px 'Avenir Next', system-ui"; c.textAlign = "center"; c.textBaseline = "middle";
  for (let h = 1; h <= 12; h++) {
    const a = (h / 12) * Math.PI * 2 - Math.PI / 2;
    c.fillText(String(h * 5).padStart(2, "0"), cx + Math.cos(a) * (R - 54), cy + Math.sin(a) * (R - 54));
  }
  c.font = "500 15px 'Avenir Next', system-ui";
  c.fillText("CHRONOGRAPH · AUTOMATIC", cx, cy - 70);
  c.fillStyle = "#c8102e"; c.fillRect(cx - 2, cy - R + 30, 4, R - 30);
  c.fillStyle = ink; c.fillRect(cx - 5, cy - 5, 150, 10);
  // colour stripes + text on right
  const cols = ["#ff3b30", "#ff9500", "#ffcc00", "#34c759", "#00c7be", "#007aff", "#5856d6", "#ff2d55"];
  cols.forEach((col, i) => { c.fillStyle = col; c.fillRect(760 + i * 40, 80, 40, 220); });
  c.fillStyle = "#fff"; c.font = "700 64px 'Avenir Next', system-ui"; c.textAlign = "left";
  c.fillText("Sapphire 0.5 mm", 760, 380);
  c.font = "400 18px Georgia, serif";
  for (let i = 0; i < 14; i++) c.fillText("The quick brown fox jumps over the lazy dog 0123456789", 760, 440 + i * 26);
}

function Env(): ReactNode {
  const root = useGlassRoot();
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    if (ref.current === null || root === null) return;
    paint(ref.current);
    root.setBackdropTexture("env", { kind: "canvas", canvas: ref.current });
  }, [root]);
  return <canvas ref={ref} className="env" aria-hidden="true" />;
}

const BD = { kind: "texture", id: "env" } as const;

function Readout(): ReactNode {
  const cap = useGlassCapabilities("big");
  const root = useGlassRoot();
  useEffect(() => {
    if (root === null || !q.has("sweep")) return;
    return root.subscribe(() => {
      for (const el of document.querySelectorAll<HTMLElement>(".g")) {
        el.style.setProperty("--vitrea-sweep", q.get("sweep") ?? "0.375");
        el.style.setProperty("--vitrea-shimmer", "1");
      }
    });
  }, [root]);
  useEffect(() => {
    const el = document.getElementById("readout")!;
    el.textContent = `${location.search}\n` +
      `renderer=${cap?.activeRenderer} refraction=${cap?.refraction} tuned=${cap?.materialDocument?.tuned}`;
    (window as unknown as { __lab: unknown }).__lab = cap;
  }, [cap]);
  return null;
}

function Box(p: { x: number; y: number; w: number; h: number; r?: number; capsule?: boolean; t: number; label?: string }): ReactNode {
  return (
    <GlassSurface asChild radius={p.r ?? 12} capsule={p.capsule ?? false} thickness={p.t}>
      <div className="g" style={{ left: p.x, top: p.y, width: p.w, height: p.h }}>{p.label}</div>
    </GlassSurface>
  );
}

function Lab(): ReactNode {
  return (
    <>
      <Env />
      <Readout />
      <GlassGroup id="big" backdrop={BD}>
        <Box x={420 - 250} y={H / 2 - 250} w={500} h={500} capsule t={bigT} />
      </GlassGroup>
      <GlassGroup id="small" backdrop={BD}>
        <Box x={770} y={130} w={44} h={44} capsule t={smallT} />
        <Box x={840} y={120} w={64} h={64} capsule t={smallT} />
        <Box x={930} y={100} w={96} h={96} capsule t={smallT} />
        <Box x={1060} y={90} w={140} h={140} capsule t={smallT} />
      </GlassGroup>
      <GlassGroup id="loupe" backdrop={BD}>
        <Box x={900} y={640} w={170} h={170} capsule t={loupeT} />
      </GlassGroup>
      <GlassGroup id="text" backdrop={BD}>
        <Box x={760} y={330} w={260} h={64} capsule t={smallT} />
        <Box x={1060} y={420} w={320} h={200} r={36} t={smallT} />
        <Box x={760} y={560} w={240} h={56} capsule t={smallT} label="Start" />
      </GlassGroup>
    </>
  );
}

createRoot(document.getElementById("root")!).render(
  <GlassRoot renderer="webgpu" colorScheme={scheme} windowActivation="active" materialProfile={PROFILES[tune]}>
    <Lab />
  </GlassRoot>,
);
