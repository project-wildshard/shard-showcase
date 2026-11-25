# A clean-room prompt for a Fable one-shot of the Kitchen Sink

Ask A16.

- Jake wants to see what one Fable session makes of the plan before anyone renovates, audits or
  moves it forward. So the plan itself is untouched; the prompt sits in `docs/prompts/`.
- Clean room means the builder never sees our engine, so the prompt can't point at the plan: it is full
  of hosts, shardfiles, slices and singleplayer paths that would only confuse. Instead it distils the
  game design: §1–§3 (halves, town, west toys, bands, Vault, gauntlet, Titan arena), the locked combat
  maths from levels-combat §15, the roster, quests/economy, and the HUD rules from UI-PICKS.
- Kept the golden-ratio XP curve as designed (it is a ~60 h grind) and gave the build a dev menu (set
  level, XP ×10, teleport, time, storm) so "done" can be checked without the grind.
- First person, because the game is (the mockups' figure is only for scale). Art and audio are made in
  code (three.js geometry, WebAudio), no downloads, so the orchestral score becomes procedural music.

## Split in two

Jake: "let's split this into two files." ZONE-DESCRIPTION.md is the game alone (look, map, combat,
enemies, quests, HUD, audio) with no tech, so it can feed other builds too; FABLE-PROMPT.md is the
short brief (stack, clean room, phone, tests, dev menu, done-when) that tells Fable to read it. The
description is copied into the empty directory before the paste. Audio's "WebAudio only" moved to
the brief, since that is tech.

## Vaguer, standalone

Jake: "the less you poison / steer / context rot it the better … The more vague we are the more fable
will just make something magical & amazing." The description went from ~150 lines of distilled plan
to ~60: no links or provenance (it is copied bare), no camera choice, no maths, no roster names, no
HUD layout. What stays is the shape (500 m, peaceful west, combat east, levels 1–20, dungeon, gauntlet,
boss portal), the look, "at least these" weapons and enemy kinds, and the Crate Titan, the one name
settled since v1. The provenance now lives only here: KITCHEN-SINK.md §1–§3 as of 2026-11-25.

## Some detail back

Jake: "you might have gone overboard … we do want to add some detail back in lol". He picked from a
list rather than me guessing: the west places by name, the robot roster, the set pieces (Vault rooms,
gauntlet courts, Titan portal, storm hour), the quest/economy hooks and the six-band level shape.
Combat feel and the HUD stay vague, so Fable invents those. ~95 lines, still no numbers or formulas.

## The cube and the roads

Jake: "we designed a bunch of shit and we don't want to lose" it: the mini dungeon, the raid-style
boss, ruling 19ad's 500 m cube (interiors by portal, but physically inside the cube, never
overlapping) and the zone staying a valid shard, 500 × 500 m with a road entrance mid-edge on all
four sides. The description says it is one zone of a grid joined by roads, so Fable knows why the
limits exist, and that the roads may just lead off the edge, so it doesn't build the neighbours.

## The brief, cut too

Jake: "the PROMPT.md is also too leading". The brief is now four lines under the paste mark:
TypeScript + three.js, single-player, mobile first in portrait, done at the Crate Titan on a phone.
Gone: git, pnpm, Vitest, the asset ban, the enemy cap, the dev menu. The clean-room note (no
Wildshard repo, sharddev or engine) stays above the paste mark, for whoever runs it, so Fable never
hears those names.

## The AAA bar

Jake: "far more aggressive on the AAA nature", in his words "plays like a AAA PS5 MMORPG" and "a big
wow impact". The brief opens on his two lines, adds feel and a living world, and keeps mobile first,
now "still look stunning there". "A gauntlet loop light vibe" I read as a light self-review loop: build
a slice, play it, screenshot at phone size, judge it against a shipped PS5 game, fix the weakest
thing, repeat. Done-when now includes "looks and feels AAA the whole way".

Then, Jake: "I Dont think we can afford to prompt it to work in a loop". The play / screenshot / judge
loop is gone; the AAA bar stays in the bullets and the done-when.
Jake, a moment later: "fable will guzzle all the tokens", but "we do want to tell it to build a slice
play it and judge it harsley … we just dont want to prompt it for 'loop' and 'dont stop'". So one pass
per slice: play it, judge it against a shipped PS5 game, fix what falls short, then the next slice. No
"loop", no "again", no "don't stop", so nothing invites open-ended polishing.
Jake: "Rename it from 'kitchen sink' to 'showcase MMO zone' … remove all references to 'kitchen sink'".
Done for both prompt files (only their titles had it). The plan, its folder, this journal and the ask
keep the old name: they are the plan and the history, not what Fable reads.

## Moved to the clean room

Jake: "move the files when done to ~/projects/game-demos/showcase-zone-clean-room", an empty git repo
outside this one. Both files went there and left docs/prompts/. FABLE-PROMPT.md lost its how-to header
on the way (it named Wildshard, sharddev and ask A16), so the clean room holds only what Fable should
see. I didn't commit in that repo; that's Jake's to start. Their history up to the move is in this
repo's log for docs/prompts/.
