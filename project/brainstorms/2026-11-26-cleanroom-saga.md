# Grill: the cleanroom saga

> Written by: Claude

> **State:** done, 2026-11-26. Goal: settle the
> cleanroom saga's open decisions (D1–D6 in its master plan) and
> anything they open up, so its phase 1 to 3 plans can be written.
> Settled answers are promoted to D-decisions in `docs/decisions.md`.

Plan and research live in `docs/plans/cleanroom-saga/`: the master
plan `2026-11-26-opus-cleanroom-saga-master-PLAN.md` and
`support/cleanroom-research.md`.

## Summary / key decisions

- **D1, budget:** each of the 8 zones gets one Fable one-shot only.
  An AAA push happens later, and only for zones Jake picks.
- **D2, scope: the zone bar.** Every zone description asks for:
  - enemies with levels, and content for at least levels 1–10 (to
    15 or 20 if the zone has room; only the Showcase must reach 20);
  - a main quest line with several steps, some side quests, and some
    NPCs to talk to;
  - at least one boss at the end of the main quest;
  - elites;
  - several weapons;
  - some peaceful content and some combat content.

  A town or hub, a mini dungeon and a raid-style boss are optional.
  Each zone is built around the identity it has now: *"improving
  existing zones"* while keeping *"some of the heart & charm of each
  original zone"*.
- **D3, pilot:** Signal Dunes goes first.
- **D4, builder:** Fable builds. The brief may say *"to save costs and
  tokens, delegate non-visual work to opus"*.
- **D5, upload:** decide the method after phase 2 (the shard-file
  explainer). Meanwhile, start bringing PROTOTYPE-TO-MMO and its ideas
  into this saga. Jake also asked which other meta plans (in review or
  draft) belong here (Q4).
- **D6, look:** each description names its zone's own look in plain
  words, and each clean room gets three new concept-art images that
  Jake approves.
- **Showcase re-look:** a restyle pass on Cratefall in its own repo,
  keeping its gameplay, against three new approved concept images.
- **Meta plans join the saga, moved here now:** PROTOTYPE-TO-MMO,
  PS5-feel, WASM-HOST, HOST-AUDIT and Procedural RPG lessons.
- **Concept art:** an agent makes about nine candidates per zone with
  Codex's default `image_gen`, recording the exact model on each image,
  and Jake approves three.
- **The camera rule** (every zone's brief, and the engine later):
  - third person by default; holstered and melee are third person
    only;
  - a ranged weapon drawn switches to first person, shooter style;
  - horseback is third person, and horseback archery is first person.
- **Stack in the brief:** TypeScript, three.js and Rapier, with no
  other upload hints.
- **Pacing:** after the pilot, the clean rooms run one at a time, and
  each run's lessons tune the next brief.
- **Authoring:** Opus drafts each zone description, and Jake reviews
  it, with its three concept images, on an artifact page.
- **Repos:** like Cratefall: `~/projects/game-demos/<zone>-clean-room`,
  `Raynos/<zone>-clean-room`, public, on GitHub Pages.
- **Order:** the Signal Dunes pilot first, then the Cratefall restyle.
- **Done bar per clean room:** playable on a phone from level 1 to the
  main-quest boss, an Opus audit against the D2 bar, and golden frames
  shot.
- **Who runs Fable:** Jake. Agents never spawn or prompt Fable; he
  starts each clean-room session himself in a new game-demos repo.
- **Handoff per zone:** a local folder,
  `~/projects/game-demos/<zone>-clean-room`, after `git init`, holding
  the brief, `ZONE-DESCRIPTION.md` and the three concept images. No
  GitHub repo; Jake creates that and Pages himself.
- **Cratefall restyle:** Jake's own Fable session. Agents make the
  concept art, get it approved, and write a restyle brief.
- **Phase 2 is a docs site plus artifacts:** a public docs website
  for the shard format, built in the shard-format repo and deployed to
  `format.wildshard.io` on Cloudflare (as www does). It has separate
  pages for humans and for agents (skills or markdown allowed). It is
  not a versioned spec: the public source code is the spec. Artifacts
  also explain things to Jake. It starts now, alongside the pilot prep.
- **Showcase look target:** the three new concept images are painted
  in the Kitchen Sink's orange-and-grey direction (ruling 19ab, the
  round-11 mockups). They become both the Cratefall restyle's target
  and the Kitchen Sink's.

