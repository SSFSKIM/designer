/**
 * Light travelling once around each rim as the glass materialises.
 *
 * The runtime's highlight pass draws a specular band at the `sweep` phase with the `shimmer`
 * amplitude, and nothing in the bindings drives either channel (`platform-web/src/channels.ts`);
 * this is the page driving them, on the runtime's own frame loop, for the one moment the material
 * arrives. Under Reduce Motion the runtime zeroes the shimmer gain itself, and this driver does
 * not start. Never at idle.
 */

import { GLASS_CHANNEL_PROPERTIES, type GlassRoot } from "@vitreajs/vitrea-web";

const DURATION_MS = 1100;
const STAGGER_MS = 160;

export function runMaterialiseSweep(root: GlassRoot, hosts: readonly HTMLElement[], reducedMotion: boolean): () => void {
  if (reducedMotion || hosts.length === 0) return () => undefined;
  let elapsed = 0;
  const unsubscribe = root.subscribe(({ deltaMs }) => {
    elapsed += Math.min(deltaMs, 50);
    let running = false;
    hosts.forEach((host, index) => {
      const t = (elapsed - index * STAGGER_MS) / DURATION_MS;
      if (t < 0) {
        running = true;
        return;
      }
      if (t >= 1) {
        host.style.removeProperty(GLASS_CHANNEL_PROPERTIES.sweep);
        host.style.removeProperty(GLASS_CHANNEL_PROPERTIES.shimmer);
        return;
      }
      running = true;
      host.style.setProperty(GLASS_CHANNEL_PROPERTIES.sweep, t.toFixed(4));
      host.style.setProperty(GLASS_CHANNEL_PROPERTIES.shimmer, Math.sin(Math.PI * t).toFixed(4));
    });
    if (!running) unsubscribe();
  });
  return () => {
    unsubscribe();
    for (const host of hosts) {
      host.style.removeProperty(GLASS_CHANNEL_PROPERTIES.sweep);
      host.style.removeProperty(GLASS_CHANNEL_PROPERTIES.shimmer);
    }
  };
}
