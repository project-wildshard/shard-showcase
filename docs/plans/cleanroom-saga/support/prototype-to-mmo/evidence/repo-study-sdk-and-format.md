# Repo study: the SDK, CLI and shard format

> Moved from meta `docs/prototype-to-mmo/evidence/repo-study-sdk-and-format.md` at `386423cbea` into the cleanroom saga (D38, 2026-11-26).

> Written by: Claude

> **State:** point-in-time record, 2026-11-16. A read-only study by a research subagent for [STRATEGY.md](../STRATEGY.md). Scope: `wildshard/sharddev`, `shard-format`, `repo-kit` and `shard-templates`. Nothing was built, run or changed. The claims the strategy leans on hardest were re-read in the source by the lead agent; they are listed in the folder [README](../README.md).

I read these repos without changing anything. I didn't run the CLI, builds or tests. The engine is outside the four repos, so I only grepped it briefly where noted.

## Wildshard authoring toolchain today (read-only study, 2026-11-16)

### 1. What a shard is in the format

**Checked in code:**
- **The file.** A shard file is a strict tar of `shard.json` (the index) plus `sections/<name>.json` and assets referenced by hash. The contract is a set of valibot schemas: `ShardfileSchema` in `shard-format/src/format/shardSchema.ts` (678 lines), across 383 non-test modules in `src/format`. Format version is `0.1.0.1` (`version.ts`); the package is at v0.12.0.
- **What it can say.** `docs/RUNTIME-CONTRACT.md` (489 lines) has generated tables, with a test that keeps them in step with the code:
  - 72 section names, all `@1`, and "There are no custom sections".
  - 63 `client/plan` kinds, 18 world-assembly stages, 46 server hosts and 94 named-file families.
  - Coverage includes terrain, tiles, props, look, lights, sky, water, weather, audio, creatures, species, spawns, encounters, quests, NPCs, items, loot, ledger, UI, movers, portals and player modes (zipline, ladder, ride, grapple).
- **Shard type.** There is no field for first-person vs third-person, and no camera-mode field. Searching all four repos found only first-person arms (`heldView.ts`) and weapon documents such as `weapons/rifle-page.json`. The engine's level spec has only a first-person-hands option. A first-person shooter shard is therefore expressible as held-weapon rows, but nothing declares a "type".
- **HUD.** HUD is owned by the platform. `ui.ts` (90 lines) allows only five kinds (`marker`, `counter`, `bagPanel`, `bossPanel`, `relabel`), at most 64 of them: "plain data the platform draws in its own HUD style". The lint rule `lint-no-raw-hud` refuses custom HUD. So "normalise the HUD" means throwing the prototype's HUD away rather than converting it.

**Can a shard carry its own code? Only sandboxed Wasm compiled from AssemblyScript, never JS/TS.**
- RUNTIME-CONTRACT.md line 8 says "A shard is data… never carries code that engine imports."
- `runtime.ts` (38 lines) allows only `kind: 'client-plan'`; "LD9 retired the copied-runtime `entry` arm".
- Scripts run in a few places: `sim/scripts` (ABI v1, run on the server), `actors/return-scripts`, `actors/spawn-scripts`, `view/modules`, and ABI v2 lanes, which are only partly built and sit behind a Developer flag.
- v1 limits (SCRIPT-ABI.md, 1,408 lines):
  - decisions run at about 10 Hz;
  - at most 32 commands and 16 events per call, 400k fuel per call;
  - 1–4 pages of 64 KiB memory, which is reset before every call;
  - at most 16 saved state slots.
- The command whitelist is: move, strike, stop, field, spawn, despawn, flag, timer, signal, grant, reward, cue, channel, encounter. `impulse` and `weather` are refused when the shard is installed.

**Could it express the looping train that carries players and teleports between tunnels? Not as the format stands today.**
- **Movers** (`movers.ts` 224 lines, `moverMotion.ts` 271): at most 32 movers. A `track` has at most **10 keyframes** with `loop: 'repeat'`, and coordinates are limited to ±250 m.
- **`carry`** (riding a mover) is accepted only when `kind === 'channel'`, the driver is a `winch` in `ride` mode, return is `'command'` and there is no gate. In practice that is a seated ride between two `landings`, each with an interaction prompt, not a free-standing platform that players stand on while it loops.
- SCRIPT-ABI says outright: "There is no `mover` command." It also has no teleport command.
- **Portals** (`portalLink.ts`): fixed road → destination → exit nodes, "no URL, author callback or arbitrary teleport target". `portalRide.ts` is a fade-and-veil transition to fixed landings.
- **Multiplayer gaps in v1:** `playersInZone` returns "0 or 1 for the single local player" and `player.join` "does not prove multiplayer joins".
- **Scene shards:** `scene/lower.ts:169` refuses spin and bob because they "need moving parts: an engine row after M2".
- Every new mechanic so far has meant a new format row plus engine support. The last five shard-format releases (v0.8 to v0.12, all dated 2026-11-16) each warn: "Shards using these fields need an engine that implements them."

