import { expect, test, type Page } from "@playwright/test";

import { channelDelta, gotoHarness, sample } from "../support";

/**
 * The author tint, in pixels, on the CSS tier.
 *
 * Everything else about the tint is arithmetic and is unit-tested as arithmetic.
 * What only a browser can answer is what a tinted surface does with the backdrop
 * behind it once the colour lands — and since W10 that answer has two halves,
 * because the reference's has (claims §5.36). Apple's tinted material is an
 * **opaque, hue-preserving shade of the seed** whose brightness follows the
 * untinted material's own luminance, composited over the material at the
 * author's strength. So at full strength the surface IS the shade: the GPU tier's
 * tracks the backdrop pixel by pixel, and this tier — one colour per element —
 * reads the material's luminance at one level per source and paints one colour,
 * which is its documented granularity. Below full strength the material the
 * shade sits on still transmits, and the backdrop comes through.
 *
 * The assertions are relationships between sampled pixels and the published
 * declarations, plus the one fold this tier does in closed form: the author's
 * layer over the material's single `rgba()` is `α″ = 1 − (1 − s)(1 − α′)`.
 */
test.beforeEach(async ({ page }) => {
  await gotoHarness(page);
});

const PANEL = { x: 300, y: 200, width: 220, height: 120 };

/**
 * Two surfaces over the same backdrop in one group, one tinted and one not.
 *
 * The pair is the point: it is the composition Apple's guidance describes (one
 * emphasised control among plain ones) and the one that proves tint strength is
 * a per-surface quantity rather than a property of the whole optics pass.
 */
const buildPair = async (page: Page, tint: string): Promise<void> => {
  await page.evaluate(async (colour) => {
    await window.h.createRoot({ renderer: "css" });
    window.h.addGroup("g");
    window.h.addSurface({
      groupId: "g",
      nodeId: "panel",
      left: 300,
      top: 200,
      width: 220,
      height: 120,
      radius: 26,
      label: "",
      tint: colour,
    });
    window.h.addSurface({
      groupId: "g",
      nodeId: "plain",
      left: 300,
      top: 360,
      width: 220,
      height: 120,
      radius: 26,
      label: "",
    });
    window.h.frame(3);
  }, tint);
};

/**
 * One tinted surface over a registered flat backdrop, so the level the shade is
 * read at is known — the tone this tier samples from the source.
 */
const buildOver = async (page: Page, fill: string, tint: string): Promise<void> => {
  await gotoHarness(page);
  await page.evaluate(
    async ([backdrop, colour]) => {
      await window.h.createRoot({ renderer: "css" });
      window.h.addTextureGroup({ groupId: "g", sourceId: "g.raster", fill: backdrop });
      window.h.addSurface({
        groupId: "g",
        nodeId: "panel",
        left: 300,
        top: 200,
        width: 220,
        height: 120,
        radius: 26,
        label: "",
        tint: colour,
      });
      window.h.frame(3);
    },
    [fill, tint] as const,
  );
};

const PLAIN = { x: 300, y: 360, width: 220, height: 120 };

interface Declared {
  readonly tint: string;
  readonly occlusion: number;
}

const declared = (page: Page, nodeId: string): Promise<Declared> =>
  page.evaluate((id) => {
    const el = document.querySelector<HTMLElement>(`[data-vitrea-node="${id}"]`);
    return {
      tint: el?.style.getPropertyValue("--vitrea-tint") ?? "",
      occlusion: Number.parseFloat(el?.style.getPropertyValue("--vitrea-occlusion") ?? "0"),
    };
  }, nodeId);

/** `rgba(r, g, b, a)` → the three channels. */
const channelsOf = (tint: string): [number, number, number] => {
  const parts = (/rgba?\(([^)]*)\)/.exec(tint)?.[1] ?? "").split(",").map((part) => Number(part));
  return [parts[0] ?? 0, parts[1] ?? 0, parts[2] ?? 0];
};

const level = (rgb: readonly [number, number, number]): number =>
  0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2];

