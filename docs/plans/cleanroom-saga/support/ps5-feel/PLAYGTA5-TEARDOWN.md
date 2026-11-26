# playgta5.com teardown: AAA in a browser tab

> Moved from meta `docs/plans/support/ps5-feel/PLAYGTA5-TEARDOWN.md` at `386423cbea` into the cleanroom saga (D38, 2026-11-26).

> Written by: Claude

> **State:** read 2026-11-11 ~17:40 Cancún from the site's shipped page and worker sources (`index.html`, `loader.js`,
> `wgpu_worker.js`, `io_worker.js`, `net_worker.js` under `/b/0cdcabcef9/`), fetched with curl. Not run in a
> browser: J148 allows third-party sites only in a cloud container or system Chrome ([PS5-FEEL-PLAN](../../2026-11-11-opus-ps5-feel-PLAN.md)
> row PF2 does that run). Evidence for [PS5-FEEL-PLAN.md](../../2026-11-11-opus-ps5-feel-PLAN.md). We study the techniques only; none of
> its code or Rockstar's assets come into our repos.

## What it is

Grand Theft Auto V for PC, compiled to WebAssembly and drawn with WebGPU, playable from a URL. Story Mode, a Sandbox Mode,
and GTA Online's own flow over peer-to-peer WebRTC with three "servers" (separate meshes). It is a port of the real
engine (comments name `scrThread::Run`, `CPauseMenu`, `rage/base/src/net/netsocket_wasm.cpp`), not a remake. The source
comments are dated 2026-10-06 to 2026-11-10 and talk about "10,000 visitors a day", so it is about five weeks old and live
at scale. The comments' style (dated, measured, plain-language, "the user's 4-core Chromebook") reads like an agent-built
port.

## How it works, in its own words

| Layer | What they did | Numbers they wrote down |
|---|---|---|
| Threads | The engine's `main()` runs in a dedicated worker (`loader.js`) and may block; the page owns only the canvas, transferred on to a GPU worker. Every engine thread is an Emscripten pthread worker. Needs cross-origin isolation (the page sends COOP `same-origin`, COEP `require-corp`). | 80 to 116 threads by default, ~20 MB each; 54 in the low profile; +24 workers pre-spawned for network play |
| Renderer | D3D11 calls become a **command ring in shared wasm memory**; one GPU worker owns every WebGPU object and replays it. Game threads block on a futex word only for readbacks and queries. Redundant state is skipped (each WebGPU call costs microseconds). Readbacks ride the next submit. | Two readbacks a frame saved ~0.65 ms each |
| Shaders | HLSL translated to WGSL offline, bundled into ~4 MB packs per effect; fetched when an effect *creates* a shader, not at its first draw. A pack is dropped 8 s after last use. | ~20 requests instead of ~6,000; ~70 MB if all stayed resident |
| Code | `game.wasm` (63 MB) is compiled while downloading (streaming compile), in the io worker because Chrome's code cache copies piled up in a thread that never collects garbage. | Renderer native memory 1.7 GB to 0.37 GB at 4 minutes |
| Data | An io worker streams every HTTP response straight into an **append-only block store in OPFS** (`store.bin` + `journal.bin`), then into the wasm heap. No JS buffers, so no GC. Blocks are keyed by file version, so a patch re-downloads only what changed. | Sync XHR + a service worker had cost ~1.5 GB + ~0.9 GB of renderer memory |
| Boot | A `?record=1` run logs the block ranges the engine touches at boot; every later load fetches that **boot set** at once, in parallel, while the player is still on the title screen. Small files come as compressed batches cached on Cloudflare as static files. Speculative fetches go at low fetch priority so a blocking read never queues behind them. | Boot set ~580 to 600 MB; Range streams: 6 in flight 3.4 MB/s, 128 in flight 14.1 MB/s; engine reads had waited 6.6 s behind 32 prefetch streams |
| Title screen | The game's own Scaleform loading screen redone in HTML and CSS 3D. The player picks Story, Sandbox or Multiplayer *while* the wasm compiles, the boot set downloads and the GPU worker compiles pipelines; `main()` waits on that choice. | The engine waits at ~62 % of the load if nothing is chosen |
| Low-end profile | `navigator.deviceMemory <= 4` gets 2 cores, quarter textures, shadows off (a third of all draws), no SSAO or post, 720p scaled up. | GPU memory 1.16 GB to 0.5 GB; streamed assets 1.38 GB to 0.95 GB; a 4 GB Chromebook 1.9-3.8 fps, 4.9-7.3 fps with 4 cores |
| Timers | Chrome on Windows rounds `Atomics.wait` timeouts up to the 15.6 ms OS tick unless the renderer has a sub-16 ms timer pending, so the page keeps an **empty `setInterval`** alive. | A 60 fps cap had held at 37 fps; a 1 ms wait took 15.5 ms, 2.1 ms with the timer |
| Audio and input | The engine mixer writes a ring in shared memory that an AudioWorklet plays; DOM input writes a shared-memory input block. Vsync ticks from `requestAnimationFrame` wake the engine's frame limiter through a futex. | |
| Multiplayer | **No game server.** Each tab is a peer; a net worker is the hub of a WebRTC data-channel overlay (the page owns the `RTCPeerConnection`s, Chrome has none in workers). Each machine hosts its own view of one world; nearby players are promoted into the session group, far ones become ghost dots fed by gossip. A PHP rendezvous introduces peers (no WebSocket). The player id is a public key; hellos prove it; a player reported by three others is cut off. Proximity voice rides the same links. | Ghost states every 50 ms, gossip every 1 s, overlay tick every 500 ms; two free STUN servers |
| Operations | Build-id URLs cached forever; an old tab asking for a gone build reloads itself (once a minute at most). GPU device lost: one automatic reload per 3 minutes. A 30 s stall watchdog. A one-line announcement from `message.txt`. 503/500/429 retried 8 times with jitter (~20 s). Files over 480 MB split for Cloudflare's 512 MB cache limit. Saves in IndexedDB, protected from the cache filling the quota. | |

## What it tells us

1. **The browser is not the limit.** Jake played it (2026-11-11): 60 fps, smooth, full textures, assets, animation and
   driving; "nothing like a browser game". A PS5-class game runs in a tab today.
2. **The engineering that made it fit** is three habits: keep the main thread free (workers, shared rings, futexes),
   never touch the garbage collector on the hot path, and hide every wait behind the player's own choice.
3. **What makes it look and feel like GTA** is not the browser part at all. It is the original game's lighting, image
   chain, animation, vehicles and art direction, carried over whole. That is the gap
   [PS5-FEEL-PLAN.md](../../2026-11-11-opus-ps5-feel-PLAN.md) audits and closes.
