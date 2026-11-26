# History: the shard-platform saga in singleplayer

> Moved from meta `docs/prototype-to-mmo/evidence/history-shard-platform-saga.md` at `386423cbea` into the cleanroom saga (D38, 2026-11-26).

> Written by: Claude

> **State:** point-in-time record, 2026-11-16. A read-only study by a research subagent for [STRATEGY.md](../STRATEGY.md), saved as reported. Nothing was built, run or changed. Each study marks what it read in code or docs against what it inferred.

All paths are relative to `/Users/raynos/projects/games/wildshard-singleplayer/`. I read only documents and `git log`, not `progress/` or `art/`. Two limits on the sources. WASM-HOST and HOST-AUDIT were marked "Moved to meta" on 2026-11-15 (commit `8c56c4616b`), so later edits to them are not in this repo. Many of Jake's decision pages are claude.ai artifacts; only the decisions they recorded survive in `docs/plans/decisions.md`. The phrase "as custom as the engine's WASM host allows" does not appear anywhere in this repo.

## 1. Timeline

| Dates | Saga (main file) | Goal | What it left behind |
|---|---|---|---|
| 09-16 → 09-30 | Shard builds and remasters (Driftwood, Nalati, Pine; `project/archive/2026-09-*`) | Polished single-player shards | Shards as trusted TS: Driftwood ~16k lines, Nine ~25.5k |
| 09-25 → 10-01 | GAME-NORMALIZATION (`project/archive/2026-10-01-game-normalization.md`) | Split code into engine · game · kit · shard plugins | `ShardContext` plugins. Decision 67: "Subclasses for behaviour". Decision 57: the API may change if every in-repo shard moves with it |
| 09-30 | engine-fit; `docs/design/mmo/SHARD-PLATFORM-PLAN.md` | Decide whether to adopt a game engine; think about the MMO | "Don't adopt an engine". Proposed devices, a logic graph, look stacks, material graphs, and WASM only as "a small, earned, sandboxed scripting tier" |
| 10-01 → (draft) | WORLDCLAW-SHARD / THIN-ICE / GW2-ZONES | Make building a shard fun | Still drafts at the split |
| 10-03 | ARCH-GUARDS, LAYER-PURITY, MMO-REQUIREMENTS | Lint the layers; write down the MMO constraints | WASM plugins approved; 80/20 split |
| 10-03 → 11-04 | **SHARD-PLATFORM** (`project/archive/2026-11-04-shard-platform.md`) | Make every shard an MMO-compatible shardfile | Every shard at zero custom TS; G1–G1009 decisions |
| 10-10 | Shardfile design system (G290–G319) | Fix the fake generalisation | SDK wrappers deleted; kit dissolved |
| 10-13 | Waves W1–W3 (G403); SHARD-PLATFORM-NEXT split off (G417) | Port component by component | NEXT N1–N8, S1–S22 (never started) |
| 10-16 → 10-17 | Host bar (G454, G481); Wasm ABI v1 (G457, G484) | Stop shard logic leaking into the engine | `docs/HOST-BAR.md`; ABI v1 |
| 10-20 → 11-04 | **WASM-HOST** (`docs/plans/parked/2026-10-20-opus-wasm-host-PLAN.md`) | A batched host for ABI v2 | v2 partly built behind the Developer switch; parked 11-04 |
| 10-21 → 10-24 | Zero (G567, G604) → G693 | Zero custom TS per shard | Ruler deleted 10-24 |
| 10-22 → | **HOST-AUDIT** (`docs/plans/parked/2026-10-22-opus-host-audit-PLAN.md`) | Score every host; fix the "damage" | 114-row inventory; parked |
| 10-24 → | SHARDFILE-NEXT (`docs/plans/SHARDFILE-NEXT.md`) | What a live MMO zone needs from the format | Draft, parked |
| 10-24 → 11-03 | Custom sections (HA7; `docs/plans/MULTI-REPO-SAGA/host-audit/custom-sections-*.md`) | Custom sections to zero | 342 left on 11-03, rows Z0–Z15 |
| 10-27 → 10-30 | Mega build / FINISH-LINE / FOUNDATIONS / BURN-DAMAGE-LIST | Finish every mini plan by any means | Damage list; the graph runtime moved from TSL to compiled GLSL |
| 11-04 → 11-15 | Archive, then the multi-repo split | — | `engine.pin.json` pins an `engine` repo plus `shard-*` repos |

