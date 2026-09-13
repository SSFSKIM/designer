/**
 * W27e G3's landing gate: every visible label rendered on demo glass.
 *
 * One table drives all three demo routes, both schemes and both tiers. A floor is
 * named for the rendered-pixel promise it checks: 4.5 for body labels, 3.0 for
 * the large plate labels, and named secondary pixel floors (4.45 CSS, 4.25
 * WebGPU) while each tier solves against an ideal composite that its selected
 * drawing form does not exactly paint. Tertiary and quaternary are measured and ordered,
 * never held to a floor they do not promise.
 *
 * This file belongs to the full-Chromium project because that is the only demo
 * project that can reach a hardware WebGPU adapter. It asks for CSS explicitly in
 * half its rows, so one instrument measures both tiers instead of comparing the
 * full browser to the headless shell's different compositor.
 */

import { expect, test, type Locator, type Page } from "@playwright/test";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

import {
  BODY_FLOOR,
  LARGE_FLOOR,
  SAMPLE_DELAYS,
  contrast,
  inkOf,
  inkOver,
  luminance,
  surfaceOf,
  surfaceUnderInk,
  type Channels,
} from "./glass-contrast";

const TIERS = ["css", "webgpu"] as const;
const SCHEMES = ["light", "dark"] as const;
const SECONDARY_PIXEL_FLOORS = { css: 4.45, webgpu: 4.25 } as const;

type Tier = (typeof TIERS)[number];
type Scheme = (typeof SCHEMES)[number];
type FloorName = "body-pixel" | "large-label-pixel" | "secondary-pixel";

interface LabelFamily {
  readonly id: string;
  readonly selector: string;
  readonly count: number;
  readonly floor: number | null;
  readonly floorName: FloorName | "read-only";
  readonly surface: "host" | "self";
}

interface InkReading {
  readonly rgb: Channels;
  readonly alpha: number;
  readonly ratio: number;
}

interface LabelReading {
  readonly route: string;
  readonly state: string;
  readonly family: string;
  readonly text: string;
  readonly surface: Channels;
  readonly floor: number | null;
  readonly floorName: LabelFamily["floorName"];
  readonly inks: readonly InkReading[];
  readonly ratio: number;
}

interface RunRecord {
  readonly tier: Tier;
  readonly scheme: Scheme;
  readonly takenAt: string;
  readonly accessibility: {
    readonly reduceTransparency: string;
    readonly increaseContrast: string;
  };
  readonly browser: {
    readonly userAgent: string;
    readonly dpr: number;
    readonly viewport: { readonly width: number; readonly height: number };
  };
  readonly adapter: unknown;
  readonly resolvedTiers: Record<string, readonly string[]>;
  readonly readings: LabelReading[];
  secondaryAttribution?: unknown;
}

const BODY = {
  floor: BODY_FLOOR,
  floorName: "body-pixel",
} as const;
const LARGE = {
  floor: LARGE_FLOOR,
  floorName: "large-label-pixel",
} as const;
const secondaryGate = (tier: Tier) => ({
  floor: SECONDARY_PIXEL_FLOORS[tier],
  floorName: "secondary-pixel" as const,
});
const READ_ONLY = { floor: null, floorName: "read-only" } as const;

const family = (
  id: string,
  selector: string,
  count: number,
  gate: Pick<LabelFamily, "floor" | "floorName">,
  surface: LabelFamily["surface"] = "host",
): LabelFamily => ({ id, selector, count, ...gate, surface });

async function gotoRoute(page: Page, path: string, tier: Tier, scheme: Scheme): Promise<void> {
  await page.emulateMedia({ colorScheme: scheme });
  const separator = path.includes("?") ? "&" : "?";
  await page.goto(`${path}${separator}renderer=${tier}`);
  await page.waitForSelector("[data-vitrea-root]", { state: "attached" });

  // The public site deliberately opens in light rather than following the OS.
  if (path === "/") {
    await page.getByTestId("color-scheme-select").selectOption(scheme);
    await expect(page.locator("html")).toHaveAttribute("data-color-scheme", scheme);
  }
}

