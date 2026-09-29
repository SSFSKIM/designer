/**
 * The line editor: the buffer being typed after the prompt, and the escape sequences that keep
 * the terminal's picture of it true.
 *
 * It owns a region of the screen that starts at the prompt's first cell and runs as many rows as
 * the prompt and the buffer wrap to. Every edit redraws that region whole — up to its first row,
 * erase below, prompt and buffer, then the cursor placed — because a partial redraw has to know
 * where each wrapped row starts, and by then it has done the same arithmetic a full one does. The
 * arithmetic is the terminal's own: a character that does not fit in what is left of a row starts
 * the next one (so a wide character never straddles the edge), and a row filled to its last cell
 * leaves the cursor pending there until something is written. The editor resolves that with a
 * space and a backspace, zsh's own trick, which wraps onto the next row as a continuation of the
 * same line rather than a new one.
 *
 * That matters on resize, because of what xterm does then (measured on the installed xterm, not
 * assumed): it reflows every wrapped line except the one the cursor is in, which keeps its rows —
 * widening joins nothing and narrowing truncates rather than wraps. So the region's rows, and the
 * cursor's row within them, survive a resize exactly, and the editor redraws at the new width from
 * the same counters. An explicit new line would have split the region into two lines, and the
 * first would reflow on its own. Cursor-up stops at the screen's top row and cannot enter the
 * scrollback, so the editor keeps the region's first row on the screen: typing stops at the
 * terminal's last row, and a line that is taller anyway (a shrunk window, a recalled line) is
 * drawn from a cleared screen's top, as Ctrl-L does, without losing a character of it.
 *
 * Nothing here writes: each method returns the text to write, and the shell writes it.
 */

import { cellWidth, clusters, stripAnsi } from "./ansi";

interface Position {
  readonly row: number;
  readonly col: number;
}

export class LineEditor {
  private chars: string[] = [];
  private cursor = 0;
  private prompt = "";
  private promptCells: number[] = [];
  /** Rows between the region's first row and the one the terminal cursor is on now. */
  private cursorRow = 0;
  /** The terminal cursor's column, when the editor knows it. */
  private cursorCol: number | undefined;
  /** Whether the region was drawn and is still the one the next redraw replaces. */
  private active = false;

  private columns: number;
  private rows: number;

  constructor(columns: number, rows: number) {
    this.columns = columns;
    this.rows = rows;
  }

  /** Starts a new line at the terminal's current row, which must be at column 0. */
  begin(prompt: string, text = "", cursor?: number): string {
    this.prompt = prompt;
    this.promptCells = [...stripAnsi(prompt)].map(cellWidth);
    this.setText(text, cursor);
    this.cursorRow = 0;
    this.cursorCol = undefined;
    this.active = true;
    return this.render();
  }

  get text(): string {
    return this.chars.join("");
  }

  /** The buffer to the left of the cursor, which completion reads. */
  get beforeCursor(): string {
    return this.chars.slice(0, this.cursor).join("");
  }

  get isActive(): boolean {
    return this.active;
  }

  get isEmpty(): boolean {
    return this.chars.length === 0;
  }

  setText(text: string, cursor?: number): void {
    this.chars = clusters(text);
    this.cursor = Math.min(this.chars.length, cursor ?? this.chars.length);
  }

  insert(text: string): void {
    const added = clusters(text);
    if (added.length === 0) return;
    // A combining mark typed on its own belongs to the character before the cursor.
    if (cellWidth(added[0] as string) === 0 && this.cursor > 0) {
      this.chars[this.cursor - 1] += added.shift() as string;
    }
    this.chars.splice(this.cursor, 0, ...added);
    this.cursor += added.length;
    this.fit(added.length);
  }

  /** Replaces the clusters from `from` to the cursor with `text`, as completion does. */
  replaceBeforeCursor(from: number, text: string): void {
    const added = clusters(text);
    const before = this.chars.length;
    this.chars.splice(from, this.cursor - from, ...added);
    this.cursor = from + added.length;
    this.fit(Math.max(0, this.chars.length - before));
  }

  /**
   * Refuses what typing or a paste would put past the terminal's last row, the way a full field
   * takes no more. Only new text is cut: a line that is already taller than the screen (recalled
   * from history, or kept through a resize that shrank the screen) keeps every character and is
   * drawn in the overflow mode `render` describes.
   */
  private fit(added: number): void {
    const fits = (): boolean => this.rows < 1 || this.endRow() < this.rows;
    if (added === 0 || fits()) return;
    // Keep as many of the clusters just inserted before the cursor as still fit.
    const inserted = this.chars.splice(this.cursor - added, added);
    this.cursor -= added;
    let lo = 0;
    let hi = added;
    while (lo < hi) {
      const mid = (lo + hi + 1) >> 1;
      this.chars.splice(this.cursor, 0, ...inserted.slice(0, mid));
      const ok = fits();
      this.chars.splice(this.cursor, mid);
      if (ok) lo = mid;
      else hi = mid - 1;
    }
    this.chars.splice(this.cursor, 0, ...inserted.slice(0, lo));
    this.cursor += lo;
  }

  private endRow(): number {
    return (this.layout().at(-1) as Position).row;
  }

  /** Where the word the cursor is in (or just after) starts, in clusters. */
  wordStart(): number {
    let at = this.cursor;
    while (at > 0 && this.isSpace(at - 1)) at--;
    while (at > 0 && !this.isSpace(at - 1)) at--;
    return at;
  }

  private wordEnd(): number {
    let at = this.cursor;
    while (at < this.chars.length && this.isSpace(at)) at++;
    while (at < this.chars.length && !this.isSpace(at)) at++;
    return at;
  }

