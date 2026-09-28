#!/usr/bin/env node
/* global process, Buffer, console -- a build-time script, run by Node, never shipped */
/**
 * The planetarium page's star catalogue, built from the Yale Bright Star Catalogue (5th revised
 * edition, Hoffleit & Warren 1991; CDS V/50, public domain) into one small binary the page fetches.
 *
 *   node apps/demo/scripts/build-planetarium-stars.mjs <path/to/bsc5.dat>
 *
 * Writes `src/gallery/planetarium/data/stars.bin`: a little-endian Uint32 count, then per star
 * Float32 RA (radians, J2000), Float32 Dec (radians), Int16 V magnitude × 100, Int16 B−V × 100
 * (32767 where the catalogue has none), and Uint16 HR number — 14 bytes each. Entries with no
 * J2000 position (the catalogue's novae and non-stellar objects) are dropped. The proper names
 * below are attached by HR number and each is checked against the catalogue's own Bayer name, so
 * a wrong number fails the build rather than mislabelling a star.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = process.argv[2];
if (source === undefined) throw new Error("Pass the path to bsc5.dat (CDS V/50 catalog).");
const out = resolve(here, "../src/gallery/planetarium/data");

/** Proper name, HR number, and the Bayer/Flamsteed fragment the catalogue's Name field carries. */
const NAMED = [
  ["Sirius", 2491, "Alp CMa"], ["Canopus", 2326, "Alp Car"], ["Arcturus", 5340, "Alp Boo"],
  ["Vega", 7001, "Alp Lyr"], ["Capella", 1708, "Alp Aur"], ["Rigel", 1713, "Bet Ori"],
  ["Procyon", 2943, "Alp CMi"], ["Betelgeuse", 2061, "Alp Ori"], ["Achernar", 472, "Alp Eri"],
  ["Altair", 7557, "Alp Aql"], ["Aldebaran", 1457, "Alp Tau"], ["Antares", 6134, "Alp Sco"],
  ["Spica", 5056, "Alp Vir"], ["Pollux", 2990, "Bet Gem"], ["Fomalhaut", 8728, "Alp PsA"],
  ["Deneb", 7924, "Alp Cyg"], ["Regulus", 3982, "Alp Leo"], ["Castor", 2891, "Alp Gem"],
  ["Polaris", 424, "Alp UMi"], ["Bellatrix", 1790, "Gam Ori"], ["Alnilam", 1903, "Eps Ori"],
  ["Alnitak", 1948, "Zet Ori"], ["Mintaka", 1852, "Del Ori"], ["Saiph", 2004, "Kap Ori"],
  ["Mirfak", 1017, "Alp Per"], ["Algol", 936, "Bet Per"], ["Alioth", 4905, "Eps UMa"],
  ["Dubhe", 4301, "Alp UMa"], ["Alkaid", 5191, "Eta UMa"], ["Mizar", 5054, "Zet UMa"],
  ["Denebola", 4534, "Bet Leo"], ["Alphard", 3748, "Alp Hya"], ["Rasalhague", 6556, "Alp Oph"],
  ["Albireo", 7417, "Bet1Cyg"], ["Alphecca", 5793, "Alp CrB"], ["Hamal", 617, "Alp Ari"],
  ["Scheat", 8775, "Bet Peg"], ["Markab", 8781, "Alp Peg"], ["Alpheratz", 15, "Alp And"],
  ["Mirach", 337, "Bet And"], ["Almach", 603, "Gam1And"], ["Shaula", 6527, "Lam Sco"],
  ["Nunki", 7121, "Sig Sgr"], ["Kaus Australis", 6879, "Eps Sgr"], ["Sadr", 7796, "Gam Cyg"],
  ["Enif", 8308, "Eps Peg"], ["Diphda", 188, "Bet Cet"], ["Elnath", 1791, "Bet Tau"],
  ["Alhena", 2421, "Gam Gem"], ["Adhara", 2618, "Eps CMa"], ["Wezen", 2693, "Del CMa"],
  ["Menkar", 911, "Alp Cet"], ["Schedar", 168, "Alp Cas"], ["Caph", 21, "Bet Cas"],
  ["Ruchbah", 403, "Del Cas"], ["Kochab", 5563, "Bet UMi"], ["Eltanin", 6705, "Gam Dra"],
  ["Acrux", 4730, "Alp1Cru"], ["Mimosa", 4853, "Bet Cru"], ["Gacrux", 4763, "Gam Cru"],
  ["Rigil Kentaurus", 5459, "Alp1Cen"], ["Hadar", 5267, "Bet Cen"], ["Peacock", 7790, "Alp Pav"],
  ["Alnair", 8425, "Alp Gru"], ["Zubenelgenubi", 5531, "Alp2Lib"], ["Sabik", 6378, "Eta Oph"],
  ["Menkent", 5288, "The Cen"], ["Atria", 6217, "Alp TrA"], ["Alsephina", 3485, "Del Vel"],
  ["Avior", 3307, "Eps Car"], ["Miaplacidus", 3685, "Bet Car"], ["Aspidiske", 3699, "Iot Car"],
  ["Suhail", 3634, "Lam Vel"], ["Tarazed", 7525, "Gam Aql"], ["Unukalhai", 5854, "Alp Ser"],
  ["Cor Caroli", 4915, "12Alp2CVn"], ["Vindemiatrix", 4932, "Eps Vir"], ["Zosma", 4357, "Del Leo"],
  ["Algieba", 4057, "Gam1Leo"], ["Merak", 4295, "Bet UMa"], ["Phecda", 4554, "Gam UMa"],
  ["Megrez", 4660, "Del UMa"], ["Thuban", 5291, "Alp Dra"], ["Alderamin", 8162, "Alp Cep"],
  ["Sheratan", 553, "Bet Ari"], ["Rasalgethi", 6406, "Alp1Her"], ["Kornephoros", 6148, "Bet Her"],
  ["Sadalmelik", 8414, "Alp Aqr"], ["Sadalsuud", 8232, "Bet Aqr"], ["Deneb Kaitos", 188, "Bet Cet"],
];