async function showSection(page: Page, id: string): Promise<void> {
  await page.evaluate((section) => {
    document.getElementById(section)?.scrollIntoView({ block: "center", behavior: "instant" });
  }, id);
  await expect(page.locator(`#${id}`)).toHaveAttribute("data-current", "");
}

async function resolvedTierForSection(page: Page, id: string, tier: Tier): Promise<string[]> {
  const cells = page.locator(`#${id} .readout__row`, { hasText: "What is drawing" }).locator("dd");
  await expect(cells.first(), `${id} must publish its resolved renderer`).toBeVisible();
  await expect
    .poll(async () => Promise.all((await cells.all()).map((cell) => cell.innerText())))
    .toEqual(Array.from({ length: await cells.count() }, () => tier));
  return Promise.all((await cells.all()).map(async (cell) => (await cell.innerText()).trim()));
}

async function resolvedTierForPlayground(page: Page, tier: Tier): Promise<string[]> {
  const cells = page.locator(".state-table tr", { hasText: "activeRenderer" }).locator("td");
  await expect(cells.first(), "the playground must publish a resolved renderer").toBeVisible();
  await expect
    .poll(async () => Promise.all((await cells.all()).map((cell) => cell.innerText())))
    .toEqual(Array.from({ length: await cells.count() }, () => tier));

  const inkCells = page.locator("[data-testid^='ink-tier-']");
  await expect
    .poll(async () => Promise.all((await inkCells.all()).map((cell) => cell.innerText())))
    .toEqual(Array.from({ length: await inkCells.count() }, () => `${tier} · css-backdrop`));

  return [
    ...(await Promise.all((await cells.all()).map(async (cell) => (await cell.innerText()).trim()))),
    ...(await Promise.all(
      (await inkCells.all()).map(async (cell) => (await cell.innerText()).trim()),
    )),
  ];
}

function surfaceHost(target: Locator): Locator {
  return target.locator("xpath=ancestor-or-self::*[@data-vitrea-node][1]");
}

async function measureFamily(
  page: Page,
  record: RunRecord,
  route: string,
  state: string,
  spec: LabelFamily,
): Promise<LabelReading[]> {
  const targets = page.locator(spec.selector);
  await expect(targets, `${route} ${state}: ${spec.id}`).toHaveCount(spec.count);
  const readings: LabelReading[] = [];

  for (const target of await targets.all()) {
    await expect(target, `${route} ${state}: ${spec.id} must be visible`).toBeVisible();
    const surfaceTarget = spec.surface === "self" ? target : surfaceHost(target);
    await expect(surfaceTarget, `${route} ${state}: ${spec.id} needs a surface`).toHaveCount(1);
    const surface = await surfaceOf(surfaceTarget);
    const surfaceLevel = luminance(surface[0], surface[1], surface[2]);
    const inks = (await inkOf(target)).map((ink) => ({
      rgb: ink.rgb,
      alpha: ink.alpha,
      ratio: contrast(inkOver(ink, surface), surfaceLevel),
    }));
    const ratio = Math.min(...inks.map((ink) => ink.ratio));
    const text = (await target.innerText()).trim().replace(/\s+/g, " ");
    const reading: LabelReading = {
      route,
      state,
      family: spec.id,
      text,
      surface,
      floor: spec.floor,
      floorName: spec.floorName,
      inks,
      ratio,
    };
    record.readings.push(reading);
    readings.push(reading);

    if (spec.floor !== null) {
      expect(
        ratio,
        `${route} ${state}: ${text || spec.id} against ${spec.floorName}; ` +
          `surface ${surface.join(",")}; ink ${JSON.stringify(inks)}`,
      ).toBeGreaterThanOrEqual(spec.floor);
    }
  }
  return readings;
}

