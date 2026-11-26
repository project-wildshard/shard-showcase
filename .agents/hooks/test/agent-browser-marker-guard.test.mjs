// .agents/hooks/agent-browser-marker-guard.mjs (meta QA 11-25 row 148, after rows 124 and 129): every agent-browser
// an agent drives carries the Wildshard agent user agent, so production's room door refuses it (J205).
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { after, test } from 'node:test';
import { fileURLToPath } from 'node:url';
import { marked, unmarkedBrowser } from '../agent-browser-marker-guard.mjs';

const HOOK = fileURLToPath(new URL('../agent-browser-marker-guard.mjs', import.meta.url));
const root = mkdtempSync(join(tmpdir(), 'ab-marker-'));
after(() => rmSync(root, { recursive: true, force: true }));

/** A home whose ~/.agent-browser/config.json holds `config`, or none. @param {string} name @param {object} [config] */
function home(name, config) {
  const dir = join(root, name);
  mkdirSync(join(dir, '.agent-browser'), { recursive: true });
  if (config) writeFileSync(join(dir, '.agent-browser', 'config.json'), JSON.stringify(config));
  return dir;
}
const markedHome = home('marked', { headed: false, userAgent: 'WildshardAgent/1 (agent-browser)', args: '--mute-audio' });
const plainHome = home('plain', { headed: false, args: '--mute-audio' });
const work = join(root, 'work');
mkdirSync(work);
const project = join(root, 'project');
mkdirSync(project);
writeFileSync(join(project, 'agent-browser.json'), JSON.stringify({ userAgent: 'Mozilla/5.0 plain' }));
writeFileSync(join(work, 'plain.json'), JSON.stringify({ userAgent: 'Mozilla/5.0 plain' }));

/** @param {string} command @param {{ home?: string, cwd?: string, env?: Record<string, string>, cdp?: string }} [o] */
const check = (command, o = {}) => unmarkedBrowser(command, {
  home: o.home ?? markedHome,
  cwd: o.cwd ?? work,
  env: o.env ?? {},
  cdp: () => o.cdp,
});

test('the marker matches engine actor.ts, and the helper call counts', () => {
  for (const ua of ['WildshardAgent/1', 'WildshardAgent/1 (opus-mark148)', 'Mozilla/5.0 (iPhone) Safari/604.1 WildshardAgent/1 (x)', '$(node -e "agentUserAgent()")']) assert.ok(marked(ua), ua);
  for (const ua of ['Mozilla/5.0 HeadlessChrome/158', 'xWildshardAgent/1', 'WildshardAgent/2', '']) assert.ok(!marked(ua), ua);
});

test('an unmarked agent-browser is refused', () => {
  const cases = [
    ['agent-browser open https://staging.wildshard.io/', { home: plainHome }, /no user agent is set/u],
    ['agent-browser snapshot -i', { home: plainHome }, /no user agent is set/u],
    ['AGENT_BROWSER_USER_AGENT="Mozilla/5.0 plain" agent-browser open https://staging.wildshard.io/', {}, /AGENT_BROWSER_USER_AGENT is "Mozilla\/5\.0 plain"/u],
    ['export AGENT_BROWSER_USER_AGENT=plain; agent-browser open https://play.wildshard.io/', {}, /AGENT_BROWSER_USER_AGENT is "plain"/u],
    ['AGENT_BROWSER_USER_AGENT=plain && agent-browser open https://play.wildshard.io/', {}, /AGENT_BROWSER_USER_AGENT is "plain"/u],
    ['agent-browser open https://play.wildshard.io/', { env: { AGENT_BROWSER_USER_AGENT: 'HeadlessChrome' } }, /AGENT_BROWSER_USER_AGENT/u],
    ['agent-browser --user-agent "Mozilla/5.0 (iPhone)" open https://play.wildshard.io/', {}, /--user-agent/u],
    ['agent-browser --user-agent=plain open https://play.wildshard.io/', {}, /--user-agent/u],
    ['agent-browser open https://play.wildshard.io/', { cwd: project }, /agent-browser\.json sets userAgent "Mozilla\/5\.0 plain"/u],
    [`cd ${project} && agent-browser open https://play.wildshard.io/`, {}, /agent-browser\.json sets userAgent/u],
    ['agent-browser --config plain.json open https://play.wildshard.io/', {}, /the config plain\.json sets userAgent/u],
    ['AGENT_BROWSER_CONFIG=plain.json agent-browser open https://play.wildshard.io/', {}, /the config plain\.json/u],
    ['agent-browser set device "iPhone 14"', {}, /set device/u],
    ['agent-browser set headers \'{"User-Agent":"plain"}\'', {}, /set headers/u],
    ['agent-browser --headers \'{"user-agent":"plain"}\' open https://staging.wildshard.io/', {}, /--headers/u],
    ['agent-browser --auto-connect open https://play.wildshard.io/', {}, /--auto-connect/u],
    ['agent-browser --cdp 9222 open https://play.wildshard.io/', { cdp: 'Mozilla/5.0 HeadlessChrome/158' }, /over CDP \(9222\)/u],
    ['agent-browser connect 9222', { cdp: 'Mozilla/5.0 HeadlessChrome/158' }, /over CDP/u],
    ['AGENT_BROWSER_CDP=ws://127.0.0.1:9222/devtools/browser/x agent-browser click @e1', { cdp: 'HeadlessChrome' }, /over CDP/u],
    ['npx -y agent-browser open https://play.wildshard.io/', { home: plainHome }, /no user agent/u],
    ['echo hi; /opt/homebrew/bin/agent-browser open https://play.wildshard.io/', { home: plainHome }, /no user agent/u],
    ["AGENT_BROWSER_USER_AGENT='WildshardAgent/1(${WS_LANE_NAME})' agent-browser open https://play.wildshard.io/", {}, /AGENT_BROWSER_USER_AGENT/u],
    ['unset AGENT_BROWSER_USER_AGENT; agent-browser open https://play.wildshard.io/', { home: plainHome, env: { AGENT_BROWSER_USER_AGENT: 'WildshardAgent/1' } }, /no user agent/u],
  ];
  for (const [command, options, reason] of cases) {
    const found = check(command, options);
    assert.notEqual(found, null, command);
    assert.match(found ?? '', reason, command);
  }
});

