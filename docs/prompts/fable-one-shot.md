# Fable one-shot: the Kitchen Sink zone, clean room

Ask A16. Paste everything below the line into a fresh Fable session in
an empty directory. It is self-contained on purpose: the builder never
sees a Wildshard repo, sharddev, the shard format or the engine. It is
distilled from [KITCHEN-SINK.md](../plans/KITCHEN-SINK.md) §1–§3 and
levels-combat §15 as of 2026-11-25.

---

Build a complete, playable, single-player game in one go: **the Kitchen
Sink**, one hand-made MMO zone that you play alone. It should feel like
logging into an MMO when nobody else is online: a town with quest
givers and shops, level bands of enemies, elites, a mini dungeon and a
raid-style final boss, all in a single 500 × 500 m area.

## Ground rules

- A new git repo in this directory. TypeScript (strict) + three.js +
  Vite, pnpm. Commit as you go with clear messages.
- Clean room: no game engine, no server, no multiplayer, no accounts.
  Everything runs in the browser; save to localStorage.
- No downloaded art or audio. Build models from three.js geometry in
  code, sounds and music from WebAudio.
- First-person camera.
- **Mobile first.** It must run smoothly on an iPhone in **portrait**,
  with touch controls. Desktop (WASD, mouse, click) works too. Cap the
  pixel ratio, use instancing, and give full AI to at most 16 enemies
  within 60 m; enemies further away idle cheaply.
- Unit-test the combat and level maths (Vitest). `pnpm build` and
  `pnpm test` must pass.
- A dev menu (behind a small gear icon): set your level, XP ×10,
  teleport to any zone, set the time of day, start a storm.

## Look

A simple, polished, playful stylised look: a warm orange and cool grey
workshop/test-yard palette with cyan accents. Finished materials,
characterful robots, soft lighting and shadows, sky, fog, day/night.
Never placeholder: no grid floors, no stencilled size labels, no plain
grey blocks.

## The map (500 × 500 m, ground plus two hidden interiors)

The **west half is non-combat**: no enemies, no XP, no money. It has:

- **Town** (~120 m walled square): a gate plaza, a main street, six
  NPCs (three quest givers for levels 1–6, 7–12 and 13–20; Tinker Rook
  for upgrades; a weapons-shop keeper; a stable hand), a kill-contract
  board and a trophy wall. Its east gate is the only way into combat.
- Weapon range (dummies, bow/crossbow lanes 10–50 m, rifle to 75 m).
- Physics yard: three pressure plates open a gate; crates, see-saws, a
  ball run.
- Riding course with a loaner horse: 8 rings, 4 jumps, a lap timer.
- Movers run (moving platforms, lifts, conveyors).
- Grapple course (5 hooks) and a ~100 m zipline into town.
- Climb yard: a scramble wall, ladders, swaying rope bridges.
- "The Rock": a 16 m crag with a squeeze cave and a lookout bench.
- Hoverboard park: kickers, a halfpipe, rails, a bowl, a trick score.
- Each toy keeps a personal best on a real sign board. Six vistas,
  four hidden caches and 20 "Gold 1×1" collectibles across the map.

The **east half is combat only**:

- **NE**: bands L1–3, 4–6, 7–9 and 10–12 in a 2 × 2 grid.
- **SE top**: band L13–15 (a stealth yard: an eye/UNSEEN indicator)
  and band L16–18.
- **SE bottom**: the gauntlet (three sealed courts, five waves) and the
  Titan gate, a plaza with an 18 m portal arch.
- **Training Vault** (portal in band 10–12, interior at y −40): four
  rooms (a puzzle, a fight, a climb, the Vault Warden). Dying restarts
  that room; solved puzzles stay solved.
- **Titan arena** (behind the portal, interior at y −150): a ⌀104 m
  floor for the 15 m Crate Titan.

## Levels and combat

- Levels 1–20. XP comes only from kills: 10 × enemy level, less for
  enemies below you, 0 at 6 below ("grey" kills pay nothing). The XP
  curve grows by the golden ratio (×1.618) per level.
- Death costs 25 % of this level's XP and never delevels. You respawn
  at the last checkpoint you reached.
- Seven attributes grow automatically on level-up, like Fire Emblem:
  no points, no respec. VIT = max HP (100 → 600), STR = melee damage,
  DEX = ranged damage and hit chance, AGI = dodge, DEF = armour, MDEF =
  energy resistance, LUK = crit size and lucky saves. Each new save
  rolls aptitudes: two at ×1.2, three at ×1.0, two at ×0.8, shuffled.
  A gain is round(step × aptitude × random 0.4–1.6).
