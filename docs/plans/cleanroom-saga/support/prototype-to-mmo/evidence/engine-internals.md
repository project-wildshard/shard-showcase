# Engine internals: world model, physics, replication, hosts, AI, rendering

> Moved from meta `docs/prototype-to-mmo/evidence/engine-internals.md` at `386423cbea` into the cleanroom saga (D38, 2026-11-26).

> Written by: Claude

> **State:** point-in-time record, 2026-11-16. A read-only study by a research subagent for [STRATEGY.md](../STRATEGY.md), saved as reported. Nothing was built, run or changed. Each study marks what it read in code or docs against what it inferred.

I read the engine and the wire package without changing, building or running anything. Short answer: there is no general entity model. The server is one class, `SimHost`, that holds two hard-coded tables (creatures and players) plus a registry of named per-tick callbacks. Everything else in a zone belongs to the host that installed it. Line counts below are `wc -l` of the file. Runtime TypeScript under `src/` (tests excluded) comes to about 282k lines: client/engine 92.6k, client/game 92.8k, shared/engine 32.1k, server/game 21.0k, shared/game 20.9k, server/engine 9.2k, plus the host folders.

## 1. The world model

**Server.** `src/server/engine/sim.ts` (714) defines `class SimHost`. Its state is:
- `entities: Map<string, AnimalSim>`: creatures only.
- `players: Map<string, PlayerSim>`.
- `strikes`, `adapters: Map<string, SimStateAdapter>` (save and restore), `flags`, `quests`, `physics`, `combat`, `events`, `floors: MotionPlatform[]` and `water`.
- `onStep(id, run, adapter?, phase)` (line 546). Every other system registers itself here as a named callback with an optional snapshot adapter.

A tick (`step`, line 604) runs player input, then physics, then player moves, then the step callbacks, strike runners and every `AnimalSim.step`, then the after-body callbacks.

Nothing else is a first-class object. Movers, projectiles, pickups, portals, triggers, NPCs and bosses each live in their installer's private storage. One example is `KinematicMover` bodies in a `Map` inside `src/server/game/plugin/mover.ts` (605). The only common thread is `SimStateAdapter` (`snapshot`/`restore`) and lifetime through `Scope` (`src/shared/engine/app/scope.ts`, 557).

**Creatures.** `AnimalSim` (`src/shared/engine/entities/AnimalSim.ts`, 400) is the one actor type. It covers animals, enemies, bosses and horses. Its spec (`AnimalSimSpec`) is `kind`, `variant`, `rarity`, `hp`, `aggressive`, `dims`, `mods` and `flight`, with free-form numbers in `mem: Record<string, number>`.

**Script entities (the closest thing to a general entity).** `ScriptWorld` in `src/shared/engine/script/effects.ts` (111) holds `ScriptEntity { id, name, position, fields: Record<number, number>, frozen }`. It has declared field ranges, archetypes, an event list and `maxEntities`, and changes go through a transaction. Today it is used for movers and script bodies; scripts pass empty `archetypes: []` in several places.

**Client.**
- `src/client/engine/world/registry.ts` (348) defines `Piece`: an `object`, `colliders: ColliderDesc[]`, `surface`, `floor()`, `follows?: Object3D` (a moving collider), `active()` and `mode`. One `add(piece)` call makes a thing drawn, solid and visible in the explorer. This is a generic registry for static and moving scenery.
- `LevelContext` (`src/server/engine/level/context.ts`, lines 54–87) gives `system`, `on`/`answer`, `rows`, `piece`, `hud` and `inputContext`.
- Creatures are drawn through `RowBodies`, `AnimalView` and `AnimalFactory`.

**Parenting and attachment.** On the server there is none in general. Attachment exists only as bespoke mechanisms:
- a kinematic deck carries a `CharacterMotor` (`src/shared/engine/physics/mover.ts`, 60);
- `SimHost.floors`;
- `liftRider.ts` (62);
- riding, where `SimRide` or `SimPlayerDriver` takes over the player's motion;
- grapple.

