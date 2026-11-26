# Clean-room research: a Fable 5.2 MMO clean room for every zone

> Written by: Claude (opus), 2026-11-26. Ask: A19.

Research for the
[cleanroom saga](../2026-11-26-opus-cleanroom-saga-master-PLAN.md).
It answers four questions:

1. What did we prompt to start with?
2. How did the prompt change?
3. Why a clean room, and how does a clean room get into Wildshard?
4. How do we make Fable 5.2 clean rooms of the other eight zones?

Surveyed 2026-11-26: this repo at `d7f1a2d`, the clean room
(`~/projects/game-demos/showcase-zone-clean-room`) at `3afcd88`,
meta, engine, shard-format and sharddev at their checkouts that day,
and the seven shard repos. Two read-only research agents did the
engine and shard surveys. Their findings are cited by path, and
anything they inferred is marked [inferred].

Short names for paths:

- **CF** is the clean room (Cratefall).
- **W** is `~/projects/games/wildshard`.
- **SP** is `~/projects/games/wildshard-singleplayer`.
- **META** is `~/projects/games/project-wildshard-meta`.

## 1. What we prompted first

Ask A16 (2026-11-25), in Jake's words: *"We want to kind of make a
short prompt for a fable one shot of the plan. Clean room, standalone
new git repo, typescript & three.js, no sharddev / shardformat /
engine, playable singleplayer that looks like playing the MMO alone,
no multiplayer or server, mobile friendly, portrait mobile HUD."*

The first draft was `docs/prompts/fable-one-shot.md` at `efa2105`
(02:22): 174 lines, one file, distilled from §1–§3 of the Kitchen Sink
plan, the locked combat maths (levels-combat §15) and UI-PICKS. It had
these sections:

- **Ground rules:**
  - TypeScript strict, three.js, Vite, pnpm, a new git repo.
  - No engine, server or accounts; saves in localStorage.
  - No downloaded art or audio.
  - A first-person camera.
  - Mobile first in portrait, with a 16-enemy AI cap.
  - Vitest on the combat maths.
  - A dev menu: set level, XP ×10, teleport, time, storm.
- **Look:** a warm orange and cool grey test yard with cyan accents,
  and *"never placeholder"*.
- **Map:** the 500 × 500 m cell, the peaceful west with its town and
  nine toys (range, physics yard, riding, movers, grapple, climb,
  the Rock, hover park), and the combat east.
- **The rest:** levels and combat (the golden-ratio XP curve, the
  attributes), the robot roster, quests and economy, a calm portrait
  HUD, audio, and a "done when".

## 2. How it changed

Every step is a commit in this repo (`git log efa2105..34ba249`) and
a steering line in A16. The whole job took 23 minutes, from 02:22 to
02:45 local time.

| Commit    | Step                         | Brief | Zone |
|-----------|------------------------------|-------|------|
| `efa2105` | first draft, one file        | 174   | —    |
| `23c9320` | split brief from zone        | 38    | 144  |
| `dbc71e8` | zone made vague, standalone  | 38    | 58   |
| `760da03` | some detail back             | 38    | 93   |
| `8cf94de` | cube, roads, dungeon, raid   | 38    | 104  |
| `97eb820` | brief cut to essentials      | 19    | 104  |
| `cf0d55a` | brief pushed to AAA, loop    | 32    | 104  |
| `e3db735` | self-review loop dropped     | 27    | 104  |
| `accdfe6` | judge each slice, no "loop"  | 31    | 104  |
| `e217455` | named Showcase MMO Zone      | 31    | 104  |
| `34ba249` | moved to the clean room      | —     | —    |

"Brief" and "Zone" are line counts of `FABLE-PROMPT.md` and
`ZONE-DESCRIPTION.md`.

What drove each step (A16 and the journal
`project/journal/2026-11-25-fable-one-shot-prompt.md`):

