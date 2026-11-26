# Inventory: every section, page kind, server host and the script layer

> Moved from meta `docs/prototype-to-mmo/evidence/inventory-sections-hosts-scripts.md` at `386423cbea` into the cleanroom saga (D38, 2026-11-26).

> Written by: Claude

> **State:** point-in-time record, 2026-11-16. A read-only study by a research subagent for [STRATEGY.md](../STRATEGY.md), saved as reported. Nothing was built, run or changed. Each study marks what it read in code or docs against what it inferred.

## Wildshard today: an inventory of the format, the engine hosts, the script layer and the cost of adding a mechanic

Some of this I read directly in code or docs, and some I worked out. Everything in tables or quotes was read at the paths given. Text marked **(inferred)** is my judgement, and that includes **every bucket assignment (a/b/c/d)**. Repo heads I read: shard-format `cf745e1` (v0.12.0), engine `2f7b035dc`, sharddev `82f441e`, meta working tree, 2026-11-16. Nothing was modified, built or run.

---

## 1. The full lists

The generated tables are in `/Users/raynos/projects/games/wildshard/shard-format/docs/RUNTIME-CONTRACT.md`:
- the 72 sections are at lines 62–133;
- the 63 kinds are at lines 192–254;
- the 18 stages are at lines 265–282;
- the 46 hosts are at line 292.

Users per host and kind come from three meta files:
- `/Users/raynos/projects/games/project-wildshard-meta/project/archive/server-parity/HOSTS.md`
- `/Users/raynos/projects/games/project-wildshard-meta/project/evidence/host-ruler/inventory-2026-11-13.md`
- `/Users/raynos/projects/games/project-wildshard-meta/docs/audits/2026-11-15-one-format-audit.md`

Shard abbreviations: Dr Driftwood, Pi Pine Hollow, Na Nalati, Ni Nine Dragon, Du Dunes, Sk Sky Reach.

**Bucket rule I applied (inferred):**
- **(a)** is anything an engine for any genre needs: space and geometry, rendering, physics, navigation, audio, time and environment, state and persistence, events, script.
- **(b)** is a named gameplay mechanic.
- **(c)** is a platform or MMO service: HUD chrome, economy, cosmetics, discovery, travel.
- **(d)** is tooling and packaging.

### 1a. Sections: all 72

The schemas are in `src/format/sections.ts`, `src/format/platformDataSections.ts` and `src/format/shardSchema.ts`.

