# E11c C1: dock apron finish

The exact C1 Loading Yard already has D1 and D2 openings, paired
shutter leaves and an indicator insert. These two independent assets
add a slatted cast-iron drain cap and broken ochre paint marks to the
apron sides, so both entrances read as working loading docks.

Both models are textureless and sit at a ground-centered origin, local
X along the long edge of the drain. See the fit receipt for the eight
world placements. Each side has one cap and one paint mark. The Blender
yaw transforms apply before conversion to Three coordinates.

A five-by-five grid on each placement verifies a single level receiver
surface (200 down-rays), then each reimported vertex is checked against
the same floor. Each overlay is outside the central 5 m band, avoids
donor-triangle intersections, and extends at most 12 mm above the
floor. Paint is 2 mm above the receiver. The dark recess is visual:
the resident floor is untouched and no drain hole is cut. The already
existing shutter/relay pose is for reference, not new geometry.

This is decorative only. No water simulation, obstacle, collision,
door operation, wave behavior, or native placement is included.

```sh
out=/tmp/c1-dock-apron
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/c1_dock_apron.py -- "$out"
cmp "$out/e11c-c1-dock-apron.json" project/layouts/e11c-c1-dock-apron.json
```

Set `WILDSHARD_VALIDATE_ONLY=1` for deterministic exports and fit without
rendering. No generated .blend, donor copy, or scratch texture is needed.
