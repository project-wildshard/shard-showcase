# E11c: C1 recessed dock fixtures

Two new standalone props: one 39,436 B / 624-triangle shutter
leaf, re-used twice at each opening, and a 13,636 B / 188-triangle
blue relay strip that caps the existing blank housing. The exact
C1 Loading Yard GLB is the host and was not modified.

At the original D1/D2 anchors (14, 167) and (96, 167), the open
and closed poses have zero leaf/donor mesh overlaps. Thirty
parallel sample rays per dock pass through the open arrangement
and strike the leaves in the closed one. This is a sampled art
check, not complete collision or navigation coverage. The relay
is static art and does not reflect door state.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/c1_dock_shutters.py \
  -- /tmp/c1-dock-shutters
```

Set `WILDSHARD_VALIDATE_ONLY=1` for exports and measured fit only.
Both meshes reimported in Blender and Three.js. The [receipt](../layouts/e11c-c1-dock-shutters.json)
pins the C1 donor hash and both coordinate checks. The same D1
camera and lights render each pose. No animation, spawns, waves,
runtime sealing, collision or native deployment.