| # | Section | What it holds / does | Engine host (side) | Bucket |
|---|---|---|---|---|
| 1 | `actors/creatures` | Creature brains (named presets: pursue, grazer, diver, guardian, perch-hunter, skirmisher, challenge-grazer, ram-grazer, orbit-diver, script), groups, spawns | `installDeclaredBrains` (server) | b |
| 2 | `actors/crowds` | Instanced flocks: count, range, run/walk/graze speeds, bleat cue (`crowds.ts`) | `prepareDeclaredCrowds` (both) | b |
| 3 | `actors/moves` | Named fixed-step steering moves: stalk, dive, takeoff, ring-run, burrow, surface, perch, orbit, climb, relocate… | `ActorMoveRunner` (server) | b (inferred: locomotion behaviours a generic engine would script) |
| 4 | `actors/npcs` | Quest NPC bindings | `installDeclaredQuestHost` (server) | b |
| 5 | `actors/return-scripts` | Stateless Wasm "return program" modules (v1/v2 project) | `ReturnProgram` (both) | a (script) |
| 6 | `actors/spawn-scripts` | Spawn-group catalogue: recipes, species, sites, plus a v1/v2 script per slot | `SpawnScript` (server) | a (spawner + script) |
| 7 | `actors/spawns` | Placed creature spawns (`runtime.spawns`) | `installDeclaredBrains` (server) | a (instance placement) |
| 8 | `actors/species` | Open species rows: kind label, body, temperament, senses, abilities, harvest | `speciesResolver` / `clientSpeciesLooks` | b |
| 9 | `actors/species-programs` | First-party species programs (the second creature path) | none (metadata) | b |
| 10 | `actors/strikes` | Creature strike table that species programs name | none (creature host) | b |
| 11 | `audio/audio` | Cues, ambience, score | `installDeclaredAudio` (page) | a |
| 12 | `client/plan` | The page-feature list (63 kinds below) | `installClientPhase` (page) | d (dispatch manifest) |
| 13 | `collections/displays` | Trophy/keepsake display parts and slots | `CollectionCatalogue` (page) | b |
| 14 | `combat/encounters` | Elite/boss phase tables, checkpoints, retry, panels | `createShardfileSim` (server) | b |
| 15 | `combat/items` | Item rows, contexts, loadout, launches | `installDeclaredItems` (both) | b |
| 16 | `combat/strikes` | Melee/ranged strike rows | `createShardfileSim` (server) | b |
| 17 | `economy/ledger` | Fact → platform profile reward mapping | `Ledger` (both) | c |
| 18 | `economy/loot` | Loot tables and barter economy | `declaredLootPresentation` | c |
| 19 | `explore/catalogue` | Explorer (model browser) references | `explorerRoster` (page) | c |
| 20 | `held/arms` | First-person held rig, camera framing, material bindings | `HeldClaims`, `HeldView` (page) | b |
| 21 | `held/equipment` | Firearm/launcher model and view rows | `HeldEquipment` (page) | b |
| 22 | `held/finishes` | Cosmetic finish locker identities | `HeldFinishes` (page) | c |
| 23 | `held/gear` | Explorer identities and counts for held families | `heldGear` (page) | c |
| 24 | `held/loadout` | Ammunition, ownership, save ABI, input, cues | `installHeldLoadout` (page) | b |
| 25 | `look/colour-functions` | Pure vec3 colour expressions on materials | `materialColourGraph` (page) | a |
| 26 | `look/hull-book` | Procedural creature hull bodies | `productHullBook` (page) | b (inferred: bespoke mesh pipeline) |
| 27 | `look/keyed-sky` | Photographic sky presets | `keyedSkyBackdrop` (page) | a |
| 28 | `look/look` | Material families, materials, curves, samplers, post, presentation | `shardfileLook` (page) | a |
| 29 | `look/map` | Minimap image | `reserveMapImage` (page) | c |
| 30 | `look/materials` | Material/look rows (`rows.looks`) | `clientMaterials` (page) | a |
| 31 | `look/painted` | Painted light, fog, clock, sky contract | `productPaintedLook` (page) | a |
| 32 | `look/rigged-hulls` | Rigged hull generator flaps | `productRiggedHulls` (page) | b (inferred) |
| 33 | `look/toon` | Toon day palette: sky, two-band light, fog | `toonLook` (page) | a |
| 34 | `models/island-library` | Fixed geometry groups, figures, collection slots | `IslandLibrary` (page) | a (mesh library; one user) |
| 35 | `player/stealth` | Grass cover, sight, HUD markup | `StealthController` (page) | b |
| 36 | `quests/directors` | Pacing director stages (optional AS handler) | `DirectorStageLane` (both) | b |
| 37 | `quests/host` | Bounded native quest composition: routes, stages | `installDeclaredQuestHost` | b |
| 38 | `quests/quests` | Flags, quests, triggers, dialogue | `DeclaredQuests` (both) | b |
| 39 | `sim/bodies` | Script-owned declared bodies: actor or dynamic prop with shape and material | `DeclaredBodyOps` (server) | a |
| 40 | `sim/client-channels` | Data-only visual expression DAG programs (no Wasm) | `ClientScriptViews` (page) | a |
| 41 | `sim/client-scripts` | v0 Wasm presentation scripts (pose, emitters) | `createShardfileClientScripts` (page) | a |
| 42 | `sim/hooks` | Named conditions (field equals) and scene events | `createShardfileScriptLane` (server) | a (event triggers) |
| 43 | `sim/plumbing` | Debug rows, input actions, tier values | `installDeclaredPlumbing` (page) | d |
| 44 | `sim/runtime-plan` | Selects the native interpreter; only kind `held-melee` | `prepareProductRuntimePlan` | b |
| 45 | `sim/scripts` | v1 decision script rows | `DecisionHost` (server) | a |
| 46 | `sim/sim` | 60 Hz fixed step, script tick divisor, v0 script refs | `createShardfileScriptLane` | a |
| 47 | `state/migrations` | State migration chain | `logicalStateFromLane` | a |
| 48 | `state/modes` | Ride gaits, grapple modes, traverse modes (zipline, updraft, ladder) | `playerModes` (both) | b |
| 49 | `state/state` | Declared typed fields, shared and player scope | `numericScriptState` | a (replicated state) |
| 50 | `ui/card` | HUD accent colour | none | c |
| 51 | `ui/compendium` | Journal entries and icons | `declaredProductCompendium` | c |
| 52 | `ui/completion` | Completion card and live stats | `installCompletion` (page) | c |
| 53 | `ui/level` | Discovery manifest metadata | none | c |
| 54 | `ui/strings` | Player-facing strings | none | c |
| 55 | `ui/ui` | HUD kinds (marker, counter, bag panel, boss panel, relabel) plus `targets`: panels, interactions, itemActions, NPC talkers | `mountDeclaredUi`, `installDeclaredTargets` | c (inferred: `targets` part is an interaction primitive) |
| 56 | `view/modules` | v2 view-lane Wasm modules | format admission | a |
| 57 | `world/collision` | Mesh collision | `installShardfileColliders` (both) | a |
| 58 | `world/days` | Day-cycle rows | `declaredDay` (both) | a |
| 59 | `world/edge` | N/E/S/W boundary profiles plus entryways to other shards | `createPortalTraversal` (both) | c (MMO grid seams/travel) |
| 60 | `world/movers` | Kinematic movers: platform, chain, static, channel; track, winch, pendulum, waves drivers; triggers; carry | `createComposedMoverHost` / `installClientMoverOwners` | a |
| 61 | `world/navigation` | Navmesh | `installProductNavigation` | a |
| 62 | `world/physics` | Raw native physics bytes | none (native host) | a |
| 63 | `world/props` | Props (now also `props.bodies`: dynamic Rapier bodies, v0.12.0) | `propColliderDescriptors` | a |
| 64 | `world/scenes` | Scene recipes and steps | `installWorldScenes` (page) | a |
| 65 | `world/spawn` | Player spawn point | none | a |
| 66 | `world/targets` | Strike targets and named spots | `WorldTargetHost` (both) | a |
| 67 | `world/terrain` | Terrain and native ground | `clientGround` (both) | a |
| 68 | `world/tiles` | Tiles, far, near, ring | `clientTileViews` (page) | a |
| 69 | `world/traversal` | Hoverboard speed cap | `createPortalTraversal` | c |
| 70 | `world/trees` | Baked tree set | `productTreeSet` (page) | a |
| 71 | `world/water` | Water bodies | `installClientWater` / `shardfileWater` | a |
| 72 | `world/weather` | Weather rows | `declaredWeather` (both) | a |

**Section counts (inferred):** a 34, b 22, c 14, d 2.

There are also 94 registered named-file families (`RUNTIME-CONTRACT.md` §4, lines 310–403). Many of them are one-mechanic documents: `combat/titan-fight`, `weapons/jian-row`, `riding/session`, `world/crag-cave` and others.

### 1b. `client/plan` kinds: all 63

