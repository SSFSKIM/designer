/**
 * The command line's grammar: the part of zsh a person types without thinking about it.
 *
 * Words split on blanks; single quotes are literal; double quotes keep blanks and still expand
 * `$NAME`, `${NAME}` and `$?`; a backslash escapes the next character; `~` at the start of a word
 * is the home directory. An unquoted `*` or `?` makes a word a pattern the shell expands against
 * the snapshot. Commands join with `|`, and pipelines with `;`, `&&` and `||`. A redirect keeps
 * the stream it names (`>` and `1>` standard output, `2>` standard error, `&>` both), so the shell
 * can silence the right one for `/dev/null` and refuse every other target (the filesystem is
 * read-only); a descriptor duplicate like `2>&1` writes nothing anywhere and is dropped. What the
 * grammar does not carry (command substitution, background jobs, input redirection) is a parse
 * error that says so, never a silent misreading.
 *
 * A variable is kept as a reference in the parsed word and read only when its pipeline runs, so
 * `cd ~; echo $PWD` prints the directory `cd` went to, as it does in zsh. Its value is taken
 * literally, neither split nor globbed, which is zsh's default too.
 */

/** A run of literal text, or a variable read when the word is expanded. */
export type Part =
  | { readonly text: string; readonly wild: readonly boolean[] }
  | { readonly variable: string };

export interface Word {
  readonly parts: readonly Part[];
}

/** A word with its variables read: its text, and which of its UTF-16 units are wildcards. */
export interface Expanded {
  readonly text: string;
  /** Undefined when the word has no unquoted wildcard and is not a pattern. */
  readonly wild: readonly boolean[] | undefined;
}

export interface Redirect {
  /** Which stream goes to the target: standard output, standard error, or both. */
  readonly stream: "out" | "err" | "both";
  readonly target: Word;
}

export interface Command {
  readonly words: readonly Word[];
  readonly redirects: readonly Redirect[];
}

export interface Pipeline {
  /** How this pipeline joins the one before it; the first's is ";". */
  readonly join: ";" | "&&" | "||";
  readonly commands: readonly Command[];
}

export type Parsed =
  | { readonly ok: true; readonly pipelines: readonly Pipeline[] }
  | { readonly ok: false; readonly error: string };

type Token =
  | { readonly kind: "word"; readonly word: Word }
  | { readonly kind: "op"; readonly op: "|" | ";" | "&&" | "||" }
  | { readonly kind: "redirect"; readonly redirect: Redirect };

const NAME = /[A-Za-z_][A-Za-z0-9_]*/y;

