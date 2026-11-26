# Research: primitive-based engines that host creators' scripts

> Moved from meta `docs/prototype-to-mmo/evidence/precedents-primitives-research.md` at `386423cbea` into the cleanroom saga (D38, 2026-11-26).

> Written by: Claude

> **State:** point-in-time record, 2026-11-16. Web research by a research subagent for [STRATEGY.md](../STRATEGY.md), with numbered sources at the end. Each claim is marked fetched, snippet-only or from memory; the strategy uses only the fetched ones for anything it leans on.

## Primitives-first engine for hosted user content: precedents and numbers

Legend: **[F]** = page I fetched and read; **[S]** = seen only in a search-result snippet; **[M]** = from memory, not verified this session. Numbers in brackets refer to the source list at the end.

## 1. Platforms that run untrusted creator scripts on their own servers

**Roblox**
- **Sandbox:** Luau removes `io`, `package`, `dofile`/`loadfile` and all bytecode loading, and trims `os` and `debug`. Builtins are read-only, and each script gets its own global table that reaches builtins through `__index` [1][F].
- **CPU metering:** there is no instruction counter. The host sets an interrupt that Luau is guaranteed to reach at any function call or loop iteration, and a watchdog uses it (10 s in Studio) [1][F]. I found no documented hard per-script CPU quota on live servers.
- **Memory:** Luau has no limit by default; the host sets one [1][F]. Roblox's docs give about 6 GB per server, after which the server crashes [4][S]; forum posts cite 6.25 GB.
- **Replication:** it is a property of the data model, not of features. The server's data model is copied to clients and kept in sync [6][F]. With `StreamingEnabled` (on by default for new places) only nearby Workspace content is sent [3][S].
- **Prediction:** the only general mechanism is physics network ownership. Unanchored assemblies near a player are simulated by that client, and the docs say "Roblox cannot verify physics calculations when a client has ownership" [2][F].
- **Engine versus Luau:** Roblox is moving character movement out of the engine. The Character Controller Library "replaces rigid Humanoid state machines" with abilities written as Luau tables. Ability callbacks "run in both the predicted client and authoritative server simulations", so they must be deterministic and must not yield [5][F].
- **Core classes** (Part, MeshPart, Model, Attachment, constraints, Humanoid, RemoteEvent, default camera and control scripts in Luau) [M].

**Second Life**
- **Memory:** 16 KB per pre-Mono script and 64 KB per Mono script [7][F].
- **Scheduling:** scripts are the lowest-priority slice of a roughly 22 ms simulator frame. On Homestead regions script time caps at about 5 to 6 ms even with spare time left [8][S]. An idle script still costs 0.001 to 0.003 ms per frame [9][S].
- **Current direction:** Linden Lab is replacing Mono with Luau ("SLua", alpha March 2025). Its FAQ cites Mono memory problems, says the best LSL-on-Mono result was 10% slower than Luau, and says scripts come out about half the size [10][S].
- **Design rationale and content effects** (many tiny scripts talking by link messages to dodge the memory cap) [M]; I did not find a primary source.

**Fortnite UEFN**
- **Timeline:** Scene Graph went Experimental on 13 June 2024, with no publishing [11][F]. It went Beta in v36.00 (June 2025) as "a new foundational engine layer that unifies editor and runtime views" [12][F]. Epic's docs still label it Beta today [13][F].
- **Launch component set:** "meshes, materials, collision, sounds, VFX, and player interaction", plus prefabs that Verse can spawn and destroy [12][F].
- **Relation to devices:** entities and prefabs "are not directly compatible with the devices"; bridging needs custom Verse [13][F].
- **Not found:** an Epic statement saying outright that devices were insufficient. The closest is Scene Graph as "a unified structure that connects all the objects in the world" [66][F].
- **Unreal Engine 6:** on 17 June 2026 Epic said Scene Graph is a new gameplay framework built from scratch on Verse, with Actors and Blueprints to be deprecated later [14][F]. A trade-press report of Unreal Fest Tokyo (3 November 2026) says keynote slides marked Blueprints, Actors and the C++ Gameplay Framework "Remove" from UE6 Early Access, planned for late 2027, with Fortnite migrating first [15][F, secondary source].