async function measureFamilies(
  page: Page,
  record: RunRecord,
  route: string,
  state: string,
  families: readonly LabelFamily[],
): Promise<LabelReading[]> {
  const out: LabelReading[] = [];
  for (const spec of families) out.push(...(await measureFamily(page, record, route, state, spec)));
  return out;
}

async function measurePhases(
  page: Page,
  record: RunRecord,
  route: string,
  state: string,
  families: readonly LabelFamily[],
): Promise<void> {
  for (const delay of SAMPLE_DELAYS) {
    await page.waitForTimeout(delay);
    await measureFamilies(page, record, route, `${state} at +${String(delay)}ms`, families);
  }
}

async function adapterRecord(page: Page): Promise<unknown> {
  return page.evaluate(async () => {
    if (navigator.gpu === undefined) return { available: false };
    const adapter = await navigator.gpu.requestAdapter();
    if (adapter === null) return { available: false };
    const info = {
      vendor: adapter.info?.vendor ?? null,
      architecture: adapter.info?.architecture ?? null,
      device: adapter.info?.device ?? null,
      description: adapter.info?.description ?? null,
    };
    const reported = (adapter as GPUAdapter & { readonly isFallbackAdapter?: boolean })
      .isFallbackAdapter;
    const identity = Object.values(info).filter((value) => value !== null).join(" ");
    return {
      available: true,
      // Chromium has removed this non-standard member on some builds. Its adapter
      // identity still distinguishes the hardware Metal path from SwiftShader.
      isFallbackAdapter:
        reported ?? /swiftshader|llvmpipe|software|cpu/i.test(identity),
      isFallbackAdapterReported: reported ?? null,
      info,
    };
  });
}

async function runSite(page: Page, record: RunRecord): Promise<void> {
  await gotoRoute(page, "/", record.tier, record.scheme);

  await showSection(page, "material");
  record.resolvedTiers["/ material"] = await resolvedTierForSection(
    page,
    "material",
    record.tier,
  );
  await measurePhases(page, record, "/", "material", [
    family("size labels", ".plate strong", 3, LARGE),
  ]);

  await showSection(page, "page");
  record.resolvedTiers["/ page"] = await resolvedTierForSection(page, "page", record.tier);
  await page.waitForTimeout(600);
  await measureFamilies(page, record, "/", "ordinary page content", [
    family("size labels", ".plate strong", 3, LARGE),
  ]);

  await showSection(page, "tone");
  record.resolvedTiers["/ tone"] = await resolvedTierForSection(page, "tone", record.tier);
  const slider = page.getByTestId("ground-level");
  for (let value = 2; value <= 160; value += 2) {
    await slider.fill(String(value));
    await expect(page.getByTestId("ground-level-readout")).toContainText(
      `${(value / 1000).toFixed(3)} linear`,
    );
    await page.waitForTimeout(320);
    await measureFamilies(page, record, "/", `tone ${String(value).padStart(3, "0")}/1000`, [
      family("size labels", ".plate strong", 3, LARGE),
    ]);
  }

  await showSection(page, "access");
  // The access section exposes policy rather than duplicating the group's tier
  // readout. It uses the same registered texture and root as the material section,
  // whose resolved renderer was read above.
  record.resolvedTiers["/ access"] = [`same texture root: ${record.tier}`];
  await measurePhases(page, record, "/", "accessibility", [
    family("material label", ".plate strong", 1, LARGE),
  ]);

  await showSection(page, "behavior");
  record.resolvedTiers["/ behavior"] = await resolvedTierForSection(
    page,
    "behavior",
    record.tier,
  );
  const closedFamilies = [
    family("toolbar controls", ".bar .control", 3, BODY, "self"),
    family("segments", ".segmented .segment", 3, BODY, "self"),
    family("closed morph", ".platter .control", 1, BODY, "self"),
  ] as const;
  await measurePhases(page, record, "/", "behaviour closed", closedFamilies);

  const favorite = page.getByRole("button", { name: "Add to favorites" });
  await favorite.click();
  await expect(page.getByRole("button", { name: "Remove from favorites" })).toBeVisible();
  await measureFamily(
    page,
    record,
    "/",
    "behaviour favourite selected",
    family("selected favourite glyph", ".bar .control--icon", 1, BODY, "self"),
  );

  await page.getByRole("button", { name: "Actions" }).click();
  await expect(page.locator(".menu__item")).toHaveCount(4);
  await measureFamilies(page, record, "/", "behaviour menu open", [
    family("menu items", ".menu__item", 4, BODY, "self"),
  ]);
}

