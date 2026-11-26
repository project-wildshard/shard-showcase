// .agents/hooks/prod-title-guard.mjs (meta QA 11-25 row 129, after row 124): `agent-browser` run by hand never reaches
// production's rooms or a play.wildshard.io path past the title (J205); the title, staging and local pass.
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import { joinsProduction, pastTitle } from '../prod-title-guard.mjs';

const HOOK = fileURLToPath(new URL('../prod-title-guard.mjs', import.meta.url));
const run = (payload) => spawnSync(process.execPath, [HOOK], { input: JSON.stringify(payload), encoding: 'utf8', env: { PATH: process.env.PATH ?? '' } });

test('agent-browser past the title or at the rooms host is refused', () => {
  for (const command of [
    'agent-browser open https://play.wildshard.io/nalati-grasslands/',
    'agent-browser open "https://play.wildshard.io/?chunk=nalati-grasslands"',
    'agent-browser open "https://play.wildshard.io/?agent=opus&zone=far-reach"',
    "agent-browser --session prod open 'https://play.wildshard.io/play'",
    'agent-browser open play.wildshard.io/driftwood-isle/',
    'agent-browser open https://rooms.wildshard.io/up',
    'agent-browser eval "new WebSocket(\'wss://rooms.wildshard.io/rooms/155\')"',
    'npx -y agent-browser open https://play.wildshard.io/nine-dragon-stack/',
    'cd /tmp && WS_LANE_NAME=x agent-browser open https://play.wildshard.io/x/',
    'agent-browser open https://staging.wildshard.io/ && agent-browser open https://play.wildshard.io/pine-hollow/',
    '/opt/homebrew/bin/agent-browser open https://PLAY.wildshard.io/sky-reach/',
    'agent-browser-session open https://play.wildshard.io/glowfen/',
  ]) {
    assert.notEqual(joinsProduction(command), null, command);
  }
  assert.match(joinsProduction('agent-browser open https://rooms.wildshard.io/up') ?? '', /rooms\.wildshard\.io is production's rooms host/u);
  assert.match(joinsProduction('agent-browser open https://play.wildshard.io/?chunk=nalati') ?? '', /\?chunk on play\.wildshard\.io is past the title/u);
});

test("the bare title, staging, local, other commands, quoted text and the escape hatch pass", () => {
  for (const command of [
    'agent-browser open https://play.wildshard.io/',
    'agent-browser open https://play.wildshard.io',
    'agent-browser open "https://play.wildshard.io/?agent=opus-guard131&mute=1"',
    'agent-browser open https://play.wildshard.io/index.html?nolock=1&sw=0',
    'agent-browser open https://staging.wildshard.io/nalati-grasslands/',
    'agent-browser open "https://staging.wildshard.io/?chunk=far-reach"',
    'agent-browser open http://localhost:5173/driftwood-isle/',
    'agent-browser snapshot -i',
    'curl -A "curl WildshardAgent/1" https://play.wildshard.io/version.json',
    'echo "agent-browser open https://play.wildshard.io/nalati-grasslands/"',
    'grep -rn "rooms.wildshard.io" docs/',
    'git commit -m "agent-browser open https://rooms.wildshard.io is refused"',
    'ALLOW_PROD_PAST_TITLE=1 agent-browser open https://play.wildshard.io/nalati-grasslands/',
  ]) {
    assert.equal(joinsProduction(command), null, command);
  }
  assert.equal(pastTitle('https://play.wildshard.io.'), null);
  assert.equal(pastTitle('not a url'), null);
});

test('the hook exits 2 with the rule for both tools and passes bad input', () => {
  const refused = run({ tool_name: 'Bash', tool_input: { command: 'agent-browser open https://play.wildshard.io/nalati-grasslands/' } });
  assert.equal(refused.status, 2);
  assert.match(refused.stderr, /BLOCKED by \.agents\/hooks\/prod-title-guard\.mjs/u);
  assert.match(refused.stderr, /ALLOW_PROD_PAST_TITLE=1/u);
  assert.equal(run({ tool_name: 'Bash', tool_input: { command: 'agent-browser open https://play.wildshard.io/' } }).status, 0);
  assert.equal(run({ tool_name: 'Edit', tool_input: { file_path: '/x', old_string: 'a', new_string: 'b' } }).status, 0);
  const bad = spawnSync(process.execPath, [HOOK], { input: 'not json', encoding: 'utf8' });
  assert.equal(bad.status, 0);
  assert.equal(bad.stderr, '');
});
