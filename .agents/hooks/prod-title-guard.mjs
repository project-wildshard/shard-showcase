#!/usr/bin/env node
// PreToolUse(Bash) guard, for Claude Code and Codex alike (meta QA 11-25 row 129, after row 124). Production is humans
// only (J205, J209): an agent may open play.wildshard.io's bare title, never join a world. Row 124 made every marked
// Playwright browser and agent-browser-session's own Chrome stop at the title, but `agent-browser` run by hand reads
// ~/.agent-browser/config.json (Jake's dotfiles, whose args are only --mute-audio), so nothing stopped it.
// This refuses a command that runs `agent-browser` (or `agent-browser-session`) naming
//   - rooms.wildshard.io, in any URL or as a bare host; or
//   - a play.wildshard.io URL past the title: any path but `/` or `/index.html`, or a query word other than `agent`,
//     `mute`, `nolock` or `sw` (repo-kit files/scripts/wildshard-browser-marker.mjs prodNavigationRefusal, the same rule).
// The title itself, staging, localhost and every other host pass; so do quoted text and other commands. Escape hatch
// (J381), only on Jake's word: ALLOW_PROD_PAST_TITLE=1 in the command. Bad input prints nothing and exits 0: a hook
// must never break a session.
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { readPayload } from './lib/payload.mjs';

const PROD_PAGE_HOST = 'play.wildshard.io';
const PROD_ROOMS_HOST = 'rooms.wildshard.io';
const TITLE_WORDS = new Set(['agent', 'mute', 'nolock', 'sw']);
const TITLE_PATHS = new Set(['/', '/index.html']);
/** Leading env assignments and wrappers before the command word. */
const PREFIX = /^(?:(?:export\s+)?\w+=\S*\s+|(?:sudo|nohup|exec|command|time|env|caffeinate(?:\s+-\w+)*|timeout\s+\S+|npx(?:\s+-y)?|pnpm\s+(?:exec|dlx)|bunx)\s+)*/iu;
const BROWSER = /^agent-browser(?:-session)?$/u;
/** A URL with a scheme, or a schemeless one that starts with a production host. */
const URLS = /\b(?:https?|wss?):\/\/[^\s"'`<>\\)]+|(?<![\w.-])(?:play|rooms)\.wildshard\.io\.?(?:[:/?#][^\s"'`<>\\)]*)?(?![\w-])/giu;

/**
 * Replace quoted strings with placeholders, so a message's `;` or `agent-browser` reads as text, not a command.
 * @param {string} command @returns {{ bare: string, quoted: string[] }}
 */
function unquote(command) {
  /** @type {string[]} */
  const quoted = [];
  const bare = command.replace(/'[^']*'|"(?:[^"\\]|\\.)*"/gu, (match) => {
    quoted.push(match.slice(1, -1));
    return `__Q${quoted.length - 1}__`;
  });
  return { bare, quoted };
}

/** @param {string} text @param {string[]} quoted */
const requote = (text, quoted) => text.replace(/__Q(\d+)__/gu, (_, index) => quoted[Number(index)] ?? '');

/** Why an agent may not open this URL in a browser, or null. @param {string} text */
export function pastTitle(text) {
  let url;
  try {
    url = new URL(/^[a-z]+:\/\//iu.test(text) ? text : `https://${text}`);
  } catch {
    return null;
  }
  const host = url.hostname.toLowerCase().replace(/\.$/u, '');
  if (host === PROD_ROOMS_HOST) return `${PROD_ROOMS_HOST} is production's rooms host`;
  if (host !== PROD_PAGE_HOST) return null;
  const extra = [...url.searchParams.keys()].filter((word) => !TITLE_WORDS.has(word));
  if (!TITLE_PATHS.has(url.pathname)) return `${url.pathname} on ${PROD_PAGE_HOST} is past the title`;
  return extra.length === 0 ? null : `?${extra.join('&')} on ${PROD_PAGE_HOST} is past the title`;
}

/**
 * Why a shell command would drive agent-browser past production's title, or null when it would not.
 * @param {string} command @returns {string | null}
 */
export function joinsProduction(command) {
  if (typeof command !== 'string' || /(?:^|\s)ALLOW_PROD_PAST_TITLE=1(?:\s|$)/u.test(command)) return null;
  const { bare, quoted } = unquote(command);
  // A command word also starts after $( ( or a backtick.
  for (const raw of bare.split(/&&|\|\||[;&|\n]|\$\(|[(`]/u)) {
    const head = raw.trim();
    if (!head) continue;
    const prefix = PREFIX.exec(head)?.[0] ?? '';
    const [first = '', ...rest] = head.slice(prefix.length).split(/\s+/u);
    const name = requote(first, quoted).split('/').pop() ?? '';
    if (!BROWSER.test(name)) continue;
    for (const arg of rest.map((token) => requote(token, quoted))) {
      for (const match of arg.matchAll(URLS)) {
        const reason = pastTitle(match[0]);
        if (reason !== null) return `\`${name}\` names ${match[0]}: ${reason}`;
      }
    }
  }
  return null;
}

/** The refusal text: what happened, the way through, and the escape hatch. @param {string} reason */
export function refusal(reason) {
  return [
    `BLOCKED by .agents/hooks/prod-title-guard.mjs: ${reason}.`,
    '',
    'Production is humans only (J205, J209; meta QA 11-25 rows 124 and 129). An agent may open the bare title,',
    'https://play.wildshard.io/ (query words agent, mute, nolock, sw only), and never a path past it, a zone, a deep',
    'link or rooms.wildshard.io. Prove play on staging (https://staging.wildshard.io) or a local rig instead.',
    'Escape hatch (J381), only on Jake\'s word: put ALLOW_PROD_PAST_TITLE=1 in front of the command and name it in',
    'your receipt.',
  ].join('\n');
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  let raw = '';
  try {
    raw = readFileSync(0, 'utf8');
  } catch {
    raw = '';
  }
  let reason = null;
  try {
    const { tool, command } = readPayload(raw);
    reason = tool === 'shell' ? joinsProduction(command) : null;
  } catch {
    reason = null;
  }
  if (reason !== null) {
    process.stderr.write(`${refusal(reason)}\n`);
    process.exit(2);
  }
}
