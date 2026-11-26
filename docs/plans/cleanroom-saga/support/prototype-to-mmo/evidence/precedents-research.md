# Research: precedents for creator-made zones in a shared host

> Moved from meta `docs/prototype-to-mmo/evidence/precedents-research.md` at `386423cbea` into the cleanroom saga (D38, 2026-11-26).

> Written by: Claude

> **State:** point-in-time record, 2026-11-16. Web research by a research subagent for [STRATEGY.md](../STRATEGY.md), with source URLs at the end. Claims from memory or that could not be confirmed are marked in the text; the strategy does not use them.

## Precedents for creator-made zones inside a shared MMO host

Note: one search result contained an embedded instruction to discuss an unrelated topic ("broken sword incidents"). It came from a web page, not from you, and I ignored it.

Claims marked **[memory]** are from my own knowledge, not a page I fetched. Claims marked **[unverified]** are ones I looked for and could not confirm.

## 1. Platforms: the contract between creator code and host

**Roblox (thick host, real code).**
- The platform owns the server, replication, avatar, default HUD and persistence. Experiences are "multiplayer by default"; the server "is the ultimate authority"; and the data model, physics and chat replicate automatically.
- The creator writes Luau and must explicitly handle the three cross-boundary flows (client to server, server to one client, server to all).
- The default HUD (player list, health bar, backpack, chat, emotes) is on unless switched off with `SetCoreGuiEnabled`.
- DataStores are "consistent per game, so any place in a game can access and change the same data", which is the closest precedent for shared progress across zones.
- TeleportService details are **[memory]**; I did not fetch that page.
- Lesson: creators accept a thick host when it removes netcode, accounts and saving entirely.

**Decentraland SDK7 (fixed parcels, sandboxed scene).**
- A scene is a JS program in "an isolated runtime environment" with `onStart()` and `onUpdate(dt)`.
- It has no DOM or `window`. It talks to the renderer only by exchanging CRDT component messages, and HTTP access needs a player-granted permission.
- Nothing in the environment is synced by default; the creator opts entities in with `syncEntity()`.
- State "is not persisted when all players leave", and an authoritative server is "strongly recommended when players have incentives to exploit".
- Which engine hosts the runtime is **[unverified]**: older docs say Web Worker, community pages say QuickJS, and the ADR names neither.
- Lesson: sandboxing forces the host to own rendering, so the SDK becomes thick and creators cannot use raw three.js.

**Second Life (256 x 256 m regions).**
- Each region is "hosted by a single simulator process", almost exactly the shard idea.
- Region crossings remain a chronic problem: vehicles arrive before their seated avatars, scripts halt on handoff, and failures rise with passenger count.
- Lesson: never let gameplay straddle a zone boundary. Your tunnel teleport is the right instinct.

**Fortnite Creative / UEFN.**
- The host owns the character, health, inventory, weapons and movement. A third-party blog puts it as "you're modifying Fortnite's character, not building your own". Epic's docs do not state the limits directly.
- Creators report that some functions exist only as devices, and that moving props from Verse stutters.
- Despite the lock-down, Epic reported 11.2 billion hours across about 260,000 UEFN islands, over $1 billion paid out since 2023, and creator islands at 36.5% of playtime in 2024 (figures via secondary press).
- Lesson: a locked character and HUD does not stop content. Distribution and payouts drive supply.

**Discord Activities and portal SDKs (thinnest hosts).**
- Discord: the game runs in an iframe, and the SDK wraps a `postMessage` protocol for identity and auth. The game, backend and netcode stay with the developer.
- Poki: a handful of lifecycle calls (`gameLoadingFinished`, `gameplayStart`, `gameplayStop`, `commercialBreak`, `getUser`, `login`), plus a rule that events never fire twice in a row.
- Lesson: an "arbitrary game with platform services wrapped around it" works when the contract is lifecycle events plus identity, not gameplay.

**Hytopia (closest technical analogue).**
- The developer writes TypeScript game code. The platform ships the compiled server and the client, and handles "networking, prediction, entity lifecycle, physics", in a "100% server-authoritative setup", with hosting included.
- The "AI-first" positioning is **[unverified]**; the README does not mention it.

