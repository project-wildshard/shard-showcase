# Mini plan: a clean-room one-shot as the target (CR)

> Written by: Claude

> **State:** ready for review, 2026-11-26: Jake's picks are in
> (below); the rows hold until he says go. Ask: A18 (the prompt itself
> was A16).

Parent: [KITCHEN-SINK.md](../KITCHEN-SINK.md). Surveyed 2026-11-26
against this repo at `a601dfb` and the clean room
(`~/projects/game-demos/showcase-zone-clean-room`) at `3afcd88`.

## Why

Jake, 2026-11-26 (A18): *"a mini plan talking about how we prompted a
cleanroom one shot as a target for this zone / shard"*.

The Kitchen Sink is about 2,100 hours of slices, and nothing is built
yet. On 2026-11-25 we gave one Fable session a short prompt in an
empty repo instead. That session produced a playable game of the same
zone, Cratefall, live at
<https://raynos.github.io/showcase-zone-clean-room/>. This plan
records how we prompted it and turns the result into a target the
shard is measured against. We already have mockups, but Cratefall is
a game made from the same spec that people can actually play.

Jake on what Cratefall is, said in the clean-room session
(2026-11-25):

- *"Shard showcase and shard kitchen sink are two different names for
  the same thing. ZONE-DESCRIPTION is basically the simple version of
  the kitchen sink plan."*
- *"Let's keep cratefall free as its own standalone game, but also
  let's start steering it towards experiments i value."*
- *"i really like the third person hero so i think i'm going to make
  the engine third person … Dodge roll is fun, status effects we can
  figure out. Names dont matter."*

## How we prompted it (the record)

All of this is in A16 and in
`project/journal/2026-11-25-fable-one-shot-prompt.md`. Commits
`efa2105` to `34ba249` show the prompt text at each step.

1. **Distil, then cut.** It started as about 150 lines distilled from
   §1–§3 of this plan, the locked maths and UI-PICKS. Jake: *"the less
   you poison / steer / context rot it the better … The more vague we
   are the more fable will just make something magical & amazing."*
   It was cut to about 60 lines, then grew back to about 100 by his
   picks: the west places, the robot roster, the set pieces, the quest
   hooks and the six-band shape.
