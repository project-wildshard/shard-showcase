# Prior design thinking, the scene side and the showcase plans

> Moved from meta `docs/prototype-to-mmo/evidence/prior-design-and-scene-side.md` at `386423cbea` into the cleanroom saga (D38, 2026-11-26).

> Written by: Claude

> **State:** point-in-time record, 2026-11-16. A read-only study by a research subagent for [STRATEGY.md](../STRATEGY.md), saved as reported. Nothing was built, run or changed. Each study marks what it read in code or docs against what it inferred.

I read the docs in all four repos and checked the claims against the code. I ran only read-only commands and ran nothing in the repos. Throughout, **[doc]** means a document says it and **[code]** means I checked it in source. Paths are relative to `~/projects/games/`.

## 1. Code versus data: what was considered and what was decided

**Where the design started** [doc] `wildshard-singleplayer/docs/design/mmo/SHARD-PLATFORM-PLAN.md` (2026-09-30).
- §4 states the problem: uploaded TS/JS "can read cookies and storage, call `fetch`… Lint rules don't stop a malicious uploader — only a runtime boundary does."
- It surveyed Roblox (Luau), Minecraft, UEFN (Verse) and Second Life, and concluded: "every one that lasted converged on **uploaders mostly don't ship code**."
- On WASM it said "About half of it" is solved. It does not sandbox shaders, budgets or content.
- It listed three possible source languages: AssemblyScript, Rust, and "QuickJS compiled to WASM — keeps TypeScript… but runs roughly 20–50× slower".
- §5 is titled "build with code, ship data, earn scripting". Generators run on the author's machine. Gameplay is "schema-validated JSON, wired to engine devices and the logic graph". Visuals are "look stacks + material graphs". Sandboxed scripting is a later tier, earned by trusted authors.
- §6.1 takes "Fortnite Creative devices and LittleBigPlanet logic" as the model. It also proposes archetype brains and boss "phase tables".
- §10.1 defines the **80/20 split**: about 80 % data and assets, at most 20 % trusted runtime TypeScript kept in `runtime/`.

**The "catalogue"** [doc] `MMO-REQUIREMENTS.md`.
- Decision 3 says: "80 % data and approved systems (a logic system, look stacks, material graphs, WASM plugins), 20 % custom runtime per shard."
- Decision 9 moved "the catalogue (logic system, devices, brains, phase tables, look stacks, material graphs, WASM plugins)" out of the requirements and into the plan, because requirements should state needs, not mechanisms.
- Decision 5 made WASM plugins an approved system. That amends the earlier one-shot brief's ban on "JavaScript, TypeScript, WASM… or unrestricted shader programs" (`VISION.md:37,122`).
- R1 says "**Authors invent mechanics**", not only configure the platform's.
- O4 picks "**AssemblyScript first** (plain linear-memory Wasm, not WasmGC)… QuickJS at most as a slow 'any JS' fallback."

**The clean-room audits (E435) warned against the catalogue as the main mechanism** [doc] `docs/design/mmo/research/e435/plan-audit-claude.md`.
- §2.3: "Behaviour should be a sandboxed language whose host API *is* the logic system… keeps 'approved systems' small (the verbs, not a component per mechanic)."
- Also §2.3: "A graph catalogue on its own forces the engine team to pre-build every mechanic. That's Roblox's pre-Luau problem."
- Its review table (a row above) warned about "a wide component zoo", saying "each one-user graduation is a permanent compatibility promise".
- It noted Claude "writes… large hand-wired JSON node graphs badly", while the Fortnite/LittleBigPlanet model is "designed for a *visual* editor".
- It called line counts "gameable by folder name".
- `plan-audit-codex.md` agreed: "one small capability API, reusable devices, and an experimentally chosen general-purpose behaviour runtime… SP30's 'every gap becomes an approved system' makes the central team a bottleneck."

**Languages that were evaluated** [doc] `research/e435/behaviour-language-claude.md` (with its own lab measurements).
- The pick was AssemblyScript. Rust was the runner-up.
- **Rejected for sandboxed shard scripts:**
  - WasmGC languages: "no per-module memory cap and no memory snapshot".
  - JS engines compiled to Wasm: "StarlingMonkey/ComponentizeJS is about 8–10 MB. Javy/QuickJS is 20×+ slower".
  - Porffor (alpha) and Static TypeScript (no Wasm back end).
  - Luau-in-Wasm: "The best interpreter alternative to QuickJS, but still an interpreter." Its size and speed were marked unverified.
