# An engine of primitives: brainstorm

> Moved from meta `docs/prototype-to-mmo/BRAINSTORM.md` at `386423cbea` into the cleanroom saga (D38, 2026-11-26).

> Written by: Claude

> **State:** working notes, 2026-11-16. Second version, rewritten with [STRATEGY.md](STRATEGY.md). Options weighed, including the ones not picked and the one Jake rejected. Nothing here is decided or scheduled.

## 1. Where could gameplay live? Six answers

The central choice is where a new mechanic goes when an author has an idea the engine can't do yet.

| | Answer | Who does this | Why not, or why |
|---|---|---|---|
| A | **An engine host per mechanic** | Wildshard today; Fortnite Creative's devices | Every idea becomes engine work and a long promise. 41 of 46 server hosts serve one shard |
| B | **Trusted TypeScript in the shard, against a small host API** | The singleplayer-era shards; this folder's first strategy | **Rejected by Jake, 2026-11-16.** It breaks the hosting constraint: "I'm not going to be running arbitrary fucking free JS, arbitrary TypeScript." It also answered one zone, not the engine |
| C | **The prototype as its own page inside the MMO's shell** | Discord Activities, web game portals | Not an MMO: no shared server authority, no shared enemies or weapons, and each zone feels different |
| D | **JavaScript run inside a WebAssembly sandbox** | Figma's plugins | Keeps the constraint, but the project measured it in October: 20 to 40 times slower than AssemblyScript, and maths that differs between devices |
| E | **Data only: a logic graph or a catalogue of devices** | LittleBigPlanet, early Roblox | The 3 October audit's warning: the platform team must build every mechanic first |
| F | **AssemblyScript on a small core of primitives, with a shared library** (picked) | Roblox with Luau; Overwatch's Statescript; where Jake's own plans already point | The work is the core and the library. Speed on the phone is unproven |

**What the first strategy got wrong.** It measured the distance from a prototype to a shard and tried to shorten it by loosening the rule. The rule is fixed. The distance shortens when the sandboxed layer can hold whole mechanics and a library supplies most of them.

**B, C and D are not fallbacks.** They are listed so nobody proposes them again without new evidence.

## 2. Choices still open inside the picked answer

| Choice | Options | Leaning, and why |
|---|---|---|
| **Shape of an entity** | (1) A tree of nodes with a fixed set of components. (2) Flat rows with a parent column. (3) A full entity-component system where authors define components | (1) or (2). A fixed component set keeps the engine's fast paths and the upload check simple. Author-defined data goes in state fields |
| **Where script state lives** | (1) In the script's memory, saved by the host. (2) In declared fields on entities | (2). Saving, replicating, rolling back and migrating are then one mechanism. The v2 simulation interface already wipes memory each call |
| **How a movement mode is written** | (1) A free AssemblyScript function run on client and server. (2) A table of states and transitions the engine interprets, like Statescript. (3) Both: a table for the common cases, a function for the rest | (3). The parked host plan already has combo transition tables applied by the 60 Hz host |
| **How the library is delivered** | (1) Source compiled into each shard. (2) Separate modules the engine links at load | (1). Each shard keeps the version it was built with, so the library can change freely. Shards grow by a few kilobytes |
| **A friendlier layer above AssemblyScript** | (1) None; agents write AssemblyScript. (2) Generated typed bindings so scripts read `entity.health`, not offsets. (3) A small language of its own | (2) first. Jake said in October he was "happy to build DSLs", and the source plan found scripts full of raw memory writes |
| **How fast scripts run** | 10 Hz as today, 30 Hz, or 60 Hz | 30 Hz on the server, display rate for visuals. It depends on a phone benchmark that has no recorded result |
| **How much a zone may change the player** | (1) Nothing; movement is the engine's. (2) Modes from the library only. (3) Any scripted mode within limits | Jake's call. (3) is what makes parkour, sailing and climbing possible |

## 3. What the shared library might hold

Not a spec. Each row is a mechanic the engine holds today as one or more hosts, and what it would be written on.

| Library module | Written on | Engine code it could replace |
|---|---|---|
| Door, lift, platform | Bodies, paths, events | Parts of the movers host |
| Ladder, zipline, rail | Movement modes, paths | `ladder.ts`, `cableTraversal.ts` |
| Grapple | Movement modes, queries, joints | The grapple code, about 1,300 lines |
| Mount and taming | Parenting, movement modes, senses, state fields | `riding.mounted`, `riding.taming`, `riding.trample`; twelve script operations |
| Vehicle, boat | Bodies, parenting, movement modes, space fields | New |
| Patrol, guard, camp | Senses, paths, steering | The patrol and encounter hosts |
| Herd, pack, flock | Senses, steering | Four herd hosts; three brain classes |
| Boss phases | Abilities, parts, state fields, events | Three boss shapes |
| Waves and a director | Events, declared pools, state fields | Encounter and population hosts |
| Weapon families | Abilities, queries, animation events | The compiled-in weapon families |
| Stealth | Senses, space fields, abilities | The stealth and grass-cover code |
| Quest runner, dialogue | Tables, events, platform services | `quest.kill-steps` and its siblings |
| Day clock, weather | Space fields, state fields | Three day clocks, three weather systems |

