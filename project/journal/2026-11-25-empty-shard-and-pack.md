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

## Blue sky, green ground

The bare shard was a flat gray plane under a gray sky (`emptyShardfile`:
heights 0, colours 0.5, no look). Jake: "can we have blue sky and a flat
green ground". Swapped the entry to the SDK's scene API (`defineShard`,
as its authoring-slice does): `world.sky` a two-colour gradient,
`world.ground` flat with one grass colour, a hemisphere light and a sun.
`import * as THREE` trips our strict lint (import/namespace cannot see
through three's re-exports), so it uses named imports.

## K5 was done elsewhere

The dotfiles agent made set-label.sh write `hc label goal=<tag>`
(dotfiles 03cc526), so plan row K5 is ticked; peers.sh shows goals.
Phase 2 is now the four repo-kit rows plus sharddev 0.5.0.

## Phase 2 split by owner

Jake: "yeah move the plan into the repokit repo". Rows K1-K4 now live
in repo-kit (f970ade); its cleanup-coverage test read this checkout and
went red on our moved kit, so shard-showcase waits in its pending list
(01911a2). What lands here is opus-2026-11-25-sdk-0-5-and-kit.md: SDK
0.5.0, `wildshard update --guide docs/GUIDE.md`, and the re-stamp.
