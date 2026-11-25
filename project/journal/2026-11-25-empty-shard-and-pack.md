# A bare shard in src/, and pack that uploads

Asks A13, A14; closes A1 phase 1 and A9.

- `wildshard new --empty` only makes a new folder, so it ran in tmp/ and only its `src/` came over
  (`generators/`, `shard.config.ts`), reformatted by our oxfmt. Its package.json, tsconfig and oxlint config are
  what we already have (ours are stricter); GUIDE.md and the skills wait on sharddev's `update` (plan row K6).
  The strict gates now have real code to bite on: lint, tsc, format and `wildshard check` all pass.
- `pack` was just `build`, which writes a draft (sdk 0.2) that upload refuses. Now it is build, `wildshard
  prepare` (phone WebKit recording; 3.5 s with the engine client cached), build of the prepared folder: sdk 0.3.
  It must be `pnpm run pack`: bare `pnpm pack` is pnpm's own tarball command and never reaches the script.
- A1 phase 2 (repo-kit and sharddev fitting the lean layout, the hc port upstream, set-label) is a plan now:
  docs/plans/opus-2026-11-25-kit-phase-2.md. Jake: leave origin/art and origin/website alone.