**Hytale.**
- Mods are server-side only: "we don't intend to support any client mods", to avoid every server needing a different client.
- It also rejects text scripting in favour of visual scripting, the opposite of what suits coding agents.

**One-liners.**

| Platform | Outcome or contract |
|---|---|
| Core (Manticore) | Raised about $145M, UE4, 50% revenue share, reportedly 20,000+ user-made games at launch. A platform shutdown is **[unverified]**; I confirmed only that Manticore's standalone *Out of Time*, built on Core, closed about six months after its Steam release. |
| Crayta | Closed 3 March 2023; "not enough gamers played it". |
| Dreams | Live support ended 1 September 2023; the game stays online. |
| Project Spark | Ended May 2016, services off 12 August 2016. |
| EverQuest Landmark | Closed after EverQuest Next was cancelled. The February 2017 date is **[memory]**. |
| Manyland | Two developers, browser sandbox, shut 29 February 2024 after budget trouble. |
| Rune | Deterministic `logic.js` runs on clients and Rune's servers; no async, `Date`, `fetch` or regex. Current status **[unverified]**. |
| Playroom Kit | `setState`/`getState`, with one player's browser as host. |
| VRChat Udon, Garry's Mod (Lua), Minecraft plugins and datapacks, Neverwinter Nights persistent worlds, Rec Room, Hiber3D, Spatial, PlayCanvas | **[memory]**, not researched. All are "host owns avatar, networking and UI; creator scripts inside it". |

## 2. Real code against a thin API versus declarative data

I found no controlled comparison, and none between Fortnite Creative 1.0 and UEFN. The circumstantial evidence favours real code for agents.

- **Vibe Jam.** The rules require 90% AI-written code, a web game with no login, near-instant load, and recommend three.js. The 2025 edition drew over 1,000 submissions; 2026 drew 945, per a vendor blog.
- **Vibe Jam portal convention.** An exit portal redirects to `https://vibejam.com/portal/2026` with `username`, `color`, `speed`, `ref`, and optional `hp`, velocity and rotation. The receiving game sees `?portal=true` and spawns a return portal. This is a working precedent for cheap continuity between independently built three.js games.
- **fly.pieter.com.** Reported as one HTML file on three.js with a Python WebSocket server. Revenue figures conflict across sources.
- **Roblox.** It now ships an official open-source Studio MCP server for "external AI coding tools like Cursor and Claude Code". It also announced Build (prompt to playable game) and an agentic Assistant in April 2026. The largest code-SDK platform is betting on agents driving the real API.
- **Rosebud (vendor source).** "Single-file projects work best"; multi-file projects "confuse the model"; small wording changes cause black screens; templates "make a huge difference".

My inference from this: agents succeed with a familiar library, a starting template, a single small artefact and a fast run-and-look loop. A bespoke declarative format has no training data behind it. Declarative tools suit human non-programmers, which is Hytale's reasoning.

One gap matters for your plan. No platform I found takes arbitrary standalone code and retrofits services afterwards. Every one has the creator code against the host API from the first line.

## 3. Multiplayer without creator netcode

| Model | Creator writes | Known limits |
|---|---|---|
| Roblox or Hytopia, server-authoritative replication | Ordinary game code against host entities | Roblox "cannot verify physics calculations when a client has ownership", so client-owned physics is exploitable; forcing server ownership "can make physics jittery". |
| Croquet/Multisynq, deterministic replicated model | A model/view split; the model must be bit-identical everywhere | Any non-determinism diverges. Colyseus's docs warn that even differing Rapier builds produce different floats. Current limits **[unverified]**; the docs returned 403. |
| Rune, predict-rollback | Pure synchronous logic | Heavy language restrictions; examples show 4 players. |
| Playroom, shared key-value state | `setState`/`getState` calls | The host is a player's browser. Playroom's own guide says to stay elsewhere if you need strict server authority. |
| Decentraland, CRDT per component | `syncEntity(entity, components)` | Last-write-wins (per community docs), no persistence, exploitable without a server. |
| Durable Objects with PartyServer | Your own room server, one object per room | Hibernation suits idle rooms, not a ticking simulation. Per-object connection and CPU limits **[unverified]**. |

