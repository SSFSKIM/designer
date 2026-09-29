/**
 * The shell's text primitives: the palette it may write, and how many cells a string takes.
 *
 * The palette is the contract's: the sixteen ANSI foreground colours and bold, each span closed
 * with a full reset so no colour can leak past the text it was meant for. The roles are the
 * conventional ones, so the page can design each colour for what it will carry: red for errors,
 * green for passes, yellow for warnings and numbers, blue for directories, magenta for branches
 * and refs, cyan for paths and hashes, bright black for secondary metadata.
 *
 * Width follows the terminal, not the string: a cell grid counts an East Asian wide character
 * (Hangul, Kana, CJK ideographs, fullwidth forms and the wide emoji) as two cells and a combining
 * mark as none, so a Korean word composed by the IME moves the cursor two cells per syllable. The
 * table is Unicode's East Asian Width, exact for the scripts an IME composes and coarse for emoji,
 * which is what xterm's Unicode 11 width provider draws.
 */

const paint =
  (codes: string) =>
  (text: string): string =>
    text === "" ? "" : `\x1b[${codes}m${text}\x1b[0m`;

export const bold = paint("1");
export const red = paint("31");
export const green = paint("32");
export const yellow = paint("33");
export const blue = paint("34");
export const magenta = paint("35");
export const cyan = paint("36");
export const grey = paint("90");
export const boldBlue = paint("1;34");
export const boldMagenta = paint("1;35");
export const boldGreen = paint("1;32");

/** A directory's name, as `ls` and `tree` draw it. */
export const directory = boldBlue;