  private isSpace(index: number): boolean {
    return /\s/.test(this.chars[index] ?? "");
  }

  backspace(): boolean {
    if (this.cursor === 0) return false;
    this.chars.splice(--this.cursor, 1);
    return true;
  }

  deleteForward(): boolean {
    if (this.cursor >= this.chars.length) return false;
    this.chars.splice(this.cursor, 1);
    return true;
  }

  left(): boolean {
    if (this.cursor === 0) return false;
    this.cursor--;
    return true;
  }

  right(): boolean {
    if (this.cursor >= this.chars.length) return false;
    this.cursor++;
    return true;
  }

  home(): boolean {
    const moved = this.cursor !== 0;
    this.cursor = 0;
    return moved;
  }

  end(): boolean {
    const moved = this.cursor !== this.chars.length;
    this.cursor = this.chars.length;
    return moved;
  }

  wordLeft(): boolean {
    const to = this.wordStart();
    const moved = to !== this.cursor;
    this.cursor = to;
    return moved;
  }

  wordRight(): boolean {
    const to = this.wordEnd();
    const moved = to !== this.cursor;
    this.cursor = to;
    return moved;
  }

  /** Removes and returns the text between the cursor and `to`, either side of it. */
  kill(to: "start" | "end" | "word-back" | "word-forward"): string {
    const targets = {
      start: () => 0,
      end: () => this.chars.length,
      "word-back": () => this.wordStart(),
      "word-forward": () => this.wordEnd(),
    };
    const target = targets[to]();
    const from = Math.min(target, this.cursor);
    const removed = this.chars.splice(from, Math.abs(target - this.cursor));
    this.cursor = from;
    return removed.join("");
  }

  /**
   * Where each cell-run lands: the position before every prompt and buffer cluster, and after the
   * last. A cluster that does not fit in the rest of its row starts the next one.
   */
  private layout(): Position[] {
    const widths = [...this.promptCells, ...this.chars.map((c) => cellWidth([...c][0] ?? " "))];
    const positions: Position[] = [];
    let row = 0;
    let col = 0;
    for (const w of widths) {
      if (col + w > this.columns) {
        row++;
        col = 0;
      }
      positions.push({ row, col });
      col += w;
    }
    // A row filled to its last cell: the next character, and so the cursor, is on the next row.
    positions.push(col >= this.columns ? { row: row + 1, col: 0 } : { row, col });
    return positions;
  }

  private moveTo(from: number, to: Position): string {
    if (from === to.row && this.cursorCol === to.col) return "";
    let out = "";
    if (from > to.row) out += `\x1b[${from - to.row}A`;
    else if (from < to.row) out += `\x1b[${to.row - from}B`;
    out += "\r";
    if (to.col > 0) out += `\x1b[${to.col}C`;
    this.cursorRow = to.row;
    this.cursorCol = to.col;
    return out;
  }

  /**
   * The whole region redrawn, the cursor left where the buffer's cursor is. A region taller than
   * the screen cannot be reached by cursor-up, so it is drawn from a cleared screen's top every
   * time, and the cursor goes no higher than the screen's first row.
   */
  render(): string {
    if (!this.active) return "";
    const positions = this.layout();
    const end = positions[positions.length - 1] as Position;
    if (this.rows > 0 && end.row >= this.rows) {
      let out = "\x1b[H\x1b[2J" + this.prompt + this.chars.join("");
      if (end.col === 0) out += " \b";
      const target = positions[this.promptCells.length + this.cursor] as Position;
      const top = end.row - (this.rows - 1);
      const row = Math.max(target.row, top);
      this.cursorRow = end.row;
      this.cursorCol = end.col;
      return out + this.moveTo(end.row, { row, col: row === target.row ? target.col : 0 });
    }
    let out = this.cursorRow > 0 ? `\x1b[${this.cursorRow}A` : "";
    out += "\r\x1b[J" + this.prompt + this.chars.join("");
    // Resolve a pending wrap onto the next row, as a continuation of this line.
    if (end.col === 0 && end.row > 0) out += " \b";
    this.cursorRow = end.row;
    this.cursorCol = end.col;
    const target = positions[this.promptCells.length + this.cursor] as Position;
    return out + this.moveTo(end.row, target);
  }

  /**
   * Leaves the region: the cursor to the end of the buffer, then a new line, so what follows
   * starts below everything typed. `suffix` is written at the end of the buffer first (`^C`).
   */
  finish(suffix = ""): string {
    if (!this.active) return "";
    const positions = this.layout();
    const end = positions[positions.length - 1] as Position;
    const out = this.moveTo(this.cursorRow, end) + suffix;
    this.active = false;
    // When the buffer filled its last row, the end is already the start of a fresh row, still
    // marked as this line's continuation; erasing it from its first cell ends the line there.
    return end.col === 0 && end.row > 0 && suffix === "" ? `${out}\x1b[K` : `${out}\r\n`;
  }

  /** The region after the screen was cleared: it now starts on the top row. */
  redrawAtTop(): string {
    this.cursorRow = 0;
    this.cursorCol = undefined;
    return this.render();
  }

  /**
   * Follows a new terminal size, and returns the redraw it needs. The region kept its rows through
   * the resize (the header says why), so the counters still say where its first row is — unless
   * the terminal lost rows and pushed that row into the scrollback, in which case the screen is
   * cleared and the line drawn from the top.
   */
  resize(columns: number, rows: number): string {
    const changed = columns !== this.columns || rows !== this.rows;
    this.columns = columns;
    this.rows = rows;
    if (!this.active || !changed) return "";
    this.cursorCol = undefined;
    if (this.rows > 0 && this.cursorRow >= this.rows) return "\x1b[H\x1b[2J" + this.redrawAtTop();
    return this.render();
  }
}
