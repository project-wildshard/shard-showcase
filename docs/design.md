# shard-showcase: design

Status: active 2026-11-25. Rewritten to match the repo (ask A15).

Living doc: **how** this repo is built. What it is for and why is
`docs/prd.md`. Keep this true as the code changes. Commands and code
rules are `docs/dev.md`.

## Layout

The top level is `src/`, `docs/` and `project/` (ask A1), plus the
configs tools look for at the root.

- `src/shard.config.ts`: the build entry `wildshard` loads.
- `src/generators/`: the shard source. Today a placeholder scene
  (`defineShard`): a blue sky, flat green ground, a sun, a spawn point.
  The Kitchen Sink slices replace it.
- `src/scripts/.kit/`, `src/test/.kit/`: repo-kit's tooling and its
  tests, stamped from `../repo-kit`. Edit them there, not here.
- `src/scripts/`: this repo's own scripts (typecheck, check-shard,
  publish).
- `.agents/`, `.githooks/`: agent hooks and skills, git hooks.

## Build

`wildshard build .` bakes `src/` into a draft shard file in `out/`
(gitignored). `pnpm run pack` then prepares it in phone WebKit and
builds again: the sdk 0.3 file upload accepts.

## Dependencies

- `@wildshard/cli` and `@wildshard/sdk` (sharddev), pinned in
  `package.json`; the engine comes in through them.
- `@wildshard/format` (shard-format), the shard file schema.
- `three`, for scene authoring.

## Boundaries the checks enforce

- Strictest lint on `src/` (every oxlint category, nursery included,
  type-aware) and strict `tsc` (D28, ask A9).
- `wildshard check`: lint, build, validate and report on every push.
- Main only, many agents, commits by pathspec (D29).

## Open tension

R-2 says **0 % custom TypeScript**, but today's placeholder scene is a
TypeScript module. It stays until the first slice puts data and shared
hosts in its place.
