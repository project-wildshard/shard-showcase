# Plans take meta's names

Jake: "in the meta repo we renamed the plan files, can you do that
naming convention here". Meta's a80a03d8 names a plan
`<date>-<model>-<title>-PLAN.md`, using the date and model of its first
commit.

- KITCHEN-SINK.md becomes `2026-10-20-opus-kitchen-sink-PLAN.md`. Its
  first commit was singleplayer `3c27cc76f3` (2026-10-20, Opus, the
  parked v1, G525). Its links in docs/ and the tracker source follow.
  The journals keep the old name, because they are history.
- The SDK 0.5 plan keeps its name for now: `t14` is archiving it
  (A17).
- The kitchen-sink-v2 mini plans are sub-documents, as in meta's
  support/, so they keep their names.
- The name check in `.githooks/check-index.mjs` and the write-plan
  skill still describe the old `<model>-<date>-<slug>.md`. Both are
  stamped from repo-kit, so the fix goes there. Until it does, a new
  plan named the meta way gets a warning, not a refusal.
