# Concept art: how the candidates were made

The scripts that produced the ZC2 and CR4 candidates, kept so a
later round can be re-run the same way.

- `brasswick-prompts.py` writes the 9 Brasswick jobs (CR4): 3
  subjects (square, gate, fight) × 3 takes. Take 1 repaints a
  Cratefall golden frame, take 2 adds a Kitchen Sink round-11 mockup
  as the palette reference, take 3 is a fresh composition.
- `zone-prompts.py <slug>...` writes 9 jobs per zone (ZC2): 3 subjects
  (vista, hub, fight) × 3 takes, each job holding the zone's
  `ZONE-DESCRIPTION.md` as `zone.md`, whose look section is the art
  direction.
- `gen.sh <job dir>` runs one job through `codex exec` (its built-in
  image tool, gpt-image-2), writing `concept.png`. It skips a job that
  already has one.

The jobs ran in `tmp/concept-art/`. The committed candidates are
1536-wide JPEG copies; the full PNGs stay in `tmp/` until Jake's picks
are copied into each clean room's `concept/`.
