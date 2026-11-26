# Cleanroom saga: a Fable MMO clean room of every zone, then the engine to take them

> Written by: Claude

> **State:** in progress, 2026-11-26. This is a saga master plan. As
> in meta (J446, J447) it holds no rows of its own: each member plan
> counts its own. Jake answered the open decisions in a grill
> (D30–D39 in `docs/decisions.md`). Building now:
> - the phase 1 starter packs and concept-art candidates;
> - the phase 2 format docs site.
>
> Ask: A19.

Research:
[support/cleanroom-research.md](support/cleanroom-research.md). It
covers the prompt, its history, why we used a clean room, the shard
file, the gap table and the eight zones. Grill log:
`project/brainstorms/2026-11-26-cleanroom-saga.md`.

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

One Fable session turned a 104-line zone description into Cratefall
in about 2.5 hours. The Kitchen Sink plan for the same zone is 87
slices and about 2,100 hours, none of them built (research §2–§3).

## Goal

There are two halves:

1. **Nine clean rooms.** Each zone is a playable Fable-built game made
   from a plain description and three approved concept images, played
   on a phone to its boss, audited, and shot as golden frames.
2. **An engine and format that take them.** Their content and
   mechanics come into Wildshard, server-authoritative and inside the
   phone budgets, one piece at a time. Each piece is built once for
   every zone that needs it.

**Done when** every zone plays in Wildshard on a phone at its clean
room's quality bar, with the camera rule (D35) and the mechanics its
clean room proved, in the zone's own art direction.

## How it runs (D31–D36)

- **Jake runs Fable.** Agents never spawn or prompt Fable. They make
  each zone's starter pack (D34), make concept candidates, audit the
  result and shoot golden frames.
- **One one-shot per zone** (D31), the Signal Dunes pilot first, then
  one at a time (D33).
- **The zone bar** (D32): levels 1–10 at least, a main quest ending
  in a boss, side quests, NPCs, elites, several weapons, and peaceful
  and combat content. Each is built around the zone's own identity.
- **The camera** (D35): third person; a drawn ranged weapon goes first
  person.
- **The look** (D36): each zone's own art direction, in words and in
  three approved concept images.

## Phases and member plans

| Phase | Member plan                            | State             |
|-------|----------------------------------------|-------------------|
| 0     | Showcase clean room and restyle        | in progress       |
| 1     | Eight zone clean rooms                 | in progress       |
| 2     | Shard format docs site and artifacts   | in progress       |
| 3     | Upload: the moved meta plans, then one | moved, parked     |
|       | plan per piece                         |                   |

- **Phase 0:**
  [2026-11-26-opus-showcase-cleanroom-PLAN.md](2026-11-26-opus-showcase-cleanroom-PLAN.md).
  The rows:
  - CR1: quality frames;
  - CR2: mix and match the design;
  - CR3: wire it into the Kitchen Sink;
  - CR4: Brasswick concept art in the Kitchen Sink style;
  - CR5: the restyle brief for Jake's Fable session.
- **Phase 1:**
  [2026-11-26-opus-zone-cleanrooms-PLAN.md](2026-11-26-opus-zone-cleanrooms-PLAN.md).
  Starter packs, concept candidates, then each zone's one-shot, audit
  and golden frames.
- **Phase 2:** the docs site lives in the shard-format repo, under its
  own commits (D37). Explainer artifacts for Jake are published from
  this saga. Plan row: ZC-F in the phase 1 plan tracks the link back.
- **Phase 3:** the five meta plans moved in (D38). How mechanics get
  in, a host each or primitives, is decided after phase 2:
  - [PROTOTYPE-TO-MMO](2026-11-22-fable-prototype-to-mmo-PLAN.md):
    primitives and the upload loop;
  - [PS5-feel](2026-11-11-opus-ps5-feel-PLAN.md): look, feel, 60 fps,
    PF16 third-person;
  - [WASM-HOST](2026-10-20-opus-wasm-host-PLAN.md): the script host;
  - [HOST-AUDIT](2026-10-22-opus-host-audit-PLAN.md): one-shard
    hosts;
  - [RPG lessons](2026-11-24-opus-procedural-rpg-lessons-PLAN.md):
    the procedural RPG; small, fun, code-drawn.

  Each keeps its own State (draft or parked). The per-piece plans
  below get written when phase 2 is done.

### The pieces (phase 3)

The "Zones" column comes from the shard survey (research §5) plus
the Showcase. Phase 1 will add to it. "Drift" is Driftwood and "ND"
is Nine Dragon.

| Piece                                 | Cost  | Zones               |
|---------------------------------------|-------|---------------------|
| World, geometry, surfaces, light      | $–$$  | all                 |
| Third-person camera, body, animation  | $$$   | all (D35)           |
| Combat engine: strings, dodge, skills | $$$   | all with combat     |
| Weapons and the shooter stance        | $–$$  | all (D35)           |
| Enemies, AI, enemy types              | $$    | all (D32)           |
| Elites and phased bosses              | $$$   | all (D32)           |
| Riding and taming                     | $$    | Showcase, Nalati    |
| Hoverboard, skate park, grind         | $–$$  | Showcase, Drift, ND |
| Movers, zipline, grapple, bridges     | $–$$  | most                |
| Swimming, boats                       | $$    | Drift, Nalati, Pine |
| Quests, quest boards, dialogue        | $–$$  | all (D32)           |
| Progression: levels, perks, gear      | $$$   | all (D32)           |
| HUD: portrait, landscape, desktop     | $$    | all                 |
| Audio                                 | $–$$$ | all                 |
| Weather, day, interiors, cutscenes    | $–$$  | most                |
| Phone budgets                         | $$    | all                 |

## Seams

- **The Kitchen Sink**
  ([plan](../2026-10-20-opus-kitchen-sink-PLAN.md)) stays the
  Showcase's build plan. Its look target becomes the new Showcase
  concept art, painted in its own style (D36). Phase 3 reuses its
  slices, and CR2 decides which side's design wins, item by item.
- **Meta:** the five plans moved here on 2026-11-26. Each left a
  pointer at its old path (D38).
- **shard-format:** the phase 2 docs site lives there, under its own
  commits.
- **The clean-room repos:** one per zone under `~/projects/game-demos/`,
  each its own game. Jake owns the Fable sessions, GitHub and Pages
  (D34).
- **Other agents:** `t14` is archiving the SDK plan (A17). Work is on
  `main` only (D29).

## Verification

- **Phase 1:** each clean room is checked by a phone playthrough to its
  boss, an audit against D32, and golden frames (D33).
- **Phase 2:** checked by the live site at `format.wildshard.io` and
  Jake reading the artifacts.
- **Phase 3:** each piece is checked by a zone that uses it playing on
  staging, on a phone, with two players, against its golden frames.

## Sync

- `docs/decisions.md`: D30–D39, written 2026-11-26.
- `docs/prd.md`: none. The PRD covers the Showcase, and this saga
  spans every zone.
- `AGENTS.md`: none. The Fable rule is D34.