### 2. Where the lines go

These are lines in tracked code-language files (ts, mjs, js, py, sh, as). They match your stated totals.

| Repo | Code-lang lines | Tests | Main areas |
|---|---|---|---|
| shard-format | 124,509 | 17% | `src/format` 72,790 (63,216 product / 9,574 test); `packages/wire` 33,318, which is the `@wildshard/wire` netcode codec, not the shard format; scripts 4,715; githooks 2,947; tools 2,592; ci 2,462; CLI 963 |
| sharddev | 113,908 | 34% | `src/sharddev` 40,347 (26,742 / 13,605); `test/` 12,602; scripts 12,713, plus music 5,373, img2mesh 4,466, practice 2,282 and blender 623; `src/shards` (templates) 7,506; `src/cli` 7,185; drafts 4,077 |
| repo-kit | 37,063 | 43% | Almost all process: hooks, land/worktree/release scripts, disk tooling |

- **shard-format beyond code:** 5,653 lines of docs and about 33k lines of art binaries.
- **sharddev beyond code:** about 80k lines of generated sfx JSON under `scripts/music`.
- **repo-kit by category (all files):** gates and process tooling 31%, tests 27%, product code 19%, journals and agent files 11%.
- **Rough split of all tracked lines:**
  - shard-format: about 42% product code, 9% tests, 7% hooks/agents/process.
  - sharddev: 25% product code, 15% tests, 8% process.

### 3. The CLI

**Checked in `bin/wildshard.mjs` and `src/cli/main.ts`:** the verbs are `new`, `update`, `check`, `synth`, `build`, `validate`, `prove`, `dev`, `watch`, `schema`, `prepare`, `hero`, `build-shards`, `grid`, `content`, `serve`, `pack` (deprecated), `upload`, `account`, `whoami` and `delete`.
- There is **no `import`, `adopt`, `port`, `ingest`, `publish` or `init`**. `new` (alias `init`) only copies a template.
- glTF loading exists only inside the bake (`bake/glb.ts`). The skill `wildshard-mockup-to-model` imports one GLB at a time by its SHA-256.

**The documented path from prototype to live** (`GUIDE.md` §1 and "Uploading", 1,102 lines):
1. `new --template scene`
2. Port the prototype by hand into `defineShard`
3. `check` (lint, build, validate, prove, report card)
4. `dev` and `hero` together, then look at the images
5. Commit
6. `check` again
7. `prepare` (records the shard in phone WebKit using a fetched ~310 MB client)
8. `build <folder>`
9. `account` / `whoami`
10. `upload --channel staging`
11. The Wildshard team places the shard on the grid ("Only the Wildshard team places a shard"; automatic placement "is built but switched off")
12. Upload again to prod with a new version and a new hero (J306)

That is 10 to 12 steps. The share link is "Not built yet (SA36, SA37)".

**What gates block it:** 122 refusal rules in GUIDE §6, of which 50 are lint rules, plus 53 shard-format validation codes, budgets, the hero being stale or unchanged, and a clean git tree.

**Inconsistencies in the guide:** the step table says upload "works only for the Wildshard team today: it needs the team's creator key". Step 5 of the same guide describes a self-serve `wildshard account` key.

**The closest thing to a prototype import is the scene shard** (`src/sharddev/scene/`, 2,848 lines):
- `defineShard(identity, world => …)` takes real three.js at build time.
- The world API is: `part`, `ground`, `sky`, `post`, `spawn`, `trigger`, `interact`, `detail`.
- Motion is cosmetic only: `flicker`, `pulse`, `drift`, `rise`, `sway`, `uvScroll`.
- The build refuses `ShaderMaterial`, `onBeforeCompile`, SpotLight, multi-material meshes, lines and canvas textures.
- Gameplay goes in through `extend: (shard) => ({...shard, quests…})`, which means hand-written format rows.

**One real precedent, outside the four repos:** `shard-brasscap/src/shard.config.ts` is "three.js scene source (… brasscap-cleanroom e311139 on the sdk's scene API)", with gameplay in hand-authored `rows/*.json` and `sources/gate.as`. The journal `sharddev/project/journal/2026-11-13-mossgate-cleanroom.md` describes an earlier cleanroom port done by agent lanes. Both were manual agent work, not a single command.

### 4. The "zone authoring guide"

