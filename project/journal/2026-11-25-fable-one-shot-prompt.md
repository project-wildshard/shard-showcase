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
