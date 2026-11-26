# Plan: shard-showcase takes SDK 0.5.0 and the new repo-kit

> **State:** done, 2026-11-26, archived on Jake's word, A17: "ask me
> any questions or decisions to finish and archive
> opus-2026-11-25-sdk-0-5-and-kit.md". U1 7c0fe6d + a27e836 (sdk 0.5.1,
> src/static, out/), since moved to 0.7.0 (a601dfb); U2 in 7c0fe6d
> (skills in .agents/skills, docs/GUIDE.md); U3 d1400c8; U4 f7d8ca0
> with repo-kit 5ef37f7 (Jake: "delete CLAUDE.md here, delete CLAUDE.md
> in repo-kit just fucking do it"). A1 phase 2; its kit rows K1-K4
> moved to repo-kit `docs/plans/opus-2026-11-25-shard-lean-layout.md`
> (repo-kit f970ade). K5 was done in dotfiles 03cc526.

## Rows

- [x] **U1 Upgrade to SDK 0.5.0.** Its migrate codemod (sharddev
  fd5dd864) moves public/ to src/static/. Repoint `pack`, .gitignore
  and docs/dev.md from public/shardfiles/ to the new build output.
  Done when `pnpm run pack` writes an sdk 0.3 shard file and
  `pnpm check` is green.
- [x] **U2 `wildshard update --guide docs/GUIDE.md`.** The four skills
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
- [x] **U4 Delete CLAUDE.md.** Claude Code ≥ 2.1.277 reads AGENTS.md
  itself (code.claude.com/docs/en/memory); repo-kit's
  `agent-parity.mjs --strict` still calls a missing CLAUDE.md a gap,
  and another agent is fixing that there (Jake, 2026-11-25). Done when
  the re-stamped parity check accepts AGENTS.md alone and CLAUDE.md is
  gone with `pnpm check` green.
