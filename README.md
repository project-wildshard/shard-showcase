# shard-showcase

> Written by: Claude, at Jake's request (A10). Humans own this file.

The Showcase: a Wildshard shard, shaped like shard-brasscap. The shard
source will live in `src/`; it is not there yet.

## Use

```sh
pnpm install     # deps, pinned tools, git hooks
pnpm dev         # wildshard dev .
pnpm build       # wildshard build . (pack is the same)
pnpm check       # the gate: lint, typecheck, format, tests
pnpm fix         # apply lint fixes and formatting
```

Lint (`.oxlintrc.author.json`) and types (`tsconfig.json`) are as strict
as they go.

## Layout

- `src/`: the shard source. `src/scripts/` and `src/test/` hold repo
  tooling; their `.kit/` folders are repo-kit's.
- `docs/`: living docs (`docs/dev.md` for the dev rules).
- `project/`: history and journal.

Agents: start at `AGENTS.md`.