Kind, side and hosts come from the generated table. "Does" comes from the `HOSTS.md` §1 column. Users come from the HR8 inventory. Some kinds were measured as a group, so their users are not split per kind.

| Kind | Side / server host | Users | Does | Bucket |
|---|---|---|---|---|
| `arena-room.entry` | view | Na | Arena kit, lair views | b |
| `audio.cues` | view | group: Sk Na Pi Du | Sound cues | a |
| `audio.scene` | view | group: Sk Na Pi Du (+ Open Plots) | Audio scene | a |
| `bag.finds` | view | Na | Finds panel, reads flags | c |
| `boss.held` | both / `heldBoss` | Sk | Storm Roc view | b |
| `boss.spawned` | view | Sk Du | Boss views | b |
| `boss.telegraph` | view | Sk Du | Strike walls/tells | b |
| `combat.targets` | both / `heldArms` | Na | Aim prediction | b |
| `content.catalogue` | both / `loadout` | Dr Na Pi | Item, shop and effect rows | c |
| `debug.expose` | view | all six | Debug | d |
| `elite.construct` | both / `windElite` | Na | Elite loan | b |
| `elite.entry` | both / `windElite` | Na | Lair views | b |
| `fx.trail` | view | Sk (one-user per HR8) | Trails | a |
| `held.claims.enter` | both / `grapple` | Dr Na Ni | Weapon slots, grapple entry | b |
| `held.claims.install` | both / `heldArms` | Dr Na Ni | Weapon slots | b |
| `held.claims.prepare` | both / `heldArms` | Dr Na Ni | Weapon slots | b |
| `held.cosmetics` | view | Na Pi | Finish locker | c |
| `held.melee` | both / `melee` | Sk Du | Melee prediction, viewmodel | b |
| `held.ranged-feel` | view | Na Pi | Camera kick | b |
| `held.ranged-page` | both / `heldRanged` | Pi | Ranged kit, finish claims | b |
| `light.emitters` | view | group: Sk Na Pi Du | Lamps | a |
| `look.painterly` | view | group: Sk Na Pi Du | Painterly look | a |
| `motion.channels` | view | Sk Du | Channels that follow movers | a |
| `page.life` | view | Pi | Flock draws, carcass timers | b |
| `player.enter` | both / `fallFloor` | Sk Du | Pitch, floor, columns | a |
| `population.homes` | view | Sk Du | Home bodies, herdless | b |
| `population.hull-book` | view | group: Dr Na Pi (+Sk Du) | Hull kit | b |
| `population.product-creatures` | view | Dr (per audit) | Creature looks | b |
| `population.wildlife` | view | Na | Wildlife | b |
| `portal.ride` | both / `portalRide` | Ni | Veil panel, ride law | b |
| `practice.course` | view | Na Ni | Practice room cards | b |
| `quest.chapter-view` | view | Na | Chapter story view | b |
| `quest.composition` | both / `questComposition` | Dr Pi | Quest page, mirrors flags | b |
| `quest.continuation` | both / `keepsakes` | Dr | Keepsakes, item effects, shop UI | b |
| `quest.page` | both / `questHost` | Sk Du | Quest, NPC prompts | b |
| `quest.reference` | both / `places` | Dr | Places | b |
| `quest.spawns` | view | Pi | Spawn puffs | b |
| `quest.views` | view | Pi | Page views (SILLY) | b |
| `quest.world` | both / `places` | Dr | Places | b |
| `riding.session` | view | Na | Mount HUD | b |
| `species.program` | view | Sk Na Du | Species looks and rigs | b |
| `state.adventure` | both / `saves` | Na | Page saves, seed flags | a (persistence) |
| `stealth.entry` | both / `stealth` | Na | Sneak ×2, crouch HUD | b |
| `strings.register` | view | all six | Strings | c |
| `taming.entry` | view | Na | Taming prompts | b |
| `timed.encounters` | both / `slots` | Na | Night views | b |
| `view.program` | both / `poseViews` | Dr Na Ni | View Wasm | a |
| `weather.fields` | view | Du | Eases scene values by quest flag | a |
| `weather.forest` | view | Na Pi | Forest weather rig, HUD | b |
| `world.ambient-life` | both / `harvest` | Dr | Flock draws | b |
| `world.assembly` | both / `collision` | Dr Na Ni | Ordered world-build stages | a |
| `world.baked` | both / `collision` | Dr | Baked tiles and boxes | a |
| `world.bind-sets` | view | Dr Na Ni Pi | Named places | a |
| `world.dressing` | both / `collision` | Na | Scatter dressing and colliders | a |
| `world.forest-page` | both / `collision` | Pi | Forest page, cave shell, terrain cut | b |
| `world.meadow` | view | Na | Grass, particles | b |
| `world.movers` | both / `movers` | Dr | Boat and bridge bodies | a |
| `world.paths` | both / `collision` | Dr Na | Trail ramp colliders | a |
| `world.runtime-hooks` | both / `fallFloor` | Dr Ni | Bounds, fall floor | a |
| `world.scenes` | both / `collision` | Dr Sk Na Du | Scene nodes, colliders, streaming | a |
| `world.sets` | view | Dr Na Ni Pi | Named places | a |
| `world.updates` | view | Dr Na (+ Open Plots) | Per-frame arena, night, look | a |
| `world.water` | view | Dr Na | Water surface | a |

**Kind counts (inferred):** a 21, b 37, c 4, d 1.

The one-format audit (read) counts **37 of 63 kinds with exactly one shard user**. The ratchet ceiling `products.single-shard-page-features` is 30, because it leaves out `world.*`, `view.*` and `page.life` (`/Users/raynos/projects/games/wildshard/shard-format/docs/ONE-WAY.md`).