1. **Two files.** Jake: *"let's split this into two files."* The game
   with no tech went into `ZONE-DESCRIPTION.md`, so it can feed other
   builds. The short build brief that reads it went into
   `FABLE-PROMPT.md`.
2. **Vague beats detailed.** Jake: *"for fable level intelligence so
   the less you poison / steer / context rot it the better … should
   not reference other files … let fable decide if its going to build
   first or third person … The more vague we are the more fable will
   just make something magical & amazing."* The description went from
   144 lines to 58. The maths, the roster names, the HUD layout and
   the camera choice all went.
3. **Some detail back.** Jake: *"i think you might have gone overboard
   right we do want to add some detail back in lol"*. He picked what
   came back:
   - the west places by name;
   - the robot roster;
   - the set pieces;
   - the quest and economy hooks;
   - the six-band shape.
   Combat feel and the HUD stayed vague.
4. **Keep the shard rules.** Jake: *"we designed a bunch of shit and
   we don't want to lose: mini dungeon, raid style final boss; the
   whole zone must be a 500x500x500 cube … it must still be a valid
   wildshard MMO zone/shard"*. This added the cube, the four road
   entrances mid-edge, and interiors that sit physically inside the
   cube.
5. **Cut the brief.** Jake: *"the PROMPT.md is also too leading"*.
   What was left: TypeScript and three.js, single-player, mobile first,
   and done means the Titan beaten on a phone. Gone: git, pnpm,
   Vitest, the asset ban, the enemy cap and the dev menu.
6. **Push the bar.** Jake: *"far more aggressive on the AAA nature …
   plays like a AAA PS5 MMORPG … big wow impact"*.
7. **No loop.** A "work in a loop until it's AAA … don't stop" line
   went in and came out. Jake: *"I Dont think we can afford to prompt
   it to work in a loop"*, *"fable will guzzle all the tokens"*, but
   *"we do want to tell it to build a slice play it and judge it
   harsley"*. The result is one pass per slice, with no "loop", no
   "again" and no "don't stop".
8. **Rename and move.** "Kitchen sink" became "Showcase MMO Zone" in
   both files. They then moved to the empty clean-room repo, and the
   brief lost its how-to header so that nothing Fable read named
   Wildshard.

### The prompt as run

The brief became the clean room's `README.md` (CF `d00211a`, 02:47),
and Jake pasted it into a fresh Claude Code session on Fable.
`ZONE-DESCRIPTION.md` there is byte-identical to `e217455`. The brief
in full:

```text
Make an absolutely amazing single-player game that feels like an MMO
zone and plays like a AAA PS5 MMORPG. The zone is described in
`ZONE-DESCRIPTION.md`. Read all of it first.

- Graphics: amazing. It should feel like a polished AAA game and
  have a big wow impact from the very first frame.
- Feel: every swing, shot, jump, ride and kill should feel juicy
  and satisfying, with real weight, impact and feedback.
- World: alive and dense, with something worth finding around every
  corner. Never empty, never grey, never placeholder.
- Mobile first. It must play great on a phone held in portrait,
  with touch controls, and still look stunning there. Desktop should
  work too.
- TypeScript and three.js. Single-player; no multiplayer or server
  needed.

Build it slice by slice. After each slice, play it yourself on a
phone-sized screen, judge it harshly against a shipped PS5 game, and
fix what falls short before you start the next slice.

Done when you can play it on a phone from level 1 in town to beating
the Crate Titan, and it looks and feels like a AAA game the whole way.
```

### What it made, and what that cost

Everything ran in one Claude Code session in the clean-room folder,
`7aabdbae`, kept under
`~/.claude/projects/-Users-jakeverbaten-projects-game-demos-showcase-zone-clean-room/`.
It ran from 2026-11-25 02:48 to 2026-11-26, mostly on Fable 5.2 with
some Opus. It also spawned about 30 Codex helpers for textures, icons
and character paint, which ran in its scratch folders.

