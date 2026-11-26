# No CLAUDE.md

A17, finishing the sdk-0-5-and-kit plan. Jake on its last row, U4:
"just fucking do it bro, delete CLAUDE.md here, delete CLAUDE.md in
repo-kit just fucking do it".

Step one re-stamps the agent tooling from repo-kit (`agent-sync --from
../repo-kit`): the kit's prod-title and agent-marker browser guards,
its newer no-sound guard and two skill texts. Nothing showcase-local
changed in them.

Step two takes the kit's agent-parity.mjs and agent-sync.mjs (repo-kit
5ef37f7: AGENTS.md alone is `same`) and deletes CLAUDE.md. Gotcha:
this repo's own `src/scripts/.kit/agent-sync.mjs --from ../repo-kit`
never re-stamps those two scripts in a lean repo (it looks for them at
the lean path inside the kit); the kit's own
`node ../repo-kit/scripts/agent-sync.mjs --from ../repo-kit --root .`
does. dev.md also loses U1's stale `public/shardfiles/` line.
