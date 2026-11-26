#!/usr/bin/env node
// PreToolUse(Bash) guard, for Claude Code and Codex alike (meta QA 11-25 row 148, after rows 124 and 129). Production
// is humans only (J205): row 129's prod-title-guard keeps agent-browser off play.wildshard.io past the title, but a
// browser opened on the bare title can still click ENTER THE MMO. Row 124's prod room door refuses a join that carries
// the Wildshard agent user agent (`WildshardAgent/1`, engine actorMarkers.json), so every agent browser must carry it.
// This refuses a command that runs `agent-browser` when the browser it drives would not carry the marker. How
// agent-browser 0.37.1 picks its user agent (measured 2026-11-26, opus-mark148):
//   1. AGENT_BROWSER_USER_AGENT beats everything;
//   2. then ./agent-browser.json's userAgent (the command's folder), then ~/.agent-browser/config.json's;
//   3. the --user-agent flag counts only when no config sets one (a config's userAgent silently wins);
//   4. over CDP (--cdp, AGENT_BROWSER_CDP, `connect`) the attached Chrome keeps its own user agent, which this reads
//      from its /json/version; --auto-connect attaches to a human's Chrome and is refused;
//   5. `set device <name>` replaces the user agent with the device's, so it is refused, as is a `set headers` or
//      --headers user agent without the marker.
// Refused too: an unmarked --user-agent flag or --config file, even when a config would win, so the command reads true.
// `close`, `install`, `--help` and other commands that drive no page pass; so do quoted text and other commands.
// Escape hatch (J381), only for a check that must look like a player, never on production: ALLOW_UNMARKED_BROWSER=1 in
// the command. Bad input prints nothing and exits 0: a hook must never break a session.
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { isAbsolute, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { readPayload } from './lib/payload.mjs';

/** Engine's actor.ts AgentToken: the token alone, at the start or after a space, with an optional `(lane)`. */
const AGENT_TOKEN = /(?:^|\s)WildshardAgent\/1(?:\s+\([^)]*\))?(?=\s|$)/u;
/** Leading env assignments and wrappers before the command word. */
const PREFIX = /^(?:(?:export\s+)?\w+=\S*\s+|(?:sudo|nohup|exec|command|time|env|caffeinate(?:\s+-\w+)*|timeout\s+\S+|npx(?:\s+-y)?|pnpm\s+(?:exec|dlx)|bunx)\s+)*/iu;
/** Flags that take a value, so the word after them is not the subcommand. */
const VALUE_FLAGS = new Set([
  '--session', '--namespace', '--profile', '--config', '--user-agent', '--args', '--proxy', '--proxy-bypass',
  '--executable-path', '--extension', '--init-script', '--enable', '--cdp', '-p', '--provider', '--state', '--restore',
  '--restore-save', '--restore-check-url', '--restore-check-text', '--session-name', '--screenshot-dir',
  '--screenshot-quality', '--screenshot-format', '--color-scheme', '--download-path', '--max-output',
  '--allowed-domains', '--action-policy', '--confirm-actions', '--engine', '--idle-timeout', '--model', '--ca-cert',
  '--device', '--headers', '--fps',
]);
/** Subcommands that drive no page, so their user agent does not matter. */
const NO_PAGE = new Set(['close', 'install', 'upgrade', 'help', 'skills', 'session', 'profiles', 'plugin', 'dashboard', 'confirm', 'deny']);
const ASSIGN = /^(?:export\s+)?([A-Za-z_]\w*)=(.*)$/su;

/** True when a user agent carries the marker, or calls the helper that makes one. @param {string} ua */
export const marked = (ua) => AGENT_TOKEN.test(ua) || /\bagentUserAgent\b/u.test(ua);

/**
 * Replace quoted strings with placeholders, so a message's `;` or `agent-browser` reads as text, not a command.
 * @param {string} command @returns {{ bare: string, quoted: { text: string, single: boolean }[] }}
 */
