/**
 * The opaque half of the page: the shoot column, the frame column and the filmstrip. All of it
 * is content on the tonal ground, printed rather than floated, because a tally, a histogram and
 * a strip of thirty frames are things to read, not controls (materialist skill, the decision
 * function's first question). The prose that explains the floating controls lives here, beside
 * them, and never on the glass.
 */
import { useEffect, useRef, type CSSProperties } from "react";

import { PHOTOGRAPHS, SHOOT, type Frame } from "./data";
import { HISTOGRAM_BINS, cropRect, hasCrop, paintThumb, type Histogram } from "./develop";
import { PickIcon, RejectIcon, StarIcon } from "./icons";

export function ShootColumn({ frames, style, reduceTransparency, onReduceTransparency }: {
  frames: readonly Frame[];
  style: CSSProperties;
  reduceTransparency: boolean;
  onReduceTransparency: (on: boolean) => void;
}) {
  const picks = frames.filter((f) => f.flag === "pick").length;
  const rejects = frames.filter((f) => f.flag === "reject").length;
  const rated = frames.filter((f) => f.rating > 0).length;
  const bursts = PHOTOGRAPHS.length;
  const open = PHOTOGRAPHS.filter((_, s) => !frames.slice(s * 3, s * 3 + 3).some((f) => f.flag === "pick")).length;
  return (
    <aside className="col col-lead" style={style} aria-label="Shoot">
      <header className="shoot">
        <h1>{SHOOT.title}</h1>
        <p>{SHOOT.brief}</p>
        <p className="quiet">{SHOOT.date} &middot; {frames.length} frames</p>
      </header>
      <section aria-labelledby="cull-h">
        <h2 id="cull-h">Cull</h2>
        <dl className="tally">
          <div><dt>Picks</dt><dd>{picks}</dd></div>
          <div><dt>Rejects</dt><dd>{rejects}</dd></div>
          <div><dt>Unflagged</dt><dd>{frames.length - picks - rejects}</dd></div>
          <div><dt>Rated</dt><dd>{rated}</dd></div>
        </dl>
        <p className="quiet">{open === 0 ? "Every burst has a pick." : `${open} of ${bursts} bursts still without a pick.`}</p>
      </section>
      <section aria-labelledby="keys-h">
        <h2 id="keys-h">Keys</h2>
        <dl className="keys">
          <div><dt><kbd>{"\u2190"}</kbd><kbd>{"\u2192"}</kbd></dt><dd>Previous, next</dd></div>
          <div><dt><kbd>P</kbd></dt><dd>Pick</dd></div>
          <div><dt><kbd>X</kbd></dt><dd>Reject</dd></div>
          <div><dt><kbd>U</kbd></dt><dd>Unflag</dd></div>
          <div><dt><kbd>1</kbd>{"\u2013"}<kbd>5</kbd></dt><dd>Rate, <kbd>0</kbd> clears</dd></div>
          <div><dt><kbd>\</kbd></dt><dd>Before, after</dd></div>
          <div><dt><kbd>E</kbd></dt><dd>Exposure</dd></div>
          <div><dt><kbd>W</kbd></dt><dd>White balance</dd></div>
          <div><dt><kbd>R</kbd></dt><dd>Crop</dd></div>
          <div><dt><kbd>Esc</kbd></dt><dd>Close the tool</dd></div>
        </dl>
      </section>
      <section aria-labelledby="display-h">
        <h2 id="display-h">Display</h2>
        <button type="button" role="switch" className="switch" aria-checked={reduceTransparency}
          onClick={() => onReduceTransparency(!reduceTransparency)}>
          <span className="switch-track" aria-hidden="true"><span className="switch-knob" /></span>
          Reduce transparency
        </button>
      </section>
    </aside>
  );
}

export function FrameColumn({ frame, frames, histogram, style }: {
  frame: Frame;
  frames: readonly Frame[];
  histogram: Histogram | null;
  style: CSSProperties;
}) {
  const d = frame.develop;
  const crop = hasCrop(d) ? cropRect(d) : null;
  const pct = (v: number) => (v < 0.001 ? "0" : v < 0.01 ? (v * 100).toFixed(2) : (v * 100).toFixed(1));
  return (
    <aside className="col col-trail" style={style} aria-label="Frame details">
      <section aria-labelledby="hist-h">
        <h2 id="hist-h">Histogram</h2>
        <HistogramPlot histogram={histogram} />
        {histogram !== null && (
          <p className="quiet small">Clipped {pct(histogram.clippedHigh)} % highlights, {pct(histogram.clippedLow)} % shadows</p>
        )}
      </section>
      <section aria-labelledby="frame-h">
        <h2 id="frame-h">Frame {frame.index + 1} of {frames.length}</h2>
        <p className="mono">{frame.file}</p>
        <p className="mono quiet">{frame.time}</p>
        <p className="mono quiet">{frame.shutter} s &middot; {frame.photo.aperture}<br />ISO {frame.photo.iso} &middot; {frame.photo.focal} mm</p>
      </section>
      <section aria-labelledby="adj-h">
        <h2 id="adj-h">Adjustments</h2>
        <dl className="adjust">
          <div><dt>Exposure</dt><dd className="mono">{d.ev === 0 ? "0.00" : `${d.ev > 0 ? "+" : "−"}${Math.abs(d.ev).toFixed(2)}`} EV</dd></div>
          <div><dt>Temperature</dt><dd className="mono">{d.temp} K</dd></div>
          <div><dt>Tint</dt><dd className="mono">{d.tint > 0 ? "+" : d.tint < 0 ? "−" : ""}{Math.abs(d.tint)}</dd></div>
          <div><dt>Crop</dt><dd className="mono">{crop === null ? "none" : `${d.aspect === "original" ? "3:2" : d.aspect}, ${Math.round(d.scale * 100)} %`}</dd></div>
          <div><dt>Straighten</dt><dd className="mono">{d.angle === 0 ? "0.0" : `${d.angle > 0 ? "+" : "−"}${Math.abs(d.angle).toFixed(1)}`}{"°"}</dd></div>
        </dl>
      </section>
      <section aria-labelledby="credit-h" className="credits">
        <h2 id="credit-h">Photographs</h2>
        <ul>
          {PHOTOGRAPHS.map((p) => (
            <li key={p.id} aria-current={p.id === frame.photo.id ? "true" : undefined}>
              <a href={p.profile} target="_blank" rel="noreferrer">{p.photographer}</a>
            </li>
          ))}
        </ul>
        <p className="quiet small">On Unsplash. Thirty exposures from ten photographs: the bursts, filenames and exposure data are this demo&rsquo;s.</p>
      </section>
    </aside>
  );
}