**The test for a library module:** it uses no script operation and no section that a different mechanic couldn't also use.

## 4. The train, as a test of parenting

The train was the example in the vision note. It is now one test among many: it needs entities with parents, a path and bodies.

| Option | How it works | Good | Bad |
|---|---|---|---|
| **Cars are entities on a path; riders are their children** (fits the primitives) | Each car's position is a function of server time along a path. A rider's position is held relative to the car. A car wraps inside the dark tunnel | Matches what Jake described; nothing is teleported from the rider's view | Needs parenting that survives a jump of position |
| **Train stands still, canyon scrolls** | The train is the origin; scenery loops past | No moving-platform physics | Awkward as soon as players get off |
| **One rigid train that teleports** | A single mover jumps from tunnel to tunnel | Closest to today's movers | The whole train must fit in a tunnel; today a jump of more than 1.5 m drops the riders |
| **Two trains** | One leaves as the other arrives | No teleport | Not the set piece Jake described |

**Numbers.**

- A quarter circle of radius 400 m is about 630 m of track.
- At 12 m/s a car is in the open for about 50 seconds; at 8 m/s, about 80 seconds.

## 5. Conventions for a prototype that uploads easily

A first draft of the one page that would go in the prompt for hour one. A prototype that follows it imports nothing from Wildshard.

1. **Two modules.** `rules` holds all rules and state and never touches three.js. `view` builds the scene and only reads the rules' state.
2. **The rules are written in the subset of TypeScript that AssemblyScript accepts.** No closures, no exceptions, plain classes and numbers. Whether one file can serve both is untested (STRATEGY section 10).
3. **One clock.** The rules have one `update(dt)` at a fixed step.
4. **Motion on a path is a function of time.** Never add up per-frame deltas for something every player must see in the same place.
5. **Things are a flat list with a parent**, not nested objects with methods. Players are in the list, even with one player.
6. **Input is a small record** (move, look, fire, interact), filled in by the page.
7. **The box.** 500 by 500 metres, metres as the unit, y up, x and z within ±250, eye height 1.68 m.
8. **Quests, collectibles and enemy types are tables** at the top of the rules, not scattered conditions.
9. **The HUD is drawn from a short list of calls** (objective, counter, boss bar, marker, message).
10. **It must hold 60 fps on the phone** before anything else happens to it.

## 6. The second hour, as a checklist

A first draft of the chapter the authoring guide lacks.

1. Run the `view` module through the SDK's scene compiler. Fix what it refuses.
2. Mark what moves or reacts as entities; give them bodies and parents.
3. For each thing the prototype hand-rolled, look for a library module first: enemies, weapons, lifts, the quest tracker.
4. Compile what's left of `rules` to WebAssembly against the primitives.
5. Move the tables into the shard's tables. Declare which state fields are replicated and which are saved.
6. Declare what the zone asks of the MMO: journal quests, collectibles, ledger facts.
7. Run it with two players. Fix what assumed one.
8. Upload to staging.

## 7. Loose ideas

- **Rewrite one host first, as proof.** The ladder is 137 lines and the zipline 356. Both as library AssemblyScript, with the engine files deleted, would show the whole path on something small.
- **A new host needs a note saying which of speed, trust or shared feel it is for.** That turns the rule in the strategy's section 4.1 into a habit at review time.
- **Count the ideas, not the lines.** A board of ideas landed with "engine changed: yes or no" would show whether the method is working better than any line count has.
- **Make the idea bank public to authors.** Each idea is a prompt someone could vibe-code against in hour one.
- **Let the prototype be judged before any upload.** Singleplayer's GW2-ZONES found that content nobody finished counted for nothing. A prototype that isn't fun shouldn't be uploaded.
- **The smoke bot as the gate.** A bot that boards the train, rides a loop and fires a shot proves more than a list of refusal rules.
- **Third-person may come cheaper than it looks** if the engine owns the camera and the body and the shard never touches either.

## 8. Questions nobody has answered yet

- Do 30 Hz scripts fit the phone's frame budget? The October benchmark has no recorded result.
- Can a movement mode written as a script be predicted on the player's device without visible correction?
- How many script operations does a general core need? The v1 interface has several dozen reads and commands, many of them tied to one mechanic; the aim is fewer, not more.
- Can the creature, weapon and quest systems be driven from scripts without their hosts?
- How well do coding agents write AssemblyScript at the scale of a whole zone? The shards' 5,000 lines are the only evidence.
- What does a shard's saved state look like when its scripts change between versions?
- Who reviews an agent-written shard before it reaches production, and how?
