# W0a/W0b: East Gate boundary as a two-part threshold

The round-11 M07 plaza mockup shows the masonry East Gate in front
and a separate industrial closure across the avenue behind it. W0a
calls for a north–south seam wall and a single crossing; W0b calls
the East Gate a gatehouse. This study keeps those two objects and
their jobs distinct. It does not amend the map or add a second route.

It reuses twelve pinned, unmodified GLBs. The carved span and reused
flanks are framed at staged world X −8, matching the earlier local
West threshold transform. The separate seam overlay is a proposed
composition at X 0. Its two leaves are fixed in an open position.
The western crop uses paving, a shaded stall, and no-enemy signage;
industrial bays, tarmac and amber hazard paint carry the eastern side.
The East backdrop is a placeholder and does not place any enemy packs.

The modeled gate jamb opening is 12.057 m and the lowest central span
vertex is at Y 6.245. A grid of 100 horizontal samples from the west
plaza through both layers is unobstructed across 11.76 m, at four
heights through 2.4 m. Six off-lane samples reached the industrial wall
while the center is unobstructed. These are sampled mesh rays, not
character sweeps, navmesh, collider generation, or safe-zone logic.

Rebuild all three views and the measurement report from repository root:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/east_gate_boundary.py -- /tmp/east-threshold
```

Keep the recipe, donor pins and measurement JSON; no new unique model,
duplicate inventory ID, full cell bake or native level deployment.
