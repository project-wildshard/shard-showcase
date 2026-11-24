# E13 Gold cue on the Titan Gate crown

Round 5 at ce1cf050b3 places the arch at (216,229) with its crown at
18 m. The lab draws the Gold 1×1 marker with a base at 18.5 m. Keep
that half-meter difference as a visual seat rather than moving the
original unscaled cube or creating a second collectible model.

The existing modern gate donor is uniformly scaled from 4.68 to 18 m
for these stills only. Its outer width is 23.73 m; the archived
lintel is 22 m. This is not an exact reconstruction or native
placement. The new seat fits the eight sampled crown points and its
top matches the cube base in nine reimport samples. The gate masks
the center of the cube from the 1.70 m plaza camera; the tip is still
visible in that frame. Gameplay visibility and traversal are untested.

```sh
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/showcase-studies/titan_crown_gold.py -- \
  /absolute/scratch/titan-crown
```

The new 7,468-byte, 100-triangle mesh is just the seat. Place it at the
crown origin for the study. The donors are pinned, not duplicated.
The portal trigger, pickup, railings and any climb route are out of
scope.