On the client, attachment means the three.js scene graph, rig sockets (`hand.R`, `hand.L`) and `Piece.follows`.

## 2. Physics and queries

**Rapier usage.** `Physics.ts` (211) owns one world, with snapshot and per-scope ownership of handles. Across the code I counted these calls:
- Collider shapes: `cuboid` ×17, `capsule` ×8, `heightfield` ×6, `ball` ×6, `trimesh` ×4, `cylinder` ×1, `convexHull` ×1.
- Body kinds: `dynamic` ×4, `kinematicPositionBased` ×3, `fixed` ×2.

Collision groups are a fixed list of nine in `groups.ts` (64): `WORLD`, `PLAYER`, `CREATURE`, `HITBOX`, `PROJECTILE`, `ITEM`, `DEBRIS`, `BORDER`, `SENSOR`. Dynamic bodies (items, drops) are in `bodies.ts` (600).

**Character controller.** `CharacterMotor.ts` (451) wraps Rapier's `KinematicCharacterController` in a capsule, upright or lying (the horse). Players and creatures both use it.

**Reusable queries** in `src/shared/engine/physics/query.ts` (189) are `worldHit`, `floorBelow`, `castRay`, `castSegment`, `lineOfSight`, `sweepBall` and `canStandAt`. `overlap.ts` has `overlapBox`, and `navmesh.ts` (206, using the navcat library) has `closestWalkable` and `findPath`. Any trusted TypeScript may import them. Shard WebAssembly reaches them only through opcode adapters:
- `src/server/engine/script/queries.ts` (37): raycast, overlap, nearest and path, clamped to ±250 m and capped result counts;
- `queryBatchV2.ts` (118) for the v2 script interface.

**Player motor.** `src/shared/engine/player/motion.ts` (391) is the one composed step, shared by server and client, built from walk, fall, jump, shove, impulse, dash, swim and board. `modes.ts` (239) declares two kinds of mode:
- `MotorMode = 'foot' | 'board' | 'swim' | 'wade'` is hard-coded into `motion.ts`.
- `DrivenMode = 'ride' | 'grapple' | 'glide' | 'climb' | 'drive'`. Glide, climb and drive are "approved, not yet built".

The modes that exist are separate hand-written laws:
- ladder: `src/shared/game/shardfile/ladder.ts` (137);
- zipline: `cableTraversal.ts` (356);
- grapple: `src/shared/game/grapple/sim.ts` (352) plus the server host (181) and the client tool (481);
- ride: `src/shared/game/riding/physics.ts` (691).

To add a mode you extend the `DrivenMode` union. You then write a `PlayerModeDriver` (`drive`/`step`/`pose`) or a `traverse` callback for the client, and a `SimPlayerDriver` or `player.traversal` answer for the server. If the mode is to be predicted, it also needs a `PredictedRide` and a wire ride law.

## 3. Replication

**The wire is a generic grammar.** `grammar.ts` (220) defines typed nodes (uint, quant, angle, enum, ref, text, struct, union…). `WireClass` carries fields with `send: all|owner|others|initial`, `predicted` and `relevance`. A frame (`snapshot.ts`, 164) is the owner block, then the ride words, then a delta per handle with a change mask. Engine code binds accessors to these classes with `bindClass` (`src/shared/engine/net/schema.ts`, 157). The 16-bit slot+generation handles (`handles.ts`, 74) and distance-based send rates (`tiers.ts`) are generic.

**But the classes are feature-specific.** There are six, in `classes.ts` (177) and `player.ts` (81):

| Class | Fields | What it is |
|---|---|---|
| `player` | 57 | ~38 predicted motor fields such as `dashT`, `hoverBob`, `climbTo`, `diving` |
| `animal` | 24 | AI state enum, `attackT`, `flinch`, `rideable`… |
| `encounter` | 15 | boss/elite bar |
| `script` | 7 | a body's pose |
| `state` | 1 | one named number |
| `flag` | 0 | exists while a flag is set |

