# Deck A: a 70-degree scramble face

W8b calls for a slab of holds around 70 degrees up to
Deck A at 6 m. The rebuilt Climb Yard also has its
earlier inferred stepped massing and three ladders.
This alternative meets the open west edge of Deck A
and leaves both of those elements intact. It does not
choose a final route or build the separate Rock pitches.

The one GLB (58,872 B / 1,052 triangles) places its origin
at the lower centre. Blender +X is uphill, +Y across.
The face rises 5.9725 m over 2.174 m horizontally and
carries 24 staggered holds, with lighter and warmer paths.
The last 12 mm before the deck is an intentional open
seam, not a collision patch. The centre line was shifted
270 mm from the layout centre to land on the original
planks instead of a plank-to-plank gap.

The new export is reimported and checked against evaluated
yard geometry. Three ground samples gave 27.5 mm. Across
three plank centers the slab face at 3 mm back from the
edge is at 5.99174 m with the original landing at 6 m.
The BVHs do not intersect the original deck. No motion,
attachment, traversal, clearance envelope, or performance
is implied by the visual contact test.

```sh
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/west-climb-rock/build.py -- --output /tmp/w8b-base
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/scramble_deck_a.py -- \
  /tmp/w8b-base /tmp/w8b-fit
```

The latter renders from the yard and above the proposed
join. No donor geometry is duplicated in the new export.