function tokenize(line: string, home: string): Token[] | string {
  const tokens: Token[] = [];
  let parts: Part[] = [];
  let started = false;
  /** The stream of a redirect whose target is the next word. */
  let pendingRedirect: Redirect["stream"] | undefined;

  const push = (text: string, wild = false): void => {
    const last = parts[parts.length - 1];
    const marks = Array.from({ length: text.length }, () => wild);
    if (last !== undefined && "text" in last) {
      parts[parts.length - 1] = { text: last.text + text, wild: [...last.wild, ...marks] };
    } else parts.push({ text, wild: marks });
    started = true;
  };
  const end = (): void => {
    if (!started) return;
    const word: Word = { parts };
    if (pendingRedirect !== undefined) {
      tokens.push({ kind: "redirect", redirect: { stream: pendingRedirect, target: word } });
      pendingRedirect = undefined;
    } else tokens.push({ kind: "word", word });
    parts = [];
    started = false;
  };
  /** The variable at `line[at]` (a `$`), and where the text after it resumes. */
  const variable = (at: number): [Part, number] | string => {
    const next = line[at + 1];
    if (next === "?") return [{ variable: "?" }, at + 2];
    if (next === "(") return "command substitution is not simulated here";
    if (next === "{") {
      const close = line.indexOf("}", at + 2);
      if (close < 0) return "bad substitution";
      return [{ variable: line.slice(at + 2, close) }, close + 1];
    }
    NAME.lastIndex = at + 1;
    const match = NAME.exec(line);
    if (match === null) return [{ text: "$", wild: [false] }, at + 1];
    return [{ variable: match[0] }, at + 1 + match[0].length];
  };
  const pushVariable = (at: number): number | string => {
    const found = variable(at);
    if (typeof found === "string") return found;
    const [part, next] = found;
    if ("text" in part) push(part.text);
    else parts.push(part);
    started = true;
    return next;
  };

  let i = 0;
  while (i < line.length) {
    const c = line[i] as string;
    if (c === " " || c === "\t") {
      end();
      i++;
    } else if (c === "\\") {
      if (i + 1 < line.length) push(line[i + 1] as string);
      i += 2;
    } else if (c === "'") {
      const close = line.indexOf("'", i + 1);
      if (close < 0) return "unmatched '";
      push(line.slice(i + 1, close));
      i = close + 1;
    } else if (c === '"') {
      started = true;
      i++;
      while (i < line.length && line[i] !== '"') {
        const d = line[i] as string;
        if (d === "\\" && i + 1 < line.length && '"\\$`'.includes(line[i + 1] as string)) {
          push(line[i + 1] as string);
          i += 2;
        } else if (d === "$") {
          const next = pushVariable(i);
          if (typeof next === "string") return next;
          i = next;
        } else {
          push(d);
          i++;
        }
      }
      if (i >= line.length) return 'unmatched "';
      i++;
    } else if (c === "$") {
      const next = pushVariable(i);
      if (typeof next === "string") return next;
      i = next;
    } else if (c === "~" && !started && /^([/\s;|&<>]|$)/.test(line.slice(i + 1, i + 2))) {
      push(home);
      i++;
    } else if (c === "*" || c === "?") {
      push(c, true);
      i++;
    } else if (c === "`") {
      return "command substitution is not simulated here";
    } else if (c === ">" || c === "<" || (c === "&" && line[i + 1] === ">")) {
      if (c === "<") return "input redirection is not simulated here";
      let stream: Redirect["stream"] = "out";
      if (c === "&") {
        stream = "both";
        i++;
      } else {
        // A lone digit before the `>` names a descriptor, not a word.
        const only = parts.length === 1 ? parts[0] : undefined;
        const digit = only !== undefined && "text" in only && /^\d$/.test(only.text);
        if (digit && only.wild[0] !== true) {
          stream = only.text === "2" ? "err" : "out";
          parts = [];
          started = false;
        }
      }
      end();
      i += line[i + 1] === ">" ? 2 : 1;
      if (line[i] === "&") {
        // `2>&1`, `>&2`: a duplicate, which writes nothing anywhere.
        i++;
        while (i < line.length && /\d/.test(line[i] as string)) i++;
      } else pendingRedirect = stream;
    } else if (c === "|" || c === ";" || c === "&") {
      end();
      const two = line.slice(i, i + 2);
      if (two === "||" || two === "&&") {
        tokens.push({ kind: "op", op: two });
        i += 2;
      } else if (c === "&") {
        return "background jobs are not simulated here";
      } else {
        tokens.push({ kind: "op", op: c });
        i++;
      }
    } else {
      push(c);
      i++;
    }
  }
  end();
  if (pendingRedirect !== undefined) return "parse error near `\\n'";
  return tokens;
}

export function parse(line: string, home: string): Parsed {
  const tokens = tokenize(line, home);
  if (typeof tokens === "string") return { ok: false, error: tokens };
  const pipelines: Pipeline[] = [];
  let join: Pipeline["join"] = ";";
  let commands: Command[] = [];
  let words: Word[] = [];
  let redirects: Redirect[] = [];

  const endCommand = (op: string): string | undefined => {
    if (words.length === 0) return `parse error near \`${op}'`;
    commands.push({ words, redirects });
    words = [];
    redirects = [];
    return undefined;
  };
  for (const token of tokens) {
    if (token.kind === "word") words.push(token.word);
    else if (token.kind === "redirect") redirects.push(token.redirect);
    else if (token.op === "|") {
      const error = endCommand("|");
      if (error !== undefined) return { ok: false, error };
    } else {
      if (words.length === 0 && commands.length === 0 && token.op === ";") continue;
      const error = endCommand(token.op);
      if (error !== undefined) return { ok: false, error };
      pipelines.push({ join, commands });
      commands = [];
      join = token.op;
    }
  }
  if (words.length > 0) commands.push({ words, redirects });
  else if (commands.length > 0 || join !== ";") {
    return { ok: false, error: "parse error near `\\n'" };
  }
  if (commands.length > 0) pipelines.push({ join, commands });
  return { ok: true, pipelines };
}

/** Reads a word's variables, as the shell does just before running its command. */
export function expand(word: Word, variable: (name: string) => string): Expanded {
  let text = "";
  const wild: boolean[] = [];
  for (const part of word.parts) {
    if ("text" in part) {
      text += part.text;
      wild.push(...part.wild);
    } else {
      const value = variable(part.variable);
      text += value;
      for (let i = 0; i < value.length; i++) wild.push(false);
    }
  }
  return { text, wild: wild.includes(true) ? wild : undefined };
}

/** The regular expression one path segment of a pattern word matches. */
export function segmentPattern(segment: string, wild: readonly boolean[]): RegExp {
  let source = "";
  for (let i = 0; i < segment.length; i++) {
    const c = segment[i] as string;
    if (wild[i] === true) source += c === "*" ? "[^/]*" : "[^/]";
    else source += c.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }
  return new RegExp(`^${source}$`, "u");
}
