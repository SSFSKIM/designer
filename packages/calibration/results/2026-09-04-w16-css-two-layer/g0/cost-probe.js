(() => {
  // The demo pages do not animate on their own, so the probe moves the page every
  // frame: a `backdrop-filter` over content that has not moved is served from a
  // cached surface and would measure nothing. Scrolling is tried first because it
  // moves exactly what the glass is over; where the page does not scroll, an
  // injected moving strip behind the glass supplies the invalidation instead, and
  // which of the two ran is reported so the reading is never silently empty.
  const filtered = () =>
    [...document.querySelectorAll("*")].filter(
      (el) => getComputedStyle(el).backdropFilter !== "none",
    );
  const scroller = document.scrollingElement ?? document.documentElement;
  const scrollable = scroller.scrollHeight - scroller.clientHeight > 8;
  let mover = null;
  if (!scrollable) {
    mover = document.createElement("div");
    mover.style.cssText =
      "position:fixed;inset:-200px;z-index:0;pointer-events:none;background-size:32px 32px;" +
      "background-image:linear-gradient(45deg,#0008 25%,transparent 25%,transparent 75%,#0008 75%)," +
      "linear-gradient(45deg,#0008 25%,#fff8 25%,#fff8 75%,#0008 75%);" +
      "background-position:0 0,16px 16px;will-change:transform";
    document.body.append(mover);
  }
  let t = 0, last = performance.now();
  const s = [];
  const frame = (now) => {
    t += 1;
    if (mover) mover.style.transform = `translate(${(t % 64) - 32}px,${((t * 7) % 64) - 32}px)`;
    else window.scrollBy(0, t % 2 ? 1 : -1);
    s.push(now - last);
    last = now;
    if (s.length < 240) requestAnimationFrame(frame);
    else {
      const w = s.slice(60).sort((a, b) => a - b);
      const els = filtered();
      const boxes = els.map((el) => el.getBoundingClientRect());
      window.__cost = {
        frames: w.length, medianMs: w[w.length >> 1],
        meanMs: w.reduce((a, b) => a + b, 0) / w.length,
        fps: 1000 / (w.reduce((a, b) => a + b, 0) / w.length),
        p90Ms: w[Math.floor(w.length * 0.9)], minMs: w[0],
        n: els.length,
        invalidatedBy: mover ? "injected moving strip" : "scroll",
        largest: boxes.length
          ? boxes.map((b) => [Math.round(b.width), Math.round(b.height)])
              .sort((a, b) => b[0] * b[1] - a[0] * a[1])[0]
          : null,
      };
      document.documentElement.dataset.done = "1";
    }
  };
  requestAnimationFrame(frame);
})();