- Attacks can fail. The fail chance is 12 % at equal level, +9.75 % per
  level the target is above you, capped at 90 %. A fail shows as
  DEFLECT (sparks, clang), DODGE or PARRY. MISS is only for aim misses.
  Odds are never shown as a %.
- Damage = weapon × forge tier × ATK × K / (K + DEF). Crits are 10 %
  base, capped at 40 %, size ×(1.5 + LUK/100). Glances do half damage
  against higher-level targets.
- Parry: block within 0.15 s of a hit landing to take no damage and
  crit on your next swing. Stagger bars fill from hits (STR fills them
  faster); a full bar stuns for 1.5 s.
- No heals in a fight, no potions. Regen starts 5 s after combat and
  fills you in 12 s. A level-up refills HP.
- Pacing at equal level: a common dies in ~7 sword swings and kills you
  in ~11 hits. Elites have 7× a common's HP; the Titan 22×.
- Weapons (bought in the weapons shop, level-locked): sword (combo and
  parry), spear, bow, crossbow (iron, pitch and broadhead ammo) and a
  lever rifle. Forge I–IV upgrades raise every weapon at once.

## Enemies (robots)

- Commons: Crate Mite L1–3, Pallet Jack L4–6, Plumb Drone L7–9,
  Welder Unit L10–12, Riveter L13–15, Arc Sentry L16–18.
- Packs respawn ~90 s after you leave, never in view. Enemies leash
  home and reset. Rare variants spawn now and then (+1 or +2 levels, a
  new look, better drops).
- Night shift: at night each band's enemy swaps to a tougher variant
  (+1 level).
- Elites: Big Pallet L6, the Vault Warden L12, Foreman Unit 7 L18.
  Night elites: Sir Nibbles L4, Hot Mess L13, Riveting Rita L16.
- Final boss: the Crate Titan, L20, 15 m tall, three phases (slam
  rings, rolling crate lanes, crate rain with Crate Mite adds). It has
  a skippable in-engine intro the first time and drops the legendary
  Titan Cleaver sword. Its portal opens after your first gauntlet clear.
- Robots chirp; they never speak.

## Quests and economy

- 12 quests, four per tier, from the three tier givers: kill + collect,
  explore + elite hunt, set pieces. Givers show a grey "!" when you are
  too low and a yellow "!" when you can take the quest. A locked quest
  says NEEDS LV n once, with one OK button.
- One quest triggers storm hour: the whole map turns to an evening
  storm until you light four beacons. Storms count as night. A day is
  20 min of day + 4 min of night.
- The currency is Scrip. Every kill also drops one salvage part for its
  robot type. Tinker Rook sells one-off UPGRADES and has a BENCH that
  turns parts into ammo. The kill-contract board pays Scrip plus a
  trophy and a joke title the first time. 20-slot pack, chests, crates.
- Beating the Titan shows a "zone complete" card.

## Portrait HUD (calm, nothing permanent and busy)

- **Top**: the minimap with one chip under it: the tracked quest, or the
  running activity (course clock, vault room, trick score).
- **Bottom**: a thin XP bar with an "LV n" chip on its left, above the
  controls.
- **Controls**: a left-thumb move stick and right-side drag to look.
  ATTACK, plus a fight row of GUARD · LOCK · DODGE · JUMP. Tap the
  weapon chip to slide out three ammo tiles.
- **Nameplates** within 25 m: "Lv 7 Plumb Drone", an HP bar, a stagger
  bar, and con colours (grey, green, yellow, orange, red, skull).
- **Floating numbers**: white hits, big yellow crits, small grey
  glances, DEFLECT / DODGE / PARRY words; at most 6 on screen.
- **Level-up never blocks a fight**: in combat you get a ring, a sting
  and a one-line chip ("LEVEL 7 · +11 VIT"). The tick-up card, with each
  attribute gain in turn, waits until you are out of combat.
- **Other cards**: elite banner, boss bar with phases, a death card
  with the XP line, checkpoint card, boss title card with HOLD TO SKIP.
  Toasts are one short line. Big moments get a centred line that fades
  in ~2 s.
- **Bag**, with five tabs: MAP (MAP / QUESTS), CHARACTER (CHARACTER /
  GEAR; attributes, aptitudes, derived stats), FINDS, PACK, FEATS.

## Audio

WebAudio only: footsteps, weapon hits, deflect clangs, robot chirps,
level-up and quest stings, ambience per area, and simple procedural
music that shifts for elites and the boss.

## Done when

On a phone in portrait you can start at level 1 in town, take a quest,
try the west toys, cross the east gate, level through the bands, clear
the Training Vault and the gauntlet, and beat the Crate Titan (the dev
menu may be used to skip the grind). Write a README with how to run it
and what is in and out.
