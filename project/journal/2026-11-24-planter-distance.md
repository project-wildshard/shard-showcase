# Raised planter: distance foliage insert

Reuse the exact PROP-014 masonry and loam. The original planting
is available unchanged for close shots. The alternate GLB contains
four reduced foliage components only, with the existing yellow
and green palette. Replace the original planting when assembling
this study; do not render both variants together.

The two 24 m portraits use identical light and camera. Quantify
silhouette overlap by rasterizing the projected foliage triangle
union at 402 × 874, then compare intersection over union. This is
a geometry proxy for that one camera only, not a full image metric.
The third render shows the alternate planting up close.

```sh
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/showcase-studies/planter_distance_insert.py -- \
  /absolute/scratch/planter-distance
```

Both distance views and the detail use the original stonework. No
runtime LOD selection, asset placement, frame rate or draw-call claim
is made.