const text = readFileSync(source, "latin1");
const lines = text.split("\n").filter((line) => line.trim() !== "");
const field = (line, from, to) => line.slice(from - 1, to);
const num = (s) => (s.trim() === "" ? undefined : Number(s));

const stars = [];
const byHr = new Map();
for (const line of lines) {
  const hr = num(field(line, 1, 4));
  const rah = num(field(line, 76, 77));
  const ram = num(field(line, 78, 79));
  const ras = num(field(line, 80, 83));
  const deSign = field(line, 84, 84);
  const ded = num(field(line, 85, 86));
  const dem = num(field(line, 87, 88));
  const des = num(field(line, 89, 90));
  const vmag = num(field(line, 103, 107));
  const bv = num(field(line, 110, 114));
  if (hr === undefined || rah === undefined || ded === undefined || vmag === undefined) continue;
  const raHours = rah + (ram ?? 0) / 60 + (ras ?? 0) / 3600;
  const decDeg = (deSign === "-" ? -1 : 1) * (ded + (dem ?? 0) / 60 + (des ?? 0) / 3600);
  const star = { hr, ra: (raHours / 12) * Math.PI, dec: (decDeg / 180) * Math.PI, vmag, bv, name: field(line, 5, 14).trim() };
  stars.push(star);
  byHr.set(hr, star);
}
stars.sort((a, b) => a.vmag - b.vmag);

const names = [];
const seenHr = new Set();
for (const [name, hr, bayer] of NAMED) {
  if (seenHr.has(hr)) continue; // Deneb Kaitos is a second name for Diphda; the first wins.
  seenHr.add(hr);
  const star = byHr.get(hr);
  if (star === undefined) throw new Error(`HR ${hr} (${name}) is not in the catalogue.`);
  if (!star.name.replace(/\s+/g, "").includes(bayer.replace(/\s+/g, ""))) {
    throw new Error(`HR ${hr} is "${star.name}", not ${bayer}: ${name} would be mislabelled.`);
  }
  names.push({ hr, name });
}

const RECORD = 14;
const buffer = new ArrayBuffer(4 + stars.length * RECORD);
const view = new DataView(buffer);
view.setUint32(0, stars.length, true);
stars.forEach((star, i) => {
  const o = 4 + i * RECORD;
  view.setFloat32(o, star.ra, true);
  view.setFloat32(o + 4, star.dec, true);
  view.setInt16(o + 8, Math.round(star.vmag * 100), true);
  view.setInt16(o + 10, star.bv === undefined ? 32767 : Math.round(star.bv * 100), true);
  view.setUint16(o + 12, star.hr, true);
});
writeFileSync(resolve(out, "stars.bin"), Buffer.from(buffer));
writeFileSync(resolve(out, "names.json"), JSON.stringify(names) + "\n");
console.warn(`${stars.length} stars (${buffer.byteLength} bytes), ${names.length} named; brightest ${stars[0].name} ${stars[0].vmag}, faintest ${stars.at(-1).vmag}`);
