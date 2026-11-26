# Repo study: the engine

> Moved from meta `docs/prototype-to-mmo/evidence/repo-study-engine.md` at `386423cbea` into the cleanroom saga (D38, 2026-11-26).

> Written by: Claude

> **State:** point-in-time record, 2026-11-16. A read-only study by a research subagent for [STRATEGY.md](../STRATEGY.md). Scope: `wildshard/engine`. Nothing was built, run or changed. The claims the strategy leans on hardest were re-read in the source by the lead agent; they are listed in the folder [README](../README.md).

## Wildshard engine: what it is today, measured against the train-shard intent

I only read files and ran read-only git, grep and wc commands. The repo is `~/projects/games/wildshard/engine`, package `@wildshard/engine` v0.1.29. Two labels mark how sure each point is: **[code]** means I read the source, **[docs]** means it comes from docs, comments or file names only.

## 1. Architecture map and size

There is one pnpm package (`pnpm-workspace.yaml` lists only `.`). It has 7,877 tracked files and 588,289 lines of code (`.ts/.tsx/.mjs/.js/.py/.sh/.css`, with generated files excluded). That matches your 588k figure.

| Area | Lines | Share |
|---|---|---|
| `src/` runtime code (no tests) | 277,976 | 47% |
| — `src/client` | 181,769 | |
| — `src/shared` | 55,019 | |
| — `src/server` | 36,900 | |
| — `src/cook` | 3,455 | |
| Tests (49,530 next to the code in `src/` + 143,997 in `test/`) | ~193,500 | 33% |
| `scripts/` (776 top-level files plus folders such as `parity/` and `app-build/`) | 106,666 | 18% |
| `lint/`, `.githooks/`, `.agents/`, `kit/` | 9,530 | ~2% |
| `.github/` (YAML) | 2,184 | |

Data not counted above:
- 564k lines of JSON under `test/`, mostly parity baselines such as `test/parity/baselines/m5/far-reach.desktop.json` at 38k lines.
- 263k lines of JSON under `budgets/`.
- 28k lines of journals under `project/`.

Largest subsystems:
- `src/client/engine/render`: 17.2k lines (+6.8k tests)
- `src/client/game/grid`: 17.8k (+5.4k tests)
- `src/client/game/shardfile`: 24k
- `src/client/engine/world`: 11.1k
- UI/HUD: about 18.2k in `src/client/engine/ui` plus `src/client/game/ui`

By theme inside `scripts/`: release, deploy and VPS scripts are about 6.7k lines plus 3.2k in `scripts/app-build`. Gate-like scripts (land, push, check, lint, ratchet, budget, worktree) are about 13k. Cook and bake scripts are about 2.2k. The cook code in this repo is small (`src/cook` is 3.5k). The shard schema lives in a separate package, `@wildshard/shard-format` (377 files and 61.5k lines in the 0.5.10 copy installed here).

## 2. Runtime model

- **Renderer** **[code]**: three.js 0.186.0 with WebGL only. `src/client/engine/render/renderer.ts:26` says `type Renderer = THREE.WebGLRenderer`, and line 5 says "No TSL, no WebGPURenderer". Physics is Rapier (`@dimforge/rapier3d-simd`), and the UI uses Preact.
- **Hosting** **[code]**: there are no Cloudflare Durable Objects; grep finds no `DurableObject` anywhere. Three hosts exist:
  - **Dedicated server:** Node. `src/server/host/dedicated/main.ts` uses `node:http` and `worker_threads`. Each worker thread runs cells on a 60 Hz clock (`cellHost.ts:1`), and player saves go to PostgreSQL.
  - **Standalone:** the server runs in a Web Worker inside the browser as a listen server (`src/server/host/standalone/serverWorker.ts`).
  - **Pages:** static Cloudflare Workers only (`pages/wrangler.jsonc`).
  - `docs/vps-setup.md:361-372` records 25 resident cells on four workers in production.
- **Netcode** **[code + docs]**: the server is authoritative (decision J5 in `docs/decisions.md`). The fixed step is 1/60 (`src/shared/engine/core/fixedStep.ts:3`). The client predicts and interpolates (`src/client/engine/net/predictor.ts`, `interpolator.ts`), and the server keeps a hit history for lag compensation (`src/server/engine/combat/rewind.ts`).
- **How a shard loads** **[code]**: a shard is uploaded as a "shardfile" (JSON + assets), cooked into packs, and loaded as data. The schema has 72 declared sections and 63 engine-owned client feature "kinds" (`@wildshard/format/src/tools/runtime-hosts.json`).

### Can a shard bring its own gameplay code? Partly, through sandboxed Wasm only.