- **The shipped one** is `sharddev/GUIDE.md` (1,102 lines, "The shard author's guide"). It ships in the npm package and `new`/`update` copy it into every repo.
- **Four skills ship with it** (208 lines in total): `wildshard` (the loop), `wildshard-mockup-to-model`, `wildshard-goldens` and `wildshard-upgrade`.
- **The `AGENTS.md` that `new` writes** (`agentFiles.ts`) says: read GUIDE.md first, the skills are in `.claude/skills/`.
- **What they tell an agent:** a loop of steps, each with a "Done when"; fix refusals using the `GUIDE.md#anchor` each one points to; take every number from `check --json`.
- **What none of them cover:** porting a standalone prototype, adding MMO quests or collectibles, or matching the MMO's HUD.

**Where the docs disagree with the code:**
- `shard-format/docs/SHARDFILE.md:1656` "Checked authoring guide (SF86)" points to `api/SDK.md` and `pnpm docs`. Neither exists in either repo; the links are left over from the singleplayer import.
- `sharddev/scripts/docs/authoring-guide.md` (307 lines) is excluded from the npm package (`!scripts/docs`).
- GUIDE §2 teaches the **v0** script prelude (`on_tick`, `abi_version`, `in_ptr`, …). SCRIPT-ABI calls v0 legacy, "retired per shard".
- GUIDE says npm install works from 0.3. `scripts/docs/standalone-author.md` says it fails until NP7.
- Format docs claim "~320 modules"; there are 383.

### 5. repo-kit and shard-templates

- **shard-templates** is a scaffold only: 76 files, 490 lines of code (a stub CLI), last commit 2026-11-13. Its "Coming with the import" list never arrived. `repo-kit/consumers.json` says it is "retired, its GitHub repo is gone". The real templates live in `sharddev/src/shards`:
  - `_template`: 77 files, 12,935 lines
  - `mossgate` (the scene template): 6 files, 1,356 lines
  - also `authoring-slice`, `ink-cel-valley` and `pastel-plain`
- **repo-kit** stamps 85 files (8,900 lines) into 15 consumer repos: git hooks, `.claude`/`.agents`, lint and format configs, `land`/`worktree` scripts, CI and a publish workflow.
- **Two very different starting points for a new shard:**
  - An outside author's repo from `wildshard new` is light: package.json, tsconfig, README, GUIDE, 4 skills, AGENTS/CLAUDE, plus the template.
  - A first-party shard repo carries much more. shard-brasscap has 238 files, of which about 13.6k lines are kit/process (hooks, agents, kit, scripts, journals, CI) next to about 50k lines in `src`.

### 6. Complexity and health signals

- **Versions:**
  - Script ABI: v0 (legacy, still used), v1 (shipped) and v2 (only partly built).
  - Format: three accepted spellings (`0.1`, `0.1.0.0`, `0.1.0.1`). Prepared shard files are `sdk "0.2"` (drafts / legacy) or `"0.3"` (needs `cook.json`).
  - Release pace: shard-format went v0.4.8 → v0.12.0 in 4 days, while sharddev pins `shard-format@0.7.0`.
- **`migrations.ts`** covers saved-state migration only. SCRIPT-ABI says restore "requires exact stateVersion; it does not run those migrations".
- **Legacy markers:** 42 non-test format modules mention "legacy". There is a Pine grandfather exemption (`script-side-grandfather.ts`), the retired `--template blender`, the deprecated `pack`, and the stale singleplayer links.
- **Other gaps the docs state:**
  - memory caps are report-only;
  - proof tapes can fail in the engine's save step through no fault of the author;
  - share links are not built;
  - automatic grid placement is switched off.
- **Duplication:** the 25 module names shared by format and sharddev are mostly thin wrappers that import from format (for example, sharddev `movers.ts` is 75 lines and imports format). One real copy exists: `runtime-hosts.json` is maintained by hand from engine tables, and the docs admit the gap.
- **Activity over the last two weeks:** sharddev 441 commits (template content, scene API, release, CI port tests); shard-format 313 (additive feature rows); repo-kit 309 (release, disk and publish tooling). The direction is "authoring as easy as the cleanroom" (J339, the scene front end), alongside a lot of process tooling.

### For and against "upload my prototype"

**For:**
- three.js scene source is now a first-class shard source.
- `watch` hot-swaps edits in about 0.9 s.
- Brasscap shows a canyon cleanroom ported onto the scene API.
- HUD, quests, items and UI are platform-owned data, so they come out uniform.
- Refusals are machine-readable and point to the guide, which suits an agent.

**Against:**
- There is no ingest, port or "stamp MMO features" command.
- Prototype gameplay JS cannot ship; it has to be rewritten as rows plus AssemblyScript within tight v1 limits.
- Movers are limited to 10 keyframes, with carry only as a two-landing winch ride, no teleport primitive and no mover command, so the looping, teleporting train needs new format and engine work.
- There is no shard-type or camera field.
- There is no guide for porting a prototype or adding MMO quests or collectibles, and the cited SDK authoring guide doesn't exist.
- The path to live is 10 to 12 gated steps, and the final grid placement depends on the Wildshard team.
