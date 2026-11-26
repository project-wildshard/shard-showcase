# The idea bank

> Moved from meta `docs/prototype-to-mmo/IDEAS.md` at `386423cbea` into the cleanroom saga (D38, 2026-11-26).

> Written by: Claude

> **State:** working notes, 2026-11-16. A test for [STRATEGY.md](STRATEGY.md), not a backlog. Nothing here is scheduled, and no idea is approved or ordered. Ideas 1 to 16 are Jake's, from his voice notes of 2026-11-16; ideas 17 to 37 were added by the agent to widen the test. The "leans on" column is the agent's judgement.

## How to read it

Jake's method is to implement about a hundred ideas and generalise the engine with each. This file asks the question in advance: if every idea here had to be built, how many different primitives would the engine need?

- Each idea is a 500 m zone, described by what the player does in it. A named game is a reference for the feeling, not something to copy.
- **Leans on** lists the primitives from section 5 of the strategy that the idea can't work without. Every idea also uses entities, state fields, events and queries, so those aren't listed.
- The words in that column are fixed so the rows can be counted: `abilities`, `senses`, `bodies`, `modes` (movement modes), `animation` (clips with events), `parts` (hit zones on a body), `fields` (space fields), `parenting`, `third-person`, `paths`.
- **Asks the platform** is anything the idea needs from the MMO itself beyond the standard HUD, quests, saves and loot.

## Jake's zones and ideas

