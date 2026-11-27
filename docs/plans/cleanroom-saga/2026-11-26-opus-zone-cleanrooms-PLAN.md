# Eight zone clean rooms (ZC)

> Written by: Claude

> **State:** in progress, 2026-11-26: ZC1 done; concept art dropped
> (D40). ZC2 (art direction in the brief) is done for Signal Dunes and
> waits on Jake's review. Every row after ZC2 waits on Jake: he
> approves each zone's brief and description and runs its Fable
> session himself (D34). Ask: A19.

Saga: [cleanroom saga](2026-11-26-opus-cleanroom-saga-master-PLAN.md),
phase 1. Rules: D31–D36 in `docs/decisions.md`. Research §5 lists
each zone's sources.

## Why

Jake, 2026-11-26: *"in the saga we need to make cleanrooms of the
other 8 zones"*, and on the wrap-up: *"the 8 starter packs for the 8
cleanrooms"*, *"you can make the 9 draft concept arts for the 8
cleanrooms + the art refresh of brashwick"*.

## Rows

- [x] **ZC1 Starter packs for all eight.** Each zone gets a folder,
  `~/projects/game-demos/<slug>-clean-room`, after `git init` and
  with no GitHub. It holds:
  - `README.md`, the shared brief;
  - `ZONE-DESCRIPTION.md`, at the D32 bar, in the zone's own look and
    identity, naming nothing from Wildshard;
  - `concept/`, dropped by D40 (Signal Dunes done; the other seven
    lose theirs in ZC2).

  Copies live in `support/zones/<slug>/` here, with a `SOURCES.md`
  that the clean room never sees. The slugs are `signal-dunes`,
  `sky-reach`, `mossgate`, `brasscap`, `driftwood`, `pine-hollow`,
  `nalati` and `nine-dragon`. Done when all eight folders and copies
  exist, and each description has a main-quest boss, a level range
  and elites.
- [x] ~~**ZC2 Concept candidates.**~~ ~~**ZC3 Jake's review page.**~~
  Dropped by D40, 2026-11-26. 81 candidates were made and put on a
  review page (`7b08cd6`); Jake: *"they just dont look like real game
  screenshots, its all that openai sloppy vibe"*. The candidates were
  removed from the tree; the scripts stay in
  `support/concept-art/` as a record.
- [ ] **ZC2 Art direction in the brief.** No concept images: each
  brief carries a short art-direction bullet in the zone's own vibe,
  taken from its existing style docs, and says Fable sets the art.
  Signal Dunes first (done, waits on Jake's review); the other seven
  follow once he approves its wording. Done when all eight briefs and
  descriptions name no `concept/` and each has the bullet.
- [ ] **ZC4 Signal Dunes one-shot (pilot).** Jake runs Fable in the
  folder. Done when D33 holds: it plays on a phone to the Dune
  Matriarch (or whichever main boss the description names), an Opus
  audit scores the D32 bar, and the golden frames are shot. The
  brief's lessons go into the other seven briefs before the next run.
- [ ] **ZC5 The other seven, one at a time.** Same done-when as ZC4,
  zone by zone, in an order Jake picks.
- [ ] **ZC-F Phase 2 link.** The shard-format docs site at
  `format.wildshard.io` and the explainer artifacts are linked from
  the master plan. Done when both URLs resolve.

## Seams

- **Owns:** `support/zones/` here and the eight game-demos folders,
  until Jake takes each one over for its Fable run.
- **Phase 0** (the Showcase plan, CR4) makes the Brasswick concept art
  with the same tooling.

## Verification

ZC1–ZC3 are checked by reading the files and the review page. ZC4 and
ZC5 are checked by a phone playthrough, the audit and the frames.

## Sync

- `docs/decisions.md`: D31–D36 already hold the rules.
- `AGENTS.md`: none.
