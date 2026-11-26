# Repo study: the meta plans, the site and the API

> Moved from meta `docs/prototype-to-mmo/evidence/repo-study-meta-site-api.md` at `386423cbea` into the cleanroom saga (D38, 2026-11-26).

> Written by: Claude

> **State:** point-in-time record, 2026-11-16. A read-only study by a research subagent for [STRATEGY.md](../STRATEGY.md). Scope: `project-wildshard-meta`, `wildshard/www.wildshard.io` and `wildshard/api-server`. Nothing was built, run or changed. The claims the strategy leans on hardest were re-read in the source by the lead agent; they are listed in the folder [README](../README.md).

I did a read-only pass over all three repos. Each section below separates what the docs say from what I checked in code or git myself.

## 1. Meta repo: intent, plans, decisions

**Size (I counted these).** `docs/plans/` holds 309 markdown files and 62,783 lines:
- about 36 live top-level plans
- `archive/`: 100 entries, 20,261 lines
- `parked/`: 13 entries
- `multi-repo/grill/`: 34 decision-session logs

`docs/vision` is 4 files and 295 lines. `project/journal` is a single 21-line relay note written by Codex. The meta repo has 3,896 commits, and 3,853 of them came after Nov 2. There were 734 on Nov 15 and 626 so far today.

**Vision.** `docs/vision/VISION.md` is labelled "historical synthesis from 2026-09-30; partly superseded". The current requirements live in singleplayer's `MMO-REQUIREMENTS.md`, which I did not read. The sharpest lines:
- "A **first-person, multiplayer, browser sandbox**… each **authored by a player**. **Claude Code is the level editor.**"
- The server must load a shard "**as config, never as arbitrary code**".
- "Shard size: 500 m × 500 m × **500 m**".
- Uploading is a beacon "ritual", and the source says: "do not substitute a CLI uploader for this experience."
- Jake's original `sources/FUNDAMENTALS.md` and `GAME-REFERENCES.md` list "First person, shooter mechanics", quests, and "custom collectibles / exploration / puzzles" as things authors must be able to make.

**Who makes shards.** The plans say agents first and outside creators later. J340: "AI agent lanes are the main author, outside creators get the same API later." `MMO-PLAN.md:341`: "Parked for outside authors (J152): creator keys…". J364: "one format for everyone… no such thing as first part or third party shard." ONE-FORMAT is only done when a "stranger shard" made in plain JSON or Python plays on staging.

I found no creator-economy, payment or payout plan. The only "economy" is the in-game "two wallets" rule.

**J-numbers.** These are Jake's numbered decisions: J1 to J381, one table row each, in §2 of `docs/plans/MULTI-REPO-SAGA/2026-11-04-opus-multi-repo-master-PLAN.md`. That file is 619 lines and about 75k tokens. Each plan also keeps its own D-numbers, and singleplayer has G- and E-numbers. The ones that matter for the voice note:

| Topic | Decision |
|---|---|
| Can a shard carry code? | **J341**: the upload is "only data and WASM"; there is "zero typescript or javascript in the… shardfile"; "TypeScript three.js code is how shard sources are written." Behaviour is AssemblyScript compiled to WASM. |
| Clean-room prototype then port | **J339**: shard source should be "JUST AS EASY… as a clean room single shot three.js + rapier project". **J344**: the next 3 zones each get a cleanroom first, then a port; after that, "agents author directly with `watch`". |
| Performance budgets | **J343**: MMO bar is 30 fps on phone and 60 on desktop; "cleanroom standalone prototype on iphone is 60 fps". **J303**: audio is green up to 6 MB, red over 10. **J98**: 5 GB of R2 for shardfiles. |
| Cell entry and size | **J352**: solid walls around each cell, entry only through 4 road gates, then a 5-second count and a loading screen ("Continuous grid crossing is too fucking hard"). **J320**: about 630×630 m loaded including roads. |
| Uploads and placement | **J379**: the API places every staging upload on a 7×7 grid. **J306**: each new version needs a new hero image. **J259**: shards must be "prepared" before upload. |
| Live-zone ports | **J340** puts them "out of scope for now". |

