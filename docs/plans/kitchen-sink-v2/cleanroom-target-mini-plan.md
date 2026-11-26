# Mini plan: a clean-room one-shot as the target (CR)

> Written by: Claude

> **State:** ready for review, 2026-11-26. Ask: A18 (the prompt
> itself was A16). Nothing here is built until Jake says go.

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

- [ ] **CR1 Pick the target frames.** From Cratefall's 25 golden frames
  (`docs/media/golden/README.md`; each has a scripted camera in
  `tools/golden/scenes.js`), choose the ones whose place exists in
  this plan's map (town square, Crate Fields, the Vault, the Titan
  arena, …). Write `cleanroom-targets.md` beside this file with one
  row per frame: the source path at a pinned SHA, the place, and the
  matching spot (P, facing f) on round 5 of the map layout. Done when
  every chosen frame has a spot, frames with no place in the map are
  listed as dropped with a reason, and Jake has approved the list.
- [ ] **CR2 Compare the design.** Read Cratefall's state page,
  `docs/AAA-PLAN.md`, `docs/COMBAT.md` and `docs/HUD.md` against
  §2 of this plan and its mini plans. List what Fable invented that
  the plan lacks (dodge roll, third person with first-person aim for
  ranged weapons, Overdrive, the Tally Book, simulated adventurers and
  zone chat, …). Also list what the plan has that Cratefall dropped or
  solved differently. Each line gets adopt, leave or ask, and each ask
  becomes a row in [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) with a
  recommendation. Done when the list is in this file and every ask is
  in OPEN-QUESTIONS. The calls Jake has already made (above) are
  recorded as decided, not asked again.
- [ ] **CR3 Wire it into the parent.** Add a row for this plan to
  KITCHEN-SINK.md §5. Add Cratefall live and its state page to §6. Add
  one line to STATE.md saying the shard's look is measured against the
  CR1 frames. Done when the three links resolve.

## Seams

- **Owns:** this file and `cleanroom-targets.md`. It edits one row in
  KITCHEN-SINK.md §5 and §6, one line in STATE.md, and appends rows to
  OPEN-QUESTIONS.md.
- **Other agents:** `t14` is working on plan archiving on `main`.
  That touches `docs/plans/` but not the Kitchen Sink files. Work is on
  `main` only (D29).
- **Clean room:** a separate repo with its own session. Cite it by SHA
  so the targets don't drift when it moves on.

## Verification

This is a docs plan, so there is nothing to run yet. CR1's list is
checked when the look loop builds its first board: each chosen frame
must load beside a capture from the shard at its spot. CR2 is checked
by `pnpm check` (the asks and plan gates) and by Jake reading the list.

## Sync

- `docs/prd.md`: none, because it already points at the Kitchen Sink.
  A target is a tool for that plan, not a new product.
- Living docs: KITCHEN-SINK.md and STATE.md, in CR3.
- `docs/decisions.md`: none until Jake answers the questions below.
- `AGENTS.md`: none.

## Open decisions for Jake

1. **Target for what?** The look (CR1), the design (CR2), or both.
   Recommend both, starting with the look.
2. **Which Cratefall?** The one-shot at `81c7fdd`, or the latest
   build, pinned per round. Recommend the latest build: the one-shot
   is the baseline, and the AAA push and its painted targets are what
   we would want the shard to match.
3. **Copy the media here, or link it?** Recommend linking by SHA.
   Cratefall's `docs/media` is 97 MB and this repo stays lean.
