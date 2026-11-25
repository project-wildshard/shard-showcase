# E12g: Crate Titan south retry alcove

This replaces the three visual placeholders only in the composed
review of the underground Crate Titan bowl. The original arena GLB
is unchanged. The new GLB keeps four separately editable assemblies:
roof and shell, checkpoint terminal, exit ring and fog surround.
The exit field and smudged fog in the pictures are Blender-only
previews. The export has no portal, respawn, fog trigger, encounter
binding, collision metadata, or dependency on the test environment.

Round 5 `layout.js` and `lab.js` place the bowl at (150, −150, 165).
The visible floor strip starts 56 m south of centre and ends at 69 m.
The lab models it with an 18 m floor strip around the stated 16 m
alcove envelope. An unobtrusive sill connects it to the circular slab.
That archive puts the terminal stake four metres west of centre
and the return portal four metres east. The exit ring sits at
(154, −145.8, 232.8), with a 3.4 m centreline radius. The arena fog
plane stays at world Z 218, separate from the return portal. This
refit follows those placements rather than moving the exit to line
up with the prior preview's placeholder at the centre of the room.

Geometry tests independently read the exported GLB in Blender and
Three.js. They probe the walk surface, near-floor to standing-height
sightlines on the centre approach, and the open circular aperture
within the frame. The aperture check excludes the room's rear wall:
it's a portal art concept, not a passable gap through solid geometry.
The combined visual fit also tests the unchanged donor bowl (apart
from the hidden old pocket) against the renewed approach.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/titan_retry_alcove.py -- /tmp/titan-retry
node scripts/blender/showcase-studies/check_titan_retry_alcove.mjs \
  /tmp/titan-retry/e12g-titan-retry-alcove.glb
```

[Approved E12g slice](../../docs/plans/kitchen-sink-v2/slices/E12g-titan-arena-fight.md)
· [Prior bowl study](2026-11-23-wsc-scene-008-titan-bowl.md)
· [Validation receipt](../layouts/e12g-titan-retry-alcove-proof.json)
