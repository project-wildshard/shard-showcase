# W11a and E9: rain and pavement splash art

Wind streaks and a surface splash are two separate, texture-free GLBs.
The Blender weather frame uses the exact existing E9 tower and lamp as a
warm landmark and instances the new GLBs around it. Neither E9 file
was touched.

- The rain tile is a tapering crossed-ribbon stamp for a nominal
  6 × 6 × 4 m cell, planted at ground level. 76 static streaks,
  304 triangles, 17,680 bytes. +X wind convention in Blender.
  Tile placement, travel, spread, density, sorting and draw distance
  belong to the actual weather system; the GLB has no falling animation.
- Splash: 104 triangles, 8,304 bytes, one 0.833 s transform animation.
  The early impact rises, then rings expand and flatten; the
  beginning/end match at near-zero scale. Blender checked the
  imported animation at both the rising and flattened stages.
  A runtime effect still needs timing, pooling and correct surface height.
- Both assets use single double-sided alpha-blended material primitives.
  Raw combined size is 25,984 bytes, separate from the original E9 kit.
  This is not a weather benchmark or evidence of mobile overdraw cost.

Run from repo root:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/storm_rain_fx.py -- /tmp/storm-rain
```

The script rebuilds and reimports the two exports and renders one studio
frame with procedural wet pavement, indirect light and mock buildings.
The wide tiled rain and staggered frozen splash samples in that frame
are studio dressing. No Lights Out quest changes, ambient runtime,
wetness shader, lighting director, sound, or in-game weather was deployed.
