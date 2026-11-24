# W9a Gold pickup fit in the Rock

Round 5 places the bottom of the 1 m Gold cube at world XYZ
`(-200, -5.5, 44)`. The exact mesh overlaps the later art liner at
station 30. The roof is 1.1 m above the floor, leaving only 0.6 m
above the original hovering base.

The art candidate is `(-201.8, -5.5, 40)`, 4 m before the original
point and 1.8 m west of the route center. It keeps the half-metre
hover and leaves 1.3 m between the pickup edge and the route
centerline. Retain the original position and model hash in the
[fit receipt](../layouts/w9a-squeeze-cave-gold-fit.json).
The tests compare the exact model triangles against the rebuilt
cave liner and dressing; overhead and floor rays check both poses.
The section omits the near wall only for the camera. The chamber
uses art-only lighting to show the pickup.

From repository root with Blender 4.3.2 and the repository Node setup:

```sh
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/west-climb-rock/build.py -- --output /tmp/rock-source
blender -b /tmp/rock-source/climb-rock-editable.blend -t 6 \
  --python-exit-code 1 --python scripts/blender/showcase-studies/rock_squeeze_gold.py \
  -- /tmp/rock-gold
```

Set `WILDSHARD_VALIDATE_ONLY=1` to skip the two image renders.
There is no new asset ID, GLB, terrain cut, runtime placement,
collection interaction, collision, reward timing or traversal test.
