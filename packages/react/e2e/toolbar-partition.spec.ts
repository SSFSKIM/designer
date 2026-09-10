/**
 * The toolbar partition, in a browser (W27b; contract X5).
 *
 * The playground's toolbar is split the way Apple splits one: a flexible spacer,
 * then a trailing item that declares `sharedBackground="hidden"` and takes a
 * sampling group of its own. What that has to be true of is asserted here —
 * one toolbar, two groups, and enough room between them — and what it must
 * *not* disturb is asserted where it already was: `semantics.spec.ts` arrows
 * from the favourites button straight to the menu trigger, across the split,
 * and `End` still reaches it.
 *
 * Structural rather than pixel, so it runs on all three engines: the group a
 * host belongs to is on the host as `data-vitrea-group`, and the room between
 * two partitions is a measured distance.
 */

import { expect, test } from "@playwright/test";

import { gotoPlayground } from "./support";

const GROUP_ATTRIBUTE = "data-vitrea-group";

test.beforeEach(async ({ page }) => {
  await gotoPlayground(page);
});

/** The group a control's own glass host registered in. */
const groupOf = (page: import("@playwright/test").Page, name: string) =>
  page
    .getByRole("button", { name })
    .evaluate((element, attribute) => element.closest(`[${attribute}]`)?.getAttribute(attribute), GROUP_ATTRIBUTE);

test("one toolbar, two sampling groups", async ({ page }) => {
  await expect(page.getByRole("toolbar")).toHaveCount(1);

  const shared = await groupOf(page, "Share");
  const stepped = await groupOf(page, "Actions");

  expect(shared).toBe("toolbar");
  // The item's own `groupProps` named this one; the partition would otherwise
  // have taken the toolbar's id with an index.
  expect(stepped).toBe("toolbar-menu");
});

test("every member of the shared partition is in the shared group", async ({ page }) => {
  for (const name of ["Share", "Add to favorites", "Disabled"]) {
    expect(await groupOf(page, name), name).toBe("toolbar");
  }
});

test("the spacer opens its minimum, and the two partitions are at least that far apart", async ({
  page,
}) => {
  const spacer = page.locator("[data-vitrea-toolbar-spacer]");
  await expect(spacer).toHaveCount(1);
  await expect(spacer).toHaveAttribute("data-vitrea-toolbar-spacer", "flexible");

  // The minimum is the sampling padding the material requires under the live
  // policy — derived by the toolbar, not written into the page's CSS.
  const minimum = await spacer.evaluate((element) =>
    Number.parseFloat(getComputedStyle(element).minWidth),
  );
  expect(minimum).toBeGreaterThan(0);

  const box = await spacer.boundingBox();
  expect(box?.width ?? 0).toBeGreaterThanOrEqual(minimum - 0.5);

  // And the shapes on either side of it really are that far apart, which is the
  // property the proxies need rather than the property the spacer declares.
  const left = await page.getByRole("button", { name: "Disabled" }).boundingBox();
  const right = await page.getByRole("button", { name: "Actions" }).boundingBox();
  const gap = (right?.x ?? 0) - ((left?.x ?? 0) + (left?.width ?? 0));
  expect(gap).toBeGreaterThanOrEqual(minimum);
});