### 1c. Server hosts: all 46

These are the cases in `/Users/raynos/projects/games/wildshard/engine/src/server/game/shardfile/nativeAssemblyHosts.ts:138-308`. Users come from `HOSTS.md` §2. The sum checks out against the audit's "41 of 46 used by exactly one shard": Dr 9, Pi 13, Na 16, Ni 3.

| Host | Users | What the case installs | Bucket |
|---|---|---|---|
| `ammunition` | Pi | Held ammunition, refilled on respawn | b |
| `boss.arena` | Na | Arena room entry (rooms only) | b |
| `boss.ground` | Pi | Ground boss from an encounter plus a decision programme | b |
| `boss.open-arena` | Na | Open arena: weather, cover, fight | b |
| `collision` | Dr Na Pi | Native baked collision | a |
| `collision.pieces` | Ni | Adds baked pieces (a "fourth collider build", SILLY) | a |
| `combat.motion` | Pi | Combat movement speed | b |
| `commands` | 2 | Binds player command input and the ledger fact port | a |
| `day.declared` | Na | Day clock from a file | a |
| `day.keyed-sky` | Pi | Day clock from `look/keyed-sky` | a |
| `day.toon` | Dr | Day clock from `look/toon` | a |
| `decisions` | 2 | v1 decision authority (`nativeDecisionAuthority`) | a |
| `encounter.patrol` | Na | Night patrol, slots, captain and wind-elite hookups | b |
| `grapple` | Ni | Grapple profile and hooks | b |
| `held.arms` | Na | Held arms, combat motion, stealth sneak-shot | b |
| `item.ranged` | Pi | Bolt, cycle or bow weapon | b |
| `item.swept` | 2 (Dr Ni) | Swept melee items | b |
| `loadout` | Pi | Native loadout, lock rules, pickup | b |
| `population.elites` | Pi | Elite feature on the day clock | b |
| `population.elites-ready` | Pi | Initialise the elites | b |
| `population.environment` | Pi | Population habitat | b |
| `population.mixed` | Dr | Island herd (mixed roster, keeper, perch program) | b |
| `population.poses` | Dr | Publish island poses each step | b |
| `population.reactions` | Dr | Item alarm/stagger reactions | b |
| `population.roster` | Pi | Herd roster | b |
| `population.settle` | Dr | Settle the island population | b |
| `population.shelter` | Pi | Herd shelter trees | b |
| `population.spawn-script` | Pi | v1/v2 spawn script | b |
| `portal.ride` | Ni | Portal ride with ledger facts | b |
| `quest.body-scripts` | Dr | v1 body ops (`sim/bodies`) | a (inferred: generic, name aside) |
| `quest.chapter` | Dr | Chapter director, captain wake | b |
| `quest.composition` | 2 (Dr Pi) | Native quest composition | b |
| `quest.kill-steps` | Dr | Kill-count quest steps | b |
| `riding.elites` | Na | Elite roster, strikes, conditions | b |
| `riding.elites-ready` | Na | Bind elites to population and taming | b |
| `riding.environment` | Na | Wild environment: grass, wind | b |
| `riding.groups` | Na | Herd/pack group rows | b |
| `riding.hunt` | Na | Population hunt | b |
| `riding.mounted` | Na | Mounted player | b |
| `riding.roster` | Na | Boot roster | b |
| `riding.taming` | Na | Taming | b |
| `riding.trample` | Na | Grass trample trail | b |
| `water.field` | Na | Water surface query from the field | a |
| `water.sea` | Dr | Sea surface with waves | a |
| `weather.native` | Na | Weather with shelters and storm reactions | a (inferred: Nalati-coupled) |
| `weather.program` | Pi | Weather continuation | a |

**Host counts (inferred):** a 12, b 34, c 0, d 0.

`HOSTS.md` marks 22 of these native hosts as SILLY: three day clocks, two water hosts, two weather hosts, "one herd in four hosts", "three boss shapes", and so on.

### 1d. `world.assembly` stages: all 18

Schema: `/Users/raynos/projects/games/wildshard/shard-format/src/format/worldAssembly.ts:28-60`.

| Stage | Side | What it does | Bucket |
|---|---|---|---|
| `ambient-flock` | view | One flock draw over perches | b |
| `arena-room` | both / `arenaRoom` | Arena fight files, weather, anchor | b |
| `drawn-models` | view | Models from fixed draws in one painterly look | a |
| `dressing` | both | Dressing, with optional bind-sets | a |
| `dressing-anchor` | both | Dressing part at an anchor | a |
| `dressing-piece` | both | Dressing part | a |
| `entry` | both | World-entry rows, publishing placements and floor | a |
| `fixed-draws` | view | Load fixed draws | a |
| `group` | both | A scene part as a group | a |
| `mesh` | both | A scene part as a mesh | a |
| `painted-reseed` | view | Reseed a painted world | a |
| `painted-world` | view | Painted world with casters and forest flag | a |
| `place` | both | An admitted scene placement and its floor | a |
| `rope-chain` | both / `ropeDecks` | Rope chain from a deck (engine `ropeChain` is a real physics feature) | a |
| `rope-deck` | both / `ropeDecks` | Rope-bridge deck site | b |
| `site` | both | Catalogue model site, optional building life | a |
| `streamed-cover` | view | Streamed canopy/cover cells | a |
| `water-surface` | view | Borrow a water surface | a |

**Stage counts (inferred):** a 15, b 3.

---

## 2. The script layer as it is

### Languages, compilation, runtime

