# Prototype to MMO: an engine of primitives

> Moved from meta `docs/plans/parked/2026-11-22-fable-prototype-to-mmo-PLAN.md` at `386423cbea` into the cleanroom saga (D38, 2026-11-26).

> Written by: Claude

> **State:** draft, parked, 2026-11-22. A holding plan so the idea isn't lost; nothing is built, scheduled or assigned
> to a lane. The thinking is in [docs/prototype-to-mmo/](support/prototype-to-mmo/README.md). Every row waits for Jake to
> promote it. It is its own saga, not part of MULTI-REPO-SAGA (Jake, 2026-11-16).

> **Progress:** 0 of 7.

## Why

Jake, 2026-11-22: *"This prototype to mmo concept and all its files, can we add a draft parked plan in ./docs/plans to
cover it ? otherwise ill lose it."*

The concept, in his words of 2026-11-16 (four voice notes, kept in
[evidence/2026-11-16-voice-notes.md](support/prototype-to-mmo/evidence/2026-11-16-voice-notes.md)):

- The author's loop: an hour to vibe-code a clean-room three.js prototype of a zone, then a second hour telling the CLI
  "upload this to the MMO" and adding the MMO's features.
- The real question: *"How do you beef up the engine 1,000 times, 1,000,000 times, such that really cool ideas can be
  uploaded into the MMO? And how do you do that in a way where we don't add hundreds of custom sections, hundreds of
  hosts to the API? How do you do that out of composable, simpler, lower level primitives?"*
- The fixed rule: *"People are going to be uploading content to my MMO server, and I'm going to be running it, and I'm
  not going to be running arbitrary fucking free JS, arbitrary TypeScript."*
- The method: *"if I get a chance to implement 100 ideas, and every idea we just like expand and generalize the
  engine... then we can iterate to the future."*
- Where it lives: *"a brand new saga"*, *"nothing to do with multi-repo, nothing to do with shard platform"*, *"far too
  early to be planning"*. That is why this file is a short pointer with coarse rows, not a build plan.

## What the strategy says, in five lines

1. Since October the shards' one-off TypeScript went to zero by moving into the engine, not into the shards. On
   2026-11-16, 41 of 46 server hosts and 37 of 63 page kinds served exactly one shard.
2. It keeps happening for three reasons: the server has no general "thing" a script can act on; the script layer can't
   hold a whole mechanic yet; and reusable gameplay has nowhere to live except the engine.
3. The answer keeps the hosting rule and AssemblyScript, and moves gameplay: a small engine core of about fourteen
   primitives, a shared library of mechanics written in AssemblyScript and shipped with the SDK, and one script
   interface (the v2 host, finished and stripped of mechanic-specific operations).
4. The method is Jake's hundred ideas. An idea may widen a primitive; it may never add a section, a host or a script
   operation named after a mechanic.
5. Thirty-six of thirty-seven test ideas need only ten primitives between them. The one that doesn't fit is base
   building.

## Context a fresh reader needs

Read in this order. Everything is under [docs/prototype-to-mmo/](support/prototype-to-mmo/).

