# shard-showcase: decisions

Living doc. Decisions that bind this repo, newest last. Cross-repo
decisions (J-numbers) are Jake's and live in
`Raynos/project-wildshard-meta` `docs/plans/MULTI-REPO-SAGA/decisions/`;
this repo's own are D-numbers. The Kitchen Sink plan's rulings (§2) bind
the shard itself.

- **D25**: 2026-11-04: a commit of 30+ changed lines stages a
  `project/journal/` entry (`.githooks/pre-commit`).
- **D27**: 2026-11-04: main only. Superseded by D29.
- **D28**: 2026-11-05, tightened 2026-11-25 (A9): the strictest lint
  on `src/`: every oxlint category an error, nursery too, type-aware,
  unused disable directives are errors; strict `tsc`.
- **D29**: 2026-11-24: many agents on `main` only: no worktrees, no
  `plan/*` branches, no `land`. Replaces D27 and its 2026-11-12
  relaxation (meta J240, J290). Jake: "put this repo into 'many agents
  on main only, no worktrees, no landing' mode". The pre-push gate runs
  the same `pnpm check` as CI, so landing's CI wait bought little.
- **D30**: 2026-11-26 (A19): the cleanroom saga lives in this repo,
  in `docs/plans/cleanroom-saga/`, after meta's multi-repo saga. It
  covers Fable clean rooms of all nine zones, then the path that gets
  them into Wildshard. Jake: "This is going to become a saga lol".
  Grill: `project/brainstorms/2026-11-26-cleanroom-saga.md`.
- **D31**: 2026-11-26: each of the 8 zone clean rooms gets one Fable
  one-shot only. An AAA push happens later, and only for zones Jake
  picks (the Showcase's push used the whole allowance, about $580).
- **D32**: 2026-11-26: the zone bar. Every zone description asks for:
  - levelled enemies and content for at least levels 1–10 (15 or 20
    if the zone has room; only the Showcase must reach 20);
  - a multi-step main quest, side quests and NPCs;
  - a boss at the end of the main quest;
  - elites;
  - several weapons;
  - peaceful and combat content.

  A town or hub, a mini dungeon and a raid boss are optional. Each is
  built around the zone's current identity, *"improving existing
  zones"* while keeping *"the heart & charm of each original zone"*.
- **D33**: 2026-11-26: Signal Dunes is the pilot. After it, the clean
  rooms run one at a time. One is done when it plays on a phone from
  level 1 to the main-quest boss, an Opus audit passes D32, and its
  golden frames are shot.
- **D34**: 2026-11-26: Jake runs every Fable session himself; agents
  never spawn or prompt Fable. Agents hand him a starter pack, a local
  `~/projects/game-demos/<zone>-clean-room` folder after `git init`
  (no GitHub), holding:
  - the brief (`README.md`);
  - `ZONE-DESCRIPTION.md`, drafted by Opus and reviewed by Jake;
  - `concept/`.

  The brief names TypeScript, three.js and Rapier, and says *"to save
  costs and tokens, delegate non-visual work to opus"*.
- **D35**: 2026-11-26: the camera rule, for the clean rooms and later
  the engine:
  - third person by default, and melee is third person only;
  - drawing a ranged weapon switches to first person, like a shooter,
    and holstering goes back to third person;
  - on horseback it's third person, and horseback archery is first
    person.
- **D36**: 2026-11-26: art direction. Each zone description names
  the zone's own look in plain words, and each clean room gets three
  concept images Jake approves. They are picked from about nine
  candidates made with Codex's default `image_gen`.
  The Showcase's new concept art is painted in the Kitchen Sink's
  orange-and-grey style (ruling 19ab). It is the target for both a
  Cratefall restyle and the Kitchen Sink. Jake runs the Cratefall
  restyle in his own Fable session, after the pilot. Cratefall's
  quality is the bar; its art direction is not (A18).
- **D37**: 2026-11-26: phase 2 is a public docs site for the shard
  format, built in the shard-format repo and served at
  `format.wildshard.io` on Cloudflare, like www. It has pages for
  humans and pages for agents, plus artifacts that explain things to
  Jake. It is not a versioned spec: *"the public github repo the
  source code should be the spec"*. Started 2026-11-26.
- **D38**: 2026-11-26: five meta plans move into the saga:
  PROTOTYPE-TO-MMO, PS5-feel, WASM-HOST, HOST-AUDIT and Procedural RPG
  lessons. How clean-room mechanics get into Wildshard (a host per
  mechanic, or primitives) is decided after phase 2.
- **D39**: 2026-11-26: plans are named
  `<date>-<model>-<title>-PLAN.md`, with the date and model of the
  plan's first commit, as in meta's `a80a03d8`.
