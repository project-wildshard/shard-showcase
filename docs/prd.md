# shard-showcase: PRD

Status: active 2026-11-25. Rewritten from the Kitchen Sink plan (ask
A15); Jake: "its the whole purpose of the repo".

Living doc: **what** this repo is for and **why**. How it is built is
`docs/design.md`; decisions are `docs/decisions.md`; the plan is
`docs/plans/2026-10-20-opus-kitchen-sink-PLAN.md`. Requirement ids (`R-1`) are stable: cite
them from plans, commits and tests.

## One line

The Showcase Template: one shard that holds every engine feature, built
from data, and plays like an MMO zone from level 1 to 20.

## Requirements

- **R-1** One 500 × 500 m cell in the 5 × 5 grid, in the orange-and-grey
  look, polished, never placeholder (KITCHEN-SINK §1). It takes the
  hologram plot's cell when it is done.
- **R-2** Every engine feature in one place, authored with **0 % custom
  TypeScript** (G524): shared hosts, data rows and AssemblyScript. A
  feature that needs shard code becomes engine host work instead.
- **R-3** West half non-combat (hub, practice, traversal toys); east
  half combat only (six level bands, elites, the mini dungeon, the
  boss).
- **R-4** Levels 1 to 20, XP only from kills, at most 8 attributes
  shared by players and enemies.
- **R-5** Plays end to end on the phone tier, level 1 to the Crate
  Titan, within 1.2 GB; other shards play unchanged.
- **R-6** Built with sharddev (`pnpm run pack`, prepared) and uploaded
  to api-server.

## How it gets built

In vertical play slices, west half first (Jake, 2026-11-03): each slice
does only the engine work its piece needs, builds that piece, and
migrates every other shard it touches. The slices are in
`docs/plans/kitchen-sink-v2/slices/`. Nothing is built until Jake says
"build it".

## Not this repo

- Engine, SDK or format code (engine, sharddev, shard-format). Shared
  host work is done there, inside the slice that needs it.
- Validating or cooking the shard file (api-server and the engine's
  cook worker).
- The level 1 to 20 rollout to other shards (KITCHEN-SINK §8).