/** The luminance histogram, achromatic like the rest of the chrome: hue here would sit beside the frame. */
function HistogramPlot({ histogram }: { histogram: Histogram | null }) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const canvas = ref.current;
    const ctx = canvas?.getContext("2d");
    if (canvas === null || canvas === undefined || ctx === null || ctx === undefined) return;
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    const styles = getComputedStyle(canvas);
    ctx.fillStyle = styles.getPropertyValue("--hist-well").trim() || "rgba(0,0,0,0.06)";
    ctx.fillRect(0, 0, w, h);
    if (histogram === null) return;
    const bins = histogram.luma;
    // The tallest bin is usually the shadows' spike on a low-key frame; the second-tallest
    // scales the plot so the mid-tones stay readable, as raw converters do.
    const sorted = [...bins].sort((a, b) => b - a);
    const peak = Math.max(1, sorted[1] ?? sorted[0] ?? 1);
    ctx.beginPath();
    ctx.moveTo(0, h);
    for (let i = 0; i < HISTOGRAM_BINS; i += 1) {
      const x = (i / (HISTOGRAM_BINS - 1)) * w;
      const y = h - Math.min(1, (bins[i] ?? 0) / peak) * (h - 2);
      ctx.lineTo(x, y);
    }
    ctx.lineTo(w, h);
    ctx.closePath();
    ctx.fillStyle = styles.getPropertyValue("--hist-fill").trim() || "rgba(0,0,0,0.55)";
    ctx.fill();
  }, [histogram]);
  return <canvas ref={ref} className="histogram" role="img" aria-label="Luminance histogram of the developed frame" />;
}

export function Filmstrip({ frames, current, onSelect, thumbs, ground }: {
  frames: readonly Frame[];
  current: number;
  onSelect: (index: number) => void;
  thumbs: ReadonlyMap<string, HTMLImageElement>;
  ground: string;
}) {
  const canvases = useRef(new Map<number, HTMLCanvasElement>());
  const work = useRef<HTMLCanvasElement | null>(null);
  const painted = useRef(new Map<number, string>());
  const items = useRef(new Map<number, HTMLLIElement>());

  useEffect(() => {
    work.current ??= document.createElement("canvas");
    for (const frame of frames) {
      const canvas = canvases.current.get(frame.index);
      const image = thumbs.get(frame.photo.id);
      if (canvas === undefined || image === undefined) continue;
      const key = `${JSON.stringify(frame.develop)}|${ground}`;
      if (painted.current.get(frame.index) === key) continue;
      painted.current.set(frame.index, key);
      paintThumb(canvas, work.current, image, frame, ground);
    }
  }, [frames, thumbs, ground]);

  useEffect(() => {
    items.current.get(current)?.scrollIntoView({ block: "nearest", inline: "center" });
  }, [current]);

  return (
    <nav className="band" aria-label="Filmstrip">
      <ol className="strip">
        {frames.map((frame) => {
          const selected = frame.index === current;
          const flag = frame.flag === "pick" ? "picked" : frame.flag === "reject" ? "rejected" : "unflagged";
          return (
            <li key={frame.index}
              className={frame.index % 3 === 0 && frame.index > 0 ? "burst-start" : undefined}
              ref={(el) => { if (el === null) items.current.delete(frame.index); else items.current.set(frame.index, el); }}>
              <button type="button" className="thumb" aria-current={selected ? "true" : undefined}
                data-flag={frame.flag ?? "none"}
                aria-label={`Frame ${frame.index + 1}, ${frame.file}, ${flag}, ${frame.rating === 0 ? "unrated" : `${frame.rating} star${frame.rating > 1 ? "s" : ""}`}`}
                onClick={() => onSelect(frame.index)}>
                <canvas width={192} height={128}
                  ref={(el) => { if (el === null) canvases.current.delete(frame.index); else canvases.current.set(frame.index, el); }} />
                <span className="thumb-meta" aria-hidden="true">
                  <span className="mono">{frame.index + 1}</span>
                  {frame.flag === "pick" && <PickIcon on />}
                  {frame.flag === "reject" && <RejectIcon on />}
                  {frame.rating > 0 && (
                    <span className="mini-stars">
                      {Array.from({ length: frame.rating }, (_, i) => <StarIcon key={i} on size={10} />)}
                    </span>
                  )}
                </span>
              </button>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
