# Developing shard-showcase

Living doc: commands, layout, code rules and git hooks. AGENTS.md links
here; what the repo does is `docs/prd.md`, how it is built `docs/design.md`.

## Commands

Run from the repo root.

- `pnpm install`: installs deps and points `core.hooksPath` at `.githooks/`.
- `pnpm dev` / `pnpm build`: `wildshard dev .` / `wildshard build .` on the shard
  source in `src/` (once it exists).
- `pnpm check`: the one gate (pre-push and CI): lint, format:check, test,
  then the kit and agent checks.
- `pnpm test`: every `node:test` file (`src/test/.kit/`, `.githooks/`,
  `.agents/hooks/test/`).
- `pnpm fix`: the hooks only check; this fixes lint and format.
- `node src/scripts/.kit/md-wrap.mjs <file>`: rewraps Markdown prose to ~72 columns.
- `src/scripts/.kit/ask-new.sh "<Jake's words>"`: opens an ask (`docs/tasks/asks/README.md`).

## Layout

The root stays thin: README.md and AGENTS.md (humans only), CLAUDE.md
(`@AGENTS.md`), package.json, pnpm-lock.yaml, .npmrc, .gitignore,
.editorconfig, `docs/`, `project/`, `src/` and the dot dirs. Scratch
goes in `tmp/<task>/` and is deleted when done.

- `src/scripts/.kit/`: repo-kit's tooling (asks, lint, md-wrap), plain JS.
- `src/test/.kit/`: tests of repo-kit's scripts (hidden, beside the shard source).
- `src/`: the shard source, like shard-brasscap's (not yet imported).
- `docs/`: living docs. `docs/plans/` is the queue, `docs/tasks/asks/`
  the receipts.
- `project/`: history. `journal/`, `origins/` (the meta-repo plans this
  repo came from), `archive/`.

## Code rules

- TypeScript only, imports with explicit `.ts`/`.tsx` extensions.
- Every function has an explicit return type. `kit/.oxlintrc.json` denies
  every category (D28); disable a rule only with a one-line reason beside it.
- Pin dependencies exactly (`.npmrc` has `save-exact=true`).
- Other Wildshard repos are git dependencies pinned by tag
  (`github:project-wildshard/<repo>#vX.Y.Z`). They are private, so CI reads
  them with the org GitHub App token.
- Tests use real things (git in temp dirs, real files and processes); never
  mock git. No LLM, `claude`, herdr or network in tests.

## Git hooks

| Hook | Checks | Bypass |
| --- | --- | --- |
| commit-msg | Conventional Commits subject ≤ 50, body ≤ 72, one `Assisted-by: AGENT:MODEL` trailer, no AI `Co-Authored-By` | `SKIP_ATTRIB=1` (human-only commit) |
| pre-commit | `main` in the main checkout (D27), staged set echo, whitespace, 1 MB cap, credentials, sh / mjs syntax, new-plan Status line, journal (D25) | `ALLOW_BRANCH=1`, `ALLOW_BIG=1`, `ALLOW_SECRET=1`, `SKIP_JOURNAL=1` |
| pre-commit | lint + format:check on staged code (typecheck too, once a `typecheck` script exists); 8 s budget | `SKIP_BUDGET=1` (time only), `SKIP_CHECK=1` |
| pre-push | outgoing commits: size, credentials, syntax; then `pnpm check` | `ALLOW_BIG=1`, `ALLOW_SECRET=1`, `SKIP_CHECK=1` |

Bypasses are for the case they name, never for a red gate: fix the code,
not the gate.

## Global-store trial

The root default stays off until the ordered GVS rollout.
Use `pnpm install --frozen-lockfile --config.ci=false
--config.enableGlobalVirtualStore=true` for the isolated trial.
The engine0.1.0 extension declares its installed author-tool edges using
this repository's existing versions; all source pins stay unchanged.
Hosted CI installs the real store and configures its cache with CI=true.
This scaffold currently has no authored shard directory or product.
An installed CLI or zero-product build is not a gameplay boot proof.