**Language and toolchain (read).**
- Guests are written in AssemblyScript, pinned at 0.28.20 with Binaryen 132.0.0 (`SCRIPT_ABI`, `/Users/raynos/projects/games/wildshard/shard-format/src/format/scriptAbi.ts`).
- They are compiled in memory by sharddev:
  - `/Users/raynos/projects/games/wildshard/sharddev/src/sharddev/bake/compileScript.ts` handles v0 and v1.
  - `compileScriptV2.ts` and `v2Fuel.ts` handle v2.
  - `buildDecisionScripts.ts` generates the binding glue.
- Admission reads the bytes and never runs them (`shard-format/src/format/scriptAdmission.ts`, `scriptAdmissionV2.ts`, `scriptFuelV2.ts`).
- Note: SCRIPT-ABI.md still links to the old monorepo paths (`sdk/bake/...`, `engine/script/decision.ts`).

**Wasm runtime (read).** No interpreter or wasmtime is involved. Everywhere, guests run on the host's native `WebAssembly.Module` / `WebAssembly.Instance`, constructed synchronously:
- `engine/src/shared/engine/script/host.ts:192` (v0)
- `decisionModule.ts:108` (v1)
- `moduleV2.ts:99` and `viewLane.ts:129` (v2)

So guests run on V8 in Node and Chrome, and on JavaScriptCore in Safari. The server is Node ≥24.18 (`engine/package.json`), with cells in `worker_threads` (`src/server/host/dedicated/cellWorker.ts`). Every page also runs the server's code in a worker for offline play. Physics is Rapier Wasm (`src/shared/engine/physics/rapier.ts`).

**Fuel metering (read).**
- **v0/v1:** Binaryen rewrites the guest at build time (`instrumentScript`, `compileScript.ts`).
  - Every function entry and every loop header calls imported `env.fuel(cost)` with `cost = bytes.length*4 + 128*functionCount + 1024`.
  - Every function is wrapped with `enter`/`leave` for call depth.
  - Every non-store, non-compare float op is wrapped in `finite32`/`finite64`.
  - The host charges in JS (`ScriptHost.charge`, host.ts:182) and throws when the budget is exhausted.
- **v2:** a private, non-exported fuel global is decremented per basic block by instruction-count cost (`v2BlockCosts`).
  - Entry wrappers set it from the `fuel` argument and trap through `unreachable`.
  - The guest has no imports at all. Admission verifies the exact charge sequence.
- WASM-HOST's critique of v1 (read): Pine's `life` module pays 32,064 per iteration, so "about 12 iterations fit in a 400k call".

### Imports and exports per ABI (read)

| | v0 (`scriptAbi.ts`, `host.ts`) | v1 (`scriptAbiV1.ts`, `decisionModule.ts`) | v2 (SCRIPT-ABI.md §v2, `moduleV2.ts`) |
|---|---|---|---|
| Imports | `memory`; `enter()`, `leave()`, `fuel(i32)`, `abort(i32×4)`, `finite32(f32)→f32`, `finite64(f64)→f64`, `query(kind,reqPtr,respPtr)→i32` | Same guards minus `query`, plus `ws_read(op,a:f64,b:f64)→f64` and `ws_list(op,a,b,out,cap)→i32` | `env.memory` only; no function imports |
| Exports | `abi_version`, `__start`, `init(seedLo,seedHi)`, `in_ptr`, `in_cap`, `out_ptr`, `out_cap`, `out_count`, `on_tick` | `ws_abi`(=1), `ws_init(lo,hi)`, `ws_io`, `ws_handle()→count`, optional `__start` | `ws_abi`(=2), `ws_io`, `ws_init(lo,hi,fuel)→rem`, plus one work entry per lane: `ws_step(tick,fuel)`, `ws_project(fuel)` or `ws_view(dt,alpha,fuel)` |
| Exported state | Every mutable global as `__state_N` | Same | Same, except the fuel global |
| When called | Install: `__start`, `abi_version`, `init`, then pointers are read. Each due tick: `on_tick` then `out_count` | Install: `__start`, `ws_abi`, `ws_init`, `ws_io`, then the image is captured. Each call: rewind, write IO, one `ws_handle` for the event batch | Init once. Each due tick or request: rewind, write frame, one entry |

### What a script can read and change (read)

**v0 queries** (`/Users/raynos/projects/games/wildshard/engine/src/server/engine/script/queries.ts`):
- raycast(1)
- box overlap(2)
- nearest walkable(3)
- path(4)
- parameter query 410

**v0 input** (`lane.ts:101`): tick, dt, actor command, entity, token, role, then state counts and values, then events.

**v0 effects** (`/Users/raynos/projects/games/wildshard/engine/src/shared/engine/script/effects.ts`):
- `field`: write a declared numeric field within its range
- `spawn`: spawn a declared archetype at xyz
- `event`: send a declared event to an entity
- `position`: set own xyz, ±250 m

v0's `ScriptWorld` is already a small entity model: id, name, position, numeric fields, frozen/interactive.

**v1 events:** start, tick, timer, zone.enter, zone.leave, interact, hit, threshold, death, move.done, strike.done, flag, signal, strike.target (not wired), player.join, player.leave, spawned, stop, plus field/cue/channel (30–32, not wired).

**v1 scalar reads:** x, y, z, yaw, hpShare, alive, field, distance, nearestPlayer, flag, timerLeft, random, actorInZone, playersInZone, moving, strikeState, playerFlag, spawnGroupAlive, bearing.
- The code also has **bodyX, bodyY, bodyZ, bodyAlive, bodyYaw, bodyVisible and playerIntent (20–26)**. SCRIPT-ABI.md (reviewed 10-17) does not list them.

**v1 list reads:** actorsInZone, playersWithin, groundHeight, nearestWalkable, path (≤32 pts), radial.
- The code also has **declaredFloor (7)**, which is not in the doc.

