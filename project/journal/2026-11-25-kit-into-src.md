# kit/scripts and bin-pins into src/scripts/.kit

Jake's call (A1 steering). `kit/scripts/*` (8) and `kit/bin-pins.json` now sit in `src/scripts/.kit/` beside the
rest of repo-kit's scripts. `kit/` keeps only `.oxlintrc.json` and `.oxfmtrc.json`.

- Depth fixes in the moved files: `asks.mjs` finds the repo three folders up; `bin-pins.mjs` reads its new path.
- Callers repointed: the agent hooks (session brief, herdr guard, md-prose-width), five skills, the hook tests and
  their sandbox copies, `check-index.mjs`'s run-the-hook-suite trigger, ci.yml, package.json, AGENTS.md, docs and
  the asks README. A bulk sed doubled one path in `bin-pins.mjs` (caught by running it).
- Found on the way: the kit's scripts were never linted or format-checked. Both kit configs ignore `scripts/**`,
  which oxlint and oxfmt resolve from `kit/`, i.e. `kit/scripts/**`. So `pnpm lint` checked nothing; run strict,
  `asks.mjs` alone has 175 errors. I told Jake earlier they were the only code linted: wrong. Nothing lost by the
  move; the shard lint is A9.