## Q&A log

### Q1: Fable budget per zone (D1)
- Asked: one-shot only, one-shot plus a short push, or a full AAA push
  for each zone? (Showcase: 2.5 h one-shot, then about $580 of Fable
  on the AAA push.)
- Captured: one-shot only (the recommended option). An AAA push is
  opt-in, per zone, later.
- Flags: none.

### Q2: Scope of each zone description (D2)
- Asked: the full MMO-zone shape, the zone's own size with its own
  boss, or the full shape with a shared level curve?
- Captured (his own list, not one of the options):
  - *"Each zone must have enemies with levels, and content from at
    least level 1-10 ( only showcase goes to 20 ); if a zone
    description has enough 'space' to go to level 15 or 20 sure."*
  - Must have: a main quest line with several steps, some side
    quests, some NPCs to talk to, at least one boss at the end of the
    main quest, elites, several weapons, and some peaceful and some
    combat content.
  - Optional: a town or hub (*"does not need a town or hub, it
    depends"*), a mini dungeon, a raid-style boss.
  - *"Each zone is built around its core identity that it currently
    has."*
  - *"There are plans lying around in the old singleplayer repo to
    'renovate' and improve pinewood/nalati/driftwood so they all have
    'as much' content as each other."*
  - The aim: *"a combination of 'improving existing zones' along with
    'keep some of the heart & charm of each original zone'"*.
- Flags: find the singleplayer renovation plans for Pine Hollow,
  Nalati and Driftwood, and feed them into each description (owner:
  Claude, now).
  Found in SP `docs/plans/`:
  - `GW2-ZONES.md`, "Shards as fun as Guild Wars 2 zones": a draft
    from 2026-10-10; its rules moved to WORLDCLAW-SHARD and
    FINISH-LINE;
  - `gw2-zones/`;
  - `DRIFTWOOD-REMASTER-V2.md`, in progress on 2026-10-03.

  Also in SP `project/archive/`: `2026-09-23-driftwood-remaster.md`
  and `2026-09-25-pine-hollow-remaster.md`. Phase 1 reads these per
  zone.

### Q3: Pilot, builder, upload method, look (D3–D6)
- Asked four at once: the pilot zone, who builds, how mechanics get
  into Wildshard, and art direction.
- Captured:
  - **D3:** Signal Dunes (recommended).
  - **D4:** *"Fable builds, but the original prompt can say 'to save
    costs and tokens, delegate non-visual work to opus'"*.
  - **D5:** decide after phase 2: *"but also lets start taking
    prototype-to-mmo and its ideas into this saga. Is there any other
    plans in the meta repo that we should start taking into this
    saga, plans under review or draft ?"*
  - **D6:** options 1 and 2 combined: *"lets put some brand new
    concept art that I approve ( 3 images ) into each cleanroom."*
- Flags:
  - Survey meta's review, parked and draft plans for saga candidates
    (owner: Claude, now).
  - How concept art gets made and approved (next batch).

### Q3b: Re-look the existing one-shot (Jake, unprompted)
- Captured: *"Also as part of the saga we need to re-look the existing
  oneshot lol :( we need to make brand new concept art for it and
  restyle it somehow ..."*. This changes phase 0: before, Cratefall
  was read-only from here; now the saga restyles it.
- Meta plans that could join the saga (surveyed 2026-11-26 in
  `docs/plans/review/` and `parked/`):
  - PROTOTYPE-TO-MMO: primitives and the upload loop. Already in.
  - PS5-feel: look, feel, 60 fps; PF16 is the third-person spring
    arm.
  - WASM-HOST: the script host behind the primitives.
  - HOST-AUDIT: one-shard hosts and putting shard code back.
  - Procedural RPG lessons: small code-drawn art; review draft.
  - Engine benchmarks: phone budgets.
- Flags: the restyle method, and which plans join (next batch).

### Q4: Meta plans, how they move, the restyle, concept art
- Captured:
  - **Plans that join** (multi-select, all four ticked): PS5-feel,
    WASM-HOST, HOST-AUDIT, Procedural RPG lessons, plus
    PROTOTYPE-TO-MMO.
  - **How they come in:** *"Move them here now"*: git-move them into
    `docs/plans/cleanroom-saga/` and leave a pointer in meta.
  - **Restyle:** a restyle pass on Cratefall (recommended): keep its
    gameplay; change palette, materials and lighting, and take the
    neon out, against the new concept art.
  - **Concept art:** option 1, an image model with Jake picking, and
    he asked: *"its codex cli gpt image 2.6 right"*. Checked in the
    Codex rollouts the clean room spawned on 11-25 (57 files): the
    imagegen skill uses Codex's built-in `image_gen`, and its CLI
    fallback defaults to `gpt-image-2`. No "2.6" appears there.
    `gpt-image-1.5` is the fallback it must ask about first.
- Flags:
  - Moving files out of meta is an edit in another repo: do it at
    wrap-up, with meta's `scripts/plan-move.mjs` rules in mind (owner:
    Claude).
  - Confirm the image model name, gpt-image-2 or a newer "2.6" (owner:
    Jake).

### Q5: Image model, camera, portability, pacing
- Captured:
  - **Image model:** Codex `image_gen` default (recommended).
  - **Camera:** *"I've decided that I want third person camera, but I
    also want all of the ranged weapons to basically be first person
    camera like a shooter, so when you swap to a ranged weapon it goes
    first person. and when you hostler weapon it goes third person,
    melee is third person only. horseback is third person, horseback
    archery is first person again"*.
  - **Portability:** *"typescript, three.js, rapier."* The brief
    names the stack, Rapier included, and nothing more about porting.
  - **Pacing:** one at a time (recommended).
- Flags: the camera rule is also an engine requirement for phase 3
  (the third-person and shooter pieces), and Cratefall partly differs
  today (aiming goes first person; does drawing a ranged weapon?).
  Check it in the restyle (owner: Claude).

### Q6: Authoring, repos, order, done bar
- Captured: Opus drafts and Jake reviews (recommended); repos like
  Cratefall (recommended); pilot first, then the restyle; done is the
  boss on a phone plus an audit (recommended).
- Steering (unprompted): *"btw you dont spawn fables or prompt fables,
  ill handle all that myself in new game demos clean rooms"*. So the
  saga's agents prepare the inputs (the description, the brief, the
  concept art) and do the audits. Jake runs every Fable session.