**Message kinds** (`records.ts`, 272; `events.ts`, 219):
- Messages: `hello`, `cmds`, `act`, `welcome`, `frame`, `events`.
- Acts: `interact`, `reload`, `equip`, `chat`, `report`, `ride`, `climate`, `buy`, `board`, `wear`, `pose`.
- Events: `spawn`, `despawn`, `hit`, `died`, `quest`, `phase`, `reward`, `travel`, `ledger`, `chat`, `mount`, `dismount`, `owned`, `view`, `player-died`.
- The command record has feature fields: `attack`, `heavyTarget`, `lockTarget`, `hookTarget`, `launcher`.
- Ride laws: one, `mount`, with 38 f32 words (`rides.ts`, 69).

The generic parts are `spawn`/`despawn`, `state`, `flag`, `script`, `view` (a name plus numeric args) and `owned`. Everything else is per feature.

**The server side enumerates by hand.** `SimNetWorld.visit` (`src/server/engine/net/simWorld.ts`, 130) lists players, then `host.entities`, then encounter rows, then script bodies, `state` rows and flags. Features piggyback on string-named `state` rows. Grapple, for example, publishes `grapple.<id>.phase/clock/hook…` through `publishWorldState` (`src/shared/engine/sim/shardRows.ts`, 106).

**Prediction, interpolation, lag compensation.**
- Prediction (`src/client/engine/net/predictor.ts`, 269) covers only your own character: "The world is never rolled back, only this character." Rides plug in through `PredictedRide`.
- Interpolation (`interpolator.ts`, 179) is generic over any class's columns (`blendOf(cls)`).
- Lag compensation (`src/server/engine/net/hitHistory.ts`, 114) rewinds `AnimalSim` bodies only, up to 12 ticks.
- I found no projectile class on the wire; shots travel as command fields plus `hit` events.

**What a new kind of replicated thing costs today.** The cheap route is to encode it as `state` rows or `view` events with string names, which needs no wire change. A real class needs four steps:
1. a `WireClass` in shard-format `packages/wire` (a wire minor release);
2. a `bindClass` binding in the engine's `netSchemas`;
3. a new branch in `SimNetWorld.visit`;
4. a bespoke client consumer.

## 4. Hosts and kinds

**A server host** is one `case` in the `switch (row.host)` inside `prepareAssemblyFeature` (`src/server/game/shardfile/nativeAssemblyHosts.ts`, 310, lines 136–309). There is no registry object or interface. A host:
- receives its plan row (typed by the `NativeAssemblyFeature` union in shard-format `src/format/nativeAssembly.ts`, 141) and `AssemblyPrepared` (the product, bake, navmesh and ports);
- reads its data asynchronously, then returns a synchronous `Step` that takes an `AssemblyRun`. That is a shared bag of `host: SimHost` plus fields that earlier hosts leave for later ones (`day`, `wild`, `roster`, `bindings`…);
- may do anything to the `SimHost`: `onStep`, `events.on/answer`, `useWater`, `useDayClock`, `spawn`, collider toggles, `publishWorldState`;
- records itself with `registerInstalled(host, key)` (`installedSides.ts`, 18), where the key is from a 22-name union.

Three examples:
- **`water.sea`** (2 lines): reads the sea row and calls `host.useWater({ surfaceAt, bob })`. Almost entirely generic machinery.
- **`grapple`** (`src/server/game/grapple/native.ts`, 181, plus `grapple/sim.ts`, 352): one claw per player and a headless camera projection. It parses its own command tape, overwrites the player's position and velocity before the walk, toggles guard colliders, publishes seven `state` rows per player, and has its own valibot save schema. The only generic machinery used is `onStep` and its adapter, `publishWorldState` and `host.leading`; the rest is mechanic logic.
- **`riding.mounted`** (`src/server/game/riding/native.ts`, 362, plus `riding/physics.ts`, 691, `nativePopulation.ts`, 384 and `nativeTaming.ts`, 346): seats, a horse motor-state schema, mount and claim rules, pond and wet masks, and a 38-word ride law that the wire must also know. Nearly all of it is feature-specific.

