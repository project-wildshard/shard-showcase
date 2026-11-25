# Plan: shard-showcase takes SDK 0.5.0 and the new repo-kit

> **State:** held, 2026-11-25: waits on sharddev 0.5.0 (being cut) and
> repo-kit's lean-layout plan. A1 phase 2; its kit rows K1-K4 moved to
> repo-kit `docs/plans/opus-2026-11-25-shard-lean-layout.md` (Jake:
> "yeah move the plan into the repokit repo", repo-kit f970ade). K5,
> set-label writing the hc goal, was done in dotfiles 03cc526.

## Rows

- [ ] **U1 Upgrade to SDK 0.5.0.** Its migrate codemod (sharddev
  fd5dd864) moves public/ to src/static/. Repoint `pack`, .gitignore
  and docs/dev.md from public/shardfiles/ to the new build output.
  Done when `pnpm run pack` writes an sdk 0.3 shard file and
  `pnpm check` is green.
- [ ] **U2 `wildshard update --guide docs/GUIDE.md`.** The four skills
  land in .agents/skills/ (sharddev b6214533), then `pnpm agents:sync`;
  GUIDE.md sits under docs/ so the top level stays lean (A1). Done
  when the skills load and `agent-sync --check` stays green.
- [x] **U3 Re-stamp from repo-kit** once its K1-K4 ship. Done when the
  stamp changes nothing here, shard-showcase leaves repo-kit's
  `test/tooling/cleanup-coverage-pending.json`, and `pnpm check` is
  green. Then archive this plan.
  **Done 2026-11-25:** d1400c8 (lean) and the L4 bin-cache re-stamp;
  repo-kit `kit.mjs plan` is all `same`, the pending list no longer
  names showcase, `pnpm check` green. The plan stays open for U1, U2,
  U4.
- [ ] **U4 Delete CLAUDE.md.** Claude Code ≥ 2.1.277 reads AGENTS.md
  itself (code.claude.com/docs/en/memory); repo-kit's
  `agent-parity.mjs --strict` still calls a missing CLAUDE.md a gap,
  and another agent is fixing that there (Jake, 2026-11-25). Done when
  the re-stamped parity check accepts AGENTS.md alone and CLAUDE.md is
  gone with `pnpm check` green.