async function runLaws(page: Page, record: RunRecord): Promise<void> {
  await gotoRoute(page, "/laws/", record.tier, record.scheme);
  const scenarios = [
    { id: "tone", count: 2, dynamic: false },
    { id: "tint", count: 2, dynamic: false },
    { id: "body", count: 1, dynamic: false },
    { id: "lens", count: 1, dynamic: false },
    { id: "nested", count: 2, dynamic: true },
  ] as const;

  for (const scenario of scenarios) {
    await showSection(page, scenario.id);
    record.resolvedTiers[`/laws/ ${scenario.id}`] = await resolvedTierForSection(
      page,
      scenario.id,
      record.tier,
    );
    const families = [family(`${scenario.id} labels`, ".plate strong", scenario.count, LARGE)];
    if (scenario.dynamic) {
      await measurePhases(page, record, "/laws/", scenario.id, families);
    } else {
      await page.waitForTimeout(600);
      await measureFamilies(page, record, "/laws/", scenario.id, families);
    }
  }
}

function alphaFromRgb(declaration: string): number {
  const found = /\/\s*([\d.]+)\)$/.exec(declaration);
  if (found === null) throw new Error(`no alpha in ${declaration}`);
  return Number(found[1]);
}

function rgbaFromDeclaration(declaration: string): { readonly rgb: Channels; readonly alpha: number } {
  const found = /^rgba?\((\d+)[, ]+\s*(\d+)[, ]+\s*(\d+)(?:[, ]+|\s*\/\s*)([\d.]+)\)$/.exec(
    declaration,
  );
  if (found === null) throw new Error(`not an rgba declaration: ${declaration}`);
  return {
    rgb: [Number(found[1]), Number(found[2]), Number(found[3])],
    alpha: Number(found[4]),
  };
}

function ratioForBlack(alpha: number, surface: Channels): number {
  const level = luminance(surface[0], surface[1], surface[2]);
  return contrast(
    luminance((1 - alpha) * surface[0], (1 - alpha) * surface[1], (1 - alpha) * surface[2]),
    level,
  );
}