function unquote(command) {
  /** @type {{ text: string, single: boolean }[]} */
  const quoted = [];
  const bare = command.replace(/'[^']*'|"(?:[^"\\]|\\.)*"/gu, (match) => {
    quoted.push({ text: match.slice(1, -1), single: match.startsWith("'") });
    return `__Q${quoted.length - 1}__`;
  });
  return { bare, quoted };
}

/**
 * A shell word's value: quotes dropped, `$NAME`, `${NAME}` and `${NAME:-default}` read from the command's own
 * variables, then the environment (single-quoted text stays literal).
 * @param {string} word @param {{ text: string, single: boolean }[]} quoted
 * @param {(name: string) => string | undefined} lookup
 */
function value(word, quoted, lookup) {
  const expand = (text) => text.replace(/\$\{(\w+)(?::?-([^}]*))?\}|\$(\w+)/gu, (_, braced, fallback, plain) => {
    const found = lookup(braced ?? plain);
    return found === undefined || found === '' ? (fallback ?? '') : found;
  });
  return word.split(/(__Q\d+__)/u).map((part) => {
    const match = /^__Q(\d+)__$/u.exec(part);
    if (!match) return expand(part);
    const piece = quoted[Number(match[1])];
    if (!piece) return '';
    return piece.single ? piece.text : expand(piece.text);
  }).join('');
}

/** A JSON config's userAgent, or undefined when the file or the field is missing. @param {string} path */
function configAgent(path) {
  try {
    const parsed = JSON.parse(readFileSync(path, 'utf8'));
    return typeof parsed?.userAgent === 'string' && parsed.userAgent !== '' ? parsed.userAgent : undefined;
  } catch {
    return undefined;
  }
}

/** A user-agent value in a headers JSON, or undefined. @param {string} json */
function headerAgent(json) {
  try {
    const parsed = JSON.parse(json);
    if (parsed === null || typeof parsed !== 'object') return undefined;
    const key = Object.keys(parsed).find((name) => name.toLowerCase() === 'user-agent');
    return key === undefined ? undefined : String(parsed[key]);
  } catch {
    return undefined;
  }
}

/** The user agent of the Chrome a CDP address points at, or undefined when it does not answer. @param {string} target */
function cdpAgent(target) {
  let base;
  if (/^\d+$/u.test(target)) base = `http://127.0.0.1:${target}`;
  else {
    try {
      const url = new URL(target);
      base = `http://${url.host}`;
    } catch {
      return undefined;
    }
  }
  const read = spawnSync('curl', ['-s', '-m', '1', `${base}/json/version`], { encoding: 'utf8', timeout: 2000 });
  try {
    const agent = JSON.parse(read.stdout ?? '')['User-Agent'];
    return typeof agent === 'string' ? agent : undefined;
  } catch {
    return undefined;
  }
}

/**
 * @typedef {{ env?: NodeJS.ProcessEnv, cwd?: string, home?: string, cdp?: (target: string) => string | undefined }} Context
 */

/**
 * Why a shell command would drive an agent-browser that does not carry the agent marker, or null when it would not.
 * @param {string} command @param {Context} [context] @returns {string | null}
 */