| # | Idea | What the player does | Leans on | Asks the platform |
|---|---|---|---|---|
| 1 | Driftwood: Wind Waker in 500 m | Sails a small boat between islets, reads the wind, lands and explores | parenting, modes, bodies, fields | |
| 2 | Pine Hollow: first-person hunting | Stalks animals upwind with rifles, crossbows and bows; shot placement matters | abilities, senses, parts, fields | |
| 3 | Nine Dragon: Chongqing meets cyberpunk | Climbs a vertical city by grapple, wall-run and rooftop parkour | modes, bodies, paths | |
| 4 | Nalati grasslands | Rides the steppe, watches herds and wolf packs, tames a horse | senses, parenting, modes, abilities, fields | |
| 5 | The showcase | One of everything: conveyor, jump pad, see-saw, parry, scramble climb | bodies, modes, abilities, animation, paths | |
| 6 | Mossgate and Brasscap templates | The bare minimum done well: weapons, enemies, characters to talk to, quests | abilities, senses | |
| 7 | The canyon train | Rides a looping train through two tunnels, fights along its roofs, raids the camps | parenting, paths, bodies, abilities, senses | |
| 8 | Desert infiltration (Metal Gear Solid V's Afghanistan) | Scouts an outpost, crawls, distracts guards, gets in and out unseen | senses, abilities, modes, fields, animation, third-person | |
| 9 | Rooftop assassin (Assassin's Creed) | Climbs anything, leaps between roofs, blends into crowds, takes down a target | modes, senses, animation, third-person, abilities | |
| 10 | Ancient Rome | Walks a crowded forum and market, then fights in the arena | senses, animation, abilities | |
| 11 | Tropical outposts (Far Cry 3) | Frees an outpost any way they like: fire, animals, vehicles, a glider | senses, abilities, bodies, fields, modes, parts | |
| 12 | Samurai duels (Ghost of Tsushima) | Stances, standoffs and timed parries, with the wind showing the way | abilities, animation, third-person, senses, fields | |
| 13 | Machine hunting (Horizon) | Shoots components off large machines, lays traps, uses elemental arrows | parts, abilities, senses, third-person, animation, bodies | |
| 14 | A Skyrim hold | Clears a barrow with sword and spells, talks to a jarl, fights a dragon | abilities, senses, animation, parts | |
| 15 | A Crysis beach | Suit powers (strength, speed, cloak), physics props, huts that break | abilities, senses, bodies, parts | |
| 16 | Squad role-playing (Mass Effect) | Powers on cooldown, two squad mates, cover, conversations with choices | abilities, senses, third-person, animation, modes | |

## More, towards the hundred

| # | Idea | What the player does | Leans on | Asks the platform |
|---|---|---|---|---|
| 17 | Climb a giant (Shadow of the Colossus) | Climbs a walking creature and strikes its weak points | parenting, modes, parts, animation, third-person, bodies | |
| 18 | Glide and climb anywhere (Breath of the Wild) | Climbs any surface, glides on updraughts, uses fire, ice and wind | modes, fields, abilities, bodies | |
| 19 | Wall-run arena (Titanfall) | Chains wall-runs, slides and double jumps while shooting | modes, abilities | |
| 20 | Big-monster hunt (Monster Hunter) | A long fight with one beast: break its parts, read its tells | parts, abilities, animation, senses, third-person | |
| 21 | Ship crew (Sea of Thieves) | Several players crew one ship: sails, helm, cannons, repairs | parenting, bodies, fields, modes, abilities | Player-versus-player rules |
| 22 | Convoy chase (Mad Max) | Boards and wrecks a moving convoy from their own vehicle | parenting, bodies, paths, abilities, senses, parts | |
| 23 | Physics puzzle chambers | Cubes, buttons, lifts and launch pads, solved alone or in pairs | bodies, paths | |
| 24 | Parkour time trial (Mirror's Edge) | Runs a rooftop course against the clock | modes, paths | A leaderboard |
| 25 | Boss duel (Dark Souls) | One hard enemy, stamina, dodge timing, learned patterns | abilities, animation, parts, senses, third-person | |
| 26 | Horde survival (Left 4 Dead) | Four players hold out against waves paced by a director | senses, abilities | |
| 27 | Shrinking ring (PUBG) | A closing circle pushes players together | fields, abilities | Player-versus-player rules |
| 28 | Capture the flag | Two teams, two bases, a flag that is carried | parenting, abilities | Player-versus-player rules |
| 29 | Wave defence | Places turrets along a lane and holds it | paths, senses, abilities | |
| 30 | Fishing village | Casts a line, plays the fish, sells the catch | bodies, fields | A shard-drawn interface |
| 31 | Hoverboard race | Races a track with boosts and shortcuts | bodies, modes, paths | A leaderboard |
| 32 | Card tavern | Sits at a table and plays cards against other players | | A shard-drawn interface |
| 33 | Blink-and-sneak heist (Dishonored) | Teleports short distances, hides in shadow, steals something | abilities, senses, modes, fields | |
| 34 | Deep dive (Subnautica) | Dives a reef with limited air, light and pressure | modes, fields, bodies, senses | |
| 35 | Mech pilot | Climbs into a walker, stomps and fires its weapons, gets out again | parenting, modes, abilities, parts, bodies | A shard-drawn interface |
| 36 | Dragon rider | Tames and flies a dragon and fights from its back | parenting, modes, abilities, senses, animation | |

## What the count shows

Across ideas 1 to 36:

| Primitive | Ideas that lean on it |
|---|---|
| Abilities | 27 |
| Senses and steering | 21 |
| Movement modes | 18 |
| Bodies and joints | 16 |
| Space fields | 12 |
| Animation with events | 12 |
| Hit zones on parts | 10 |
| Parenting | 9 |
| Third-person camera and body | 8 |
| Paths | 8 |

- **Thirty-six ideas need ten primitives**, plus the four every idea uses. Today the same ideas would need a host each, or several.
- **The same primitive shows up in ideas that look nothing alike.**
  - Parenting plus a movement mode: the boat, the horse, the train car, the giant, the ship, the mech, the dragon.
  - Abilities: the suit powers, the spells, the squad powers, the elemental arrows, the blink, the stances.
  - Senses: the guards, the herd, the horde, the crowd, the squad mates.
  - Space fields: the sailing wind, the hunter's scent, the fire that spreads, the closing ring, the air and pressure of a dive.
- **Abilities and senses lead the count**, and both already exist in the engine in some form: a combat pipeline built on tags and attributes, and perception written into each creature brain. They need opening, not inventing.
- **Movement modes come third** and are the largest piece of new work, because each one must be predicted on the player's own device.

## What doesn't fit

| # | Idea | Why it doesn't fit |
|---|---|---|
| 37 | Build a base (Minecraft, Conan) | The player changes the shape of the world and it stays changed. Section 5 has no primitive for geometry that players edit and the server saves. A small version (placing pieces from declared templates on a grid) fits the declared pools in the strategy's section 7; digging and free building do not |

Three other things sit outside the primitives and belong to the platform:

- **Player-versus-player rules** (ideas 21, 27, 28): who may hurt whom, teams, and what a death costs.
- **A shard-drawn interface** (ideas 30, 32, 35): a card table, a fishing reel or a cockpit can't be made from the standard HUD's pieces.
- **Leaderboards** (ideas 24, 31): a saved, ranked score across players.

## Which idea pulls which primitive forward

The strategy's section 9.4 gives an order of generalising. These are the ideas that would force each step.

| Step | What becomes general | Ideas that force it |
|---|---|---|
| A | The script interface and the shared library | All of them |
| B | Entities with parents | 7 the train, 1 the boat, 28 the flag |
| C | Movement modes | 3 Nine Dragon, 19 wall-run, 24 time trial, 18 glide and climb |
| D | Abilities for weapons; hit zones as parts | 2 hunting, 13 machine hunting, 15 suit powers |
| E | Senses and steering as a shared service | 8 infiltration, 11 outposts, 26 horde |
| F | Third-person body, animation with events | 12 duels, 9 assassin, 25 boss duel |
| G | Space fields | 1 sailing wind, 27 the ring, 34 the dive |
