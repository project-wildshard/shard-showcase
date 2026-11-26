# Repo study: the shards and the clean-rooms

> Moved from meta `docs/prototype-to-mmo/evidence/repo-study-shards-and-cleanrooms.md` at `386423cbea` into the cleanroom saga (D38, 2026-11-26).

> Written by: Claude

> **State:** point-in-time record, 2026-11-16. A read-only study by a research subagent for [STRATEGY.md](../STRATEGY.md). Scope: the nine `wildshard/shard-*` repos, both `*-cleanroom` repos, `leftover`, and a light look at `wildshard-singleplayer`. Nothing was built, run or changed. The claims the strategy leans on hardest were re-read in the source by the lead agent; they are listed in the folder [README](../README.md).

## What Wildshard shards are today, and how the two clean-room prototypes became shards

I only read files and ran read-only git, ls, wc and grep commands. "Verified" means I read it in a file or git log. "Inferred" means it comes from docs or names, or from a partial check.

**The most important finding:** in both precedents the shard already existed before the clean-room. The clean-room was a look study made afterwards, and its look was then poured back into an existing shard that already had gameplay. Brasscap went shard → clean-room → shard again. That is the opposite of the owner's plan, where the prototype comes first and MMO features are "stamped in" later.

Two repos you didn't list also exist: `shard-format` (the format spec, which held Brasscap before it got its own repo) and `shard-templates`. Mossgate's shard lives in a third, `sharddev`.

## 1. Anatomy of a shard repo

**Verified: what the content is written in.** A shard is (a) JSON data rows, (b) TypeScript generators that run at build time and emit a "shardfile", (c) GLB/KTX2/audio assets, and (d) small AssemblyScript behaviour scripts (`.as` files) compiled to WASM. The scripts run in the live game in a sandbox, through a fixed set of commands such as `Do.strike`, `Do.field`, `body.teleport` and `ws_view`.

So shards do contain runtime gameplay code, but only as these limited scripts. TypeScript never ships to the live game. Brasscap's three.js scene code runs only when `wildshard build` or `wildshard watch` runs (`src/shard.config.ts:1-5`). The Showcase plan states the rule outright: "0 % custom TypeScript… shared hosts, data rows and AssemblyScript only."

**`shard-brasscap`** (238 tracked files, 36.7k text lines, 9.3 MB tracked):

| Bucket | Lines | Where |
|---|---|---|
| Data rows | 10.9k | `src/rows/` (35 JSON files). `world/edge.json` alone is 6,238 lines of pretty-printed colour triples, and `sim/client-scripts.json` is 1,049 |
| Scene generators (TS) | 944 | `src/generators/` (world.ts 546, sideDoor.ts 70, …) |
| Runtime scripts (AssemblyScript) | 109 | `behaviour/wyrm.as` 46, `sources/gate.as` 36, `sand.as` 27 |
| Build-time GLB generators and their tests | 7.2k | `tools/` (canyon.ts 3,657). `canyon.glb` and `depot.glb` are no longer referenced anywhere in `src/` or `package.json`, so they look like dead weight |
| Tests | 1.1k | `test/` |
| Journal | 363 | `project/journal/` |
| Stamped process | ~15.7k (43%) | `scripts/` 4.7k, `.agents/` 3.4k, `.githooks/` 3.0k, `pnpm-lock` 2.2k, `kit/` 1.1k, CI 320, AGENTS/docs |

**`shard-pine-hollow`** (1,854 files, 117k text lines, 508 MB tracked, 1,037 binary files):

| Bucket | Lines |
|---|---|
| `src/data` | 46.0k (85 files; `lookGraphs.json` alone is 31.7k) |
| `src/generators` | 21.8k (278 TS files) |
| `src/blender` (Python) | 5.6k |
| `src/behaviour` | 687 (16 `.as` files: king, elites, night, contracts, director…) |
| `public/assets` | 9.7k text plus about 1,000 GLB/KTX2/WebP/M4A files |
| Tests | 6.6k |
| Stamped process | ~21.1k (18%) |

**Stale READMEs (verified):** Pine's `src/README.md` describes TS folders `world/`, `species/`, `combat/` (for example "`LeverRifle extends Firearm`"), and `sky-reach` cites `behaviour/islet.as`. None of these exist. The READMEs date from the singleplayer era, when shards were TypeScript plugins.

## 2. The nine shards