**Dated archive folders in `project/archive/`:**
- `2026-10-01-gw2-zones-council`: GW2-ZONES review.
- `2026-10-02-shard-polish-council`: shard polish review.
- `2026-10-03-mockup-council`: look and mockup review.
- `2026-10-04-shard-platform-council-2`, `-council-3` and `2026-10-07-shard-platform-council-4`: the plan councils.
- `2026-10-10-progress-trailer`: the "building my first MMO" trailer.
- `2026-10-13-shard-platform-side`: kit/commons audit, mockup waves E449/E450, debug inventory, wall-clock plan.
- `2026-10-20-wasm-host-council`: the two v2 rounds.
- `2026-11-04-shard-platform`: history, decisions, the 20+ mini plans and spikes.

The undated folders are `game-normalization/` (specs 00–13), `handoffs/` (E329–E410) and `reviews/`. The dated `.md` files run in order: per-shard plans (09-18 → 09-30), normalization and guards (10-01 → 10-03), then about 60 SHARD-PLATFORM mini plans (10-26 → 11-04): zero, quest-host, mega-build, foundations, QA lists, tile-streaming, CI.

## 2. SHARD-PLATFORM in depth

**Goal, in Jake's words (E431, 10-03):** *"80% data and approved systems … The remaining 20% is custom runtime per shard so we don't have to rewrite everything in one go."* Scope (G41): *"purely to make shardfiles that are MMO & multiplayer compatible, I do not want to build any multiplayer code."* G146 set the end state: *"the runtime is just a temporary hack … eventually everything needs to be … data or assembly script; … take inspiration from … Verse … Luau … I'm happy to build DSLs."*

**Milestones:**
- M1, the package: the template booted from its shardfile on 10-04 (`ed790a281e`).
- M2: the 3 × 3 grid.
- M3: the ports, worked in waves:
  - W1 Sky Reach + Signal Dunes.
  - W2 Pine + Driftwood.
  - W3 Nalati + Nine.
  - Each wave was cut into components C1–C9: static world, looks, effects, creatures, NPCs/quests, items/combat, movers, audio, boot glue.

**What was measured, and how the measure changed:**
- At the council (10-03) every shard was "100–107 % custom" (`history.md` §2).
- Shard folder sizes before the port (`docs/reviews/shardfile-architecture-audit-2026-10-10.md`): Signal 4,248 · Sky 9,452 · Driftwood 16,815 · Pine 19,686 · Nine 20,371 · Nalati 26,807 lines.
- The measure moved four times:
  - Public-SDK share ≥ 80 %.
  - G291: custom TS ≤ 20 % of the frozen legacy folder.
  - G567/G604: zero. *"When we talk about percentage done, it's all about 0."*
  - G693 (10-24), after zero was reached: the ruler itself was deleted.
- On 10-21 the plan read "89,880 of 98,854 cut". The marketing line (`docs/plans/marketing-site/refresh-mini-plan.md` MR6) became *"about 99,000 lines of one-off code down to zero"*.

**What the zero hid:**
- 10-10 audit: in 30 hours, **22,043 lines (81 %) of new platform code had one user**. The port *added* about 17k TS. Jake: *"we just slammed absolutely everything into the game engine."*
- G594 (10-22): about 807 Pine/Driftwood lines sat in one-user TS hosts the ruler could not see.
- HOST-AUDIT's first pass: about 4,570 lines in 49 modules reachable only through one shard (Pine 2,781).
- `game/plugin/*` (13,405 lines) scored 1/6 on the host bar.

**Converting a shard (the documented route):**
- G295/G309 set the order: "data rows first, then a generic SDK system with a second user in mind, AssemblyScript for truly custom logic, `runtime/` last."
- C1 static world became generator-baked tiles. "Generators are not custom code" (G467): *"moving stuff into generators is fucking gg bro."*
- C2 looks moved to look graphs and a shared `post-graph` platform (G599/G600).
- C4/C5 moved to a shared quest host (G532), elite/contracts/herd hosts (G473), a moves library plus spawn-group AS bindings (G457, G484).
- C6 moved to item hosts (G516).
- Per-frame view code went to the WASM view lane (G570).
- AS stayed small: 56 files / 2,791 lines in total (WASM-HOST H13).

**Hosts and sections, start vs end:**