**Decentraland SDK7**
- **Model:** entities are bare IDs, components are data, systems are scene code [65][F].
- **Component count:** the protocol repository has 67 component schema files, including result and UI types. Examples are Transform-adjacent types, MeshRenderer, MeshCollider, GltfContainer, Animator, AudioSource, Raycast, PointerEvents, Tween, TriggerArea and Material [17][F].
- **Limits per scene of n parcels:** 10,000n triangles, 200n entities, 300n bodies, log2(n+1)×20 materials, log2(n+1)×10 textures, 330 m height. These are soft warnings. File size is hard: 15 MB per parcel, 300 MB cap [16][F].
- **Sandbox and sync:** scene state reaches the renderer as CRDT messages keyed by entity and component ID [18][S]. Scenes running in QuickJS is stated only in community pages [S].

**VRChat Udon**
- **Speed:** the official docs say "Udon can take about 200x to 1000x longer to run a piece of code than the equivalent in normal C#" [19][F].
- **Failed rewrite:** Udon 2 was cancelled in December 2024 after "two years of work" against a 3 to 6 month estimate. Marshalling penalised extern-heavy code, and compatibility mode ran existing worlds two to ten times slower [20][F].

**Others**
- **Rec Room Circuits:** chip cap raised from 5,000 to 7,500 per room, with CPU and network "heat" budgets [21][S]. Metering is by graph size and heat, not time.
- **Source engine I/O:** entities expose named inputs and outputs wired in the editor with delay and fire-once settings [22][S]. A few generic entities plus wiring covered most of a level's gameplay logic.
- **Core (Lua), Dreams (thermometer budget), Garry's Mod (Lua entities), Minecraft (functions, default 65,536-command chain limit):** all [M].

## 2. "Few primitives, many games" in general engines

**Unreal Gameplay Ability System**
- Epic describes it as "designed mainly for RPGs, action-adventure games, MOBAs, and other types of games" [23][F].
- The five primitives are abilities, attributes ("enhanced floating point values that can be temporarily buffed / debuffed"), gameplay effects (instant damage, or lasting poison, buffs and debuffs), tags, and cues (cosmetic only) [23][F].
- Epic's listed uses include stat changes, cooldowns, resource costs, blocking other abilities, and status effects such as a Sleep debuff [23][F].
- The community reference says it was "battle tested in AAA commercial games such as Paragon and Fortnite", and that it replicates all of this and predicts ability activation, montages, attribute changes, tags, cues and root-motion movement [24][F].
- It cannot predict cooldowns, removal of effects, or periodic effects [24][F].

**Blueprint versus C++:** I could not retrieve Epic's own figure. A forum microbenchmark (UE 4.16) reported Blueprint 27 times slower than C++, and 1.7 times when nativized [25][S; exact thread not confirmed]. The usual "about 10x" is [M].

**Overwatch:** a third-party summary of Tim Ford's GDC 2017 talk gives about 46 client systems and 103 component types, with only three systems (movement, weapon, Statescript) carrying gameplay netcode [61][S].

**Unity, Godot, Bevy, Flecs, Unreal Character Movement:** [M]. Unity's GameObject plus MonoBehaviour, Godot's node tree plus signals, and ECS with ChildOf/IsA relations and prefabs are each one composition primitive, one behaviour hook and one messaging primitive. Custom movement modes exist in Unreal (`MOVE_Custom` with a replicated sub-mode byte) [S].

## 3. Sandboxed scripting choices

**AssemblyScript** (official status page, undated) [26][F]:
- Closures: not implemented.
- Exceptions: "Throwing currently aborts the program."
- Union types: only nullable class types.
- Iterators and `for..of`, rest parameters, async: not implemented.
- RegExp, Date, JSON: limited.
- I found no write-up on how AI coding agents handle AssemblyScript.

**JavaScript engine compiled to WebAssembly**

| Measure | Figure | Source |
|---|---|---|
| bench-v8 score, QuickJS (2019 build, native) | 942 | [27][F] |
| bench-v8 score, V8 `--jitless` | 1,916 | [27][F] |
| bench-v8 score, V8 with JIT | 33,640 | [27][F] |
| V8 jitless slowdown versus JIT | 6% on typical web workload, 80% on Web Tooling Benchmark | [28][S] |
| Javy static module | at least 869 KB | [31][S] |
| Javy dynamically linked module | 1 to 16 KB plus a shared engine module | [31][S] |
| Shopify Functions limits (2023 article) | 256 KB module, 5 ms run | [29][F] |
| Javy JS versus Rust-built Wasm at Shopify | about 3 times slower | [29][F] |
| StarlingMonkey with weval ahead-of-time specialisation | 2.77x geomean speedup over its interpreter | [34][F] |
| Porffor Test262 pass rate | about 48%, undated, self-described pre-alpha | [36][S] |