**[code]**
- **Server-side scripts:** `src/shared/engine/script/host.ts` runs WebAssembly modules supplied by the shard (`sim/scripts`, admitted by SHA-256 in `src/server/game/shardfile/scripts.ts`). A module exports `on_tick` and can return only four numeric effects (`effects.ts:2`): `field`, `spawn`, `event`, `position`.
  - Those effects are bounded: positions must be within ±250 (`effects.ts:13`), and fields, archetypes and events must be declared in advance.
  - Hard caps (`scriptLimits`): 9 modules, 24 MB memory, 128 effects and 8 spawns per tick, 2M fuel per call.
  - A module can also make 4 query kinds plus a parameter query.
- **Client-side scripts:** "view programs" (`viewProgram.ts`) are Wasm that can only move objects, bones, uniforms or the camera it is lent. Its own comment says "a rendered pose is a visual only and never an authority position."
- **No arbitrary TypeScript from shards:** the TS plugin class `ShardPlugin` (`src/client/game/plugin/context.ts:195`) is labelled "trusted". For a cooked shard product it is an empty class (`hybrid.ts:36` `ClientPlanRuntime extends ShardPlugin {}`, and it throws unless `firstParty`).
- **Bottom line:** custom behaviour has to be a numeric Wasm state machine that drives engine-owned systems.

## 3. The train test

**Fits the 500 m zone** **[code]**: 500 m is a hard platform constant. `CHUNK_SIZE: 500` and a 500×500×500 cell are set in `src/shared/engine/core/config.ts:4,15`, positions are clamped to ±250 everywhere, and the vertical range is 250 m below and above. A 500×500 canyon fits exactly.

**Moving platforms that carry players exist** **[code]**:
- `KinematicMover` (`src/shared/engine/physics/mover.ts`) is a Rapier kinematic body built from up to 128 boxes.
- `CharacterMotor.carry()` (`CharacterMotor.ts:399-413`) pins a player's feet to the deck.
- Limits from the format's `movers.ts` and `moverMotion.ts`: at most 32 movers per shard. Keyframe tracks allow at most 10 keys, with loop modes `once`, `repeat` or `pingpong`. Drivers are `waves`, `winch`, `static`, `track` or `pendulum`.
- A guest Wasm module can own a mover's pose.
- A 10-key track is coarse for a big looping train path, so a custom Wasm driver would probably be needed (inferred).

**The teleport would drop the riders** **[code]**: `CharacterMotor.carry()` ends the ride if the deck's new pose puts the feet more than 1.5 m from where they were ("a respawn, a quest's teleport: that ends the ride"). A deck that jumps from one tunnel to the other would therefore leave everyone behind. I found no feature that teleports a group or a mover together with its riders.

**Teleporters** **[code]**: `portal.ride` (`src/shared/game/shardfile/portalRide.ts`, format `portalRide.ts`) is a walk-in portal with a fade and landing nodes, for the player only. `portalLink` handles links between zones.

**First-person shooting** **[code]**:
- The game is first-person by design. `src/client/game/cosmetics/cosmetics.ts:3` says "The game is first person and the player has no body mesh."
- A hitscan firearm exists (`src/client/game/plugin/heldFirearm.ts`).
- Weapon families are `bow`, `cone`, `firearm`, `lash`, `melee` and `thrown`, with projectile physics in `src/shared/engine/combat/projectile*.ts`.

**Third-person action does not exist** **[code]**: grep finds no third-person, orbit or chase camera; the only mention is a comment in `cosmetics.ts`. There is no shard-type or genre field in the format.

**Enemies, quests and collectibles** **[code]**:
- **Enemies/AI:** server AI 3.5k lines + shared AI 5.2k + population 3.3k. Declared `actors/creatures`, `actors/spawns`, `combat/encounters` and spawn scripts. Today's commits mention ranged "ledge marksmen".
- **Quests:** a declarative schema (format `quests.ts`, 333 lines) with steps, markers, region/death/script triggers and dialogue. About 9.7k runtime lines across the quest folders.
- **Collectibles:** `collections/displays`, `bag.finds`, achievements.

**HUD** **[code]**: a shard can declare only 5 UI kinds, at most 64 entries (format `ui.ts`): `marker`, `counter`, `bagPanel`, `bossPanel`, `relabel`. The format describes them as plain data "the platform draws in its own HUD style and slots". A shard cannot bring its own HUD.

## 4. MMO features you could "stamp" onto a zone

