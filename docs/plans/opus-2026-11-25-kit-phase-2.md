# Plan: A1 phase 2, the kit and the SDK fit the lean layout

> **State:** draft, 2026-11-25. Phase 1 of ask A1 is closed (Jake:
> "ok A1 phase 1 is closed"); these rows are what it deferred. Rows
> K1 to K4 and K6 change `../repo-kit` or sharddev: tell Jake before
> touching another repo.

Jake, A1: *"I really want ./src ./docs ./project if posible"*. This
repo now has that; repo-kit and sharddev still assume the old layout,
so the next stamp or `wildshard update` would undo or break it.

## Rows

- [ ] **K1 repo-kit stamps into `src/scripts/.kit/` and
  `src/test/.kit/`.** Its scripts, `bin-pins.json` and tests live
  there here (Jake: "src/scripts/.kit sounds good to me"); repo-kit
  still writes `scripts/` and `kit/`. Done when a repo-kit sync into
  this repo changes nothing.
- [ ] **K2 repo-kit's `sync.sh` runs here.** It calls `pnpm format`
  and `pnpm test:hooks`, which this repo dropped (Jake: "Repo kit sync
  will fail yes"). Done when `sync.sh` exits 0 against this repo.
- [ ] **K3 the herdr to hc port goes upstream.** `peers.sh`,
  `guard-hc-send.sh`, owner records and their fake-`hc` tests (A12,
  a8fa088) replace repo-kit's herdr versions. Done when a sync keeps
  them.
- [ ] **K4 drop dead kit tooling.** `land.mjs`, `worktree.mjs` (D29:
  main only) and `lint.mjs` (points at the deleted `kit/` config) are
  unused here. Done when repo-kit stops stamping them into this repo,
  or Jake keeps them.
- [x] **K5 `~/.claude/set-label.sh` labels the hc terminal.** Done in
  dotfiles 03cc526 by another agent: it runs `hc label
  $HC_TERMINAL_ID goal=<tag>`, so `peers.sh` shows the goal (t14 read
  `goal=showcase hygiene`, 2026-11-25).
- [ ] **K6 sharddev `wildshard update` fits this layout.** It writes
  real folders into `.claude/skills` (agent-sync owns that) and has
  no way to add GUIDE.md and the 4 skills without a template. Done
  when `wildshard update` brings GUIDE.md and the skills in and
  `pnpm check` stays green.