- The bench-v8 row means native QuickJS is about half of jitless V8 and about 1/36 of JIT V8. I found no measured QuickJS-in-Wasm versus V8 number; expect worse than the native ratio.
- Shopify still "strongly recommends Rust" for production because JS hits instruction limits sooner, and Javy has no event loop [30][F].
- Figma moved from a Realms shim to "a JavaScript VM written in C" compiled to WebAssembly after a Realms vulnerability; plugins run on the main thread with ES2020+ [32][33][F]. That this VM is QuickJS is [M].
- StarlingMonkey (SpiderMonkey in Wasm) is in production at Fastly and Fermyon [35][S]. JITs are generally unavailable inside Wasm sandboxes [34][F].
- Static Hermes: nothing found. Cloudflare Workers using V8 isolates, not a Wasm-hosted engine: [M].

**Lua in WebAssembly**
- wasmoon (official Lua 5.4 in Wasm) reports 15.3 ms versus Fengari's 389.9 ms on a heap sort, and 130 kB versus 69 kB gzipped. This is the project's own benchmark, and it warns that heavy JS interop erodes the gain [37][S].
- Luau in Wasm: I found only third-party Emscripten builds; official build maturity and performance are unverified.

**Metering**
- **Wasmtime fuel:** "completely deterministic", but slower than epochs [38][F]. One Wasmtime issue reports 15 to 40% overhead [39][S].
- **Wasmtime epochs:** about 10% slowdown, non-deterministic [38][F].
- **V8 and Node:** I found no native fuel facility. The established workaround is rewriting the module to count instructions per basic block (`wasm-metering`, Parity `wasm-instrument`, `finite-wasm`) [40][S].
- **Killing a worker:** this is the non-deterministic fallback. A WebKit bug reports that `worker.terminate()` fails to stop non-yielding WebAssembly [41][S]. Node/V8 behaviour was not confirmed.
- **Determinism:** the spec's sources of nondeterminism are NaN bit patterns, shared-memory threads, relaxed SIMD, resource exhaustion and host imports [42][F]. Avoid threads and relaxed SIMD, canonicalise NaNs, and keep host imports deterministic.

**Component Model and WIT**
- Not native in any browser. Version 1.0 "can't formally reach 1.0 without native implementation in at least two browser engines"; Mozilla and V8 are evaluating (article dated 8 June 2026) [43][F].
- `jco transpile` runs components in browsers today as core Wasm plus JS glue [43][F], but its browser support is labelled experimental [44][S].

**Boundary cost**
- Firefox 2018: 100 million JS-to-Wasm calls in about 450 ms, roughly 4.5 ns each when types are monomorphic [45][F]. I found no current V8 figure.
- Figma measured about 0.1 ms per postMessage round trip, about 1,000 per second [32][F].
- Direct calls are cheap and cross-thread messages are not, so batch commands and share linear memory [M for the mitigation pattern].

## 4. Scene interchange and shaders

**glTF 2.0** (Khronos extensions README as fetched today) [46][F]:
- **Ratified:** KHR_lights_punctual, the KHR_materials family, KHR_texture_basisu, KHR_mesh_quantization, KHR_animation_pointer, KHR_interactivity, KHR_node_visibility, KHR_node_selectability, KHR_node_hoverability, KHR_gaussian_splatting.
- **Not ratified:** KHR_physics_rigid_bodies and KHR_collision_shapes (Review Draft), KHR_audio_graph (Proposal).

**KHR_interactivity**
- Behaviour graphs of event, flow and data nodes that read and write glTF properties and custom variables. They "can be constrained to prevent infinite loops".
- Submitted for ratification 16 July 2026. Babylon.js plays it; three.js is not named among implementers [47][F].
- The README listing it as ratified is newer than that press release; I did not find a separate ratification announcement.