export function unmarkedBrowser(command, context = {}) {
  if (typeof command !== 'string' || /(?:^|\s)ALLOW_UNMARKED_BROWSER=1(?:\s|$)/u.test(command)) return null;
  const env = context.env ?? process.env;
  const home = context.home ?? env['HOME'] ?? homedir();
  const probe = context.cdp ?? cdpAgent;
  let cwd = context.cwd || process.cwd();
  const { bare, quoted } = unquote(command);
  /** Variables this command sets or unsets, in order; null is unset. @type {Map<string, string | null>} */
  const vars = new Map();
  for (const raw of bare.split(/&&|\|\||[;&|\n]|\$\(|[(`]/u)) {
    const head = raw.trim();
    if (!head) continue;
    const prefix = PREFIX.exec(head)?.[0] ?? '';
    const words = head.slice(prefix.length).split(/\s+/u).filter(Boolean);
    /** Variables set in front of this command word, for it alone. @type {Map<string, string>} */
    const own = new Map();
    const lookup = (/** @type {string} */ name) => {
      if (own.has(name)) return own.get(name);
      if (vars.has(name)) return vars.get(name) ?? undefined;
      return env[name];
    };
    for (const word of prefix.trim().split(/\s+/u)) {
      const match = ASSIGN.exec(word.replace(/^export\s+/u, ''));
      if (match) own.set(match[1] ?? '', value(match[2] ?? '', quoted, lookup));
    }
    // A segment that is only assignments (`A=b`, `A=b C=d`) sets them for the rest of the command.
    if (words.every((word) => ASSIGN.test(word))) {
      for (const [name, set] of own) vars.set(name, set);
      for (const word of words) {
        const match = ASSIGN.exec(word);
        if (match) vars.set(match[1] ?? '', value(match[2] ?? '', quoted, lookup));
      }
      continue;
    }
    const first = value(words[0] ?? '', quoted, lookup);
    if (first === 'unset') {
      for (const word of words.slice(1)) vars.set(value(word, quoted, lookup), null);
      continue;
    }
    if (first === 'export') {
      for (const word of words.slice(1)) {
        const match = ASSIGN.exec(word);
        if (match) vars.set(match[1] ?? '', value(match[2] ?? '', quoted, lookup));
      }
      continue;
    }
    if (first === 'cd' && words[1] !== undefined) {
      const target = value(words[1], quoted, lookup).replace(/^~(?=\/|$)/u, home);
      if (target && !target.includes('$')) cwd = isAbsolute(target) ? target : resolve(cwd, target);
      continue;
    }
    if ((first.split('/').pop() ?? '') !== 'agent-browser') continue;
    const args = words.slice(1).map((word) => value(word, quoted, lookup));
    const reason = judge(args, lookup, { cwd, home, probe });
    if (reason !== null) return reason;
  }
  return null;
}

/**
 * Why one agent-browser argument list drives an unmarked browser, or null.
 * @param {string[]} args @param {(name: string) => string | undefined} lookup
 * @param {{ cwd: string, home: string, probe: (target: string) => string | undefined }} where
 */
function judge(args, lookup, { cwd, home, probe }) {
  /** @type {string[]} */
  const positional = [];
  /** @type {Record<string, string>} */
  const flags = {};
  let autoConnect = false;
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index] ?? '';
    if (/^(?:-h|--help|-V|--version)$/u.test(arg)) return null;
    if (arg === '--auto-connect') autoConnect = true;
    const eq = /^(--[\w-]+)=(.*)$/su.exec(arg);
    if (eq && VALUE_FLAGS.has(eq[1] ?? '')) flags[eq[1] ?? ''] = eq[2] ?? '';
    else if (VALUE_FLAGS.has(arg)) {
      flags[arg] = args[index + 1] ?? '';
      index += 1;
    } else if (!arg.startsWith('-')) positional.push(arg);
  }
  const verb = positional[0];
  if (verb === undefined || NO_PAGE.has(verb)) return null;
  if (autoConnect) return '`agent-browser --auto-connect` drives a human\'s running Chrome, which carries no agent marker';
  if (verb === 'set' && positional[1] === 'device') return '`agent-browser set device` replaces the user agent with the device\'s, which carries no agent marker';
  const headers = verb === 'set' && positional[1] === 'headers' ? headerAgent(positional[2] ?? '') : undefined;
  if (headers !== undefined && !marked(headers)) return `\`agent-browser set headers\` sends user agent "${headers}", which carries no agent marker`;
  const flagHeaders = flags['--headers'] === undefined ? undefined : headerAgent(flags['--headers']);
  if (flagHeaders !== undefined && !marked(flagHeaders)) return `\`agent-browser --headers\` sends user agent "${flagHeaders}", which carries no agent marker`;

  const cdp = flags['--cdp'] ?? (verb === 'connect' ? positional[1] : undefined) ?? lookup('AGENT_BROWSER_CDP');
  if (cdp !== undefined && cdp !== '') {
    const agent = probe(cdp);
    if (agent === undefined || marked(agent)) return null;
    return `\`agent-browser\` over CDP (${cdp}) drives a Chrome whose user agent is "${agent}": CDP keeps the attached Chrome's user agent`;
  }

  const fromEnv = lookup('AGENT_BROWSER_USER_AGENT');
  if (fromEnv !== undefined && fromEnv !== '') {
    return marked(fromEnv) ? null : `AGENT_BROWSER_USER_AGENT is "${fromEnv}", which carries no agent marker`;
  }
  const flag = flags['--user-agent'];
  if (flag !== undefined && !marked(flag)) return `\`agent-browser --user-agent "${flag}"\` carries no agent marker (and a config's userAgent silently beats the flag)`;
  const configPath = flags['--config'] ?? lookup('AGENT_BROWSER_CONFIG');
  const named = configPath ? configAgent(isAbsolute(configPath) ? configPath : resolve(cwd, configPath)) : undefined;
  if (named !== undefined && !marked(named)) return `the config ${configPath} sets userAgent "${named}", which carries no agent marker`;
  const projectPath = resolve(cwd, 'agent-browser.json');
  const project = configAgent(projectPath);
  const userPath = resolve(home, '.agent-browser/config.json');
  const user = configAgent(userPath);
  const winner = project ?? named ?? user ?? flag;
  if (winner === undefined) return `no user agent is set (no AGENT_BROWSER_USER_AGENT, and neither ${projectPath} nor ${userPath} sets userAgent), so the browser runs as a plain HeadlessChrome`;
  if (marked(winner)) return null;
  const source = winner === project ? projectPath : winner === named ? `${configPath}` : userPath;
  return `${source} sets userAgent "${winner}", which carries no agent marker`;
}

/** The refusal text: what happened, the way through, and the escape hatch. @param {string} reason */
export function refusal(reason) {
  return [
    `BLOCKED by .agents/hooks/agent-browser-marker-guard.mjs: ${reason}.`,
    '',
    'Every agent browser carries the Wildshard agent user agent, so production\'s room door refuses it (J205; meta QA',
    '11-25 rows 124 and 148). The default ~/.agent-browser/config.json sets "userAgent": "WildshardAgent/1',
    '(agent-browser)"; when that is missing or overridden, put the marker in the environment, which beats every config:',
    '  AGENT_BROWSER_USER_AGENT="WildshardAgent/1 (${WS_LANE_NAME:-agent})" agent-browser open <url>',
    'An agent shell keeps no variables between calls: put it in front of every agent-browser command, or close the',
    'session (agent-browser close) and reopen it marked. A phone shape keeps the marker: `agent-browser set viewport',
    '402 874` with AGENT_BROWSER_USER_AGENT="<the phone\'s user agent> WildshardAgent/1 (<lane>)", never `set device`.',
    'Over CDP, attach only to a Chrome launched with the marker (engine src/scripts/agent-browser-session.mjs).',
    'Escape hatch (J381), only for a check that must look like a player, never on production: put',
    'ALLOW_UNMARKED_BROWSER=1 in front of the command and name it in your receipt.',
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
    const { tool, command, cwd } = readPayload(raw);
    reason = tool === 'shell' ? unmarkedBrowser(command, { cwd }) : null;
  } catch {
    reason = null;
  }
  if (reason !== null) {
    process.stderr.write(`${refusal(reason)}\n`);
    process.exit(2);
  }
}