2. **Two files.** `ZONE-DESCRIPTION.md` describes the game with no
   tech. It keeps the shard rules: the 500 m cube, four road entrances,
   peaceful west, combat east, the Vault and the Crate Titan.
   `FABLE-PROMPT.md` is the brief. It opens on the AAA bar (*"plays
   like a AAA PS5 MMORPG"*, *"a big wow impact"*), sets mobile first in
   portrait and TypeScript + three.js, and says done means beating the
   Titan on a phone.
3. **Clean room.** The builder never sees Wildshard, sharddev, the
   shard format or the engine. Both files were moved into an empty repo
   with nothing that names Wildshard. The brief is that repo's
   `README.md`, and `ZONE-DESCRIPTION.md` matches our last version
   byte for byte.
4. **One pass per slice, no loop.** The brief tells it to build a
   slice, play it at phone size, judge it harshly against a shipped
   PS5 game, fix what falls short, then move on. Jake: *"we just dont
   want to prompt it for 'loop' and 'dont stop'"*, because *"fable
   will guzzle all the tokens"*.

**What it cost and made** (clean-room session `7aabdbae`, commit
times, and the clean room's `docs/AAA-PLAN.md`):

- **The one-shot:** from 02:48 (brief pasted) to 05:16 (`81c7fdd`),
  39 commits, with five subagents in parallel. An audit counted 71 of
  78 description requirements done, 7 partial and none missing. It ran
  at 60 fps on desktop and *"reads as a responsive, well-instrumented
  prototype"*, not yet a console game.
- **The AAA push:** the same session ran on to `3afcd88` (368 commits,
  63k lines). It used up the Fable allowance (Jake: *"100% of the
  fable ( 580$ cost )"*) and then switched to Opus subagents with at
  most two Fable.
- **What it left behind:** 25 golden frames (start, now and painted
  target), a media library (`docs/media/`, 182 stills and 18 clips), a
  trailer, and a state page. None of it has been checked on a real
  phone.

## Rows

Each row is one lane. The clean room is read only from here: Cratefall
stays its own game (Jake), so no row writes there.

**Mix and match** (Jake, 2026-11-26): *"we are going to mix & match
the look, we are going to mix & match the design, some of the
original kitchen sink design needs to come back, some of the
cratefall design will overwrite."* On the look: *"I appreciate and
like the 'quality of the work' but not the art direction"*. That means
Cratefall's geometry, world detail, assets and density are the target,
and its art direction, concept art, neon lights and parts of its
palette and style are not.

- [ ] **CR1 Pick the quality targets.** From Cratefall's 25 golden
  frames (`docs/media/golden/README.md`; each has a scripted camera
  in `tools/golden/scenes.js`) and its zone stills, choose the ones
  whose place exists in this plan's map (town square, Crate Fields,
  the Vault, the Titan arena, …). Write `cleanroom-targets.md` beside
  this file with one row per frame:
  - the source path in the clean room (the latest build; Jake: *"its
    not going to drift"*);
  - the place, and the matching spot (P, facing f) on round 5 of the
    map layout;
  - what the frame is the bar for (geometry, detail, density, light),
    and what in it is not (neon, palette, style), so a look loop
    doesn't copy Cratefall's art direction.

  Copy the most important frames into `cleanroom-targets/` beside it.
  Link the rest. The shard's own art direction (the polished
  orange-and-grey look, ruling 19ab, the round-11 remaster mockups)
  stays the style target. Done when every chosen frame has a spot and
  a quality-versus-style note, frames with no place in the map are
  listed as dropped with a reason, and Jake has approved the list.
- [ ] **CR2 Mix and match the design.** Read Cratefall's state page,
  `docs/AAA-PLAN.md`, `docs/COMBAT.md` and `docs/HUD.md` against §2 of
  this plan and its mini plans. List each place where the two differ:
  what Fable invented (dodge roll, third person with first-person aim
  for ranged weapons, Overdrive, the Tally Book, simulated adventurers
  and zone chat, …) and what the plan has that Cratefall dropped or
  solved differently. Each line gets one of three calls:
  - **Cratefall overwrites:** the plan changes to match.
  - **Kitchen Sink comes back:** the plan's design stays.
  - **Ask:** it becomes a row in [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md)
    with a recommendation.

  The calls Jake has already made are recorded as decided: third
  person, the dodge roll, names don't matter, and status effects are
  still to settle. Done when the list is in this file and every ask is
  in OPEN-QUESTIONS.
- [ ] **CR3 Wire it into the parent.** Add a row for this plan to
  KITCHEN-SINK.md §5. Add Cratefall live and its state page to §6. Add
  one line to STATE.md: the shard's quality bar is the CR1 frames, and
  its style stays its own. Done when the three links resolve.

## Seams

- **Owns:** this file, `cleanroom-targets.md` and `cleanroom-targets/`.
  It edits one row in KITCHEN-SINK.md §5 and §6, one line in STATE.md,
  and appends rows to OPEN-QUESTIONS.md.
- **Other agents:** `t14` is working on plan archiving on `main`.
  That touches `docs/plans/` but not the Kitchen Sink files. Work is on
  `main` only (D29).
- **Clean room:** a separate repo with its own session. It is read
  only from here.

## Verification

This is a docs plan, so there is nothing to run yet. CR1's list is
checked when the look loop builds its first board: each chosen frame
must load beside a capture from the shard at its spot. CR2 is checked
by `pnpm check` (the asks and plan gates) and by Jake reading the list.

## Sync

- `docs/prd.md`: none, because it already points at the Kitchen Sink.
  A target is a tool for that plan, not a new product.
- Living docs: KITCHEN-SINK.md and STATE.md, in CR3.
- `docs/decisions.md`: none. CR2 changes go into the plan and its
  OPEN-QUESTIONS.
- `AGENTS.md`: none.

## Decided (Jake, 2026-11-26)

1. **Target for what:** both the look and the design, mixed and
   matched. Take the quality of the look, not its art direction.
2. **Which Cratefall:** the latest build.
3. **Media:** link it, and copy the important frames.
4. **Build:** hold. Rows wait for Jake's go.
