/**
 * W31 G2 — does every transcendental in `src/wgsl/` evaluate inside f32?
 *
 * The class this answers is the tracker's "Nothing checks that a WGSL
 * transcendental's argument stays inside f32" (W30 G3b), whose instance was
 * `tanh` of a cubic in a distance measured in σ: nothing bounded the distance,
 * Metal lowers `tanh` through `exp(2t)`, f32's `exp` overflows at 88.72, and the
 * `Inf/Inf` that came back reached the composite's alpha and left a strip of a
 * 44 px surface undrawn (claims §5.159b). The fix was one clamp. What was still
 * missing is the property: **no argument of any of these functions may leave the
 * range on which the function is finite in f32**, for every input a document or
 * a scene can produce.
 *
 * ## What this module is, and what it deliberately is not
 *
 * It is an interval evaluator over the shader text. Given a call, it resolves
 * each argument's expression through `let`/`const` bindings, single-`return`
 * helper functions and the bounding builtins (`clamp`, `max`, `min`, `abs`,
 * `select`, `mix`, `saturate`, and the builtins whose own range is a fact —
 * `atan2`, `length`, `sqrt`, `cos`, `smoothstep`), does interval arithmetic over
 * `+ - * /`, and saturates everything it cannot resolve to the whole of f32.
 * Saturating is what makes the answer SOUND rather than optimistic: an argument
 * the evaluator cannot follow is treated as if it could be f32's largest value,
 * so the only way to pass is to be bounded by the source itself.
 *
 * It is not a WGSL compiler and it does not try to be. Where the bound is a fact
 * about a material leaf or a scene quantity rather than about the expression —
 * an exponent a document writes, a normal the field pass has already normalised
 * — no textual evaluator can see it, and the site belongs in the committed
 * range-proof table beside this file instead (`proofs.ts`), whose entries name
 * the bound, what it depends on, and what makes it hold over any value a fit
 * could produce.
 *
 * ## Why these functions
 *
 * `exp`, `exp2`, `pow`, `tanh`, `sinh`, `cosh`, `log`, `log2` are the named set:
 * every one of them either grows faster than any polynomial or has a pole, and
 * every one of them is lowered on some backend through `exp2`/`log2`, which is
 * the mechanism that produced §5.159b's NaN. `inverseSqrt` joins them for its
 * pole at zero — the package has no call of it today, and the rule is here so
 * that the first one is classified rather than waved through.
 *
 * **Bare division and `1.0/x` are NOT scanned, and that is a decision rather
 * than an omission.** Three reasons, in the order that decided it. (1) A divisor
 * that reaches zero returns `±Inf` from a finite numerator; only `0/0` returns
 * the NaN that travels through a multiply by zero into alpha, which is the
 * signature this class exists for. (2) `src/wgsl/` performs over a thousand
 * divisions and exactly ONE of them has a uniform as its immediate divisor
 * (`in.position.xy / ou.screen.xy`, the viewport's own size in device px, which
 * is ≥ 1 wherever a pass runs at all); every divisor a material leaf can reach
 * is already written `max(x, 1e-4)` or `max(x, 1e-6)` in the shader's own idiom.
 * A per-site rule over the other thousand would be a proof table the size of the
 * shader, and a table that size is one nobody re-reads. (3) The standing readback
 * guard catches the alpha-hole signature of a NaN however it was produced,
 * including from a division, which is the coverage a division rule would buy at a
 * fraction of its cost.
 */

import { readdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

export const WGSL_DIR = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "src", "wgsl");

/** The largest finite f32. Every interval here is saturated to ±this. */
export const F32_MAX = 3.4028234663852886e38;
/** `exp` overflows f32 above this: ln(F32_MAX). */
export const LN_F32_MAX = Math.log(F32_MAX);
/** `exp2` overflows f32 above this. */
export const LOG2_F32_MAX = 128;
/**
 * `tanh`'s own bound, and the reason it is not `Infinity`.
 *
 * `tanh` is mathematically bounded by 1 and could never overflow — but a backend
 * that lowers it to `(exp(2t) − 1)/(exp(2t) + 1)`, which is what Dawn emits on
 * Metal's fast-math path, overflows f32's `exp` at `2t > LN_F32_MAX` and hands
 * back `Inf/Inf`. §5.159b measured exactly that. So the bound this module holds
 * `tanh` to is the LOWERING's, not the function's.
 */
