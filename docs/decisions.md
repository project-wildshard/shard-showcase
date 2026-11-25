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