**v1 commands:**
- move, strike, stop, field, spawn, despawn, flag, timer, signal, grant, reward, cue, channel, encounter.
- impulse and weather are refused at install.
- The code also has **body.spawn, body.teleport, collider.enabled, body.place, body.visible, body.retire (17–22)**. These are not in the doc; their implementation is `/Users/raynos/projects/games/wildshard/engine/src/server/game/quest/bodyOps.ts`.
- view.* (100–105) are not wired.
- "There is no `mover` command."

**Scope rules:** a script may act only on owned actors and observed targets. There are four binding kinds (encounter, quest, zone, shard) plus spawn-group and borrowed-body bindings. The player handle is `0x7fffffff`. `playersInZone` returns 0 or 1, and `nearestPlayer` returns the local player; the doc says these "do not prove multiplayer joins".

**v2 queries:** walkable(4), path(5), ray(8), overlap(9), nearest-of-roster(10), sight(11), grass(12), normal(13). They go through a request ring and are answered in the `afterBodies` phase, delivered on the next tick.

**v2 world operations** (`/Users/raynos/projects/games/wildshard/shard-format/src/format/scriptActionsV2.ts`):
- impulse 14, dismount 23, ignite 24, page effect 25.
- **Taming-specific ops 26–39:** trust, ownership, lead, mount, hurt, pose (buck/rear/kick), adopt, bond, release stallion, hide stallion, retire, breaking, notice, playerPose.
- Group-step native rows add memory, state, steer, path, confine, contact, damage, stagger, claim, scare, notify-*.

### Caps and where each constant lives (read)

| Cap | Value | Where |
|---|---|---|
| v0 fuel | 2,000,000 per call; 8,000,000 per tick | `SCRIPT_LIMITS`, `/Users/raynos/projects/games/wildshard/shard-format/src/format/scriptLimits.ts` |
| v0 other limits | instances 9, memory 24 MB (three copies reserved), effects 128/tick, spawns 8, events 32, queries 64, failures 3 | same |
| v0 memory | 64 pages per module | `SCRIPT_ABI` |
| v1 fuel | 400,000 per call; 2,000,000 per decision tick (configurable up to 2M and 8M) | `engine/src/server/engine/script/decision.ts:156-158` |
| v1 IO | 16 state slots, 32 params, 16 events/call, 32 commands/call, 1–4 pages | `SCRIPT_V1_LAYOUT`, `scriptAbiV1.ts` |
| v1 per tick | 64 binding calls/tick (`decision.ts:307`); 128 commands/tick; 4 spawns and 8 timers per call; 3rd failure disables | `decision.ts` |
| Module structure | ≤256 KiB, 512 functions, 128 globals, 1024 locals, depth 64 | `SCRIPT_ABI` |
| v2 | Same v1 quotas; 1–4 pages; fuel passed in as an argument; ≤8 projection candidates; ≤16 group members | SCRIPT-ABI §v2 |
| Shard declared budget | `serverBudget.commandsPerTick` ≤1,024 | `RUNTIME-CONTRACT.md` §6 |

### Memory persistence and tick rates (read)

**Does guest memory persist between calls?**
- **v0: yes.** The whole memory and the globals are snapshotted after each good call and saved in checkpoints (`host.ts:427`, `checkpoint()`).
- **v1: no.** It rewinds the whole image every call. Only the declared slots are durable.
- **v2 sim/project: no**, it rewinds.
- **v2 view: yes** between frames, but it is never saved.

**Tick rates:**
- Simulation runs at 60 Hz fixed.
- v1 decisions run every 6th step (about 10 Hz), and only when events are queued. Optional `tick` events at 1, 2, 5 or 10 Hz.
- v0 lane divisor comes from `sim/sim.scriptTickDivisor` (must divide 60).
- Client scripts use their own divisor (default 2, so 30 Hz).
- v2 sim runs at 10 Hz, or 30 Hz with a written reason, staggered per module.
- v2 view runs at display rate, halving under budget, never below 15 Hz.
- ReturnProgram runs synchronously in the caller's phase.

### Where scripts run (read)

- v1 DecisionHost is server code (`src/server/...`): rooms and the in-page server worker.
- v0 ScriptHost is shared code: server lanes, brains (`scriptBrain.ts`), movers (`plugin/mover.ts`), items, director, and page client scripts (`client/engine/script/client.ts`).
- ReturnProgram (v1/v2 project) runs on both sides.
- The view lane runs on the page, and also on the server for boss pose views (`slotHeights.ts`, `headlessArenaPose.ts`).

### ABI v2 lanes: purpose and how far built

**What the lanes were meant to add (read, `/Users/raynos/projects/games/project-wildshard-meta/docs/plans/parked/2026-10-20-opus-wasm-host-PLAN.md`):**
- three entry kinds: `sim` (saved fixed step), `project` (stateless call-and-return) and `view` (per-frame, client-only);
- no JS calls inside guest code;
- batched host-written observations;
- a query ring;
- one memory per module per lane.

The stated goal is W12: "a sample shard whose combo, mover and view effect are pure AS with zero shard TS". The plan header says "parked… nobody builds it", and every row reads "open".

**What the code shows was built (read):**
- Started 10-21 (G570) and widened by G604.
- Files: `compileScriptV2`, `admitScriptV2`, `ScriptModuleV2`, `SimBatchV2` and `OwnedSimBatchV2` (used only by `server/game/population/spawnScript.ts`), `queriesV2`, `inputInboxV2`, `GroupStepV2` and `GroupBankV2` (used by `stalker.ts`, `grazer.ts`, `GroupBrain.ts`), `ReturnProjectionV2` (taming, arena room), and `ViewLane`/`viewProgram`.
- Shipped guests: Nalati `pack.as` on group-step, `titanFireView.as` on the view lane (lane 3), `directorV2.as` in Driftwood and Pine.