test('a marked agent-browser passes, as do commands that drive no page, other commands and the escape hatch', () => {
  const cases = [
    ['agent-browser open https://staging.wildshard.io/', {}],
    ['agent-browser click @e3 && agent-browser snapshot -i', {}],
    ['AGENT_BROWSER_USER_AGENT="WildshardAgent/1 (${WS_LANE_NAME:-agent})" agent-browser open https://staging.wildshard.io/', { home: plainHome }],
    ['export AGENT_BROWSER_USER_AGENT="Mozilla/5.0 (iPhone) Safari/604.1 WildshardAgent/1 (x)"; agent-browser set viewport 402 874', { home: plainHome }],
    ['WS_AGENT_UA="curl WildshardAgent/1 (x)"; AGENT_BROWSER_USER_AGENT="$WS_AGENT_UA" agent-browser open https://staging.wildshard.io/', { home: plainHome }],
    ['agent-browser open https://staging.wildshard.io/', { home: plainHome, env: { AGENT_BROWSER_USER_AGENT: 'WildshardAgent/1 (env)' } }],
    ['AGENT_BROWSER_USER_AGENT="WildshardAgent/1" agent-browser open https://play.wildshard.io/', { cwd: project }],
    ['agent-browser --user-agent "WildshardAgent/1 (x)" open http://localhost:5173/', { home: plainHome }],
    ['agent-browser --session m --headed false open https://staging.wildshard.io/', {}],
    ['agent-browser --cdp 9222 snapshot', { home: plainHome, cdp: 'Mozilla/5.0 HeadlessChrome/158 WildshardAgent/1 (session)' }],
    ['agent-browser --cdp 9222 snapshot', { home: plainHome, cdp: undefined }],
    ['agent-browser set headers \'{"x-trace":"1"}\'', {}],
    ['agent-browser close', { home: plainHome }],
    ['agent-browser --session m148 close', { home: plainHome }],
    ['agent-browser --help', { home: plainHome }],
    ['agent-browser --version', { home: plainHome }],
    ['agent-browser', { home: plainHome }],
    ['agent-browser install', { home: plainHome }],
    ['agent-browser skills get core', { home: plainHome }],
    ['echo "agent-browser open https://play.wildshard.io/"', { home: plainHome }],
    ['git commit -m "agent-browser set device is refused"', { home: plainHome }],
    ['curl -A "curl WildshardAgent/1" https://staging.wildshard.io/version.json', { home: plainHome }],
    ['ALLOW_UNMARKED_BROWSER=1 agent-browser open http://localhost:5173/', { home: plainHome }],
  ];
  for (const [command, options] of cases) assert.equal(check(command, options), null, command);
});

test('the hook exits 2 with the fix and the escape hatch, and passes bad input', () => {
  const env = { PATH: process.env.PATH ?? '', HOME: plainHome };
  const run = (payload) => spawnSync(process.execPath, [HOOK], { input: JSON.stringify(payload), encoding: 'utf8', env });
  const refused = run({ tool_name: 'Bash', cwd: work, tool_input: { command: 'agent-browser open https://play.wildshard.io/' } });
  assert.equal(refused.status, 2);
  assert.match(refused.stderr, /BLOCKED by \.agents\/hooks\/agent-browser-marker-guard\.mjs/u);
  assert.match(refused.stderr, /AGENT_BROWSER_USER_AGENT="WildshardAgent\/1 \(\$\{WS_LANE_NAME:-agent\}\)" agent-browser open <url>/u);
  assert.match(refused.stderr, /ALLOW_UNMARKED_BROWSER=1/u);
  const fixed = 'AGENT_BROWSER_USER_AGENT="WildshardAgent/1 (${WS_LANE_NAME:-agent})" agent-browser open https://staging.wildshard.io/';
  assert.equal(run({ tool_name: 'Bash', cwd: work, tool_input: { command: fixed } }).status, 0);
  assert.equal(run({ tool_name: 'Edit', tool_input: { file_path: '/x', old_string: 'a', new_string: 'b' } }).status, 0);
  const bad = spawnSync(process.execPath, [HOOK], { input: 'not json', encoding: 'utf8', env });
  assert.equal(bad.status, 0);
  assert.equal(bad.stderr, '');
});
