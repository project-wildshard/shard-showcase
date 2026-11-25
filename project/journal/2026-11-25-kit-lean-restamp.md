# Re-stamped from repo-kit's lean layout

Jake asked repo-kit's agent to make this commit (repo-kit plan
`opus-2026-11-25-shard-lean-layout`, S1 and R1). Showcase was where
the lean layout started. repo-kit folded its one-off edits back in, so
this stamp mostly brings the kit's copies up to date, as listed in
repo-kit `docs/showcase-restamp.md`:
- **Publish scripts:** they are kit-owned now, in `src/scripts/.kit/`
  with `publish-cook.yml`. Our own `src/scripts/publish-*.mjs` and
  `typecheck.mjs` are gone, and `typecheck` runs the `.kit` copy.
- **Land:** land, worktree and lint.mjs are retired, because Showcase
  is main only (no `land.config.json`).
- **Agent tooling:** the agent hooks and skills come from repo-kit
  (hc, the new guards), along with scratch-dir and scratch-sweep.
- **Node:** `engines.node` gets an upper bound, per the kit's new
  node-engines check.

Still to come: `src/scripts/.kit/bin-pins.json` stays as is until
repo-kit's L4 moves bins to pnpm (npm-bin-deps fix first). U3 in the
sdk-0.5 plan ticks after that.

## L4: one bin cache (later the same day)

The bins moved to the kit's pnpm profile on npm-bin-deps 2.2.0, with
`binDependenciesProjectSettings: false`: npr no longer copies our pnpm
overrides into `.bin-deps/`, so we share one cache entry with every repo.
The re-stamp also brought the kit's newer hook, publish and main-push
files. The kit plan is all `same`.