- **The one-shot:** from 02:48 to 05:16 (`81c7fdd`), about 2.5 hours
  and 39 commits, with five subagents building in parallel. An audit
  (CF `docs/AAA-PLAN.md` §1) found 71 of 78 description requirements
  done, 7 partial and none missing, at 60 fps on desktop. In the
  audit's words it *"reads as a responsive, well-instrumented
  prototype with a strong UI"*, not yet a console game.
- **The AAA push:** the same session, steered by Jake, ran on to
  `3afcd88`: 368 commits and 63k lines (three.js, Rapier, Vite),
  deployed to <https://raynos.github.io/showcase-zone-clean-room/>.
  It used up the Fable allowance. Jake: *"we used 100% of the fable
  ( 580$ cost )"*. After that the rules were a Fable main agent, at
  most five subagents, and at most two of them on Fable.
- **What it left:**
  - 25 golden frames (start, now and a painted target);
  - a media library (`docs/media/`: 182 stills, 18 clips, a
    trailer);
  - a state page;
  - plans for the AAA push, combat, the HUD and first person.
  None of it has been checked on a real phone.
- **Jake's verdict** (in the clean-room session, 2026-11-25): *"Let's
  keep cratefall free as its own standalone game"*, *"i really like
  the third person hero so i think i'm going to make the engine third
  person"*, *"Dodge roll is fun"*. On 2026-11-26 he added that he
  likes the quality of the work but not its art direction (A18).

## 3. Why a clean room

1. **To see what the plan becomes without the engine.** The Kitchen
   Sink is about 2,100 hours of slices (33 west, 54 east), and none is
   built. The journal for A16 puts it this way: Jake wanted *"to see
   what one Fable session makes of the plan before anyone renovates,
   audits or moves it forward"*. The one-shot answered that in 2.5
   hours.
2. **The engine's shape would have steered it.** A builder inside
   Wildshard has to work through hosts, sections, the shard file and
   the 0 %-custom-TypeScript rule. A clean room shows what the design
   wants when nothing gets in the way, and that is the target the
   engine then has to reach.
3. **It is how Jake already wants authors to work.** META decisions
   J339 (*shard source is as easy as a cleanroom three.js project*),
   J343 (the fps bars) and J344 (*the three-cleanroom blocker loop;
   Opus builds, Fable audits*) come from 2026-11-13. On 2026-11-16 his
   voice notes describe *"an hour to vibe-code a clean-room three.js
   prototype of a zone, then a second hour telling the CLI 'upload
   this to the MMO'"* (META
   `docs/plans/parked/2026-11-22-fable-prototype-to-mmo-PLAN.md`).

### Clean rooms we made before

- **Look-only clean rooms, 2026-11-13 to 11-19.** Mossgate, Brasscap,
  Mirror Salt and Glowfen got standalone three.js and Rapier pages,
  built as look targets and ported back by hand (META
  `project/archive/TEMPLATES-CLEANROOM-PLAN.md`, Part B of
  `project/archive/2026-11-19-shard-source.md`).
  - They had no gameplay: posed creatures for screenshots only (META
    `docs/prototype-to-mmo/evidence/repo-study-shards-and-cleanrooms.md`
    §3).
  - The Mossgate and Brasscap checkouts are gone.
  - `W/shard-mirror-salt/cleanroom/` and `W/shard-glowfen/cleanroom/`
    are still there.
- **Sky Reach and Signal Dunes** were rebuilt clean-room from their
  docs alone (row 0, E357 Z3).
- **Cratefall is the first full game** made from a plain description:
  combat, levels, quests, a boss. That is what's new.

## 4. How a clean room gets into Wildshard

### What a shard file is

The spec is in `W/shard-format/docs/`:

- `SHARDFILE.md`: the fields. It says the version is `0.1.0.2`, but
  `src/format/version.ts` says `0.1.0.6`.
- `RUNTIME-CONTRACT.md`: the sections, client-plan kinds, server hosts
  and limits, mostly generated from code.
