# W10a · Scuffed grass and teasel at the paddock exit

Replace the uniformly scattered stubble in the W10a visual
study with two grounded prototypes: bent meadow grass close
to the rail and taller golden teasel outside it. The original
archived 48 × 60 m paddock and 12 × 14 m chute are unchanged.
Fence, signs, mounting block, trough, and trees are the same
donors as the previous stage. No new permanent placements.

| Prototype | Placements | GLB bytes | Triangles | Material draws |
|---|---:|---:|---:|---:|
| Pressed meadow bunch | 32 | 26,188 | 301 | 3 |
| Weathered roadside teasel | 14 | 80,448 | 1,122 | 4 |

At the recorded transforms all 69,804 reimported vertices are
outside the 12 m chute. Minimum distance from the lane is
253 mm; minimum lateral separation from the fence mesh envelope
is 88 mm. The foremost sign edge has at least 364 mm of forward
separation. The study's soil sits at −15 mm in world Y. These
are geometry checks, not a native path, performance, or horse test.
The preview shares mesh data; there is no in-game draw-call claim.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/paddock_verge.py -- /tmp/paddock-verge
node project/check-paddock-verge.mjs
```

Use `WILDSHARD_VALIDATE_ONLY=1` to skip both renders. The script
reimports the two exported foliage files before measuring the fit.
`project/layouts/w10a-chute-verge-proof.json` records the measured
transforms and exact GLB hashes. The GLBs contain only static,
double-sided material geometry, with no textures, collision, lights,
animations, wind, or preview stage. Keep separate from the W9b
lookout's bearberry/heather and the East Band 2 dry verge.
