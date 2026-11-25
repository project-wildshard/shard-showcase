# package.json scripts, from first principles

Ask A8 (Jake: "a choatic clusterfuck"; keep lint, pack, build for a shard like shard-brasscap; leave the deps).

- 19 scripts down to 9: prepare, dev, build, lint, format:check, fix, test, check, agents:sync. The five `check:*`
  steps are inlined into `check`; the three test scripts are one `test` (so pre-push now runs the hook tests CI ran
  alone); `lint:fix` + `format` are `fix`; `md:wrap` was an alias. `pack:shards`/`build:shards` (`pack-all.mjs`,
  `publish-public.mjs`, both looping over shards that do not exist) are `build` = `wildshard build .`, which writes
  the shardfile (`pack` is deprecated); `publish-shard.mjs` already falls back to it. `lint:shards` and its
  engine-era `.oxlintrc.author.json` went: `wildshard check .` lints shard source. It joins `check` with the
  shard source, which goes in `src/` as in brasscap.
- `lint.mjs` now ignores the kit-owned trees itself (`.githooks`, `.agents`, `scripts`, `kit/test`, and `src`
  without its own config). The config could not: oxlint resolves `ignorePatterns` from the config folder, kit/.
  So `lint` is a bare `node kit/scripts/lint.mjs`. Probed: kit/ is still linted, staged `scripts/` files skipped.
- The kit tests left `src/test/.kit` for `kit/test` so `src/` can be the shard. `pnpm check`: 249 tests, 24 s.
- Kit-owned leftovers for phase 2: `run-checks.mjs` still hints `pnpm lint:fix / pnpm format`.
- Pre-push now runs the hook tests, and `lanes.test.mjs` failed there only: `.githooks/test-helpers.mjs` scrubbed
  `GIT_*` and the bypass flags from the sandbox env but not pre-push's `WS_PUSH_REFS`, so a sandboxed
  `run-checks.mjs push` chased the outer push's commit. Added it to the scrub list (a kit file; phase 2).
- Undone: moving the kit tests to `kit/test` was not signed off; Jake chose `src/test/.kit` (A3) and wants it.
  Back there; `lint.mjs` drops `kit/test/**` (`src/**` is ignored without a src config anyway). The worry that
  `src/` as shard source would pick them up found no support in sharddev: no walk over all of `src/`.