- **The evidence behind the choice:**
  - AS ran at the same speed as V8's JIT and about 20–40× faster than QuickJS. Modules were 5–9 KB and instantiated in 0.2–0.6 ms.
  - Injected fuel cost +11–15 % on allocation-heavy code and +37–79 % on tight loops. A `while(true)` loop was stopped in 7–22 ms.
  - The memory cap "trapped at exactly 4 MiB".
  - The decisive finding was determinism. Host `Math` differs between V8 and JavaScriptCore, and Pine's shipping `combatMath.ts` gave tens of thousands of mismatched results. AS carries its own maths library, so it computes identical bits on both.
- G309 [doc]: "Keep AssemblyScript… behaviour is mostly data rows on shared systems (G295), so AssemblyScript stays small."
- G146: "a DSL is welcome if it compiles to data or WASM".

**Entity-component models and scene graphs.**
- I found no proposal for an entity-component model. The only mention is Overwatch's "deterministic ECS sim", cited as a netcode reference (`authority-claude.md:434`). The nearest idea is G9, "Entity scripts + a shard director" (`project/archive/2026-11-04-shard-platform/decisions-archive.md`).
- A scene graph was compared directly in `docs/audits/shardfile-vs-roblox.md`:
  - "no tree ships… The product is flat sections of rows… about 300 schema modules in `src/format/`, one per mechanic… Ahead: Roblox for discoverability."
  - It recommends against borrowing "A runtime tree any script can change. `Instance.new` anywhere… defeats budget-first admission."
  - It also recommends against "Per-frame general scripting… Our scripts are event-driven, 10 Hz and fuel-metered."

**How it actually ended** [doc].
- G604 replaced 80/20 with "zero custom lines", and that target was reached (G693).
- The way zero was reached was by moving shard code into engine and game "hosts". `docs/plans/parked/2026-10-22-opus-host-audit-PLAN.md` quotes Jake after the G594 audit "found Pine/Driftwood code hidden in one-user TypeScript hosts", and counts "**250 modules are named as hosts**". G595 now requires Jake to approve every one-user host individually.
- The logic-graph and devices idea was never built as designed. Instead the work produced "a section and a host per mechanic", the shape the audits had warned about.

## 2. What happened to the catalogue ideas

These are verified in code under `wildshard/shard-format/src/format/` (391 modules). `docs/RUNTIME-CONTRACT.md` lists **72 sections, 81 `client/plan` kinds and 46 server hosts**, each mapped to a compiled-in host. It also says "There are no custom sections."

| Idea | Today | Usage in shard repos (rough file-level grep) |
|---|---|---|
| Logic system | `quests/directors` (`directorStages.ts`, v2): up to 64 stages. A `when` is a boolean expression (`! && \|\|`) over up to 16 inputs bound to `flag:`, `zone:`, `event:`, `actor:*.dead\|present` or `day:a..b`. Actions are a closed list: spawn, despawn, flag, score, weather, toast, reward, emit. Also `hooks` (field equals value; scene events), `quests.triggers` and `targets` | Directors are declared in dunes, sky-reach and nine-dragon (one file each) |
| Devices | `world/movers`, `world/props`, `world/traversal`, player `modes` (Grapple, Mount, Updraft, Zipline, Ladder in `sharddev/src/sharddev/modes.ts`). The word "device" does not appear | Movers rows in brasscap and sky-reach |
| Brains | `brains.ts`, `speciesBrain.ts`, `groupBrains.ts`, and an `actors/creatures` section installed by `installDeclaredBrains` | Driftwood, Dunes, Sky, Nalati, Pine |
| Phase tables | `bossEncounter.ts` (354 lines), `bossProfiles.ts`, `combat/encounters` with HP-threshold phases | Pine, Nalati, Driftwood, Dunes, Sky, Brasscap |
| Look stacks | `postStack.ts` (ordered post graphs under an instruction budget), `postGraphLook.ts`, plus `toonLook`, `paintedLook` and `keyedSky` sections | Post graphs only in Nalati and Nine |
| Material graphs | `materialGraph.ts` (1,220 lines, about 121 ops; budget 160 nodes, 4 samplers, 480 instructions; maximum 4,096 / 16 / 8,192) | Graph materials referenced in most shards; heaviest in sky-reach and nine |
| WASM plugins | AS → Wasm in `sim/scripts`, `actors/return-scripts`, `actors/spawn-scripts`, `view/modules`; ABI v0, v1 and v2 all exist | About 80 `.as` files: Nalati 36, Pine 32, Driftwood 6, Brasscap 3, Dunes 2, Nine 1, Sky 1 |