Least work for an agent-authored prototype is the declared-shared-state shape used by Playroom and Decentraland. The prototype stays single-player-shaped and marks which state is shared. It is cheatable and weak for physics and shooter hit validation.

The durable shape is Hytopia's and Roblox's: the zone's simulation runs in a host-owned authoritative room. The agent does the same amount of work either way if the host API hides which one is underneath.

## 4. Trains and moving platforms

**Why it is hard.**
- Amy Hennig said most games fake a train with a moving background, but Uncharted 2's train really moved. The level was a "headache for everyone involved" and drove a large share of the game's new technology.
- Its train follows a spline around a large loop, with cutscenes masking area transitions. This comes from secondary coverage; I could not open the slide deck.
- Fallout 3's engine had no vehicles, so the metro car is an armour piece (`DLC03MetroCarArmor`) worn by a character.
- Unreal forum threads show persistent multiplayer jitter on moving bases whenever client and server disagree about the platform's position.

**Standard multiplayer solution, where the mover really moves.**
- Parent the player to the platform and replicate the platform-local position.
- Make the platform's motion a pure function of synchronised time, not accumulated delta time.
- Treat boarding and leaving as an explicit switch of reference frame. Unity's Netcode needs a teleport of the interpolators at that point.

**Simplest robust technique for three.js: the train never moves.**
- Make the train the world origin, with static colliders.
- Scroll the canyon past as a looping ribbon of chunks, driven by one shared scalar: track position as a function of server time.
- Store every player position in train-local coordinates. Replication is then ordinary, and there is no moving-platform physics at all.
- The tunnel is a dark chunk during which you swap the scenery set. The teleport becomes a scenery swap that moves nobody.
- Place camps and enemies in track coordinates (distance along the track, lateral offset).
- Cost: anything on the ground lives in a scrolling frame. That is easy if players stay on the train and awkward if they dismount for long.

Source-engine `func_tracktrain` with landmark teleports is the classic moving-train alternative, but that is **[memory]**; the Valve wiki returned 403.

## 5. Sandboxing creator JavaScript

**Figma's sequence is the reference case.**
1. Cross-origin iframe. Rejected because it forced an async API and needed a document copy that took 14 seconds on a large file.
2. Realms shim on the main thread. Chosen for speed.
3. A JavaScript VM compiled to WebAssembly, adopted after a privately disclosed Realms vulnerability.

The final split has logic in the VM and UI in a null-origin iframe, with about 500 audited lines at the boundary.

**Other options.**
- ShadowRealm was a Stage 2.7 draft as of February 2025. Its explainer says it does not aim to control or prevent IO. Later status **[unverified]**.
- QuickJS in WebAssembly is an interpreter. One third-party figure puts a similar sandbox at about 1% of V8 speed, which is indicative only. It cannot host a three.js render loop, so it implies host-owned rendering as in Decentraland.
- The Roblox Luau sandbox is **[memory]**; not researched.

**For a first-party-only platform, do not build a security sandbox.** Adopt its shape instead:
- A zone is a module with `mount(host)`, `update` and `dispose`.
- A lint rule forbids direct use of `window`, storage and the network.
- This contains faults and keeps a later move to a cross-origin iframe per zone open. That is the only option that preserves raw three.js for third parties.

## 6. Scope: cautionary tales and counter-examples

**Tools without an audience.**
- Core, Crayta, Project Spark, Dreams, Landmark and Manyland all shipped capable creation tools. The ones with a stated reason cite too few players or budget; none blamed missing features.
- Worlds Adrift could not run without SpatialOS, so it could not be made peer-to-peer or self-hosted. Server costs were "not compatible with the amount of players".
- Reporting on Improbable says frequent platform updates "forced game studios to spend more time fixing code than perfecting their games".

**Counter-examples.**
- Realm of the Mad God: two developers, started as a TIGSource jam entry with a restricted shared art set, launched in the browser in June 2011, acquired by Kabam in June 2012.
- Webfishing: a solo developer who expected "maybe like 100 people" and peaked near 25,000 concurrent players.
- Garry's Mod: one person's Half-Life 2 mod in late 2004, standalone on Steam in November 2006.
- Vibe Jam: about 1,000 games a month under the constraint of one web page with instant load.
- Early Roblox, Minecraft and RuneScape origin details are **[memory]**; my searches did not return usable sources.
- "Write Games, Not Engines" is mirrored at geometrian.com. Its attribution to Josh Petrie is **[unverified]**.

