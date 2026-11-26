# Cleanroom saga: a Fable MMO clean room of every zone, then the engine to take them

> Written by: Claude

> **State:** ready for review, 2026-11-26. This is a saga master plan.
> As in meta (J446, J447) it holds no rows of its own: each member plan
> counts its own. Only the phase 0 plan is written; the other member
> plans get written as their phase comes up. Ask: A19.

Research:
[support/cleanroom-research.md](support/cleanroom-research.md). It
covers the prompt, its history, why we used a clean room, the
shard file, the gap table and the eight zones.

## Why

Jake, 2026-11-26 (A19): *"how can we make a fable 5.2 mmo cleanroom
of our 8 zones + shard showcase zone … This is going to become a saga
lol, this is going to be a mountain of work lol."* He asked for:

- **A new saga after the multi-repo one,** living in this repo for now.
  Meta's MULTI-REPO-SAGA closed on 2026-11-25 (J514).
- **Clean rooms of the other eight zones:** Driftwood, Pine Hollow,
  Nalati, Nine Dragon, Sky Reach, Signal Dunes, Mossgate and
  Brasscap.
- **An explanation of what a shard file and the shard format even
  are.**
- **A piece-by-piece path to uploading all nine clean rooms into
  Wildshard,** across the engine, the shard format and sharddev: the
  world and geometry, a new combat engine, weapons, enemies and enemy
  types, the features (horse riding, hoverboard, movers, skate park,
  quests, quest boards), the HUD, the third-person camera, *"etc etc
  etc"*.

**What one clean room showed.** One Fable session turned a 104-line
zone description into Cratefall in about 2.5 hours, and the AAA push
after it took the Fable allowance to 100%. The Kitchen Sink plan for
the same zone is 87 slices and about 2,100 hours, none of them built.
Jake liked the quality and the third-person hero, kept Cratefall as
its own game, and wants the engine to go third person (research §2).

**It continues an idea of Jake's.** On 2026-11-16 he described the
author loop as an hour to vibe-code a clean room, then an hour to
"upload this to the MMO". He wanted that as *"a brand new saga"*
(META `docs/plans/parked/2026-11-22-fable-prototype-to-mmo-PLAN.md`).

## Goal

There are two halves:

1. **Nine clean rooms.** Each zone is a playable Fable-built game made
   from a plain description, deployed, audited, and shot as golden
   frames.
2. **An engine and format that take them.** Their content and
   mechanics come into Wildshard, server-authoritative and inside the
   phone budgets, one piece at a time. Each piece is built once for
   every zone that needs it.

**Done when** every zone plays in Wildshard on a phone at its clean
room's quality bar, with the camera, combat and features its clean
room proved, in the zone's own art direction.

## Phases and member plans

| Phase | Member plan                          | State             |
|-------|--------------------------------------|-------------------|
| 0     | Showcase clean room as the target    | ready for review  |
| 1     | Eight zone clean rooms               | not written       |
| 2     | What a shard file is                 | not written       |
| 3     | Upload, one plan per piece           | not written       |

- **Phase 0, the Showcase:**
  [2026-11-26-opus-showcase-cleanroom-PLAN.md](2026-11-26-opus-showcase-cleanroom-PLAN.md).
  Cratefall is built and live. Rows CR1–CR3 pick the quality frames,
  mix and match its design with the Kitchen Sink's, and wire it into
  that plan.
- **Phase 1, eight clean rooms.** For each zone:
  - **Description.** Opus writes a `ZONE-DESCRIPTION.md` from the
    sources in research §5, in the Showcase's shape: no tech, the
    cube and road rules, "at least" lists, the zone's own look in
    plain words, and the boss as "done when". Jake reviews it.
  - **One-shot.** Fable runs the brief in a new empty repo,
    `~/projects/game-demos/<zone>-clean-room`, deployed to GitHub
    Pages.
  - **Audit.** Requirements met, a phone check, and golden frames.

  A pilot zone runs first, so the recipe is proved again before the
  other seven.
- **Phase 2, the shard file explained.** A living doc in `docs/`. It
  explains the shard file, the format, sections, hosts, scripts and
  server authority, using this repo's built `out/` as the worked
  example. It fixes or flags stale specs (shard-format `SHARDFILE.md`
  says `0.1.0.2`; the code says `0.1.0.6`) and re-counts the hosts
  that serve only one shard (the PTM2 refresh). Phase 3 builds on it.