/** How far four points across the panel differ from one another, at most. */
const spreadAcross = async (page: Page): Promise<number> => {
  const tinted = await sample(page, PANEL);
  const points = ([
    [30, 30],
    [110, 60],
    [190, 90],
    [190, 30],
  ] as const).map(([x, y]) => tinted.at(x, y));
  return Math.max(
    ...points.map((point) => Math.max(...points.map((other) => channelDelta(point, other)))),
  );
};

test("colours the surface it is set on, and only that one", async ({ page }) => {
  await buildPair(page, "#ff9500");

  const tinted = (await sample(page, PANEL)).at(110, 60);
  const plain = (await sample(page, PLAIN)).at(110, 60);

  // Warmth rather than absolute channels: the harness page's own backdrop is not
  // neutral, so what a tint has to do is *add* warmth over whatever was there,
  // and what its neighbour has to do is not gain any.
  const warmth = (pixel: { r: number; b: number }): number => pixel.r - pixel.b;
  expect(warmth(tinted)).toBeGreaterThan(warmth(plain) + 40);

  // And the declarations agree: one surface's tint moved, the other's did not.
  const declarations = await page.evaluate(() =>
    ["panel", "plain"].map(
      (id) =>
        document
          .querySelector<HTMLElement>(`[data-vitrea-node="${id}"]`)
          ?.style.getPropertyValue("--vitrea-tint") ?? "",
    ),
  );
  expect(declarations[0]).not.toBe(declarations[1]);
  /*
   * The untinted neighbour keeps the material's own colour, and since W17 G1
   * (Decision Log 2 (b)) that colour is one code below white: the inner shadow
   * enters the mirror as the shader's own layer identity, so the pair states the
   * same material with the colour scaled and the alpha raised. What this test is
   * about is that an author's tint reaches the surface it was set on and no
   * other, so the assertion follows the material's colour rather than pinning
   * the literal white it used to be.
   */
  expect(declarations[1]).toContain("254, 254, 254");
});

test("at full strength the surface is the shade — opaque, and its brightness follows the material's luminance", async ({
  page,
}) => {
  /*
   * The half of the claim that changed with W10. A full-strength tint used to be
   * a wash the backdrop still varied through; the reference's is an opaque shade,
   * and on this tier — one colour per element — that is a flat colour across the
   * surface, whatever is behind it. Its brightness is what still answers to the
   * backdrop: darker over dark content, the seed itself over light.
   */
  await buildPair(page, "#ff9500");
  expect((await declared(page, "panel")).occlusion).toBe(1);
  expect(await spreadAcross(page), "at full strength the tier paints one colour").toBe(0);

  // The shade reads the material's luminance at the level the source samples,
  // so the same seed lands darker over the dark backdrop — and keeps its hue
  // both times: an orange, warm to cool, not a brown or a grey.
  await buildOver(page, "rgb(76, 76, 76)", "#ff9500");
  const overDark = channelsOf((await declared(page, "panel")).tint);
  await buildOver(page, "rgb(220, 220, 220)", "#ff9500");
  const overLight = channelsOf((await declared(page, "panel")).tint);

  expect(level(overDark)).toBeLessThan(level(overLight) - 4);
  for (const shade of [overDark, overLight]) {
    expect(shade[0]).toBeGreaterThan(shade[1]);
    expect(shade[1]).toBeGreaterThan(shade[2]);
  }
});

test("stays glass below full strength — the backdrop still varies through a half-strength tint", async ({
  page,
}) => {
  /*
   * The other half. A solid fill is constant across the surface whatever is
   * behind it; a half-strength tint is the shade over a material that still
   * transmits, so two points over different backdrop content must still differ.
   * The harness page's backdrop is patterned, which is what makes this
   * measurable at all.
   */
  await buildPair(page, "rgb(255 149 0 / 50%)");
  expect(await spreadAcross(page), "a tinted surface that varies nowhere is a fill").toBeGreaterThan(
    2,
  );

  // And the opacity is the fold, in closed form: the author's layer at s over
  // the material at α′ is one `rgba()` at 1 − (1 − s)(1 − α′). The untinted
  // neighbour in the same group carries α′ — same span, same size lift.
  const panel = await declared(page, "panel");
  const plain = await declared(page, "plain");
  expect(Math.abs(panel.occlusion - (1 - 0.5 * (1 - plain.occlusion)))).toBeLessThan(0.002);
});