**What is not built (inferred from the code and plan):**
- H6 (one `ws_step` per module as a general scheduler)
- H7 saves
- H13 cutover (v0 and v1 are still live)
- H14 demo shard
- H17

In practice, v2 is plugged into specific existing hosts as an extension point. It is not a general entity-scripting surface.

### Shipped AssemblyScript guests (read, `find … -name '*.as'`, src only)

| Shard | AS lines | Files | Notes |
|---|---:|---:|---|
| Nalati | 3,315 | 36 | Largest: `pack.as` 450 |
| Pine Hollow | 687 | 16 | |
| Driftwood | 245 | | |
| Brasscap | 109 | | |
| Dunes | 102 | | |
| Nine Dragon | 58 | | |
| Sky Reach | 55 | | |

Nalati's largest guests:

| File | Lines | What it does |
|---|---:|---|
| `/Users/raynos/projects/games/wildshard/shard-nalati/src/behaviour/pack.as` | 450 | The wolf pack as one resumable ABI-v2 group program: roam, shadow, encircle, regroup and break phases, with segmented native requests for senses, grass, paths and token claims |
| `tamingCoordinator.as` | 294 | Taming |
| `herdTick.as` | 259 | Herd tick plus taming mutations |
| `weather.as` | 206 | |
| `heldWeapons.as` | 196 | Three weapon projections on one stateless v1 module |
| `titanFireView.as` | 161 | v2 view lane: the Titan's grass fire, moved out of `arenaFire.ts` |
| `admission.as` | 160 | |

---

## 3. Prior analysis in the repos

**`WASM-HOST.md` and `wasm-host/STATE.md`.**
- Jake: *"once you enter the WASM, it shouldn't be going back into JavaScript"*; *"long term we want to run assembly code at 60 hertz or 30 hertz."*
- Finding: *"Only ~10 Hz event decisions exist (G503). Per-frame and 60 Hz logic … has to become a shared host or stay counted shard TypeScript."*
- W5: v2 replaces v0 and v1 in one go.
- W13: the sim lane must be "server-runnable, MMO-ready".
- Status: parked (J366).

**`HOST-AUDIT.md` (parked).**
- Jake: *"Stuff that clearly does not belong in the engine or the game needs to go into the shard files as data or WASM. Various hosts need to either be deleted or made generic."*
- First pass: *"of 45 client-plan kinds, 25 have one user; ~4,570 lines in 49 modules are reachable only through one shard's kinds."*
- It also lists 250 named host modules.
- `host-audit/custom-sections-mini-plan.md` and `-zero-mini-spike.md`: Jake on custom sections, *"absolutely horrible … We want a generic platform"*. The count went 387 → 342 and then to 0 through a registry of shared file families. The spike: *"Behaviour is not data … They go to AssemblyScript on today's Script ABI (10 Hz)."*

**`archive/HOST-RULER-PLAN.md` and `host-ruler/inventory-2026-11-13.md` (done).**
- *"Shards ship no runtime TypeScript any more … the only shard code left is in one-user engine hosts."*
- One-user host lines charged per shard: Nalati 3,856 (2,796 charged), Driftwood 661, Nine 497, Pine 404, Far Reach 38, Dunes and the Open Plots 0.
- The four G594 hosts now have 2–3 users each.
- The six-test bar is in `/Users/raynos/projects/games/wildshard/engine/docs/HOST-BAR.md`: *"Single-shot code … is never a new host. It becomes a row, a number or an AssemblyScript script."*

**`audits/2026-11-15-one-format-audit.md`.**
- *"Server hosts that serve one shard: 41 of 46"*; *"Page features that serve one shard: 37 of 63."*
- *"Those hosts are the MMO primitives Jake wants. They need to be opened up and documented, not deleted."*
- *"The limit is in the engine, not the format."*
- 6 of 7 built shards use first-party-only gates.

**`ONE-FORMAT-PLAN.md` (in progress, 42 of 134 rows).**
- J364: no trust split.
- *"a host a second shard would want becomes an engine primitive, and one shard's quirk becomes that shard's WASM; a primitive's section switches it on."*
- **"Native/declared hosts":**
  - "Native" means `server/native-assembly.json` naming hosts. Only the first-party hybrids Driftwood, Pine, Nalati and Nine Dragon have it.
  - "Declared" means `createShardfileSim` or the data cell building the sim from sections alone. This is the path Brasscap and the Template use.
  - OF17 removes `native-assembly.json`: "the server derives the host list".
- **Ratchets** (`/Users/raynos/projects/games/wildshard/shard-format/docs/ONE-WAY.md`, may only drop):
  - single-shard server hosts ≤41
  - single-shard page features ≤30
  - access-gate references ≤80
  - kind literals ≤24
  - retired vocabulary (engine 908, format 198, sdk 84)
  - and more
- M7 primitives are all still open:
  - population
  - elites
  - **boss: "2 to 7 primitives"**
  - riding
  - patrol
  - held melee and ranged
  - sky
  - weather
  - **two** water primitives
  - grapple
  - portal
- World page features and view code are out of scope. Jake: *"Leave this alone right, im so lost."*

**Which way the work is moving.**
- *(read)* The ratchets point to fewer, opened hosts, folding one-shard hosts into named primitives.
- *(inferred)* Those primitives are still feature-level (boss, riding, patrol, water.sea and water.field), not low-level.
- *(read)* Historically the counts grew: kinds went 45 → 63 and sections 63 → 72 between 10-22 and now.

**Is there an entity-component or scene-graph proposal? No.** I found no proposal in meta, shard-format or engine docs. "ECS" appears only in a Decentraland bundling bug in `shard-authoring/RESEARCH-WEB.md`. `RESEARCH-PLATFORMS.md` (Unreal, UEFN, Roblox) covers authoring and versioning, not the runtime object model.

