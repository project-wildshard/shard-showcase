# Root scripts/ into src/scripts

Jake's call (A1 steering): repo-kit's scripts go to `src/scripts/.kit/`, the repo's own two
(`publish-shard`, `publish-preflight`) to `src/scripts/`. The root `scripts/` is gone; nothing was deleted.

- The moved kit files stay byte-identical except where the depth matters: five that find the repo root from
  their own folder (`'..'` became `'../../..'`) and `lane-live`'s import of `.agents/hooks/active-hours.mjs`.
  The two publish scripts import `./.kit/wildshard-agent-requests.mjs`. Usage comments inside still say
  `scripts/`; left as repo-kit wrote them.
- Callers repointed: package.json, ci.yml (store layout), publish.yml (every step, the sparse checkout,
  and the optional `select-candidate.mjs`, now looked for in `src/scripts/`), the session brief, the
  prepare-to-exit skill, the hook tests' sandboxes, the kit tests, AGENTS.md and the docs.
- `agent-parity.mjs`'s `KIT_SCRIPTS` still names `scripts/agent-*.mjs`: those are repo-kit's paths, and a
  `--kit` audit would now call them missing. Phase 2 (repo-kit learns the new home) fixes that, and a
  repo-kit sync before then would re-stamp a root `scripts/`.