**Plan status (from each plan's State and Progress lines).**
- Active:

  | Plan | Rows done |
  |---|---|
  | SHARD-SOURCE | 157/200 |
  | ONE-FORMAT | 42/131 |
  | MMO-PLAN | 32/48 (date per J213: Friends grid, logins and public grid by 2026-11-23) |
  | ZONE-ENTRY | 54/70 |
  | NET-LAG | 14/30 |
  | WIRE-STABILITY | 17/24 |
  | OFFLINE | 22/24 |
  | NEW-SHARD-E2E | 4/12 |
  | SHARD-PUBLISH-ACTIONS | 6/11 |
  | SDK-SPLIT | 0/28 (only Part B approved) |
  | CI21-PORT | 0/11 |

  TEMPLATE-E2E and TEST-COVERAGE are also live.
- Waiting on Jake's review (`MACHINES.md`): SHARD-COMPAT, REPO-KIT, LEFTOVER-CLEANUP, MULTI-REPO-DEVELOPMENT, REPO-WEIGHT. `JAKE-READ-LIST.md` has 120 unticked boxes.
- Parked: MMO-MODERATION, MMO-PARTIES, MMO-ZONE-SELECT, PS5-FEEL, WWW-REDESIGN, NIGHTLY-MAC, ENGINE-BENCHMARKS, plus WASM-HOST and HOST-AUDIT.

## 2. Honest status

**Live (per `docs/plans/support/STATE.md`, not verified against the servers):**
- prod v0.1.29 with 25 cells; staging uses the 7×7 grid
- `api.wildshard.io` is v0.18.2
- `@wildshard/sdk` 0.3.4 is on npm

**What is broken or painful, per the docs:**
- **The outside-author path.** `project/archive/new-shard-e2e/REPORT.md`, 07:45 today: "Honeyknoll… **cannot ship**: five SHARD-SOURCE blockers… `watch`'s page never loads. Nothing reached staging." The friction log has 31 entries. Later rows (SS-NE30/31 in SHARD-SOURCE) say SDK 0.3.4 then uploaded a fresh shard with only an account key, and it was auto-placed at cell (1,3).
- **Cleanrooms are look-only.** "Neither cleanroom page has gameplay: they pose bandits and the Wyrm for shots" (`docs/content/2026-11-15-template-content-audit.md`).
- **Brasscap had nothing to fight.** Jake on 11-15: "No weapons to pick up… no enemies to shoot." Templates now get content rather than more graphics (J357).
- **Nine Dragon's look fix** landed at 19:49 and was still not on staging at 07:39, because only the MacBook could upload shards (`docs/process/2026-11-16-working-as-a-team.md`).
- **Engine main went red twice overnight** after shard pin bumps were pushed straight to main.

**Last two weeks (I checked git).** By meta commit scope, the top items are plans (1,572), multi-repo (238), test (148), one-format, state, qa, release, ci, pagesize, build and mmo. Engine has 2,440 commits since 11-02, sharddev 441, api-server 223, www 71. Most of the effort went into the repo split, CI and release machinery, the format, and multiplayer plumbing.

**Audits and attempts to simplify:**
- `REVIEW-OVERHEAD-AUDIT-2026-11-09`: "Review is not what cost us momentum." The real costs were the coordinator's quota running out (about 68 idle lane-hours) and Jake's read queue.
- `archive/CLOSE-OUT-STRATEGY-2026-11-10`: Jake said "There's too many in flight plans". It found 9 plans that could be archived at once.
- `archive/LAND-SIMPLIFY-PLAN`: deleted 8,694 lines of landing-queue machinery.
- Token audit in `AGENTS.md`: 81% of spend was cache reads. Another measurement found lanes spend 28% of their cost before their first edit.
- One-format audit: "There is one shard format, but not one way to use it." It found 41 server hosts and 37 page features that each serve exactly one shard, plus an engine gate that admits some features from first-party shards only.
- SDK-split audit: "it is worse than… the build runs the engine's simulation."

**Jake's frustration, in his words:**
- "test coverage and shard repos as plans are just too complicated, too nuanced" (J370)
- "All the LUT fucking around sure feels like a waste of time" (J337)
- "Grid crossing is still a meme / joke" (QA 11-14)
- "I don't know why it has to wait and verify everything on staging" (team report)
- "agents have to be autonomous, they have to make progress" (J381)

## 3. Process weight

**How much process (I read the files):**
- Meta `AGENTS.md` is 236 lines; engine's is 164; `HOW-WE-BUILD-PLAN.md` is 866.
- There are two working modes (J290): commit straight to main, or a `plan/<slug>` worktree that lands through `land.mjs`. Commits are pathspec-only. Hooks block files over 5 MB, secrets, and a `STATE.md` of 3 KB or more. Meta has 11 skills. There are 34 grill logs.
- Every request Jake makes goes into a dated QA-FEEDBACK file.
- Releases come from `release/vX.Y.Z` branches, daily plus on demand, and only the MacBook ships (J356, J362). Staging serves release candidates only.
- A new blocking test must run for 7 days before it can block a merge (J186).

**Time to get something live (my estimate from the docs):**
- **An engine change reaching main:** about 20–40 minutes. Each land takes 15–25 minutes of CI (median 18), plus a preflight before it.
- **An engine change reaching staging or prod:** hours to a day, because it waits for the next release cut on the MacBook.
- **A shard change:** each upload needs `wildshard prepare` (it downloaded a 296 MB client and timed out in WebKit at 180 s in the E2E run), a new hero image, and version fields. Until SHARD-PUBLISH-ACTIONS is finished, uploads ran from the MacBook only, and the Nine fix waited about 12 hours.
- **A brand-new zone:** SHARD-SOURCE's done-when (SS17) has never been reached. SS10e (Jake picks the first zone) is blocked on him.

**Parallel agents.** The MacBook runs 3 Opus, 1 buddy and 5 Codex agents plus a coordinator. The Mac mini runs 2 Opus and 3 Codex plus a coordinator. That is up to about 14 at once, and one measurement counted 417 lanes in about 24 hours. Coordination runs through git in meta: plan rows, `STATE.md`, QA files, `lane-receipts.log`, herdr, hourly coordinator checks, and J-numbers.

## 4. Coverage of the voice note

| Voice note asks for | What the repos already say |
|---|---|
| Clean-room three.js prototype, then "upload this" | **Mostly already intended** (J339, J344; SHARD-SOURCE stage 11). But the port is manual rewriting by agents, and each gap becomes a plan row. There is no automatic "upload this" command. The stated end state (J344) is to stop needing cleanrooms. |
| A canyon with enemy camps | **Already exists**: Brasscap Mesa, "low-poly sunset canyon, lever-action rifle", three tin-bandit camps and a Dust Wyrm boss (`TEMPLATE-E2E-PLAN.md:98`, BM-1 to BM-6). The prototype is `~/projects/games/wildshard/brasscap-cleanroom` (11 commits, 1,752 lines). |
| A looping train that teleports through tunnels | **Partly.** Nine Dragon has `nds-train` and a gondola, written in AssemblyScript (`shard-nine-dragon/src/behaviour/movers.as`). The format's `world.movers` (`shard-format/src/format/moverMotion.ts`) allows at most 10 keyframes per track, points within ±250 m, and loop modes once / repeat / pingpong. I found no teleport or tunnel concept. |
| "Two shard types: FPS and third-person action" | **Not in the docs.** I found zero hits for "two shard types". Everything is first-person. The game has "no third-person body of the player anywhere" (`archive/REMOTE-PLAYERS-PLAN.md:61`). Third-person shows up only in the parked PS5-FEEL plan (row PF16) and in a write-up of a competitor (Starwild). |
| Normalise the HUD | **No plan.** The HUD belongs to the engine, mockups use "our HUD", and the cleanroom has "no HUD". |
| Quests and collectibles | Required in the vision. The format has quests and "collectible sets" (W9b). J361 says templates are "MMO-ready from the start". |
| A zone authoring guide | Only sharddev's `GUIDE.md`. The E2E run found it had no scene-shard section (F10) and called itself SDK 0.2.x (F2). |

The biggest conflict is the voice note's "upload this prototype" against J341. Under J341, a three.js prototype cannot be uploaded as it is: sharddev has to compile it into data plus sandboxed WASM.

## 5. www.wildshard.io

**Stack (I checked).** Vite 8 static pages served by a Cloudflare Worker (`src/site/worker.ts`, 113 lines). All copy lives in `src/site/COPY.md` (2,324 lines). `src/` is about 8.3k lines, and the repo has 71 commits.

**What it promises:**
- Headline: "The infinite MMO in your browser." Subline: "Every shard of the world is built by a player."
- "Anyone can add a shard… describe it to Claude or any coding agent."
- Roadmap: "the Friends grid → sign-in → the public grid, all 25 shards → uploading your own shard."
- A waitlist for creator keys and "Founding Author" titles; "We never charge for uploading a shard."
- Co-editing with friends and renovating abandoned shards.

**Promises the product doesn't obviously keep yet:**
- Player uploads, co-editing and renovation don't exist yet.
- "Discord: coming" and "iOS and Android apps: coming".
- FAQ 1 still says "Not here yet: multiplayer", although STATE lists the MMO live on prod.
- The "Journey" timeline stops at 24 Oct.
- "About 99,000 lines of one-off code, to zero" conflicts with the one-format audit's one-shard hosts and first-party gate.
- The site says uploads need a creator key, but the API has made it optional since v0.18.1.

## 6. api-server

**Shape (I checked the code).** It is a Hono app on a Cloudflare Worker.
- Storage: Neon Postgres (8 migrations; PGlite locally), KV `API_CACHE`, three R2 buckets (shardfiles, records, packs read-only), a `wildshard-migrate` queue, and a daily prune cron.
- There is no D1, no Durable Objects, and no payments code.
- Size: 41,036 tracked lines in total; 19,545 in non-test `src`, 11,172 in tests, 4,864 in scripts.

**Lines by purpose (non-test):**
- **Uploading and publishing.** Upload routes (direct-upload, commit, placement and channel routes) about 1.5k, catalogue and grid 4.0k, signing 454, shardfile checks 393, storage 948, accounts 151. Together roughly 7.5k lines, which is what "upload a zone" needs.
- **Format migrations:** 1,478 lines. This is compat work.
- **Peripheral:** telemetry 1,097, errors and inbox about 0.9k, waitlist about 0.4k, delete and adopt about 0.5k.

**How a shard gets published (from `docs/architecture/api.md`):**
1. `wildshard prepare`, then `wildshard upload`.
2. `POST /api/shardfiles/uploads` returns a presigned R2 PUT.
3. `POST .../uploads/:hash/commit` runs a streamed shard-format check. It also checks the `wsk_` account key, versions and the new hero, claims the slug for the account, and handles the channel and staging auto-placement.
4. The API sends an HTTP notice to the MMO server.
5. A cook worker on the VPS makes packs, which go to the `packs.wildshard.io` CDN.

Clients read the list through `GET /api/catalogue`. Async upload (SDK-SPLIT Part B) is approved but no rows are built.
