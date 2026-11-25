# shard-showcase: design

Status: draft 2026-11-05: scaffold only; the real design arrives with the import.

Living doc: **how** this repo is built. What it does and why is
`docs/prd.md`. Keep this true as the code changes.

## Today

Only the scaffold exists:

- `kit/scripts/`: repo-kit's tooling (asks, lint, md-wrap), plain JS.
- `src/test/.kit/`: tests of repo-kit's scripts.

## Dependencies

- `sharddev (build)`, by git tag (`github:project-wildshard/<repo>#vX.Y.Z`)
- `engine (runtime, via sharddev)`, by git tag (`github:project-wildshard/<repo>#vX.Y.Z`)

## Boundaries the checks enforce

- None yet beyond the shared lint and type rules.

## Coming with the import

- `src/shards/<slug>/`, once it has a shard
- `public/assets/<slug>/`