- **Phase 3, upload piece by piece.** One member plan per piece. Each
  names the zones that need the piece, the layer it lands in
  (format, engine client, engine server, sdk or data), and the Kitchen
  Sink slices it reuses. The cost of each is in the research §4 table.

### The pieces

The "Zones" column comes from the shard survey (research §5) plus
the Showcase. Phase 1 will add to it. "Drift" is Driftwood and "ND"
is Nine Dragon.

| Piece                                 | Cost  | Zones               |
|---------------------------------------|-------|---------------------|
| World, geometry, surfaces, light      | $–$$  | all                 |
| Third-person camera, body, animation  | $$$   | all (Jake)          |
| Combat engine: strings, dodge, skills | $$$   | all with combat     |
| Weapons and the shooter stance        | $–$$  | all; Brasscap guns  |
| Enemies, AI, enemy types              | $$    | all but Nine Dragon |
| Elites and phased bosses              | $$$   | all                 |
| Riding and taming                     | $$    | Showcase, Nalati    |
| Hoverboard, skate park, grind         | $–$$  | Showcase, Drift, ND |
| Movers, zipline, grapple, bridges     | $–$$  | most                |
| Swimming, boats                       | $$    | Drift, Nalati, Pine |
| Quests, quest boards, dialogue        | $–$$  | all                 |
| Progression: levels, perks, gear      | $$$   | Showcase, (D2)      |
| HUD: portrait, landscape, desktop     | $$    | all                 |
| Audio                                 | $–$$$ | all                 |
| Weather, day, interiors, cutscenes    | $–$$  | most                |
| Phone budgets                         | $$    | all                 |

"(Jake)" marks his call that the engine goes third person. "(D2)"
means it depends on decision D2 below.

## Seams

- **The Kitchen Sink**
  ([plan](../2026-10-20-opus-kitchen-sink-PLAN.md)) stays the
  Showcase's build plan. Phase 3 reuses its slices rather than
  replacing them, and phase 0's CR2 decides which side's design wins,
  item by item. Its paths still need re-baselining (MR1 in its
  STATE.md).
- **Meta's parked plans:** PROTOTYPE-TO-MMO (primitives instead of a
  host per mechanic) and PS5-feel PF16 (a third-person spring arm).
  Phase 3 would build what they describe (decision D5).
- **The engine, shard-format and sharddev:** phase 3 code lands in
  those repos under their own plans. This saga only links to them.
- **The clean-room repos:** one per zone under `~/projects/game-demos/`.
  Each is its own game, read only from here (Jake: *"keep cratefall
  free as its own standalone game"*).
- **Other agents:** `t14` is archiving the SDK plan (A17). Work is on
  `main` only (D29).

## Verification

- **Phase 1:** each clean room is checked by its deploy, its audit,
  and a phone playthrough to the boss.
- **Phase 3:** each piece is checked by a zone that uses it playing on
  staging, on a phone, with two players, against its golden frames.
  The member plans name their own tests.

## Sync

- `docs/prd.md`: none yet. The PRD covers the Showcase, and this saga
  spans every zone. If the saga moves to meta, it goes with it.
- `docs/`: phase 2 adds the shard-file doc.
- `docs/decisions.md`: Jake's answers to D1–D6 go there.
- `AGENTS.md`: none.

## Open decisions for Jake

1. **D1, the Fable budget per zone.** A one-shot only (about 2.5 h
   each), with an AAA push just for the zones you pick? Recommend
   yes: one Showcase push used the whole allowance.
2. **D2, scope.** Does each zone get the full MMO-zone shape (town,
   levels 1–20, dungeon, raid boss), or its own size with its own
   boss? Recommend the full shape around each zone's identity, since
   the point is the MMO bar. Nalati's description has to choose
   between its three chains.
3. **D3, the pilot.** Recommend Signal Dunes: thin, tidy, a style
   bible, and already rebuilt clean-room once. Brasscap is the
   alternative if you want your canyon train first.
4. **D4, who builds.** Fable builds and Opus helps, as the Showcase
   did, or J344's Opus builds and Fable audits? Recommend Fable
   builds, the recipe that just worked.
5. **D5, how phase 3 works.** A new host per mechanic, as today, or
   PROTOTYPE-TO-MMO's primitives and shared AssemblyScript? Recommend
   folding that parked plan into this saga as phase 3's approach.
6. **D6, art direction.** Each description names its zone's own look
   in plain words, so the clean room takes Cratefall's quality and
   not its style. Recommend yes.