export const TANH_LOWERING_LIMIT = LN_F32_MAX / 2;

export const SCANNED_FUNCTIONS = [
  "exp2",
  "exp",
  "pow",
  "tanh",
  "sinh",
  "cosh",
  "log2",
  "log",
  "inverseSqrt",
] as const;

export type ScannedFunction = (typeof SCANNED_FUNCTIONS)[number];

export interface Interval {
  readonly lo: number;
  readonly hi: number;
}

export interface CallSite {
  /** File name within `src/wgsl/`, e.g. `optics.ts`. */
  readonly file: string;
  readonly fn: ScannedFunction;
  /** The call's own text, whitespace-normalised — the proof table's key. */
  readonly call: string;
  /** One entry per argument, each whitespace-normalised. */
  readonly args: readonly string[];
  /** The resolved interval of each argument, saturated to ±`F32_MAX`. */
  readonly ranges: readonly Interval[];
  /** 1-based line of the call in the UNSTRIPPED file, for a human. */
  readonly line: number;
}

export interface Verdict {
  /** Is the result finite in f32 over `ranges`? */
  readonly finite: boolean;
  /** Which argument indices are the reason it is not. Empty when it is. */
  readonly unbounded: readonly number[];
  readonly why: string;
}

// ---------------------------------------------------------------------------
// text
// ---------------------------------------------------------------------------

/**
 * Comments out, everything else kept at its own offset.
 *
 * Kept at offset rather than deleted so a call's line number survives, and
 * because this is the step that makes the scan honest: `optics.ts`'s own note on
 * the §5.159b fix contains the text `exp(2t)`, and a scanner that read comments
 * would classify a sentence. TypeScript and WGSL spell comments the same way, so
 * one pass covers the `.ts` wrapper and the shader inside it.
 */
export function stripComments(source: string): string {
  const out = source.split("");
  let index = 0;
  while (index < source.length) {
    const two = source.slice(index, index + 2);
    if (two === "//") {
      while (index < source.length && source[index] !== "\n") {
        out[index] = " ";
        index += 1;
      }
    } else if (two === "/*") {
      const end = source.indexOf("*/", index + 2);
      const stop = end === -1 ? source.length : end + 2;
      for (let i = index; i < stop; i += 1) if (source[i] !== "\n") out[i] = " ";
      index = stop;
    } else {
      index += 1;
    }
  }
  return out.join("");
}

const norm = (text: string): string => text.replace(/\s+/g, " ").trim();

/** The index just past the `)` matching the `(` at `open`. */
function matchParen(source: string, open: number): number {
  let depth = 0;
  for (let i = open; i < source.length; i += 1) {
    if (source[i] === "(") depth += 1;
    else if (source[i] === ")") {
      depth -= 1;
      if (depth === 0) return i + 1;
    }
  }
  return -1;
}

/** Split an argument list on commas that are not inside brackets. */
function splitArgs(inner: string): string[] {
  const out: string[] = [];
  let depth = 0;
  let start = 0;
  for (let i = 0; i < inner.length; i += 1) {
    const c = inner[i];
    if (c === "(" || c === "[" || c === "<") depth += 1;
    else if (c === ")" || c === "]" || c === ">") depth -= 1;
    else if (c === "," && depth === 0) {
      out.push(inner.slice(start, i));
      start = i + 1;
    }
  }
  const tail = inner.slice(start);
  if (out.length > 0 || tail.trim() !== "") out.push(tail);
  return out.map(norm);
}

// ---------------------------------------------------------------------------
// interval arithmetic, saturated at f32's own extremes
// ---------------------------------------------------------------------------