| File | What it is |
|---|---|
| [README.md](support/prototype-to-mmo/README.md) | What the folder is, how it was made, and how far to trust it |
| [STRATEGY.md](support/prototype-to-mmo/STRATEGY.md) | The main document: one-page summary, the history, the primitives, the script layer, the format, a way there, risks, five questions |
| [IDEAS.md](support/prototype-to-mmo/IDEAS.md) | Thirty-seven zone ideas (Jake's sixteen and twenty-one more) and the primitives each leans on |
| [BRAINSTORM.md](support/prototype-to-mmo/BRAINSTORM.md) | Options weighed, including the rejected first strategy (trusted TypeScript shards) |
| [evidence/](support/prototype-to-mmo/evidence/) | Jake's four notes, twelve repo, history and precedent studies |

**The facts are dated 2026-11-16.** The folder was written from a read-only study on that day and nothing in it was
run. The repos have moved since: ONE-FORMAT went from 42 of 134 rows to 348 of 380, and the plans were regrouped into
sagas. Row PTM2 re-checks the numbers before anyone leans on them.

## Rows

The rows are coarse on purpose. They are the proofs and decisions that come before any build, and each would be split
into lane-sized rows when promoted. The code they name lives in the engine, shard-format and sharddev repos.

| Row | Work | Done when |
|---|---|---|
| PTM1 | **Jake reviews the strategy.** He reads the one-page summary in STRATEGY.md and answers the five questions in its section 12 | His answers are written under "Open decisions for Jake" below with the date, and this State line names which rows he promoted, or says the idea is dropped |
| PTM2 | **Refresh the facts and settle the overlap.** Re-count sections, page kinds, server hosts and one-shard hosts at today's heads; re-read ONE-FORMAT and WASM-HOST; say for each whether this strategy re-aims it or leaves it alone | STRATEGY.md's section 2.2 carries today's counts with the commits they were read at, and section 11 says how this relates to ONE-FORMAT and WASM-HOST on Jake's word |
| PTM3 | **Measure 30 Hz scripts on a phone.** Run the script-host benchmark that WASM-HOST's row H0 built, at 20 and 40 active scripts | The reading (p99 script time per frame) is saved in `project/evidence/prototype-to-mmo/`, with a yes or no against the 1 ms target and what it means for the primitive list |
| PTM4 | **The smallest proof: one mechanic leaves the engine.** Rewrite the ladder and the zipline as shared-library AssemblyScript in sharddev and delete the engine's `ladder.ts` and `cableTraversal.ts` | The engine's ladder and zipline tests pass with those two files gone, a shard that uses them still plays, and no count in shard-format `docs/ONE-WAY.md` rose |
| PTM5 | **One rules file, two compilers.** Try AssemblyScript's portable library: the same fixed-step rules file compiled by the TypeScript compiler for a clean-room page and by the AssemblyScript compiler for a shard | A sample in sharddev gives the same outputs for the same inputs both ways, or a note says why it can't and what the prototype conventions should be |
| PTM6 | **One idea by the two-hour loop, timed.** Pick an idea from IDEAS.md, build the clean-room prototype, then upload it | The prototype and the shard both exist, and a note records the hours spent and every place the engine or the format had to change to take it |
| PTM7 | **Ship and verify end to end** | Staging shows a zone made by the two-hour loop, with two players in it and playable on the phone, whose mechanics are library or shard AssemblyScript and which added no section, host or mechanic-named script operation |

**Later, not rows yet.** STRATEGY.md's section 9.4 gives an order of generalising, each step pulled by an idea: (A) the
script interface and the shared library, (B) entities with parents, (C) movement modes as predicted scripts, (D)
abilities for weapons and hit zones as parts, (E) creatures on shared senses and steering, (F) a third-person body and
animation with events, (G) space fields. They become rows only if Jake promotes this plan after PTM1.

## Seams

- **WASM-HOST** ([MULTI-REPO-SAGA/SHARD-SAGA/WASM-HOST.md](2026-10-20-opus-wasm-host-PLAN.md)): draft, parked.
  The strategy's first move is to take it off the shelf with a changed aim (operations about entities and state, not
  taming). That is Jake's call in PTM1; this plan starts nothing there.
- **ONE-FORMAT** ([MULTI-REPO-SAGA/SHARD-SAGA/ONE-FORMAT-PLAN.md](https://github.com/Raynos/project-wildshard-meta/blob/main/project/archive/ONE-FORMAT-PLAN.md)): live.
  Its rule "a host a second shard would want becomes an engine primitive" is the one the strategy would change to "goes
  in the shared library". Nothing here edits that plan.
- **HOST-AUDIT** ([MULTI-REPO-SAGA/HOST-AUDIT.md](2026-10-22-opus-host-audit-PLAN.md)): parked. Same ground, older.
- **Files this plan owns:** this file and `docs/prototype-to-mmo/`. It owns no code.

## Verification

Nothing is built, so nothing is verified. When rows are promoted, the checks live in the repos that own the code: the
engine's traversal tests for PTM4, sharddev's script build for PTM5, and a staging walk for PTM7.

## Sync

- `MULTI-REPO-MASTER-PLAN.md`: none. Jake, 2026-11-16: its own saga, "nothing to do with multi-repo".
- `MULTI-REPO-SAGA/STATE.md`: none. Nothing live changes and no lane holds it.
- `docs/README.md`: the `prototype-to-mmo/` row now links this plan.
- `AGENTS.md`, agent section: one row in the "Cross-repo plan" table pointing here.
- J-numbers: none taken. Jake's answers in PTM1 would be the first.

## Open decisions for Jake

From STRATEGY.md section 12. Unanswered as of 2026-11-22.

1. Is the rule right that reusable gameplay goes into a shared AssemblyScript library, and the engine takes only what
   needs speed, trust or shared feel? It would turn boss, riding, patrol and grapple into library modules.
2. Does the WebAssembly host plan come off the shelf, re-aimed at entities and state?
3. Is a general entity with a parent acceptable, with declared pools as the budget guard?
4. May an upload change how the player moves?
5. Which idea goes first: the train (parenting), Nine Dragon (movement) or infiltration (senses)?
