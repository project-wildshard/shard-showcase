// `wildshard check .` (lint, build, validate, prove, report) once the shard
// source exists. Its author lint is type-aware (A9), so it gets the pinned
// tsgolint the way `pnpm lint` does. Without src/shard.config.ts it says so
// and passes, so the gate stays usable until the first shard source lands.
import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { lintEnvironment } from './.kit/bin-tools.mjs';

if (existsSync('src/shard.config.ts')) {
  const run = spawnSync('pnpm', ['exec', 'wildshard', 'check', '.'], { env: lintEnvironment(), stdio: 'inherit' });
  process.exitCode = run.status ?? 1;
} else {
  console.log('check:shard: no src/shard.config.ts yet; skipped');
}