async function secondaryAttribution(page: Page): Promise<unknown> {
  const plate = page.getByTestId("ink-plate-light");
  const specimen = plate.locator(".ink-level--secondary .ink-level__specimen");
  const plateMedian = await surfaceOf(plate);
  const underGlyph = await surfaceUnderInk(specimen);
  const overlay = page.locator(".ink-overlay");
  const previousVisibility = await overlay.evaluate((element) => {
    const html = element as HTMLElement;
    const value = html.style.getPropertyValue("visibility");
    const priority = html.style.getPropertyPriority("visibility");
    html.style.setProperty("visibility", "hidden", "important");
    return { value, priority };
  });
  let ground: Channels;
  try {
    ground = await surfaceOf(page.locator('.ink-ground[data-ground="light"]'));
  } finally {
    await overlay.evaluate((element, { value, priority }) => {
      const html = element as HTMLElement;
      if (value === "") html.style.removeProperty("visibility");
      else html.style.setProperty("visibility", value, priority);
    }, previousVisibility);
  }
  const declarations = await plate.evaluate((host) => {
    const style = (host as HTMLElement).style;
    return {
      tint: style.getPropertyValue("--vitrea-tint"),
      secondary: style.getPropertyValue("--vitrea-foreground-secondary"),
    };
  });
  const tint = rgbaFromDeclaration(declarations.tint);
  const solveSurface = [0, 1, 2].map(
    (index) =>
      (1 - tint.alpha) * (ground[index] ?? 0) + tint.alpha * (tint.rgb[index] ?? 0),
  ) as unknown as Channels;
  const tokenAlpha = alphaFromRgb(declarations.secondary);
  const recovered = (await inkOf(specimen))[0];
  if (recovered === undefined) throw new Error("secondary specimen has no ink");

  return {
    candidate: "solve-composite",
    declaredGroundByte: 231,
    sampledGround: ground,
    plateMedian,
    underGlyph,
    medianMinusUnderGlyph: plateMedian.map((value, index) => value - (underGlyph[index] ?? 0)),
    tintDeclaration: declarations.tint,
    secondaryDeclaration: declarations.secondary,
    solveSurface,
    solveMinusUnderGlyph: solveSurface.map((value, index) => value - (underGlyph[index] ?? 0)),
    tokenAlpha,
    recoveredAlpha: recovered.alpha,
    ratioTokenOnSolve: ratioForBlack(tokenAlpha, solveSurface),
    ratioTokenOnRendered: ratioForBlack(tokenAlpha, underGlyph),
    ratioRecoveredOnSolve: ratioForBlack(recovered.alpha, solveSurface),
    ratioRecoveredOnRendered: ratioForBlack(recovered.alpha, underGlyph),
  };
}

async function runPlayground(page: Page, record: RunRecord): Promise<void> {
  await gotoRoute(page, "/playground/", record.tier, record.scheme);
  record.resolvedTiers["/playground/"] = await resolvedTierForPlayground(page, record.tier);
  await page.waitForTimeout(600);

  await measureFamilies(page, record, "/playground/", "plates", [
    family("DOM plate heading", '[data-testid="dom-plate"] strong', 1, LARGE),
    family("DOM plate body", '[data-testid="dom-plate"] > span', 1, BODY),
    family("texture plate heading", '[data-testid="texture-plate"] strong', 1, LARGE),
    family("texture plate body", '[data-testid="texture-plate"] > span', 1, BODY),
    family("small texture plate", '[data-testid="texture-plate-small"] > span', 1, BODY),
  ]);

  await page.getByLabel("mix regular and clear in one group").check();
  await expect(page.getByTestId("texture-plate-small")).toContainText("clear");
  await measureFamilies(page, record, "/playground/", "clear plate state", [
    family("small texture plate", '[data-testid="texture-plate-small"] > span', 1, BODY),
  ]);

  await measurePhases(page, record, "/playground/", "controls closed", [
    family("segments", ".segmented .segment", 3, BODY, "self"),
    family("toolbar controls", ".toolbar .control", 3, BODY, "self"),
    family("closed morph", ".platter .control", 1, BODY, "self"),
  ]);

  await page.getByRole("button", { name: "Add to favorites" }).click();
  await expect(page.getByRole("button", { name: "Remove from favorites" })).toBeVisible();
  await measureFamilies(page, record, "/playground/", "favourite selected", [
    family("selected favourite glyph", ".toolbar .control--icon", 1, BODY, "self"),
  ]);

  await page.getByRole("button", { name: "Actions" }).click();
  await expect(page.locator(".menu__item")).toHaveCount(4);
  await measureFamilies(page, record, "/playground/", "menu open", [
    family("menu items", ".menu__item", 4, BODY, "self"),
  ]);
  // The open platter overlaps the band in this fixed composition. Close it before
  // measuring the labels beneath; otherwise the harness measures glass-over-glass
  // created by its own previous scenario rather than the ink plate's surface.
  await page.keyboard.press("Escape");
  await expect(page.locator(".menu__item")).toHaveCount(0);

  // Each scenario starts from the landing state. Reload before the ink plate so
  // the preceding clear-variant and open-morph checks cannot alter the pixels
  // behind it while still reporting a valid label of their own.
  await gotoRoute(page, "/playground/", record.tier, record.scheme);
  record.resolvedTiers["/playground/ ink reset"] = await resolvedTierForPlayground(
    page,
    record.tier,
  );
  await page.waitForTimeout(600);

  const nameReadings = await measureFamilies(page, record, "/playground/", "ink plates", [
    family("ink-level names", ".ink-level__name", 8, BODY),
  ]);
  expect(Math.min(...nameReadings.map((reading) => reading.ratio))).toBeGreaterThanOrEqual(BODY_FLOOR);

  const levelReadings: Record<string, LabelReading[]> = {};
  for (const [level, gate] of [
    ["primary", BODY],
    ["secondary", secondaryGate(record.tier)],
    ["tertiary", READ_ONLY],
    ["quaternary", READ_ONLY],
  ] as const) {
    levelReadings[level] = await measureFamilies(page, record, "/playground/", "ink plates", [
      family(`${level} specimens`, `.ink-level--${level} .ink-level__specimen`, 2, gate),
    ]);
  }

  for (let ground = 0; ground < 2; ground += 1) {
    const primary = levelReadings["primary"]?.[ground]?.ratio ?? Number.NaN;
    const secondary = levelReadings["secondary"]?.[ground]?.ratio ?? Number.NaN;
    const tertiary = levelReadings["tertiary"]?.[ground]?.ratio ?? Number.NaN;
    const quaternary = levelReadings["quaternary"]?.[ground]?.ratio ?? Number.NaN;
    expect(quaternary, `quaternary order on ground ${String(ground)}`).toBeLessThanOrEqual(tertiary);
    expect(tertiary, `tertiary order on ground ${String(ground)}`).toBeLessThanOrEqual(secondary);
    expect(secondary, `secondary order on ground ${String(ground)}`).toBeLessThanOrEqual(primary);
  }

  await measureFamilies(page, record, "/playground/", "ink-row controls", [
    family("bookmark and publish controls", ".ink-row .control", 4, BODY, "self"),
  ]);

  if (record.tier === "css" && record.scheme === "light") {
    record.secondaryAttribution = await secondaryAttribution(page);
  }
}