**three.js GLTFExporter**
- Supports KHR_lights_punctual, eleven KHR_materials extensions, KHR_texture_transform, KHR_mesh_quantization, EXT_mesh_gpu_instancing, EXT_materials_bump and EXT_texture_webp [48][F].
- Does not export ShaderMaterial [49][S].
- Exports only directional, point and spot lights, without shadow settings; scene background is lost [S, forum].

**Custom shaders**
- **VRChat:** allowed in worlds on all platforms; Android avatars are restricted to SDK shaders; performance ranks police the rest [50][S].
- **Decentraland:** "Only standard materials and PBR" [51][S].
- **Roblox:** no custom shaders [M].
- **WebGL risk:** Khronos says shaders are validated before reaching the driver and cannot access arbitrary memory. The acknowledged risk is denial of service from long draws, which removing loops would not fix; mitigation is robustness and context loss [52][S; direct fetch blocked].
- **three.js TSL:** compiles a JS node graph to GLSL or WGSL [53][S]. Whether a TSL graph round-trips through `toJSON`/ObjectLoader is unverified.
- **OpenUSD:** not researched; [M] only.

## 5. Generic server-authoritative netcode

- **Quake 3:** the server keeps 32 snapshots per client and delta-encodes against the last acknowledged one. A `netField_t` table of offset and bit size means it "does not even know what it is comparing" [54][F].
- **Source:** each networked class declares a SendTable of SendProps, and the engine does change detection and delta snapshots. Defaults are about 20 snapshots per second and 100 ms interpolation [55][S].
- **Unreal:** per-property replication plus RPCs. Fortnite starts a match with 100 players and about 50,000 replicated actors, which required Replication Graph [56][S].
- **Unity Netcode for Entities:** any component with a `[GhostField]` replicates. Ghosts are interpolated, predicted or owner-predicted, with quantisation, delta compression and importance scaling [57][F].
- **bevy_replicon:** replication rules per component, per-client visibility, no built-in transport. Prediction and rollback are third-party crates, some unmaintained [58][F].
- **Photon Fusion:** `[Networked]` properties live in per-tick snapshot buffers and are reset before each resimulated tick; non-networked fields are not [59][S].
- **lightyear:** [M].

