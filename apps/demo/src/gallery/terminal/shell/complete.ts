/**
 * Tab completion: a command's name in a command's place, a path everywhere else, and the few
 * arguments whose values are a closed set (git's subcommands, the profiles, `pnpm test`).
 *
 * It reads the line to the left of the cursor the way the parser will: quotes and backslashes
 * are undone to find the word being typed, and the completed word is written back with its
 * blanks and metacharacters escaped, so `Figma D` completes to `Figma\ Design/`. Hidden names are
 * offered only once a dot is typed, and `cd` is offered directories only, as zsh does.
 */

import { COMPLETABLE } from "./commands";
import { listing } from "./files";
import { HOME, lookup, resolvePath } from "./snapshot";

export interface Candidate {
  readonly name: string;
  readonly dir: boolean;
}

export interface Completion {
  /** Where, in the text before the cursor, the word being completed starts. */
  readonly from: number;
  /** What the word becomes: the one candidate completed, or the candidates' common prefix. */
  readonly replacement: string;
  readonly candidates: readonly Candidate[];
  readonly unique: boolean;
}

const GIT = ["branch", "diff", "log", "remote", "show", "status"];

function escape(text: string): string {
  return text.replace(/[\s'"\\$*?()&;|<>`!#]/g, "\\$&");
}

function commonPrefix(names: readonly string[]): string {
  let prefix = names[0] ?? "";
  for (const name of names) {
    while (!name.startsWith(prefix)) prefix = prefix.slice(0, -1);
  }
  return prefix;
}

/** The unquoted word the cursor is at the end of, where it starts, and the words before it. */
function currentWord(before: string): { word: string; from: number; previous: string[] } {
  let word = "";
  let from = 0;
  let inWord = false;
  let quote: string | undefined;
  let previous: string[] = [];
  for (let i = 0; i < before.length; i++) {
    const c = before[i] as string;
    if (quote !== undefined) {
      if (c === quote) quote = undefined;
      else word += c;
    } else if (c === "\\" && i + 1 < before.length) {
      word += before[++i];
      inWord = true;
    } else if (c === "'" || c === '"') {
      quote = c;
      inWord = true;
    } else if (/\s/.test(c) || "|;&".includes(c)) {
      if (inWord) previous.push(word);
      if (!/\s/.test(c)) previous = [];
      word = "";
      inWord = false;
      from = i + 1;
    } else {
      word += c;
      inWord = true;
    }
  }
  return { word, from, previous };
}

export function complete(
  before: string,
  cwd: string,
  profiles: readonly string[],
): Completion | undefined {
  const { word, from, previous } = currentWord(before);
  const fixed = (options: readonly string[]): Completion | undefined => {
    const names = options.filter((name) => name.startsWith(word));
    if (names.length === 0) return undefined;
    const unique = names.length === 1;
    return {
      from,
      replacement: unique ? `${escape(names[0] as string)} ` : escape(commonPrefix(names)),
      candidates: names.map((name) => ({ name, dir: false })),
      unique,
    };
  };

  if (previous.length === 0 && !word.includes("/")) return fixed(COMPLETABLE);
  if (previous.length === 1) {
    if (previous[0] === "git") return fixed(GIT);
    if (previous[0] === "profile") return fixed(profiles);
    if (previous[0] === "pnpm") return fixed(["test"]);
  }

  const expanded = word === "~" ? `${HOME}/` : word.startsWith("~/") ? HOME + word.slice(1) : word;
  const slash = expanded.lastIndexOf("/");
  const base = expanded.slice(slash + 1);
  const found = lookup(resolvePath(cwd, slash < 0 ? "." : expanded.slice(0, slash + 1)));
  if (found.kind !== "found" || found.node.kind !== "dir") return undefined;
  const dirsOnly = previous[0] === "cd";
  const candidates = listing(found.node).filter(
    (entry) =>
      entry.name.startsWith(base) &&
      (base.startsWith(".") || !entry.name.startsWith(".")) &&
      (!dirsOnly || entry.dir),
  );
  if (candidates.length === 0) return undefined;
  // The directory part is kept as it was typed, `~` included.
  const typedDir = word === "~" ? "~/" : word.slice(0, word.lastIndexOf("/") + 1);
  const unique = candidates.length === 1;
  const only = candidates[0] as Candidate;
  const replacement = unique
    ? escape(typedDir + only.name) + (only.dir ? "/" : " ")
    : escape(typedDir + commonPrefix(candidates.map((c) => c.name)));
  return { from, replacement, candidates, unique };
}