- `SCRIPT-ABI.md`: the Wasm scripts.
- `PLATFORM-FILE-FAMILIES.md`: the named JSON files.
- `preparation.md`: `cook.json` and `validation.json`.
- `VALIDATION-CODES.md`: the refusal codes.

The author's view is `docs/GUIDE.md` §2–§3 in this repo.

A built shard (`out/shard-showcase/`) is a folder, tarred into
`<slug>.shardfile`:

- **`shard.json`, the index.** Identity, the format version, the
  requires, the sections, the runtime, `files` (each file's hash,
  kind, bytes, GPU bytes, triangles and draws), and admission (the
  budgets). Files that only the server reads are listed under
  `admission.server` (J91).
- **`sections/<area>/<name>.json`, the rows.** Each has a
  `wildshard:<name>@1` schema. There are about 72 known sections and
  no custom ones. This shard ships 35, among them `world/terrain`,
  `actors/creatures`, `combat/strikes`, `quests/quests` and `ui/ui`.
- **`blobs/<kind>/<sha256>`.** Immutable GLB, image, tile and Wasm
  files. Scripts ship only as compiled Wasm.
- **`mounts/`.** Files served at public URLs.
- **`cook.json`.** The preparation (J487): mounts, the near-ring fence
  and a hint for warming up programs.
- **`validation.json`.** The build's receipt: a cache hint, not a
  gate.

The validator is strict:

- Unknown keys fail, and only plain JSON is accepted.
- Sections, kinds and hosts must each be on the registered list.
- Wasm may import only `ws_read` and `ws_list`, with 1–4 memory pages
  and no `memory.grow`.
- The 500 m cube is checked, with four clear 8 m entryways at y=0.
- Every cost is re-measured.

Budgets:

- **Wire:** library 8 MB, critical 2 MB.
- **Resident:** library 25 MB, sim 25 MB.
- **Server:** tick ≤16.7 ms, ≤25 MB, ≤10k entities.
- **Wasm:** ≤256 KiB per module, 9 modules per side, capped fuel.
- **Audio:** 6 MB green, 10 MB red.

### How gameplay gets in

J341: the uploaded file is data plus sandboxed Wasm. TypeScript and
three.js are how authors write source; they run at build time only.
There are three routes:

1. **Data rows** in sections or named files.
2. **AssemblyScript compiled to Wasm:** v1 decision scripts at 10 Hz.
   ABI v2 is parked with WASM-HOST.
3. **Picking a compiled-in engine host by name:** about 63 page kinds
   and 46 server hosts (RUNTIME-CONTRACT §2–3).

**A host** is shared engine code that shards drive with data (engine
`docs/HOST-BAR.md`; register `engine/lint/host-register.json`, 416
rows). Birthing a new one takes 11 steps (`kitchen-sink-v2/slices/
IMPACT.md` §3): a format schema, routing, generated types, the engine
host, an SDK facade, shared AssemblyScript, the bake, the register,
tests, docs, and migrating every user. Across repos that means a
shard-format release plus pin bumps in the engine, api-server and
sharddev. A host with only one user needs Jake's yes (G595).

**The structural problem** (META `docs/prototype-to-mmo/STRATEGY.md`
§3, dated 2026-11-16):

- 41 of 46 server hosts and 37 of 63 page kinds served one shard.
- The server has no general entity.
- The script layer can't hold a whole mechanic.

So today every Cratefall mechanic Wildshard lacks becomes a new host.
The parked PROTOTYPE-TO-MMO plan (META
`docs/plans/parked/2026-11-22-fable-prototype-to-mmo-PLAN.md`)
proposes the alternative: about 14 engine primitives plus a
shared AssemblyScript library, where *"An idea may widen a primitive;
it may never add a section, a host or a script operation named after
a mechanic."*

### Server authority changes everything gameplay

