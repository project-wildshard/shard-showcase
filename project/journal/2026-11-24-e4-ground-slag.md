# E4 foundry ground slag: static cue

The E4 ground cue is visually separate from the existing furnace
and its ambient motes. This static proposed decal uses a dark
crust, discontinuous orange rim, and sparse center fractures. It
exports as one low-profile mesh with no textures or light objects.

The reimported asset is tested against brick and slate surfaces
derived from the tracked E04 and E05 swatch colours. Measure the
area and place the plane 3 mm above its highest sampled point.
Day and dim portraits use identical 1.70 m eye height, 6 m
distance, 55-degree vertical FOV and display exposure. Emission
is camera-only for these Blender stills, with no bloom. The
alternate slate view shows the same reusable shape at close range.

```sh
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/showcase-studies/foundry_slag_decal.py -- \
  /absolute/scratch/e4-slag
```

The roughly 1 m footprint is a visual sample, not a specified
gameplay size. No enemy, damage, duration, status, collision or
native placement is authored. Furnace and ember assets are unchanged.
