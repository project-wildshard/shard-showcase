# History: the multi-repo saga's plans on format, hosts and scripts

> Moved from meta `docs/prototype-to-mmo/evidence/history-multi-repo-saga.md` at `386423cbea` into the cleanroom saga (D38, 2026-11-26).

> Written by: Claude

> **State:** point-in-time record, 2026-11-16. A read-only study by a research subagent for [STRATEGY.md](../STRATEGY.md), saved as reported. It read the meta repo's live, parked and archived plans, the J-decisions and the grill logs. Its plan index and tag counts are approximate, and its last section is its own inference.

I've read everything the report needs except the items listed under "Not read" at the end. I stayed read-only, left `docs/prototype-to-mmo/` alone and printed no secrets.

## Wildshard meta repo: history of the format, hosts and scripts work

**Repo:** `/Users/raynos/projects/games/project-wildshard-meta`. All plan paths below are under `docs/plans/`. Dates are 2026, Cancún time. "Doc:" marks what a file says. "Inference:" marks my own reading.

**Activity (from git):** 4,000 meta commits since 11-04. There were 734 on 11-15 and 773 on 11-16. SHARD-SOURCE-PLAN has 253 commits since 11-06. ONE-FORMAT-PLAN has 130 commits since it was created on 11-15. MULTI-REPO-PLAN has 310 since 11-04. WASM-HOST.md and HOST-AUDIT.md first appeared in meta on 11-15 (commit `f41664b7`), moved over from singleplayer under J366, and each has one commit.

## 1. Plan index

**Files:** 40 live at the top level (the QA-FEEDBACK files count one each), 11 parked plus 2 subdocs, and 97 archived (94 .md and 3 .html).

### Format, hosts and scripts (FORMAT/HOSTS/SCRIPT)

| Plan | State | Goal |
|---|---|---|
| ONE-FORMAT-PLAN | live, 42/134, M1 active | One shard format with no first-party path. Creatures leave the engine. One-shard hosts become documented primitives. |
| SHARD-COMPAT-PLAN | draft, 6/57 | Format changes never force a re-upload. Migrations are data only. Sections and hosts are versioned. |
| HOST-AUDIT.md | draft, parked (J366) | Delete or generalise one-shard hosts. Behaviour goes to data or WASM. |
| WASM-HOST.md | draft, parked (J366) | Script ABI v2: sim, project, view and bake lanes, fuel inside Wasm, no shard TypeScript. |
| archive/HOST-RULER | 10/10, closed 11-14 | Measure and register the hosts. Shards ship no runtime TS. |
| archive/SERVER-PARITY | 24/25 | The world was built twice (page and server). Fix openWorld, add a side table and a parity diff. |
| archive/SHARDFILE-EVOLUTION | folded into SHARD-COMPAT | A breaking-change detector. |
| archive/SHARD-PIPELINE | 4/20, folded into SHARD-COMPAT | Cook, migrate and break rules. |
| archive/SHARD-IMPORTS | folded into SHARD-COMPAT Track D | |
| archive/SHARD-SIZE | 15/16 | Byte budgets. |
| archive/CUSTOM-CREATURES | folded into ONE-FORMAT M5 | The v1 plan was a "sandworm in disguise". |

### Authoring (AUTHORING)

- **Live:**
  - SHARD-SOURCE-PLAN: 170/201. A compiler front end, `wildshard watch`, the cleanroom loop.
  - SDK-SPLIT-PLAN: 5/36, Part B approved under J379. Six packages; async upload.
  - NEW-SHARD-E2E-PLAN: NE1 to NE5 done. A Honeyknoll shard built with nobody watching.
- **Archived:** AUTHORING-PARITY (0/39, folded into SHARD-SOURCE), SHARD-AUTHORING (46/54), SHARD-PUBLISH-ACTIONS (complete 11-16, J371), SHARD-DELETE (12/12), TEMPLATES-CLEANROOM (4/18), T1-TOOLING and T1-TOOLING-PLAN, DRAFTS (7/7).

### Content (CONTENT)

- **Live:** TEMPLATE-E2E-PLAN, 128/144. Content first (J357/J361): Brasscap TC-B rows, Mossgate TC-M rows.
- **Archived:** AUDIO (21/21), REMOTE-PLAYERS (13/13, J296).
- **Parked:** PS5-FEEL.

### Netcode and server (NETCODE/SERVER)