const FULL: Interval = { lo: -F32_MAX, hi: F32_MAX };

const sat = (value: number): number =>
  Number.isNaN(value) ? 0 : Math.max(-F32_MAX, Math.min(F32_MAX, value));

const span = (lo: number, hi: number): Interval => ({ lo: sat(Math.min(lo, hi)), hi: sat(Math.max(lo, hi)) });

const hull = (a: Interval, b: Interval): Interval => span(Math.min(a.lo, b.lo), Math.max(a.hi, b.hi));

const corners = (a: Interval, b: Interval, op: (x: number, y: number) => number): Interval => {
  const values = [op(a.lo, b.lo), op(a.lo, b.hi), op(a.hi, b.lo), op(a.hi, b.hi)].filter(
    (v) => !Number.isNaN(v),
  );
  if (values.length === 0) return FULL;
  return span(Math.min(...values), Math.max(...values));
};

const add = (a: Interval, b: Interval): Interval => span(a.lo + b.lo, a.hi + b.hi);
const sub = (a: Interval, b: Interval): Interval => span(a.lo - b.hi, a.hi - b.lo);
const mul = (a: Interval, b: Interval): Interval => corners(a, b, (x, y) => x * y);

const div = (a: Interval, b: Interval): Interval => {
  // A divisor straddling zero gives no bound at all. Saying so is the point:
  // the alternative is a bound that is not one.
  if (b.lo <= 0 && b.hi >= 0) return FULL;
  return corners(a, b, (x, y) => x / y);
};

/** `x * x` for the same `x`: non-negative however little is known about `x`. */
const square = (a: Interval): Interval => {
  const magnitudes = [Math.abs(a.lo), Math.abs(a.hi)];
  const hi = Math.max(...magnitudes) ** 2;
  const lo = a.lo <= 0 && a.hi >= 0 ? 0 : Math.min(...magnitudes) ** 2;
  return span(lo, hi);
};

const absInterval = (a: Interval): Interval => {
  const magnitudes = [Math.abs(a.lo), Math.abs(a.hi)];
  const hi = Math.max(...magnitudes);
  const lo = a.lo <= 0 && a.hi >= 0 ? 0 : Math.min(...magnitudes);
  return span(lo, hi);
};

// ---------------------------------------------------------------------------
// the evaluator
// ---------------------------------------------------------------------------

/**
 * Builtins whose range is a fact about the function rather than about its
 * argument. Each one here is a bound the WGSL spec gives, not an assumption.
 */
const BUILTIN_RANGE: Readonly<Record<string, Interval>> = {
  atan2: { lo: -Math.PI, hi: Math.PI },
  atan: { lo: -Math.PI / 2, hi: Math.PI / 2 },
  asin: { lo: -Math.PI / 2, hi: Math.PI / 2 },
  acos: { lo: 0, hi: Math.PI },
  sin: { lo: -1, hi: 1 },
  cos: { lo: -1, hi: 1 },
  tanh: { lo: -1, hi: 1 },
  sign: { lo: -1, hi: 1 },
  fract: { lo: 0, hi: 1 },
  step: { lo: 0, hi: 1 },
  smoothstep: { lo: 0, hi: 1 },
  saturate: { lo: 0, hi: 1 },
  length: { lo: 0, hi: F32_MAX },
  distance: { lo: 0, hi: F32_MAX },
  sqrt: { lo: 0, hi: F32_MAX },
  exp: { lo: 0, hi: F32_MAX },
  exp2: { lo: 0, hi: F32_MAX },
};

interface Context {
  /** Innermost scope first; each is a block of WGSL text to look declarations up in. */
  readonly scopes: readonly string[];
  readonly file: string;
  readonly depth: number;
  readonly seen: ReadonlySet<string>;
}