| Repo | Theme | Tracked / .git | Files, commits | Distinctive | Status field in its own manifest |
|---|---|---|---|---|---|
| brasscap | Sunset canyon, tin bandits | 9.3 MB / 6 MB | 238, 47 | Lever rifle, scattergun, long rifle; 3 bandit camps (respawn after 90 s); Dust Wyrm boss in 2 phases; 8-step quest; side door moved by a lever | `hidden` (on staging per meta plans) |
| driftwood | Toon island | 48 MB / 42 MB | 986, 117 | Boat mover (`waves`), chain bridge mover, zipline, Drowned Captain boss, keepsakes | `live`, order 1 |
| dunes | Dusk dunes, bullwhip | 12 MB / 11 MB | 580, 94 | Flying ray, Matriarch boss, signal-tower quest | `experimental` |
| nalati | Painterly steppe | 162 MB / 147 MB | 1,354, 132 | Horse riding and taming (`riding.as`, `mounts.as`), herds, Titan boss; 36 `.as` files | `earlyAccess` |
| nine-dragon | Vertical neon city | 50 MB / 46 MB | 750, 108 | Monorail train, gondola and drones (look only); portal teleport; grapple; no creatures | `experimental` |
| open-plots | 20 diorama plots | 45 MB / 47 MB | 985, 99 | Data-only, 20 outputs | `hidden` / `earlyAccess` |
| pine-hollow | PBR boreal forest | 508 MB / 490 MB | 1,854, 118 | Canoe you ride (winch mover), zipline, lever rifle with sights, crossbow, night waves, Antler King, contracts | `earlyAccess` (its README says `live`) |
| showcase | "Kitchen Sink" | 1.8 MB | 314, 42 | **No `src/` at all.** 9.7k lines of plans, "nothing built" | none |
| sky-reach | Floating islands | 40 MB / 48 MB | 681, 103 | Rising-islet movers, rope bridges, Storm Roc boss | `experimental` |

- **Disk use is mostly not content.** `du` shows 0.8–4 GB per repo, but `node_modules` accounts for about 1.5–1.8 GB of that in most of them.
- **Brasscap is on a newer toolchain than the rest.** It alone pins sdk 0.3.3 and engine 0.1.24. The other eight are on sdk 0.2.x and engine 0.1.18.
- **Live status is unclear.** No shard's own docs say it is live on play.wildshard.io; there is only each manifest's `status` field. Meta plans record production at engine v0.1.22.

## 3. The clean-room precedent

### Brasscap

- **The clean-room (verified):** `brasscap-cleanroom` is a standalone three.js + rapier page deployed on Vercel. It has about 1.55k lines of source (`world.js` 563, `main.js` 274, `phone.js` 247, `actors.js` 184, `bake.js` 129, `util.js` 122) plus about 200 lines of capture scripts. It has 11 commits between 11-13 18:54 and 11-14 00:52, about 6 hours. It contains posed bandits, the Wyrm, a first-person weapon view, baked lighting and a performance path for phones.
  - **It has no gameplay.**
- **The order of events (verified from git):**
  1. 11-11 20:36 to 11-12: Brasscap is built as a data shard ("Template 2", "a Blender-only shooter") in `shard-format/corpus`, about 28 commits covering the rifle, bandits, gate, Wyrm and quest.
  2. 11-13 18:35: the owner complains about the look. The clean-room is started right after, under the rule "imports nothing from engine…".
  3. 11-13 19:20–23:33: the clean-room's colours, lights and actors are hand-ported back into the data shard. This needed new format features (`2026-11-13-render-match.md`, `brasscap-cleanroom-port.md`).
  4. 11-14 02:40: `shard-brasscap` is created as its own repo.
  5. 11-15 10:22–13:42: the clean-room's JS is copied almost verbatim into TS generators and becomes the scene. The data shard's gameplay rows are layered on top with `defineShard(..., {extend: gameplay})`. `world.ts` (531 non-blank lines) matches the clean-room's 544.
  6. 11-15 15:00 onward: about 30 content commits. The whole Brasscap story took about 5 days and roughly 80 commits across two repos.
