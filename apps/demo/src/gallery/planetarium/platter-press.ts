/**
 * Press inside an open platter, written by the page (`references/vitrea.md` §6).
 *
 * An open `GlassMorph` host is not interactive, so the plain buttons on a platter get no light or
 * compression from the runtime. The runtime reads a host's channels off its inline style every
 * frame whatever `interactive` says, so on a press inside the platter the page writes `press`,
 * `glow` and the press point onto the platter's host from a frame subscription taken when the
 * press begins — after the morph's own listener, so the write lands last — and leaves when the
 * light has decayed. The timing is the runtime's own character: glow attacks in about 70 ms and
 * decays over 320, compression settles in about 260. Under Reduce Motion there is no compression,
 * and the glow still arrives.
 */

import { GLASS_CHANNEL_PROPERTIES, type GlassRoot } from "@vitreajs/vitrea-web";
import { useEffect } from "react";

export function usePlatterPress(
  root: GlassRoot | null,
  hostSelector: string,
  active: boolean,
  reducedMotion: boolean,
): void {
  useEffect(() => {
    if (root === null || !active) return;
    const host = document.querySelector<HTMLElement>(hostSelector);
    if (host === null) return;
    let press = 0;
    let glow = 0;
    let pressed = false;
    let unsubscribe: (() => void) | undefined;
    const write = (): void => {
      host.style.setProperty(GLASS_CHANNEL_PROPERTIES.press, press.toFixed(4));
      host.style.setProperty(GLASS_CHANNEL_PROPERTIES.glow, glow.toFixed(4));
    };
    const step = (deltaMs: number): void => {
      const dt = Math.min(deltaMs, 50);
      const pressTarget = pressed && !reducedMotion ? 1 : 0;
      press += (pressTarget - press) * (1 - Math.exp(-dt / (pressed ? 60 : 90)));
      const glowTarget = pressed ? 1 : 0;
      glow += (glowTarget - glow) * (1 - Math.exp(-dt / (pressed ? 70 : 320)));
      write();
      if (!pressed && press < 0.002 && glow < 0.002) {
        press = 0;
        glow = 0;
        write();
        unsubscribe?.();
        unsubscribe = undefined;
      }
    };
    const onDown = (event: PointerEvent): void => {
      if (event.button !== 0) return;
      const rect = host.getBoundingClientRect();
      host.style.setProperty(GLASS_CHANNEL_PROPERTIES.pressX, `${(event.clientX - rect.left).toFixed(2)}px`);
      host.style.setProperty(GLASS_CHANNEL_PROPERTIES.pressY, `${(event.clientY - rect.top).toFixed(2)}px`);
      pressed = true;
      unsubscribe ??= root.subscribe(({ deltaMs }) => step(deltaMs));
    };
    const onUp = (): void => {
      pressed = false;
    };
    host.addEventListener("pointerdown", onDown);
    window.addEventListener("pointerup", onUp);
    window.addEventListener("pointercancel", onUp);
    return () => {
      host.removeEventListener("pointerdown", onDown);
      window.removeEventListener("pointerup", onUp);
      window.removeEventListener("pointercancel", onUp);
      unsubscribe?.();
      for (const property of [GLASS_CHANNEL_PROPERTIES.press, GLASS_CHANNEL_PROPERTIES.glow]) {
        host.style.removeProperty(property);
      }
    };
  }, [root, hostSelector, active, reducedMotion]);
}
