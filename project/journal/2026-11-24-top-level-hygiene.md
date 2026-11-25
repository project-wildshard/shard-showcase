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