- **Live:** MMO-PLAN (32/48), MMO-SERVER (in progress), MMO-FAILURE-MODES (2/25), NET-LAG (14/30), OFFLINE (26/27), SERVER-CELLS (9/10), WIRE-STABILITY (17/24), ZONE-ENTRY (J352).
- **Archived:** E5-REPLICATION, E5.3, E7 (14/14), E7-SITTING-RUNBOOK, GRID-CROSSING, GRID-CROSSING-2 (23/37), GVS (10/10), ROAD-PRELOAD (3/8), ROAD-RESIDENT (5/9).
- **Parked:** MMO-MODERATION, MMO-PARTIES ("really complicated feature"), MMO-ZONE-SELECT.

### Infrastructure (INFRA)

- **Live:** LEFTOVER-CLEANUP, PACKS-CDN (2/5), PAGE-SIZE (25/28), REPO-DISK (38/48), REPO-WEIGHT (stale), SENTRY-TRIAGE.
- **Archived (all complete or closed):** API-CLOUDFLARE, API-SERVER-CD, AUTO-RELEASE, BROWSER-KEYCHAIN, LOCAL-SUPER-REPO, MAC-MINI-ACCESS, MAC-MINI-RUNNER, NODE-MODULES-WEIGHT, NPM-PUBLISH (10/12), OFF-VERCEL, OPENCLAW-EXTRACT, RELEASE-BRANCHES, RELEASE-TRAIN, SHELL-CUTOVER (3/4), SPLIT-REPAIR, STALE-BUILD, TEMP-HYGIENE, VERCEL-SPEND, VPS-HARDENING, WWW-CLOUDFLARE.
- **Parked:** EMAIL-PROOF.

### Process (PROCESS), one line each

- **Live:**
  - CI-QUEUE: draft, J384.
  - CI21-PORT: 1/11.
  - HOW-WE-BUILD: 156/209.
  - LOCAL-LINK: 0/8.
  - MACHINES.
  - MINI-FLOW: 8/12.
  - MINI-UNBLOCK: 7/15.
  - MULTI-REPO-DEVELOPMENT: draft, 11-07.
  - REPO-KIT: 8/11.
  - TEST-COVERAGE: lean, J370.
  - QA-FEEDBACK 11-12, 11-13, 11-14, 11-15, 11-15-mini, 11-16, 11-16-mini.
- **Archived:** AUTO-COMPACT-TRIAL, BOILERPLATE, BROWSER-TESTS-BENCH, BUILD-MAX-APPROACH, CI-JOB-PACKING, CLOSE-OUT-STRATEGY, COMMIT-QUALITY, DEV-SPEED, DOWNLOAD-THEN-C, ENGINE-CI-SPEED, ENGINE-CUT, ENGINE-FLAKY-TESTS, ENGINE-MOVE-CLEANUP, FAST-SLOW-TESTS, HEAVY-SIM-TESTS, JAKE-BLOCKERS-AUDIT, LAND-SIMPLIFY, LANES-AFTER-SORT, MOVES, MULTI-AGENT-TOOLING, P0-SETUP, P1-IN-TREE, P3-GAPS, P3-LIFT, P4-P5-LIFT, PHONE-CLOSE, PLAN-STATUS, QA-FEEDBACK 11-07/09/10/11, SINGLEPLAYER-LEFTOVERS, TEST-SPEED (67/88), VELOCITY, VITEST-BENCH, WORKTREE-LAND-STANDARD, WORKTREE-PR (dropped).
- **Parked:** JAKE-REVIEW-SINGLEPLAYER, NIGHTLY-MAC, PHONE-ALARMS.
- **Also:** the `multi-repo/` folder (MULTI-REPO-PLAN with J1 to J384, STATE, JAKE-READ-LIST, grill logs).

### Other (OTHER)

- **Live:** NINE-DRAGON-BENCHMAX (perf; NB8 "budget not met").
- **Archived:** DEVICE-TELEMETRY, KEYBOARD-PLATFORM, LOADING-DIAGNOSTICS, LOADING-SCREEN, MOBILE-GRAPHICS (11/12), MOBILE-KEYBOARD, RELOAD-BUTTON, SETTINGS-REDESIGN, VOICE-CHAT, VOICE-POLISH, WWW (1/12).
- **Parked:** ENGINE-BENCHMARKS, NOVEMBER-IDEAS, WWW-REDESIGN.

### Counts per tag