All verified in code:
- **Identity:** device identity plus a `Name#1234` tag (`saves/names.ts`, migration `0004-names.sql`). There is no login, password or OAuth anywhere.
- **Persistence:** PostgreSQL `player_save`, keyed by player, epoch and shard (`0001-saves.sql`). The `PlayerDoc` holds position, health, quest book, purse, pack, gear and ledger, and is "one player's whole save on one shard" (`playerDoc.ts`). So inventory is per shard.
- **Cross-shard profile:** the only thing that travels between shards is a profile of titles, cosmetics and achievements (`0005-profile.sql`). The database stops shards from granting these.
- **Chat:** room and proximity chat with a filter (`chatWire.ts`, `chatFilter.ts`).
- **Voice:** voice relay over Cloudflare TURN.
- **Travel:** a world grid of cells, with entry through zone gates without a page reload (v0.1.29 changelog, `crossing.ts`, `src/shared/game/grid`).
- **Missing:** no parties, guilds, friends, trading UI or leaderboards. "party" appears 62 times but never as a system.
- **Coupling:** all of these are engine-owned systems turned on by sections in the shard's data. A shard does not import them as code.

## 5. Complexity and health signals

- **Age and pace** **[code]:** the repo began 2026-11-04 by importing earlier singleplayer code ("ENGINE-CUT", `docs/plans/opus-2026-11-05-engine-import.md`). It has 2,440 commits in 12 days, up to 469 a day, from many agent "lanes" working at once.
- **Commit mix over two weeks:**
  - By type: 1,007 `fix`, 561 `test`, 371 `feat`, 97 `perf`.
  - Top scopes: grid 187, build 166, test 103, ci 102, boot 92, server 91, net 77, ci21 77, release 72.
- **Process weight:**
  - 41 package scripts. `pnpm check` chains 13 steps.
  - 16 CI workflow files (`ci.yml` alone is 594 lines).
  - 30 git hook files and 76 lint files, including many debt, ratchet and baseline JSONs.
  - `AGENTS.md` (164 lines) is mostly worktree, land, push-gate and CI-red procedure.
  - `project/journal` holds 954 entries; a journal entry is required for any commit over 30 lines.
- **Stale or missing docs:**
  - `docs/design.md` still says "Only the scaffold exists".
  - The layout section of `docs/dev.md` mentions zod and esbuild, but the code uses valibot and Vite.
  - `docs/SHARDS.md` is referenced in `manifest.ts` but does not exist.
  - The CLI (`src/cli/main.ts`) only has `serve`. The author toolkit is a separate repo, `sharddev`, which `docs/prd.md` lists under "Not this repo".
- **Legacy markers in `src/`:** "legacy" appears 641 times in 199 files and "retire" 1,855 times in 453 files. Only 37 TODOs. Examples include "trusted legacy view callbacks" (`mover.ts:157`) and "Frozen legacy mover adapters".
- **Timings** **[docs]:** about 70 s for the split push gate, about 3 min to land, a 25-minute CI job limit, and an estimated 45–60 minutes for nightly runs (`docs/nightly.md:143`). I found no documented per-shard cook time.
- **Stale local install:** the checkout's `node_modules` points at shard-format 0.5.10, but the lockfile pins 0.7.0. I checked that the movers, UI and script-limit constants quoted above are the same in 0.7.0.

## 6. Recent direction (the last 150 commits are all from 2026-11-16)

- **Grid and zones:** entering zones in the same page, offline gates, a road set, movers in data cells.
- **Release churn:** versions v0.1.26 to v0.1.29 were all released that day.
- **Boot:** keeping menus live while loading.
- **Hardening:** nightly, test pinning ("ci21") and network-lag tests.
- **Content features:** water splashes, detail layers, creature layer policies, shard pinning from GitHub Actions.

Over the two weeks the emphasis is the dedicated server and VPS, the cell grid, boot and loading speed, CI and landing tooling, and moving to data-driven ("native/declared") hosts.

## For and against the train shard

**For:**
- The 500 m cell matches the zone exactly.
- Kinematic decks that carry players, Wasm-driven movers, hitscan FPS, enemy encounters, quests and collectibles all exist.
- The server is authoritative with prediction.

**Against:**
- A shard cannot ship arbitrary TypeScript, only numeric Wasm within tight caps.
- A deck that teleports releases its riders by design (the 1.5 m check).
- Movers are limited to 32 per shard and 10 keyframes per track.
- The HUD is limited to 5 declared kinds, so "normalising the HUD" means rewriting it in those kinds rather than porting it.
- There is no third-person mode and no shard-type field.
- Turning a three.js prototype into a shardfile means re-expressing it in the 72 data sections. The tool for that lives in `sharddev`, which this report did not examine.