/** The right-hand side of `let|const|var <name> = …;` in `scope`, or undefined. */
function declarationOf(scope: string, name: string): { rhs: string; kind: string } | undefined {
  const pattern = new RegExp(
    String.raw`(?:^|[^\w.])(let|const|var)\s+${name}\s*(?::[^=;]*)?=\s*`,
    "m",
  );
  const found = pattern.exec(scope);
  if (found === null) return undefined;
  const start = found.index + found[0].length;
  let depth = 0;
  for (let i = start; i < scope.length; i += 1) {
    const c = scope[i];
    if (c === "(" || c === "[" || c === "{") depth += 1;
    else if (c === ")" || c === "]" || c === "}") depth -= 1;
    else if (c === ";" && depth === 0) {
      return { rhs: norm(scope.slice(start, i)), kind: found[1] as string };
    }
  }
  return undefined;
}

/** Is `name` assigned again after its declaration? A reassigned `var` is not its initialiser. */
function reassigned(scope: string, name: string): boolean {
  const pattern = new RegExp(String.raw`(?:^|[^\w.])${name}\s*(?:=[^=]|\+=|-=|\*=|/=)`, "g");
  let count = 0;
  while (pattern.exec(scope) !== null) count += 1;
  // One hit is the declaration itself.
  return count > 1;
}

/**
 * The body of the innermost `fn … { … }` containing `index`.
 *
 * Resolution has to be scoped: `optics.ts` declares a `let t` in `rim_weight`
 * and another in `outer_shadow_falloff`, and a file-wide lookup would answer the
 * second call with the first binding — or, worse, see two and decide the name
 * was reassigned. The enclosing body is the innermost scope; the file follows it,
 * for module-level `const`s like `TAU`.
 */