test("a half-strength tint lands between the untinted material and the full one", async ({
  page,
}) => {
  // The strength axis, end to end: the author writes it as the colour's alpha,
  // and it moves the material's tint colour rather than its opacity.
  const centreFor = async (tint: string | undefined): Promise<{ r: number; b: number }> => {
    await page.evaluate(async (colour) => {
      await window.h.createRoot({ renderer: "css" });
      window.h.addGroup("g");
      window.h.addSurface({
        groupId: "g",
        nodeId: "panel",
        left: 300,
        top: 200,
        width: 220,
        height: 120,
        radius: 26,
        label: "",
        ...(colour === undefined ? {} : { tint: colour }),
      });
      window.h.frame(3);
    }, tint);
    return (await sample(page, PANEL)).at(110, 60);
  };

  const plain = await centreFor(undefined);
  const half = await centreFor("rgb(255 149 0 / 50%)");
  const full = await centreFor("#ff9500");

  const warmth = (pixel: { r: number; b: number }): number => pixel.r - pixel.b;
  expect(warmth(half)).toBeGreaterThan(warmth(plain));
  expect(warmth(full)).toBeGreaterThan(warmth(half));
});

test("keeps the frost — a tint changes the colour and the opacity, never the blur", async ({
  page,
}) => {
  const blurFor = async (tint: string | undefined): Promise<string | undefined> => {
    await page.evaluate(async (colour) => {
      await window.h.createRoot({ renderer: "css" });
      window.h.addGroup("g");
      window.h.addSurface({
        groupId: "g",
        nodeId: "panel",
        left: 300,
        top: 200,
        width: 220,
        height: 120,
        radius: 26,
        label: "",
        ...(colour === undefined ? {} : { tint: colour }),
      });
      window.h.frame(3);
    }, tint);
    return page.evaluate(() => {
      const host = document.querySelector<HTMLElement>('[data-vitrea-node="panel"]');
      return host?.style.getPropertyValue("--vitrea-blur");
    });
  };

  // The blur is the material's, not the tint's: whatever the fold does to the
  // alpha to composite the author's layer, it must not touch the frost.
  expect(await blurFor("#ff9500")).toBe(await blurFor(undefined));
});

test("gives up the tint entirely under forced colours", async ({ page }) => {
  // The accessibility policy that removes the material removes the colour with
  // it: there is no glass to tint, and the palette is the platform's.
  await page.emulateMedia({ forcedColors: "active" });
  await buildPair(page, "#ff9500");

  const style = await page.evaluate(() => {
    const host = document.querySelector<HTMLElement>('[data-vitrea-node="panel"]');
    return {
      tint: host?.style.getPropertyValue("--vitrea-tint"),
      ink: host?.style.getPropertyValue("--vitrea-foreground"),
    };
  });

  expect(style.tint).toBe("Canvas");
  expect(style.ink).toBe("CanvasText");

  // And the surface is flat, which is what "no glass" means in pixels.
  const panel = await sample(page, PANEL);
  expect(channelDelta(panel.at(110, 60), panel.at(40, 30))).toBe(0);
});

test("refuses a colour it cannot parse, and says so rather than inventing one", async ({
  page,
}) => {
  const findings = await page.evaluate(async () => {
    await window.h.createRoot({ renderer: "css", devMode: true });
    window.h.addGroup("g");
    window.h.addSurface({
      groupId: "g",
      nodeId: "panel",
      left: 300,
      top: 200,
      width: 220,
      height: 120,
      radius: 26,
      label: "",
      tint: "definitely-not-a-colour",
    });
    window.h.frame(3);
    return window.h.diagnosticCodes();
  });

  expect(findings).toContain("tint-unparseable");

  // A browser parses everything else, including the keywords a numeric-only
  // parser would have had to refuse.
  await buildPair(page, "rebeccapurple");
  const tinted = (await sample(page, PANEL)).at(110, 60);
  expect(tinted.b).toBeGreaterThan(tinted.g + 10);
});