Cratefall is client-only. Wildshard runs every gameplay system on the
server, even offline: offline is a listen server in a Web Worker
(J31). The engine `server/` owns AI, combat resolution, quests, loot,
weather, scripts and saves (META multi-repo master plan §5). It ticks
at 60 Hz with Rapier, the client predicts only its own character, and
hits rewind creatures for up to 12 ticks.

What that means for each Cratefall system:

- **Combat:** combo windows, perfect dodge, finishers and Overdrive
  are resolved on the server and predicted on the client.
- **Aiming:** Cratefall's per-bone rays become server hits on
  head and body zones.
- **Movement:** every new mode (horse gaits, grind rails, conveyors)
  becomes a predicted mode, with a wire class, a sim branch and a
  client consumer.
- **Scripts:** they run at 10 Hz and are event-driven, so Cratefall's
  per-frame TypeScript can't be ported as it stands.
- **Saves:** they move from localStorage to the server; XP, loot and
  perks become server-trusted.
- **Shared state:** the day and weather are shared. Fake adventurers
  meet real players, at most 32 to a room.

### The pieces, and where each gap lands

Layers: **F** format, **EC** engine client, **ES** engine server or
shared sim, **SDK** sharddev, **D** shard data and AssemblyScript.
Cost: **$** data in an existing host, **$$** extend a host, **$$$** a
new engine system. "KS" is the Kitchen Sink slice that already covers
the piece.

| Piece              | Gap in    | Cost  | KS slices          |
|--------------------|-----------|-------|--------------------|
| Terrain            | D, SDK    | $     | W0a                |
| Buildings, props   | D, SDK    | $–$$  | W0b                |
| Blender models     | D         | $     | E1a, E12f          |
| Surfaces, shaders  | F, EC     | $$    | —                  |
| Light, fog, sky    | D, EC     | $     | W11a               |
| Third-person cam   | EC, ES    | $$$   | (meta PF16)        |
| Animation, body    | EC        | $$$   | —                  |
| Combat engine      | F, ES, EC | $$$   | E0b, E0g, W3d      |
| Shooter stance     | EC, ES    | $$    | W3b, W3c           |
| Weapons            | D, F      | $–$$  | W3a–c, E0i         |
| Enemies, AI        | D, ES     | $$    | E0h, E1c–E6        |
| Elites, bosses     | ES, EC, F | $$$   | E8a–e, E12a–h      |
| Horse riding       | ES, F     | $$    | W10a, W10b         |
| Hoverboard         | D         | $     | W5a                |
| Movers, zipline    | D, ES     | $–$$  | W6a–d, W7a–b       |
| Skate park, grind  | ES, F, D  | $$    | W5b, W5c           |
| Quests, boards     | D, F      | $–$$  | W1b, E1f, E1g, E13 |
| Dialogue, voices   | D, EC     | $–$$  | W1a                |
| Progression 1–20   | F, ES, EC | $$$   | E0a–f, E0i         |
| HUD layouts        | EC        | $$    | E0e, E0f, UI-PICKS |
| Audio (synth)      | SDK or EC | $–$$$ | W11b, E15a–b       |
| Weather, day       | D         | $     | W11a, E7b, E9      |
| Interiors (Vault)  | ES, F     | $$    | E10a–d             |
| Cutscenes          | EC, F     | $$    | E12d               |
| Sim adventurers    | ES, EC    | $$    | —                  |
| Phone budgets      | D, CK     | $$    | W12, E17           |

Notes on the big ones:

- **Third person (camera, body, animation).** The engine is first
  person only, and the local player has no body mesh
  (`W/engine/src/client/game/cosmetics/cosmetics.ts:3`). Cratefall's
  feel rests on its orbit camera (`src/core/camera.ts`) and its
  procedural humanoid (`entities/humanoid/anim.ts`, 1,330 lines).
  Jake has already said the engine goes third person.
