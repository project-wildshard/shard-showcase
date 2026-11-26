# Make Wildshard look and feel like a PS5 game

> Moved from meta `docs/plans/parked/2026-11-11-opus-ps5-feel-PLAN.md` at `386423cbea` into the cleanroom saga (D38, 2026-11-26).

> Written by: Claude

> **State:** draft, parked, 2026-11-11. Audit and rows; nothing is built. PF1 is done (the teardown). PF3 (cross-origin
> isolation) is approved (J268) and goes to the next free lane; PF4 (the WebGPU test) is approved as a test (J269). Every
> other row waits for Jake to promote it.

## Why

Jake, 2026-11-11, with a link to <https://playgta5.com>:

> *"We need to take everything we doing to the AA to the A, like a level beyond… the browser can do anything and
> everything, we are just not even."*

and, correcting the first draft of this plan:

> *"it's literally GTA5, its 60 fps, it runs smooth, its the full game, textures, assets animations driving. It looks and
> feels really fucking good, nothing like a browser game. Its a literal example of a PS5 style game playing in a browser…
> how can we make our browser ai slop not feel like a random slop demo game but feel like a real PS5 game polished, 60
> fps running full feature, full graphics quality in the browser."*

> *"like we already load in 5s, what I want is for the game to look and feel like a GTA5 style PS5 game lol."*

Loading, sharing and new platform features are out of scope (J270). This plan is only about **look, feel and 60 fps**.

## 1. What the port proves

[ps5-feel/PLAYGTA5-TEARDOWN.md](support/ps5-feel/PLAYGTA5-TEARDOWN.md): the real GTA V renderer, assets and animation run at
60 fps in a tab. So the browser is not why we look like a demo. The gap is in four places, in this order:

1. **Lighting and image:** how light, shadow, atmosphere and the camera image are built.
2. **Motion:** how characters, the camera and vehicles move.
3. **Content:** whether every asset shares one scale, one material language and one level of detail.
4. **Frame rate:** 60 everywhere, steady, with the quality above switched on.

## 2. Audit: Wildshard against GTA V (engine `main`, 2026-11-11)

