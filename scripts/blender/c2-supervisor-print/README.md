# C2 Shift Supervisor banner print

Optional alternate print for the existing C2 Pit banner (WSC-SCENE-007).
The plan calls for the Shift Supervisor to rise on the platform beneath
this banner. Preserve the exact scene, cloth, cantilevers, lift pieces
and anchors. For this visual variant only, hide the node
`13 Cloth banner.002` (the old pale chevrons), then add the new print
as a sibling at the C2 scene origin, world (55, 0, 212). All artwork is
encoded as mesh with three materials, no images. The print and letters
face the player entering from the north. It does not include an enemy,
badge rig, wave trigger, announcer or new collision.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/c2-supervisor-print/build.py -- /tmp/c2-print
```

Append `--proof-only` after the output directory to skip renders. Build
samples the original cloth surface, reimports the new GLB, checks the
print remains ahead of the cloth at each triangle centroid, and ray
tests all triangle centroids from three 1.70 m-high approaches.
The lower edge stays 5.19 m above the deck's measured top of travel.
Those are geometry checks, not a device legibility test. The two
matched scene studies show the existing lift parked in its raised pose.