**A client kind** is an entry in `CLIENT_FEATURES` (`src/client/game/shardfile/clientPlan.ts`, 529):

```ts
interface ClientFeature { phase; rank; lifetime: 'resident'|'entered'; sections; install(ctx: ShardContext, row, resident: Scope); play?; world?; preparePlay? }
```

The comment says "Adding a kind requires its strict format schema and a reviewed platform host." `install` gets the whole trusted `ShardContext`. The 63 kinds map largely one to one onto features (`boss.telegraph`, `held.ranged-page`, `world.forest-page`, `weather.forest`…).

## 5. AI and combat

**AI.**
- `CreatureBrain` (`src/server/engine/ai/CreatureBrain.ts`, 23) is a thin wrapper over `Hfsm` (`hfsm.ts`, 51).
- The real behaviours are large hand-written classes: `stalker.ts` (1,502), `grazer.ts` (1,360), `huntPattern.ts` (1,012), `diver.ts` (540), `BossBrain.ts` (295), `flock.ts` (334). There are also small archetype wrappers: `pack`, `ramGrazer`, `orbitDiver`, `perchHunter`…
- `PlatformBrain` (`platform.ts`, 140) is a generic, data-tuned pursue/leash/wander archetype with explicit perception and path ports.
- WebAssembly brains run through the decision host (`src/server/engine/script/decision.ts`, 573). Its vocabulary (shard-format `scriptAbiV1.ts`) is about 26 reads, 7 lists, 20 events and 28 commands, such as `move`, `strike`, `spawn`, `body.spawn`, `collider.enabled`, `impulse`, `view.clip`. The "return programs" (`returnProgram.ts`, 448) are also WebAssembly.

**Perception** is per brain: sight cone, range and hearing radii by player speed in `huntPattern.ts` and `grazer.ts`, and a ray line-of-sight in `PlatformBrain`. There is no shared perception service. **Navigation** is a per-shard baked navmesh queried for paths; the character motor resolves the actual movement. I found no steering library.

**Combat** has real general primitives:
- `CombatPipeline` (`pipeline.ts`, 157): an `Actor` with `tags`, `state` and `attributes`, a `DamageRequest`, and ordered `DamageRuleDef` tag rules (`cap`/`add`/`mul`/`negate`/`override`).
- `EffectService` (216, types 47): a `EffectDef` with `instant|timed|permanent`, attribute `modifiers`, stacking, `grants` and `blockedBy` tags. This is close to the gameplay-ability systems in other engines.
- Hit zones are head plus body capsule only (`AnimalVolumePort`, `isHeadshot`).
- Strikes (`strikes.ts`, 199) and items (`ItemSpec`, `ItemAttack` in `items.ts`, 147) are data. Weapon families are compiled-in constructors (`itemFamilies.ts`; `client/game/plugin/weaponFamily.ts`, 785).

Balance: numbers are data-driven, but behaviour code is hand-written per archetype.

## 6. Rendering

Zone visuals come from bespoke systems, not a generic scene loaded from glTF:
- `worldScenes.ts` (767) with tile streaming (`tileDriver.ts`, 489), placement pages, welds, batches;
- terrain (`Terrain.ts`, splat), grass, trees (`TreeFactory`), water (`world/water`), sky (`skyRig`, `BakedSky`), weather, post looks;
- glTF is used for assets (17 files import `GLTFLoader`).

**What shards control.** Material families (`render/families/registry.ts`: pbr, toon, painterly, emissive, ground…), plus a validated material graph (`GraphIr`, 121 ops, with a cost budget) compiled to GLSL by `render/graph/glsl.ts` (1,056) and `glslProgram.ts` (698). A post-processing graph (`glslPost.ts`) is driven from `look/post`. Shards cannot supply raw shader code.

**Animation.** `src/client/engine/anim` is about 420 lines: `RigContract` (clip names `idle|walk|run|attack|hit|die|turn|swim|fly`, plus sockets) and `AnimMachine` over three.js `AnimationMixer` with crossfades. I found no clip events. Creature poses are largely procedural (`animalPose.ts`, 401; `shared/game/plugin/animation.ts`, 618).

