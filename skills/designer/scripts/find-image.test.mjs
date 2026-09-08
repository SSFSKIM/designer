// scripts/find-image.test.mjs — the parts that need no network: header parsing, the inventory
// walk, the two normalisers, orientation mapping, key discovery, the snippet.
import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync, mkdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { dimensions, inventory, normalizeUnsplash, normalizeOpenverse, orientationParams, unsplashKey, snippet, verify } from "./find-image.mjs";

const png = (w, h) => {
  const b = Buffer.alloc(33); b.writeUInt32BE(0x89504e47, 0); b.writeUInt32BE(0x0d0a1a0a, 4);
  b.writeUInt32BE(13, 8); b.write("IHDR", 12); b.writeUInt32BE(w, 16); b.writeUInt32BE(h, 20); return b;
};
const gif = (w, h) => { const b = Buffer.alloc(13); b.write("GIF89a", 0); b.writeUInt16LE(w, 6); b.writeUInt16LE(h, 8); return b; };
const jpeg = (w, h) => {
  // SOI, an APP0 segment, then SOF0 carrying the size.
  const b = Buffer.from([0xff, 0xd8, 0xff, 0xe0, 0x00, 0x04, 0x00, 0x00, 0xff, 0xc0, 0x00, 0x11, 0x08, 0, 0, 0, 0, 0x03]);
  b.writeUInt16BE(h, 13); b.writeUInt16BE(w, 15); return b;
};

test("reads dimensions from PNG, GIF, JPEG and SVG headers", () => {
  assert.deepEqual(dimensions(png(1600, 900), ".png"), { width: 1600, height: 900 });
  assert.deepEqual(dimensions(gif(320, 240), ".gif"), { width: 320, height: 240 });
  assert.deepEqual(dimensions(jpeg(4000, 3000), ".jpg"), { width: 4000, height: 3000 });
  assert.deepEqual(dimensions(Buffer.from('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'), ".svg"), { width: 24, height: 24 });
  assert.deepEqual(dimensions(Buffer.from('<svg width="120" height="40">'), ".svg"), { width: 120, height: 40 });
  assert.equal(dimensions(Buffer.from("not an image"), ".png"), null);
});

test("inventory lists image files with sizes and skips build directories", () => {
  const root = mkdtempSync(join(tmpdir(), "find-image-"));
  mkdirSync(join(root, "public", "images"), { recursive: true });
  mkdirSync(join(root, "node_modules", "pkg"), { recursive: true });
  writeFileSync(join(root, "public", "images", "hero.png"), png(2400, 1600));
  writeFileSync(join(root, "public", "images", "mark.svg"), '<svg viewBox="0 0 64 64"></svg>');
  writeFileSync(join(root, "node_modules", "pkg", "logo.png"), png(10, 10));
  writeFileSync(join(root, "README.md"), "# not an image");
  const files = inventory(root).sort((a, b) => a.path.localeCompare(b.path));
  assert.deepEqual(files.map((f) => [f.path, f.kind, f.width, f.height]), [
    ["public/images/hero.png", "raster", 2400, 1600],
    ["public/images/mark.svg", "svg", 64, 64],
  ]);
});

test("normalises an Unsplash result to the common shape with a sized URL and a credit", () => {
  const c = normalizeUnsplash({
    id: "loDPKt_srQ0", width: 7281, height: 4993, color: "#d9d9d9", alt_description: "a store aisle", description: null,
    urls: { raw: "https://images.unsplash.com/photo-1?ixid=abc" }, links: { html: "https://unsplash.com/photos/x", download_location: "https://api.unsplash.com/photos/loDPKt_srQ0/download?ixid=abc" },
    user: { name: "Oxana Melis", links: { html: "https://unsplash.com/@oxana" } },
  }, 1600);
  assert.equal(c.source, "unsplash");
  assert.equal(c.url, "https://images.unsplash.com/photo-1?ixid=abc&w=1600&fit=crop&auto=format&q=80");
  assert.equal(c.credit, "Photo by Oxana Melis on Unsplash");
  assert.match(c.creatorUrl, /utm_source=designer&utm_medium=referral$/);
  assert.equal(c.downloadLocation, "https://api.unsplash.com/photos/loDPKt_srQ0/download?ixid=abc");
});

test("normalises an Openverse result with its licence and attribution", () => {
  const c = normalizeOpenverse({
    id: "3f2a1b00-0000-4000-8000-000000000000", title: "Old fashioned tools", url: "https://live.staticflickr.com/x.jpg", width: 1024, height: 620,
    license: "by", license_version: "2.0", license_url: "https://creativecommons.org/licenses/by/2.0/", creator: "someone", creator_url: "https://flickr.com/someone",
    foreign_landing_url: "https://flickr.com/photos/1", attribution: '"Old fashioned tools" by someone is licensed under CC BY 2.0.',
  });
  assert.equal(c.source, "openverse");
  assert.equal(c.license, "BY 2.0");
  assert.equal(c.credit, '"Old fashioned tools" by someone is licensed under CC BY 2.0.');
  assert.equal(c.downloadLocation, null);
});

test("maps orientation to each service's parameter and rejects an unknown one", () => {
  assert.deepEqual(orientationParams("landscape"), { unsplash: "&orientation=landscape", openverse: "&aspect_ratio=wide" });
  assert.deepEqual(orientationParams(null), { unsplash: "", openverse: "" });
  assert.throws(() => orientationParams("wide"), /landscape, portrait or squarish/);
});

test("reads the key from the environment before the key file", () => {
  assert.equal(unsplashKey({ UNSPLASH_ACCESS_KEY: " abc " }), "abc");
});

test("the snippet carries alt, intrinsic size, a container colour and the credit", () => {
  const s = snippet({ source: "unsplash", url: "https://i/x", alt: 'aisle "A"', width: 7281, height: 4993, color: "#d9d9d9", creator: "Oxana Melis", creatorUrl: "https://unsplash.com/@oxana?utm" });
  assert.match(s, /alt="aisle &quot;A&quot;"/);
  assert.match(s, /width="7281" height="4993"/);
  assert.match(s, /background:#d9d9d9/);
  assert.match(s, /Photo by <a href="https:\/\/unsplash.com\/@oxana\?utm">Oxana Melis<\/a> on <a href="https:\/\/unsplash.com\/\?utm_source=designer&utm_medium=referral">Unsplash<\/a>/);
});

test("verify accepts only an OK image response", async () => {
  const ok = async () => ({ ok: true, headers: new Map([["content-type", "image/jpeg"]]) });
  const html = async () => ({ ok: true, headers: new Map([["content-type", "text/html"]]) });
  const gone = async () => ({ ok: false, headers: new Map() });
  assert.equal(await verify({ url: "https://x" }, ok), true);
  assert.equal(await verify({ url: "https://x" }, html), false);
  assert.equal(await verify({ url: "https://x" }, gone), false);
});
