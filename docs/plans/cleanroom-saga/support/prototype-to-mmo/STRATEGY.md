# An engine of primitives: strategy

> Moved from meta `docs/prototype-to-mmo/STRATEGY.md` at `386423cbea` into the cleanroom saga (D38, 2026-11-26).

> Written by: Claude

> **State:** draft, parked, 2026-11-16. Second version. The first version (trusted TypeScript shards against a small host API) was rejected by Jake the same day and is summarised in [BRAINSTORM.md](BRAINSTORM.md), section 1. This is a strategy, not a plan: it has no rows, no lanes, no J-numbers and no dates, nothing in it is scheduled, and it belongs to no existing plan.
>
> **Authority:** Jake's four voice notes of 2026-11-16 ([evidence/2026-11-16-voice-notes.md](evidence/2026-11-16-voice-notes.md)).
>
> **How sure:** the repos and their plan history were read, not run. The bucket counts in section 2 are a research agent's judgement, row by row, in [evidence/inventory-sections-hosts-scripts.md](evidence/inventory-sections-hosts-scripts.md). Section 11 lists what wasn't checked.

## One-page summary

**The question.** How does the engine become a thousand times more capable, so that really cool ideas can be uploaded into the MMO, without adding hundreds of sections and hosts, and while every upload stays data plus sandboxed WebAssembly that Jake hosts?

**What the history shows.** Since October the shards' one-off TypeScript went from about 99,000 lines to zero. It did not become shard content. It moved into the engine: 46 server hosts, of which 41 serve exactly one shard, and 63 page kinds, of which 37 serve one shard. All the shards together hold about 5,000 lines of AssemblyScript. The counts are still rising: page kinds went from 45 to 63 and sections from 63 to 72 since 22 October.

**Why it keeps happening.** Three structural reasons, none of which a stricter rule can fix:

1. **The world has no general "thing".** On the server only creatures and players are first-class. A mover, a pickup or a portal lives privately inside the host that made it, so a script has nothing general to act on.
2. **The script layer can't hold a mechanic yet.** The shipped interface runs at about 10 Hz, forgets its memory between calls, and prices fuel so that about twelve loop iterations fit in a call. The interface that fixes this (v2) was designed in October and has been parked since 4 November.
3. **Reusable gameplay has nowhere to live except the engine.** The SDK's shared AssemblyScript library is 91 lines. So "a second shard wants this" has always meant "write an engine host".

**The strategy.** Keep the constraint, the format's safety and AssemblyScript. Change where gameplay lives:

1. **A small engine core of primitives**, about fourteen, named for what they are (an entity with a parent, a body, a state field, a zone, a query, a movement mode, an ability) and never for a mechanic.
2. **A shared library of mechanics written in AssemblyScript**, shipped with the SDK and compiled into each shard: zipline, ladder, mount, grapple, boss phases, patrols, stealth, quests. This is where "a second shard wants this" goes from now on.
3. **One script interface.** Finish v2, strip the mechanic-specific operations out of it, and let it run at 30 Hz on the server and client.
4. **A hundred ideas as the method.** Each idea may add or widen a primitive; none may add a section, a host or an operation named after a mechanic. The counts of sections, kinds and hosts may only fall.

**What it buys.** A new mechanic stops being engine work. The compatibility promise shrinks to a small core. And the uploaded shard stays what it is today: data plus sandboxed WebAssembly.

**The biggest risks.** Whether 30 Hz scripts fit a phone's frame budget (the benchmark was built in October; no result is recorded). And scope: there are already four overlapping format plans. This has to become the lens for two of them, not a fifth.

**The first move, if Jake wants one.** Unpark the WebAssembly host work, with one change of aim: its operations describe entities and state, not taming.

---

## 1. The question

In Jake's words: "How do you beef up the engine 1,000 times, 1,000,000 times, such that really cool ideas can be uploaded into the MMO? And how do you do that in a way where we don't add hundreds of custom sections, hundreds of hosts to the API? How do you do that out of composable, simpler, lower level primitives?"

