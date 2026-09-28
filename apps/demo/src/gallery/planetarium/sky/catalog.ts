/**
 * The star catalogue as the page holds it: parallel typed arrays, sorted brightest first, read
 * from the binary `build-planetarium-stars.mjs` writes (`data/stars.bin`, its layout in that
 * script's header) and the proper names beside it.
 */

export interface StarCatalog {
  readonly count: number;
  /** Right ascension, radians, J2000. */
  readonly ra: Float32Array;
  /** Declination, radians, J2000. */
  readonly dec: Float32Array;
  /** Visual magnitude. */
  readonly mag: Float32Array;
  /** B−V colour index; 0.5 where the catalogue has none. */
  readonly bv: Float32Array;
  /** Harvard Revised number. */
  readonly hr: Uint16Array;
  /** Catalogue index by HR number. */
  readonly indexOfHr: ReadonlyMap<number, number>;
  /** Proper names, by HR number. */
  readonly nameOfHr: ReadonlyMap<number, string>;
  /** Catalogue indices of the named stars, brightest first. */
  readonly named: readonly number[];
}

const RECORD = 14;

export function parseCatalog(buffer: ArrayBuffer, names: readonly { hr: number; name: string }[]): StarCatalog {
  const view = new DataView(buffer);
  const count = view.getUint32(0, true);
  const ra = new Float32Array(count);
  const dec = new Float32Array(count);
  const mag = new Float32Array(count);
  const bv = new Float32Array(count);
  const hr = new Uint16Array(count);
  const indexOfHr = new Map<number, number>();
  for (let i = 0; i < count; i += 1) {
    const o = 4 + i * RECORD;
    ra[i] = view.getFloat32(o, true);
    dec[i] = view.getFloat32(o + 4, true);
    mag[i] = view.getInt16(o + 8, true) / 100;
    const colour = view.getInt16(o + 10, true);
    bv[i] = colour === 32767 ? 0.5 : colour / 100;
    hr[i] = view.getUint16(o + 12, true);
    indexOfHr.set(hr[i] as number, i);
  }
  const nameOfHr = new Map(names.map((entry) => [entry.hr, entry.name] as const));
  const named = names
    .map((entry) => indexOfHr.get(entry.hr))
    .filter((index): index is number => index !== undefined)
    .sort((a, b) => (mag[a] as number) - (mag[b] as number));
  return { count, ra, dec, mag, bv, hr, indexOfHr, nameOfHr, named };
}

export async function loadCatalog(binUrl: string, names: readonly { hr: number; name: string }[]): Promise<StarCatalog> {
  const response = await fetch(binUrl);
  if (!response.ok) throw new Error(`The star catalogue did not load (${String(response.status)}).`);
  return parseCatalog(await response.arrayBuffer(), names);
}
