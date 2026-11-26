# Prototype to MMO: an engine of primitives

> Moved from meta `docs/prototype-to-mmo/README.md` at `386423cbea` into the cleanroom saga (D38, 2026-11-26).

> Written by: Claude

> **State:** draft, parked, 2026-11-16. A new, separate line of thinking. Nothing here is scheduled or being built.

## What this folder is

On 2026-11-16 Jake recorded what he wants from Wildshard: vibe-code a standalone three.js prototype of a zone in an hour, then spend a second hour telling the CLI to upload it into the MMO with the MMO's features added.

The first strategy written here answered that for one zone (a canyon train) with trusted TypeScript shards. Jake rejected it the same day. The real question is bigger: how the engine becomes capable enough for a hundred very different ideas, out of a small set of composable primitives, without a section and a host per idea, and with every upload staying data plus sandboxed WebAssembly.

This folder holds an outside agent's reading of Jake's four notes, studies of the repos and of both sagas' plan history, research into what other platforms did, and a strategy.

**What it is not** (Jake, 2026-11-16: "a brand new saga"; "far too early to be planning"):

- It is not part of the multi-repo plan or the shard-platform plan.
- It is not a build plan. It has no lanes and no J-numbers. Since 2026-11-22 a short parked plan, [PROTOTYPE-TO-MMO-PLAN.md](../../2026-11-22-fable-prototype-to-mmo-PLAN.md), points here so the idea isn't lost (Jake: "otherwise ill lose it"); its seven coarse rows all wait for him.
- It has no entries in `STATE.md`, the QA-FEEDBACK files or `MACHINES.md`, on purpose.
- It decides nothing. Where the strategy would change the aim of an existing plan it says so and leaves the call to Jake.

Its shape copies singleplayer's `docs/plans/GW2-ZONES.md`: one main document with its evidence next to it.

## What's in it

| File | What it is |
|---|---|
| [STRATEGY.md](STRATEGY.md) | The main document. One-page summary first; then how the one-off code kept moving into the engine, why, the primitives, the script layer, the format, a way there, and five questions for Jake |
| [IDEAS.md](IDEAS.md) | Thirty-seven zone ideas (Jake's sixteen and twenty-one more), each with the primitives it leans on, and the count across them |
| [BRAINSTORM.md](BRAINSTORM.md) | Options weighed: six answers to where gameplay lives (including the rejected first strategy), open design choices, what a shared library might hold, draft prototype conventions |

**Evidence, second round** (the engine and the history):

| File | What it is |
|---|---|
| [evidence/2026-11-16-voice-notes.md](evidence/2026-11-16-voice-notes.md) | Jake's four notes: the vision, where this lives, the correction, and the pointer to the existing sandbox and history |
| [evidence/inventory-sections-hosts-scripts.md](evidence/inventory-sections-hosts-scripts.md) | Every section, page kind and server host, sorted into primitive, mechanic, platform or tooling; the three script interfaces; what a new mechanic costs |
| [evidence/engine-internals.md](evidence/engine-internals.md) | The engine's world model, physics, replication, hosts, creature brains and rendering |
| [evidence/prior-design-and-scene-side.md](evidence/prior-design-and-scene-side.md) | Earlier design thinking (the 3 October audits, the language choice), the SDK's scene front end, the showcase plans |
| [evidence/history-shard-platform-saga.md](evidence/history-shard-platform-saga.md) | Singleplayer's shard-platform saga: timeline, the WebAssembly story, generalising attempts, Jake's recurring complaints |
| [evidence/history-multi-repo-saga.md](evidence/history-multi-repo-saga.md) | Meta's plans, live, parked and archived, on format, hosts and scripts; related decisions and grill quotes |
| [evidence/precedents-primitives-research.md](evidence/precedents-primitives-research.md) | Roblox, Second Life, Fortnite's Scene Graph, Decentraland, VRChat, Unreal's ability system, Overwatch's Statescript, sandbox costs; with sources |

**Evidence, first round** (made for the rejected strategy; the facts still hold, the framing is the train):

| File | What it is |
|---|---|
| [evidence/repo-study-engine.md](evidence/repo-study-engine.md) | The engine measured against the train |
| [evidence/repo-study-sdk-and-format.md](evidence/repo-study-sdk-and-format.md) | The CLI, the author guide and what a shard file can express |
| [evidence/repo-study-shards-and-cleanrooms.md](evidence/repo-study-shards-and-cleanrooms.md) | The nine shards, and how the two clean-rooms became shards |
| [evidence/repo-study-meta-site-api.md](evidence/repo-study-meta-site-api.md) | The written vision and plans, the public site's promises, and the API |
| [evidence/precedents-research.md](evidence/precedents-research.md) | User-content platforms, trains in multiplayer, sandboxing, scope failures; with sources |

## How it was made, and how far to trust it

- **Read only.** No repo was built, run, tested or changed, and the live game wasn't played.
- **The studies were done by subagents**, each five to ten minutes of reading. Their reports are saved as written. Each marks what it read in code or docs against what it inferred.
- **The bucket counts are one agent's judgement.** Whether a section or host is a "primitive" or a "mechanic" was decided row by row; the rows are in the inventory file.
- **The lead agent re-read these in source**, because the strategy leans on them:
  - `shard-format/src/format/scriptActionsV2.ts`: the taming operations 26 to 37 in the v2 script interface.
  - `engine/src/server/game/shardfile/nativeAssemblyHosts.ts`: 46 cases in the server host switch.
  - `sharddev/src/commons/scripts/`: three AssemblyScript files, 91 lines.
  - `sharddev/src/sharddev/bake/compileScript.ts`: the fuel formula.
  - The sizes of the ladder, zipline, grapple, riding and creature-brain files in `engine/src`.
  - `docs/plans/parked/2026-10-20-opus-wasm-host-PLAN.md`, `docs/audits/2026-11-15-one-format-audit.md` and singleplayer's `docs/design/mmo/research/e435/plan-audit-claude.md`: the quotes used.
  - From the first round: `CharacterMotor.carry()` (a jump of more than 1.5 m ends a ride), the 500 m cell, mover limits, and J339 to J381 in `MULTI-REPO-PLAN.md`.
- **Everything else is as the subagents reported it.**
- **One web page in the first round of research carried an embedded instruction** to discuss an unrelated topic. It was ignored, and nothing from that page is used.

## If this is picked up

Start with the one-page summary in [STRATEGY.md](STRATEGY.md), then its section 12: five questions only Jake can answer. The first move it suggests is to take the WebAssembly host plan off the shelf with a changed aim. That would be Jake's decision; nothing here starts it.