What stays fixed:

- **The hosting constraint.** "People are going to be uploading content to my MMO server, and I'm going to be running it, and I'm not going to be running arbitrary fucking free JS, arbitrary TypeScript." An upload is data plus sandboxed WebAssembly (J341), in one format for everyone (J364).
- **The shape.** "An engine that looks a lot more like Unreal Engine or Unity than it does like what we have now, but it's still an MMO." First-person at its core, third-person to come.
- **The method.** "If I get a chance to implement 100 ideas, and every idea we just expand and generalize the engine... then we can iterate to the future."
- **The author's loop.** An hour for a clean-room three.js prototype; a second hour to add the MMO primitives from the SDK.
- **What exists.** A sandboxed scripting layer is already there: three WebAssembly interfaces, with authors writing AssemblyScript.

## 2. How we got here

The full histories are in [evidence/history-shard-platform-saga.md](evidence/history-shard-platform-saga.md) and [evidence/history-multi-repo-saga.md](evidence/history-multi-repo-saga.md).

### 2.1 The same move, four times

Each time the measure of progress was met, the one-off logic moved down a layer instead of going away.

| When | The measure | Where the one-off logic went |
|---|---|---|
| September | Shards are trusted TypeScript, 4,000 to 27,000 lines each | It was in the shard |
| 3 to 10 October | "80% data and approved systems" | Into "generic" game systems; an audit found 81% of that new platform code had one user |
| 16 to 24 October | Zero custom TypeScript per shard | Into engine hosts; 250 modules named as hosts |
| 24 October to 4 November | Zero custom sections (387 at the peak) | Into a registry of named file families and one-user host approvals |
| Today | One format, counts that only fall | 41 of 46 server hosts and 37 of 63 page kinds still serve one shard |

Jake saw it each time:

- 16 October: "Are we moving basically shard specific logic into the engine … Should it be generic based on WASM + ASM instead?"
- 17 October: "We got rid of 800 shard specific code. We've got 1800 engine code, so nothing is free."
- 22 October: "Stuff that clearly does not belong in the engine or the game needs to go into the shard files as data or WASM. Various hosts need to either be deleted or made generic."

Every remedy so far was a bar: the rule of two, the host bar, one-by-one approvals, the ratchets. None of them was a smaller set of primitives.

### 2.2 What the inventory looks like today

A research agent classified every item as a general primitive, a named gameplay mechanic, a platform service or tooling.

| | Total | General primitive | Named mechanic | Platform service | Tooling |
|---|---|---|---|---|---|
| Format sections | 72 | 34 | 22 | 14 | 2 |
| Page kinds | 63 | 21 | 37 | 4 | 1 |
| Server hosts | 46 | 12 | 34 | 0 | 0 |

- Server hosts include `riding.taming`, `riding.trample`, `population.shelter`, `boss.open-arena`, `quest.kill-steps`.
- Duplicates the project's own audit calls "silly": three day clocks, two water hosts, three weather systems, one herd across four hosts, three boss shapes.
- Even the newest script interface has operations numbered 26 to 37 for taming a horse: trust, ownership, lead, mount, adopt, bond, release, breaking.

### 2.3 What one more mechanic costs

- **When it fits existing rows:** no format change and a few small engine fixes. Brasscap's ledge marksmen cost about 37 lines of engine runtime code.
- **When it needs a new host:** about 7 touch points in the format, 10 or more in the engine, a format release, and a pin bump in every consumer.
- **At showcase scale:** the Kitchen Sink plan priced its missing hosts at about 386 hours before content. Still missing from the engine in that plan: a conveyor, a jump pad, a parry, cutscenes, a see-saw. The "Engine Top 20" tracker beside it found that 439 of its hours (37%) "are spent moving shards rather than building the feature".

### 2.4 This direction was argued for before

It is already in the repos, in three places.