| | Start (council baseline, `history.md`) | End (HOST-AUDIT 10-22 → custom-sections spike 11-03) |
|---|---|---|
| Behaviour code | 13 `CreatureBrain` subclasses, 2 + 4 boss classes, 3 `Weapon` subclasses, 45 function fields in rows, 10 data interactable kinds | 250 modules named as hosts (game 201) |
| Sections and schemas | — | 62 host modules for 63 section kinds; about 300 schema modules in `src/format`; 1,072 platform section rows; **342 custom sections (30.6 MB)** |
| Platform size | — | engine 100.8k, game 94.6k, format 19.2k, sdk 12.1k lines |

**Councils:** four councils, 215 + 98 + 64 + 53 findings. They objected to how precise the measures and gates were, not to the direction. Examples:
- R1-A15: "80/20 can be declared while gameplay stays browser-only".
- R1-B5: "AS counts as custom".
- R1-A8: "Build-time fuel isn't admission enforcement".
- Council 4: M2-ready reporting.

**Deferred at the archive (CO8 table):**
- SHARD-PLATFORM-NEXT: N2 (delete the hybrid host), N4 (quality pass), N5 (delete the plugin scaffolding), N6 (permanent architecture docs), N7 (untrusted-shardfile hardening), S19 (outside-author trial).
- HOST-AUDIT HA0–HA8.
- WASM-HOST (S9 benchmark folded into H0).
- Nalati's grid-ready "closed unreachable" (G828).

## 3. The WASM story

1. **The ban, and lifting it.** VISION's binding brief: *"never accept uploaded arbitrary executable code, JavaScript, TypeScript, WASM"*. The 09-30 design said WASM is "not the default for everything". On 10-03 Jake decided *"WASM plugins are approved systems"* (`MMO-REQUIREMENTS.md` decision 5).
2. **Why AssemblyScript.** It was picked in E435 ("O4 reversed from Rust first"). The recorded evidence: *"about JIT speed, 5–9 KB modules, a compiler that runs inside Node, fuel metering and exact memory caps on V8 and JavaScriptCore, bit-identical maths."* G48 adds: *"identical results everywhere only for scripts (AssemblyScript gives that for free)."* G309 kept it on 10-10: "fast, deterministic, already built and pinned."
3. **v0 (from 10-04, `17541e6790` SF11a).** A raw numeric protocol: `in_ptr/out_ptr`, `env.query`, `on_tick`. Used by ScriptLane, client scripts, DirectorLane and movers, with a "three-copy 24 MB" memory policy. The design system graded director AS written "against raw memory offsets (`load<f64>(16384+i*8)`). Readability is F."
4. **v1 (10-16/17, W1 spike; G453, G454, G457, G484).**
   - Why: G453(1), *"Simulation never lives in `runtime/`"*, needed a server-runnable path, and v0 was unreadable.
   - What it added (`docs/SCRIPT-ABI.md`): typed reads and lists, events, commands checked against authority, declared durable slots, bindings and spawn groups.
   - Limits: event-driven at about 10 Hz, ≤ 64 binding calls per tick, 32 commands per call, fixed memory of 1–4 × 64 KiB with `memory.grow` refused, memory rewound every call.
   - G454(7): *"Wasm runs decisions only … per-frame work stays in engine mechanics."*
   - G503 (10-18) pulled Pine's per-frame stag walk back to 10 Hz, "no exceptions".
5. **v2 (WASM-HOST, 10-20).** Jake took it off the builder (G517): *"I don't want to fuck around the builder with changing the assembly script engine … if we're going to fix it, we should fix it properly."*
   - **Three lanes plus bake:**
     - sim `ws_step`: fixed tick, 10 Hz (30 Hz with a written reason), saved.
     - project `ws_project`: synchronous, stateless projections.
     - view `ws_view`: display rate, client-only, memory kept between frames.
   - **What v2 lets a script do that v1 cannot:**
     - One batched entry per module per tick, with no JS calls inside guest code (fuel becomes an internal global).
     - A host-written observation block with input edges stamped to the 60 Hz tick.
     - A request ring for ray/path/overlap queries.
     - Per-frame visual code (H9) and a view-target adapter for instanced figures, bones and look values.
     - Combo transition tables applied by the 60 Hz host.
     - "MMO-ready" per-player observation rows (W13).
   - **Built 10-21 → 10-23, behind the Developer switch:** wire contract `5c706107f9`, metering/admission `944241477a`, view-lane host `3bd42fb3c4`, observations, queries, height grids, Driftwood bridge sway, Nalati Titan and pasture modules.
   - **Not done:** the H13 cutover. v0, v1 and v2 all coexist.
   - The H4 group sections that grew into SCRIPT-ABI v2 (about lines 880–1358) mostly "borrow original native" contexts, RNG streams and steering so legacy Nalati code ports byte-for-byte.