**Overwatch Statescript** (Dan Reed's GDC 2017 slides, text extracted) [60][F]:
- **What it is:** a visual graph of Entry, Condition, Action and State nodes. Each node type is a C++ class, and variables live in instance and owner bags.
- **Authority:** server-authoritative; only button input and aim go client to server.
- **Replication:** the server records per-command-frame deltas (changed variables, states, executed actions).
- **Prediction:** remote entities "do not simulate Statescript Instances", they only replicate. The local entity does "Rollback, Replicate, Simulate" on each packet, keeping history of its own variables, states and input.
- **Bandwidth:** scripts are compiled to work out which nodes and variables remote clients need. Tracer firing a full clip and reloading costs 2,028 bits local versus 806 bits remote over 2 seconds.
- **Benefit:** "New gameplay features can be added without writing synchronization or state machine logic in code."
- **Costs:** "Hefty up-front implementation cost for the runtime, an editor, and a debugger", and eventual consistency rather than blow-by-blow replication.

## 6. Rewrites versus incremental generalisation

- **Spolsky:** rewriting from scratch is "the single worst strategic mistake that any software company can make"; Netscape went almost three years between 4.0 and the 6.0 beta [62][F].
- **VRChat Udon 2:** a recent in-domain case of a scripting-VM rewrite cancelled after two years [20][F].
- **Unreal:** Sweeney in 1998 said the goal "was to build up a base of code that could be extended and improved through many generations of games" [63][S, secondary]. Epic's UE6 break is being proven on Fortnite first [15][F, secondary].
- **Roblox:** generalising incrementally, with the new character controller opt-in beside the legacy Humanoid [5][F].
- **Rule of thumb:** "write games, not engines" appears in forum threads, with advice to extract shared code when starting the second game [64][S]. I found no citable source for "extract the engine from the third game". Brooks's second-system effect and the id Tech, Source and Minecraft histories are [M].

## What this implies for a primitives-first redesign

1. **Replication belongs to the data model.** Quake 3, Source, Unreal, Unity, Fusion and Roblox all declare fields as replicated and let one generic delta path carry them. A zipline or boat then needs no message type of its own.
2. **Small primitive sets do ship.** UEFN's Beta launched with six component families [12], Decentraland has 67 schemas including UI [17], and GAS covers buffs, damage, cooldowns and status effects with five concepts [23]. Decentraland's 200 entities per parcel shows the budget is the real design constraint.
3. **Movement and abilities are where "one subsystem per mechanic" dissolves.** Roblox's ability tables with shared label bits [5], GAS tags and effects [23], and Statescript states [60] are the same shape. Grapple, ladder, sail and takedown can be data on one mechanism.
4. **Prediction of sandboxed scripts has two proven models.** Either only client-owned physics is predicted (Roblox), or the same deterministic script runs on the owning client and server with rollback of its own variables only (Statescript, Roblox's new controller). The second needs deterministic guests; WebAssembly qualifies if threads and relaxed SIMD are off and NaNs are canonicalised [42].
5. **The guest language is a trade.** AssemblyScript lacks closures and exceptions [26]. An interpreter in Wasm is real JS or Lua, but QuickJS is about 1/36 of JIT V8 on old native numbers [27] and Udon shows creators tolerate 200 to 1000 times slowdowns only with heavy engine-side primitives [19]. Slower guests push more work into host primitives, which favours a richer component set and batched commands.
6. **Metering in Node needs instrumentation.** Fuel is native only in Wasmtime (15 to 40% overhead reported); for V8 on both server and browser, inject counters at upload time, with worker termination as a backstop.
7. **glTF covers static scenes, not gameplay.** Lights, materials and instancing are ratified; physics is still draft; KHR_interactivity is new and has no three.js runtime named [46][47]. Expect custom extensions or a sidecar for components, and no path for raw ShaderMaterial [49].
8. **Do it incrementally.** The evidence (Spolsky, Udon 2, Roblox's opt-in controller, Fortnite migrating first) favours adding the generic layer beside existing sections and re-expressing one existing mechanic at a time over a from-scratch rebuild.

## Could not verify

- Roblox hard per-script CPU limits.
- Second Life design rationale and share of scripted content.
- An explicit Epic statement that devices were insufficient.
- Epic's own Blueprint-versus-C++ ratio.
- QuickJS-in-Wasm versus V8 measurements.
- Official Luau Wasm build.
- Node `worker.terminate()` behaviour on spinning Wasm.
- TSL serialisation.
- OpenUSD comparison.
- Anything on AI agents and AssemblyScript.

The Statescript slide PDF was saved by the fetch tool at `/Users/raynos/.claude/projects/-Users-raynos-projects-games-wildshard-vision/231c15d6-550b-4fe9-9781-29149538795b/tool-results/webfetch-1794850548122-ud74xv.pdf`.

## Sources

1. https://luau.org/sandbox
2. https://create.roblox.com/docs/physics/network-ownership
3. https://create.roblox.com/docs/workspace/streaming
4. https://create.roblox.com/docs/projects/performance-optimization/memory
5. https://create.roblox.com/docs/characters/character-controller-library
6. https://create.roblox.com/docs/projects/client-server
7. https://wiki.secondlife.com/wiki/LSL_Script_Memory
8. https://kokua.atlassian.net/wiki/spaces/KKA/pages/15237163
9. https://wiki.secondlife.com/wiki/LSL_Script_Efficiency
10. https://wiki.secondlife.com/wiki/Lua_FAQ
11. https://forums.unrealengine.com/t/scene-graph-is-now-available-as-an-experimental-feature-in-uefn/1901700
12. https://dev.epicgames.com/documentation/fortnite/36-00-fortnite-ecosystem-updates-and-release-notes
13. https://dev.epicgames.com/documentation/fortnite/getting-started-in-scene-graph-in-fortnite
14. https://gamesbeat.com/unreal-engine-6-will-combine-ue5-and-uefn-into-a-unified-engine-state-of-unreal/
15. https://www.invenglobal.com/articles/28098/epic-games-will-remove-blueprints-and-actors-from-unreal-engine-6
16. https://docs.decentraland.org/creator/development-guide/sdk7/scene-limitations/
17. https://github.com/decentraland/protocol/tree/main/proto/decentraland/sdk/components
18. https://eca22ceb.adr-cvq.pages.dev/adr/ADR-133 and https://b90f4824.adr-cvq.pages.dev/adr/ADR-117
19. https://creators.vrchat.com/worlds/udon/udonsharp/performance-tips
20. https://ask.vrchat.com/t/on-udon-2-soba-and-why-we-changed-directions/28484
21. https://forum.rec.net/t/new-rooms-2-circuit-limits-road-to-r2/6092
22. https://developer.valvesoftware.com/wiki/Inputs_and_Outputs
23. https://dev.epicgames.com/documentation/en-us/unreal-engine/understanding-the-unreal-engine-gameplay-ability-system
24. https://github.com/tranek/GASDocumentation
25. https://forums.unrealengine.com/t/nativize-blueprint-assets-speed-vs-c/70081
26. https://www.assemblyscript.org/status.html
27. https://github.com/quickjs-zh/QuickJS/blob/master/bench.md
28. https://v8.dev/blog/jitless
29. https://shopify.engineering/javascript-in-webassembly-for-shopify-functions
30. https://shopify.dev/docs/apps/build/functions/programming-languages/javascript-for-functions
31. https://github.com/bytecodealliance/javy
32. https://www.figma.com/blog/how-we-built-the-figma-plugin-system/
33. https://developers.figma.com/docs/plugins/how-plugins-run/
34. https://cfallin.org/blog/2024/08/28/weval/
35. https://andreiltd.github.io/StarlingMonkey/print.html
36. https://github.com/CanadaHonk/porffor
37. https://github.com/ceifa/wasmoon
38. https://docs.wasmtime.dev/examples-interrupting-wasm.html
39. https://bytecodealliance.github.io/zulip-archive/stream/225357-git-wasmtime/topic/wasmtime.20.2F.20issue.20.234109.20Slacked.20fuel.20metering.html
40. https://cdn.jsdelivr.net/npm/wasm-metering@0.2.1/README.md and https://paritytech.github.io/try-runtime-cli/wasm_instrument/gas_metering/index.html
41. https://bugs.webkit.org/show_bug.cgi?id=289686
42. https://github.com/WebAssembly/design/blob/main/Nondeterminism.md
43. https://bytecodealliance.org/articles/the-road-to-component-model-1-0
44. https://www.socket.dev/npm/package/@bytecodealliance/jco-transpile
45. https://hacks.mozilla.org/2018/10/calls-between-javascript-and-webassembly-are-finally-fast-%F0%9F%8E%89/
46. https://github.com/KhronosGroup/glTF/blob/main/extensions/README.md
47. https://www.khronos.org/news/press/gltf-interactivity-extension-submitted-for-ratification
48. https://threejs.org/docs/pages/GLTFExporter.html
49. https://discourse.threejs.org/t/why-doesnt-gltfexporter-support-shadermaterials/21382
50. https://creators.vrchat.com/platforms/android/quest-content-limitations/
51. https://dbeb74c0.new-docs-6m4.pages.dev/creator/3d-modeling/materials
52. https://wikis.khronos.org/webgl/Main_Page/cms/security
53. https://threejs.org/docs/TSL.html
54. https://fabiensanglard.net/quake3/network.php
55. https://developer.valvesoftware.com/wiki/Networking_Entities and https://developer.valvesoftware.com/wiki/Source_Multiplayer_Networking
56. https://dev.epicgames.com/documentation/unreal-engine/replication-graph-in-unreal-engine
57. https://docs.unity3d.com/Packages/com.unity.netcode@1.4/manual/ghost-snapshots.html
58. https://github.com/projectharmonia/bevy_replicon
59. https://doc.photonengine.com/fusion/v2/manual/data-transfer/networked-properties
60. https://media.gdcvault.com/gdc2017/Presentations/Reed_Dan_NetworkingScriptedWeapons.pdf
61. https://edgegap.com/blog/game-backend-deep-dive-overwatch-2016-netcode-architecture-rollback
62. https://www.joelonsoftware.com/2000/04/06/things-you-should-never-do-part-i/
63. https://en.wikipedia.org/wiki/Unreal_Engine_1
64. https://www.gamedev.net/forums/topic/523006-make-games-not-engines/
65. https://docs.decentraland.org/creator/development-guide/sdk7/entities-components/
66. https://dev.epicgames.com/documentation/fortnite/scene-graph-in-unreal-editor-for-fortnite