- **The clean-room audits of 3 October** (singleplayer `docs/design/mmo/research/e435/`): "Behaviour should be a sandboxed language whose host API *is* the logic system… the verbs, not a component per mechanic." And: "A graph catalogue on its own forces the engine team to pre-build every mechanic. That's Roblox's pre-Luau problem: every new shard idea becomes engine work." And: "each one-user graduation is a permanent compatibility promise".
- **The WebAssembly host plan of 20 October** (`docs/plans/parked/2026-10-20-opus-wasm-host-PLAN.md`). Jake: "to beef up what can be done with WASM... to unlock new capabilities so that other shards going forward have more capabilities"; "once you enter the WASM, it shouldn't be going back into JavaScript"; "long term we want to run assembly code at 60 hertz or 30 hertz." Its stated end: "New shards should be data plus AS with no TypeScript, including combat feel and motion."
- **The one-format audit of 15 November:** "Those hosts are the MMO primitives Jake wants. They need to be opened up and documented, not deleted."

What this strategy adds is the reason those intentions kept losing to the next deadline, and a way to make them the path of least resistance.

## 3. Why it keeps happening

### 3.1 The world has no general "thing"

Details are in [evidence/engine-internals.md](evidence/engine-internals.md).

- The server is one class holding two tables: creatures and players. Everything else (movers, projectiles, pickups, portals, triggers, bosses) lives in the private storage of the host that installed it.
- There is no general way for one thing to ride or be attached to another. A deck that carries a player, a lift rider, a mount and a grapple are four separate mechanisms.
- The network layer has a general grammar for typed fields, but only six classes use it. The player class has 57 fields, about 38 of them movement state for specific mechanics (`dashT`, `hoverBob`, `climbTo`, `diving`).

So a script has nothing general to reach for. A mechanic that touches the world needs an engine host to own the things it touches.

### 3.2 The script layer can't hold a mechanic yet

Details are in [evidence/inventory-sections-hosts-scripts.md](evidence/inventory-sections-hosts-scripts.md), section 2.

| | v0 | v1 (the main one) | v2 (parked) |
|---|---|---|---|
| Runs | Per tick, divisor set by the shard | About 10 Hz, only when events are queued | 10 or 30 Hz on the server; display rate for visuals |
| Memory between calls | Kept | Wiped every call; 16 saved slots | Wiped for simulation; kept for visuals |
| Fuel | Charged through a JavaScript call | Same | Counted inside the WebAssembly |
| Calls into JavaScript | Every function entry and loop | Same | None |
| Used by | 2 scripts | About 23 programs | Nalati's pack, taming and Titan fire; Driftwood's bridge sway |

- **The fuel price is the module's size.** Every loop iteration costs `bytes × 4 + 128 × functions + 1024`. Pine's `life` module pays 32,064 per iteration, so about twelve iterations fit in a call. The plan says: "That, not JS speed, is why integrators are refused today."
- **v2 fixes speed, fuel and rate**, and a 450-line wolf pack already runs on it as one AssemblyScript program. But it was parked on 4 November ("Wasm host, we're not working on that"), again by G969 and again by J366, and no v1 to v2 migration has started.
- **v2 was shaped around the old code.** Its group sections "borrow original native" state so legacy Nalati code ports byte for byte, and its world operations include taming.

### 3.3 Reusable gameplay has nowhere to live except the engine

- The SDK's shared AssemblyScript library is three files and 91 lines. Each shard writes its behaviour from scratch.
- So the rule "a host a second shard would want becomes an engine primitive" sends every reusable mechanic into the engine. The one-format plan's own list of primitives to open is feature-shaped: population, elites, boss ("2 to 7 primitives"), riding, patrol, grapple, portal.
- In the engines Jake points at, the reusable layer is on the script side. Roblox is moving character movement out of its engine into script-defined abilities. Unreal's ability system covers damage, buffs, cooldowns and status effects with five concepts. Epic moved Fortnite's creators from one device per feature towards entities and components.

## 4. First principles

### 4.1 One rule for where gameplay goes

Something belongs in the engine only if at least one of these is true:

1. **Speed.** It runs over many objects every frame: physics, rendering, pathfinding, animation, replication.
2. **Trust.** It guards something a script must not control: authority, saves, the economy, identity, budgets.
3. **Shared feel.** Players must find it identical in every zone: how the body collides and is predicted, the HUD's chrome, the travel gates.

Everything else is gameplay, and gameplay is written in AssemblyScript: in the shared library if a second shard would want it, in the shard if not.

This replaces "would a second shard want it?" as the test for the engine. That question still matters; its answer now picks between the library and the shard.

### 4.2 Three layers

| Layer | What it holds | Who writes it | How it changes |
|---|---|---|---|
| **Engine core** | The primitives in section 5, plus the platform services | The platform | Rarely; every addition is a long promise |
| **Shared library** | Mechanics in AssemblyScript: zipline, ladder, lift, mount, grapple, boss phases, waves, patrols, stealth, quest runner, dialogue | The platform and, later, authors | Freely; each shard compiles in the version it was built with |
| **Shard** | Its scene, its tables, its own scripts | The author and their agent | Per upload |

The middle layer is what's missing today, and it is what the voice note asks for: "all the primitives in shard dev for cool MMO features in this clean room prototype, just add them".

It also answers the requirement that authors' shards "keep working for years". A shard carries its own copy of the library, so only the engine core has to stay stable.

## 5. The primitives

About fourteen. Each is named for what it is. The third column is what the engine has today; the fourth is what the primitive would absorb once mechanics are rewritten on top of it.

| Primitive | What it is | Today | What it absorbs |
|---|---|---|---|
| **Entity with a parent** | One kind of thing: an id, a position, a parent | Only creatures and players are first-class; no general parenting. The script layer has its own small entity with numeric fields and a declared maximum | Movers, props, pickups, targets, spawns. Riding, carrying and attaching become "set the parent". The train is this |
| **Bodies and joints** | Static, moving and free physics bodies; colliders; joints | Rapier is wrapped well; a general kinematic mover; free prop bodies since format 0.12; a rope chain | Lifts, doors, boats, bridges, see-saws, conveyors, vehicles |
| **Queries** | Ray, overlap, nearest, path, line of sight | General functions; v2 exposes eight through a request ring | Stays as it is |
| **State fields** | Declared typed values on an entity, a player or the shard; each marked replicated, predicted or saved | Declared shared and per-player fields exist. The network grammar is general, but its classes are per feature | Per-feature network classes; per-host save formats; script memory |
| **Events and zones** | Tick, timer, enter, leave, hit, death, interact, input, signal | v1 has about 20 events | Stays, widened |
| **Movement modes** | The engine owns the body, collision and prediction; a mode is a small script that turns input into motion, run the same on client and server | Foot, board, swim and wade are hard-coded. Ladder, zipline, grapple and riding are each hand-written (137 lines, 356, about 1,300 and 691 for the riding physics alone) with their own save and network state | Ladder, zipline, grapple, mount, glide, climb, wall-run, sail, prone, cover |
| **Camera rig** | First- or third-person, with a visible body | First-person only; the local player has no body | The third-person shard type |
| **Abilities** | Attributes, effects, tags, damage rules, hit zones | The combat pipeline and effect service already work this way. Weapon families are compiled in; hit zones are head and body only | Weapon families, boss phases, status effects, stealth bonuses, levels, powers on cooldown |
| **Senses and steering** | Sight, hearing, navigation, steering moves for anything that thinks | A general navmesh. Perception is rewritten in each brain; brains are 1,000 to 1,500 lines of TypeScript each | The brain classes; herd, pack, elite and patrol hosts |
| **Animation** | Rigs, clips, blending, clip events, sockets | About 420 lines; poses are mostly procedural; no clip events | Needed for third-person, takedowns and sword timing |
| **Effects and sound** | Emitters, trails, decals, lights, cues | A 76-line particle pool; audio cues exist | Per-feature effect code |
| **Material graphs** | Shaders as data, compiled by the engine, under a budget | 121 operations, budgets, compiled to GLSL; no raw shader code | Stays as it is |
| **Space fields** | Values that vary over the zone and that scripts and bodies can sample: wind, water, cover, fire, sound | Two water hosts, three weather systems, three day clocks, grass cover inside stealth | Those duplicates |
| **Paths** | Curves that things follow | Mover tracks of up to 10 keys; zipline cables | Rails, patrol routes, races, the train's track |