- **What was lost (verified in the port's own comments):**
  - The weapon view, AO and lamp baking, and dust sprites were dropped (`world.ts:1-14`).
  - Per-face brightness jitter was dropped.
  - The horizon mesas shrank from 320 m to 195 m and the clouds from 900 m to 200 m to fit the 500 m cell.
  - The posed creatures were replaced by live ones.
  - The Wyrm first came out person-sized and was later scaled ×5 (commit `1fd33ce`).
- **The engine needed fixes too.** `2026-11-15-play-probe.md` records that on staging the owner found "no gun, no enemies". The server held the rifle but never handed it over, and the page drew none of the 12 creatures. Fixing it took engine changes (TC-E1a–d) before any row changes.
- **Why 1.7k became about 21k content lines (36.7k with stamped process):** almost none of it is the clean-room.
  - Gameplay rows the clean-room never had.
  - 7.2k lines of GLB generators.
  - About 6k lines of machine-shaped edge data.
  - About 15.7k lines of stamped process.

### Mossgate

- **The clean-room (verified):** `mossgate-cleanroom` is a standalone three.js + rapier page: `world.js` 1,145, `main.js` 404, `textures.js` 336, `sky.js` 92, with 14 commits on 11-13 to 11-14.
- **Where it went (verified):** it did not become its own repo. It became `sharddev/src/shards/mossgate/`: 1,356 lines (`world.ts` 1,001, textures 249, sky 64), 3 commits from 11-14 to 11-16, described as "a shard whose only source is a three.js scene" (`shard.config.ts:1`). It is "Template 1" (sword).
- **Inferred:** per `TEMPLATE-E2E-PLAN.md`, its gameplay is a separate track (TC-M rows).

## 4. Trains, movers, teleports, first-person

- **Moving things are declared as data that the engine runs.** The engine's mover kinds (`shard-format/src/format/movers.ts`) are platform, chain and channel. They can be driven by `track`, `winch` (ride/carry) or `pendulum`. Coordinates are clamped to ±250 m.
- **Nine Dragon's monorail train (verified, `behaviour/movers.as`):** a look-only script slides it along x and wraps at a 300 m loop. It has no collider and no riders.
- **The nearest thing to a train you can ride:** Pine's canoe, a `winch` mover in `ride` mode with `carry` (`generators/canoe.ts:26-30`). The other movers are Driftwood's boat and bridge, Sky Reach's islets, and Brasscap's side door (a `track` mover triggered by a shared value from `gate.as`).
- **Teleport (verified):** Nine Dragon has a portal ride (`data/portals.json`): a trigger box, then a fade out / hold / fade in over a "veil", then a landing node. The format allows only "two explicit directed links… no arbitrary teleport target" (`portalLink.ts:9`). Driftwood's `barrels.as` uses `body.teleport` only to reset barrels.
- **Nobody has built a moving vehicle that carries players and teleports between tunnels.**
- **Camera perspective:**
  - Brasscap is first-person; the clean-room uses the engine's 1.68 m eye height.
  - The engine has 89 files mentioning "viewmodel".
  - "Third-person" appears only in a cosmetics comment (`engine/src/client/game/cosmetics/cosmetics.ts:8`). **I found no third-person shard type** (grep only, so treat as inferred).
- **Enemy camps and waves:** these are data rows. Brasscap uses `creatures.groups` packs, encounter rows and strike rows (capped at 20 m range), and its boss is scripted in `wyrm.as`.

## 5. Duplication between shards (verified with git blob hashes)

- 122 files are byte-identical in all nine repos.
- Each repo has 125–175 files that are byte-identical with 5 or more other shards: `.agents/`, `.githooks/` (2,968 lines everywhere), `scripts/` (land/worktree/agent-sync), `kit/`, `lint/`, and CI. The publish workflow is "stamped as kit.mjs renders them".

| Repo | Stamped process share of text lines |
|---|---|
| Showcase | 96% |
| Dunes | 63% |
| Brasscap | 43% |
| Pine Hollow | 18% |

On top of that, the unique content in big shards is dominated by single generated-looking files (Pine's 31.7k-line `lookGraphs.json`, Brasscap's `edge.json`).

## 6. `leftover` and `wildshard-singleplayer`

- **`leftover`** (212 files) is the owner's "dumping ground". All that is left in it is a 253-line R2 packs Cloudflare Worker (`src/packs/`) plus tooling.
  - **Inferred:** per `PACKS-CDN-PLAN.md`, packs.wildshard.io now serves R2 directly, and the Worker is waiting to be removed once its traffic is zero. Nothing appears to depend on leftover.
- **`wildshard-singleplayer`** is the original monorepo: 18.6k files, 24,952 commits since 09-16, 69 GB on disk. Most of the files are `progress/` (8.4k) and `art/` (7.2k). Its `src/` holds 1,188 files, all under `src/shards`.
  - Every shard was lifted out of it with fresh history (for example "import shard-pine-hollow at 65925fa862").
  - **Inferred:** meta decision J189 says "singleplayer is archived", and its last deploy commit (`b43594f01e`, 11-13) is a kill switch that redirects the retired origin to play.wildshard.io.
  - No shard `package.json` depends on it. The engine has only a grid file named `singleplayer.json`.