- **The combat engine.** The engine has swept melee, a dodge and
  status effects that no server motor reads yet. There's no ability
  or skill system. Cratefall's `src/systems/combat.ts` (1,789 lines)
  has strings, a perfect dodge, skills, Overdrive and finishers.
- **Progression.** The engine has no XP, levels or perks today.
- **Budgets.** Cratefall plans about 10 MB before the town is playable
  and about 50 MB in all. A shard gets 2 MB critical and 8 MB library
  wire. Nothing in Cratefall has been measured on a phone.
- **Audio.** Cratefall synthesises all its sound (about 6.4k lines of
  Web Audio). The cheap route renders it to files at bake time
  [inferred]; a live synth host is the expensive one.

Some of what Cratefall has no plan covers yet: skills and Overdrive,
finishers and weak points, simulated adventurers, the landscape HUD,
synth audio, and the Tally Book and Overtime endgame.

The Kitchen Sink slices still name singleplayer-era paths, and
re-baselining them is open row MR1 in `kitchen-sink-v2/STATE.md`.

## 5. Clean rooms of the other eight zones

### The zones

| Zone        | Repo               | TS    | Status       | Best source  |
|-------------|--------------------|-------|--------------|--------------|
| Driftwood   | shard-driftwood    | 18.1k | live         | SP plans     |
| Pine Hollow | shard-pine-hollow  | 20.6k | earlyAccess  | SP remaster  |
| Nalati      | shard-nalati       | 20.2k | earlyAccess  | SP design/   |
| Nine Dragon | shard-nine-dragon  | 21.4k | experimental | SP plan      |
| Sky Reach   | shard-sky-reach    | 9.2k  | experimental | SP plan      |
| Signal Dunes| shard-dunes        | 5.8k  | experimental | SP plan      |
| Mossgate    | sharddev template  | 4.2k  | template     | META plan    |
| Brasscap    | shard-brasscap     | 1.5k  | earlyAccess  | rows, plan   |

"TS" is lines of shard source. Every repo's last activity was
2026-11-25, mostly SDK and kit moves.

- **Driftwood Isle.** A low-poly tropical island reached by sailboat.
  You hunt three glyph shards to open the Ring Shrine and fight the
  Drowned Captain. Swimming and diving are its real mechanic; a boat
  and a zipline round it out. Thin by the MMO bar: one chain of four
  steps.
  Sources: SP `project/archive/2026-09-18-driftwood.md` and
  `2026-09-23-driftwood-remaster.md`, `docs/HOW-DRIFTWOOD-GOT-BUILT.md`.
- **Pine Hollow.** A photoreal boreal forest from dawn fog to lantern
  night. A hunting sandbox (contracts, hides, four named elites)
  ending at the Antler King. Photoreal is the hardest look to
  one-shot.
  Source: SP `project/archive/2026-09-25-pine-hollow-remaster.md`
  (651 lines).
- **Nalati Grasslands.** A painterly Tian Shan steppe: taming and
  riding, kokpar, herds and wolf packs, three quest chains, and two
  bosses (the Golden King, and Jel Ata, Father of the Wind). It has
  the most design and the most mechanics, too many to one-shot, so
  the description has to choose.
  Sources: SP `docs/design/nalati/` (10 docs),
  `W/shard-nalati/src/data/questContent.json`.
- **Nine Dragon Stack.** A vertical neon city 500 m tall. What's built
  is a fragment: Lantern Square, a grapple course, the hoverboard.
  Nine strata, the Nine Red Envelopes quest and the Well Dragon are
  designed but not built. Its description would come from the unbuilt
  design, which suits the cube rule.
  Source: SP `docs/plans/NINE-DRAGON-STACK.md` (475 lines).
- **Sky Reach.** Eight islands floating over cloud. A war fan whose
  gust knocks foes off edges, hover bridges, and the Storm Roc. Small,
  silent, and already rebuilt clean-room once.
  Sources: SP `project/archive/2026-11-04-sky-reach.md`,
  `docs/design/far-reach/style-bible.md`.