6. **Budgets and evidence.**
   - Fuel: 400,000 per call, 2,000,000 per tick (ceilings 2M and 8M), "ceilings from scenario traces" (G457(3)).
   - The plan's own diagnosis of the fuel price: `bytes*4 + 128*functions + 1024` per loop iteration, so Pine's `life` module "pays 32,064 per iteration … about 12 iterations fit in a 400k call" — "That, not JS speed, is why integrators are refused today."
   - The AS line budget was ≤ 10 % of legacy lines (G454(8)).
   - The v2 target was ≤ 1 ms per frame for 20 bindings on the phone (W12). The H0 benchmark (`b6d309d7e6`) was built, but **no result is recorded** in this repo.
7. **Where it is supposed to end up (clearest statements).**
   - Jake, 10-20: *"to beef up what can be done with WASM to make it more performant, to unlock new capabilities so that other shards going forward have more capabilities"*; *"once you enter the WASM, it shouldn't be going back into JavaScript"*; *"long term we want to run assembly code at 60 hertz or 30 hertz."*
   - The plan's Why: *"New shards should be data plus AS with no TypeScript, including combat feel and motion."*
   - The counter-statement four days earlier, G453(4): shard-unique behaviour goes to *"platform hosts driven by data first, AssemblyScript Wasm only for the genuinely one-off."*
   - Last word, G1009 (11-04): *"Wasm host, we're not working on that."*

## 4. Generalisation attempts

| Attempt | What happened | Recorded reason |
|---|---|---|
| Devices + logic graph (09-30 plan §6.1, like Fortnite or LittleBigPlanet) | Never built as such. G9 chose "entity scripts + a shard director". Directors became stage-machine rows with a bounded `when` boolean language (design-system §4.1; `ENGINE.md` "directorWhen") | Not stated. *Inference:* AS scripts took the logic graph's role |
| "The kit becomes the SDK" (T6, G135) | Kit dissolved (SF54). The SDK grew about 193 `export const X = Y` facades, deleted by G307 | *"the design of the SDK was completely misinterpreted … this wrapper SDK around the game package"* |
| `game/systems/*` "generic" systems (10-09) | 81 % had one user; moved back (G303); rule of two (G294); the template doesn't count as a second user (G312) | "relocation, not generalisation" |
| Five shared systems: directors, 13 → 5 brain archetypes, movers, player modes, weapon rows (G319) | Approved 10-10, superseded by the zero target (G604) | — |
| Platform features "from day one" with a fixture as second user: contracts, elites, quest step runner, riding, grapple (G473–G478) | Built. G520 re-scored the fixture-backed growth; 14 of 31 self-scored hosts were "too high" (G496) | *"We got rid of 800 shard specific code. We've got 1800 engine code, so nothing is free"* (G481) |
| One host register (HA5) | Planned, not built | Five drifting lists, "no single register" |
| Custom sections | Allowed with a shrink-only ratchet on 10-16 (G453(3); `feat(sdk): define custom product sections`). Became 387, then 342 | E498: *"Those are absolutely horrible … We should be having one generic format for everything, and some of those custom sections may have to be evicted to WASM"* |
| Material/look graphs (G4, G306, SF59) | The graph format stayed. The TSL runtime cost "76 % more" per draw on Nine and was replaced by a compiled-GLSL back-end (NF13–NF18) | Performance. Hand-written GLSL was ported *to* graph nodes (G595(2)) |
| Tags (SHARDFILE-NEXT E) | Draft | "instead of a new section per mechanic" |

**Where a specific path was chosen over a general one:**
- Elites became "a generic engine feature" — *"Jake's pick over the WASM recommendation"* (G600 L4).
- Mover kernels became "an engine mover mechanic … no Wasm runs per frame" (G457(6)).
- The Blender island loader became a native host with one user (G586).
- Jake asked *"how to get pinewood to 20% or less without assembly script"* (G474).
- Riding and grapple stay game hosts (G478, G599).

