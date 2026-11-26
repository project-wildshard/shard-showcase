# E2 · Replaceable lane-end cover

The Band 2 plan needs a place to route a charging Pallet Jack into
cover without making the lane a dead end for the player. This optional
fixture sits at the last edge of the existing 1.7 × 8.4 m warning
mesh. It is a low cast frame with a separate ribbed rubber face,
braced side feet and amber end returns. Existing floor marks and four
staged haul crates are unchanged. This is not a canonical map anchor.

- 90,332 bytes / 1,138 triangles / no textures. Ground/front-edge
  local origin, faces incoming traffic along glTF +Z; the enclosure
  extends along local −Z. Two selectable nodes.
- Real Blender reimport: all 315 forward rays across the warning width
  hit the fixture at 0.32–1.08 m height; 18 flank controls miss it.
- Native Engine 0.1.44 + Rapier on a flat test slab: from center and
  ±0.65 m, three stock player capsules stop at Z≈−8.00; the three
  matching no-fixture runs reach Z≈−13.74. Two routes at X±1.85 m
  pass the cover and turn back toward lane center behind it. No
  airborne ticks. Tests use reimported obstacle triangles.

This is environment art and player access verification only.
There is no Pallet Jack, stun, attack, cover-trigger behavior,
placed native room, or phone test. The exact rail/side crate
spacing describes the isolated review, not the final level.

```sh
d=/absolute/scratch/e2-stop
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/e2-lane-stop/build.py -- "$d"
WSC_NODE_PROJECT=/path/to/pinned/engine/project node --experimental-transform-types \
  scripts/blender/e2-lane-stop/check.mjs "$d/geometry.json" "$d/art.json" "$d/proof.json"
cmp "$d/proof.json" project/layouts/e2-charge-lane-stop-proof.json
```