**How expressive is the data logic.** It is a bounded state machine over booleans. There are no variables, no arithmetic and no timers as inputs. Anything beyond that goes to AssemblyScript or to a new host.

## 3. The scene side today

**The `defineShard` API** [code] `sharddev/src/sharddev/scene/{shard,author,lower,shardfile}.ts`; GUIDE.md §2b.
- The build function runs **only at compile time**.
- The `world` object offers: `scene`, `part(name, build, {panel})`, `ground(heightAt, {colourAt, material, detail})`, `sky(tslColour, {environment})`, `post({tone, exposure, bloom, vignette})`, `spawn`, `trigger(id, obj, {radius, flag})`, `interact(id, obj, {label, radius, scene, unless})` and `detail(id, instancedMesh, {cell, radius, sway})`.
- Helpers in `scene/author.ts`: `solid`, `paint`, `Water`, and `animate` with `flicker`, `pulse`, `drift`, `rise`, `sway` and `uvScroll`.
- `scene/creature.ts` adds `creatureGlb`.
- A third argument, `extend`, merges in hand-written sections (quests, items and so on).

**What it accepts** [code]:
- `MeshStandardMaterial`, `MeshBasicMaterial`, `SpriteMaterial` and `PointsMaterial`.
- Node materials, but only with `color`, `emissive`, `roughness`, `metalness` and `opacity` slots. Other TSL goes through `GraphMaterial(graph())`.
- Transparency, alpha test, additive blending and `polygonOffset` are kept.
- `InstancedMesh` stays instanced, written with `EXT_mesh_gpu_instancing`.
- Lights: point lights (the 16 brightest only), the brightest directional light, hemisphere and ambient lights.
- `scene.fog` and a colour background.

**Every refusal and its stated reason** [code] `lower.ts`:
- `ShaderMaterial`: "a … is raw GLSL"; write it in TSL instead.
- `onBeforeCompile`: "patches GLSL".
- Node slots other than the five above (`positionNode`, `normalNode`, `outputNode` and so on): "has no graph stage".
- Unknown material types: "has no lowering yet".
- `SpotLight`: "has no lowering yet… spot lamps are an engine row after M1".
- Multi-material meshes: "Split it into one mesh per material".
- `Line`: "Draw a line as a thin mesh (a TubeGeometry)".
- Geometry that is not triangles.
- Textures with no pixels at compile time: "a CanvasTexture needs a browser"; use `paint()` or a `DataTexture`.
- `Points` with `sizeAttenuation` off.
- A graph material on a sprite or points, or with declared motion. Motion has to go in the graph's `vertex.offset` instead.
- A motion type that doesn't fit the object: "spin and bob need moving parts: an engine row after M2".
- Panel parts that hold sprites, points, lights or water, or that move.
- A ground material that is emissive, transparent, not front-sided, or has a map ("the terrain has no uvs").
- Anything placed outside the 500 m cell.

**Not refused, but not supported.** I found no `SkinnedMesh` or animation check in `lower.ts`, so a skinned mesh inside `world.part` appears to be read as a static mesh. Rigs and clips go through `creatureGlb` only: bones are named groups and meshes are bound rigidly to one bone. The older `synth` path (`sceneAnimation.ts`) does read skins and clips.

**Output** [code] `scene/shardfile.ts`:
- 62.5 m tiles, each a GLB merged per material, plus simplified L1 tiles.
- `look.materials` entries bound to GLB materials by name.
- Painted textures as KTX2.
- `look.light.lamps`, the sun and ambient keys, fog and post settings.
- The terrain bake with an entry-road check, collider boxes, `water[]` pool rows.
- Panels as library GLBs, `look.details` layers, `quests.triggers` and `targets.interactions`.
- A starter sword is added by default.

