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
