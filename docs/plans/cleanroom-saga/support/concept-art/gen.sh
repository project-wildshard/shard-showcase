#!/usr/bin/env bash
# Run one concept-art job: <job dir> holding prompt.txt and optional ref-*.jpg/png.
# Codex's built-in image tool writes concept.png into the job dir.
set -u
dir="$1"
[ -f "$dir/concept.png" ] && { echo "skip $dir"; exit 0; }
args=()
for ref in "$dir"/ref-*; do [ -f "$ref" ] && args+=(-i "$ref"); done
codex exec --skip-git-repo-check -s workspace-write -C "$dir" "${args[@]}" - < "$dir/prompt.txt" > "$dir/codex.log" 2>&1
if [ -f "$dir/concept.png" ]; then echo "ok $dir"; else echo "FAIL $dir"; fi