// eslint-disable-next-line no-control-regex -- an escape sequence begins with ESC.
const SEQUENCE = /\x1b\[[0-9;?]*[@-~]|\x1b[^[]/g;

export function stripAnsi(text: string): string {
  return text.replace(SEQUENCE, "");
}

/** Code points that take two cells: East Asian Wide and Fullwidth, as [first, last] pairs. */
const WIDE: readonly (readonly [number, number])[] = [
  [0x1100, 0x115f], [0x231a, 0x231b], [0x2329, 0x232a], [0x23e9, 0x23ec], [0x23f0, 0x23f0],
  [0x23f3, 0x23f3], [0x25fd, 0x25fe], [0x2614, 0x2615], [0x2648, 0x2653], [0x267f, 0x267f],
  [0x2693, 0x2693], [0x26a1, 0x26a1], [0x26aa, 0x26ab], [0x26bd, 0x26be], [0x26c4, 0x26c5],
  [0x26ce, 0x26ce], [0x26d4, 0x26d4], [0x26ea, 0x26ea], [0x26f2, 0x26f3], [0x26f5, 0x26f5],
  [0x26fa, 0x26fa], [0x26fd, 0x26fd], [0x2705, 0x2705], [0x270a, 0x270b], [0x2728, 0x2728],
  [0x274c, 0x274c], [0x274e, 0x274e], [0x2753, 0x2755], [0x2757, 0x2757], [0x2795, 0x2797],
  [0x27b0, 0x27b0], [0x27bf, 0x27bf], [0x2b1b, 0x2b1c], [0x2b50, 0x2b50], [0x2b55, 0x2b55],
  [0x2e80, 0x303e], [0x3041, 0x33ff], [0x3400, 0x4dbf], [0x4e00, 0x9fff], [0xa000, 0xa4cf],
  [0xa960, 0xa97f], [0xac00, 0xd7a3], [0xf900, 0xfaff], [0xfe10, 0xfe19], [0xfe30, 0xfe6f],
  [0xff00, 0xff60], [0xffe0, 0xffe6], [0x16fe0, 0x16fe4], [0x17000, 0x18aff],
  [0x1b000, 0x1b16f], [0x1f004, 0x1f004], [0x1f0cf, 0x1f0cf], [0x1f18e, 0x1f18e],
  [0x1f191, 0x1f19a], [0x1f200, 0x1f251], [0x1f300, 0x1f320], [0x1f32d, 0x1f335],
  [0x1f337, 0x1f37c], [0x1f37e, 0x1f393], [0x1f3a0, 0x1f3ca], [0x1f3cf, 0x1f3d3],
  [0x1f3e0, 0x1f3f0], [0x1f3f4, 0x1f3f4], [0x1f3f8, 0x1f43e], [0x1f440, 0x1f440],
  [0x1f442, 0x1f4fc], [0x1f4ff, 0x1f53d], [0x1f54b, 0x1f54e], [0x1f550, 0x1f567],
  [0x1f57a, 0x1f57a], [0x1f595, 0x1f596], [0x1f5a4, 0x1f5a4], [0x1f5fb, 0x1f64f],
  [0x1f680, 0x1f6c5], [0x1f6cc, 0x1f6cc], [0x1f6d0, 0x1f6d2], [0x1f6eb, 0x1f6ec],
  [0x1f6f4, 0x1f6f8], [0x1f910, 0x1f93e], [0x1f940, 0x1f970], [0x1f973, 0x1f976],
  [0x1f97a, 0x1f9ff], [0x1fa70, 0x1faff], [0x20000, 0x2fffd], [0x30000, 0x3fffd],
];

/** Combining marks, format characters and the conjoining Hangul vowels and finals. */
const ZERO = /^[\p{Mn}\p{Me}\p{Cf}ᅠ-ᇿힰ-퟿]$/u;

export function cellWidth(char: string): 0 | 1 | 2 {
  const code = char.codePointAt(0) ?? 0;
  if (code < 0x300) return 1;
  if (ZERO.test(char)) return 0;
  let lo = 0;
  let hi = WIDE.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    const [first, last] = WIDE[mid] as readonly [number, number];
    if (code < first) hi = mid - 1;
    else if (code > last) lo = mid + 1;
    else return 2;
  }
  return 1;
}

/**
 * The string cut into what the cursor steps over: a base character with any zero-width marks
 * that follow it. The line editor's buffer is an array of these, so Left never lands between a
 * letter and its accent.
 */
export function clusters(text: string): string[] {
  const out: string[] = [];
  for (const char of text) {
    if (out.length > 0 && cellWidth(char) === 0) out[out.length - 1] += char;
    else out.push(char);
  }
  return out;
}

/** Cells a plain or coloured string takes on one line. */
export function width(text: string): number {
  let cells = 0;
  for (const char of stripAnsi(text)) cells += cellWidth(char);
  return cells;
}

/** Pads a plain or coloured string with spaces to `cells`, by the width it will draw at. */
export function pad(text: string, cells: number): string {
  return text + " ".repeat(Math.max(0, cells - width(text)));
}

export function padStart(text: string, cells: number): string {
  return " ".repeat(Math.max(0, cells - width(text))) + text;
}

/**
 * Names laid out in columns the way BSD `ls -C` does: down each column first, every column as
 * wide as the widest name rounded up to the next tab stop, as many columns as fit. A width too
 * narrow for two columns gives one name per line.
 */
export function columns(names: readonly string[], terminalWidth: number): string[] {
  if (names.length === 0) return [];
  const widest = Math.max(...names.map(width));
  const column = (widest + 8) & ~7;
  const count = Math.max(1, Math.floor(terminalWidth / column));
  if (count === 1) return [...names];
  const rows = Math.ceil(names.length / count);
  const lines: string[] = [];
  for (let row = 0; row < rows; row++) {
    let line = "";
    for (let col = 0; col < count; col++) {
      const name = names[col * rows + row];
      if (name === undefined) break;
      const last = (col + 1) * rows + row >= names.length;
      line += last ? name : pad(name, column);
    }
    lines.push(line);
  }
  return lines;
}

/** Thousands separated, as a count reads in prose. */
export function count(n: number): string {
  return n.toLocaleString("en-US");
}

/** A byte count the way `ls -lh` prints it: 4.0K, 12M, 1.1G. */
export function humanSize(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`;
  const units = ["K", "M", "G", "T"];
  let value = bytes / 1024;
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit++;
  }
  return `${value < 10 ? value.toFixed(1) : Math.round(value)}${units[unit]}`;
}
