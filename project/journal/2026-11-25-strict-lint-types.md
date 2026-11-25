# Strict lint and types for the shard (A9), and 919ccbf's fallout

The audit of 919ccbf found the shard would go unlinted: I had deleted `.oxlintrc.author.json`, which
`wildshard check` needs at the root (sharddev `authorLint.ts`; without it the lint is a silent skip), and
nothing else ran it. Jake: fix it, ignore the build output, "Add pack back", rename the stale hints.

- `.oxlintrc.author.json` is `wildshard new`'s (sdk 0.4.12), not the old engine-era copy, made strictest:
  `typeAware`, `nursery` an error, unused disable comments an error. Its ignores now also skip `src/scripts`
  and `src/test/.kit`. Gotcha: the template already has an `ignorePatterns` key at the bottom, and a
  duplicate JSON key means the last wins; my first one, at the top, was silently dropped (600 errors in the
  kit copies). Merged into the one key.
- `tsconfig.json` at the root: `wildshard new`'s bundler settings plus the strictest flags we use elsewhere
  (noUncheckedIndexedAccess, exactOptionalPropertyTypes, ...), `types: ["node"]`. `tsc` refuses a project
  with no inputs (TS18003), so `typecheck` is `src/scripts/typecheck.mjs`: a note and a pass until the
  first tracked `.ts` under `src/`.
- Proved on real shard code: the `wildshard new --empty` source dropped into `src/` (then removed). Lint:
  clean; a planted file fails on any, console.log, return types. tsc: catches unchecked index and missing
  returns; 3 errors left inside the sdk's shipped `.ts`, as `three` has no types (`@types/three`, a new dep,
  is Jake's call). Brasscap's own typecheck covers only `tools/`, not its shard source.
- `pack` is back as `wildshard build .` (`wildshard pack` is a deprecated alias of it). `public/shardfiles/`
  and `public/assets/*/map/` are gitignored as in the template. The hints for `pnpm lint:fix` / `format`
  / `test:hooks` now name `pnpm fix` / `pnpm test`. `publish-shard.mjs`'s `build:shards` branch stays: it
  is how multi-shard repos build, not a hint.
- Still open from the audit: repo-kit `sync.sh` runs `pnpm format` and `pnpm test:hooks` by name.

## Then: @types/three, kit/ gone, src formatted

- `@types/three` 0.186.0 (matches `three`). Installing it was not enough: the sdk's and kit's shipped `.ts` sit in
  pnpm's global virtual store, and resolving `three` from there never reaches this repo's `node_modules/@types`.
  `tsconfig.json` `paths` maps `three` and `three/*` to it. The template source now typechecks with 0 errors; a
  planted unchecked index still fails.
- `kit/.oxlintrc.json` deleted (it linted nothing). `kit/.oxfmtrc.json` moved to the root and now formats `src/`
  minus `src/scripts` and `src/test/.kit`; `format:check` and `fix` use it. `kit/` is gone. The template's own
  source is not in this style (4 files flagged), so a shard copied in needs one `pnpm fix`.
- `src/scripts/.kit/lint.mjs` now points at a config that no longer exists; nothing calls it. repo-kit's next
  sync re-stamps `kit/`, and `sync.sh` still wants `pnpm format` / `test:hooks` (Jake: leave it, phase 2).