- **Signal Dunes.** Dunes after sunset: a bullwhip, a caravan chain to
  a signal fire, and the Dune Matriarch with a sandstorm phase. The
  thinnest of the eight, but tidy.
  Sources: SP `project/archive/2026-11-04-signal-dunes.md`,
  `docs/design/sunscar-dunes/style-bible.md`.
- **Mossgate Hollow.** The SDK's teaching template: seven toon regions,
  the Lamplighter chain, two elites, and the Barrow Warden. It has no
  design doc. Its look-only clean room (2026-11-13) is lost.
  Sources: META `project/archive/MOSSGATE-ZONE-PLAN.md`,
  `W/sharddev/docs/plans/opus-2026-11-12-mossgate-v2.md`.
- **Brasscap Mesa.** A first-person sunset canyon: rifles, three bandit
  camps, and the Dust Wyrm. It is mostly the engine's test-bed (T1
  runs on it, J434) and has already gone shard, clean room, shard.
  Jake's 2026-11-16 voice note asks for a canyon clean room with a
  train and a tunnel.
  Sources: `W/shard-brasscap/src/rows/quests/quests.json`, META
  `project/archive/TEMPLATE-E2E-PLAN.md`.

### What this means for the descriptions

- **No zone is near the Showcase's bar.** None has levels to 20, a
  town, or a peaceful west and a combat east; each has one chain and
  one boss. So a description for any of them adds scope rather than
  recording what exists. Whether every zone gets the full MMO-zone
  shape is a decision for Jake (master plan, D2).
- **Distil from the design docs, not the code.** Content is spread
  across many JSON files, and most `src/README.md` files describe
  singleplayer-era folders that no longer exist.
- **Keep what made the Showcase prompt work:**
  - a description with no tech, plus a short brief;
  - the shard rules (the cube, the four road entrances);
  - "at least" lists rather than numbers;
  - the AAA bar;
  - one pass per slice and no loop;
  - a "done when" that names the boss on a phone.
- **Look direction is the open risk.** Jake liked Cratefall's quality
  but not its art direction. Each zone already has a look (Driftwood
  faceted, Pine photoreal, Nalati painterly, Nine Dragon neon), so
  each description should name its look in plain words.

### Cost and pacing

- **The Showcase:** the one-shot took about 2.5 hours. The AAA push
  that followed used up the Fable allowance (about $580, Jake).
- **Eight more:** one-shots only would be roughly 20 hours of Fable
  wall-clock [inferred from one run]. An AAA push on each is not
  affordable on the same allowance.
- **Old precedent:** J344 is Opus builds and Fable audits; the Showcase
  ran the other way round, Fable building with Opus helping.

## 6. Sources

- **This repo:**
  - A16 and A19;
  - `project/journal/2026-11-25-fable-one-shot-prompt.md`;
  - the commits `efa2105` to `34ba249`;
  - the Kitchen Sink plan and `kitchen-sink-v2/slices/IMPACT.md`;
  - `docs/GUIDE.md`.
- **The clean room:** `README.md`, `ZONE-DESCRIPTION.md`,
  `docs/AAA-PLAN.md`, `docs/media/`, and the session transcript
  `7aabdbae`.
- **META:**
  - `docs/plans/MULTI-REPO-SAGA/` (how a saga is laid out);
  - `docs/plans/parked/2026-11-22-fable-prototype-to-mmo-PLAN.md`;
  - `docs/prototype-to-mmo/STRATEGY.md`;
  - `docs/plans/parked/2026-11-11-opus-ps5-feel-PLAN.md` (PF16);
  - decisions J339, J341, J343, J344;
  - `project/archive/TEMPLATES-CLEANROOM-PLAN.md`.
- **W:**
  - shard-format `docs/`;
  - engine `docs/HOST-BAR.md` and `docs/design.md`;
  - the seven `shard-*` repos;
  - sharddev's Mossgate folder.
