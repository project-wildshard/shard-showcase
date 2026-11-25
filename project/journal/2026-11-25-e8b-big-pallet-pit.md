# E8b: Big Pallet's yard pit

A standalone **environment kit**, not the boss, encounter, or Gauntlet C2 pit.
The previous E07 portrait has a dry floor, warm steel, pallet stacks, and a
low black-and-ochre rim. Round 5 fixes the geometry: center at Three.js
`(96,0,-206)`, floor radius 12 m and top +0.05 m, wall outer radius 14 m
and top +1.40 m, with opposite 0.50-radian openings. The exact source is
`Raynos/project-wildshard-singleplayer@ce1cf050b36fa236155ac26d43e721b9012c49df`,
`art/showcase-template/round-5-blockout/{layout,lab}.js`.
The E07 portrait was verified as Git blob
`4103843a6c28b0ddb88b4969056a98c09dc4718f`.

E8b calls for two charge-stun pillars, but the archived lab did not place
them. The candidate places 2.90 m capped structures at local Three X/Z
(−6.8, −0.6) and (+6.8, +0.6), out of the north-south lane. The rim detail,
wear strips, and floor coloring are new art. The existing stacked-pallet
model is reference dressing in the review images only; it is unchanged
and not bundled. The center of the floor is the GLB origin.

The Blender and front-facing Three reimports each clear 342 center-lane
rays across a sampled 5.60 m width and at three heights. Both openings
measure 5.9377 m at 0.75 m height. Off-lane wall controls hit, and 63
downward probes land on the authored +0.05 m floor. The export has 14
material draws and no embedded textures. These are static geometry
tests, not character collision, stun, traversal, combat or performance
proof. No new stable catalogue ID and no live placement.

Rebuild and render from the repository root:
```sh
T=/tmp/wildshard-e8b-pit
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/big_pallet_pit.py -- "$T" --render
node project/check-big-pallet-pit.mjs "$T/e8b-big-pallet-pit.glb"
```
Drop `--render` for a model-only rebuild. Exact measurements and provenance
are in `project/layouts/e8b-big-pallet-pit-proof.json`.
