import { existsSync, readFileSync } from 'node:fs';
import { expect, test } from 'vitest';

// vitest.config.ts excludes every path in test/lift-pending.json: lifted tests that still wait on a port. An entry
// whose file is gone hides nothing and only hides the next file of that name, so it must leave the list.
// Until a shard lands here this is also the repo's one Vitest file, which gives the worktree guard's Vitest check
// (test/tooling/worktree-guard.test.mjs, in pnpm check) a real discovery to prove a planted worktree stays out of.
const pending: unknown = JSON.parse(readFileSync(new URL('lift-pending.json', import.meta.url), 'utf8'));

test('test/lift-pending.json lists only test files that exist', () => {
  expect(Array.isArray(pending)).toBe(true);
  for (const entry of pending as unknown[]) {
    expect(typeof entry).toBe('string');
    expect(existsSync(String(entry)), `${String(entry)} is gone: drop it from test/lift-pending.json`).toBe(true);
  }
});
