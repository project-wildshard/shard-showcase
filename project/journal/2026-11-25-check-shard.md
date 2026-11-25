# wildshard check in pnpm check

Ask A11.md. `wildshard check .` fails outright with no shard source (UNRESOLVED_ENTRY shard.config.ts), which
would turn every push red for every lane on main. So `check:shard` (brasscap's name) is
`src/scripts/check-shard.mjs`: a note and a pass until `src/shard.config.ts` exists, then `wildshard check .`.

- Its author lint is type-aware now (A9), and sharddev runs oxlint without the pinned tsgolint: "Failed to find
  tsgolint executable". The script passes `bin-tools.mjs`'s `lintEnvironment()` (OXLINT_TSGOLINT_PATH).
- Proved with the `wildshard new --empty` source dropped in (removed after, with its build output): lint, build,
  validate, report pass; prove skips (no proof.json); a planted `any` fails lint.
- Found: `build` alone makes an "unprepared draft" api-server refuses; `wildshard prepare` (phone WebKit recording)
  must run on the built folder first. So `pack` = `wildshard build .` is not yet uploadable. For Jake.
- Bug from 6101906: `format:check` carried `--no-error-on-unmatched-pattern` and the commit hook appends it too, so
  any commit staging src/ code failed ("cannot be used multiple times"). The flag moved to `check`'s call.