**Effects.** `ParticlePool.ts` (76), `Impacts`, `LightPool`, `groundFx`. These are small pools, not a general effects system.

**Level of detail and streaming.** `THREE.LOD` in `models/place.ts`, far impostors (`grid/farImpostor*`), distance-banded creature tick and physics rates (`sim/bands.ts`), tile and page residency. Occlusion: I found no occlusion-culling system, only `hiddenFaces.ts` and frustum and shadow culling.

## 7. Third person

There is no third-person camera and no visible local body. The game is first person: `Player.ts` (689) places the camera at the feet plus eye height, and draws arms through `firstPersonArms.ts`. The local player's only body is an invisible shadow body (`client/game/cosmetics/bodyShadow.ts`) that casts worn cosmetics as a shadow.

Remote players appear as one shared procedural "castaway" skinned mesh (about 1,100 triangles, `models/castawayBody.ts`). It is posed in code from the replicated row (`otherPlayers.ts`, 286; `remoteGait`, `remoteStrike`, `remoteAir`, `remoteBoard`, `remoteDeath`), with held items on hand sockets and a name tag. `FreeCam` exists, but only for the explorer view.

## 8. The trusted plugin path

`ShardPlugin` (`src/client/game/plugin/context.ts`, 199) is an abstract class with staged `world`/`kit`/`play` hooks receiving `ShardContext`. That context is `LevelContext` plus the manifest, game services, row registration verbs, the shard's 500 m cell bounds and the built shard product. Its only subclasses now are internal:
- `declaredClientPlanEntry` (`shard/declaredEntry.ts`);
- `HybridShardPlugin` and `ClientPlanRuntime` (`shardfile/hybrid.ts`, 539);
- `GridPageShellPlugin` (`grid/pageShell.ts`);
- an inline class in `sourceManifest`.

No sibling shard repo subclasses it; only a sharddev test mentions it. `manifest.ts:474` still has `load?` and `resolveTrustedRuntime?` hooks. The singleplayer-era shard code is gone from `src`: there is no `src/shards/`, and it has no history in this repo's git log. There are still 251 comment references to `src/shards/...` paths. The plugin folder's helpers (`geometry.ts` 2,083 lines, `ui.ts` 1,514) remain widely imported.

## Closest to a general, primitive-based design
1. The wire grammar and the class, row and delta machinery (`grammar.ts`, `schema.ts`, `handles.ts`, `interpolator.ts`).
2. `CombatPipeline`, `EffectService` and tag-matched rules (attributes, modifiers, stacking, tags).
3. `SimHost.onStep` with `SimStateAdapter` plus `Scope`: a uniform system and save registration.
4. The shard script interface: `ScriptWorld` entities with declared fields and archetypes, a transactional effect model, and physics or navigation queries as opcodes.
5. Physics wrappers: `CharacterMotor`, `query.ts`, collision groups, `KinematicMover`, and the client `Piece` registry.

## Most feature-specific
1. Server world storage: only `AnimalSim` and `PlayerSim` are first-class. Everything else is private to its host, and there is no general parenting.
2. The 46 server hosts: a hand-written `switch` with ordering coupling through `AssemblyRun`. The 63 client kinds are mostly one per feature.
3. The wire classes, the `player` predicted fields and the acts and events: grapple, mount, climate, buy and board each have their own fields.
4. Movement modes: each traversal is a separate hand-written law with its own save schema, wire state and client view.
5. Rendering and AI behaviours: bespoke terrain, water, sky, forest and weather systems, and 300 to 1,500-line brain classes per archetype.

**What I verified and what I inferred.** Everything quoted above with a type name or line was read in the code. Four things are inferences from partial reads:
- that projectiles are never replicated as entities (no class or record exists, but I did not trace every shot path);
- that no occlusion system exists (the search found none);
- that animation has no clip events;
- the per-host split between generic and mechanic logic, beyond the three hosts I read.