- Flags: none.

### Q7: Handoff, restyle runner, phase 2, Kitchen Sink look
- Captured:
  - **Handoff:** "Repo, no GitHub": a local folder after `git init`
    with the files.
  - **Restyle:** Jake's Fable session (recommended).
  - **Phase 2:** *"We definitely want an artifact, but more importantly
    we want an entire docs website deployed `format.wildshard.io` from
    shardformat ; its "*. His answer was cut off there.
  - **Look:** new art in the Kitchen Sink style (recommended).
- Flags: finish Jake's phase 2 sentence, and settle the docs site's
  build, host and timing (next batch).

### Q8: Phase 2's docs site, its host and timing; wrap-up
- Captured:
  - *"we need a publicly hosted docs website for the format in the
    format repo but i also need artifacts to explain wtf is going on
    to me. The site is for humans & agents, we can put some skills or
    md on there too. It should have different pages for humans and for
    agents etc. Its not a public, versioned spec … i think the public
    github repo the source code should be the spec lol. It just needs
    to be human readable docs, agent readable docs"*.
  - **Host:** Cloudflare, like www (recommended).
  - **Timing:** start now (recommended).
  - **Wrap-up:** *"Yes, do it all"*: promote the decisions, update the
    plans, move the five meta plans here with a pointer left in meta,
    and commit and push both repos. Jake had to leave.
- Flags: none.

## Parking lot (tangents / parallel threads)

- Jake prefers up to 4 questions per question-tool call (2026-11-26).

## Open flags (pending input)