**Platform services stay as they are** and are not for composing: identity, saves, the economy ledger, the HUD and journal, inventory, chat and travel. A shard declares what it uses; the MMO draws and guards them.

**Several of these are already general.** The combat pipeline, the network grammar, the queries, the physics wrappers and the material graphs need opening up, not inventing. The real gaps are the entity, the movement modes, senses as a shared service, animation and effects.

## 6. The script layer: finish it and re-aim it

This builds on `docs/plans/parked/2026-10-20-opus-wasm-host-PLAN.md`. It keeps AssemblyScript, which was chosen on measurements: it runs at the speed of the browser's own compiled code, modules are 5 to 9 KB, and it computes identical results on every device, which host maths does not.

1. **One interface.** v2 replaces v0 and v1, as that plan already says. Fuel is counted inside the WebAssembly, which removes the module-size price.
2. **Operations about things, not mechanics.** The interface knows entities, fields, events, queries and a short list of commands: set a field, spawn from a declared template, set a parent, apply an impulse, play a clip, start an ability. Taming becomes library code that uses them. The number of operations is a count that may only fall.
3. **State lives in declared fields, not in script memory.** The simulation interface already wipes memory every call. With state in fields on entities, a save, a network update, a rollback and a migration are all the same data. Sixteen slots stops being a limit, and the script itself stays stateless.
4. **30 Hz on the server**, as Jake asked in October, and the visual interface at display rate on the client.
5. **Movement modes are predicted scripts.** A mode's script runs on the player's own client and on the server from the same state, which is why identical maths matters. Roblox's new character controller and Overwatch's Statescript both work this way. This is the hardest piece, and the one that Nine Dragon, the grapple, the mount and the climb all depend on.
6. **A shared library in the SDK.** It starts by rewriting the simplest existing mechanics as AssemblyScript on the primitives: the ladder and the zipline, a door, a lift.

## 7. The format from first principles

Today: 72 sections, 94 named file families, 63 page kinds, a host list.

From first principles a shard has six kinds of content:

| Family | What it holds | Replaces |
|---|---|---|
| **Scene** | The tree of entities and their components, written as a three.js scene and compiled by the SDK. Static geometry is still merged into tiles for speed | `world/*`, most of `look/*`, `sim/bodies`, `world/movers`, `world/props`, `world/targets` |
| **Templates** | Reusable entities: a creature, a weapon, a pickup, a train car | `actors/species`, `combat/items`, `held/*`, the spawn catalogues |
| **Scripts** | AssemblyScript compiled to WebAssembly, including the library modules the shard uses | `sim/scripts`, `actors/*-scripts`, `view/modules`, and every named mechanic |
| **Tables** | Plain rows that scripts and services read: quests, loot, dialogue, strings | `quests/*`, `economy/loot`, `ui/strings` |
| **Assets** | Models, textures, audio, material graphs | The same as today |
| **Platform** | What the shard asks of the MMO: ledger facts, the map, the card, the edges | `economy/ledger`, `ui/card`, `look/map`, `world/edge` |

**Budgets stay first.** An earlier audit advised against "a runtime tree any script can change", because it "defeats budget-first admission". The answer is declared pools: a script can only spawn from templates the shard declares, up to a count the shard declares, so the worst case is still known at upload. The script layer's own entity model already has a declared maximum.

**Nothing here is a new format to migrate to.** It is the direction each change to the existing one should move in. The source plan's rule stands: "No new format. A compiler front end."

## 8. The ideas as the test

[IDEAS.md](IDEAS.md) lists Jake's sixteen zones and ideas and twenty more, each with the primitives it leans on. Which primitives an idea leans on is the agent's judgement; the totals are counted from that file's rows. Across 36 ideas:

