# W11a: West zipline crosswind study

The reviewed West route supplies both world-space endpoints and the
97 still-air centres along its 1.2 m sag. This model replaces only
the visible cable in a render. The West route, its endpoints,
fittings, landing pad and all traversal data are unchanged.

The five-second loop uses two position morphs. A tapered envelope
moves the midspan up to 38 cm sideways in each direction and adds
up to 7.6 cm of dip. The first and last 6% of the cable are fixed.
The timing starts at zero, has zero-deformation first and last
frames and runs at the same clip duration in Three.js. At 241
sampled instants, both endpoints and the measured sleeve rings stayed
put. Blender reimport verified the 776 unique baseline radial
positions against the 97 centres. No textures, gates, physics rig,
weather coupling, collision, live route installation, or rider test.

Render 1 uses the actual dark neutral cable. Render 2 uses a warm
diagnostic tint to distinguish peak deflection from cyan dashes on the
unchanged curve. The tints and dashes are not part of the cable GLB.

```sh
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/west-town/build.py -- --output /tmp/west-town
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/zip_wind_sway.py -- /tmp/west-town /tmp/zip-sway
node scripts/blender/showcase-studies/check_zip_wind_sway.mjs /tmp/zip-sway/w11a-west-zip-sway.glb
python scripts/blender/showcase-studies/zip_wind_board.py /tmp/zip-sway
```

The picture legend uses Pillow and DejaVu fonts; the asset doesn't.
Use `WILDSHARD_VALIDATE_ONLY=1` to rerun export and geometry checks
without generating stills.

[W11a weather scope](../../docs/plans/kitchen-sink-v2/slices/W11a-day-night-weather.md)
· [Previous landing fit](2026-11-24-zip-finish-fit.md)
· [Validation receipt](../layouts/w11a-west-zip-sway-proof.json)
