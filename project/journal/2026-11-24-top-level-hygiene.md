# Top-level hygiene, phase 1

Ask A1 (Jake): too many top-level folders; he wants `src/ docs/ project/`.

- Deleted `lint/`. Three of its four baselines (`legacy-line-basis`, `nine-tiling-baseline`, `tile-bake-debt`) were
  engine leftovers that nothing read. `ratchet.json` (`{"budgets": {}}`) was passed as `WILDSHARD_RATCHET_FILE`,
  which the SDK lint plugin never reads, so `lint:shards` passes without it. The `lint/**` oxlint override went too.
- Deleted `test/lift-pending.{json,test.ts}`: an empty exclude list and a test that checked it. It was the repo's only
  Vitest file, and the kit's `worktree-guard` test fails a repo that uses Vitest with zero tests. So Vitest went
  as well (`vitest.config.ts`, `test:shards`, the devDependency); the first shard source brings it back.
- Deleted `public/assets/.gitkeep`. `publish-public.mjs` copies `src/shards/<slug>/assets/public` there for an
  empty slug list. sharddev's `cookInput.ts` hard-codes `<repo>/public` as the read root, so the real fix is there.
- Found: `kit/`, `scripts/` and `test/tooling/` are repo-kit's, and most of the "local" scripts are byte-identical
  copies in all 12 sibling shards, outside `sync.sh`'s `files/`. Phase 2 (repo-kit `.kit/`, sharddev `public/`) is
  a plan, not done here.
- `node_modules` had no `@wildshard/sdk` at all before `pnpm install`, so `lint:shards` was failing locally.

## pnpm-workspace.yaml goes

- This repo is one package, so `packages: [.]` did nothing. `allowBuilds` moved to package.json's `pnpm` block: a
  scratch install of sharp 0.34.5 is silent with it there and warns "Ignored build scripts" without it.
- The global store settings (J230) went to `.npmrc`. package.json's `pnpm` block ignores `enableGlobalVirtualStore`
  (a scratch install made a local `.pnpm`). `.npmrc` is a repo-kit file, so sync now reports it locally edited here
  until phase 2 folds the two lines into repo-kit's copy (Jake's pick). `assert-store-layout` still sees the global store.
- The "Ignored build scripts: esbuild" warning was there before: the HEAD config gives it too.
- Also dropped `scripts/blender/targets.json`: it named a `build.sh` that never existed here.

## Main only, no landing (D29)

- Jake: put this repo into "many agents on main only, no worktrees, no landing" mode. AGENTS.md's two-mode git
  section (J290) and its landing block became one main-only section; D29 in docs/decisions.md replaces D27's 11-12
  relaxation. `land.config.json` went: it held only land's defaults, and nothing lands here now.
- `scripts/land.mjs`, `worktree*.mjs` and their `test/tooling` tests stay: repo-kit stamps them. Dropping them is
  phase 2, and the mode itself is a meta call (J290) for Jake to make org-wide if he wants.

## guard-git-add: an apostrophe hid the pathspec (A2)

- The guard stripped single-quoted strings, then double-quoted ones, in two sed passes. An apostrophe inside a
  double-quoted message (`"AGENTS.md's"`) opened a fake single-quoted string that ran to the next `'` in the
  command and ate the `-- <paths>`, so a pathspec commit was refused as bare. One pass with an alternation now:
  the leftmost quote wins, and `\"` escapes stay inside their string. Five new cases in `hooks.test.mjs`, two red
  before the fix. The hook is repo-kit's (agent-sync), so the fix diverges here until repo-kit takes it.

## test/tooling moves to src/test/.kit (A3)

- Jake: "move test/tooling into src/test/.kit/ ... a good compromise". The four still in use moved there:
  lane-live, leftovers-report, owned-scratch, chrome-keychain. The five worktree and land tests went (worktree-guard,
  land-fixture, disk-land, reap-report, keep-copy): D29 retired that tooling here. Imports gain one `../`; the
  `pnpm check` list, the lint and format ignores, `docs/chromium.md` and `.githooks/session-brief.test.mjs` follow.
- Top level now: `docs/ kit/ project/ scripts/ src/`. A repo-kit sync would put `test/tooling/worktree-guard` and
  `chrome-keychain` back and flag `session-brief.test.mjs`, until repo-kit learns the path (phase 2).

## kit/cli and kit/test go (A4, A5)

- `kit/cli` was a placeholder `shard-showcase` bin with only `--help` and `--version`; nothing called it.
  `kit/test/helpers/git.ts` was a temp-git helper no test used. With both gone there is no TypeScript left, so
  `typecheck`, `test`, `test:kit` and `kit/tsconfig.json` went too (pre-commit runs typecheck only when the script
  exists). Also dropped the stale `public/**` and `vitest.config.ts` lint ignores; `docs/dev.md` and
  `docs/design.md` no longer list a `src/scripts/` that never existed.

## pnpm settings back in pnpm-workspace.yaml (A6)

- Jake regretted the `pnpm` key in package.json. pnpm 10's root settings file is pnpm-workspace.yaml, so it
  is back, settings only (no `packages:`): `allowBuilds`, the 80 `ignoredOptionalDependencies`, and the global-store
  pair. `.npmrc` is byte-identical to repo-kit's again. A frozen install still matches the lockfile (pnpm refuses one
  whose settings drift), and the CI cache keys list the file again.

## Bin tools install with pnpm (A7)

- Jake: flip `binDependenciesInstaller` to pnpm. `npr install` rewrote `.bin-deps/`: `pnpm-lock.yaml` and a generated
  `pnpm-workspace.yaml` (our ignored optionals) replace `package-lock.json`. `kit/bin-pins.json` now pins installer
  `pnpm` and those three hashes; the CI npr cache key hashes them too. `npr install --frozen` and `pnpm check` pass.
- `kit/bin-pins.json` and `.bin-deps/` are repo-kit's (K1a: "consumers share the exact committed binary install"),
  so this repo is off the kit profile until repo-kit moves to pnpm too (phase 2).
