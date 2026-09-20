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

import {
  BACKDROPS,
  POLICIES,
  RATIOS,
  SCHEMES,
  SPANS,
  caseKey,
  declarationsOf,
  policyCaseKey,
  policyOf,
  renderCase,
} from "./w30-css-declaration-bed";

const RECORDED = JSON.parse(
  readFileSync(resolve(import.meta.dirname, "w30-css-declarations-pre-leaves.json"), "utf8"),
) as Record<string, Record<string, string>>;

/**
 * The same bed under the two accessibility regimes (claims §5.158 §8, finding
 * 6).
 *
 * Its own fixture rather than more rows in the one above, because the one above
 * is committed evidence recorded before the leaves and is never re-recorded.
 * This one was recorded the same way after the fact — `packages/platform-web/src`
 * checked out at `01347a2c`, the pre-leaf tree, the recorder run there with
 * `--policies`, the working tree restored — so the comparison is still against
 * pre-leaf bytes and not against a recomputation.
 */
const RECORDED_POLICIES = JSON.parse(
  readFileSync(
    resolve(import.meta.dirname, "w30-css-declarations-policies-pre-leaves.json"),
    "utf8",
  ),
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

  it("covers the policy bed too, and the policy cases are not the nominal ones", () => {
    expect(Object.keys(RECORDED_POLICIES).length).toBe(
      POLICIES.length * SCHEMES.length * SPANS.length * BACKDROPS.length * RATIOS.length,
    );
    /*
     * The fold has to be visible, or the loop below pins the nominal regime twice
     * under two names. `opticsUnderPolicy` is what makes them different — the
     * frost, the occlusion lift, the border and the tint saturation.
     */
    for (const policy of POLICIES) {
      const moved = Object.keys(RECORDED).filter(
        (key) => JSON.stringify(RECORDED_POLICIES[`${policy}/${key}`]) !== JSON.stringify(RECORDED[key]),
      );
      expect(moved.length, `${policy}: folds nothing, so its rows are the nominal ones`).toBe(
        Object.keys(RECORDED).length,
      );
    }

    /*
     * And the two regimes reach the shadow differently, which is the whole
     * reason both are here. Reduced transparency lifts the occlusion and moves
     * every `box-shadow` alpha on the bed; increased contrast moves the border,
     * the foreground and the frost and leaves the shadow exactly where it was.
     * Recorded as an assertion rather than as a sentence, because "the shadow is
     * unmoved" is a claim about the fold that a later wave could break silently.
     */
    const shadowMoved = (policy: (typeof POLICIES)[number]): number =>
      Object.keys(RECORDED).filter(
        (key) =>
          RECORDED_POLICIES[`${policy}/${key}`]?.["render.outerShadow"] !==
          RECORDED[key]?.["render.outerShadow"],
      ).length;
    expect(shadowMoved("reduced-transparency")).toBe(Object.keys(RECORDED).length);
    expect(shadowMoved("increased-contrast")).toBe(0);
    // And the shadow is drawn under both regimes at the same blur radius, which
    // is the law's inert identity read on the folded path.
    for (const [caseName, declarations] of Object.entries(RECORDED_POLICIES)) {
      const shadow = declarations["render.outerShadow"] ?? "";
      if (shadow === "none") continue;
      expect(shadow, caseName).toContain(`${String(2 * 15.55)}px`);
    }
  });

  for (const policy of POLICIES) {
    it(`${policy}: every declaration is character-identical to the pre-leaf recording`, () => {
      const resolved = policyOf(policy);
      for (const scheme of SCHEMES) {
        for (const spanPx of SPANS) {
          for (const backdrop of BACKDROPS) {
            for (const dpr of RATIOS) {
              const key = policyCaseKey(policy, scheme, spanPx, backdrop, dpr);
              const recorded = RECORDED_POLICIES[key];
              expect(recorded, `${key}: absent from the pre-leaf recording`).toBeDefined();
              expect(
                declarationsOf(renderCase(scheme, spanPx, backdrop, dpr, resolved)),
                `${key}: the CSS tier's declarations moved across W30 G2's leaves`,
              ).toStrictEqual(recorded);
            }
          }
        }
      }
    });
  }
});