| Primitive | Ideas that lean on it |
|---|---|
| Abilities | 27 |
| Senses and steering | 21 |
| Movement modes | 18 |
| Bodies and joints | 16 |
| Space fields | 12 |
| Animation with events | 12 |
| Hit zones on parts | 10 |
| Parenting | 9 |
| Third-person camera and body | 8 |
| Paths | 8 |

- Every idea uses entities, state, events and queries; those are not counted.
- None of the 36 needs a primitive outside section 5. Three need player-versus-player rules, three need a shard-drawn interface beyond the standard HUD, and two need a leaderboard. Those are platform questions.
- **One idea doesn't fit:** building a base, as in Minecraft or Conan. Section 5 has nothing for geometry that players edit and the server saves. Placing pieces from declared templates would fit; digging and free building would not.
- The spread is the point. Wind Waker's boat, the mount, the train car and climbing a giant are all parenting and a movement mode. Crysis's suit, Skyrim's shouts, Mass Effect's powers and elemental arrows are all abilities.

## 9. Getting there

### 9.1 Not a rewrite

The evidence is against starting over:

- VRChat cancelled a rewrite of its scripting engine in 2024 after two years against a three to six month estimate.
- Roblox is generalising by offering its new character controller beside the old one.
- Epic is proving its new entity framework on Fortnite first.

So the core grows underneath what exists. Each step rewrites existing mechanics on a new primitive and deletes the hosts they replace. Old shards keep their hosts until an idea needs the primitive that replaces them.

### 9.2 The rule for each idea

1. **Can existing primitives and the library do it?** Then it is shard tables and shard AssemblyScript, and the engine isn't touched.
2. **Would a second idea want the mechanic?** Then it goes in the shared library.
3. **Does the library need something the core can't give?** Then add or widen a primitive, named for what it is, and in the same change rewrite one existing host on top of it.
4. **Never:** a section named after a mechanic, a new host, a script operation named after a mechanic.

### 9.3 Counts that say whether it's working

The project already has counts that may only fall (`shard-format/docs/ONE-WAY.md`). Use them:

| May only fall | Today |
|---|---|
| Format sections | 72 |
| Page kinds | 63 |
| Server hosts | 46 |
| Script interfaces | 3 |
| Script operations named after a mechanic | at least 12 |

| Should rise | Today |
|---|---|
| Shared AssemblyScript library | 91 lines |
| Share of new ideas that land with no engine change | not measured; near zero for anything new |

The last one is the real measure of "it works".

### 9.4 An order, driven by ideas

This is an order of generalising, not a schedule. Each step has an idea that needs it and existing hosts it lets go.

| Step | What becomes general | Ideas that need it | Hosts it lets go |
|---|---|---|---|
| A | The script interface: one of them, about things, 30 Hz, state in fields; the shared library begins | All of them | The v0 and v1 interfaces; ladder and zipline as engine code |
| B | Entities with parents; fields replicated by declaration | The train, the boat, climbing a giant | Movers, carry, the lift rider, per-feature network classes |
| C | Movement modes as predicted scripts | Nine Dragon, the grapple, the mount, the glider | Grapple, riding and traversal code; most of the player's 38 mechanic fields |
| D | Abilities for weapons; hit zones as parts | The hunt, machine hunting, suit powers | Weapon families; the three boss shapes |
| E | Creatures as library code on shared senses and steering | Infiltration, outposts, herds | The brain classes; the herd, pack, elite and patrol hosts |
| F | A visible body, a third-person camera, animation with events, effects | Sword duels, the rooftop assassin, squad cover | Nothing; this is new |
| G | Space fields and the world's look systems | Sailing wind, fire spread, weather | The duplicate clocks, water and weather |

- Step E continues the creature work already under way in the one-format plan (bodies, temperament, senses, abilities).
- Step A is the WebAssembly host plan, re-aimed.

## 10. The author's two hours