**Where a specific mechanic became general:**
- The strike-targets host is shared by Sky's gust and Signal's lash (G457(2)).
- One quest host replaced two (G532).
- The cell field (G600 L3) and the post-graph look (G599 N1) were also generalised.

## 5. Recurring pain (Jake's words)

- **Speed and being stuck:**
  - *"I'm so sick of being stuck on this project for 3 weeks"* (G596).
  - *"I feel the circling the drain … we also need to stop jerking the builder around"* (G466).
  - *"Go fast as fuck. And then deal with the damage later"* (G769). The mega build measured "~0.19 counted rows per lane-hour"; the push gate was red on 51 of 72 ticks.
- **Engine damage:**
  - *"I'm really, really worried that we just punched the engine in the face"* (G481).
  - The host bar's purpose: *"the engine is supposed to be very flexible and not have all kinds of random Sky specific and Dune specific if statements in them."*
- **Hosts:**
  - *"How do you decide if the platform/engine hosts we build are good or silly … are we moving basically shard specific logic into the engine … Should it be generic based on WASM + ASM instead?"* (G454).
  - *"One shard hosts are approved by me one by one"* (G595).
- **The format:** the custom-sections quote above (E498, 10-24). On 11-03: *"they all have to be generic, high-quality hosts in the engine."*
- **Cheating the measure:** *"converted into data or WASM in the correct way … without cheating"* (G571).
- **Authoring quality:**
  - *"the current worlds need so much polish it feels like slop"* (WorldClaw, 10-01).
  - G302: generators must be readable, *"never procedural soup."*
- **Process weight:** "Finish to the spirit, trash the process" (G416). The phrase "ceremony porn" also appears (JAKE.md).
- **What he asked for each time:** generic hosts, one format, data or WASM, honest numbers, and less ceremony.

## 6. Where it points

**What the documents say directly:**
- The stated architecture since 10-16 is "engine mechanics + data rows + per-shard Wasm decisions" with "Host APIs take data only; per-shard hooks are Wasm script references, never TS callbacks" (G454(4)–(5), HOST-BAR test 6).
- G453(5): *"No dynamic JS loader, ever"* — a shard becomes loadable "by losing its `runtime/`".

**What I infer (not stated anywhere):**
- Each time the measure was satisfied, the one-off logic moved down a layer rather than going away:
  - First from shard TS into `game/systems`.
  - Then into one-user hosts.
  - Then into private data schemas (342 custom sections, about 300 format schema modules).
- The direction held from 10-03 to 11-04: trusted TS → declared data read by engine hosts → a sandboxed AS layer that keeps widening (v0 → v1 at 10 Hz decisions only → v2 with per-frame view, observations, queries).
- Every remedy so far was a *bar* (rule of two, the host bar, Jake's per-host approvals), not a smaller set of primitives.
- The WASM layer is the only part that kept gaining reach: G454(7) "decisions only" was reversed by the view lane within four days.
- Yet AS is only ~2.8k lines, about 3 % of the original ~99k. The conversion went almost entirely into hosts and data, and new content (OPEN-PLOTS, THIN-ICE, GW2-ZONES) does not mention WASM at all.
- v2's "borrow original native" contracts suggest the ABI was being shaped to fit legacy code rather than primitives.

**Questions left explicitly open at the 11-04 split:**
- WASM-HOST: the H13 cutover (W5: "v2 replaces v1 and v0 in one go"); the H0 phone numbers; threads (H15, W11); deterministic physics (H16).
- HOST-AUDIT: ruler fix (HA0), scores (HA2), the one register (HA5); Jake's per-host approvals were never applied.
- Custom sections: rows Z0–Z15 (about 45 lane-days).
- SHARD-PLATFORM-NEXT: N2/N5 (delete the hybrid host and plugin scaffolding), N6 (permanent architecture docs), N7 (untrusted hardening before any outside author), S19 (outside-author trial).
- SHARDFILE-NEXT: Q1 (where the player record lives); tags and `tagged()` reads "agreed with WASM-HOST"; `intents` (typed player requests); the server-only cut.
- Format back-compat: G453(6) "No format back-compat … revisit for the MMO".
- Whether a logic/DSL layer exists between rows and AS. G146 welcomed one; it was never decided.