**Materials and shaders** [code/doc]:
- Authors write TSL. `graph()` in `sharddev/src/sharddev/materials.ts` converts it into graph IR JSON. Only approved ops convert.
- The graph has stages `vertex.offset`, `surface`, `lighting` and `outline`; screen-space `post` graphs and `fog` graphs are separate graph kinds.
- The engine compiles the graph to GLSL with its own compiler. The TSL runtime was deleted in NF18 (`close-out-mini-plan.md`).
- So an author can define a new effect as data, but only within that vocabulary and its budgets. G306: raw GLSL is "never data in a shardfile".
- Prepared products (`sdk: "0.3"`) carry `cook.json` with "actual linked GLSL pairs" recorded in phone WebKit (`cook-preparation.ts`). I did not check whether the engine trusts these or derives them again.

**Other content** [code]:
- Water: `water` / `waterWaves` rows.
- Sky: a TSL dome graph, or `look/keyed-sky`.
- Weather: `world/weather`, `weatherEffects`, `rainPresentation`.
- Post: `postStack`.
- Particles: sprite and points cards with declared motion. There is no general particle system.
- Decals: I found no dedicated section.
- **glTF** is a binary container only: tiles, panels and skinned rigs with clips are GLB, textures are KTX2. All meaning lives in Wildshard-specific sections.

## 4. The showcase plans

[doc] `shard-showcase/docs/plans/KITCHEN-SINK.md` plus `kitchen-sink-v2/`. The goal is "every engine feature in one place, authored with **0 % custom TypeScript**… Shared hosts, data rows and AssemblyScript only. A feature that can't be built that way becomes a Wave 1 host row."

**Contents.**
- A town hub with level-tier quest givers, shops, a stable hand and a kill-contract board.
- Weapons: sword with combo and parry, spear, bow, crossbow with ammo types, lever rifle.
- A riding course with a loaner horse; movers and lifts; grapple and zipline; physics props; a hoverboard park with tricks and rails; pressure plates.
- Ladders, scramble climbs, rope bridges and a cave.
- A stealth yard; levels 1–20 with dice-roll misses and seven attributes; six enemy bands; rare variants, night variants and six elites.
- Waves and a gauntlet; the Crate Titan boss with an in-engine cutscene; a "storm hour" weather quest; day and night.
- The Training Vault, a four-room mini dungeon behind a portal.
- Secrets, collectibles, trophies, finishes, feats and full orchestral audio.

**How it would be built.** 87 vertical slices (33 west, 54 east). Each slice does "only the engine / game / host work its piece needs", migrates every other shard that uses what it touched, then builds the showcase piece "as data + AssemblyScript" (`slices/IMPACT.md`). IMPACT gives the recipe for a new host: format schema → route it as a section or `client/plan` kind → author schema → host in game → SDK facade → commons AS → bake.

**New engine or format work identified** (`wave-1-hosts-mini-plan.md`, about 386 hours before the levels, loot and dungeon mini plans):
- **Missing entirely:** conveyor and jump pad, parry, cutscenes, scramble climb, tricks, a see-saw hinge, levels and XP, and an enemy cap.
- **One-user hosts needing a second user:** spear, mount loaner, grapple, stealth, portal.
- **Rebuilds:** an interactables section (Driftwood ships named JSON), movers and the director "out of the plugin", "boss in four paths", "three quest paths", and Pine-shaped weapons.
- A validator rule for interiors staying inside the 500 m cube.

**The "Engine Top 20"** (`tracker/engine-top-20/index.html`): "Only six of the 20 are new". In hours, new 276, rebuild 567, extend 328, and "439 hours (37 %) are spent moving shards rather than building the feature". After the split into separate repos: "a new section means a tagged release and a version bump."

## 5. How an author writes behaviour

**Today** [code/doc].
- `behaviour/*.as` compiles to Wasm.
- ABI v0 uses the prelude `./wildshard` (`sharddev/src/sharddev/as/prelude.ts`): `begin`, `shared(i)`, `player(i)`, `eventCount`/`eventType`, `setShared`, `emit`, `spawn`, `moveTo`, with **four commands per call** (GUIDE.md:270).
- ABI v1 decision scripts get a generated per-row module (`decisionScriptBindings.ts`) exposing `Do.*`, `Read.*`, `State`, `Params`, `Timer`, `Field` and `Event`. The `Do` commands are move, strike, stop, field, spawn, despawn, flag, timer, signal, grant, reward, cue, channel, impulse, encounter, weather, plus body and collider commands.
- ABI v2 has raw region accessors (`as/wsV2.ts`).
- Limits (SCRIPT-ABI.md): fuel 400k per call and 2M per tick; decisions about 10 Hz, only when events are queued; 1–4 pages of 64 KiB, with `memory.grow` refused; at most 16 state slots and 32 parameters.