**Hour one: the clean room.** Any three.js, any JavaScript, on the author's machine. Nothing changes here.

**Hour two: the upload.** The agent, with the SDK and its guide:

1. Runs the scene code at build time, as the SDK does today, to get the tree of entities.
2. Turns what moves or reacts into entities with components.
3. Replaces what the prototype hand-rolled with library mechanics: its enemies, its weapons, its lift, its quest tracker.
4. Rewrites the rest of its rules as AssemblyScript against the primitives.
5. Declares what it wants from the MMO: quests in the journal, collectibles, the ledger.

**What makes hour two an hour:**

- **The library is large**, so most of step 4 is already written.
- **The prototype's rules are written the right way from the start**: one module that never touches three.js, one update at a fixed step, motion on a path as a function of time, quests and collectibles as tables.
- **The same file can run in both places.** AssemblyScript ships a "portable" standard library intended to let one source file compile with the ordinary TypeScript compiler as well. If that holds here, the prototype's rules run in the clean room as TypeScript and upload unchanged as WebAssembly. This is untested and worth an early experiment.

## 11. Risks, and what wasn't checked

**Risks.**

1. **Speed on the phone.** The target in the host plan is 1 ms per frame for 20 scripts. The benchmark was built in October and no result is recorded. If 30 Hz scripts don't fit, more has to stay in the engine and the primitive list grows.
2. **Predicted movement scripts are hard.** Two industry examples work this way; neither is a small team's. Until step C works, movement mechanics stay hand-written.
3. **Scope.** Jake on the format plans: "im so lost", "so many draft plans". There are four overlapping ones (ONE-FORMAT, SHARD-SOURCE, SHARD-COMPAT, SDK-SPLIT) and two parked (WASM-HOST, HOST-AUDIT). This strategy should replace how two of them are aimed, not join them.
4. **Moving old shards costs more than building new things.** The showcase's engine tracker measured 37% of its hours going there. So don't move them on principle. A host stays until an idea needs its replacement.
5. **AssemblyScript is awkward.** No closures, no exceptions, almost no union types. The library and generated bindings hide most of it. Nothing was found on how well coding agents write it at scale; the shards' 5,000 lines are the only evidence.
6. **A general entity is easier to abuse.** Declared pools and budgets are the defence, and the budgets must exist before the freedom does.
7. **The same mechanic could feel different in every zone.** If movement is scriptable, each author can change it. A strong default library and a limit on what a mode may alter are the answer; how strict is Jake's call.

**What wasn't checked.**

- Nothing was run. No benchmark, build or game.
- The bucket counts in 2.2 are one agent's judgement per row.
- Whether the engine's creature, weapon and quest systems can be reached from scripts without their hosts was not traced in code.
- The portable AssemblyScript idea in section 10 is unverified beyond the package shipping a portable library.
- The research on Epic's next engine rests partly on a trade-press report of a conference keynote. This document does not rely on it.
- The lead agent re-read these in source: the taming operations in the v2 interface, the 46 cases in the server host switch, the 91-line shared library, the fuel formula, the file sizes quoted in section 5, and the quotes from the WebAssembly host plan, the one-format audit and the 3 October audit. Everything else is as the studies in `evidence/` reported it.

## 12. Open questions for Jake

1. **Is the rule in 4.1 right?** Reusable gameplay goes into a shared AssemblyScript library, and the engine takes only what needs speed, trust or shared feel. This changes the one-format plan's list of primitives: boss, riding, patrol and grapple would become library modules.
2. **Does the WebAssembly host come off the shelf**, re-aimed at entities and state?
3. **Is a general entity with a parent acceptable**, with declared pools as the budget guard? An earlier audit advised against a tree scripts can change.
4. **May an upload change how the player moves?** Scripted movement modes are what make parkour, sailing and climbing possible, and they are also what could make zones feel inconsistent.
5. **Which idea goes first?** The train exercises parenting. Nine Dragon exercises movement. Infiltration exercises senses. Each pulls a different primitive forward.