function writeEvidence(record: RunRecord): void {
  const directory = process.env.W27E_G3_EVIDENCE_DIR;
  if (directory === undefined) return;
  mkdirSync(directory, { recursive: true });
  writeFileSync(
    join(directory, `contrast-${record.tier}-${record.scheme}.json`),
    `${JSON.stringify(record, null, 2)}\n`,
  );
}

test.describe.configure({ mode: "serial" });

for (const tier of TIERS) {
  for (const scheme of SCHEMES) {
    test(`${tier} · ${scheme}: every demo glass label holds its named floor`, async ({ page }) => {
      test.setTimeout(8 * 60_000);
      await page.setViewportSize({ width: 1440, height: 1000 });
      await gotoRoute(page, "/playground/", tier, scheme);
      const adapter = await adapterRecord(page);
      if (tier === "webgpu") {
        expect(adapter).toMatchObject({ available: true, isFallbackAdapter: false });
      }

      const record: RunRecord = {
        tier,
        scheme,
        takenAt: new Date().toISOString(),
        accessibility: {
          reduceTransparency: process.env.W27E_REDUCE_TRANSPARENCY ?? "unrecorded",
          increaseContrast: process.env.W27E_INCREASE_CONTRAST ?? "unrecorded",
        },
        browser: {
          userAgent: await page.evaluate(() => navigator.userAgent),
          dpr: await page.evaluate(() => window.devicePixelRatio),
          viewport: page.viewportSize() ?? { width: 0, height: 0 },
        },
        adapter,
        resolvedTiers: {},
        readings: [],
      };

      await runPlayground(page, record);
      await runSite(page, record);
      await runLaws(page, record);
      writeEvidence(record);

      test.info().annotations.push({
        type: "measurement",
        description: `${String(record.readings.length)} label readings written for ${tier}/${scheme}`,
      });
    });
  }
}
