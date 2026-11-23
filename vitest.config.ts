import { readFileSync } from 'node:fs';
import path from 'node:path';
import { defineConfig } from 'vitest/config';
import { viteTmpRoot } from './scripts/vite-tmp.mjs';


export default defineConfig({
  plugins: [viteTmpRoot()],
  resolve: { dedupe: ['three', 'valibot'] },
  test: {
    execArgv: ['--import', path.resolve('node_modules/@wildshard/sdk/src/sharddev/bake/format-hook.mjs')],
    testTimeout: 30_000,
    environment: 'node',
    server: { deps: { inline: [/@wildshard\//u] } },
    include: ['src/shards/**/*.test.ts', 'test/**/*.test.ts'],
    exclude: ['**/node_modules/**', ...JSON.parse(readFileSync('test/lift-pending.json', 'utf8'))],
    passWithNoTests: true,
  },
});
