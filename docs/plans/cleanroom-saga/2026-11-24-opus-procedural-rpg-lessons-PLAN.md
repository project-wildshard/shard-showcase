# Lessons from a 300 KB RPG

> Moved from meta `docs/plans/review/2026-11-24-opus-procedural-rpg-lessons-PLAN.md` at `386423cbea` into the cleanroom saga (D38, 2026-11-26).

> Written by: Claude

> **State:** draft, waiting on Jake to review (J513), 2026-11-24. Every row is a proposal. Nothing is built from this plan until Jake picks
> rows on the [board](https://claude.ai/artifact/UrJRSxcv5NBnd1nMkyEzDa). Lane opus-rpglearn wrote it and built nothing.

> **Progress:** 0 of 15.

## Why

Jake, 2026-11-24 ~17:00 Cancún: *"opus subagent look at https://kevintngo.github.io/procedural-rpg/ look at the source
code for it, its a full RPG with fun elements and cool art style and it fits in 300KB. What can we learn, how can we make
our games more fun, how can we make our games faster and higher FPS, how can we build better and cooler content."*

The game is Brushwild (`kevintngo/procedural-rpg` at `8078241`, MIT). We read its source and learned its techniques. We
copy none of its code, art or content and do not recreate the game. Its published page is one `index.html` of 305,443
bytes (101,261 gzipped). The repo's `src/` holds 487 KB of readable JS, most of it GLSL. In the rows below, `bw:` means
that repo's `src/`.

## What we learned

**Size: it ships code that draws, not files.** The game has no images, models or sound files. Every tree, house and
creature is a small distance-field (SDF) function in GLSL; there are 30 props in `bw:world/props.js` and 8 creature
bodies in `bw:gfx/archetypes/`. The land comes from a seed, 32×32 units at a time, about 3 ms a chunk
(`bw:world/worldgen.js:178`, timing from its README). Music and all 39 sounds are synthesized live (`bw:audio/audio.js:532-623`). Place names
are a root plus an ending, so 26 × 15 tables give 550 different names (`bw:world/sites.js:29-30`).
*Example:* a tree is 15 lines of GLSL, five soft-blended spheres with a wobble (`bw:world/props.js:54-73`), not a GLB.
Ours: Driftwood downloads 22.8 MB and Dunes 11.5 MB (engine `budgets/baselines.json`). The engine's session JS alone is
1.37 MB gzipped.

**Fun: every danger is drawn on the ground before it lands, and you answer by moving.** Each beast has one move of its
own: a leap, a charge down a lane, a slam, spores. Its mark fills in from the centre and reaches the rim at the instant
the blow lands (`bw:gfx/passes/fx.js:242-263`, `bw:game/systems/specials.js`). Step out and the number reads "Dodged". Every
beast has one mustard-coloured part, the part that hurts. Blows have weight: the world holds for 30 ms on a hit, 60 ms on
a crit, 70 ms on a kill, 130 ms on an elder kill and 50 ms when you are hit; the longest hold wins
(`bw:game/systems/combat.js:9`, `bw:game/game.js:119-128`). Risk pays: night makes beasts hit 20% harder but pay 60% more
coin. Falling drops a fifth of your coin where you fell, marked on the map, until you go back for it
(`bw:game/systems/stakes.js:14-51`). Exploring pays: every new country pays experience, and caches, stone rings (a
4-minute boon) and beacons sit off the roads on a 96-unit grid (`bw:world/finds.js:16`).
*Example:* the Bristlehog draws a lane, charges down it at speed 13, and if it misses it stands winded for 1.4 s, which
is your window (`bw:game/systems/specials.js:63-103`).

**Speed: few draws, few programs, and math instead of triangles.** A frame is about 12 draw calls: one full-screen
raymarch of the whole world, one ink pass, one instanced draw per creature kind, one draw for every effect, and one final
pass (`bw:gfx/renderer.js:207-230`). It has about 11 shader programs, each compiled one per frame before first sight
(`bw:gfx/renderer.js:111-117`). The world is drawn at a resolution that follows the measured GPU time every 0.7 s,
between 0.45× and 1.5×. Figures, strokes and the HUD stay at full resolution, so the change barely shows
(`bw:gfx/renderer.js:82-108`). Creature poses update 12 times a second ("on twos"), positions every frame. Everything
has a cap: 26 creatures, 700 particles, 24 shadow casters and 8 lights (`bw:config.js:20-34`, `bw:game/fx.js:7`).
*Example:* each creature is a 4-vertex quad. Its body is raymarched inside the quad from 24 floats of instance data, so
40 sproutlings cost one draw (`bw:gfx/passes/entities.js:199-227`).
Ours: Driftwood on an iPhone 13 at phone Low draws 330k to 700k triangles in 45 to 75 draws, is held by the GPU at 19
to 21 ms frames, and links about 40 more shaders after entry, at 77 to 270 ms each (meta
`project/evidence/driftwood-fps/costs-2026-11-19.md`, `project/evidence/driftwood-fps/df20-mini-df20/README.md`).

**Content: every piece of content is a row, and a row can carry its own shader.** A biome is a data row plus a
`score(climate)` function over five slow noise fields: warmth, wet, magic, wild and distance from home. The generator
blends the best scores, so a new biome never touches the generator (`bw:world/biomes.js:1-60`). A prop row lists
`[propId, chance in the open, chance in a forest]`; most trees in a district share one leaf colour and about a fifth
stray, so every wood has a colour of its own (`bw:world/worldgen.js:115-160`). Monsters, specials, talents, items,
bounty kinds, tips and sounds are each one row, and a sound's key is the event name (`bw:audio/audio.js:437`). The
whole game is drawn from one box of 33 pencils (`bw:gfx/glsl/pencil.js:29-37`).
*Example:* adding a creature move is one entry in `SPECIALS` with `begin` (draw the mark) and `update` (move the body),
named by the monster row's `special` field.

## Context a fresh executor needs

- Brushwild: `gh repo clone kevintngo/procedural-rpg` (MIT). Read `README.md` first, then the file named in the row.
  Learn the technique and write our own; never paste its code, GLSL, art or names.
- engine `2fcd9ad03`. Render: `src/client/engine/render/renderer.ts`, `tiers.ts`, `farLod.ts`. Loop and post:
  `src/client/engine/core/Game.ts:773-900, 1817-1990`. Hit-stop: `Game.ts:1051`, `combat/view/SweptMelee.ts:515-549`.
  Telegraphs: `fx/groundTell.ts`, used today by elites, bosses and shardfile abilities (`game/shardfile/abilityTell.ts`).
  Budgets: `budgets/caps.json`, `budgets/baselines.json`.
- sharddev `fc810262`: `packages/sdk/GUIDE.md:430-560` (`defineShard`, `world.ground`, `world.detail`, no runtime JS).
- shard-driftwood `c3d2747`, shard-dunes `4d9e402`.
- meta: `docs/plans/MULTI-REPO-SAGA/2026-11-24-opus-qa-PLAN.md` rows 6 (far views), 11 and 14 (no image stand-ins, J510) and 31 (Driftwood
  FPS); `docs/plans/parked/2026-11-22-fable-prototype-to-mmo-PLAN.md` (parked; engine of primitives).
- Decisions in force: no dynamic resolution on the phone (Jake, 2026-10-20, cited at engine `Game.ts:1818`); a hard cap
  moves only on Jake's word (J439/J444); no flat images for 3D objects (J510); phone checks are play-only for Jake, lanes
  measure on WebKit; no sound from agent runs (QA row 49).

## Rows

Ordered by player impact. Every row is a proposal until Jake picks it.

| Row | Work | Owner | Done when |
|---|---|---|---|
| RL1 | **Driftwood holds 60 on the phone by drawing fewer triangles (QA row 31).** Brushwild spends its GPU on per-pixel math over a few draws; we spend ours on 330k to 700k triangles. Cut Driftwood's phone-Low scene: meshopt-simplify the wide statics past 60 m (extend `render/farLod.ts`), merge static props per square, drop hidden backfaces of the island shell. | shard-driftwood, engine | iPhone 13 route at phone Low DPR 1 (`df20` legs): p50 ≤ 16.7 ms, p95 ≤ 20 ms; scene ≤ 250k triangles and ≤ 50 draws; `render/phone-low/*/driftwood-isle` baselines re-recorded; look board shows no visible loss at 0, 20 and 60 m. |
| RL2 | **Every hostile attack is drawn on the ground first and fills to the hit.** Today only elites, bosses and shardfile abilities use `GroundTell`; plain creatures hit without a mark. Make a tell part of every attack row (ring, lane or wedge), with the fill reaching 1 on the hit's frame, and a "Dodged" number when the player leaves the mark. | engine (`fx/groundTell.ts`, creature attack rows), zones | a test drives each Dunes and Driftwood creature attack and asserts the tell's fill reaches 1 within one frame of the damage tick; a lint refuses an attack row with no tell; playtest: Jake dodges each move on purpose. |
| RL3 | **One feel table: each event has its own hold, shake and sound.** Today a kill holds as long as a hit (`mountedBlade.ts:115`: body, head and kill are all 0.045 s). Move hit-stop, shake and the hit sound into one table keyed by event (hit, crit, kill, elite kill, hit taken), longest hold wins with a 140 ms cap, presentation clock only. Shards override rows. | engine (`Game.ts:1051`, `combat/view/*`) | unit test of the table; a frame log of one fight shows kill holds longer than hit holds and elite kill longest; the server tick is untouched (existing net tests green); playtest: Jake says kills feel heavier. |
| RL4 | **The part that hurts wears one colour.** Each zone picks one accent colour for danger, and every hostile creature wears it on the part that deals damage (horns, claws, the sting). | zones (Dunes, Driftwood first), sharddev look rule | a board of every Dunes and Driftwood hostile shows the accent on its damaging part; Jake picks the colour per zone on the board. |
| RL5 | **Falling costs something you can win back, and night pays more.** On death, drop a share of carried coin where you fell, marked on the map, held until you return or fall again; at night creatures notice you from farther away and hit harder, and pay more. Server-owned. | engine (server economy, map marker) | room test: death drops the share, a second death clears it, pickup restores it; night multipliers in one row per zone; playtest: Jake goes back for his drop at least once. |
| RL6 | **Things to find off the road.** An SDK helper places finds on a coarse grid away from roads and sites, from the zone's seed: caches, boon stones (a timed buff) and lookouts that reveal the map around them. Visiting a new landmark pays. | sharddev (`world.finds`), engine (reach, boon, reveal), Dunes | Dunes has at least 12 finds placed by the helper; a walk test reaches one every 90 s or less on the main loop; playtest: Jake opens a cache and takes a boon. |
| RL7 | **No hitch the first time something appears.** Brushwild compiles one program per frame before first sight. We link about 40 programs after entry at 77 to 270 ms each on iOS. Warm every program a zone can show during the loading screen, one per frame, and count links after the first frame. | engine (`render/precompile*`, loading screen) | Driftwood and Nine route on WebKit: 0 shader links after the first playable frame; the loading screen gets no longer than today plus 1 s. |
| RL8 | **The far ring is drawn, not baked (QA row 6).** Brushwild fades distance to bare paper with a thinner, paler lay and a haze edge (`bw:gfx/passes/world.js:188-195`). Draw a neighbour cell's far view from a small height-and-colour texture with a shader (one draw, lit and hazed like the viewer's sky), keeping its landmarks. | engine (far render), sharddev (far baker writes the texture) | far ring is 1 draw per neighbour and ≤ 256 KB per cell; a board puts it beside row 6's mesh far view at 2 and 3.5 km; Jake picks one. |
| RL9 | **The 3D world can drop resolution while the HUD stays sharp, on the phone too.** Brushwild moves only the world's internal resolution, every 0.7 s from a GPU timer, and keeps figures and HUD at full resolution. This reverses Jake's 2026-10-20 "no dynamic resolution on the phone", so it is his look call first. | engine (`Game.ts:1817-1832`, `renderBudget.ts`) | a board shows Driftwood on WebKit at fixed DPR 1 beside world-adaptive, with fps on each; Jake says yes or no. If yes: phone Low p95 ≤ 20 ms on the iPhone 13 route with no visible blur at rest. |
| RL10 | **One colour box per zone.** A zone declares a box of at most 32 colours; every material colour comes from it, and woods take a district colour with a few strays. This is a look rule, not a byte rule. | sharddev (palette lint, `materials`), Dunes | the lint reports palette coverage per zone; Dunes reaches 100%; a before/after board for Jake. |
| RL11 | **Scatter by climate table.** An SDK helper blends a few slow noise fields (warm, wet, wild) and takes prop tables `[id, open chance, forest chance]` per biome, so authors write rows, not placement loops. | sharddev (`bake/forest`, `bake/meadow`) | Dunes' scatter is rewritten as tables in under 80 lines with the same look on a fixed-camera board; a test pins the placement for a seed. |
| RL12 | **Creatures drawn as raymarched shapes in a quad (a prototype).** One Dunes creature becomes an SDF body raymarched in an instanced quad: real 3D shading and an outline at any distance, not a flat card (J510), one draw for the whole herd. | engine (new archetype pass), shard-dunes | 50 of them on screen cost 1 draw and ≤ 2 ms GPU on the iPhone 13; a board shows it beside the GLB at 5, 40 and 150 m; Jake says if it looks right. |
| RL13 | **Zone music made live.** Brushwild plays generative pentatonic music keyed by biome and time of day, scheduled ahead on the audio clock. Try one zone's score as live synthesis instead of decoded m4a loops. | engine (`audio/synth.ts`), shard-driftwood | Driftwood's decoded audio memory drops by at least 15 MB (ledger, today 18.7 MB); Jake listens to both on his own device and picks (agents never play sound). |
| RL14 | **Driftwood stops shipping what it does not draw.** `near.glb` (4.17 MB) has no meshopt compression, and `trailside.glb` is 3.25 MB. Driftwood also tracks 8.5 MB of Pine Hollow horizon KTX2 in `public/assets/gpu/horizon/`. Compress the GLBs; check whether the Pine Hollow files reach the download and drop them if so. | shard-driftwood | phone download baseline (22.8 MB) drops by at least 4 MB; same look on the fixed-camera board. |
| RL15 | **Ship and verify end to end** (J373). | coordinator | staging, with the picked rows released: Driftwood holds the phone fps floor on Jake's phone in two-player play; a creature's tell, dodge and kill hold read right in a shared fight; the picked far view and colours show on staging; no new Sentry errors for 24 h. |

