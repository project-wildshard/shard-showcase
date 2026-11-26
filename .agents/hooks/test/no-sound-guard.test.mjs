// .agents/hooks/no-sound-guard.mjs (meta QA-FEEDBACK-2026-11-24 row 49): no agent run makes a sound on Jake's Mac, from
// either agent tool; muted, headless and read-only commands pass.
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import { makesSound, staleSilence } from '../no-sound-guard.mjs';

const HOOK = fileURLToPath(new URL('../no-sound-guard.mjs', import.meta.url));
const run = (payload) => spawnSync(process.execPath, [HOOK], { input: JSON.stringify(payload), encoding: 'utf8' });

test('booting or driving the iOS Simulator is refused', () => {
  for (const command of [
    'xcrun simctl boot "iPhone 17 Pro"',
    'xcrun simctl boot wildshard-iphone && xcrun simctl openurl booted http://localhost:5173',
    'simctl launch booted com.apple.mobilesafari',
    'open -a Simulator',
    'open -g -a Simulator',
    'open -a /Applications/Xcode.app/Contents/Developer/Applications/Simulator.app',
    'open "/Applications/Xcode.app/Contents/Developer/Applications/Simulator.app"',
    'idb boot ABC',
    'cd engine; xcrun simctl boot X',
    'echo $(xcrun simctl boot X)',
  ]) {
    assert.match(makesSound(command) ?? '', /iOS Simulator/u, command);
  }
});

test('an unmuted Chromium, a headed Playwright, a game page in a desktop browser and speakers are refused', () => {
  for (const command of [
    '"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --use-mock-keychain --password-store=basic http://x',
    '~/Library/Caches/ms-playwright/chromium-1200/chrome-mac/Chromium.app/Contents/MacOS/Chromium --headless',
    '~/Library/Caches/ms-playwright/chromium_headless_shell-1200/chrome-mac/chrome-headless-shell --remote-debugging-port=9222',
    'google-chrome --headless=new --dump-dom http://localhost:5173',
    'npx playwright open http://localhost:5173',
    'pnpm exec playwright codegen https://staging.wildshard.io',
    'agent-browser --args "--use-mock-keychain" open http://localhost:5173',
    'AGENT_BROWSER_ARGS="--headless" agent-browser open http://localhost:5173',
    'export AGENT_BROWSER_ARGS="--headless"',
    'open http://localhost:5173/?zone=driftwood',
    'open -a "Google Chrome" https://staging.wildshard.io/play',
    'afplay /System/Library/Sounds/Glass.aiff',
    'say done',
  ]) {
    assert.notEqual(makesSound(command), null, command);
  }
});

test('muted launches, reads, text, shutdowns, artifacts and the escape hatch pass', () => {
  for (const command of [
    'xcrun simctl shutdown all',
    'xcrun simctl list devices',
    'pkill -x Simulator',
    'grep -rn "simctl boot" scripts',
    'git commit -m "never xcrun simctl boot" -- a',
    'echo "open -a Simulator"',
    '"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --mute-audio --use-mock-keychain --password-store=basic',
    'chrome-headless-shell --mute-audio --remote-debugging-port=9222',
    'agent-browser open http://localhost:5173',
    'agent-browser --args "--mute-audio,--use-mock-keychain" open http://localhost:5173',
    'npx playwright test e2e/smoke.spec.ts',
    'npx playwright install chromium',
    'open -a "Google Chrome" https://claude.ai/artifact/abc',
    'open project/evidence/board.png',
    'node scripts/fps/table.mjs --profiles phone-high',
    'ls ~/Library/Caches/ms-playwright',
    'ALLOW_AGENT_SOUND=1 xcrun simctl boot X',
    '',
  ]) {
    assert.equal(makesSound(command), null, command);
  }
});

test('the hook exits 2 with the way through and the escape hatch; other commands and tools pass silently', () => {
  const blocked = run({ tool_name: 'Bash', tool_input: { command: 'xcrun simctl boot wildshard-iphone' } });
  assert.equal(blocked.status, 2);
  assert.match(blocked.stderr, /BLOCKED by \.agents\/hooks\/no-sound-guard\.mjs: the iOS Simulator/u);
  assert.match(blocked.stderr, /headless Playwright WebKit/u);
  assert.match(blocked.stderr, /ALLOW_AGENT_SOUND=1/u);
  for (const payload of [{ tool_name: 'Bash', tool_input: { command: 'xcrun simctl shutdown all' } }, { tool_name: 'Edit', tool_input: { file_path: 'x' } }, {}]) {
    const passed = run(payload);
    assert.equal(passed.status, 0);
    assert.equal(passed.stderr, '');
  }
  assert.equal(spawnSync(process.execPath, [HOOK], { input: 'not json', encoding: 'utf8' }).status, 0);
});

// Meta QA 11-25 row 140: a shard's browser-playwright.mjs launches through its kit marker; a stamp from before silencePage
// let headless WebKit play game audio, so a script run in that repo is refused until the kit is restamped.
test('a script run in a repo whose kit browser marker does not silence pages is refused', () => {
  const root = mkdtempSync(join(tmpdir(), 'no-sound-stamp-'));
  try {
    const shard = join(root, 'shard-x'), engine = join(root, 'engine');
    for (const [repo, marker, launcher] of [
      [shard, 'export function installBrowserActorMarker() {}', "import './.kit/wildshard-browser-marker.mjs';"],
      [engine, 'export function installBrowserActorMarker() {}', "import './browser-actor-marker.mjs';"],
    ]) {
      mkdirSync(join(repo, '.git'), { recursive: true });
      mkdirSync(join(repo, 'src/scripts/.kit'), { recursive: true });
      writeFileSync(join(repo, 'src/scripts/.kit/wildshard-browser-marker.mjs'), marker);
      writeFileSync(join(repo, 'src/scripts/browser-playwright.mjs'), launcher);
    }
    for (const [command, cwd] of [['node src/scripts/test-gpu.mjs', shard], ['bash src/scripts/run.sh', shard],
      [`cd ${shard} && node src/scripts/test-gpu.mjs`, root], [`node ${shard}/src/scripts/test-gpu.mjs`, root]]) {
      assert.match(staleSilence(command, cwd) ?? '', /does not silence pages/u, command);
    }
    for (const [command, cwd] of [['git status', shard], ['ALLOW_AGENT_SOUND=1 node x.mjs', shard],
      ['node src/scripts/test-gpu.mjs', engine], ['node x.mjs', root]]) {
      assert.equal(staleSilence(command, cwd), null, command);
    }
    writeFileSync(join(shard, 'src/scripts/.kit/wildshard-browser-marker.mjs'), 'export function silencePage() {}');
    assert.equal(staleSilence('node src/scripts/test-gpu.mjs', shard), null, 'a restamped marker passes');
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
