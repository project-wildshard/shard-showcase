# E3: maintenance perch for the suspended screen

The Band 3 Plumb Drone plan specifies high perches and a 0.9 m drone. This is static environment art, not the drone or an install. Two outward-facing half-saddles hug the existing 12-sided right post. Tilted braces carry an ochre pan, with a dark traction pad, cool inlays and stand-off fasteners. No parts enter the inboard curtain side of the post. The existing E3 screen is unchanged and appears only as the donor and preview context.

The GLB origin is the post axis at Blender local (4, 0, 4.02) on that donor, or Three (4, 4.02, 0), with the shelf extending along local +X. Pad top is about 4.20 m above the screen's base. Its 1.24 × 1.02 m pad accepts a nominal 0.9 × 0.9 m footprint at the center, but the actual animated rotor envelope is unknown. Forty-eight reimported radial samples put the inner saddle 6.76–6.94 mm clear of the steel. Thirty-five pad rays hit. The new geometry misses every sampled central opening ray (0.85/1.70/2.10 m). The perch extends the screen's outer footprint by 1.465 m on the right; recompute pack clearance before choosing any actual placement. No collider, interactable, light, pathing, visual blocking, or AI state is installed.

```sh
D=/tmp/e3-perch
blender -b -t 8 --factory-startup --python-exit-code 1 \
  --python scripts/blender/e3-perch/build.py -- "$D"
cmp "$D/e3-maintenance-perch.glb" public/assets/wildshard-art/e3-maintenance-perch.glb
cmp "$D/e3-maintenance-perch-proof.json" project/layouts/e3-maintenance-perch-proof.json
```

Use `--no-render` to skip the two visual reviews. One reimported mesh, five render primitives, 1,380 triangles and no images, skins or animation. Both renders use the same rebuilt GLB.