| Area | What GTA V does | Wildshard today (where it is) | Gap |
|---|---|---|---|
| Frame rate | 60, steady | Phone capped at 30 (`client/engine/core/tier.ts` `frameCapFps` → `mobileCap`); desktop uncapped; Nine Dragon falls to 15-18 fps on a hot phone ([ENGINE-BENCHMARKS](https://github.com/Raynos/project-wildshard-meta/blob/main/docs/plans/parked/2026-11-10-opus-engine-benchmarks-PLAN.md)) | Big |
| Image | HDR with filmic tone map and eye adaptation; temporal anti-aliasing; renders below native and reconstructs | FXAA on/off only (`graphicsQuality.ts`); tone mapping set per level, one path sets none (`NoToneMapping`); 2× pixel density is how we buy sharpness | Big. Temporal AA plus upscaling is how consoles get both quality and 60 fps |
| Shadows | Soft cascades, contact shadows, shadows always on | `PCFShadowMap`; Low turns sun shadows off | Medium |
| Ambient occlusion | SSAO everywhere: objects sit *in* the world | Not in the post chain (only `Terrain.ts` mentions it) | Big: the main reason props look pasted on |
| Sky and atmosphere | Scattering sky, volumetric fog, light shafts, full day/night and weather | Per-level fog and god rays; Driftwood's phone tier has no rays and no bloom | Medium |
| Reflections | Wet roads, water and glass reflect the scene | None found beyond water shading | Medium |
| Camera image | Motion blur, depth of field, lens effects | None (no motion blur or DoF in the tree) | Medium |
| Night | Hundreds of lights in a street | Three's forward renderer: each extra light costs every lit draw | Big for night scenes |
| Locomotion | Starts, stops, turns, leans, foot IK on slopes, look-at | Three `AnimationMixer` with state crossfades (`client/engine/anim/machine.ts`); IK only in limb, arm and NPC rigs | Big: the "floaty" feel |
| Hits and deaths | Physics-blended reactions (Euphoria) | Ragdolls for dying animals only (`client/engine/physics/ragdoll.ts`) | Medium |
| Camera | Spring arm with collision, lag, speed FOV, shake | Not audited yet (PF2 does) | ? |
| Driving | Full vehicle physics, chase camera, engine audio | No cars. Hoverboard only. Rapier ships a ray-cast vehicle controller we don't use | A whole feature |
| Content | One art direction: consistent scale, PBR values, texel density, decals, dense dressing | Generated meshes from mixed sources; no texel-density or material-value check | Big, and the root of "AI slop" |
| Audio | Reverb zones, occlusion, surface footsteps, layered city ambience | Spatial audio and ambience beds exist (`client/engine/audio/`) | Small to medium |

## 3. On WebGPU (J269)

Jake: *"WebGPU we can test it, but what benefit would it have lol."* Switching API changes nothing on screen by itself.
It pays for three things in this plan: **many lights** (clustered lighting in a compute pass makes PF13's lit night
streets affordable), **more objects at 60 fps** (lower CPU cost per draw, GPU culling), and **cheaper effects** (AO, TAA
and particles in compute). PF4 measures whether those wins are real on our scenes before anything depends on them.

## 4. Rows

One lane each, under an hour. Every visual row ends with a before/after **board** (screenshots, same camera, same time of
day), because Jake judges looks from images. FPS rows report Mac and Jake's iPhone 17 Pro.

| Row | Work | Done when |
|---|---|---|
| PF1 | Tear down playgta5.com from its shipped sources | Done: [ps5-feel/PLAYGTA5-TEARDOWN.md](support/ps5-feel/PLAYGTA5-TEARDOWN.md) |
| PF2 | **The gap board.** Six matched scenes, GTA V (playgta5.com in headless system Chrome, J148) against Wildshard: street at noon, golden hour, night, character close-up walking, running on a slope, camera in motion. Each pair annotated with what differs | A published board in JAKE-READ-LIST; every difference maps to a row below or a new one |
| PF3 | Cross-origin isolation (COOP/COEP) on preview, then play (J268) | `crossOriginIsolated === true` on preview, all e2e green, anything that broke listed and fixed |
| PF4 | WebGPU test: Driftwood on three's WebGPU renderer behind a flag (J269) | One table: CPU ms per frame, GPU ms, draw count, and a 200-light night scene, WebGL against WebGPU, Mac and iPhone |
| PF5 | 60 fps budget: profile Driftwood and Nine Dragon at an uncapped 60 on iPhone and Mac; name the top five costs | A table of the five costs with ms each, and the cap lifted behind a setting |
| PF6 | Temporal AA with upscaling: render at 1× (or below) and reconstruct, replacing FXAA and 2× density | Board: sharper than today's 2× at lower GPU ms |
| PF7 | One HDR image: filmic tone map and eye adaptation, the same on every level | Board of all seven shards before and after; no level left with no tone mapping |
| PF8 | Ambient occlusion (half-resolution GTAO) in the post chain | Board: props and characters grounded; GPU ms under 2 on iPhone |
| PF9 | Soft shadows: cascades with soft filtering plus screen-space contact shadows, kept on at 60 fps | Board: soft penumbra, characters' feet touch the ground |
| PF10 | Sky, atmosphere and volumetric fog with a full day/night cycle | Board: the same street at dawn, noon, dusk and night |
| PF11 | Reflections: screen-space plus reflection probes for water, wet ground and glass | Board: water and a wet road reflect the scene |
| PF12 | Camera image: motion blur and depth of field (cutscenes and menus) | A clip of a fast camera turn, before and after |
| PF13 | Night with many lights: clustered lighting (WebGPU if PF4 says so) | Board: a street with 100+ lamps at 60 fps |
| PF14 | Locomotion: starts, stops, turn-in-place, lean, foot IK on slopes, look-at | Side-by-side clip of the player walking a slope and turning, before and after |
| PF15 | Hit reactions: physics-blended ragdoll for people, not only animals | Clip: a hit staggers, a death falls with physics |
| PF16 | Third-person camera: spring arm with collision, lag, speed FOV, small shake | Clip of a run through a doorway and a sprint, before and after |
| PF17 | Driving: one car on Rapier's ray-cast vehicle controller, chase camera, engine sound (needs Jake's go: a new feature) | Jake drives a lap of a shard on his phone at 60 fps |
| PF18 | Content audit: texel density, PBR values and scale of every asset in one shard, worst offenders listed | A table per asset and a fix list; the shard's worst ten fixed |
| PF19 | Decals and set dressing: grime, wear, road markings, litter, on one street | Board: the same street, before and after |
| PF20 | Foliage wind and water shading | Clip: grass and trees move in wind, water has depth and foam |
| PF21 | Audio: reverb zones, occlusion, surface footsteps | A clip walking from a street into a building |

**Recommended order:** PF2 first (it is the yardstick, and it may reorder everything), PF3 and PF5 alongside it, then the
image rows in the order that changes the most pixels: PF6, PF7, PF8, PF9; then motion (PF16, PF14); then the rest.

## Seams

- [ENGINE-BENCHMARKS-PLAN.md](https://github.com/Raynos/project-wildshard-meta/blob/main/docs/plans/parked/2026-11-10-opus-engine-benchmarks-PLAN.md) (parked) owns the benchmark harness; PF4 and PF5 use it or seed it.
- The graphics settings (MOBILE-GRAPHICS MG8, `graphicsQuality.ts`) are Jake's toggles: new effects become toggles there, and
  High stays "never more expensive" until Jake moves that line.
- Engine decision 22 / X6 (WebGPU containment): PF4 is the flagged test J269 allows; the default renderer stays WebGL.
- [SHARD-AUTHORING-PLAN.md](https://github.com/Raynos/project-wildshard-meta/blob/main/project/archive/2026-11-19-shard-source.md#part-c) owns shard content; PF18 and PF19 fix assets through it.
- J176: browser only. J148: playgta5.com runs only in headless system Chrome or a cloud container, never repo Playwright.
- Code lands in engine through `scripts/land.mjs` (J240). This plan owns only its own two files.

## Verification

Every row's proof is its board or clip, published and listed in JAKE-READ-LIST, plus FPS numbers from the real game on
preview (Mac and Jake's iPhone). A visual row is done when Jake has seen its board, not when the code merges.

## Sync

- `MULTI-REPO-PLAN.md`: J268 (cross-origin isolation), J269 (WebGPU as a test), J270 (scope: look and feel, no tiers).
- `STATE.md`: none; nothing live changed.
- `docs/README.md`: the parked row names PS5-FEEL.
- `AGENTS.md`: none.
- `archive/QA-FEEDBACK-2026-11-11.md`: rows 1 to 3.

## Open decisions for Jake

1. **Driving (PF17):** add cars? Recommended: yes, one car on one shard as a test, after PF2.
2. **Phone 60 fps (PF5):** lift the phone's 30 cap once PF5 shows the costs fit? Recommended: yes, behind the settings
   toggle first.