The closest things that exist:
1. A three.js scene graph at **authoring** time, which is then lowered to sections (`/Users/raynos/projects/games/wildshard/sharddev/src/sharddev/scene/shard.ts`, `author.ts`: `world.part`, `solid()`, `animate()`, `Water`).
2. The five creature layers (body, temperament, senses, abilities, type tag) in ONE-FORMAT/`CREATURES.md`.
3. v0's `ScriptWorld` entity model.
4. The CC59 and CC60 rows (script hooks on brains, whole-creature WASM from any upload).

**Evidence that today's design is already more general than you may assume (read):**
- Brasscap and the Template are full games (camps, a boss, quests, levers, a lift) built only from rows, GLBs and AS on the data cell, with no native hosts. Open Plots use 2 kinds.
- `world/movers` is a generic kinematic primitive:
  - kinds: platform, chain, static, channel;
  - drivers: track, winch, pendulum, waves;
  - triggers: always, interact, stand, shared-field;
  - `carry` for seated rides such as the canoe.
- Zipline, ladder and updraft are rows under `state/modes` (`/Users/raynos/projects/games/wildshard/shard-format/src/format/modes.ts`), not hosts.
- `sim/bodies` plus body ops, `props.bodies` (dynamic Rapier), `targets`, `hooks` and `state` fields form a generic interaction layer.
- *(inferred)* The caveat: each traversal mode or carry is still a named schema variant with its own engine code. For example, `cableTraversal.ts` is 356 lines.

---

## 4. How a new mechanic is added today (read from git)

**A. Mossgate lift to a ledge cache (Template, 2026-11-16).** It reuses the mover primitive.

| Repo | Commit | Files | Lines | What changed |
|---|---|---:|---|---|
| shard-format | — | 0 | 0 | Nothing |
| sharddev | `985d1cf` | 13 | +198/−4 | New `generators/lift.ts` (70) plus 7 data JSONs, `product.ts`, `world.ts`, a test |
| sharddev | `e095536` | 4 | +6/−6 + binaries | Hero recapture |
| sharddev | `feaeafd` | 9 | +14/−12 | Fix, incl. `door.as` |
| engine | `b8e302ab0` | 7 | +108/−3 | New `grid/dataCellMovers.ts`, test 53 |
| engine | `7b02fd510` | 8 | +133/−24 | New `shardfile/dataPageMovers.ts`, side-parity |
| engine | `fafee64e8` | 9 | +62/−40 | Pins/staging |
| engine | `f2d3fad3a` | 1 | +2/−1 | Test fix |

- Totals: sharddev 26 file-touches, +218/−22. Engine 25 file-touches, +305/−68, of which about 108 lines are runtime code.
- Release path: staging upload Template rev 8 (0.3.3), with engine pins edited by hand.
- *(inferred)* No schema or host was added. But movers only ran where the `world.movers` kind installed them, so two more runtime paths needed new code.

**B. Brasscap ledge marksmen and brawler (2026-11-16).** It is rows over existing brains and strikes.

| Repo | Commit | Files | Lines | What changed |
|---|---|---:|---|---|
| shard-format | — | 0 | 0 | Nothing |
| sharddev | — | 0 | 0 | Nothing |
| shard-brasscap | `94c748a` | 8 | +177/−7 | `creatures.json` +49, `species.json` +36, `strikes.json` +38, loot, materials, client-scripts, `world.ts` |
| engine | `52551f4a7` | 2 | +28 | Test; marksmen excluded because they fell off the ledge |
| engine | `cda0634f4` | 2 | +12/−3 | Creature floor on declared solids |
| engine | `8e8e9662c` | 5 | +31/−21 | Review fix |
| engine | `72bcd28ae` | 7 | +64/−17 | Pins and test |

- Engine total: 16 file-touches, +135/−41, of which about 37 lines are runtime code.

**For contrast:**
- **A new one-user host, portal.ride and collision.pieces (2026-11-05).**
  - shard-format `8b97743`: 4 files, +37/−16.
  - Monorepo `3138fbd1c4`: 9 files, +41/−27 (switch cases plus version bumps in 5 `package.json` files and the lockfile).
  - Monorepo `206719f1ff`: 6 files, +135/−42.
  - The host code predates all of this.
  - Today `portal.ride` touches 7 shard-format files (schema 22, `nativeAssembly`, `feature-sides`, `clientPlan`, `runtime-hosts.json`, contract doc, ratchet). It touches about 12 engine files: `portalRide.ts` 170, `walkInPortalRide.ts` 160, `portalRideBinding.ts` 62, the switch, `CLIENT_FEATURES`, `installedSides`, `installers`, the register, `engine-sides.json`, 2 tests, and proofs.
- **Format-only additive features** whose engine half is still pending:
  - touchable `props.bodies` (`777c20c`, 5 files, +153/−3);
  - item-use `setsFlag` (`85ab742`, 5 files, +89/−5).
  - Each one shipped as a format minor release. shard-format released v0.6 through v0.12, seven releases, on 2026-11-16.
- The zipline, canoe and winch history predates the repo split. It lives in `/Users/raynos/projects/games/wildshard-singleplayer` (for example `36a08072ea` "canoe mover" and `1ed6b8f6f0` "the zipline as a bank"). I did not trace it.

**Summary of the cost of one more mechanic.**
- *(read)* When a mechanic fits existing rows, it costs zero format changes and 0–2 small engine fixes per runtime path, plus pin and test churn.
- *(inferred)* When it needs a new host, it costs about 7 format touch points and about 10 or more engine touch points, plus a release, a pin bump in each consumer and a register row.
