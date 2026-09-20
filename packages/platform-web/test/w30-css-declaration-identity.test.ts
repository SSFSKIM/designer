/**
 * W30 G2 — the CSS tier's half of the exemption's pixel proof.
 *
 * The wave gives the outer shadow's σ a law in the casting span (claims §5.156
 * §2), and this tier evaluates it **per surface**: one `box-shadow` per member,
 * whose blur radius is `2σ` at that member's own span. The law's three leaves
 * ship at values that make it return `sigmaPx` at every span — an added zero
 * under a `max` whose other arm is a multiplied zero — so the strings this tier
 * writes must not move at all.
 *
 * "Must not move" is asserted against bytes recorded before the leaves existed
 * rather than against a recomputation, because a recomputation would be the new
 * code judging itself. `w30-css-declarations-pre-leaves.json` was written by
 * `w30-record-declarations.mjs` on the tree at the commit before the leaves, over
 * the bed in `w30-css-declaration-bed.ts`, and it is never re-recorded.
 *
 * The comparison is character-identical over EVERY property the tier emits, not
 * only the shadow: a σ law that reached the frost or the rim would be as much a
 * violation of X1 as one that reached the blur radius, and a case that looked
 * only where the change is expected cannot see that.
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import { BACKDROPS, RATIOS, SCHEMES, SPANS, caseKey, declarationsOf, renderCase } from "./w30-css-declaration-bed";

const RECORDED = JSON.parse(
  readFileSync(resolve(import.meta.dirname, "w30-css-declarations-pre-leaves.json"), "utf8"),
) as Record<string, Record<string, string>>;

describe("W30's leaves move no CSS declaration (acceptance clause 1, X1)", () => {
  it("covers the whole recorded bed, so a missing case cannot pass quietly", () => {
    expect(Object.keys(RECORDED).length).toBe(
      SCHEMES.length * SPANS.length * BACKDROPS.length * RATIOS.length,
    );
  });

  it("writes a real shadow on most of the bed, so the comparison discriminates", () => {
    // The thin regime is inert over a backdrop with no light to remove, so the
    // darkest of the three levels resolves `"none"` by design. If every case did,
    // the identity below would be a pin on the string "none".
    const shadows = new Set(
      Object.values(RECORDED).map((declarations) => declarations["render.outerShadow"]),
    );
    expect(shadows.size).toBeGreaterThan(10);
    for (const value of shadows) {
      if (value === "none") continue;
      // The blur radius is `2 · sigmaPx` on the frozen macOS 26.5 material, at
      // every span of the sweep. That is the law's inert identity, read off the
      // string the browser would have been given.
      expect(value).toContain(`${String(2 * 15.55)}px`);
    }
  });

  for (const scheme of SCHEMES) {
    it(`${scheme}: every declaration is character-identical to the pre-leaf recording`, () => {
      for (const spanPx of SPANS) {
        for (const backdrop of BACKDROPS) {
          for (const dpr of RATIOS) {
            const key = caseKey(scheme, spanPx, backdrop, dpr);
            const recorded = RECORDED[key];
            expect(recorded, `${key}: absent from the pre-leaf recording`).toBeDefined();
            expect(
              declarationsOf(renderCase(scheme, spanPx, backdrop, dpr)),
              `${key}: the CSS tier's declarations moved across W30 G2's leaves`,
            ).toStrictEqual(recorded);
          }
        }
      }
    });
  }
});