**A real example**, trimmed from `shard-brasscap/src/behaviour/wyrm.as` (46 lines):
```ts
import { Actor, Strike, Field, Timer, State, Params, Do, Read, Event } from './generated/brasscapWyrmDecision';
function beatSeconds():f64 { return State.phase==2?Params.secondBeat:Params.firstBeat; }
function strike(which:i32):void {
  Do.field(0,Field.tell,1); Do.encounter(4,1);
  const target=Read.nearestPlayer(Actor.boss);
  if(target!=0) Do.strike(Actor.boss,which,target);
  Do.timer(Timer.open,Params.windup);
}
export function onStart():void {
  if(State.phase==3) return;
  if(State.phase==0) Do.encounterPhase(0);
  State.phase=Read.hpShare(Actor.boss)>0.5?1:2; // 0.5: the second phase's `at` in encounters.json
  Do.encounter(4,1); Do.timer(Timer.arm,0.02); Do.timer(Timer.beat,beatSeconds());
}
export function onThreshold(index:i32):void {
  if(i32(Event.subject)!=Actor.boss || index!=1 || State.phase!=1) return;
  State.phase=2; Do.encounterPhase(1);
}
export function onDeath(killer:i32):void {
  if(i32(Event.subject)!=Actor.boss || (State.phase!=1 && State.phase!=2)) return;
  Do.stop(Actor.boss); State.phase=3; Do.encounterWin();
}
export function onTimer(timer:i32):void {
  if(timer==Timer.open) { Do.field(0,Field.tell,0); Do.field(0,Field.gullet,1); Do.encounter(4,3); Do.timer(Timer.shut,Params.window); }
  else if(timer==Timer.shut) { Do.field(0,Field.gullet,0); Do.encounter(4,1); Do.timer(Timer.beat,beatSeconds()); }
}
```
Note the magic numbers such as `Do.encounter(4,1)`, a guard code explained only in a comment. The template's `door.as` likewise addresses fields by literal ids (101, 201).

**Documented pain points** [doc]:
- **Language gotchas:** "no closures that capture locals, no union types, no `any`, no try/catch, no inline object types" (behaviour-language-claude §0).
- **Fuel is priced by module size** (`docs/plans/parked/2026-10-20-opus-wasm-host-PLAN.md`): "Pine's shipped `life` module pays 32,064 per iteration… a 64-point loop… exceeds even the 2M hard cap. That, not JS speed, is why integrators are refused today." Every guest also calls JS imports, and every call copies memory. WASM-HOST, the fix (ABI v2 replacing v0 and v1), was "parked 2026-11-04".
- **Gaps listed in SCRIPT-ABI.md:**
  - "No mover command exists".
  - Impulse and weather are refused at install time.
  - Generic rows refuse spawn and despawn.
  - Restore "does not run those migrations".
  - The pending event queue has no total cap.
- **Line cap:** AS source is capped at "floor(legacy lines / 10)".
- **Proof tapes:** they cannot talk to an NPC yet (GUIDE.md:136).
- **Thin docs:** GUIDE has only one paragraph on scripts.

**Shared behaviour library** [code]: almost none.
- sharddev ships `src/commons/scripts/{abi,bridge,course}.as` (14, 14 and 63 lines). It is referenced only from Nalati's and Nine's generators (`kokparProgram.ts`, `practiceProgram.ts`).
- Shard scripts otherwise import their own generated binding modules (`./generated/nalatiTitanCombined` and similar) or local files. Each shard writes its behaviour from scratch, and reuse happens by adding engine hosts, not libraries.

## Takeaways

- The ideas you're about to propose (a small set of composable primitives, a sandboxed language whose API is the platform, rather than one component per mechanic) were raised on 2026-10-03 by both clean-room audits, `plan-audit-claude.md` and `plan-audit-codex.md`, and were not followed.
- The actual pressure was the "zero custom TypeScript" ruler under deadline. It pushed mechanics into about 250 hosts and 72 per-mechanic sections. HOST-AUDIT, HOST-BAR and the showcase's 37 % "moving shards" overhead are the bill for that.
- The firm constraints that survive are AssemblyScript chosen for determinism (measured), fuel and memory caps, no raw GLSL, and budget-first admission. A scene graph that scripts can change at runtime was explicitly rejected, for budget reasons.