## Seams

- RL1, RL7 and RL9 touch the same frame budget as QA row 31 and the archived DRIFTWOOD-FPS plan. Whoever takes row 31
  owns RL1; do not run two Driftwood perf lanes.
- RL8 overlaps QA row 6 and FORMAT-PRUNE FP40 (opus-looks, opus-prune). RL8 starts only after Jake's row 6 look call,
  and only if he still wants better far views.
- RL12 must meet J510 (no image stand-ins): an SDF body is shaded 3D, not a card, but show it on a board first.
- RL5 and RL6 change server rules; they follow MMO-SERVER conventions (rows in the shardfile, server owns the truth).
- RL11 and RL10 change the SDK; they ride an SDK cut and do not change the shard format.
- This plan owns only this file. It edits no org repo.

## Verification

Each row's done-when names its proof: engine unit and room tests, the iPhone 13 route bench (`df20` legs) and WebKit
runs for speed, fixed-camera boards for looks, and Jake's playtest for fun. Lanes never play sound and never use the iOS
Simulator (QA row 49).

## Sync

- `MULTI-REPO-MASTER-PLAN.md`: none, a proposal plan; it joins only once Jake picks rows.
- `STATE.md`: none, nothing live changed; STATE is also at its 3 KB limit.
- `docs/README.md`: none, no new theme folder.
- `AGENTS.md`: none.
- `QA-FEEDBACK-2026-11-24.md`: row 56 holds the ask and points here.
- `JAKE-READ-LIST.md`: a "Decide now" line links the board.

## Open decisions for Jake

On the board, about looks and fun only:
1. Which rows to build, if any.
2. RL9: may the phone's 3D world drop resolution under load if the HUD stays sharp?
3. RL4: one danger colour per zone, yes or no?
4. RL12: is a raymarched creature in a quad a real 3D model to you?