My tagging is approximate. PS5-FEEL counts as CONTENT. Of the remaining parked files, 3 are OTHER (ENGINE-BENCHMARKS, NOVEMBER-IDEAS, WWW-REDESIGN), which is also how they are listed above.

| Tag | Count |
|---|---|
| PROCESS | about 57 |
| INFRA | about 27 |
| NETCODE/SERVER | about 20 |
| OTHER | about 14 |
| FORMAT/HOSTS/SCRIPT | 11 |
| AUTHORING | 11 |
| CONTENT | 4 |

Inference: process work outweighs format work by roughly 5 to 1, and content plans are the rarest kind.

## 2. Format, hosts and scripts: what each plan says

### WASM-HOST.md (parked)

- **Problem.** Jake on 10-20:
  - "beef up what can be done with WASM... unlock new capabilities"
  - "once you enter the WASM, it shouldn't be going back into JavaScript"
  - "run assembly code at 60 hertz or 30 hertz"

  Measured costs: the fuel price is module-sized (Pine's `life` costs 32,064 per iteration, and integrators refused it); JS calls inside the guest; memory copies; and only about 10 Hz event decisions. Doc: "New shards should be data plus AS with no TypeScript."
- **Design (ABI v2).** Four lanes:
  - a sim lane at 10 Hz, or 30 Hz with a stated reason
  - `ws_project`, replacing about 109 `.project` calls in 35 files
  - `ws_view` at display rate, client only
  - bake

  One `ws_step` per module per tick; the module is the trust boundary.
- **Requirements:** W2 untrusted authors; W5 v2 replaces v0/v1 in one go; W8 a language-neutral ABI; W13 runnable on the server.
- **Done-when (W12):** a demo shard with zero shard TS, at 1 ms or less per frame for 20 bindings.
- **Progress.** Only D1 (council) is done. The view lane was started on 10-21, scoped to Pine and Driftwood. Rows H0 to H17 are all open. Cutover scope: 56 AssemblyScript files, 2,791 lines.
- **Status.** Parked since 11-04 ("Wasm host, we're not working on that"). G969 barred the work, and J366 parked it in meta.

### HOST-AUDIT.md (parked) and host-audit/custom-sections-mini-plan.md

- **Jake, 10-22:** "Stuff that clearly does not belong in the engine or the game needs to go into the shard files as data or WASM. Various hosts need to either be deleted or made generic."
- **Measured:** 250 named hosts (201 in the game layer). About 4,570 lines serve a single shard: Pine 2,781, Driftwood 924, Nalati 869. Of 114 inventory recommendations, 95 keep, 18 fold and 1 retires.
- **Jake, 10-24 (E498):** "We don't want custom sections... one generic format for everything, and some of those custom sections may have to be evicted to WASM... pull in the WASM v2 plan."
- **Outcome.** Custom sections went from 387 (15 under `custom/` plus 372 named JSON, 33.6 MB) to 342 and then to 0 by 11-04 (rows Z0 to Z15).
  - Doc: much of that drop came from "registration" under Jake's one-user approvals (G1004). Behaviour went to AssemblyScript on the existing Script ABI, not v2.
  - Inference: the count was driven to zero, but the generic second users the plan wanted mostly never appeared.

### HOST-RULER (archived 10/10, 11-14)

- Shards ship no runtime TS: 19,972 of Pine's 19,977 lines sit in generators.
- Doc: "only shard code left is in one-user engine hosts."
- Size of each layer: the engine layer is 849 files and 129.5k lines; the game layer is 848 files and 120.9k lines.
- Kinds of thing: 63 page plan kinds, 72 section names and 46 native-assembly hosts. The register `lint/host-register.json` has 428 rows.
- One-user lines on 11-13: Nalati 3,856, Driftwood 661, Nine 497, Pine 404, Far Reach 38.

### SERVER-PARITY (archived 24/25)

- **Jake, 11-12:** "full audit... WASM v0, v1, v2... That's why we fell down the rope bridge."
- **Three ABIs live at once:**
  - v0: 2 scripts, 77 lines.
  - v1: about 23 programs, 1,270 lines, sim only.
  - v2 lanes: Nalati 5 project lanes (2,464 lines) and 5 view lanes (418); Driftwood bridgeSway (42); Nine movers (58).
- **Root cause:** the world is built twice, once from 63 page kinds and once from 46 server hosts.
- **Fixes:** 7 bugs. 27 cases were "silly" duplicates but were left alone: three day clocks, two water hosts, three weather systems, herd logic across four hosts, three boss shapes. J289/J292: "don't fix the silly hosts... fix the buggy ones."
- **Open:** migration rows M1 to M3 (v1 to v2) were never started.

### ONE-FORMAT-PLAN (live, 42/134), with `docs/audits/2026-11-15-one-format-audit.md`

- **Audit facts:**
  - 1 format; 0 shards upload JS.
  - The trust split lives in the engine (`product.ts:502-503`).
  - 41 of 46 server hosts and 37 of 63 page features serve one shard.
  - 2 creature paths, 2 creatures still in TypeScript (boar, bear), about 12 manifest duplicates, 5 ways to define a creature's look, and ABI v1 still beside v2.
- **Audit verdict:** "Those hosts are the MMO primitives Jake wants. They need to be opened up and documented, not deleted."
- **Milestones M1 to M9:**
  - Creatures leave the engine.
  - Layers and skeletons.
  - Custom hatch: CC59 script hooks with fuel of 2M per call and 8M per tick; CC60 whole-creature WASM from any upload.
  - Gates, then dangerousX, then budget tiers (OF10c).
  - Primitives OF16 to OF41.
  - OF17: a host list derived from the server replaces `native-assembly.json`.
  - Six shards moved; a stranger shard (OF25).
- **Out of scope:** world page features, view code, slug-keyed code, ABI v1.

### SHARD-SOURCE-PLAN (170/201)

- **J339:** "shard format poisons the way you define levels."
- **Poisons found:** P1 to P8. For example, P7: gameplay scripts are raw memory writes, `store<f64>(24576+...)`.
- **Answer:** "No new format. A compiler front end." Constraint: "a per-frame update(t) closure cannot ship."
- **Tooling:** `wildshard watch` with a thin devserver hook in the engine (J347). Every change must be additive.

### SHARD-COMPAT (draft, 6/57) and SDK-SPLIT (5/36)

- **SHARD-COMPAT:**
  - Migrations are data only, "Never code or binaries". An ABI change is met by an engine adapter.
  - Version scheme: Jake's four-part version plus a `version` on each section and host, and a `--trust-me-bro` override.
  - Worked example: `weather.forest` to `weather.drawn`.
- **SDK-SPLIT:**
  - Six packages: sdk, kit, build, upload, dev, cli.
  - 33 engine-reaching exports get new homes.

### Synthesis (inference)

1. **Counts.** The counts that have ratchets fall fast: custom sections went to 0 and the host register covers everything. Real one-shard engine code does not fall: 41 of 46 server hosts and 37 of 63 page features still serve one shard, and Nalati's one-user lines rose from 869 (HOST-AUDIT) to 3,856 (HOST-RULER), though the two audits may count differently.
2. **Reframing.** Between 10-22 and 11-15 the plan for hosts changed from "delete or make generic" to "open them up as documented primitives".
3. **Where behaviour moves.** Out of shard TS (done) and out of custom sections (done on paper). It moves into data rows plus engine primitives switched on by sections, with quirks pushed to shard AssemblyScript on the v1/v2 ABIs. Creatures are the first category leaving the engine (ONE-FORMAT M1 to M5).
4. **What WASM v2 is for.** It is the stated escape hatch that lets untrusted authors build anything without engine changes. Every plan points at it (E498, Q3 "there's a WASM HOST V2 plan ffs", CC60), yet it was parked three times: 11-04, G969, J366. No v1 to v2 migration has started.
5. **End state the docs describe.** The server loads data plus sandboxed WASM. The engine is a library of documented, versioned primitives, and the server derives which hosts exist. There is one ABI with budget tiers. Shards are compiled from friendly source. Upload is async and placement is automatic.

## 3. Decisions on format, hosts, scripts, authoring, creatures, camera and uploads

This leaves out the decisions you already know (J339, J340, J341, J343, J344, J352, J357, J361, J364, J370, J381).

**Format and trust**
- **Vision decision (10-03):** sandboxed WASM plugins behind a data-only host API are an approved system, which overrode the brief's ban on uploaded WASM (`docs/vision/VISION.md`, tensions table).
- **J3:** the raw shardfile format is cooked into packs.
- **J4:** declared replication, Unreal-like.
- **J21, J144, J158:** a shard never imports the engine.
- **J60, J86:** "No first-party shortcuts."
- **J152:** first-party authors only, for now.
- **J262:** an engine break means a recook.
- **J308:** the shard-format rename.
- **J316, J319:** compatibility.

**Hosts**
- **J289, J292:** fix the buggy hosts, not the silly ones.
- **J366:** a kit package; "engine has fallback boar/bear behavior is bad"; WASM-HOST and HOST-AUDIT move to meta, parked.
- **J367:** five layers, a primitives list, budget tiers, the server derives the host list, no new creatures.

**Authoring and SDK**
- **J154, J170, J317:** the `@wildshard/sdk` package.
- **J161, J168, J342:** templates; the Brasscap repo.
- **J314:** a 7×7 grid and `wildshard new`.
- **J345, J346, J347:** the engine is the deployed MMO; tooling lives in sharddev.
- **J365, J368:** also relevant to authoring and the SDK (details not re-checked this pass).

**Uploads**
- **J306:** upload names versions.
- **J371:** publish actions.
- **J373:** staging is the last row.
- **J379:** async upload with automatic placement.

**Creatures**
- **J104, J107, J108, J109, J117:** boss scaling, respawn, taming into a mount, respawn scaling.

**Camera and look**
- Remote players (J296) and the PS5 bar "GTA5 style PS5 game" (J268 to J270).
- The look loop and its end (J277, J281, J337 "no LUTs"); the 60 fps unlock (J283).
- Doc fact: "There is no third-person body of the player anywhere" (`archive/REMOTE-PLAYERS-PLAN.md`). The game is first person; third-person appears only as PS5-FEEL row PF16 and in the Starwild study.
- 11-08 grill: "A real third-person model is later Opus art work."

**Scope**
- **Q74 (07 grill):** "one server, one grid, one world... dirt simple."
- **J178:** one world, one server.

## 4. Grill quotes (Jake's words)

**Shard source, 11-13**
- **Q3:** "a given shardfile is dynamically loaded by the MMO server and its only data and WASM ; we sandboxed WASM for client & server and there's a WASM HOST V2 plan ffs... they can write as custom of a mini game as is possible within the limits of the WASM Host"
- **Q5:** "it will be done whenever it needs to be done... We already have a partial fucking implementation of wasm host v0/v1/v2 in the engine"
- **Q9:** "remember that anyone can do anything". Three authoring ways are first-class. Q6: mini games are out of scope.

**One format, 11-15**
- "this is bad. the shard format is fore everyone, there's no such thing as first part or third party shard"
- "but this is what the WASM HOST plan in singleplayer is also about right ? i feel like theres stale plans"
- **C-Q2:** "agents can choose one layer at at a time, or whoel create WASM or WASM bosses etc. like it should be flexible right ?"
- **Q-S11:** "no fucking idea out of scope, too complicated, theres so many draft plans in progress"
- **Q-S12:** "Leave this alone right, im so lost. leave it alone, just creatures"
- **Q-T22:** "I dont know what this even means lol... Probably 1 ?"
- **Q-T26:** "you start, ill double check everything myself"
- Skeletons: "2 for now lets reduce scope"
- "lol feels like a lot of scope creep" and "we are just future proofing"
- "the SDK shouldn't be using the engine in the baking pipeline"

**Template content (J357, 11-15 ~13:35)**
- "Mossgate and Brascap definitely need to be pumped full of content. Like, there's no point in having those templates if they don't have the content formula... at least as much content as Dunes and Skyreach... at least have weapons, combat, enemies, stuff, things, NPCs, quests, like the bare minimum."
- About 13:40: "Brass cap didn't [have combat]... No weapons to pick up, no weapons to spawn with, no enemies to shoot."

**Shard compat, 11-13**
- "individual sections / hosts are versioned too." Generators may run arbitrary Node.

**Creatures and players (REMOTE-PLAYERS, 11-12)**
- "it's an MMO, like, we have a placeholder... I need to see them walking... they need a sword... I need to see the attack animation."
- "we should show other players in the minimap."

**Fundamentals (`docs/vision/sources/FUNDAMENTALS.md`, original wording)**
- "a very specific format that the server must be able to load as config without loading arbirtrary code stuff."
- Upload is a ritual of nine beacons with a "30second cool upload animation".

## 5. Ideas

| Source | Idea | Status |
|---|---|---|
| parked/NOVEMBER-IDEAS NI1 | dependency-cruiser | parked |
| NI2/NI3, november-ideas/STARWILD.md | Portrait HUD, third-person camera, no minimap; 10 Hz JSON multiplayer; a 0.8 MB load in 3.7 s against Wildshard's 26 MB; models built in code and streamed over the socket; DPR 1 | parked |
| NI4 | Security and Playwright | parked |
| parked/PS5-FEEL, ps5-feel/PLAYGTA5-TEARDOWN.md | GTA V compiled to WASM and drawn with WebGPU in a tab. Jake on 11-11: "nothing like a browser game". Three habits make it fit: a free main thread, no GC on the hot path, hiding waits behind player choice. What makes it look like GTA is lighting, image chain, animation and vehicles. Rows PF1 to PF21, including PF14 foot IK, PF16 spring-arm third-person camera, PF17 Rapier ray-cast vehicle, PF18 content audit. | parked |
| concept-art/DRAFTS.md, ALPHA-REFRESH.md | A1 "Frontier atlas" and B1 "Emerald and ember" approved 10-11. The alpha refresh keeps six identities and ordinary asphalt highways, and drops the "old glowing lattice" and invented volcano and crystal biomes. | Contradicts VISION.md's lattice and volcanic art direction |
| vision/sources/GAME-REFERENCES.md | Minecraft, BDO, Conan, PUBG, Skyrim, GW2 parkour, BotW. Features: first-person shooting and melee, highway cars, hoverboard, quests, puzzles, titles. Authors make parameterised items, NPCs, scripted quests and cosmetics. Crafting is future. | Historical snapshot (10-11) |
| SHARD-SOURCE SS10a to SS10e | Glowfen, Mirror Salt, Cinder Springs, Kitewind Terraces, with tri and draw counts. A Fable audit raised 6 MUSTs, all fixed. Glowfen is recommended. | Waiting on Jake's pick (SS10e) |
| Open Plots names | alien-plain, clockwork-canyon, coral-drift, sky-race, thin-ice, and others | names only |
| NEW-SHARD-E2E | Honeyknoll: a knoll about 120 m across, a beekeeper's hut, six hives | built |
| custom-creatures audit | Jake's ten: dragon, T-Rex, giant dragonfly, chameleon, angry rabbit, skeleton horse, orc, ogre, troll, mech pilot. Custom share is about 4%. | feeds ONE-FORMAT M5 |

## 6. Where it points (inference)

### Direction

The shard is shrinking to data plus sandboxed WASM, and the engine is turning into a documented library of primitives. ONE-FORMAT is the plan carrying this, but it is creature-first and explicitly avoids world page features and view code. Content (J357) currently outranks format purity: templates get content now, and the format is fixed through creatures.

### Recurring tensions

1. **Generic versus one-user.** Every audit finds that most hosts serve one shard. The fixes were registration, approvals and reframing, not removal.
2. **WASM ambition versus parking.** Jake keeps pointing at WASM v2 as the answer (10-20, 10-24, 11-13 Q3, 11-15 "stale plans"), but no lane has carried it. Meanwhile CC60 in ONE-FORMAT quietly reintroduces "whole-creature WASM from any upload".
3. **Scope fatigue.** "im so lost", "scope creep", "leave it alone, just creatures", "so many draft plans". There are four overlapping format plans (ONE-FORMAT, SHARD-SOURCE, SHARD-COMPAT, SDK-SPLIT), and the "Plan Overlap" board on JAKE-READ-LIST is still unread.
4. **Trust.** The brief bans uploaded WASM; 10-03 allows it. J152 says first-party only; 11-15 says no first party. Gates became dangerousX, then budget tiers.
5. **Art direction.** VISION.md calls for a lattice and volcanic biomes; the approved alpha refresh rejects both. VISION.md also lists "one coherent visual language" against four looks as open.
6. **Camera.** The references are first person, but PS5-FEEL and Starwild point to third person, and the player still has no body.

### Open questions

- Will WASM-HOST be reviewed or retired? ABI v1 retirement and the v1 to v2 rows M1 to M3 are also open.
- HOST-AUDIT rows HA2 to HA7.
- Boss grouping: the proposal has 3 primitives.
- World page features and view code (Q-S11, Q-S12).
- SHARD-COMPAT D1 approval and the Kitchen Sink rewrite.
- The SS10e zone pick.
- The centre shard question (hardcoded, or a 9-cell citadel), still open in VISION.md.

### Not read

- `archive/CUSTOM-CREATURES-PLAN.md`: body only skimmed; I used the audit instead.
- Process and infra plans: progress and goal lines only.
- `host-audit/` subdocs beyond the custom-sections mini-plan and shard-platform rows.
- Git history: only commit counts and grep-matched commit subjects since 11-04 were read.