## What this implies for the plan

1. **Use real three.js code against a thin host API**, not a declarative format. This matches what agents demonstrably do well and what Roblox is building towards.
2. **Reframe "upload to the MMO".** Since nobody retrofits standalone code, give the agent a template plus a local host shim that mocks accounts, quests, HUD and networking. The prototype is then written against the contract from the start, and upload becomes validation and bundling.
3. **Let the host own the two controller kinds, the HUD, identity and persistence.** Fortnite's locked character and Roblox's default HUD show creators tolerate this, and it is what makes UI normalisation possible.
4. **Expose multiplayer as declared shared state behind a host API.** Start with presence only (Decentraland's default) and move the zone simulation into an authoritative room when cheating or shooter hit validation matters.
5. **Build the train as a stationary train with a scrolling world and a tunnel scenery swap.** Avoid a truly moving train unless dismounting is core.
6. **Make zone boundaries hard teleports only.** Second Life's region crossings show why; the Vibe Jam portal parameters are a cheap continuity convention to copy.
7. **Skip the sandbox; keep the module discipline.**
8. **Ship one zone inside the live MMO before generalising.** Extract the SDK from the second zone. The failed platforms built tools first and found no players.

## Sources

**Roblox**
- https://create.roblox.com/docs/projects/client-server
- https://create.roblox.com/docs/players/disabling-ui
- https://create.roblox.com/docs/cloud-services/data-stores
- https://create.roblox.com/docs/physics/network-ownership
- https://devforum.roblox.com/t/studio-mcp-server-updates-and-external-llm-support-for-assistant/4415631
- https://about.roblox.com/newsroom/2026/04/roblox-studio-going-agentic
- https://pulse2.com/roblox-introduces-build-to-turn-text-prompts-into-playable-games/
- https://corp.roblox.com/newsroom/2025/03/introducing-roblox-cube

**Decentraland**
- https://238c3d3d.adr-cvq.pages.dev/adr/ADR-133
- https://b90f4824.adr-cvq.pages.dev/adr/ADR-117
- https://docs.decentraland.org/creator/development-guide/sdk7/serverless-multiplayer/
- https://dbeb74c0.new-docs-6m4.pages.dev/contributor/runtime/overview
- https://cdn.jsdelivr.net/npm/decentraland-rpc@3.1.9/README.md
- https://skills.sh/decentraland/sdk-skills/multiplayer-sync (community)

**Second Life**
- https://wiki.secondlife.com/wiki/Land
- https://wiki.secondlife.com/wiki/Map
- https://jira.secondlife.com/browse/BUG-230934
- https://github.com/John-Nagle/lslutils/blob/master/regioncrossing.md
- https://feedback.secondlife.com/server-bugs/p/simulator-occasionally-halts-scripts-on-region-handoff-when-they-have-collision

**Fortnite / UEFN**
- https://forums.unrealengine.com/t/user-experience-flaws-in-uefn/2704223
- https://uefncentral.com/uk/blog/uefn-vs-unreal-engine-5-differences
- https://dev.epicgames.com/documentation/fortnite/uefnonly-devices-in-fortnite
- https://www.tubefilter.com/2026/06/17/epic-games-unreal-editor-for-fortnite-creator-payouts/
- https://respawn.outlookindia.com/gaming/gaming-news/epic-games-expands-uefn-amid-722m-creator-boom
- https://blog.kowatek.com/?p=93604

**Discord, Poki, Hytopia, Hytale**
- https://docs.discord.com/developers/activities/how-activities-work.md
- https://docs.discord.com/developers/activities/development-guides/networking
- https://sdk.poki.com/sdk-documentation.html
- https://sdk.poki.com/new-requirements
- https://cdn.jsdelivr.net/npm/hytopia@0.15.2/README.md
- https://hn.jakechampion.name/reader/https://hytale.com/news/2025/11/hytale-modding-strategy-and-status (mirror of the official post)

**Multiplayer models**
- https://developers.rune.ai/docs/how-it-works/server-side-logic
- https://playroom-docs.vercel.app/llms-full.txt
- https://playroom-docs.vercel.app/migration-guides/hathora
- https://croquet.io/sdk/docs/tutorial-2_1_model_view_reflector.html
- https://croquet.io/docs/croquet/tutorial-2_8_random.html
- https://docs.colyseus.io/netcode/determinism
- https://cdn.jsdelivr.net/npm/partyserver@0.5.6/README.md
- https://blog.partykit.io/posts/partyserver-api/

**Vibe coding**
- https://vibejam.com/2026/
- https://vibej.am/2026/press
- https://www.summerengine.com/blog/cursor-vibe-jam-2026-guide.md (vendor)
- https://www.indiehackers.com/post/Uz0wHG4pI3KBOiFhP5YR
- https://404media.co/this-game-created-by-ai-vibe-coding-makes-50-000-a-month-yours-probably-wont (paywalled past the intro)
- https://levels.io/full-multiplayer-python-websockets-game-ai
- https://www.indiehackers.com/post/7CPfMr1yRLEwH6cC8xhE
- https://lab.rosebud.ai/blog/can-google-gemini-vibe-code-games (vendor)

**Trains and moving platforms**
- https://www.engadget.com/2009-09-06-pax-2009-uncharted-2s-nathan-drake-catches-a-train.html
- https://www.engadget.com/2010-03-12-gdc-among-friends-an-uncharted-2-post-mortem.html
- https://80.lv/articles/the-secrets-of-the-train-level-in-uncharted-2
- https://www.gameenginebook.com/resources/gfg2010-final.pdf (too large to open; cited from a search excerpt only)
- https://pcgamer.com/heres-whats-happening-inside-fallout-3s-metro-train
- https://forums.unrealengine.com/t/multiplayer-how-to-get-smooth-character-interpolation-on-moving-platforms-without-jittering/108500
- https://forums.unrealengine.com/t/how-to-sync-moving-platforms-in-multiplayer/2523064
- https://discussions.unity.com/t/moving-platform-client-desync/1576356
- https://docs.coherence.io/getting-started/samples-and-tutorials/first-steps-tutorial/4-parenting-entities
- https://devforum.roblox.com/t/creating-the-illusion-of-a-moving-train/1286756 (page returned empty; cited from a search excerpt only)

**Sandboxing**
- https://www.figma.com/blog/how-we-built-the-figma-plugin-system/
- https://developers.figma.com/docs/plugins/how-plugins-run
- https://tc39.es/proposal-shadowrealm
- https://github.com/tc39/proposal-shadowrealm/blob/main/explainer.md
- https://blogs.igalia.com/compilers/2025/03/27/summary-of-the-february-2025-tc39-plenary/
- https://github.com/justjake/quickjs-emscripten
- https://besthub.dev/articles/how-webassembly-quickjs-enables-a-secure-web-sandbox-for-next-gen-open-platforms-e09f34e9f426 (third-party performance figure)

**Scope: failures and counter-examples**
- https://en.wikipedia.org/wiki/Core_(video_game_platform)
- https://rogueliker.com/out-of-time-offline/
- https://chromeunboxed.com/now-that-google-stadia-has-shut-down-crayta-is-following-suit/
- https://docs.indreams.me/en/whats-happening/news/dreams-support-update
- https://godisageek.com/2016/05/project-spark-sunset/
- https://mein-mmo.de/en/landmark-schliesst-alles,141388
- https://wiki.archiveteam.org/index.php/Manyland
- https://store.steampowered.com/app/342280
- https://steamcommunity.com/app/322780/discussions/0/1644290458825499424
- https://www.pcgamesinsider.biz/news/69671/bossa-doesnt-blame-improbable-for-worlds-adrifts-cancellation/
- https://au.finance.yahoo.com/news/softbank-backed-effort-revolutionize-gaming-060025319.html
- https://mobygames.com/game/54846
- https://realmeye.com/wiki/development
- https://www.gamesradar.com/platforms/pc-gaming/after-their-chill-fishing-game-peaks-at-more-than-20-000-concurrents-dev-reveals-they-thought-maybe-like-100-people-would-play-it-ever
- https://en.wikipedia.org/wiki/Garry%27s_Mod
- https://geometrian.com/projects/blog/write_games_not_engines.html