function enclosingBody(source: string, index: number): string | undefined {
  let best: { body: string; size: number } | undefined;
  const heads = [...source.matchAll(/(?:^|[^\w.])fn\s+\w+\s*\(/g)];
  for (const head of heads) {
    const open = source.indexOf("(", head.index ?? 0);
    const afterArgs = matchParen(source, open);
    if (afterArgs === -1) continue;
    const brace = source.indexOf("{", afterArgs);
    if (brace === -1) continue;
    let depth = 0;
    let end = -1;
    for (let i = brace; i < source.length; i += 1) {
      if (source[i] === "{") depth += 1;
      else if (source[i] === "}") {
        depth -= 1;
        if (depth === 0) {
          end = i;
          break;
        }
      }
    }
    if (end === -1 || index < brace || index > end) continue;
    const size = end - brace;
    if (best === undefined || size < best.size) best = { body: source.slice(brace + 1, end), size };
  }
  return best?.body;
}

/** A single-`return` helper's returned expression, plus its body as a scope. */
function returnOf(scope: string, name: string): { expr: string; body: string } | undefined {
  const head = new RegExp(String.raw`(?:^|[^\w.])fn\s+${name}\s*\(`, "m").exec(scope);
  if (head === null) return undefined;
  const open = scope.indexOf("(", head.index);
  const afterArgs = matchParen(scope, open);
  const brace = scope.indexOf("{", afterArgs);
  if (brace === -1) return undefined;
  let depth = 0;
  let end = -1;
  for (let i = brace; i < scope.length; i += 1) {
    if (scope[i] === "{") depth += 1;
    else if (scope[i] === "}") {
      depth -= 1;
      if (depth === 0) {
        end = i;
        break;
      }
    }
  }
  if (end === -1) return undefined;
  const body = scope.slice(brace + 1, end);
  const returns = [...body.matchAll(/(?:^|[^\w.])return\s+/g)];
  if (returns.length !== 1) return undefined;
  const first = returns[0] as RegExpMatchArray;
  const start = (first.index ?? 0) + first[0].length;
  const semi = body.indexOf(";", start);
  if (semi === -1) return undefined;
  return { expr: norm(body.slice(start, semi)), body };
}

/** Resolve one expression to an interval. Anything unresolvable is the whole of f32. */
export function evaluate(expression: string, context: Context): Interval {
  if (context.depth > 12) return FULL;
  const text = norm(expression);
  if (text === "") return FULL;
  return parseExpr({ text, index: 0 }, context);
}

interface Cursor {
  readonly text: string;
  index: number;
}

const skip = (cursor: Cursor): void => {
  while (cursor.index < cursor.text.length && cursor.text[cursor.index] === " ") cursor.index += 1;
};

function parseExpr(cursor: Cursor, context: Context): Interval {
  let value = parseTerm(cursor, context);
  for (;;) {
    skip(cursor);
    const c = cursor.text[cursor.index];
    if (c !== "+" && c !== "-") return value;
    cursor.index += 1;
    const right = parseTerm(cursor, context);
    value = c === "+" ? add(value, right) : sub(value, right);
  }
}

function parseTerm(cursor: Cursor, context: Context): Interval {
  const firstStart = cursor.index;
  let value = parseUnary(cursor, context);
  let leftText = norm(cursor.text.slice(firstStart, cursor.index));
  for (;;) {
    skip(cursor);
    const c = cursor.text[cursor.index];
    if (c !== "*" && c !== "/") return value;
    cursor.index += 1;
    const start = cursor.index;
    const right = parseUnary(cursor, context);
    const rightText = norm(cursor.text.slice(start, cursor.index));
    // `x * x` is a square whatever `x` is; that is the only structural fact
    // interval arithmetic cannot recover on its own, and `backdrop.ts`'s
    // Gaussian weight needs exactly it.
    if (c === "*" && leftText !== "" && leftText === rightText) value = square(value);
    else value = c === "*" ? mul(value, right) : div(value, right);
    leftText = rightText;
  }
}

function parseUnary(cursor: Cursor, context: Context): Interval {
  skip(cursor);
  const c = cursor.text[cursor.index];
  if (c === "-") {
    cursor.index += 1;
    const inner = parseUnary(cursor, context);
    return span(-inner.hi, -inner.lo);
  }
  if (c === "+") {
    cursor.index += 1;
    return parseUnary(cursor, context);
  }
  return parsePrimary(cursor, context);
}

function parsePrimary(cursor: Cursor, context: Context): Interval {
  skip(cursor);
  const rest = cursor.text.slice(cursor.index);

  const number = /^[0-9]+(?:\.[0-9]*)?(?:[eE][-+]?[0-9]+)?[fh]?|^\.[0-9]+(?:[eE][-+]?[0-9]+)?[fh]?/.exec(rest);
  if (number !== null) {
    cursor.index += number[0].length;
    return span(Number.parseFloat(number[0]), Number.parseFloat(number[0]));
  }

  if (rest.startsWith("(")) {
    const close = matchParen(cursor.text, cursor.index);
    const inner = cursor.text.slice(cursor.index + 1, close - 1);
    cursor.index = close;
    return evaluate(inner, { ...context, depth: context.depth + 1 });
  }

  const identifier = /^[A-Za-z_][\w]*(?:\s*\.\s*[\w]+)*/.exec(rest);
  if (identifier === null) {
    // An operator or a token this evaluator has no rule for: consume one
    // character so the parse terminates, and give up soundly.
    cursor.index += 1;
    return FULL;
  }
  cursor.index += identifier[0].length;
  const path = identifier[0].replace(/\s+/g, "");
  skip(cursor);

  if (cursor.text[cursor.index] === "(") {
    const close = matchParen(cursor.text, cursor.index);
    const args = splitArgs(cursor.text.slice(cursor.index + 1, close - 1));
    cursor.index = close;
    return callRange(path, args, context);
  }

  // A member of a uniform block or a texture read is a free variable.
  if (path.includes(".")) return FULL;
  return identifierRange(path, context);
}

function identifierRange(name: string, context: Context): Interval {
  if (context.seen.has(name)) return FULL;
  for (const scope of context.scopes) {
    const declaration = declarationOf(scope, name);
    if (declaration === undefined) continue;
    if (declaration.kind === "var" && reassigned(scope, name)) return FULL;
    return evaluate(declaration.rhs, {
      ...context,
      depth: context.depth + 1,
      seen: new Set([...context.seen, name]),
    });
  }
  return FULL;
}

function callRange(name: string, args: readonly string[], context: Context): Interval {
  const next = { ...context, depth: context.depth + 1 };
  const at = (index: number): Interval =>
    index < args.length ? evaluate(args[index] as string, next) : FULL;

  // A vector or scalar constructor over one component-wise expression is that
  // expression; over several, the hull of them.
  if (/^(?:vec[234]f|vec[234]<f32>|f32|bitcast<f32>)$/.test(name)) {
    if (args.length === 0) return span(0, 0);
    return args.map((_, index) => at(index)).reduce(hull);
  }

  switch (name) {
    case "clamp": {
      // The result is inside [low, high] whatever the first argument is, which
      // is the whole reason a clamp is the fix for this class.
      const low = at(1);
      const high = at(2);
      return span(low.lo, high.hi);
    }
    case "max": {
      const a = at(0);
      const b = at(1);
      return span(Math.max(a.lo, b.lo), Math.max(a.hi, b.hi));
    }
    case "min": {
      const a = at(0);
      const b = at(1);
      return span(Math.min(a.lo, b.lo), Math.min(a.hi, b.hi));
    }
    case "abs":
      return absInterval(at(0));
    case "select":
      return hull(at(0), at(1));
    case "mix": {
      const t = at(2);
      return t.lo >= 0 && t.hi <= 1 ? hull(at(0), at(1)) : FULL;
    }
    case "pow": {
      const base = at(0);
      const exponent = at(1);
      return powRange(base, exponent);
    }
    default:
      break;
  }

  const builtin = BUILTIN_RANGE[name];
  if (builtin !== undefined) return builtin;

  // A helper in this file with exactly one `return`: follow it, with its own
  // body as the innermost scope.
  if (!context.seen.has(`fn:${name}`)) {
    for (const scope of context.scopes) {
      const found = returnOf(scope, name);
      if (found === undefined) continue;
      return evaluate(found.expr, {
        ...context,
        scopes: [found.body, ...context.scopes],
        depth: context.depth + 1,
        seen: new Set([...context.seen, `fn:${name}`]),
      });
    }
  }
  return FULL;
}

/** `b ** e` over intervals, saturated — used both as a range and as a verdict. */
function powRange(base: Interval, exponent: Interval): Interval {
  if (base.lo < 0) return FULL;
  const values: number[] = [];
  for (const b of [base.lo, base.hi]) {
    for (const e of [exponent.lo, exponent.hi]) {
      const value = b ** e;
      if (Number.isFinite(value)) values.push(value);
      else return FULL;
    }
  }
  return span(Math.min(...values), Math.max(...values));
}

// ---------------------------------------------------------------------------
// the verdict
// ---------------------------------------------------------------------------

const fmt = (interval: Interval): string =>
  `[${interval.lo === -F32_MAX ? "-f32max" : interval.lo.toPrecision(6)}, ` +
  `${interval.hi === F32_MAX ? "f32max" : interval.hi.toPrecision(6)}]`;

export function verdictFor(fn: ScannedFunction, ranges: readonly Interval[]): Verdict {
  const argument = (ranges[0] ?? FULL) as Interval;
  const magnitude = Math.max(Math.abs(argument.lo), Math.abs(argument.hi));
  const ok = (why: string): Verdict => ({ finite: true, unbounded: [], why });
  const no = (unbounded: readonly number[], why: string): Verdict => ({ finite: false, unbounded, why });

  switch (fn) {
    case "exp":
      return argument.hi <= LN_F32_MAX
        ? ok(`argument ${fmt(argument)} is at or under ln(f32max) = ${LN_F32_MAX.toFixed(5)}`)
        : no([0], `argument ${fmt(argument)} exceeds ln(f32max) = ${LN_F32_MAX.toFixed(5)}`);
    case "exp2":
      return argument.hi <= LOG2_F32_MAX
        ? ok(`argument ${fmt(argument)} is at or under log2(f32max) = 128`)
        : no([0], `argument ${fmt(argument)} exceeds log2(f32max) = 128`);
    case "log":
    case "log2":
    case "inverseSqrt":
      return argument.lo > 0
        ? ok(`argument ${fmt(argument)} is strictly positive`)
        : no([0], `argument ${fmt(argument)} reaches zero or below, where ${fn} has its pole`);
    case "sinh":
    case "cosh":
      return magnitude <= LN_F32_MAX
        ? ok(`argument ${fmt(argument)} is within ±ln(f32max)`)
        : no([0], `argument ${fmt(argument)} leaves ±ln(f32max) = ${LN_F32_MAX.toFixed(5)}`);
    case "tanh":
      return magnitude <= TANH_LOWERING_LIMIT
        ? ok(
            `argument ${fmt(argument)} is within ±ln(f32max)/2 = ${TANH_LOWERING_LIMIT.toFixed(5)}, ` +
              `where the exp(2t) lowering stays finite (claims §5.159b)`,
          )
        : no(
            [0],
            `argument ${fmt(argument)} leaves ±${TANH_LOWERING_LIMIT.toFixed(5)}, where a backend ` +
              `that lowers tanh through exp(2t) returns Inf/Inf (claims §5.159b)`,
          );
    case "pow": {
      const base = argument;
      const exponent = (ranges[1] ?? FULL) as Interval;
      if (base.lo < 0) {
        return no([0], `base ${fmt(base)} reaches below zero, where WGSL leaves pow undefined`);
      }
      if (base.lo === 0 && exponent.lo <= 0) {
        // Either end can carry the fix: a base floored above zero, or an
        // exponent held above it. Name the one the source left free, so the
        // proof table is keyed where the bound actually has to come from.
        return no(
          exponent.lo === -F32_MAX ? [1] : [0],
          `base ${fmt(base)} reaches zero while the exponent ${fmt(exponent)} reaches zero or ` +
            `below: pow(0, e) is exp2(e · log2(0)), which is 0 only for e > 0`,
        );
      }
      const result = powRange(base, exponent);
      return result.hi < F32_MAX
        ? ok(`base ${fmt(base)} to exponent ${fmt(exponent)} is ${fmt(result)}`)
        : no(
            base.hi === F32_MAX ? [0] : [1],
            `base ${fmt(base)} to exponent ${fmt(exponent)} is not bounded inside f32`,
          );
    }
    default:
      return no([0], `no rule for ${fn as string}`);
  }
}

// ---------------------------------------------------------------------------
// the scan
// ---------------------------------------------------------------------------

const CALL = new RegExp(String.raw`(?<![\w.])(${SCANNED_FUNCTIONS.join("|")})\s*\(`, "g");

export function scanSource(file: string, source: string): CallSite[] {
  const stripped = stripComments(source);
  const out: CallSite[] = [];
  CALL.lastIndex = 0;
  for (;;) {
    const found = CALL.exec(stripped);
    if (found === null) break;
    const open = stripped.indexOf("(", found.index);
    const close = matchParen(stripped, open);
    if (close === -1) continue;
    const args = splitArgs(stripped.slice(open + 1, close - 1));
    const body = enclosingBody(stripped, found.index);
    const context: Context = {
      scopes: body === undefined ? [stripped] : [body, stripped],
      file,
      depth: 0,
      seen: new Set(),
    };
    out.push({
      file,
      fn: found[1] as ScannedFunction,
      call: norm(stripped.slice(found.index, close)),
      args,
      ranges: args.map((argument) => evaluate(argument, context)),
      line: stripped.slice(0, found.index).split("\n").length,
    });
  }
  return out;
}

/** Every call site in every file under `src/wgsl/`, in file then source order. */
export function scanWgslDirectory(directory: string = WGSL_DIR): CallSite[] {
  const files = readdirSync(directory)
    .filter((name) => name.endsWith(".ts"))
    .sort();
  return files.flatMap((file) => scanSource(file, readFileSync(join(directory, file), "utf8")));
}

export const describeInterval = fmt;
